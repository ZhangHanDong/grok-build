spec: task
name: "ch06-persistence"
inherits: project
tags: [book, chapter, runtime, persistence, sqlite]
---

## 意图

撰写《第 6 章：会话持久化》。读者是中高级工程师；本章讲清会话如何落盘与恢复：
ChatStateActor 独占持久化的无锁设计、JSONL 存储格式与目录布局、写确认屏障，
以及 NFS 感知的 SQLite journal 选择这一"事故驱动设计"的典型案例。

## 已定决策

- 主轴案例之一：ChatStateActor 独占 `Box<dyn ChatPersistence>`（&mut self 类型强制）
- 主轴案例之二：xai-sqlite-journal 按文件系统选 journal 模式（NFS SIGBUS 事故）
- 覆盖 JSONL 目录布局、persist_ack 写屏障、会话恢复（resume/load）路径
- 覆盖与 ch5 的衔接（compaction checkpoint 落盘）——点到为止
- 所有架构性陈述带 `file:line` 引用；codex 事实先查 knowledge/context/codex-reference.md
- 章末附"同一问题，`codex` 怎么做"参照小节
- 中文写作，成稿落至 `book/manuscript/ch06-persistence.md`

## 边界

### 允许修改
- book/manuscript/ch06-persistence.md
- book/knowledge/context/runtime.md
- book/knowledge/context/codex-reference.md

### 禁止做
- 不修改 crates/ 下任何源码
- 不使用无 file:line 溯源的架构性断言
- 单段源码粘贴不超过 30 行
- 不重复 ch3 的 ChatStateActor 消息拓扑（交叉引用），不深入 checkpoint/rewind 语义（ch10）

## 完成条件

场景: 持久化设计动机完整
  测试: ai_review_ch06_motivation
  假设 读者熟悉常规"加锁写文件"方案
  当 读者读完动机一节
  那么 能说出会话持久化的正确性要求（顺序、确认、崩溃恢复）与独占 actor 方案的对应关系

场景: 存储格式与恢复路径准确
  测试: ai_review_ch06_storage
  假设 读者对照 xai-chat-state 源码阅读
  当 读者核对文中每一处 `file:line` 引用
  那么 JSONL 布局、persist_ack 屏障、resume 路径的描述与源码一致

场景: NFS journal 案例成立
  测试: ai_review_ch06_nfs
  假设 文中含 xai-sqlite-journal 小节
  当 读者读完该节
  那么 能解释 WAL 在 NFS 下为何 SIGBUS、TRUNCATE + per-host DB 如何规避、kill-switch 的作用

场景: codex 参照小节到位
  测试: ai_review_ch06_codex_compare
  假设 章末含 `codex` 参照小节
  当 读者读完参照小节
  那么 文中列出 codex 会话持久化与 Grok Build 的至少 2 点取舍差异

场景: 篇幅与结构达标
  测试: check_ch06_structure
  假设 成稿位于 `book/manuscript/ch06-persistence.md`
  当 编辑运行 book/tools/check_chapter.py
  那么 正文字数在 8000-15000 之间、含至少 1 张示意图、至少 5 处 file:line 引用、
      章末含"设计要点回顾"清单

场景: 引用溯源失败被拒稿
  测试: check_ch06_citation_validity
  假设 文中存在指向 crates/ 的 `file:line` 引用
  当 任一引用指向不存在的文件或行号超出文件长度
  那么 结构检查返回非零退出码并列出失效引用

## 排除范围

- checkpoint/rewind/worktree（ch10）、compaction 策略本身（ch5）、leader 状态（ch7）、
  memory 系统（ch18）
