# 第 6 章：会话持久化

> **定位**：本章分析会话如何落盘与恢复——三方法持久化 trait 与串行 actor、一个会话
> 目录的完整解剖、persist_ack 顺序屏障，以及"写侧防御 + 读侧宽容"的损坏工程与
> NFS 感知的 SQLite journal 选择。前置依赖：第 3 章（ChatStateActor 拓扑）、第 5 章
> （压缩产物的落盘衔接）。适用场景：你的应用需要把"正在进行的长过程"可靠地写进
> 磁盘并在崩溃后恢复。

## 6.1 为什么这很重要

一个 agent 会话可能跨越数小时、消耗数美元的采样费用、承载用户尚未提交的工作脉络。
它是**用户资产**，丢一次就够用户换工具。持久化因此不是"顺手写个日志"，而是有
明确正确性要求的子系统：**顺序**（磁盘上的历史必须与模型看到的历史一致，工具
配对不能乱）、**确认**（某些写必须"确定落了"才能继续，见 6.4）、**崩溃恢复**
（进程在任何字节边界被 kill，重启后会话必须能打开——注意是"能打开"，不是
"完美无缺"，这个区分是 6.5 的主题）。

这些要求彼此还会打架。顺序要求想让所有写走同一条串行通道；确认要求想让关键写
同步等待；性能要求想让高频写异步合并。崩溃恢复则给所有选择加了一条元约束：
无论怎么优化，磁盘上任何时刻的字节都必须是"可打开"的。设计一个持久化层，
本质上是给这四股力找一个可辩护的平衡点。

常规方案是给会话文件配一把锁，谁写谁加。第 3 章已经给出了这套系统的另一种答案：
持久化被收进一个独占的 actor。本章从这个 trait 开始，一路走到磁盘上的字节，
最后看两个"真实世界打脸理论"的案例——损坏的 JSONL 与 NFS 上的 SQLite。

## 6.2 独占持久化：三个方法的 trait

`ChatPersistence` 的全部方法面小得惊人
（crates/codegen/xai-chat-state/src/persistence.rs:19）：

```rust
pub trait ChatPersistence: Send + 'static {
    fn persist_message(&mut self, item: &ConversationItem);   // 追加一行
    fn replace_history(&mut self, items: &[ConversationItem]); // 全量改写
    fn flush(&mut self);
}
```

两个动词就概括了会话历史的全部生命周期：日常**追加**（每条消息一行），以及压缩
（第 5 章）与回退时的**全量替换**。`&mut self` 的独占语义在第 3 章已经分析过——
编译期保证单一调用者；这里补上实现侧：grok-build 的 `ChannelChatPersistence`
（crates/codegen/xai-grok-shell/src/session/chat_persistence.rs:29）不直接碰磁盘，
只把三个方法翻译成 `PersistenceMsg` 投进持久化 actor 的通道。于是写路径是一条
清晰的单行道：turn 逻辑 → chat-state actor（内存态）→ 持久化 actor（磁盘态），
每一段都是串行消费的 FIFO（先进先出队列，消息按投递顺序处理）——这个"处处串行"
在 6.4 会变成一个免费的正确性保证。顺带澄清方法面的一个观感：说"两个动词概括
生命周期"指的是追加与替换这两个**历史操作**；`flush` 不改变历史，它是屏障机制
的一部分（6.4）。

## 6.3 一个会话目录的解剖

磁盘布局按 `{root}/sessions/{urlencoded(cwd)}/{session_id}/` 组织（路径按工作
目录分区，同一项目的会话天然聚在一起）。目录内容
（crates/codegen/xai-grok-shell/src/session/storage/jsonl/mod.rs:84 起的 helper 族）：

```text
session_id/
├── chat_history.jsonl        # 模型上下文：ConversationItem 逐行，append-only
├── updates.jsonl             # 展示/回放事件流（带时间戳信封），append-only
├── summary.json (+.lock)     # 会话元数据：读-改-写，temp+rename 原子替换
├── rewind_points.jsonl       # 回退点（懒加载，见 6.7）
├── plan.json / goal/state.json / signals.json …   # 单文件 JSON 侧车
├── compaction_checkpoints/   # 压缩前完整历史（第 5 章的"找回"落点）
└── subagents/{id}/           # 子代理会话寄居于此（见 6.7）
```

