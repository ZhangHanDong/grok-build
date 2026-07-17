spec: task
name: "ch08-tool-abstraction"
inherits: project
tags: [book, chapter, tools, traits]
---

## 意图

撰写《第 8 章：两层工具抽象》。读者是中高级工程师；本章讲清工具系统的类型设计：
底层 xai-tool-runtime 的 RPITIT 零装箱 Tool trait 与 ToolDyn 类型擦除、流式契约，
上层 xai-grok-tools 的注册系统与依赖注入、taxonomy 归一，以及 Expr<T> 声明式
可用性表达式。

## 已定决策

- 主轴案例：`Tool` trait（关联类型 + 原生 async fn）与 `ToolDyn` 擦除边界的
  "人体工学 vs 对象安全"两难拆解
- 覆盖 ToolStream = [Progress*, Terminal] 流式契约与阻塞工具的默认适配
- 覆盖 ToolRegistryBuilder/Resources 依赖注入、tool_taxonomy 的 ToolKind/Namespace
- 覆盖 `Expr<T>` 三层布尔表达式（types/requirements.rs）
- 所有架构性陈述带 `file:line` 引用；codex 事实先查 knowledge/context/codex-reference.md
- 章末附"同一问题，`codex` 怎么做"参照小节
- 中文写作，成稿落至 `book/manuscript/ch08-tool-abstraction.md`

## 边界

### 允许修改
- book/manuscript/ch08-tool-abstraction.md
- book/knowledge/context/tools.md
- book/knowledge/context/codex-reference.md

### 禁止做
- 不修改 crates/ 下任何源码
- 不使用无 file:line 溯源的架构性断言
- 单段源码粘贴不超过 30 行
- 不深入单个工具的实现（ch9 编辑工具、ch12 移植工具）、不讲执行编排（ch4 已述）

## 完成条件

场景: 类型设计动机完整
  测试: ai_review_ch08_motivation
  假设 读者熟悉 #[async_trait] 装箱方案
  当 读者读完动机一节
  那么 能说出 RPITIT + 显式 Send 方案避免了什么成本、类型擦除为何仍然需要、
      两难如何被拆到两个层次分别解决

场景: trait 契约讲解准确
  测试: ai_review_ch08_trait
  假设 读者对照 xai-tool-runtime 源码阅读
  当 读者核对文中每一处 `file:line` 引用
  那么 Tool/ToolDyn/ToolStream 的描述与源码一致

场景: 注册与 taxonomy 讲解准确
  测试: ai_review_ch08_registry
  假设 读者对照 xai-grok-tools 源码阅读
  当 读者读完注册系统小节
  那么 Resources 注入、FinalizedToolset、ToolKind/Namespace 归一的描述与源码一致

场景: codex 参照小节到位
  测试: ai_review_ch08_codex_compare
  假设 章末含 `codex` 参照小节
  当 读者读完参照小节
  那么 文中列出 codex 工具抽象与 Grok Build 的至少 2 点取舍差异

场景: 篇幅与结构达标
  测试: check_ch08_structure
  假设 成稿位于 `book/manuscript/ch08-tool-abstraction.md`
  当 编辑运行 book/tools/check_chapter.py
  那么 正文字数在 8000-15000 之间、含至少 1 张示意图、至少 5 处 file:line 引用、
      章末含"设计要点回顾"清单

场景: 引用溯源失败被拒稿
  测试: check_ch08_citation_validity
  假设 文中存在指向 crates/ 的 `file:line` 引用
  当 任一引用指向不存在的文件或行号超出文件长度
  那么 结构检查返回非零退出码并列出失效引用

## 排除范围

- 单个工具实现（ch9/ch12）、执行编排与审批（ch4/ch11）、MCP 工具桥（ch17）
