spec: task
name: "ch11-sandbox"
inherits: project
tags: [book, chapter, tools, sandbox, security]
---

## 意图

撰写《第 11 章：沙箱——不可信计算的边界》。读者是中高级工程师；本章讲清
OS 级隔离的分层设计：nono 统一 Landlock/Seatbelt 的文件面、seccomp BPF 的
子进程网络面、五档 profile 与自定义，以及权限系统与沙箱的关系（谁防什么）。

## 已定决策

- 主轴案例：xai-grok-sandbox 的分面设计（文件面进程级一次应用、网络面子进程逐个）
- 覆盖 nono 抽象如何统一 Linux Landlock 与 macOS Seatbelt
- 覆盖五档 profile（workspace/devbox/read-only/strict/off）与 ~/.grok/sandbox.toml
- 覆盖权限系统（审批）与沙箱（内核强制）的职责边界——防模型犯错 vs 防恶意载荷
- 所有架构性陈述带 `file:line` 引用；codex 事实先查 knowledge/context/codex-reference.md
- 章末附"同一问题，`codex` 怎么做"参照小节
- 中文写作，成稿落至 `book/manuscript/ch11-sandbox.md`

## 边界

### 允许修改
- book/manuscript/ch11-sandbox.md
- book/knowledge/context/tools.md
- book/knowledge/context/codex-reference.md

### 禁止做
- 不修改 crates/ 下任何源码
- 不使用无 file:line 溯源的架构性断言
- 单段源码粘贴不超过 30 行
- 不提供绕过沙箱的方法细节；不重复 ch4 的审批编排（交叉引用）

## 完成条件

场景: 威胁模型刻画完整
  测试: ai_review_ch11_threat
  假设 读者混淆"权限审批"与"沙箱"
  当 读者读完动机一节
  那么 能说出两者各防什么（模型误操作 vs 被注入的恶意执行）、为何都需要

场景: 文件面机制准确
  测试: ai_review_ch11_fs
  假设 读者对照 xai-grok-sandbox 源码阅读
  当 读者核对文中每一处 `file:line` 引用
  那么 nono/Landlock/Seatbelt 统一、进程级一次应用、deny 内核强制的描述与源码一致

场景: 网络面机制准确
  测试: ai_review_ch11_net
  假设 读者读 child_net 小节
  当 读者核对引用
  那么 "进程自身放行 LLM 流量、子进程 seccomp 逐个阻断"的分面理由与实现一致

场景: codex 参照小节到位
  测试: ai_review_ch11_codex_compare
  假设 章末含 `codex` 参照小节
  当 读者读完参照小节
  那么 文中列出 codex 沙箱与 Grok Build 的至少 2 点取舍差异

场景: 篇幅与结构达标
  测试: check_ch11_structure
  假设 成稿位于 `book/manuscript/ch11-sandbox.md`
  当 编辑运行 book/tools/check_chapter.py
  那么 正文字数在 8000-15000 之间、含至少 1 张示意图、至少 5 处 file:line 引用、
      章末含"设计要点回顾"清单

场景: 引用溯源失败被拒稿
  测试: check_ch11_citation_validity
  假设 文中存在指向 crates/ 的 `file:line` 引用
  当 任一引用指向不存在的文件或行号超出文件长度
  那么 结构检查返回非零退出码并列出失效引用

## 排除范围

- 权限审批流程（ch4 已述）、PlanEditGate（ch4）、hooks 拦截（ch17）、
  沙箱绕过技术细节（安全红线）
