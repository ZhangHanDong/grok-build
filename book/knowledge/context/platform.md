---
kind: context
title: 功能全景、配置治理与配套设施（第一部/第五部素材）
tags: [features, config, auth, memory, voice, acp, build-system]
sources:
  - crates/codegen/xai-grok-pager/docs/user-guide/
  - crates/codegen/xai-grok-config/
  - crates/codegen/xai-grok-config-types/
  - crates/codegen/xai-grok-auth/
  - crates/codegen/xai-grok-secrets/
  - crates/codegen/xai-grok-memory/
  - crates/codegen/xai-grok-voice/
  - crates/codegen/xai-codebase-graph/
  - crates/codegen/xai-acp-lib/
  - crates/build/xai-proto-build/
  - prod/mc/
stale: false
---

# 功能全景与配套设施

## 用户功能全景（ch1）

用户指南 24 篇（docs/user-guide/），三层：基础（入门/认证/快捷键/斜杠命令/配置）、
核心扩展（主题、MCP、Skills=SKILL.md 提示包、Plugins 含市场、Hooks、BYOK 自定义模型、
AGENTS.md、Memory）、高级（Headless `grok -p`、ACP/IDE、子代理与人格、会话管理
save/load/resume/rewind/compact、Sandbox、Plan 模式、后台任务 /loop/monitor、
终端支持 tmux/SSH/truecolor/OSC52、权限 dontAsk/safe-bash、Dashboard、用量监控）。

## 配置与认证（ch18）

六层配置合并（低→高）：/etc/grok/managed_config.toml → $GROK_HOME/managed_config.toml →
config.toml → requirements.toml（云缓存，Ed25519 静态签名，signed_policy）→
/etc/grok/requirements.toml → macOS MDM 托管偏好（ai.x.grok）。企业管控层可覆盖用户层、
支持 fail-closed 启动；每层先应用 version_overrides。
xai-grok-config-types：叶子类型依赖倒置。xai-grok-auth：HttpAuth+AuthCredentialProvider
trait 缝 + reqwest 重试中间件；支持浏览器登录/API key/OIDC/device-code。
xai-grok-secrets：正则脱敏器，清洗发往 Sentry/Mixpanel 的出站数据。

## Memory / Voice / Codebase-graph / ACP（ch18/ch2）

- memory：~/.grok/memory/，blake3(cwd) 分区；SQLite 混合检索 FTS5+sqlite-vec KNN、MMR 去冗、
  query_expansion；「dream」自动整合（时间/会话数门控+锁生命周期）与 /flush。默认关，
  --experimental-memory / GROK_MEMORY=1。
- voice：仅听写，tokio-tungstenite+rustls 连 xAI STT；macOS/Windows cpal，Linux 走系统
  录音器保 musl 静态二进制。
- codebase-graph：tree-sitter 查询驱动，go-to-def/ref、增量索引、rayon、mmap 零拷贝；
  Rust/Go/JS/TS/Python。
- acp-lib：gateway 双向 channel（agent/client 双 side）、stdio/WebSocket、_meta 分布式
  tracing span。

## 工程化（ch2）

- 75 crate 四组：crates/build(2)、crates/codegen(大部)、crates/common(20)、prod/mc(1,
  cli-chat-proxy-types——与签名器共享的"已签名部署配置信封"契约)。
- 划分哲学：极细粒度 + 依赖倒置（-types/-auth trait 缝），利于 Bazel 增量编译与测试隔离。
- 构建：xai-proto-build 封装 prost/tonic/pbjson；find_protoc 三级查找（$PROTOC→bin/protoc→
  PATH）；bin/protoc 是 dotslash 脚本（不入库二进制，声明各平台 sha256+URL，protoc 29.3）。
- 根 Cargo.toml 生成式只读；README 明示"总是 -p 单 crate 构建"。
