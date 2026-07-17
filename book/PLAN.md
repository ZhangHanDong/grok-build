# 《AI Coding Agent 架构解剖》写作总纲

以 Grok Build（xAI 开源终端 AI 编程代理，Rust，75 crate）为主轴、codex/opencode 为参照系的
agent 架构比较研究。约 25–30 万字，5 部 18 章。

## 定位

- **读者**：中高级工程师——想构建 agent 产品、深入 Rust 大型工程、理解 Claude Code 类工具原理。
- **主线**："一个 agent 的一生"：键入 prompt → 采样 → 工具执行 → 渲染 → 持久化。
- **副线**：每章末"同一问题，codex 怎么做"参照小节（openai/codex 亦为开源 Rust 实现）。
- **卖点**：Grok Build 是功能面最全的开源工业级实现，且在
  `crates/codegen/xai-grok-tools/src/implementations/` 内原样移植了 codex 与 opencode 的工具，
  三家实现共存于同一代码库、同一 taxonomy，天然适合横向对比。

## 章节大纲

### 第一部：全景
1. AI 编程代理的时代与 Grok Build 是什么（三形态；各家开源状态谱系）
2. 75 个 crate 的工程哲学：`-types`/trait-seam 依赖倒置、Bazel/Cargo 双构建、dotslash 工具链

### 第二部：代理运行时（knowledge/runtime.md）
3. Actor 化的会话引擎：SessionActor 三路 select 主循环
4. Agentic 循环：采样→工具→再采样，goal 编排与 StructuredOutput"假工具"
5. 上下文管理：token 阈值触发 + compaction-core 三种压缩策略与 trait 解耦
6. 会话持久化：JSONL + ChatStateActor、NFS 感知的 SQLite journal
7. Leader-Follower：Unix socket + ACP、版本驱动抢占

### 第三部：工具系统（knowledge/tools.md）
8. 两层工具抽象：RPITIT 零装箱 Tool trait + ToolDyn 擦除 + 依赖注入 registry
9. 文件编辑的艺术：search_replace / hashline / codex apply_patch / opencode edit 四方案对比
10. 时间旅行：checkpoint 按 prompt_index 三域（fs/hunk/git）回退，fast-worktree 与 BTRFS 快照
11. 沙箱：nono 统一 Landlock/Seatbelt、seccomp 阻断子进程网络、五档 profile
12. 拿来主义与归一层：codex/opencode 移植的工程与法务实践

### 第四部：TUI（knowledge/tui.md）
13. 事件循环与 AppView：inline viewport 双渲染模式、IoC seam
14. 增量渲染管线：diff flush、cursor blink 保护、synchronized update、LayoutCache
15. 流式 Markdown：checkpoint 冻结 O(N²)→O(N)、mermaid 双路径与进程崩溃隔离 ★样章
16. 终端工程学：Kitty/iTerm2 图像协议、OSC 8、TTY 卫生与进程作用域

### 第五部：扩展生态与治理（knowledge/platform.md）
17. MCP / Hooks / 插件市场 / 子代理解析 / Skills 体系
18. 企业级治理：六层 Ed25519 签名配置、MDM、secrets 脱敏；memory「dream」与 codebase-graph

## 基于 agent-spec 1.0 的工作流

每章流水线：

```
specs/chNN-*.spec.md 章节合约（agent-spec lint 校验合约质量）
  → Opus 调研代理（用 agent-spec atlas query/refs/impls 查符号图 + knowledge/ 事实库）
  → tech-writer skill 成文 → manuscript/chNN-*.md
  → 核对完成条件 → agent-spec archive 归档
```

配套命令：

- `agent-spec atlas build`（增量刷新符号图，存 `.agent-spec/`；`atlas check` 查新鲜度）
- `agent-spec lint-knowledge --knowledge book/knowledge`（知识库治理）
- 上游 monorepo 同步后：`atlas check` + 人工核对 knowledge/ 中 source trace 指向的文件

## 事实纪律

- manuscript 中所有架构性陈述必须能溯源到 knowledge/ 条目或 `file:line` 引用。
- knowledge/ 条目必须带 source trace（涉及的源文件路径）。
- 上游同步后 source trace 失效的条目标记 `stale: true`，相关章节进修订队列。
