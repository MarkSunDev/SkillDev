# 06 手动配置清单

> 目标：把所有需要用户手动申请的 appId/key/证书列清楚，并告诉用户**去哪里填**。
> 绝不让用户在聊天里贴真实密钥。

## 1. 清单模板

| Key | 用途 | 填写位置 | 格式 | 阶段 | 状态 |
|---|---|---|---|---|---|
| API_BASE_URL | 后端地址 | `--dart-define` / `.env` / config | string | 1.0.0 | missing |
| IM_SDK_APP_ID | 腾讯 IM | config / `--dart-define` | string | 1.0.0 | missing |
| IM_USER_SIG | IM 登录签名 | **服务端签发，不放客户端** | server | 1.0.0 | missing |
| GOOGLE_SERVICES_JSON | FCM/Google | `android/app/google-services.json` | file | 1.0.0 | missing |
| TIMPUSH_CONFIG | 厂商推送 | `android/app/src/main/assets/timpush-configs.json` | file | 1.0.0 | missing |
| GP_SKU_* | 内购商品 | Play Console + config | string | 1.0.0 | missing |
| SENTRY_DSN | 崩溃 | config / `--dart-define` | string | 1.0/1.1 | missing |
| BYTEPLUS_APP_ID | 埋点 | config | string | 1.1.0 | missing |
| APPSFLYER_DEV_KEY | 归因 | config | string | 1.1.0 | missing |
| FORTER_SITE_ID | 风控 | config | string | 1.1.0 | missing |
| DEEP_LINK_SCHEME | 深链 | Manifest/Info.plist | string | 1.0.0 | missing |
| SIGNING_KEY | 签名 | `key.properties`/keystore | file | release | missing |
| LEGAL_URLS | 法务 | config | string | release | missing |

## 2. 常见填写位置

### Flutter

- `--dart-define=KEY=...` / `--dart-define-from-file=env.json`
- `lib/core/config/app_config.dart`（占位/读取）
- `.env`（gitignore） + `.env.example`（提交）
- `android/app/google-services.json`
- `android/app/src/main/assets/timpush-configs.json`
- `android/key.properties` + keystore（gitignore）
- `ios/Runner/GoogleService-Info.plist`
- `ios/Runner/Info.plist`（权限/深链）
- CI secrets

### Android

- `local.properties`（SDK 路径；不要提交）
- `gradle.properties` / `build.gradle.kts`（非密配置）
- `AndroidManifest.xml`（scheme/权限）
- `google-services.json`
- `timpush-configs.json`
- `key.properties` + `.jks`
- 后端域名/支付 SKU 由构建变体注入

### iOS

- `Info.plist`（权限/URL scheme）
- `GoogleService-Info.plist`
- `*.xcconfig`
- Keychain/CI secrets

### React Native

- `.env` + `.env.example`
- `android/local.properties`
- `android/app/google-services.json`
- `ios/Info.plist`
- native module config

### 后端

- `.env` / secret manager
- IM userSig 签发密钥
- 支付验单密钥
- 推送服务端 key
- Forter/BytePlus/AppsFlyer 服务端配置

## 3. 安全

- 不在聊天/issue/PR 里贴真实密钥。
- 仓库只放占位符/`.env.example`。
- `.env`、keystore、`google-services.json`、`local.properties` 按项目规则 gitignore。
- CI 用 secret manager。
- 日志脱敏。
- 客户端不放大客户密钥（如 IM userSig 由服务端签发）。

## 4. 验证

- key 缺失：功能降级或 fail-fast，不静默。
- 构建：无 key 也能编译。
- 真机：填 key 后逐项验证（登录/IM/推送/支付/埋点/崩溃/归因）。
- 配置检查脚本：`tool/check_config.dart` / `scripts/check_config.sh`。

## 5. 最终输出

`docs/port/manual-config.md`：

- 每条 key 的用途/位置/格式/阶段/状态。
- 控制台入口（Firebase/Tencent/Play/BytePlus/AppsFlyer/Forter）。
- 填写顺序（先 1.0.0 核心，再 1.1.0 增长）。
- 填完后让用户回复“配置完成”，再跑验证。
