# Manual Config: <project>

> 不要在聊天/仓库里放真实密钥。仓库只放占位符/`.env.example`。

## 1. 清单

| Key | 用途 | 填写位置 | 格式 | 阶段 | 状态 | Owner |
|---|---|---|---|---|---|---|
| | | | | 1.0.0/1.1.0 | missing | |

## 2. 控制台入口

| 平台 | 用途 | 入口 |
|---|---|---|
| Firebase | FCM/Google Services | |
| Tencent Cloud | IM / TUICallEngine / TIMPush | |
| Google Play Console | 订阅/金币 SKU | |
| BytePlus | 埋点/AB | |
| Sentry | 崩溃 | |
| AppsFlyer | 归因 | |
| Forter | 风控 | |

## 3. 填写顺序

1. 后端/API base
2. IM SDKAppID / userSig（服务端）
3. FCM / TIMPush
4. GP SKU
5. Sentry
6. 1.1.0：BytePlus / AppsFlyer / Forter

## 4. 安全

- `.env`/keystore/`google-services.json`/`local.properties` 按项目规则 gitignore。
- CI 用 secret manager。
- 客户端不放大客户密钥。
- 日志脱敏。

## 5. 验证

- 无 key：可编译/功能降级或 fail-fast。
- 填 key：登录/IM/推送/支付/埋点/崩溃/归因逐项验证。
- 配置检查脚本：`tool/check_config`。

## 6. 用户确认

- 填写人：
- 日期：
- 未完成项：