这里的关键是**两种落盘策略并存**：追加型文件用 `O_APPEND` 直写——快，但单行
写入不是原子的；改写型文件（summary.json 等）走 temp+rename——慢一步，但替换
原子（mod.rs:276）。summary.json 还带一个 sidecar 锁文件（伴生的 `.lock` 文件；加锁的读-改-写在
`apply_patch_locked`，mod.rs:587）：它是目录里唯一被多方更新的"共享单元格"，
元数据的每次更新都是完整读出、修改、原子换入，锁保证两次读-改-写不交错。
另一处要标注：updates.jsonl 的写入经过内存合并缓冲再批量落盘
（crates/codegen/xai-grok-shell/src/session/persistence.rs:1446），缓冲里的事件
在崩溃时会丢——但 updates 只是展示回放素材而非权威历史，属于可再生层，丢失
窗口是被接受的。选择标准是数据形状：事件流天然追加、行内损坏可局部化（6.5
的前提），元数据是整体状态、必须要么旧要么新。**模型上下文（chat_history）与
展示事件（updates）分成两个文件**也非偶然：前者是喂给 LLM 的权威历史，后者只是
UI 回放素材——读路径的重要性不同，恢复策略也不同（resume 甚至跳过 updates，
见 6.7）。

## 6.4 persist_ack：一道顺序屏障，而非 fsync 屏障

第 4 章提到用户消息入库带确认。现在看精确语义
（crates/codegen/xai-grok-shell/src/session/acp_session_impl/turn.rs:708）：只有
用户消息走这条路——先等 chat-state actor 确认消息进入内存并投递持久化通道，再向
持久化 actor 发 `FlushAndAck` 并等回执。屏障的正确性不靠任何锁，靠**串行 FIFO 的
免费顺序保证**：持久化 actor 单通道顺序消费，`Chat(item)` 写盘必然发生在其后的
`FlushAndAck` 回执之前。第 3 章"处处串行"的架构红利在这里兑现——顺序屏障的
实现成本是一次 oneshot 往返，而不是一套锁协议。

同样重要的是弄清它**不保证**什么：`append_jsonl_line` 只做用户态 flush，不调
`sync_all()`（mod.rs:272）——ack 返回意味着字节已交给操作系统页缓存，机器断电
仍可能丢失。屏障防的是进程崩溃（高频场景），不防断电。值得指出的是，这里存在
一个几乎免费的强化空间：persist_ack 只作用于用户消息这条**低频路径**，且调用方
本就阻塞等待、其后紧跟数秒的采样——在这一条路径上补一次 fdatasync 的边际成本
接近零，却能把 6.1 定性为"不可再生资产"的用户输入护到断电级别。现状更像
"没有付费的必要还没出现"而非"论证过不值得付"——阅读源码时要区分这两种缺席。

为什么只有用户消息享受屏障？因为它是**不可再生**的——助手回复丢了可以重新采样，
工具结果丢了可以重跑，用户敲的那段话丢了就真丢了。持久化的严格度按数据的可再生
性分级，与第 4 章 usage 记账的两档严格度同一逻辑。

## 6.5 读侧宽容，写侧防御

崩溃恢复的现实是：追加写不是原子的，总有一天磁盘上会出现半行 JSON。这套系统对
损坏的处理是一个精心设计的闭环。

**写侧防御——torn-tail 自愈**（mod.rs:234）：每次追加前先读文件最后一个字节，
不是 `\n` 就先补一个，把上次崩溃留下的半行"封"成一条独立坏行。注释把目标说得
很清楚：把任何撕裂写的损害**精确限制在一条记录内**。触发场景不是臆想——写侧注释点名了 auto-update 重启中途 kill 持久化 actor 与
磁盘写满；读侧注释（mod.rs:426）还补充了重连时两个持久化 actor 短暂竞写同一
文件的场景。

**读侧宽容——跳过、隔离、绝不拒载**（mod.rs:416 的设计文档与实现）：load 时
按 `\n` 切分逐行解析，坏行跳过；首次发现损坏时把整个文件复制一份 `.jsonl.corrupt`
留证，之后的快照重写会把坏行从活文件里洗掉。理由写在注释里，值得原文引用：

