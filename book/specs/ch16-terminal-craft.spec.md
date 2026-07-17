spec: task
name: "ch16-terminal-craft"
inherits: project
tags: [book, chapter, tui, terminal]
---

## 意图

撰写《第 16 章：终端工程学》。读者是中高级工程师；本章收束 TUI 部分的"与真实
终端打交道"的硬核细节：Kitty/iTerm2 图像协议、终端能力探测、TTY 卫生与进程
作用域（子进程 detach 防喷转义码、PID-reuse 安全的 kill_all）、tty 控制权交接。

## 已定决策

- 主轴之一：图像内联（Kitty graphics protocol / iTerm2，运行时探测）
- 主轴之二：TTY 卫生（xai-tty-utils + ProcessScope，Weak-keyed registry 防 PID 复用）
- 覆盖终端能力探测（truecolor/OSC52/图像协议）
- 覆盖 tty 交接（$EDITOR/$PAGER 挂起，承接 ch13/ch14 让出的细节）
- 所有架构性陈述带 file:line 引用；codex 事实先查 knowledge/context/codex-reference.md
- 章末附"同一问题，codex 怎么做"参照小节
- 中文写作，成稿落至 book/manuscript/ch16-terminal-craft.md

## 边界

### 允许修改
- book/manuscript/ch16-terminal-craft.md
- book/knowledge/context/tui.md
- book/knowledge/context/codex-reference.md

### 禁止做
- 不修改 crates/ 下任何源码
- 不使用无 file:line 溯源的架构性断言
- 单段源码粘贴不超过 30 行
- 不重复 ch14 diff 渲染、ch15 mermaid PNG（交叉引用）

## 完成条件

场景: 主题动机完整
  测试: ai_review_ch16_motivation
  假设 读者低估"与终端打交道"的复杂度
  当 读者读完动机一节
  那么 能说出终端工程的至少 2 类硬问题（能力碎片化、进程/TTY 卫生）

场景: 图像协议准确
  测试: ai_review_ch16_image
  假设 读者对照源码阅读
  当 读者核对文中每一处 file:line 引用
  那么 Kitty/iTerm2 协议探测与内联的描述与源码一致

场景: TTY 卫生与进程作用域准确
  测试: ai_review_ch16_ttyhygiene
  假设 文中含 ProcessScope 小节
  当 读者读完该节
  那么 能解释 detach 防喷转义码、Weak-keyed registry 如何做 PID-reuse 安全 kill_all

场景: codex 参照小节到位
  测试: ai_review_ch16_codex_compare
  假设 章末含 codex 参照小节
  当 读者读完参照小节
  那么 文中列出 codex 终端处理与 Grok Build 的至少 2 点取舍差异

场景: 篇幅与结构达标
  测试: check_ch16_structure
  假设 成稿位于 book/manuscript/ch16-terminal-craft.md
  当 编辑运行 book/tools/check_chapter.py
  那么 正文字数在 8000-15000 之间、含至少 1 张示意图、至少 5 处 file:line 引用、
      章末含"设计要点回顾"清单

场景: 引用溯源失败被拒稿
  测试: check_ch16_citation_validity
  假设 文中存在指向 crates/ 的 file:line 引用
  当 任一引用指向不存在的文件或行号超出文件长度
  那么 结构检查返回非零退出码并列出失效引用

## 排除范围

- diff 渲染管线（ch14）、mermaid PNG 引擎（ch15）、事件循环（ch13）
