spec: task
name: "ch19-resilience-engineering"
inherits: project
tags: [book, chapter, resilience, concurrency, admission, circuit-breaker]
---

## 意图

新增《第 19 章：韧性工程——准入、熔断与取消泄漏》，作为第六部"Rust 工程纪律"的首章。
现书讲透了架构与工具，但没讲 Grok Build 如何用 Rust 把过载、级联失败、取消泄漏变成
可验证约束。本章解剖三块：Computer Hub SDK 的三层信号量准入（session→connection→
global、共享 deadline、过载回 tool_busy）、xai-circuit-breaker 的 Closed/Open/HalfOpen
状态机（滑窗+最小样本、原子快路径、可注入时钟）、以及"半开探针被取消 → 永占名额 →
过期租约兜底"这条取消泄漏防线。核心诚实点：这些机制目前**尚未接入主 agent 循环**
（SamplerActor），而 ch03 自己就标了那里是第一个要补 admission 的位置——"同仓已解、
主干未采"。

## 已定决策

- 落点：新增 `book/manuscript/ch19-resilience-engineering.md`；SUMMARY.md 在第五部后、
  附录前新增"# 第六部：Rust 工程纪律"含本章；preface 知识地图补第六部
- 三层准入以 admission.rs 顶注 + 常量（session 16 / conn 256 / global 1024 /
  wait_timeout 3s / tool_busy -32016）为证
- 熔断状态机 + 原子镜像快路径以 breaker.rs:1 为证；取消泄漏过期租约以
  breaker.rs 的 `probe_claimed_at_millis` 注释为证
- **诚实红线**：xai-circuit-breaker 与三层准入未被 xai-grok-shell/xai-grok-sampler
  依赖（未接入主循环）；与 ch03:199"SamplerActor 并发无上限、没 semaphore"对照
- 章末含"同一问题，codex 怎么做"与"模式提炼"，遵循全书章节模板（定位锚 + 版本演化）
- 虚拟时钟测试只作引子，指向新增测试附录（P0-②）
- 所有架构性陈述带 `file:line`；中文；含至少 1 张 mermaid；≥5 处引用

## 边界

### 允许修改
- book/manuscript/ch19-resilience-engineering.md
- book/manuscript/SUMMARY.md
- book/manuscript/preface.md
- book/specs/ch19-resilience-engineering.spec.md
- book/knowledge/context/resilience.md

### 禁止做
- 不修改 crates/ 下任何源码
- 不使用无 file:line 溯源的架构性断言
- **不声称三层准入/熔断器已接入 SamplerActor 或主 agent 循环**（源码未依赖）
- 不重编号 1–18 章（本章追加为末章）
- 单段源码粘贴不超过 30 行

## 完成条件

场景: 三层准入讲解准确
  测试: ai_review_ch19_admission
  假设 读者对照 admission.rs 阅读
  当 读者读完准入一节
  那么 能说出 session→connection→global 固定顺序、共享 deadline（最长等待=一次 timeout 非 3×）、过载回 tool_busy 而非静默丢弃

场景: 熔断状态机与原子快路径讲解准确
  测试: ai_review_ch19_breaker
  假设 读者对照 breaker.rs 阅读
  当 读者读完熔断一节
  那么 能说出 Closed/Open/HalfOpen 三态、滑窗+最小样本、is_open() 无锁原子镜像、可注入时钟

场景: 取消泄漏与过期租约
  测试: ai_review_ch19_cancel_leak
  假设 读者对照 breaker.rs 的探针租约注释阅读
  当 读者读完取消泄漏一节
  那么 能说出半开探针 future 被取消会永占名额、过期租约让丢失探针最多延迟一个冷却期恢复

场景: 诚实红线——未接入主循环
  测试: ai_review_ch19_not_wired
  假设 存在"Grok agent 循环已有熔断/准入"的误解
  当 读者读完对照一节
  那么 文中明确这些机制尚未接入 SamplerActor，并与 ch03:199 的"无 admission control"对照

场景: 章节模板结构达标
  测试: check_ch19_structure
  假设 成稿位于 book/manuscript/ch19-resilience-engineering.md
  当 编辑运行 book/tools/check_chapter.py
  那么 含定位锚、至少 1 张 mermaid、至少 5 处 file:line 引用、"设计要点回顾"与"版本演化说明"

场景: 引用溯源失败被拒稿
  测试: check_ch19_citation_validity
  假设 本章存在指向 crates/ 的 `file:line` 引用
  当 任一引用指向不存在的文件或行号超出文件长度
  那么 结构检查返回非零退出码并列出失效引用

## 排除范围

- 虚拟时钟测试方法论（新增附录，P0-②）
- 具体退避算法参数调优
- Computer Hub SDK 的其余非准入部分
