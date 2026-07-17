spec: task
name: "ch12-porting"
inherits: project
tags: [book, chapter, tools, porting, legal]
---

## 意图

撰写《第 12 章：拿来主义与归一层》。读者是中高级工程师；本章讲清如何把两个
外部开源项目（openai/codex、sst/opencode）的工具实现移植进同一代码库并共存：
移植的工程手法（切 I/O 边界、保语义并实现）、许可合规（Apache-2.0 §4(b) 变更
声明、MIT）、以及第 8 章 taxonomy 归一层如何抹平三家方言。

## 已定决策

- 主轴：移植的系统性工程原则（第 9 章已见 apply_patch/edit 局部，本章总述）
- 覆盖 codex（Apache-2.0）与 opencode（MIT）各移植了哪些工具、改了什么
- 覆盖 THIRD_PARTY_NOTICES 的合规实践（§4(b) change notice、license 文本）
- 覆盖归一层：ToolNamespace/presentation_name/x.ai/tool 如何让三方言共存（引用 ch8）
- 所有架构性陈述带 `file:line` 引用；codex/opencode 事实先查 knowledge/context/codex-reference.md
- 本章是"参照系"主题本身，无需独立 codex 小节；但需对比"移植进来" vs "原生"的差异
- 中文写作，成稿落至 `book/manuscript/ch12-porting.md`

## 边界

### 允许修改
- book/manuscript/ch12-porting.md
- book/knowledge/context/tools.md
- book/knowledge/context/codex-reference.md

### 禁止做
- 不修改 crates/ 下任何源码
- 不使用无 file:line 溯源的架构性断言
- 单段源码粘贴不超过 30 行
- 不重复 ch8 taxonomy 机制细节、ch9 编辑工具内部（交叉引用）

## 完成条件

场景: 移植动机与手法完整
  测试: ai_review_ch12_motivation
  假设 读者好奇"为何不自己写而要移植"
  当 读者读完动机一节
  那么 能说出移植的收益（对齐模型训练分布、复用成熟实现）与核心工程手法
      （切 I/O 边界、方言压薄壳、核心下沉）

场景: 移植清单准确
  测试: ai_review_ch12_inventory
  假设 读者对照 implementations/ 与 THIRD_PARTY_NOTICES 阅读
  当 读者核对文中每一处 `file:line` 引用
  那么 codex/opencode 各移植的工具清单、改动点与源码/notices 一致

场景: 许可合规讲解准确
  测试: ai_review_ch12_license
  假设 读者关心开源合规
  当 读者读完合规一节
  那么 能说出 Apache-2.0 §4(b) 变更声明义务与 MIT 归因的具体履行方式

场景: 归一层作用清晰
  测试: ai_review_ch12_taxonomy
  假设 读者已读 ch8
  当 读者读完归一一节
  那么 能解释三方言如何在同一 taxonomy 下对 UI/模型呈现为统一工具

场景: 篇幅与结构达标
  测试: check_ch12_structure
  假设 成稿位于 `book/manuscript/ch12-porting.md`
  当 编辑运行 book/tools/check_chapter.py
  那么 正文字数在 8000-15000 之间、含至少 1 张示意图、至少 5 处 file:line 引用、
      章末含"设计要点回顾"清单

场景: 引用溯源失败被拒稿
  测试: check_ch12_citation_validity
  假设 文中存在指向 crates/ 的 `file:line` 引用
  当 任一引用指向不存在的文件或行号超出文件长度
  那么 结构检查返回非零退出码并列出失效引用

## 排除范围

- taxonomy 类型机制（ch8）、编辑工具算法（ch9）、单个工具运行时（ch8）
