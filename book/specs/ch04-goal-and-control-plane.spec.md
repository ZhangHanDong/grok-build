spec: task
name: "ch04-goal-and-control-plane"
inherits: project
tags: [book, chapter, loop, goal, plan-mode, control-plane]
---

## 意图

给《第 4 章：agentic 循环》补两处深度。其一，扩写 4.4「完成契约与 recovery」：
现有文本把 goal 编排概括成"策略层返回 Continue/EndTurn"，但"模型声称完成之后
系统做什么"没有展开——`update_goal(completed:true)` 会阻塞到 `SessionActor` 给出
verdict-aware ack，期间并行启动默认 3 个对抗性 skeptic 子代理，以多数"不反驳"判定，
避免"消息刚发出就谎称成功"。其二，新增一节讲**工具作为控制面**：`enter_plan_mode`/
`exit_plan_mode`（四态机 + 只读约束 + 仅 plan 文件可写）与 `ask_user_question`
（mpsc 反向请求 → ACP 往返 → oneshot 回填 + RAII first-answer-wins）——它们不主要
操作文件，而是改变 agent 的运行方式；并澄清 `is_read_only` 不等于"无副作用"。

## 已定决策

- 扩写落点：`book/manuscript/ch04-agentic-loop.md` 的 4.4 节尾追加"goal 完成的另一面"
- 新节落点：新增 `4.7 工具作为控制面：模式切换、反向请求与用户在环`，现 4.7（codex）
  顺延 4.8、4.8（模式提炼）顺延 4.9；同步更新"设计要点回顾"引用
- update_goal 阻塞到 verdict，以 update_goal/mod.rs 头注 + `UpdateGoalAck` 枚举
  （Accepted / ClassifierNotAchieved / CapReached / Stalled / Blocked）为证
- 3 个 skeptic、多数不反驳，以 goal_classifier.rs 为证；业务失败 fail-closed、
  验证基础设施无结论 fail-open
- plan mode 四态（Inactive→Pending→Active→ExitPending）+ 只读强制，以 plan_mode.rs 为证
- ask_user_question 反向请求链，以 ask_user_question/mod.rs + pending_interaction.rs
  的 RAII first-answer-wins 为证
- 澄清 is_read_only：ask/update_goal 标 `is_read_only:true` 却改会话态/引发外部交互，
  故"只读"≈"不写工作区"，非"无副作用"
- 所有架构性陈述带 `file:line`；中文；控制面节含 1 张 mermaid（反向请求时序）
- 保留 4.2 二值循环骨架与全章 voice，只扩写加深，不推倒重写

## 边界

### 允许修改
- book/manuscript/ch04-agentic-loop.md
- book/specs/ch04-goal-and-control-plane.spec.md
- book/knowledge/context/loop.md

### 禁止做
- 不修改 crates/ 下任何源码
- 不使用无 file:line 溯源的架构性断言
- 不重写 4.4 现有 completion_requirement/recovery 内容，只在其后追加 goal 侧
- 不把 is_read_only 说成"无副作用"
- 单段源码粘贴不超过 30 行

## 完成条件

场景: 模型声称完成不等于系统接受
  测试: ai_review_ch04_goal_verdict
  假设 读者对照 update_goal/mod.rs 阅读
  当 读者读完 goal 完成扩写
  那么 能说出 update_goal 阻塞到 SessionActor 的 verdict-aware ack，而非消息送达即成功

场景: 对抗性验证与失败语义
  测试: ai_review_ch04_goal_skeptics
  假设 读者对照 goal_classifier.rs 阅读
  当 读者读完验证一段
  那么 能说出默认 3 个 skeptic 多数不反驳才通过，且业务失败 fail-closed / 验证无结论 fail-open

场景: plan mode 是控制面而非业务工具
  测试: ai_review_ch04_plan_mode
  假设 读者对照 plan_mode.rs 阅读
  当 读者读完控制面一节
  那么 能说出 plan mode 有四态、进入后工作区只读且仅 plan 文件可写

场景: ask_user_question 反向请求链
  测试: ai_review_ch04_reverse_request
  假设 读者对照 ask_user_question/mod.rs 与 pending_interaction.rs 阅读
  当 读者读完反向请求一段
  那么 能复述 mpsc 请求 → ACP 往返 → oneshot 回填，且 RAII guard 保证 first-answer-wins

场景: is_read_only 不等于无副作用
  测试: ai_review_ch04_readonly_paradox
  假设 ask/update_goal 标 is_read_only:true
  当 读者读完澄清
  那么 文中明确"只读"指不写工作区，不等于无副作用（它们改会话态或引发外部交互）

场景: 篇幅与结构达标
  测试: check_ch04_control_structure
  假设 成稿位于 book/manuscript/ch04-agentic-loop.md
  当 编辑运行 book/tools/check_chapter.py
  那么 控制面新节含至少 1 张 mermaid、至少 3 处 file:line 引用，且全章仍满足章级门禁

场景: 引用溯源失败被拒稿
  测试: check_ch04_control_citation_validity
  假设 新增内容存在指向 crates/ 的 `file:line` 引用
  当 任一引用指向不存在的文件或行号超出文件长度
  那么 结构检查返回非零退出码并列出失效引用

## 排除范围

- goal 分类器的 prompt 模板与打分内部
- plan 文件的具体渲染（TUI，第 13/14 章）
- StructuredOutput 完成契约（4.5 已覆盖）
