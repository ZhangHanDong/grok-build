spec: task
name: "ch10-time-travel"
inherits: project
tags: [book, chapter, tools, checkpoint, worktree]
---

## 意图

撰写《第 10 章：时间旅行——checkpoint 与 worktree》。读者是中高级工程师；本章
讲清 agent 的可撤销性基建：checkpoint 按 prompt_index 三域（文件系统/hunk/git）
打包回退、hunk-tracker 的来源归因、fast-worktree 的并行隔离（CoW/BTRFS/overlayfs）。

## 已定决策

- 主轴案例：workspace checkpoint 的三域对齐回退（session/checkpoint.rs）
- 覆盖 xai-hunk-tracker 的 Agent vs External 归因（actor 模式）
- 覆盖 xai-fast-worktree：git worktree + 哈希分片 CoW、BTRFS O(1) 快照、
  overlayfs 路径、SQLite 元数据（与 ch6 journal 衔接）
- 覆盖 rewind 用户语义（与 ch5 压缩抑制重置、ch6 rewind_points 懒加载的交叉引用）
- 所有架构性陈述带 `file:line` 引用；codex 事实先查 knowledge/context/codex-reference.md
- 章末附"同一问题，`codex` 怎么做"参照小节
- 中文写作，成稿落至 `book/manuscript/ch10-time-travel.md`

## 边界

### 允许修改
- book/manuscript/ch10-time-travel.md
- book/knowledge/context/tools.md
- book/knowledge/context/codex-reference.md

### 禁止做
- 不修改 crates/ 下任何源码
- 不使用无 file:line 溯源的架构性断言
- 单段源码粘贴不超过 30 行
- 不重复 ch6 持久化格式细节、ch9 编辑内原子回滚（交叉引用）

## 完成条件

场景: 可撤销性动机完整
  测试: ai_review_ch10_motivation
  假设 读者认为 git 本身已提供撤销能力
  当 读者读完动机一节
  那么 能说出 agent 场景为何 git 不够（至少 2 条：未跟踪文件/用户混编/粒度）
      与三域对齐的必要性

场景: checkpoint 机制讲解准确
  测试: ai_review_ch10_checkpoint
  假设 读者对照 workspace 源码阅读
  当 读者核对文中每一处 `file:line` 引用
  那么 三域打包、prompt_index 键、restore 流程的描述与源码一致

场景: worktree 隔离讲解准确
  测试: ai_review_ch10_worktree
  假设 读者对照 fast-worktree 源码阅读
  当 读者读完该节
  那么 CoW 克隆、BTRFS/overlayfs 分路径、池化与 GC 的描述与源码一致

场景: codex 参照小节到位
  测试: ai_review_ch10_codex_compare
  假设 章末含 `codex` 参照小节
  当 读者读完参照小节
  那么 文中列出 codex 可撤销性方案与 Grok Build 的至少 2 点取舍差异

场景: 篇幅与结构达标
  测试: check_ch10_structure
  假设 成稿位于 `book/manuscript/ch10-time-travel.md`
  当 编辑运行 book/tools/check_chapter.py
  那么 正文字数在 8000-15000 之间、含至少 1 张示意图、至少 5 处 file:line 引用、
      章末含"设计要点回顾"清单

场景: 引用溯源失败被拒稿
  测试: check_ch10_citation_validity
  假设 文中存在指向 crates/ 的 `file:line` 引用
  当 任一引用指向不存在的文件或行号超出文件长度
  那么 结构检查返回非零退出码并列出失效引用

## 排除范围

- 持久化格式（ch6）、编辑工具内部（ch9）、沙箱（ch11）、gix-status 细节（点到即止）
