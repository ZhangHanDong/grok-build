spec: task
name: "ch13-tui-eventloop"
inherits: project
tags: [book, chapter, tui, event-loop]
---

## 意图

撰写《第 13 章：事件循环与 AppView》。读者是中高级工程师；本章讲清 TUI 的整体
架构：极薄的 tokio::select! 事件循环、AppView 状态中枢、scrollback 组织、
全屏 vs --minimal 双渲染模式，以及打破 crate 循环依赖的 IoC 函数指针 seam。

## 已定决策

- 主轴：event_loop.rs 的 select 循环 + AppView 委托、scrollback/ 组织
- 覆盖双渲染模式（ScrollbackPane vs minimal insert_before）与 minimal_hook 函数指针 seam
- 覆盖 scrollback 的 IndexMap 保序+O(1)、block 类型、sticky 粘性头
- 所有架构性陈述带 file:line 引用；codex 事实先查 knowledge/context/codex-reference.md
- 章末附"同一问题，codex 怎么做"参照小节
- 中文写作，成稿落至 book/manuscript/ch13-tui-eventloop.md

## 边界

### 允许修改
- book/manuscript/ch13-tui-eventloop.md
- book/knowledge/context/tui.md
- book/knowledge/context/codex-reference.md

### 禁止做
- 不修改 crates/ 下任何源码
- 不使用无 file:line 溯源的架构性断言
- 单段源码粘贴不超过 30 行
- 不深入渲染管线 diff（ch14）、markdown/mermaid（ch15）、图像协议（ch16）

## 完成条件

场景: 架构动机完整
  测试: ai_review_ch13_motivation
  假设 读者不了解 TUI 事件驱动架构
  当 读者读完动机一节
  那么 能说出"极薄事件循环 + 集中状态中枢"相比散落状态的至少 2 个好处

场景: 事件循环与状态中枢准确
  测试: ai_review_ch13_loop
  假设 读者对照 pager 源码阅读
  当 读者核对文中每一处 file:line 引用
  那么 select 分支、AppView 委托、scrollback 组织的描述与源码一致

场景: 双渲染模式与 seam 成立
  测试: ai_review_ch13_seam
  假设 文中含双渲染模式小节
  当 读者读完该节
  那么 能解释 minimal 模式为何用函数指针 seam 避免 crate 循环依赖

场景: codex 参照小节到位
  测试: ai_review_ch13_codex_compare
  假设 章末含 codex 参照小节
  当 读者读完参照小节
  那么 文中列出 codex TUI 架构与 Grok Build 的至少 2 点取舍差异

场景: 篇幅与结构达标
  测试: check_ch13_structure
  假设 成稿位于 book/manuscript/ch13-tui-eventloop.md
  当 编辑运行 book/tools/check_chapter.py
  那么 正文字数在 8000-15000 之间、含至少 1 张示意图、至少 5 处 file:line 引用、
      章末含"设计要点回顾"清单

场景: 引用溯源失败被拒稿
  测试: check_ch13_citation_validity
  假设 文中存在指向 crates/ 的 file:line 引用
  当 任一引用指向不存在的文件或行号超出文件长度
  那么 结构检查返回非零退出码并列出失效引用

## 排除范围

- 渲染 diff 管线（ch14）、markdown/mermaid（ch15）、终端图像/TTY（ch16）