> Failing the whole load on one bad line bricks the session forever […], which
> is strictly worse than resuming without the damaged record.

（注释节选，省略处为错误码举例。）

一行坏数据让整个会话永久变砖，严格劣于丢掉那一行继续——这是把 6.1 的"能打开
优先于完美无缺"落成代码。同样的宽容延伸到语义层：load 时剔除 API 必拒的坏图
（超大/坏格式的 data-URI，`strip_invalid_images`，mod.rs:1461），让"中了毒的
历史自愈，而不是每一轮都 400"。

**版本兼容**也归入读侧宽容：格式版本记在 summary.json（`CHAT_FORMAT_VERSION`，
crates/codegen/xai-grok-shell/src/session/persistence.rs:26），读取时双向 fallback
解析新旧两种记录类型，甚至能读新旧混写的文件（旧会话被新版本续写的产物）；老
格式缺失的 reasoning 项在 load 时重建注入。关键纪律是**只在内存升级，绝不改写
磁盘**——升级写盘会让降级二进制彻底读不懂文件，load-time-only 让新旧版本可以
反复交替打开同一个会话。

"磁盘即真相"的原则还有一个小而硬的体现：压缩转写段的编号不由内存计数器分配，
而是每次从磁盘扫描现有段号推导下一个（`next_compaction_segment_index`，
mod.rs:892）。内存计数器在崩溃-恢复后会归零重数，覆盖旧段；磁盘扫描天然
resume-safe。任何"编号、偏移、游标"类状态，只要进程可能中途死掉，权威副本
就应该放在它编号的东西旁边。

读侧宽容也有边界之外的债务。fork 会话要从历史里数出"完整的 turn 边界"再切分
（`fork_filter_chat`，mod.rs:636），这个 reasoning-aware 扫描器与子代理解析 crate
里的 `count_complete_turns` 是**必须同步演进的一对**——注释显式声明了这层跨
crate 耦合。两个 crate 各自独立编译、类型互不依赖（第 2 章的拆分哲学），但语义
上是连体的；类型系统管不到的耦合只能靠注释与纪律。库化不消灭耦合，只是把它
从类型层挤到文档层——这是 trait-seam 架构的另一面。

## 6.6 SQLite 与 NFS：一次 SIGBUS 事故的完整答案

会话目录之外，系统还有两个 SQLite 库：worktree 池元数据与会话全文搜索索引。
分工原则清晰——**JSONL/JSON 存权威内容，SQLite 只存可重建的索引与缓存**
（搜索索引 schema 落后直接 drop 重建，
crates/codegen/xai-grok-shell/src/session/storage/search_fts.rs:1）。这个分层
是接下来一切激进手段的前提。

SQLite 默认推荐 WAL 模式，但 `xai-sqlite-journal` 的模块文档记录了它在网络文件
系统上的死法（crates/codegen/xai-sqlite-journal/src/lib.rs:1，注释节选）：

> WAL keeps its wal-index in an mmap'd `-shm` file and relies on coherent shared
> memory plus reliable POSIX locks — guarantees network filesystems do not
> provide. … a peer host truncating/rebuilding the `-shm` during WAL recovery
> or close rips the backing out from under our mapping and the next wal-index
> read dies with SIGBUS.

WAL 的共享索引靠 mmap 与 POSIX 锁——两样恰好都是 NFS 给不了的；另一台主机重建
`-shm` 文件时，本机的内存映射被釜底抽薪，下一次读直接 SIGBUS 崩进程。解法分三步，
每步都有讲究：

1. **检测**：`statfs(2)` 的 `f_type` 魔数比对已知网络文件系统（lib.rs:288）——
   NFS/SMB/CIFS/Ceph/Lustre/GPFS，甚至包括 WekaFS 的 `0x1803_1977`，注释说明
   这个值是在真实 wekafs 挂载上实测得来（linux/magic.h 里查不到）。检测失败
   一律当本地处理——保持 WAL，不为不确定性放弃性能。
