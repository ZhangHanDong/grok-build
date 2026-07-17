spec: task
name: "ch03-session-actor"
inherits: project
tags: [book, chapter, runtime, actor]
---

## 意图

撰写《第 3 章：Actor 化的会话引擎》。读者是中高级工程师；本章通过 xai-grok-shell 的
SessionActor 讲清"一个多事件源、长生命周期的 agent 会话为什么以及如何用 Actor 模型组织"：
消息流转、无锁设计、与 SamplerActor/ChatStateActor 的协作拓扑。

## 已定决策

- 主轴案例：`run_session` 三路 select 主循环与 `SessionActor` 的消息拓扑
- 讲清"全 Actor + mpsc、无共享锁"的动机与代价（对比 Mutex 共享状态方案）
- 覆盖 `SamplerActor` 每请求 JoinSet 并发模型
- 所有架构性陈述带 `file:line` 引用，事实以 book/knowledge/context/runtime.md 为基线
- 章末附"同一问题，`codex` 怎么做"参照小节
- 中文写作，成稿落至 `book/manuscript/ch03-session-actor.md`

## 边界

### 允许修改
- book/manuscript/ch03-session-actor.md
- book/knowledge/context/runtime.md

### 禁止做
- 不修改 crates/ 下任何源码
- 不使用无 file:line 溯源的架构性断言
- 单段源码粘贴不超过 30 行
- 不深入 agentic 循环细节（第 4 章主题）与压缩（第 5 章）、持久化（第 6 章）

## 完成条件

场景: Actor 选型动机完整
  测试: ai_review_ch03_motivation
  假设 读者熟悉 Mutex 共享状态的常规方案
  当 读者读完本章动机一节
  那么 读者能说出会话场景选 Actor 而非共享锁的至少 2 条具体理由及其代价

场景: 主循环讲解准确
  测试: ai_review_ch03_run_loop
  假设 读者对照 run_loop.rs 源码阅读，文中含 `run_session` 主轴案例
  当 读者核对文中每一处 `file:line` 引用
  那么 引用与源码一致，三路事件源与旁挂任务的职责划分描述无误

场景: 采样并发模型成立
  测试: ai_review_ch03_sampler
  假设 文中含 SamplerActor 一节
  当 读者读完该节
  那么 能解释"单线程命令处理 + 每请求 JoinSet"如何同时保住一致性与并发流式

场景: codex 参照小节到位
  测试: ai_review_ch03_codex_compare
  假设 章末含 `codex` 参照小节
  当 读者读完参照小节
  那么 文中列出 codex 会话组织方式与 Grok Build 的至少 2 点取舍差异

场景: 篇幅与结构达标
  测试: check_ch03_structure
  假设 成稿位于 `book/manuscript/ch03-session-actor.md`
  当 编辑运行 book/tools/check_chapter.py
  那么 正文字数在 8000-15000 之间、含至少 1 张示意图、至少 5 处 file:line 引用、
      章末含"设计要点回顾"清单

场景: 引用溯源失败被拒稿
  测试: check_ch03_citation_validity
  假设 文中存在指向 crates/ 的 `file:line` 引用
  当 任一引用指向不存在的文件或行号超出文件长度
  那么 结构检查返回非零退出码并列出失效引用

## 排除范围

- agentic 循环内部（ch4）、compaction（ch5）、持久化实现（ch6）、leader 架构（ch7）
- TUI 侧事件循环（ch13）
