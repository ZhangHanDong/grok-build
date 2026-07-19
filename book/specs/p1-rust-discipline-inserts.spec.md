spec: task
name: "p1-rust-discipline-inserts"
inherits: project
tags: [book, surgical, rust, newtype, error, serde, raii]
---

## 意图

把四处"Rust 把不变量变成编译器/CI 约束"的深化，外科式插进既有章节，不新开章、
不重编号：ch2 §2.5 末尾补型级验证型 newtype（wire ID/路径/NonZeroU64）；错误即恢复
协议（AuthError/RefreshTokenError 的 non_exhaustive 不对称、compaction is_deterministic）；
公共 API 与序列化演进（协议帧 deny_unknown 严、持久化 allow 宽、公共 API non_exhaustive）；
RAII 作为时序事务（默认回滚成功后 disarm、清理带 generation）。每处只做一段/一小节，
带 file:line，接住既有论点。

## 已定决策

- ch2 §2.5 末尾追加"从 crate 归属到类型不变量"块：ids.rs 构造器验证 + Deserialize 复用
  （crates/common/xai-tool-protocol/src/ids.rs:5、102）、AbsPathBuf/RelPathBuf 方向拒绝 +
  camino UTF-8（crates/codegen/xai-grok-paths/src/lib.rs:90）、context_window NonZeroU64
  （crates/codegen/xai-grok-sampling-types/src/types.rs:1047）；收束"裸值→验证构造→私有
  字段→类型化转换→Serde 不绕过"
- 错误即恢复协议：AuthError `#[non_exhaustive]` 而 RefreshTokenError 故意不加以强制穷举
  永久/瞬态、瞬态无宽泛 From（crates/codegen/xai-grok-shell/src/auth/error.rs），
  compaction `is_deterministic()` 把"重试是否有意义"编码进类型
  （crates/common/xai-grok-compaction/src/sampler.rs）
- serde 演进：streaming payload `deny_unknown_fields`
  （crates/common/xai-tool-runtime/src/streaming.rs:30）、持久化权限状态容忍未知
  （crates/codegen/xai-grok-workspace/src/permission/state.rs）、公共错误 `#[non_exhaustive]`
  （crates/codegen/xai-grok-workspace/src/error.rs）
- RAII 事务：PartialWorktreeGuard 默认删、成功 disarm
  （crates/codegen/xai-fast-worktree/src/worktree/execute.rs）、AuthAttemptGuard 带 generation
  （crates/codegen/xai-grok-shell/src/auth/single_flight.rs）
- 每处引用用完整 `crates/...` 路径；中文；不新增顶级章号、不重编号既有小节

## 边界

### 允许修改
- book/manuscript/ch02-crate-philosophy.md
- book/manuscript/ch05-compaction.md
- book/manuscript/ch06-persistence.md
- book/manuscript/ch10-time-travel.md
- book/manuscript/ch08-tool-abstraction.md
- book/specs/p1-rust-discipline-inserts.spec.md

### 禁止做
- 不修改 crates/ 下任何源码
- 不使用无 file:line 溯源的架构性断言
- 不把"未接入/未采用"的机制说成已用（沿用诚实纪律）
- 不新开顶级章、不重编号既有小节（只做段落/小节级追加）
- 单段源码粘贴不超过 30 行

## 完成条件

场景: 验证型 newtype 型级不变量准确
  测试: ai_review_p1_newtype
  假设 读者对照 ids.rs 与 paths lib.rs 阅读
  当 读者读完 ch2 §2.5 末尾新块
  那么 能说出 wire ID 的 Deserialize 复用验证构造器、路径类型按方向拒绝且 UTF-8 由类型保证、NonZeroU64 排除零窗口

场景: 错误即恢复协议准确
  测试: ai_review_p1_error
  假设 读者对照 auth/error.rs 阅读
  当 读者读完错误恢复段
  那么 能说出 RefreshTokenError 故意不 non_exhaustive 以强制穷举永久/瞬态、瞬态无宽泛 From 防误分类

场景: serde 演进不对称准确
  测试: ai_review_p1_serde
  假设 读者对照 streaming.rs 与 permission/state.rs 阅读
  当 读者读完序列化段
  那么 能说出协议帧 deny_unknown_fields 严、持久化状态容忍未知、公共 API non_exhaustive 留演进空间

场景: RAII 事务准确
  测试: ai_review_p1_raii
  假设 读者对照 worktree/execute.rs 与 single_flight.rs 阅读
  当 读者读完 RAII 事务段
  那么 能说出默认回滚成功后 disarm、清理动作带 generation 防迟到 Drop 伤后继状态

场景: 结构与引用有效
  测试: check_p1_structure
  假设 各处插入已落章
  当 编辑运行 book/tools/check_chapter.py 与 cite_heal
  那么 各章仍满足门禁、新引用全部溯源有效

场景: 引用溯源失败被拒稿
  测试: check_p1_citation_validity
  假设 插入存在指向 crates/ 的 `file:line` 引用
  当 任一引用指向不存在的文件或行号超出文件长度
  那么 结构检查返回非零退出码并列出失效引用

## 排除范围

- P2 侧栏（must_use / lint / 锁中毒 / zeroization，另作）
- 第 19 章韧性机制（已成章）
- 各机制的完整实现细节
