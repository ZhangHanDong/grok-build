spec: project
name: "ai-coding-agent-book"
tags: [book]
---

## 意图

《AI Coding Agent 架构解剖》全书写作项目的公共契约。以 Grok Build 为主轴、
codex/opencode 为参照系（见 knowledge/decisions/adr-001-book-positioning.md），
覆盖需求见 knowledge/requirements/req-001-book-coverage.md。

## 已定决策

- 中文写作；章节成稿落 `book/manuscript/`，命名 `chNN-<slug>.md`
- 事实纪律：架构性陈述必须带 `file:line` 引用或溯源到 knowledge/ 条目
- 每章调研优先用 `agent-spec atlas` 符号图查询，减少全文检索
- 结构检查统一用 `book/tools/check_chapter.py`

## 边界

### 允许修改
- book/**

### 禁止做
- 不修改 crates/、prod/、third_party/ 下任何文件
- 不在 manuscript 中粘贴超过 30 行的连续源码

## 排除范围

- 书稿排版/出版工具链（mdbook/epub 等后期另立任务）
