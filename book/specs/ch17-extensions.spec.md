spec: task
name: "ch17-extensions"
inherits: project
tags: [book, chapter, extensions, mcp, hooks, plugins]
---

## 意图

撰写《第 17 章：MCP、Hooks 与插件生态》。读者是中高级工程师；本章讲清 agent 的
可扩展性设计：MCP 外部工具接入（含版本冲突隔离）、Hooks 生命周期拦截、插件市场
分发（防路径穿越）、子代理解析的纯逻辑层、Skills 提示包。

## 已定决策

- 覆盖 MCP（xai-grok-mcp）：rmcp 集成、reqwest 版本冲突隔离、OAuth 流、退避绕过 bug
- 覆盖 Hooks（xai-grok-hooks）：生命周期事件、pre_tool_use 可 deny/allow、fail-open
- 覆盖插件市场（xai-grok-plugin-marketplace）：git 源、MarketplaceRelativePath 防穿越
- 覆盖子代理解析（xai-grok-subagent-resolution）：纯逻辑层、优先级 override>role>persona>parent
- 覆盖 Skills（SKILL.md 提示包）
- 所有架构性陈述带 file:line 引用；codex 事实先查 knowledge/context/codex-reference.md
- 章末附"同一问题，codex 怎么做"参照小节
- 中文写作，成稿落至 book/manuscript/ch17-extensions.md

## 边界

### 允许修改
- book/manuscript/ch17-extensions.md
- book/knowledge/context/tools.md
- book/knowledge/context/platform.md
- book/knowledge/context/codex-reference.md

### 禁止做
- 不修改 crates/ 下任何源码
- 不使用无 file:line 溯源的架构性断言
- 单段源码粘贴不超过 30 行
- 不重复 ch8 工具抽象、ch4 审批（交叉引用）

## 完成条件

场景: 可扩展性动机完整
  测试: ai_review_ch17_motivation
  假设 读者思考"agent 为何需要多种扩展机制"
  当 读者读完动机一节
  那么 能说出至少 3 种扩展点（外部工具/生命周期钩子/分发/子代理）各自解决什么

场景: MCP 集成准确
  测试: ai_review_ch17_mcp
  假设 读者对照 xai-grok-mcp 源码阅读
  当 读者核对文中每一处 file:line 引用
  那么 rmcp 集成、版本冲突隔离、OAuth、退避绕过的描述与源码一致

场景: Hooks 与插件安全准确
  测试: ai_review_ch17_security
  假设 文中含 hooks/插件小节
  当 读者读完该节
  那么 能解释 pre_tool_use 拦截语义、fail-open 取舍、MarketplaceRelativePath 防穿越

场景: codex 参照小节到位
  测试: ai_review_ch17_codex_compare
  假设 章末含 codex 参照小节
  当 读者读完参照小节
  那么 文中列出 codex 扩展机制与 Grok Build 的至少 2 点取舍差异

场景: 篇幅与结构达标
  测试: check_ch17_structure
  假设 成稿位于 book/manuscript/ch17-extensions.md
  当 编辑运行 book/tools/check_chapter.py
  那么 正文字数在 8000-15000 之间、含至少 1 张示意图、至少 5 处 file:line 引用、
      章末含"设计要点回顾"清单

场景: 引用溯源失败被拒稿
  测试: check_ch17_citation_validity
  假设 文中存在指向 crates/ 的 file:line 引用
  当 任一引用指向不存在的文件或行号超出文件长度
  那么 结构检查返回非零退出码并列出失效引用

## 排除范围

- 工具类型抽象（ch8）、审批权限（ch4）、沙箱（ch11）、企业配置治理（ch18）
