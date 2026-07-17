spec: task
name: "ch18-governance-memory"
inherits: project
tags: [book, chapter, governance, config, memory]
---

## 意图

撰写《第 18 章：企业级治理与记忆系统》。读者是中高级工程师；本章讲清两个高级
主题：六层签名配置合并（Ed25519 requirements、MDM、fail-closed）与 secrets
脱敏的企业治理，以及 memory「dream」自动整合 + FTS5/vec 混合检索的记忆系统。

## 已定决策

- 主轴之一：六层配置合并（managed/config/requirements 签名/MDM，企业覆盖用户 fail-closed）
- 主轴之二：memory 系统（blake3 分区、FTS5+sqlite-vec 混合检索、dream 整合、MMR 去冗）
- 覆盖 secrets 正则脱敏（清洗发往 Sentry/Mixpanel 的出站数据）
- 覆盖 codebase-graph（tree-sitter、mmap 零拷贝）作为第五部收尾
- 所有架构性陈述带 file:line 引用；codex 事实先查 knowledge/context/codex-reference.md
- 章末附"同一问题，codex 怎么做"参照小节
- 中文写作，成稿落至 book/manuscript/ch18-governance-memory.md

## 边界

### 允许修改
- book/manuscript/ch18-governance-memory.md
- book/knowledge/context/platform.md
- book/knowledge/context/codex-reference.md

### 禁止做
- 不修改 crates/ 下任何源码
- 不使用无 file:line 溯源的架构性断言
- 单段源码粘贴不超过 30 行
- 不重复 ch5 压缩、ch6 持久化（交叉引用）

## 完成条件

场景: 治理动机完整
  测试: ai_review_ch18_motivation
  假设 读者不了解企业级 agent 部署的治理需求
  当 读者读完动机一节
  那么 能说出企业治理的至少 2 个诉求（不可被用户覆盖的策略、出站数据脱敏）

场景: 六层配置合并准确
  测试: ai_review_ch18_config
  假设 读者对照 xai-grok-config 源码阅读
  当 读者核对文中每一处 file:line 引用
  那么 六层优先级、Ed25519 签名验证、fail-closed 启动的描述与源码一致

场景: 记忆系统准确
  测试: ai_review_ch18_memory
  假设 读者对照 xai-grok-memory 源码阅读
  当 读者读完记忆一节
  那么 blake3 分区、FTS5+vec 混合检索、dream 整合、MMR 去冗的描述与源码一致

场景: codex 参照小节到位
  测试: ai_review_ch18_codex_compare
  假设 章末含 codex 参照小节
  当 读者读完参照小节
  那么 文中列出 codex 治理/记忆与 Grok Build 的至少 2 点取舍差异

场景: 篇幅与结构达标
  测试: check_ch18_structure
  假设 成稿位于 book/manuscript/ch18-governance-memory.md
  当 编辑运行 book/tools/check_chapter.py
  那么 正文字数在 8000-15000 之间、含至少 1 张示意图、至少 5 处 file:line 引用、
      章末含"设计要点回顾"清单

场景: 引用溯源失败被拒稿
  测试: check_ch18_citation_validity
  假设 文中存在指向 crates/ 的 file:line 引用
  当 任一引用指向不存在的文件或行号超出文件长度
  那么 结构检查返回非零退出码并列出失效引用

## 排除范围

- 上下文压缩（ch5）、会话持久化（ch6）、认证流程（ch7 leader 提过）
