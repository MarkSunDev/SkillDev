# App 功能与数据清单 · 项目与输出契约

Bundled tool: `assets/app-function-checklist.html`. It is self-contained: inline
CSS and JavaScript, no network calls, no external fonts.

## Sections and items

### ① 基本信息

| Item | Input | Notes |
|---|---|---|
| App 名称（商店用名） | text | Required; the tool refuses to generate without it |
| 联系邮箱 | text | Required; one real, monitored address for every external channel |
| 上架平台 | iOS / Google Play | Multi-select in the bundled copy; the source attachment was single-select |
| 商店分发地区 | 仅美国 / 其他地区 | Single-select; default 仅美国 |
| 商业化模式 | 免费 / 订阅 / 内购 / 广告 | Multi-select |
| 年龄限制 | 18+ / 无限制 | Single-select; default 18+ |

### ② 核心功能

Each item is 是 / 否:

`账号注册 / 登录`, `社交 / 社区 / UGC`, `支付 / 电商交易`, `AI 功能`,
`定位服务`, `相机 / 麦克风`, `通讯录 / 相册访问`, `推送通知`,
`健康 / 健身数据`, `文件存储 / 云同步`.

### ③ 数据收集

Each item is 是 / 否:

`注册信息`, `个人资料`, `广告标识符（IDFA / GAID）`, `设备信息`,
`IP 地址 / 网络状态`, `精确位置（GPS）`, `模糊位置（粗略定位）`,
`使用行为`, `崩溃日志 / 诊断信息`, `聊天 / 评论等用户内容`,
`通讯录内容`, `相册照片 / 视频`, `麦克风录音`, `支付信息`.

### ④ 权限

Each item is 是 / 否:

`相机`, `麦克风`, `位置`, `通知`, `相册`, `通讯录`.

### ⑤ 第三方服务

Each group is multi-select with a mutually exclusive `无` option:

| Group | Options |
|---|---|
| 广告 SDK | 无 / AdMob / Meta / AppLovin / 其他 |
| 数据分析 SDK | 无 / Firebase / AppsFlyer / Adjust / 其他 |
| 崩溃上报 | 无 / Crashlytics / Sentry / 其他 |
| 支付 / 内购 | 无 / App/Play 内购 / Stripe / 其他 |
| 第三方登录 | 无 / Apple ID / Google / Facebook / 其他 |

`其他` is rendered as `其他（待补充）`. Replace it with the actual SDK name and
provider before sending to legal.

### ⑥ 数据处理

Each item is 是 / 否:

`数据是否共享给第三方`, `数据是否出售给第三方`, `数据是否跨境传输`,
`用户能否删除数据 / 注销账户`, `可能被 13 岁以下儿童使用`.

## Defaults and edge cases

- Every yes/no item starts unselected. Unselected counts as `否`.
- Every SDK group starts unselected. Unselected counts as `无`.
- Selecting `无` clears the other options in that group; selecting another
  option clears `无`.
- The age gate defaults to `18+`. When it is `18+`, the generated result reports
  `儿童可用：否（因18+门槛）` regardless of the `可能被 13 岁以下儿童使用`
  answer. If the build has no age gate, change the age selection to `无限制`
  and edit the prompt's age clauses before drafting.
- Platform selection is multi-select in this bundled copy, so an app shipped on
  both stores produces `上架平台：iOS + Google Play`.
- The tool does not submit anything; `生成结果` copies text to the clipboard
  and shows it on the page.

## Generated result format

```text
【App 信息清单】
App 名称：MyApp
联系邮箱：support@myapp.com
上架平台：iOS + Google Play
商店分发：仅美国
商业化：免费、订阅
年龄门槛：18+（进入时验证年龄，低于18岁禁止使用）

核心功能（是）：账号注册/登录、社交/社区/UGC
数据收集（是）：注册信息、设备信息
权限（是）：通知

第三方服务：
  广告：无
  数据分析：Firebase
  崩溃上报：Sentry
  支付/内购：App/Play 内购
  第三方登录：Apple ID

数据处理：共享 是｜出售 否｜跨境 是｜可注销 是｜儿童可用 否（因18+门槛）

（未点击项默认按「否」处理；SDK 未点击按「无」；「其他 SDK」名称待补充）
```

## Cross-checks before handoff

- App name and email match the draft and the config.
- Platform and distribution region match the submission plan.
- Monetization matches the build: do not select subscription or IAP for a free
  build, and do not select advertising without an ad SDK.
- Every `是` in ②-④ is visible in the draft; every `否` is absent from the
  draft's factual claims.
- Every selected SDK appears in the checklist. The first draft keeps these at
  category level; legal adds the names.
- `数据处理` answers match the privacy policy's qualified wording. In
  particular, `出售 否` does **not** license a "we do not sell" sentence; the
  drafting principle is to avoid taking a definitive position.
- `其他（待补充）` has been replaced with real names and providers.

## Four-page additions

The HTML tool covers features, data, permissions, and SDKs. For the full
four-page set, also run `scripts/preflight.py --scope four-pages` and confirm:

- the developer legal name and exact store app name;
- a dedicated, monitored child-safety (CSAM) mailbox;
- the actual runtime permissions from the merged manifest, including the
  absence of camera/location/microphone when they are not used;
- the account model (device/email/phone/username);
- the in-app deletion path and the public web deletion URL;
- the deletion request method (Google Form/hosted form/email); for a Google
  Form, the `formResponse` endpoint and all four `entry.*` IDs for the branded
  POST;
- the cancellation/restore window and retention summary;
- governing law, arbitration provider, venue, and opt-out window;
- whether the app sells/shares data or uses targeted advertising.

The checklist's `出售 否` answer still does not license an absolute "we do not
sell" sentence; use qualified wording and the opt-out mechanism legal approves.
