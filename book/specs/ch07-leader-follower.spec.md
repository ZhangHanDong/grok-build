spec: task
name: "ch07-leader-follower"
inherits: project
tags: [book, chapter, runtime, leader, acp]
---

## 意图

撰写《第 7 章：Leader-Follower——一个进程服务所有入口》。读者是中高级工程师；
本章讲清单机单 leader 架构：TUI/headless/IDE 多客户端如何经 Unix socket + ACP
共享同一 agent 运行时、请求路由与会话归属、版本驱动的 leader 抢占，以及这个
架构存在的理由（为什么不是每客户端一个进程）。

## 已定决策

- 主轴案例：leader 进程模型（leader/mod.rs、server.rs）与 connect_or_spawn 接入
- 覆盖 ACP 协议在其中的角色（acp-lib 的 gateway 双 side、_meta tracing）
- 覆盖版本驱动抢占 should_evict（仅严格更新才驱逐）
- 覆盖 leader 崩溃/退出时客户端的行为（重连？降级？）
- 所有架构性陈述带 `file:line` 引用；codex 事实先查 knowledge/context/codex-reference.md
- 章末附"同一问题，`codex` 怎么做"参照小节
- 中文写作，成稿落至 `book/manuscript/ch07-leader-follower.md`

## 边界

### 允许修改
- book/manuscript/ch07-leader-follower.md
- book/knowledge/context/runtime.md
- book/knowledge/context/codex-reference.md

### 禁止做
- 不修改 crates/ 下任何源码
- 不使用无 file:line 溯源的架构性断言
- 单段源码粘贴不超过 30 行
- 不重复 ch3（会话内部）/ch6（持久化）已详述内容

## 完成条件

场景: 架构动机完整
  测试: ai_review_ch07_motivation
  假设 读者默认"每个终端窗口各起一个独立 agent 进程"的常规方案
  当 读者读完动机一节
  那么 能说出单 leader 方案解决的至少 2 个具体问题及其引入的新代价

场景: 接入与路由讲解准确
  测试: ai_review_ch07_routing
  假设 读者对照 leader/ 源码阅读
  当 读者核对文中每一处 `file:line` 引用
  那么 connect_or_spawn、请求 ID 命名空间隔离、会话归属路由的描述与源码一致

场景: 版本抢占机制成立
  测试: ai_review_ch07_evict
  假设 文中含 should_evict 小节
  当 读者读完该节
  那么 能解释"仅严格更新才驱逐"如何防抖动并收敛到最新版、抢占时在跑会话怎么办

场景: codex 参照小节到位
  测试: ai_review_ch07_codex_compare
  假设 章末含 `codex` 参照小节
  当 读者读完参照小节
  那么 文中列出 codex 进程模型与 Grok Build 的至少 2 点取舍差异

场景: 篇幅与结构达标
  测试: check_ch07_structure
  假设 成稿位于 `book/manuscript/ch07-leader-follower.md`
  当 编辑运行 book/tools/check_chapter.py
  那么 正文字数在 8000-15000 之间、含至少 1 张示意图、至少 5 处 file:line 引用、
      章末含"设计要点回顾"清单

场景: 引用溯源失败被拒稿
  测试: check_ch07_citation_validity
  假设 文中存在指向 crates/ 的 `file:line` 引用
  当 任一引用指向不存在的文件或行号超出文件长度
  那么 结构检查返回非零退出码并列出失效引用

## 排除范围

- 会话内部机制（ch3-ch6）、编辑器插件本身（ch1 已概览）、
  auto-update 机制细节（只讲与抢占的交互）
