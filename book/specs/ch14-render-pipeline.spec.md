spec: task
name: "ch14-render-pipeline"
inherits: project
tags: [book, chapter, tui, rendering]
---

## 意图

撰写《第 14 章：增量渲染管线》。读者是中高级工程师；本章讲清 TUI 的高性能渲染：
fork 的 ratatui inline Terminal、diff flush 返回变更信号、零变更保护光标闪烁、
BeginSynchronizedUpdate 防闪烁、LayoutCache 惰性视口测量、OSC 8 超链接参与 diff。

## 已定决策

- 主轴：xai-ratatui-inline 的 diff-flush 管线与 cursor blink 保护
- 覆盖 render/draw.rs 绕过 ratatui try_draw 的手动 autoresize→flush→swap
- 覆盖 synchronized update、LayoutCache/compute_paint_window 脏标记、display_refresh 自适应帧率、RIS resize
- 覆盖为什么 fork ratatui（inline viewport、flush 变更信号、OSC 8 diff）
- 所有架构性陈述带 file:line 引用；codex 事实先查 knowledge/context/codex-reference.md
- 章末附"同一问题，codex 怎么做"参照小节
- 中文写作，成稿落至 book/manuscript/ch14-render-pipeline.md

## 边界

### 允许修改
- book/manuscript/ch14-render-pipeline.md
- book/knowledge/context/tui.md
- book/knowledge/context/codex-reference.md

### 禁止做
- 不修改 crates/ 下任何源码
- 不使用无 file:line 溯源的架构性断言
- 单段源码粘贴不超过 30 行
- 不重复 ch13 事件循环、ch15 markdown、ch16 终端图像（交叉引用）

## 完成条件

场景: 性能动机完整
  测试: ai_review_ch14_motivation
  假设 读者不了解终端增量渲染
  当 读者读完动机一节
  那么 能说出终端渲染的至少 2 个性能约束（全量重绘代价、光标闪烁副作用）

场景: diff flush 管线准确
  测试: ai_review_ch14_flush
  假设 读者对照 xai-ratatui-inline 源码阅读
  当 读者核对文中每一处 file:line 引用
  那么 flush 返回变更信号、零变更不发光标命令的机制与源码一致

场景: cursor blink 保护成立
  测试: ai_review_ch14_cursor
  假设 文中含 cursor blink 小节
  当 读者读完该节
  那么 能解释 30fps 下发光标命令为何重置闪烁计时器、零变更信号如何规避

场景: codex 参照小节到位
  测试: ai_review_ch14_codex_compare
  假设 章末含 codex 参照小节
  当 读者读完参照小节
  那么 文中列出 codex 渲染与 Grok Build 的至少 2 点取舍差异

场景: 篇幅与结构达标
  测试: check_ch14_structure
  假设 成稿位于 book/manuscript/ch14-render-pipeline.md
  当 编辑运行 book/tools/check_chapter.py
  那么 正文字数在 8000-15000 之间、含至少 1 张示意图、至少 5 处 file:line 引用、
      章末含"设计要点回顾"清单

场景: 引用溯源失败被拒稿
  测试: check_ch14_citation_validity
  假设 文中存在指向 crates/ 的 file:line 引用
  当 任一引用指向不存在的文件或行号超出文件长度
  那么 结构检查返回非零退出码并列出失效引用

## 排除范围

- 事件循环（ch13）、markdown/mermaid 渲染（ch15）、终端图像协议/TTY（ch16）
