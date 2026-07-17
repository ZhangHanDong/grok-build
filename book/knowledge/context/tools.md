---
kind: context
title: 工具系统与扩展生态（第三部素材）
tags: [tools, sandbox, checkpoint, worktree, mcp, hooks, plugins]
sources:
  - crates/common/xai-tool-runtime/src/tool.rs
  - crates/common/xai-tool-runtime/src/dispatch.rs
  - crates/codegen/xai-grok-tools/src/registry/types.rs
  - crates/codegen/xai-grok-tools/src/tool_taxonomy.rs
  - crates/codegen/xai-grok-tools/src/bridge.rs
  - crates/codegen/xai-grok-tools/src/types/requirements.rs
  - crates/codegen/xai-grok-tools/src/implementations/codex/
  - crates/codegen/xai-grok-tools/src/implementations/opencode/
  - crates/codegen/xai-grok-workspace/src/session/checkpoint.rs
  - crates/codegen/xai-fast-worktree/src/lib.rs
  - crates/codegen/xai-hunk-tracker/src/lib.rs
  - crates/codegen/xai-grok-sandbox/src/child_net.rs
  - crates/codegen/xai-grok-mcp/src/lib.rs
  - crates/codegen/xai-grok-hooks/src/lib.rs
  - crates/codegen/xai-grok-plugin-marketplace/src/lib.rs
  - crates/codegen/xai-grok-subagent-resolution/src/lib.rs
stale: false
---

# 工具系统与扩展生态

## 两层工具抽象（ch8）

- 底层统一契约 xai-tool-runtime/src/tool.rs：`Tool` trait 带关联类型 Args/Output，原生
  async fn（RPITIT）+ 显式 Send，避免 future 装箱；类型擦除交给 ToolDyn（blanket impl，
  dispatch.rs）。流式契约 `ToolStream = [Progress*, Terminal]`（tool.rs:114），阻塞工具只
  实现 run，默认 execute 用 terminal_only 包单元素流。ToolFamily/ToolVariant 共享 ToolId。
- 上层注册系统 xai-grok-tools：ToolRegistryBuilder/ToolConfig/FinalizedToolset
  （registry/types.rs），Resources 依赖注入（Cwd/FileSystem/NotificationHandle）。
  身份/词汇统一 tool_taxonomy.rs（ToolKind/ToolNamespace + `x.ai/tool` _meta 键）；
  bridge.rs ToolBridge 适配进 session 层。xai-grok-tools-api 提供 protobuf/gRPC 契约。
- `Expr<T>` 三层布尔表达式（types/requirements.rs）：同一泛型表达式树复用于
  工具依赖→参数条件→值相等，声明式描述工具可用性。

## 文件编辑与时间旅行（ch9/ch10）

- 编辑工具多套并存：grok_build/search_replace、grok_build_hashline（ContentOnly/
  ChunkFingerprint/CheckpointChain 三种抗漂移锚点）、codex apply_patch、opencode edit。
- Checkpoint（workspace/src/session/checkpoint.rs）按 prompt_index 三域打包——文件系统
  RewindPoint、hunk delta、git HEAD/index，restore 统一回退；turn 边界经 on_turn_boundary 扇出。
- xai-hunk-tracker：actor 模式，区分 Agent vs External 来源归因。
- xai-fast-worktree：git worktree add --no-checkout + 哈希分片并行 CoW 克隆；Linux 有
  BTRFS 快照（O(1)）与 overlayfs 两路径，SQLite 记元数据。xai-gix-status 用 gitoxide。

## 沙箱（ch11）

基于 nono crate，进程启动时应用一次，统一封装 Linux Landlock 与 macOS Seatbelt 内核级
文件访问控制（enforce feature；musl 退化轻量 helper）。进程级网络开放（须访问 LLM API），
子进程网络逐个用 seccomp BPF 阻断（child_net.rs，非 Linux no-op）；Linux 支持 bwrap
（__GROK_INSIDE_BWRAP）。内置 profile：workspace/devbox/read-only/strict/off，
~/.grok/sandbox.toml 自定义，deny 列表两平台内核强制。

## 扩展体系（ch17）

- MCP（xai-grok-mcp）：rmcp 2.1；隔离 reqwest 0.13 与工作区 0.12 版本冲突；OAuth 浏览器流、
  $GROK_HOME/mcp_credentials.json、streamable-HTTP/子进程传输、退避包装绕过 rmcp 零退避重连 bug。
- Hooks（xai-grok-hooks）：~/.grok/hooks/ 与 <worktree>/.grok/hooks/ 的 JSON 定义，子进程执行；
  事件覆盖 session/tool/prompt/notification；pre_tool_use 可 deny/allow，默认 fail-open。
- 插件市场：git 源（官方 xai-org/plugin-marketplace），插件捆绑 skills/hooks/MCP/commands，
  MarketplaceRelativePath 防路径穿越。
- 子代理解析（xai-grok-subagent-resolution）：纯逻辑层，优先级 显式 override > role >
  persona > parent，无 session/transport 依赖，可复用于远程 spawn。

## codex/opencode 移植清单（ch12 对比素材）

均在 implementations/ 独立目录 + THIRD_PARTY_NOTICES：
- codex（openai/codex，Apache-2.0，ToolNamespace::Codex）：apply_patch（parser/
  seek_sequence/apply）、grep_files、list_dir、read_file。
- opencode（sst/opencode，MIT）：bash、edit、glob、grep、read、skill、todowrite、write。
  保留 opencode 参数命名（filePath/oldString/newString），仅 write 归一化 snake_case。