2. **换模式 + 分库**：网络盘上改用 TRUNCATE journal，且数据库文件按主机名分裂
   （`worktrees.db → worktrees.h-<host>.db`，lib.rs:104）。分库解决的是**旧版本
   二进制**问题：journal 模式是数据库全局属性，一个不认识新逻辑的旧版进程会把
   共享库翻回 WAL；旧版不知道 per-host 文件名，于是"无 WAL"不变式**按构造成立**
   ——不依赖任何进程行为良好。这一步的可行性完全建立在"SQLite 侧全是可重建
   数据"的分工上：每台主机各建各的索引，无非多算几次。
3. **留后门**：`GROK_SQLITE_JOURNAL_MODE` 环境变量强制覆盖检测（lib.rs:39）——
   启发式检测总有误判的一天，kill-switch 让误判的用户当场自救而不是等发版。

细节处还有两笔：选 TRUNCATE 而非 DELETE，省掉每次提交的文件创建/删除往返与
NFS 的 `.nfsXXXX` silly-rename 垃圾（lib.rs:26）；转换已有 WAL 库时用 EXCLUSIVE
locking 让 wal-index 留在堆内存，全程不碰 `-shm` 的 mmap（lib.rs:189）——连
"退出 WAL"这个动作本身都要防 SIGBUS。

这一节值得当作"事故驱动设计"的标本收藏：从内核机理（mmap 一致性）到生态现实
（旧版本二进制共存）到运维退路（kill-switch），一次 SIGBUS 的答案覆盖了三个
层次。

## 6.7 生命周期：寄居、清理与冷启动

**子代理会话寄居父目录**（`subagents/{id}/`，`SessionDirMode::Explicit`，
mod.rs:21）。三个理由写在构造函数注释里
（`new_with_explicit_dir`，crates/codegen/xai-grok-shell/src/session/persistence.rs:2188）：
不同步云端、不做共享中继、生命周期由父会话协调者管理。实现上 Explicit 模式的
目录扫描直接返回空（mod.rs:120）——子代理永不出现在会话列表里，随父会话删除而
递归删除、随父会话归档而一起上传。"从属关系"用目录结构表达，列表污染、独立
GC、独立上传三个问题一次消掉。

**磁盘增长靠 TTL 收口**：会话文件 append-only 无限增长，清理由
`cleanup_stale_sessions`（crates/codegen/xai-grok-shell/src/session/persistence.rs:2663）
兜底——每进程仅跑一次、`spawn_blocking` 执行、默认 30 天 TTL 可配置，删文件后
只对"本轮真删过东西"的子树做 rmdir，避免误删并发新建的目录。长驻会话靠持久化
actor 每小时 touch 一次续命。

**冷启动性能**藏着一个量化好例子：会话列表不加载全部 summary，按 mtime 排序只读
top-N（mod.rs:184）——注释给出实测数据，约 1.2 万个会话的冷启动列表从约 3 秒降到
约 200 毫秒。持久化层的性能工程往往不在写路径（有 actor 吸收），而在这类"启动时
扫一眼全世界"的读路径上。同类的懒惰还有 `rewind_points.jsonl`：它可能非常大，
resume 路径干脆不读（`load_session_without_updates`，mod.rs:1143），真要回退时才由
文件状态追踪器按需加载——恢复一个会话所需读的字节数，取决于用户接下来要做什么，
而不是会话曾经发生过什么。

持久化 actor 自身的关停也遵守第 3 章的惯例：`biased` select 让取消信号优先于
待处理命令（crates/codegen/xai-chat-state/src/actor/mod.rs:99），保证"要求退出"
不会排在一长串积压写任务后面无限等待，同时 FIFO 里已接收的写仍按序完成——
优雅关停的两个目标（快速响应、不丢已接收数据）由分支顺序一次性表达。

## 6.8 同一问题，codex 怎么做

codex 的会话持久化同样以 JSONL 为骨架（rollout 记录器，会话即一个 rollout 文件，
支持 resume），方向一致，分岔在两处：

**其一，单文件 vs 目录**。codex 一个会话基本是一个 rollout JSONL；Grok Build
是一个目录十几种文件——模型上下文、展示事件、元数据、回退点、压缩检查点各自
独立。单文件简单、迁移容易；多文件让不同读路径各取所需（resume 不读 updates、
回退点懒加载），也让不同数据形状用不同的落盘策略（append vs temp+rename）。
文件拆分粒度跟随的是**读路径的差异**，而不是数据类别的多少。

