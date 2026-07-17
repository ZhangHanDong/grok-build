---
kind: context
title: codex 参照系已验证事实（各章"codex 怎么做"小节共用）
tags: [codex, comparison]
sources:
  - https://github.com/openai/codex (codex-rs, 2026 年中 main 分支)
stale: false
---

# codex 已验证事实库

各章参照小节引用前先查此卡；新事实经 fact-checker WebFetch 验证后追加。
⚠️ codex 迭代快，写作时标注"2026 年中 main 分支"。

## 会话与循环（ch3/ch4 已验证）

- SQ/EQ 协议：Submission Queue（用户→核心）/ Event Queue（核心→用户），类型定义在
  **独立 crate `codex-rs/protocol`**（`protocol.rs`，含 Submission/Op/Event/EventMsg），
  core 通过 codex_protocol 引用。不要写成"core 的 protocol 模块"。
- 会话组织：每会话单个 `submission_loop` 主任务（spawn_internal，跑至 Op::Shutdown）；
  会话状态可变部分为 `Mutex<SessionState>` 挂在 `Session` 上（`state.lock().await`）。
- turn 循环：以模型停止请求工具为终点；**无 goal 续跑/抗偷懒编排层**（未见反证）。
- 工具并发：⚠️**并非顺序执行**（ch4 事实核查纠正）。
  `codex-rs/core/src/tools/parallel.rs` 的 `ToolCallRuntime` 用全局 `RwLock<()>` 门：
  `tool_supports_parallel` 的工具（shell_command、web-search、mcp 等）取读锁并发，
  不支持的取写锁串行（parallel.rs:100-138）。锁粒度=工具类型；对比 Grok 的
  per-path Mutex（粒度=资源）。
- 结构化输出：面向原生 schema 后端（Responses API `text.format`/output-schema，
  client_common.rs 有 json_schema）——无需假工具垫片。

## TUI（ch15 已验证）

- 流式渲染提交粒度=行：`codex-rs/tui/src` 有 markdown_stream.rs / insert_history.rs，
  `commit_complete_source()` 按换行提交完成行、保留尾部未完成行。
- 无 mermaid 渲染：tui 目录无 mermaid 文件，图表以代码块显示。

## 写作纪律

- 每条新 codex 论断必须走 fact-checker WebFetch 验证；无法验证的在文中标注。
- 章末统一免责声明："基于 openai/codex 2026 年年中 main 分支"。

## 渲染（ch14 已验证）

- codex **也 fork 了 Terminal**：`codex-rs/tui/src/custom_terminal.rs` 从 ratatui 派生自己的
  Terminal/Frame，含 inline viewport 与 diff_buffers。差异不在"是否 fork"。
- 关键差异：codex `flush()` 返回 `io::Result<()>`（无变更信号）；Grok `flush()` 返回
  `io::Result<bool>`——正是这个 bool 使"零变更零字节"光标保护得以干净实现。
- 勿写成"codex 更多用上游 ratatui、Grok 才 fork"——两家都 fork。

## 扩展生态（ch17 已验证）

- codex **有完整的 hooks 系统**（docs/config.md：user/project/session/managed 四层，
  含 allow_managed_hooks_only 企业管控开关）。勿写成"Hooks 是 Grok 相对 codex 的额外扩展点"。
- 真实差异：Grok 有官方插件市场（xai-org/plugin-marketplace）+ 打包分发机制；
  Grok Hooks 兼容 Claude settings.json 格式，codex hooks 自成配置体系。

## workspace 结构（ch2 已验证，2026-07 WebFetch）

- codex-rs `[workspace] members` **约 128 个**（远多于 Grok 的 75 第一方 crate），
  **纯手写 Cargo workspace、无 Bazel**。含 `ext/*`（ext/mcp、ext/skills、ext/memories、
  ext/guardian…）、`utils/*`（二十来个微 crate）、`memories/read`、`memories/write`。
  ⚠️ 勿写成"codex 拆得更少更粗 / 手写清单必须克制"——**方向是反的**，codex 证明手写
  workspace 也能扩到 100+ crate。真实差异：Grok 的 codegen/ 清单是 Bazel 生成投影
  （Cargo.toml:1 "Auto-generated"），codex 是原生手写。粒度趋同，清单真源不同。
- codex `protocol` 独立 crate、core 经 codex_protocol 引用——与 Grok `-types` 依赖倒置
  哲学同源（ch2/ch3/ch4 通用）。

## 记忆子系统（ch18 已验证）

- codex **不止 AGENTS.md**：当前 main 有 `ext/memories`、`memories/read`、`memories/write`
  等 crate，是程序化记忆子系统。勿写成"codex 只靠用户显式维护的 AGENTS.md"。
  内部检索/整合实现未逐行核对——对比只做取向层，不对其实现下断言。
- codex 有 secrets/guardian/hooks/config/cloud-config 等治理设施，但**无 Grok 那套
  Ed25519 签名策略栈**（signed requirements + 落盘再校验 + 六层合并）。治理差异在
  威胁模型深度，非"codex 无治理"。
