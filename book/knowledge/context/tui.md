---
kind: context
title: TUI 层（第四部素材）
tags: [tui, rendering, markdown, mermaid, terminal]
sources:
  - crates/codegen/xai-grok-pager/src/app/event_loop.rs
  - crates/codegen/xai-grok-pager/src/app/app_view.rs
  - crates/codegen/xai-grok-pager/src/scrollback/
  - crates/codegen/xai-grok-pager/src/render/draw.rs
  - crates/codegen/xai-ratatui-inline/src/terminal.rs
  - crates/codegen/xai-grok-markdown/src/streaming.rs
  - crates/codegen/xai-grok-markdown/src/checkpoint.rs
  - crates/codegen/xai-grok-markdown/src/mermaid.rs
  - crates/codegen/xai-grok-mermaid/src/lib.rs
  - crates/codegen/xai-tty-utils/
stale: false
---

# TUI 层

## 架构（ch13）

- 事件循环 event_loop.rs：极薄 tokio::select!，只做 IO plumbing（终端事件、ACP 通道、
  spawned task 结果、动画 tick、热重载配置），全部委托 `AppView`（app_view.rs，万行级状态中枢）。
- scrollback/：state/（entries+scroll+selection+turn 导航，IndexMap 保序+O(1) 查找）、
  blocks（agent/thinking/tool/user 块类型）、render.rs（scratch-buffer）、sticky.rs（粘性 turn 头）。
- prompt：views/prompt_widget/，底层 fork 的 xai-ratatui-textarea。
- modal/views：60+ 文件，modal_window.rs 统一模态框架。
- 双渲染模式：全屏 ScrollbackPane vs `--minimal`（xai-grok-pager-minimal，已完成块经
  insert_before 打进终端原生 scrollback，仅留 pinned 活动区）。二者用函数指针 seam
  （minimal_hook）避免 crate 循环依赖，bin composition root 装配。【IoC seam 案例】

## 渲染管线（ch14）

增量 diff 渲染，核心是 fork 的 xai-ratatui-inline::Terminal（inline viewport 化）。
render/draw.rs：绕过 ratatui try_draw()，手动 autoresize→get_frame→flush→swap_buffers。
flush() 返回 bool 表示是否有 cell 变更——**零变更时不发 cursor 命令**，保留终端光标闪烁
（30fps 下 Show/MoveTo 会不断重置 500ms 闪烁计时器致光标常亮，专门修的 bug）。

其他：每帧 BeginSynchronizedUpdate/EndSynchronizedUpdate（tmux/zellij 防闪烁）；
LayoutCache + 惰性视口测量（compute_paint_window，脏标记 gaps_may_be_dirty，O(1) 高度查询）；
OSC 8 超链接折进 per-cell link layer 参与 diff；display_refresh 探测刷新率自适应帧率
（OnceLock 缓存）；resize 走 RIS 全量重渲染（终端 reflow 在 SIGWINCH 前已发生，不可预测）。

fork ratatui 的原因：上游 Terminal 面向全屏 alternate-screen；需要 inline viewport、
flush 变更信号、OSC 8 参与 cell diff、insert_before 写原生 scrollback。textarea 需要
element（paste/file-ref 原子块、稳定 ElementId）、软换行、剪贴板 trait。保留 MIT/Apache 头。

## 流式 Markdown 与 Mermaid（ch15 ★样章）

- xai-grok-markdown：LLM 流式输出的增量渲染器。checkpoint 冻结机制——仅在 top-level
  （depth=0）块边界建 checkpoint，冻结已渲染行，只重渲 tail，O(N²)→O(N)
  （streaming.rs、checkpoint.rs）。syntect 高亮、色阶降级（truecolor/256/16）、
  LaTeX→Unicode 近似（$E=mc^2$→E=mc²）。
- mermaid 双路径：(a) markdown/src/mermaid.rs 用 Unicode 盒绘字符把 flowchart/sequence/state
  内联画进文本网格；(b) xai-grok-mermaid 纯 Rust 引擎（vendored dagre mermaid-to-svg +
  resvg/usvg/tiny-skia）渲 PNG，绑定字体、无网络、确定性，仅供 OS viewer 打开。
- 崩溃隔离：untrusted 模型输出→短生命子进程渲染 + wall-clock kill 超时（release 用
  panic=abort，catch_unwind 不够）。【安全边界放进程外的案例】
- 图像内联：terminal/image.rs 支持 Kitty graphics protocol 与 iTerm2，运行时探测。

## 终端工程学（ch16）

TTY 卫生（xai-tty-utils + process_scope）：子进程 detach 防孙进程往 /dev/tty 喷转义码；
ProcessScope 用 Weak-keyed registry 做 PID-reuse 安全的 kill_all。
