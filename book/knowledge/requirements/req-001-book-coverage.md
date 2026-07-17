---
kind: requirement
id: REQ-001
title: "全书必须回答的核心问题"
liveness: auto
tags: [book, coverage]
---

## Problem

读者读完本书应能自己动手构建一个生产级 AI 编程代理。全书章节必须覆盖构建
此类系统的全部核心设计问题，避免"只讲了有什么、没讲为什么"。

## Requirements

[REQ-001] 本书 MUST 解释 agentic 循环的完整生命周期（采样→工具→再采样→终止判定）。
[REQ-002] 本书 MUST 解释上下文窗口约束下的压缩/记忆策略及其触发机制。
[REQ-003] 本书 MUST 解释工具系统的抽象设计（定义、注册、调度、流式输出）。
[REQ-004] 本书 MUST 解释不可信模型输出的安全边界（沙箱、进程隔离、权限）。
[REQ-005] 本书 MUST 解释终端 UI 在流式输出下的增量渲染方案。
[REQ-006] 本书 MUST 解释会话持久化与可恢复性（checkpoint/rewind/resume）。
[REQ-007] 本书 MUST 解释多入口架构（TUI/headless/IDE）如何复用同一运行时。
[REQ-008] 本书 MUST 解释扩展生态设计（MCP/hooks/插件/子代理）。
[REQ-009] 本书 SHOULD 每章提供与 codex 的横向对比。
[REQ-010] 本书 MUST 保证所有架构性陈述可溯源至 file:line 或 knowledge 条目。

## Scenarios

Scenario: 章节覆盖核对
  Given 全书 18 章大纲（book/PLAN.md）
  When 编辑将各 REQ 映射到章节
  Then 每条 MUST 需求至少被一章覆盖

## Dependencies

None.

## Source Trace

- book/PLAN.md
- book/knowledge/context/

## Open Questions

None.
