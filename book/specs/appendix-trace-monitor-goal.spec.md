spec: task
name: "appendix-trace-monitor-goal"
inherits: project
tags: [book, appendix, e2e-trace, monitor, actor, goal]
---

## 意图

给《附录：端到端追踪》新增第三条追踪《一个后台 monitor 唤醒 agent 去处理外部事件》。
现有两条追踪覆盖"prompt→流式回复"与"编辑文件"；本条串起被工具补齐章节新暴露的
异步链路：用户起一个 monitor 后台脚本 → 每行 stdout 变会话事件 → token bucket 限流
→ 事件经通知送到 SessionActor 消息循环、把空闲的 agent 唤醒 → 模型处理并 update_goal
（阻塞到 verdict）→ 渲染回 TUI。跨第 8、4、3、6、13/16 章，揭示"外部事件被降维成又一条
经过 SessionActor 的消息"这一 actor 模型红利。

## 已定决策

- 落点：`book/manuscript/appendix-e2e-traces.md` 新增"追踪三"（在追踪二之后、"如何用"
  一节之前）；同步把结尾"两条追踪"更新为"三条追踪"
- 沿用现有追踪格式：用户动作 / 穿过的子系统 / mermaid 时序 / 逐站(带 file:line 与
  "接缝的设计意图") / "这条追踪揭示了什么"
- monitor 每行 stdout 变事件以 monitor/tool.rs:30 为证；限流以 rate_limiter.rs:44 为证；
  update_goal 阻塞到 verdict 以 update_goal/mod.rs:1 为证（详见 4.4）
- 跨章引用第 3（SessionActor）/4（时间维度+goal）/6（durable 持久化）/8（工具）/
  13、16（渲染）章，不重复各章细节
- 中文；含 1 张 mermaid 时序图；净新增约 1600–2200 字符

## 边界

### 允许修改
- book/manuscript/appendix-e2e-traces.md
- book/specs/appendix-trace-monitor-goal.spec.md

### 禁止做
- 不修改 crates/ 下任何源码
- 不使用无 file:line 溯源的架构性断言（综合性跨章引用除外，需标章号）
- 不重复各章内部实现细节，只讲接缝
- 单段源码粘贴不超过 30 行

## 完成条件

场景: 追踪串起 monitor 到 goal 的异步链
  测试: ai_review_appendix_trace_chain
  假设 读者读完追踪三
  当 读者回顾各站
  那么 能复述 monitor 起后台脚本 → 每行 stdout 变事件 → 限流 → SessionActor 唤醒 → 模型处理 → update_goal

场景: 揭示 actor 模型红利
  测试: ai_review_appendix_trace_insight
  假设 读者读完"揭示了什么"
  当 读者总结本条追踪的设计洞察
  那么 能说出外部事件被降维成又一条经过 SessionActor 的消息，异步复用已有机制而非新造特例

场景: 跨章接缝标注到位
  测试: ai_review_appendix_trace_seams
  假设 追踪跨多章
  当 读者读每一站
  那么 每站标注所属章节，且至少覆盖第 3、4、8 章

场景: 结构达标
  测试: check_appendix_trace_structure
  假设 成稿位于 book/manuscript/appendix-e2e-traces.md
  当 编辑运行 book/tools/check_chapter.py
  那么 追踪三含 1 张 mermaid、至少 2 处 file:line 引用，且"两条追踪"已更新为"三条"

场景: 引用溯源失败被拒稿
  测试: check_appendix_trace_citation_validity
  假设 追踪三存在指向 crates/ 的 `file:line` 引用
  当 任一引用指向不存在的文件或行号超出文件长度
  那么 结构检查返回非零退出码并列出失效引用

## 排除范围

- monitor/scheduler 的完整实现细节（第 4 章）
- SessionActor 消息拓扑细节（第 3 章）
- 渲染管线细节（第 13/14/16 章）
