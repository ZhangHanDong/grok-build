---
kind: context
title: 第12章移植与合规素材（待成文）
tags: [porting, codex, opencode, license, taxonomy]
sources:
  - crates/codegen/xai-grok-tools/src/implementations/codex/
  - crates/codegen/xai-grok-tools/src/implementations/opencode/
  - crates/codegen/xai-grok-tools/THIRD_PARTY_NOTICES.md
  - THIRD-PARTY-NOTICES
  - third_party/NOTICE
  - crates/codegen/xai-grok-tools/src/tool_taxonomy.rs
  - crates/codegen/xai-grok-tools/src/registry/types.rs
stale: false
---

# 第12章素材（调研代理已产出，待 tech-writer 成文）

## 移植清单
- codex（Apache-2.0，ToolNamespace::Codex）：apply_patch（apply/parser/seek_sequence/errors/tool）、
  read_file/tool.rs（CodexReadFileTool，输出 `L{n}:`，slice/indentation 两模式）、
  grep_files/tool.rs（仅返回路径 --files-with-matches，按 mtime 排序）、
  list_dir/tool.rs（BFS 限深分页，不尊重 gitignore、需绝对路径 tool.rs:333）。
- opencode（MIT，ToolNamespace::OpenCode，导出别名加 OpenCode 前缀 mod.rs:24）：
  bash/edit/glob/grep/read/skill/todowrite/write（8 个）。
- 注册：registry/types.rs:696-707 一次性与自家工具并列；组装成 AgentDefinition::codex()/opencode()
  预设（config.rs:1508-1523），挂 codex_toolset/opencode_toolset + TemplateOverride。

## 移植工程手法（系统性）
(a) 切 I/O 边界成纯函数库：apply_patch 所有函数只吃 &str 零 fs，I/O 只在 tool.rs 经 AsyncFileSystem
    （apply.rs:1-21、tool.rs:1-5）。
(b) 参数命名按方言保留：codex snake_case（file_path），opencode camelCase（filePath/oldString，
    edit/mod.rs:62），测试锁死方言（edit/mod.rs:677/745、read/mod.rs:715）。
(c) 错误类型本地化：ParseError/ApplyPatchError（errors.rs:9/18），Io 存字符串换 PartialEq 可测（errors.rs:29-33）。
(d) 输出归一到共享类型：edit/write 复用 SearchReplaceOutput（edit/mod.rs:7、write type WriteOutput）；
    read 复用 ReadFileOutput、grep 复用 GrepSearchOutput、todowrite 复用 grok_build TodoState；
    edit 直调 grok_build::search_replace::helpers（mod.rs:22），glob/grep 共用 grok_build rg_path。
(e) 逐字移植注释分级：Ported verbatim（seek_sequence.rs:3）、exact port（indentation/slice.rs:1）、
    faithful port（list_dir/grep_files/codex mod.rs:9）、Ported from…but refactored（apply.rs:3）。

## 许可合规（三文件分工）
- 根 THIRD-PARTY-NOTICES（76 万字节）：机器生成的 crates.io/git 依赖矩阵（Part I 逐包 + Part II 全文）。
- third_party/NOTICE：仅 vendored crate（mermaid-to-svg、dagre_rust），末尾指向根 notices。
- crate 级 crates/codegen/xai-grok-tools/THIRD_PARTY_NOTICES.md：管两处 ported 源码 + 打包二进制
  （ripgrep/ugrep/bfs）。**Apache §4(b) 变更声明原文**（:9-12）："Ported files have been modified…
  this file constitutes the prominent notice of those changes required by Apache License 2.0 §4(b)."
  codex 段：上游路径 codex-rs/core/src/tools/handlers/、Copyright 2025 OpenAI + Apache 全文（:16-35）。
  opencode 段：MIT 全文含 Copyright (c) 2025 opencode（:37-64）。源码 mod.rs 顶部指回该文件。
  二进制段处理 PCRE2 例外（:88-93）、bfs 0BSD 礼节收录（:156-158），按 GROK_TOOLS_BUNDLE_* 动态裁剪。

## 归一层（本章视角，机制细节见 ch8）
- ToolNamespace 六值闭合枚举（无 other）：GrokBuild/GrokBuildConcise/GrokBuildHashline/Codex/OpenCode/MCP。
- presentation_name 折叠：read_file 与 Read → "Read"（tool_taxonomy.rs:37-73）。
- x.ai/tool _meta 信封：label=跨 harness 分组键、kind=细分辨识器、name=方言名供诊断（:162-169）。
- 模型看方言 name（file_path vs filePath），UI 按 label 统一呈现。

## 移植 vs 原生差异
- codex list_dir 不尊重 gitignore、需绝对路径（与 grok_build 相反）；grep_files 只吐路径。
- 被"归化"的部分：全经 AsyncFileSystem（沙箱/FileWritten 通知一致），共用自带 ripgrep（~/.grok/vendor/）。
- 保留方言原味错误措辞（oldString is empty…）。

## 维护成本（缺陷，值得写）
- 顶注标确切上游文件路径作对拍锚点 + 分级保真词，但**无 upstream commit/版本 pin**（notice 只有
  Copyright 2025，无 commit/日期），升级靠人工比对。grep_files 顶注引用的 "plan document" 是悬挂引用。

## 意外发现
1. write 是唯一破例：归一成 snake_case file_path（mod.rs:10-13"for grok_build consistency"，测试反断言不含 filePath）。
2. grep_files 半移植：只保留 files-with-matches。
3. 合规动态裁剪：PCRE2 例外、ugrep 待补 notice、bfs 0BSD 礼节收录。
4. apply_patch 为可测性把 Io 错误降级为字符串换 PartialEq。
5. 归一枚举闭合（新 toolset 不加值不编译）vs ToolKind 开放（serde other）——身份严格、能力宽松。
