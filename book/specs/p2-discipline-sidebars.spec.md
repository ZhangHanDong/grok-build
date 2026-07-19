spec: task
name: "p2-discipline-sidebars"
inherits: project
tags: [book, sidebar, must-use, lint, poison, zeroize]
---

## 意图

把三条"短侧栏"级的 Rust 工程纪律插进既有章节，每条一小段、不新开节：ch2 §2.7 末
「把纪律交给编译器与 CI」（`#[must_use]` 用于业务状态转换 + clippy disallowed-methods
禁 canonicalize + forbid unsafe）；ch11 §11.7 末「锁中毒按后果选语义」（parking_lot
不中毒避免 fail-open）；ch18 §18.5 末「敏感明文的内存生命周期」（Zeroizing 擦除 + XOR
只是混淆非安全边界）。控制篇幅，不扩成泛泛 Rust 教程。

## 已定决策

- ch2 §2.7 末：`#[must_use]` 编码业务语义（swap_policy.rs:183 / refresh/mod.rs:89 /
  notification/handle.rs:40）+ clippy 禁 raw canonicalize 引导 dunce（clippy.toml:9）+
  `#![forbid(unsafe_code)]`（crates/common/xai-tool-runtime/src/lib.rs:9）
- ch11 §11.7 末：`DECISIONS` 用 parking_lot::Mutex（不中毒）避免授权门 fail-open
  （crates/codegen/xai-grok-shell/src/agent/folder_trust.rs:122）；会话回收遇 poisoned 按
  "仍繁忙"处理——按"中毒时误判的代价"选语义
- ch18 §18.5 末：解密 prompt 模板用 `Zeroizing<String>` drop 擦明文、XOR 只是混淆非安全
  边界（crates/codegen/xai-grok-agent/src/prompt/template.rs:1）
- 每条侧栏 ≤700 字符；crates 引用用完整路径；不新增顶级节号、不重编号

## 边界

### 允许修改
- book/manuscript/ch02-crate-philosophy.md
- book/manuscript/ch11-sandbox.md
- book/manuscript/ch18-governance-memory.md
- book/specs/p2-discipline-sidebars.spec.md

### 禁止做
- 不修改 crates/ 下任何源码
- 不使用无 file:line 溯源的架构性断言
- 不把 XOR 混淆说成安全边界（源码自标只是混淆）
- 不新开顶级节、不重编号；不扩成泛泛 Rust 教程
- 单段源码粘贴不超过 30 行

## 完成条件

场景: must_use 与 lint 侧栏准确
  测试: ai_review_p2_lint
  假设 读者对照 swap_policy.rs 与 clippy.toml 阅读
  当 读者读完 ch2 侧栏
  那么 能说出 #[must_use] 阻止静默丢弃业务状态、事故复盘被写成 lint（禁 canonicalize、forbid unsafe）

场景: 锁中毒侧栏准确
  测试: ai_review_p2_poison
  假设 读者对照 folder_trust.rs 阅读
  当 读者读完 ch11 侧栏
  那么 能说出授权门用不中毒的 parking_lot 避免 fail-open，处理方式按误判代价选

场景: zeroization 侧栏准确
  测试: ai_review_p2_zeroize
  假设 读者对照 template.rs 阅读
  当 读者读完 ch18 侧栏
  那么 能说出解密模板用 Zeroizing drop 擦明文，且 XOR 只是混淆非安全边界

场景: 篇幅受控且引用有效
  测试: check_p2_structure
  假设 三条侧栏已落章
  当 编辑运行 book/tools/check_chapter.py 与 cite_heal
  那么 各章仍满足门禁、新引用全部溯源有效、每条侧栏简短

场景: 引用溯源失败被拒稿
  测试: check_p2_citation_validity
  假设 侧栏存在指向 crates/ 的 `file:line` 引用
  当 任一引用指向不存在的文件或行号超出文件长度
  那么 结构检查返回非零退出码并列出失效引用

## 排除范围

- must_use / lint / 中毒 / zeroize 各自的完整机制展开
- 加密方案的密码学评估
