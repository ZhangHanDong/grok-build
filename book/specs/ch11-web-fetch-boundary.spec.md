spec: task
name: "ch11-web-fetch-boundary"
inherits: project
tags: [book, chapter, sandbox, network, ssrf, web-fetch]
---

## 意图

给《第 11 章：沙箱》新增一节《内核围栏之外：Web 工具自己的网络信任边界》。11.4
讲内核层网络围栏（子进程出站被封），但漏了一条路径：agent 进程**自己**发起的 HTTP。
`web_fetch` 抓不可信 URL，需要在**应用层**自建信任边界。本节讲它的摄取管线（校验→
强制 HTTPS→SSRF 检查→同主机重定向→Content-Type 核对→HTML 清洗转 md→预算裁剪→
过长落 artifact），重点写 SSRF 关卡如实的能与不能，并用 web_search（后端托管）作对照。

## 已定决策

- 落点：`book/manuscript/ch11-sandbox.md` 新增 `11.5 内核围栏之外：Web 工具自己的
  网络信任边界`（紧接 11.4 网络面），现 11.5–11.9 顺延 11.6–11.10；同步更新"设计要点回顾"
- 摄取管线以 client.rs:70 的 fetch 文档 + mod.rs:1 顶注为证
- SSRF 拦私网/link-local/云元数据、放行 loopback、显式拉黑 169.254.169.254，以
  ssrf.rs:1 与 is_blocked_ip 为证
- 过长内容落会话 artifact，以 artifact.rs 为证
- **诚实边界（必须写）**：重定向只跟同主机（client.rs:73）；SSRF 校验的 IP 与 reqwest
  建连时再解析的 IP 之间无绑定，存在 TOCTOU 窗口——**不能宣称消灭 DNS rebinding**
- web_search 作对照：后端托管搜索，本地不直连不可信主机，信任边界位置不同
- 所有架构性陈述带 `file:line`；中文；含 1 张 mermaid（管线关卡）
- 净新增约 2000–2600 字符；保留全章 voice

## 边界

### 允许修改
- book/manuscript/ch11-sandbox.md
- book/specs/ch11-web-fetch-boundary.spec.md
- book/knowledge/context/sandbox.md

### 禁止做
- 不修改 crates/ 下任何源码
- 不使用无 file:line 溯源的架构性断言
- 不把 SSRF 防护宣称成"消灭了 DNS rebinding"或"绝对安全"
- 不重复 11.4 内核网络面的 Landlock/seccomp 内容
- 单段源码粘贴不超过 30 行

## 完成条件

场景: 应用层边界区别于内核围栏
  测试: ai_review_ch11_app_boundary
  假设 读者已读 11.4 内核网络面
  当 读者读完本节开头
  那么 能说出 web_fetch 是 agent 进程自己发起的 HTTP，内核围栏管不到，需应用层自建边界

场景: SSRF 关卡讲解准确
  测试: ai_review_ch11_ssrf
  假设 读者对照 ssrf.rs 阅读
  当 读者读完 SSRF 一段
  那么 能说出它拦私网/link-local/云元数据（含 169.254.169.254）、放行 loopback

场景: 诚实边界写明 DNS rebinding 限制
  测试: ai_review_ch11_honest_boundary
  假设 存在"有 SSRF 防护即绝对安全"的误解
  当 读者读完边界一段
  那么 文中明确重定向只跟同主机，且 SSRF 校验 IP 与建连再解析无绑定、不能宣称消灭 rebinding

场景: web_search 作后端托管对照
  测试: ai_review_ch11_websearch_contrast
  假设 读者读完对照
  当 读者比较 web_fetch 与 web_search
  那么 能说出 web_search 后端代发、本地不直连不可信主机，信任边界位置不同

场景: 篇幅与结构达标
  测试: check_ch11_webfetch_structure
  假设 成稿位于 book/manuscript/ch11-sandbox.md
  当 编辑运行 book/tools/check_chapter.py
  那么 本节含至少 1 张 mermaid、至少 3 处 file:line 引用，且全章仍满足章级门禁

场景: 引用溯源失败被拒稿
  测试: check_ch11_webfetch_citation_validity
  假设 本节存在指向 crates/ 的 `file:line` 引用
  当 任一引用指向不存在的文件或行号超出文件长度
  那么 结构检查返回非零退出码并列出失效引用

## 排除范围

- 内核 Landlock/seccomp 网络封锁（11.4 已覆盖）
- htmd 的 HTML 解析内部、缓存 TTL 细节
- web_search 后端实现
