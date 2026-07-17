spec: task
name: "ch05-compaction"
inherits: project
tags: [book, chapter, runtime, compaction, context]
---

## 意图

撰写《第 5 章：上下文管理与压缩》。读者是中高级工程师；本章讲清有限上下文窗口下
agent 如何存活：token 记账与阈值触发、compaction-core 的三种压缩策略、trait 缝
解耦让同一引擎服务多个宿主的库化设计。

## 已定决策

- 主轴案例：crates/common/xai-grok-compaction 的 trait 缝设计与三种压缩风格
  （code_compaction 全量替换 / intra_compaction 保尾 / inter_compaction 分块）
- 覆盖触发机制：`should_auto_compact` + xai_token_estimation 阈值
- 覆盖 host 侧编排（session/compaction.rs）与压缩后的会话状态衔接
- 所有架构性陈述带 `file:line` 引用；codex 事实先查 knowledge/context/codex-reference.md
- 章末附"同一问题，`codex` 怎么做"参照小节
- 中文写作，成稿落至 `book/manuscript/ch05-compaction.md`

## 边界

### 允许修改
- book/manuscript/ch05-compaction.md
- book/knowledge/context/runtime.md
- book/knowledge/context/codex-reference.md

### 禁止做
- 不修改 crates/ 下任何源码
- 不使用无 file:line 溯源的架构性断言
- 单段源码粘贴不超过 30 行
- 不深入 memory 系统（ch18 主题）；不重复 ch3/ch4 已详述内容

## 完成条件

场景: 压缩动机与设计空间完整
  测试: ai_review_ch05_motivation
  假设 读者未接触过上下文压缩
  当 读者读完动机一节
  那么 能说出为何不能简单截断历史、压缩要保什么（不变量）与可牺牲什么

场景: 三种压缩策略讲解准确
  测试: ai_review_ch05_strategies
  假设 读者对照 xai-grok-compaction 源码阅读
  当 读者核对文中每一处 `file:line` 引用
  那么 引用与源码一致，三种策略的适用场景与差异描述无误

场景: trait 缝库化设计成立
  测试: ai_review_ch05_traitseam
  假设 文中含 compaction-core 解耦小节
  当 读者读完该节
  那么 能解释 CompactionItem/ItemTokenCounter/CompactionSampler 三个 trait 各自
      抽象什么、为何该 crate 不依赖会话/采样类型

场景: codex 参照小节到位
  测试: ai_review_ch05_codex_compare
  假设 章末含 `codex` 参照小节
  当 读者读完参照小节
  那么 文中列出 codex 上下文管理与 Grok Build 的至少 2 点取舍差异

场景: 篇幅与结构达标
  测试: check_ch05_structure
  假设 成稿位于 `book/manuscript/ch05-compaction.md`
  当 编辑运行 book/tools/check_chapter.py
  那么 正文字数在 8000-15000 之间、含至少 1 张示意图、至少 5 处 file:line 引用、
      章末含"设计要点回顾"清单

场景: 引用溯源失败被拒稿
  测试: check_ch05_citation_validity
  假设 文中存在指向 crates/ 的 `file:line` 引用
  当 任一引用指向不存在的文件或行号超出文件长度
  那么 结构检查返回非零退出码并列出失效引用

## 排除范围

- memory/dream 系统（ch18）、会话持久化（ch6）、采样器内部（ch3）
