spec: task
name: "ch04-time-dimension"
inherits: project
tags: [book, chapter, loop, monitor, scheduler, async]
---

## 意图

给《第 4 章：agentic 循环》新增一节《agent 的时间维度：后台任务、监控与定时调度》。
现有章节把循环讲成响应"现在"的请求-响应；本节讲 Grok Build 如何用三种工具让 agent
处理"未来"：后台命令（现在开始、未来完成）、`monitor`（外部状态变化时主动唤醒 agent）、
`scheduler`（在未来时刻重新注入意图）。重点不是逐个工具说明，而是三种时间语义的统一
主题——一个本质请求-响应的模型如何安全持有跨 turn / 跨重启的异步状态（交给 actor 与
Resources，第 3 章）。

## 已定决策

- 落点：`book/manuscript/ch04-agentic-loop.md` 新增 `4.8 agent 的时间维度：后台任务、
  监控与定时调度`，现 4.8（codex）顺延 4.9、4.9（模式提炼）顺延 4.10；同步更新"设计要点回顾"
- monitor：每行 stdout 变会话事件、token bucket 限流 + suppression、持续过载自动杀、
  `Weak` 句柄不钉住终端后端、子代理退出 reparent 给父，以 monitor/tool.rs 与
  rate_limiter.rs 为证
- scheduler：`SchedulerActor` + `biased` select!、`durable` 经 Resources 持久化、
  重启补触发 missed 任务、循环 7 天过期、上限 50、最小间隔 60s，以 scheduler/actor.rs、
  create.rs、interval.rs 为证
- 后台命令：等待型工具（wait_tasks/get_task_output）有插话时被 select 抢占（承接 4.3）
- 不声称未验证的具体常量（如过载秒数）——软化为"持续过载"
- 所有架构性陈述带 `file:line`；中文；含 1 张 mermaid（三语义汇于 actor 唤醒）
- 净新增约 2000–2800 字符；保留全章 voice

## 边界

### 允许修改
- book/manuscript/ch04-agentic-loop.md
- book/specs/ch04-time-dimension.spec.md
- book/knowledge/context/loop.md

### 禁止做
- 不修改 crates/ 下任何源码
- 不使用无 file:line 溯源的架构性断言
- 不逐个罗列 scheduler_create/delete/list，作工具族整体写
- 不声称未经验证的具体数字常量
- 单段源码粘贴不超过 30 行

## 完成条件

场景: monitor 是唤醒而非轮询
  测试: ai_review_ch04_monitor
  假设 读者对照 monitor/tool.rs 阅读
  当 读者读完 monitor 一段
  那么 能说出 monitor 把每行 stdout 变会话事件、agent 无须轮询、事件到达时被唤醒

场景: monitor 的背压与资源纪律
  测试: ai_review_ch04_monitor_backpressure
  假设 读者对照 rate_limiter.rs 与 tool.rs 阅读
  当 读者读完 monitor 背压一段
  那么 能说出 token bucket 限流 + 持续过载自动杀、Weak 句柄不钉住终端后端、子代理退出 reparent 给父

场景: scheduler 是 actor 而非 cron
  测试: ai_review_ch04_scheduler
  假设 读者对照 scheduler/actor.rs 与 create.rs 阅读
  当 读者读完 scheduler 一段
  那么 能说出它是 SchedulerActor + biased select、durable 经 Resources 持久化、重启补触发 missed 任务、7 天过期/上限 50/最小 60s

场景: 三种时间语义的统一主题
  测试: ai_review_ch04_time_theme
  假设 读者读完本节
  当 读者回顾三种工具
  那么 能说出后台命令/monitor/scheduler 对应"现在开始未来完成/外部变化唤醒/未来时刻注入"，且异步状态交给 actor 与 Resources

场景: 篇幅与结构达标
  测试: check_ch04_time_structure
  假设 成稿位于 book/manuscript/ch04-agentic-loop.md
  当 编辑运行 book/tools/check_chapter.py
  那么 本节含至少 1 张 mermaid、至少 3 处 file:line 引用，且全章仍满足章级门禁

场景: 引用溯源失败被拒稿
  测试: check_ch04_time_citation_validity
  假设 本节存在指向 crates/ 的 `file:line` 引用
  当 任一引用指向不存在的文件或行号超出文件长度
  那么 结构检查返回非零退出码并列出失效引用

## 排除范围

- 子代理 spawn 后端的传输细节（task 工具，可另述）
- 通知系统与 TUI 视图重建的渲染（第 13/14 章）
- goal/todo 编排（4.2/4.4）
