spec: task
name: "ch17-tool-search"
inherits: project
tags: [book, chapter, tools, mcp, context, cache]
---

## 意图

为《第 17 章：扩展系统》增补一节《工具太多时：把工具表变成可搜索的二级存储》。
读者是中高级工程师。本节讲 MCP 在模型侧最关键、17.2 未覆盖的一层：Grok Build
不把所有 MCP 工具 schema 塞进每一轮采样，而是常驻两个稳定元工具——`search_tool`
（BM25 检索隐藏工具、返回其 input schema）与 `use_tool`（动态分发到真正的 MCP
工具）。提炼通用模式"全部能力 ≠ 全部进上下文"，并点出它同时解决上下文成本、
KV-cache 稳定性与动态扩展。与 17.2（MCP 依赖隔离/OAuth/安全）互补不重复。

## 已定决策

- 落点：`book/manuscript/ch17-extensions.md` 新增一节，编号 `17.3`（紧接 17.2 MCP），
  现 17.3–17.8 顺延为 17.4–17.9；同步更新"设计要点回顾"引用
- 采样只发内置工具、排除 MCP 工具，以 `sampler_turn.rs` 的
  `tool_definitions_builtins_only()` 为证
- `search_tool` 以 BM25 检索、返回 name/description/input_schema 为证；先走精确名
  快路径（限定名或裸名）再退回 BM25（tool_index.rs）
- `use_tool` 动态分发、并说明"跨 turn 保持工具集稳定、避免新 MCP 工具上线打断 KV
  cache"，以 use_tool/mod.rs 头注为证
- 提炼模式：常驻元工具 + 按需检索 schema + 二次动态分发
- 所有架构性陈述带 `file:line` 引用；中文；含 1 张 mermaid（search→use 两跳）
- 净新增约 1800–2600 字符

## 边界

### 允许修改
- book/manuscript/ch17-extensions.md
- book/specs/ch17-tool-search.spec.md
- book/knowledge/context/extensions.md

### 禁止做
- 不修改 crates/ 下任何源码
- 不使用无 file:line 溯源的架构性断言
- 不重复 17.2 的 MCP 依赖隔离 / OAuth / 令牌存储内容
- 单段源码粘贴不超过 30 行

## 完成条件

场景: 采样排除 MCP 工具讲解准确
  测试: ai_review_ch17_search_sampling
  假设 读者对照 sampler_turn.rs 阅读
  当 读者读完"为什么不全量塞进上下文"一段
  那么 能说出采样只发送内置工具定义、MCP 工具不进每轮上下文

场景: search_tool 检索与返回讲解准确
  测试: ai_review_ch17_search_tool
  假设 读者对照 search_tool 与 tool_index 源码阅读
  当 读者读完 search_tool 一段
  那么 能说出它先精确名命中、再 BM25 检索，并返回工具名/描述/input schema

场景: use_tool 分发与缓存稳定性讲解准确
  测试: ai_review_ch17_use_tool
  假设 读者对照 use_tool/mod.rs 阅读
  当 读者读完 use_tool 一段
  那么 能说出它动态分发到 MCP 工具，且常驻元工具让工具集跨 turn 稳定、不打断 KV cache

场景: 与 17.2 互补不重复
  测试: ai_review_ch17_search_crossref
  假设 17.2 已讲 MCP 依赖隔离与安全
  当 读者读完本节
  那么 本节讲"MCP 工具如何按需进模型上下文"，与 17.2"如何隔离 MCP"无实质重复

场景: 篇幅与结构达标
  测试: check_ch17_search_structure
  假设 成稿位于 book/manuscript/ch17-extensions.md
  当 编辑运行 book/tools/check_chapter.py
  那么 本节含至少 1 张 mermaid、至少 3 处 file:line 引用，且全章仍满足章级门禁

场景: 引用溯源失败被拒稿
  测试: check_ch17_search_citation_validity
  假设 本节存在指向 crates/ 的 `file:line` 引用
  当 任一引用指向不存在的文件或行号超出文件长度
  那么 结构检查返回非零退出码并列出失效引用

## 排除范围

- MCP 依赖隔离、OAuth、令牌存储（17.2 已覆盖）
- BM25 算法本身的实现细节、FNV-1a 哈希内部
- Hooks / 插件市场 / Skills（本章其它节）