**其二，防御投入的方向**。codex 的 rollout 层近来也在增厚——已独立成
`codex-rs/rollout` crate，带 SQLite 会话索引、压缩与反向 JSONL 扫描；但两家防御
的方向不同：Grok Build 的独特投入集中在**恶劣环境存活**——torn-tail 自愈、
`.corrupt` 隔离、坏图剔除、NFS 感知 journal，每一项都对应一个被点名的真实事故
场景（NFS、auto-update 重启、多客户端竞写）；codex 的投入更多在**规模化读取**
（索引、压缩）。防御性代码的分布是产品部署形态的化石记录：前者要在企业网络盘
与自更新的长驻进程里活下来，后者要在海量会话里快速检索。

**其三，索引层的组织**。codex 把会话索引做进 rollout crate 的 SQLite（state_db）；
Grok Build 的对应物是独立的 FTS5 搜索库加"按 mtime 扫目录"的列表路径（6.7），
索引与权威数据的分层原则（可 drop 重建）两家一致——这一点上是趋同演化。

（本节对 codex 的描述基于 openai/codex 2026 年年中 main 分支，核对时以
`codex-rs/rollout` 为准。）

## 6.9 模式提炼

**模式一：写侧防御 + 读侧宽容（torn-write containment）**。追加流的损坏处理
成对设计：写侧把撕裂限制在单条记录（追加前封住非 `\n` 结尾的尾巴），读侧跳过
坏行、隔离留证、绝不整体拒载。前提：记录之间相互独立、单条丢失可接受——注意
这个前提对有配对约束的记录（工具请求/结果对）并不完全成立，丢掉配对一半仍需
下游（如 6.5 的历史校验或第 5 章的孤儿清洗）兜底，宽容读取只是第一道防线。

**模式二：权威/可重建分层（authority tiering）**。权威数据用最朴素可审计的格式
（JSONL/JSON），索引缓存进 SQLite 并保持"随时可 drop 重建"。激进的存储手段
（per-host 分库、schema 变更即重建）只对可重建层使用。

**模式三：环境感知持久化（filesystem-aware storage）**。存储引擎的正确性假设
（mmap 一致性、POSIX 锁）在不同文件系统上成立度不同；用 statfs 检测环境、按
环境降级模式、按构造隔离旧版本、留环境变量 kill-switch。

**模式四：确认按可再生性分级（ack by regenerability）**。不可再生的数据（用户
输入）给顺序屏障确认，可再生的（模型输出、工具结果）fire-and-forget；屏障强度
只到进程崩溃（flush），不到断电（fsync），按威胁频率定价。

## 设计要点回顾

速查索引（详述见对应小节）：

- 持久化的三个正确性要求：顺序、确认、崩溃后"能打开优先于完美" → 6.1
- 三方法 trait（追加/全量替换/flush）；写路径单行道处处串行 → 6.2
- 目录解剖：append-only vs temp+rename 按数据形状二分；模型上下文与展示事件
  分文件 → 6.3
- persist_ack 是顺序屏障非 fsync 屏障；只保用户消息（不可再生）→ 6.4
- torn-tail 自愈 + 坏行跳过隔离 + 坏图剔除 + load-time-only 版本升级 → 6.5
- NFS/SIGBUS 三步解法：statfs 检测、TRUNCATE + per-host 按构造隔离、kill-switch；
  前提是 SQLite 只存可重建数据 → 6.6
- 子代理目录寄居三理由；30 天 TTL + touch 续命；top-N summary 冷启动 3s→200ms → 6.7
- codex 对照：单 rollout 文件 vs 多文件目录、防御方向（恶劣环境 vs 规模化读取）、
  索引分层趋同 → 6.8
- 四个可迁移模式：撕裂遏制、权威分层、环境感知、按可再生性分级确认 → 6.9

---

### 版本演化说明

> 本章核心分析基于本书快照仓库（同步自 xAI monorepo，commit 8adf901，SOURCE_REV 2ec0f0c，2026-07）。
> 涉及 crate：xai-chat-state、xai-sqlite-journal、xai-grok-shell（session/storage
> 族）。codex 对比基于 openai/codex 2026 年年中 main 分支。上游同步后请以
> `book/tools/check_chapter.py` 校验本章引用。
