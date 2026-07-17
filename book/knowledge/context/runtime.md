---
kind: context
title: 代理运行时核心（第二部素材）
tags: [runtime, actor, compaction, persistence, leader]
sources:
  - crates/codegen/xai-grok-shell/src/session/acp_session_impl/run_loop.rs
  - crates/codegen/xai-grok-shell/src/session/acp_session_impl/turn.rs
  - crates/codegen/xai-grok-shell/src/session/acp_session_impl/tool_calls.rs
  - crates/codegen/xai-grok-shell/src/session/compaction.rs
  - crates/codegen/xai-grok-shell/src/leader/mod.rs
  - crates/codegen/xai-grok-sampler/src/actor/mod.rs
  - crates/codegen/xai-grok-agent/src/agent.rs
  - crates/codegen/xai-chat-state/src/actor/mod.rs
  - crates/codegen/xai-sqlite-journal/src/lib.rs
  - crates/common/xai-grok-compaction/src/lib.rs
stale: false
---

# 代理运行时核心

## 主循环（ch3/ch4）

分层 Actor 架构，tokio 任务 + mpsc 消息传递。⚠️精确表述（ch3 评审修正）："无锁"仅
下游 actor 成立（SamplerActor/ChatStateActor 单属主零 Mutex）；SessionActor 本身经
`Arc<SessionActor>` 与旁挂任务共享，调度状态在 `TokioMutex<State>`（acp_session.rs:593、
注释 "the only fields that remain behind TokioMutex" :263），靠 LocalSet 单线程消解竞争。
`SessionCommand` 为 86 个变体（勿写"约 70"）。核心 `SessionActor` 主循环
`run_session`（run_loop.rs:33）select 三路：命令通道、ChatStateEvent、SessionEvent；
旁挂 replay 刷新定时器、fs-watch、MCP dispatcher。

单轮对话入口 `handle_prompt`（turn.rs）。agentic 循环在 turn.rs:759：反复
`process_conversation_turn_with_recovery`（采样→解析工具调用→执行）直到非 Completed；
goal 编排开启时由 `run_goal_round_end` 决定 Continue（注入续跑指令）或 EndTurn。
工具执行管线 `execute_tool_calls`（tool_calls.rs:31）。

`SamplerActor`（xai-grok-sampler/src/actor/mod.rs）：主循环单线程处理命令，每请求
`tokio::spawn` 进 JoinSet 实现并发流式；join_next 优先于收命令以清理 active_requests。

`Agent`（agent.rs）构建后不可变，持 `Arc<ToolBridge>`。生命周期扩展经 xai-agent-lifecycle
的 typed contributor 注册表（local/registry.rs）以 turn/session 钩子插入。

StructuredOutput：对无法原生约束输出的后端，用"假工具"+ jsonschema 校验 + 最多 3 次重试
（turn.rs:7 附近）。usage 记账 fail-closed + 子代理 drain 语义（turn.rs:1099）。

## 上下文压缩（ch5）

压缩引擎独立于 crates/common/xai-grok-compaction（"compaction-core"），经 trait 缝
（CompactionItem/ItemTokenCounter/CompactionSampler）与 Grok chat、grok-build 两个 host
解耦，不依赖会话/采样类型 crate（lib.rs:1-83）。三种风格：code_compaction（整会话全量替换
摘要）、intra_compaction（保尾逐步压缩）、inter_compaction（分块跨轮压缩）。

触发：`Agent::should_auto_compact`（agent.rs:201）用 xai_token_estimation::exceeds_threshold
对比 context window 与 auto_compact_threshold_percent。host 侧编排在 session/compaction.rs
（3321 行）与 full_replace_compaction.rs。

## 会话持久化（ch6）

`ChatStateActor` 专用任务独占 `Box<dyn ChatPersistence>`，&mut self 调用，无锁无原子
（persistence.rs:1-6）。JSONL 落盘：`{root}/sessions/{urlencoded(cwd)}/{session_id}/`；
子代理会话以 Explicit 目录寄居父目录。写用户消息带 persist_ack flush 屏障（turn.rs:708）。

xai-sqlite-journal：按文件系统自动选 journal 模式——本地 WAL；检测到 NFS 改 TRUNCATE
且每主机独立 DB 文件，规避 WAL -shm mmap 在 NFS 被 peer 截断致 SIGBUS（lib.rs:1-90）；
留 GROK_SQLITE_JOURNAL_MODE kill-switch。【事故驱动设计的典型案例】

## Leader-Follower（ch7）

单机单 leader（leader/mod.rs）：leader 进程持 Agent 全局状态，持久化 ~/.grok/；TUI/IDE/
headless 客户端经 Unix socket（~/.grok/leader.sock）以 ACP 协议接入，
`connect_or_spawn(client, ClientMode, ...)` 统一入口。leader/server.rs（6208 行）做请求 ID
命名空间隔离与会话归属路由。版本驱动抢占：`should_evict`（mod.rs:104）仅当客户端版本
严格更新才驱逐旧 leader——防抖动、收敛到最新版。
