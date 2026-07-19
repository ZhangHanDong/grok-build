spec: task
name: "ch08-media-tools"
inherits: project
tags: [book, chapter, tools, media, image, video]
---

## 意图

为《第 8 章：两层工具抽象》增补一节《媒体生成工具族：从能力门控到终端产物》。
读者是中高级工程师。本节不逐个介绍四个媒体 API，而是用它们串起两个第 8 章尚未
端到端展示的可迁移架构模式：**能力门控的条件注册**（远程 config → 客户端资源注入
→ 工具才注册）与**异步「发起—轮询—下载」长任务工具**（视频生成非一次 return）。
并澄清一个易错点：Grok Build 没有直接的「文本→视频」工具，`/imagine-video` 是一条
组合流水线。本节讲「媒体如何产生」，与第 16 章「媒体如何显示」互补不重复。

## 已定决策

- 落点：`book/manuscript/ch08-tool-abstraction.md` 新增一节，编号 `8.7`，
  现 8.7（codex 对照）顺延为 8.8、8.8（模式提炼）顺延为 8.9；同步更新"设计要点回顾"引用
- 四个工具只作证据：`image_gen`、`image_edit`、`image_to_video`、`reference_to_video`
  （均 `impl xai_tool_runtime::Tool`），重心在两个模式而非 API 清单
- 能力门控以 `xai-grok-agent/src/builder.rs` 的 `with_image_gen_config`/
  `with_video_gen_config` 为证：配置启用才创建 client、注入 Resources、注册工具
- 异步长任务以 `video_gen/mod.rs` 头注三段（发起 → 轮询 `GET /v1/videos/{id}` 到
  `done` → 下载 MP4 落 `<session>/videos/`）+ `VIDEO_POLL_INTERVAL_SECS` 为证
- `/imagine-video` 澄清以 `xai-grok-tools-api/src/slash_commands.rs` 为证：
  它由 `image_to_video` 门控，指令先 `image_gen` 再 `image_to_video`——组合而非原生
- 交叉引用第 16 章终端图像协议（Kitty/iTerm2）说明最终渲染，本节不重复显示机制
- 所有架构性陈述带 `file:line` 引用；中文写作；含 1 张 mermaid（流水线）
- 净新增约 2000–2800 字符

## 边界

### 允许修改
- book/manuscript/ch08-tool-abstraction.md
- book/specs/ch08-media-tools.spec.md
- book/knowledge/context/tools.md

### 禁止做
- 不修改 crates/ 下任何源码
- 不使用无 file:line 溯源的架构性断言
- 不声称 Grok Build 具备直接的「文本→视频」原生工具
- 单段源码粘贴不超过 30 行
- 不深入单个工具的算法实现，不重复第 16 章的终端显示机制

## 完成条件

场景: 能力门控条件注册讲解准确
  测试: ai_review_ch08_media_gating
  假设 读者对照 xai-grok-agent/src/builder.rs 阅读
  当 读者读完能力门控一段
  那么 能说出工具注册取决于远程配置开关，且客户端资源经 Resources 注入后工具才被注册

场景: 异步轮询长任务讲解准确
  测试: ai_review_ch08_media_async
  假设 读者对照 video_gen/mod.rs 阅读
  当 读者读完视频生成一段
  那么 能复述"发起任务 → 轮询状态至 done → 下载 MP4 落地会话目录"三段异步流程

场景: imagine-video 是组合流水线而非原生文生视频
  测试: ai_review_ch08_media_pipeline
  假设 存在「Grok 能直接文本生成视频」的常见误解
  当 读者读完 `/imagine-video` 澄清
  那么 文中明确 `/imagine-video` = image_gen → image_to_video → 轮询 → 下载，无直接文生视频工具

场景: 与第 16 章互补不重复
  测试: ai_review_ch08_media_crossref
  假设 第 16 章已讲终端图像协议与显示
  当 读者读完本节
  那么 本节讲媒体产生并交叉引用第 16 章讲显示，两处无实质重复

场景: 篇幅与结构达标
  测试: check_ch08_media_structure
  假设 成稿位于 book/manuscript/ch08-tool-abstraction.md
  当 编辑运行 book/tools/check_chapter.py
  那么 本节含至少 1 张 mermaid、至少 3 处 file:line 引用，且全章仍满足章级门禁

场景: 引用溯源失败被拒稿
  测试: check_ch08_media_citation_validity
  假设 本节存在指向 crates/ 的 `file:line` 引用
  当 任一引用指向不存在的文件或行号超出文件长度
  那么 结构检查返回非零退出码并列出失效引用

## 排除范围

- 四个工具的内部算法/模型细节、图像编辑的参考图数量上限等 API 参数枚举
- 终端图像协议与显示机制（第 16 章）
- 多模态输入（粘贴图片）的事件处理（第 13 章）
