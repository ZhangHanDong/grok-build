spec: task
name: "appendix-async-testing"
inherits: project
tags: [book, appendix, testing, async, virtual-time]
---

## 意图

新增《附录：如何测试异步状态机》。第 19 章的准入 deadline、熔断冷却窗口、退避序列都是
时序逻辑，最难测——睡真实时间会让测试又慢又 flaky。Grok Build 的答案是 tokio 虚拟时间
（`start_paused`），全仓 100+ 处、遍布 20+ 文件，是稳定方法论而非零星技巧。本附录提炼这套
方法：`start_paused = true` + `current_thread` flavor + 真实 dispatcher 循环 + 一个同时
观察生产状态与 wire 输出的 mock + 明确的 `settle()` 调度步数；以 MCP 重启退避推进到
t=1/5/21s 为工作实例。回答"如何测 timeout/debounce/backoff/重连/取消而不制造慢测试与
偶发失败"。

## 已定决策

- 落点：新增 `book/manuscript/appendix-async-testing.md`；SUMMARY.md 附录节新增一条
- MCP 重启退避推进以 mcp_restart.rs 的 `t=1s/5s/21s` + `pause`+`advance` 为证
- E2E 测试的四件套（start_paused / current_thread / 真实 dispatcher / mock 观察 wire）
  以 mcp_dispatcher_e2e_tests.rs 顶注为证
- `settle()` 以其定义（固定次数 `yield_now` 排空 spawn 任务、不推进时钟）为证
- 呼应第 19 章可注入 `Clock`（生产 SystemClock / 测试 MockClock），说明"注入时钟"是
  这套测试的接缝
- 所有引用用完整 `crates/...` 路径以便 cite_heal 校验；中文；含 1 张 mermaid
- 净新增约 2200–3000 字符；附录不套用章节"设计要点回顾/版本演化"模板

## 边界

### 允许修改
- book/manuscript/appendix-async-testing.md
- book/manuscript/SUMMARY.md
- book/specs/appendix-async-testing.spec.md

### 禁止做
- 不修改 crates/ 下任何源码
- 不使用无 file:line 溯源的架构性断言
- 不声称未验证的 start_paused 精确计数（用"100+ 处、20+ 文件"的量级表述）
- 单段源码粘贴不超过 30 行

## 完成条件

场景: 虚拟时间是方法论而非技巧
  测试: ai_review_appendix_async_scale
  假设 读者读完开头
  当 读者理解 start_paused 的分布
  那么 能说出它遍布全仓、用于系统性测试时序逻辑，而非零星使用

场景: 四件套讲解准确
  测试: ai_review_appendix_async_recipe
  假设 读者对照 mcp_dispatcher_e2e_tests.rs 阅读
  当 读者读完方法一节
  那么 能列出 start_paused + current_thread + 真实 dispatcher + 观察 wire 的 mock + settle 调度步数

场景: 退避工作实例
  测试: ai_review_appendix_async_backoff
  假设 读者对照 mcp_restart.rs 阅读
  当 读者读完实例
  那么 能说出退避序列被推进到 t=1/5/21s 而不睡真实时间

场景: settle 的确定性
  测试: ai_review_appendix_async_settle
  假设 读者对照 settle 定义阅读
  当 读者读完 settle 一段
  那么 能说出它用固定次数调度让 spawn 任务排空、且不推进 paused 时钟

场景: 结构达标
  测试: check_appendix_async_structure
  假设 成稿位于 book/manuscript/appendix-async-testing.md
  当 编辑运行 book/tools/check_chapter.py
  那么 含 1 张 mermaid、至少 3 处 file:line 引用（附录不要求"设计要点回顾"）

场景: 引用溯源失败被拒稿
  测试: check_appendix_async_citation_validity
  假设 本附录存在指向 crates/ 的 `file:line` 引用
  当 任一引用指向不存在的文件或行号超出文件长度
  那么 结构检查返回非零退出码并列出失效引用

## 排除范围

- property test / fuzz（正文已提及的其它测试形态）
- tokio 运行时内部实现
- 第 19 章韧性机制本身（本附录只讲如何测）
