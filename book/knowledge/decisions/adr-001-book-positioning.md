---
kind: decision
id: ADR-001
status: Accepted
---

## Context

要为 Grok Build（xAI 开源终端 AI 编程代理，Rust，75 crate）写一本剖析书。
openai/codex CLI 同为开源 Rust 实现，sst/opencode 为开源 TS 实现；
Grok Build 在 xai-grok-tools/src/implementations/ 内原样移植了 codex 与 opencode 的工具。

## Decision

本书定位为"以 Grok Build 为主轴、codex/opencode 为参照系的 agent 架构比较研究"，
而非单一项目源码导读。主线是"一个 agent 的一生"（prompt → 采样 → 工具 → 渲染 → 持久化），
每章末设"同一问题，codex 怎么做"参照小节。5 部 18 章，约 25–30 万字，中文写作。

## Consequences

Good, because 设计空间分析比单项目导读更耐时间，单项目会过时而取舍分析不会。
Good, because 三家实现共存于同一代码库同一 taxonomy，对比写作无需跨仓库跳转。
Bad, because 每章需额外的 codex 对照调研，工作量上浮约 20%。

## Alternatives Considered

- 纯 Grok Build 源码导读：更快成稿，但生命周期短、卖点弱。
- 三家并列平行剖析：工作量翻倍，且 opencode 为 TS，技术栈分散。
