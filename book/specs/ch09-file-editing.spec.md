spec: task
name: "ch09-file-editing"
inherits: project
tags: [book, chapter, tools, editing]
---

## 意图

撰写《第 9 章：文件编辑的艺术》。读者是中高级工程师；本章对比同一代码库内共存的
四种"让 LLM 改文件"方案——grok_build 的 search_replace、hashline 的三种抗漂移
锚点、codex 移植的 apply_patch、opencode 移植的 edit——回答"为什么这个问题
至今没有唯一正解"，并提炼各方案的失效模式与适用域。

## 已定决策

- 主轴：四方案横向对比（定位方式、歧义处理、失败模式、对模型的要求）
- 重点深挖 hashline 的三种锚点方案（ContentOnly/ChunkFingerprint/CheckpointChain）
  ——这是本仓库独有的创新点
- 覆盖"读后编辑"约束（skip_read_before_edit、与 ch8 requirements 的衔接）
- 所有架构性陈述带 `file:line` 引用；codex 事实先查 knowledge/context/codex-reference.md
- 章末"同一问题，codex 怎么做"可精简（apply_patch 本身就是移植的 codex 方案，
  对比已内嵌于正文）——但需说明 codex 原生环境与移植环境的差异
- 中文写作，成稿落至 `book/manuscript/ch09-file-editing.md`

## 边界

### 允许修改
- book/manuscript/ch09-file-editing.md
- book/knowledge/context/tools.md
- book/knowledge/context/codex-reference.md

### 禁止做
- 不修改 crates/ 下任何源码
- 不使用无 file:line 溯源的架构性断言
- 单段源码粘贴不超过 30 行
- 不深入移植的法务/工程流程（ch12 主题）、不讲 checkpoint/回退（ch10）

## 完成条件

场景: 问题空间刻画完整
  测试: ai_review_ch09_problem
  假设 读者未思考过"LLM 编辑文件为什么难"
  当 读者读完动机一节
  那么 能说出至少 3 种编辑失败模式（定位歧义、内容漂移、转义/空白陷阱等）
      及其对方案设计的约束

场景: 四方案对比准确
  测试: ai_review_ch09_compare
  假设 读者对照 implementations/ 源码阅读
  当 读者核对文中每一处 `file:line` 引用
  那么 四方案的定位机制、失败处理、参数形态描述与源码一致

场景: hashline 锚点机制讲解准确
  测试: ai_review_ch09_hashline
  假设 读者对照 hashline 源码阅读
  当 读者读完 hashline 一节
  那么 三种锚点方案的原理、各自防什么漂移、如何选择的描述与源码一致

场景: 移植环境差异说明到位
  测试: ai_review_ch09_port_context
  假设 读者想知道移植的 apply_patch 与 codex 原生版的关系
  当 读者读完相关小节
  那么 了解移植保留了什么、适配了什么（至少 2 点）

场景: 篇幅与结构达标
  测试: check_ch09_structure
  假设 成稿位于 `book/manuscript/ch09-file-editing.md`
  当 编辑运行 book/tools/check_chapter.py
  那么 正文字数在 8000-15000 之间、含至少 1 张示意图、至少 5 处 file:line 引用、
      章末含"设计要点回顾"清单

场景: 引用溯源失败被拒稿
  测试: check_ch09_citation_validity
  假设 文中存在指向 crates/ 的 `file:line` 引用
  当 任一引用指向不存在的文件或行号超出文件长度
  那么 结构检查返回非零退出码并列出失效引用

## 排除范围

- 移植的工程与法务实践（ch12）、checkpoint/hunk-tracker（ch10）、
  权限门（ch11）、工具类型抽象（ch8 已述）
