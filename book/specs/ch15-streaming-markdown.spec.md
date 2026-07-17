spec: task
name: "ch15-streaming-markdown"
inherits: project
tags: [book, chapter, tui, markdown, mermaid]
---

## 意图

撰写样章《第 15 章：流式 Markdown——为 LLM 输出而生的增量渲染器》。
读者是中高级工程师；本章通过 xai-grok-markdown 与 xai-grok-mermaid 两个 crate，
讲清"在终端里实时渲染一个正在生成中的 markdown 文档"的完整设计空间。

## 已定决策

- 主轴案例：`checkpoint` 冻结机制（O(N²)→O(N)），先讲朴素方案为何不可行，再讲解法
- mermaid 讲双路径（盒绘内联 vs 纯 Rust PNG 引擎）及`子进程`崩溃隔离
- 所有架构性陈述带 `file:line` 引用，事实以 book/knowledge/context/tui.md 与调研素材为准
- 章末附"同一问题，`codex` 怎么做"参照小节
- 中文写作，成稿落至 `book/manuscript/ch15-streaming-markdown.md`

## 边界

### 允许修改
- book/manuscript/ch15-streaming-markdown.md
- book/knowledge/context/tui.md

### 禁止做
- 不修改 crates/ 下任何源码
- 不使用无 file:line 溯源的架构性断言
- 单段源码粘贴不超过 30 行

## 完成条件

场景: 问题动机完整
  测试: ai_review_ch15_motivation
  假设 读者未接触过流式渲染且已知"每 token 全量重渲"的朴素方案
  当 读者读完本章第一节
  那么 读者能复述全量重渲的 O(N²) 成本来源与终端场景的三个额外约束

场景: checkpoint 机制讲解准确
  测试: ai_review_ch15_checkpoint_accuracy
  假设 读者对照 streaming.rs 与 checkpoint.rs 源码阅读，文中含 `checkpoint` 机制主轴案例
  当 读者核对文中每一处 `file:line` 引用
  那么 引用与源码一致，且"仅 depth=0 建 checkpoint"的原因有代码或注释佐证

场景: mermaid 崩溃隔离论证成立
  测试: ai_review_ch15_mermaid_isolation
  层级: 章节事实核查（AI 判定 + 人工抽查）
  假设 读者关心不可信输入的处理，文中含`子进程`隔离小节
  当 读者读完 mermaid 一节
  那么 文中解释了 panic=abort 使 catch_unwind 失效的机制与子进程 + wall-clock 超时的选型理由

场景: codex 参照小节到位
  测试: ai_review_ch15_codex_compare
  假设 读者想横向对比，章末含 `codex` 参照小节
  当 读者读完参照小节
  那么 文中列出 codex 在同一问题上至少 2 点取舍差异

场景: 篇幅与结构达标
  测试: check_ch15_structure
  假设 成稿位于 `book/manuscript/ch15-streaming-markdown.md`
  当 编辑运行结构检查
  那么 正文字数在 8000-15000 之间、含至少 1 张示意图、至少 5 处 file:line 引用、
      章末含"设计要点回顾"清单

场景: 引用溯源失败被拒稿
  测试: check_ch15_citation_validity
  假设 文中存在指向 crates/ 的 `file:line` 引用
  当 任一引用指向不存在的文件或行号超出文件长度
  那么 结构检查返回非零退出码并列出失效引用

## 排除范围

- scrollback/渲染管线细节（ch13/ch14 主题，仅交叉引用）
- Kitty/iTerm2 图像协议细节（ch16 主题）
- 性能实测 benchmark（引用仓库内已有测试/注释即可）
