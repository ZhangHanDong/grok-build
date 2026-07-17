spec: task
name: "ch01-era-and-what"
inherits: project
tags: [book, chapter, intro, overview]
---

## 意图

撰写《第 1 章：AI 编程代理的时代与 Grok Build 是什么》。这是全书开篇章，任务是把
读者领进门：交代 2026 年终端 AI 编程代理的格局、Grok Build 是什么与它的来龙去脉
（从 SpaceXAI monorepo 投影出的开源快照）、一口气勾勒其架构全貌，并讲清本书"以
Grok Build 为主轴、codex/opencode 为参照系"的比较方法与阅读地图。它与第 2 章
（工程结构）共同构成 Part 1 全景。

## 已定决策

- 定位为"导论 + 地图"章，深度低于子系统章，但关键事实仍需 file:line 溯源
- 覆盖：AI 编程代理时代背景、Grok Build 是什么、开源来龙去脉（monorepo 同步、
  SOURCE_REV、commit c68e39f、2026-07）、架构一览（leader-follower/ACP/TUI/工具/沙箱）
- 讲清全书比较方法论（主轴 vs 参照系）与阅读路径
- codex 事实先查 knowledge/context/codex-reference.md
- 章末附"同一问题，codex 怎么做"或等价的参照定位小节
- 中文写作，成稿落至 book/manuscript/ch01-era-and-what.md

## 边界

### 允许修改
- book/manuscript/ch01-era-and-what.md
- book/knowledge/context/*.md

### 禁止做
- 不修改 crates/ 下任何源码
- 不深入任何单个子系统的实现细节（那是后续各章，本章只做"一句话 + 指路第 N 章"）
- 不使用无 file:line 溯源的架构性断言（时代背景类叙述可不带引用，但凡涉及 Grok
  Build 自身架构的断言须溯源）

## 完成条件

场景: 时代背景到位
  测试: ai_review_ch1_era
  假设 读者不了解 2026 年终端 AI 编程代理格局
  当 读者读完时代背景一节
  那么 能说出至少 3 个同类项目与它们的共同形态（终端内、agentic loop、工具调用）

场景: Grok Build 定位与来龙去脉准确
  测试: ai_review_ch1_what
  假设 读者对照 README 与仓库根阅读
  当 读者核对文中每一处 file:line 与来龙去脉陈述
  那么 开源来源（monorepo 投影）、SOURCE_REV/commit、crate 规模等与仓库一致

场景: 架构一览指路正确
  测试: ai_review_ch1_map
  假设 读者读完架构一览
  当 读者顺着"指路第 N 章"导航
  那么 每个子系统的一句话概括与其对应章节主题一致、无张冠李戴

场景: 比较方法论清晰
  测试: ai_review_ch1_method
  假设 章内含"主轴 vs 参照系"方法论说明
  当 读者读完
  那么 能说出为何以 Grok Build 为主轴、codex/opencode 扮演什么角色

场景: 篇幅与结构达标
  测试: check_ch1_structure
  假设 成稿位于 book/manuscript/ch01-era-and-what.md
  当 编辑运行 book/tools/check_chapter.py
  那么 正文字数在 8000-15000 之间、含至少 1 张示意图、至少 5 处 file:line 引用、
      章末含"设计要点回顾"清单

场景: 引用溯源失败被拒稿
  测试: check_ch1_citation_validity
  假设 文中存在指向 crates/ 或仓库根文件的 file:line 引用
  当 任一引用指向不存在的文件或行号超出文件长度
  那么 结构检查返回非零退出码并列出失效引用

## 排除范围

- 各子系统实现细节（ch3-18）
- 工程结构与 crate 哲学（ch2）
