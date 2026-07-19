spec: task
name: "ch09-lsp-feedback"
inherits: project
tags: [book, chapter, editing, lsp, feedback]
---

## 意图

给《第 9 章：文件编辑》新增一节《编辑不是终点：LSP 诊断如何闭合反馈循环》。前面
五节讲三种编辑算法怎么把字节改对，却没讲改完如何拿到编译器级反馈。`lsp` 工具把
文本编辑闭合成语义反馈循环：经语言服务器提供六种代码智能操作，按文件扩展名路由，
把诊断包进 `<system-reminder>` 回喂模型，崩溃自动重启并重放已跟踪文档、用 lifecycle
id 排除陈旧诊断。重点还包括一条必须写出的闭环缺口——反馈只在编辑经 `search_replace`
时触发，bash/git 的改动不进 LSP 视野。并与第 18 章 tree-sitter 静态图对照（活语义 vs
静态索引）。

## 已定决策

- 落点：`book/manuscript/ch09-file-editing.md` 新增 `9.8 编辑不是终点：LSP 诊断
  如何闭合反馈循环`（末尾），现 9.8（模式提炼）顺延 9.9；同步更新"设计要点回顾"
- 六种操作以 types.rs 的 `LspOperation`（GoToDefinition/FindReferences/Hover/
  GoToImplementation/DocumentSymbol/WorkspaceSymbol）为证
- 按扩展名路由、诊断回喂 system-reminder，以 manager.rs:1 与 manager.rs:295 为证
- 崩溃自动重启、重放已跟踪文档、lifecycle id 排陈旧诊断，以 restart.rs 与 manager.rs
  的 lifecycle_id 为证
- **闭环缺口（必须写）**：`notify_file_changed` 注释"Only called after search_replace;
  other mutations (bash, git) are not tracked"（manager.rs:185）
- 与第 18 章 tree-sitter codebase-graph 对照：活语义 vs 轻量静态索引；呼应 atlas 分层
- 不声称未验证的"指数退避"具体机制——软化为"自动重启"
- 所有架构性陈述带 `file:line`；中文；含 1 张 mermaid（反馈闭环 + bash/git 绕过）
- 净新增约 1800–2400 字符；保留全章 voice

## 边界

### 允许修改
- book/manuscript/ch09-file-editing.md
- book/specs/ch09-lsp-feedback.spec.md
- book/knowledge/context/editing.md

### 禁止做
- 不修改 crates/ 下任何源码
- 不使用无 file:line 溯源的架构性断言
- 不声称 bash/git 改动会进入 LSP 反馈（源码明确不跟踪）
- 不声称未经验证的具体重启退避策略
- 单段源码粘贴不超过 30 行

## 完成条件

场景: LSP 把编辑闭合成语义反馈
  测试: ai_review_ch09_lsp_loop
  假设 读者读完本节开头
  当 读者理解 lsp 工具的定位
  那么 能说出它把诊断回喂模型，让 agent 改完就看见自己改出的编译错误

场景: 六种操作与扩展名路由
  测试: ai_review_ch09_lsp_ops
  假设 读者对照 types.rs 与 manager.rs 阅读
  当 读者读完操作一段
  那么 能列出六种操作，并说出按文件扩展名路由到不同语言服务器

场景: 崩溃恢复与陈旧诊断排除
  测试: ai_review_ch09_lsp_lifecycle
  假设 读者对照 restart.rs 阅读
  当 读者读完生命周期一段
  那么 能说出崩溃自动重启、重放已跟踪文档、用 lifecycle id 排除旧实例陈旧诊断

场景: 闭环缺口 bash/git 不跟踪
  测试: ai_review_ch09_lsp_gap
  假设 存在"LSP 反馈覆盖所有编辑"的误解
  当 读者读完缺口一段
  那么 文中明确反馈只在经 search_replace 时触发，bash/git 的改动不进 LSP 视野

场景: 篇幅与结构达标
  测试: check_ch09_lsp_structure
  假设 成稿位于 book/manuscript/ch09-file-editing.md
  当 编辑运行 book/tools/check_chapter.py
  那么 本节含至少 1 张 mermaid、至少 3 处 file:line 引用，且全章仍满足章级门禁

场景: 引用溯源失败被拒稿
  测试: check_ch09_lsp_citation_validity
  假设 本节存在指向 crates/ 的 `file:line` 引用
  当 任一引用指向不存在的文件或行号超出文件长度
  那么 结构检查返回非零退出码并列出失效引用

## 排除范围

- LSP 协议本身、async-lsp 库内部
- 各语言服务器的安装与配置
- tree-sitter codebase-graph 的实现（第 18 章）
