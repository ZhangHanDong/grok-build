spec: task
name: "ch04-agentic-loop"
inherits: project
tags: [book, chapter, runtime, agent-loop]
---

## 意图

撰写《第 4 章：Agentic 循环——采样、工具与终止判定》。读者是中高级工程师；本章讲清
一个 turn 内部发生的一切：采样→解析工具调用→执行→再采样的循环如何组织、何时终止、
如何从错误中恢复，以及 goal 编排与 StructuredOutput 两个上层机制。

## 已定决策

- 主轴案例：turn.rs 的 agentic `loop` 与 `process_conversation_turn_with_recovery`
- 覆盖 goal 编排（`run_goal_round_end` 的 Continue/EndTurn 判定）
- 覆盖 StructuredOutput"假工具"+ jsonschema 校验 + 重试机制
- 覆盖工具调用执行管线 `execute_tool_calls` 的编排（并行？顺序？错误传播）——
  但不深入单个工具实现（第 8 章主题）
- 所有架构性陈述带 `file:line` 引用，事实以 book/knowledge/context/runtime.md 为基线
- 章末附"同一问题，`codex` 怎么做"参照小节
- 中文写作，成稿落至 `book/manuscript/ch04-agentic-loop.md`

## 边界

### 允许修改
- book/manuscript/ch04-agentic-loop.md
- book/knowledge/context/runtime.md

### 禁止做
- 不修改 crates/ 下任何源码
- 不使用无 file:line 溯源的架构性断言
- 单段源码粘贴不超过 30 行
- 不重复 ch3 已详述的 SessionActor 消息拓扑（交叉引用"详见第 3 章"）

## 完成条件

场景: 循环结构讲解准确
  测试: ai_review_ch04_loop
  假设 读者对照 turn.rs 源码阅读，文中含 agentic `loop` 主轴案例
  当 读者核对文中每一处 `file:line` 引用
  那么 引用与源码一致，循环的继续/终止条件枚举完整

场景: 错误恢复路径完整
  测试: ai_review_ch04_recovery
  假设 文中含 recovery 机制小节
  当 采样失败、工具失败、拒答三类情形被讨论
  那么 每类情形的处理路径都有代码佐证，无凭空推断

场景: StructuredOutput 机制成立
  测试: ai_review_ch04_structured
  假设 文中含 StructuredOutput 小节
  当 读者读完该节
  那么 能解释"假工具"如何对不支持原生约束的后端达成结构化输出、重试上限与失败语义

场景: codex 参照小节到位
  测试: ai_review_ch04_codex_compare
  假设 章末含 `codex` 参照小节
  当 读者读完参照小节
  那么 文中列出 codex turn 循环与 Grok Build 的至少 2 点取舍差异

场景: 篇幅与结构达标
  测试: check_ch04_structure
  假设 成稿位于 `book/manuscript/ch04-agentic-loop.md`
  当 编辑运行 book/tools/check_chapter.py
  那么 正文字数在 8000-15000 之间、含至少 1 张示意图、至少 5 处 file:line 引用、
      章末含"设计要点回顾"清单

场景: 引用溯源失败被拒稿
  测试: check_ch04_citation_validity
  假设 文中存在指向 crates/ 的 `file:line` 引用
  当 任一引用指向不存在的文件或行号超出文件长度
  那么 结构检查返回非零退出码并列出失效引用

## 排除范围

- SessionActor 拓扑（ch3）、compaction 触发细节（ch5）、单个工具实现（ch8）、
  权限/沙箱（ch11）、子代理解析（ch17）
