# buzzme-android 深度代码分析（replicaNew spec 阶段实战样例）

> 2026-10-21 由 replicaNew spec 流程产出。原项目只读，未修改。
> 本文档即 `references/analyze-source.md` 清单跑一遍的结果样例，
> 也是复刻 buzzme 类产品时的"社交 App 常见形态"参考。
> 敏感值已脱敏：keystore 口令、个人邮箱、token 值不在本文档中出现。

## 0. 项目定位

iOS 社交 App BuzzMe 的 Android 复刻（行为以 iOS 为唯一参照，网络层照同族 naya-android）。
P2 阶段（1.0.0 内测）：登录/引导/5 Tab/IM/视频通话/Feed/真实付费已落地。
2 人团队约 21 周，GitLab 自建仓。

## 1. 项目骨架

- 27 模块：`:app` + core×11（common/arch/designsystem/ui/network/tcp/data/analytics/platform/im/call）
  + domain×7（account/chat/call/social/me/membership/videomatch）+ feature×8
  （login/chats/calls/discover/contacts/me/membership/notifications）。
- 依赖规则 R1–R7 在配置期强制（feature 互不依赖、domain 无 UI、三方 SDK 只许 6 个白名单模块引用）。
- 模块内统一 `port/ + impl/ + data/ + domain/ + di/`（Ports & Adapters）。
- 纯 Kotlin（main 332 文件），100% Jetpack Compose 单 Activity 无 Fragment。
- MVI 变体：`BaseScreenViewModel<S>` + UiState 四态（Idle/Loading/Content/Error）+ 一次性 effects 流。
- DI 用 Koin 4.1.1；AGP 8.13.2 / Kotlin 2.2.21；compileSdk/targetSdk 36，minSdk 26。
- 网络：OkHttp 4.12 + Retrofit 2.11（自定义 PbConverter）+ protobuf-kotlin-lite。
- 其他：Coil 2.7、MMKV 1.3.14、uCrop、security-crypto、detekt。
- 三套 applicationId：debug `com.buzzme.android` / release `com.overthefence.buzz`
  （线上包名，XmlClassGuard 改包）/ releaseLocal `com.local.buzzmetest`。
- tools/：9 个 Python 契约脚本（埋点契约、proto 注册表生成、文档一致性校验）+ bundletool。
  CI：两 stage（契约闸 + android 构建），版本号绑定 tag/pipeline。

## 2. 核心玩法

5 Tab：Chats · Calls · Contacts · Discover · Me（开白账号 Discover 与 Chats 对调）。

| 功能 | 位置 |
| --- | --- |
| 登录/引导/资料 | feature:login + domain:account（Onboarding 5 步/开白 10 步） |
| 会话/1v1 聊天（文本/图片/语音/GIF/正在输入） | feature:chats + domain:chat + core:im（腾讯 TXIMSDK） |
| 视频/语音通话+计费+充值半屏 | feature:calls + domain:call + core:call（TUICallEngine+LiteAV，自绘界面） |
| 通讯录（People you may like + 联系人 + 邀请） | feature:contacts + domain:social |
| Discover（Nearby 列表 + Feed 发帖双分段） | feature:discover + domain:social |
| 他人主页/举报/拉黑 | feature:discover/profile |
| Me（资料/签到/拉黑/金币/会员） | feature:me（3783 行巨型文件） |
| 付费墙/订阅管理 | feature:me/membership + domain:membership |
| 通知（喜欢我/访客+角标轮询） | feature:notifications |
| 礼物（面板/发送/余额） | feature:chats + domain:chat/gift |
| VideoMatch 直呼（聊天列表推荐行→直接视频） | domain:videomatch（TCP 60030/60032 曝光/撤单） |

主流程：BuzzMeRoot 按会话状态三落点（LoggedOut/Pending/Active）→ 登录（Apple 按钮走
设备静默 FastLogin、邮箱密码仅审核/开白放行）→ pending 走 Onboarding → 上传资料 →
通知权限 → 首帖 → 主 Tab。

1.1.0 规划：Nearby 划卡（45 like/60 nope 配额+付费墙）、恋爱铃、亲密值、三方收银台
（CustomTabs + 回落 IAP）。明确永不做：iOS 的 Silent passthrough（下架风险）。

## 3. 网络层（复刻时最需要注意的形态）

**不是 REST**，是 proto-id 单端点协议：
- 全部接口共用唯一端点 `POST baseUrl 根路径`，请求体 = `[4 字节大端 proto id][Protobuf 消息体]`。
- proto id ↔ 消息类型注册表 ProtoIdMap（3322 行、800+ 命令号，Python 生成）。
- proto 源码是 git submodule（同族共享，`com.pserver.proto.archat` HTTP 4000–5121/19000 段、
  `com.pserver.proto.aichat` TCP 60001+）。
- 多环境：api-prod/dev.nobuzzme.com、prod/dev-tcp.nobuzzme.com:8000（gradle.properties 注入 BuildConfig）。
- 公共请求头：`Authorization: Bearer <token>`（未登录发空 Bearer）、`x-other-uid: <deviceId>`
  （`buzzme.<ANDROID_ID>`，审核账号钉死特殊 deviceId）、`params` JSON 头（os/app_version/locale/app_name/package_name）。无签名。
- 无 refresh token：401 → 清会话登出；60 天未同步则 FastLogin 静默换新 token。
- 错误处理：ProtoCall 统一超时+重试+归类，CallPolicy 三档（DEFAULT 5s/1 重试、RELAXED 15s、
  NO_RETRY 写操作——重试=把喜欢发两次）。ApiError sealed 8 类。
- TCP 长连接：裸 TCP 16 字节帧 + 5s 心跳 + 前后台重连（后台不保活）。IM 消息走腾讯 TXIMSDK 不走 HTTP。

关键端点（proto id）：FastLogin 4198、EmailLogin 5082、UploadUserInfo 4200、
GetMatchFeedsV3 4552、SwipeCard 4554、GetPostFeed 19036、BuyCoin 4342、VerifyAndroid 4312、
GetSubscriptionsV3 4538、GetCoinProductInfos 4344、CreateCallOrder 4450、SendGift 4356、
UserCheckIn 4332、ReportUserEvent 60041（TCP）等全量见 ProtoIdMap。

## 4. 页面布局

- 单 Activity + Compose，**不用任何导航库**：自研根路由 + 覆盖层栈 + 转场
  （BuzzMeRoot / MainTabsScreen / BuzzSlideFlow / PageBackStack）。
- 底栏自绘 BuzzTabBar（角标=会话+通知未读）；顶栏自研 BuzzBar 五档高度，全程不用 Material TopAppBar。
- 启动：Application（MMKV→Koin→SDK 校验→埋点→会话 restore→IM/TCP→后台刷新）→ MainActivity
  → BuzzMeRoot。无独立 Splash。

## 5. 登录注册

- 主链路：**设备静默登录 FastLogin**（deviceId 认老用户，"Continue with Apple" 当前就传 null 走它）。
- 邮箱+密码：两步（EmailLogin 5082 归类 → FastLogin），仅审核/开白放行；type=-1 密码错必须停住
  （否则会把错密码的人当新设备注册）。忘记密码入口隐藏（后端无接口）。
- 账号归类 type：0 普通 / 1 审核（deviceId 钉死）/ 2 开白（引导 10 步+Tab 对调）。
- token 存储：MMKV `buzzme.session` + Android Keystore 加密整份 AuthUser JSON（键 `session_v1`）。
- proto 里有手机验证码接口（5000 段）但未接。

## 6. 匹配规则

- GetMatchFeedsV3(4552) limit=10 滑动窗口，filter minAge=18/maxAge=90，**LBS 用 zip_code**
  （proto 无经纬度字段，距离文案服务端下发）。
- SwipeCard(4554)：左/右滑 + viewDuration=0，NO_RETRY；响应 trigger_match 判双向匹配。
- 本地：滑动窗口+去重、已消费台账、卡片缓存落盘；每日配额键 daily_like_count/daily_nope_count
  （键名与 iOS 对账红线，StoreUserMisc 同步）。
- VideoMatch：GetRecommendUsersForVideoCall(4588) 会话排重 + TCP 曝光/撤单。
- 推荐字段：faceScore、userType、race、isOnline。

## 7. 付费订阅

- BillingClient 端口 + 三实现：GooglePlayBillingClient（Billing 8.3.0、PendingPurchases、
  自动重连、购买门禁 60s 防重、补单重放、purchaseToken 去重）/ SimulatedBillingClient（dev，
  走后端 FakeBuyCoin 真实结算）/ UnavailableBillingClient。
- **SKU 全部服务端下发不硬编码**：GetSubscriptionsV3 + GetCoinProductInfos + GetGooglePlayProducts。
- 验单（服务端唯一真源）：金币 BuyCoin(4342) 发 product_id+purchase_token；订阅 VerifyAndroid(4312)；
  访客订阅 VerifyVisitorSubscription(4540)。
- 会员：isMember = subscriptionID > 1（freeTier=1）；访客会员=商品 id 含 visitor。
- 权益：免费音视频共享（1 份=60 秒，未领自动领）+ 免费文本；扣费前 precheck，余额不足拉充值半屏。
- 通话计费：60s 一轮 DeductCoinMsg 周期扣费，余额不足业务码 131 不抛错。
- 结算落库键：buzzme.userpaytimes（BuzzMe 专用）/ buy_coin_count / buy_vip_id（沿用 naya 键名）。
- 三方支付留口：CreatePayment 拿 redirect_url CustomTabs + 轮询状态。

## 8. 第三方 SDK

腾讯 IM imsdk-plus 8.6.7019（SDKAppID=1600002475，与 iOS 共用）+ TUICallEngine + LiteAV；
Google Play Billing 8.3.0；Coil；MMKV；uCrop（唯一 manifest 三方 Activity）；
FCM/BytePlus/AppsFlyer/Sentry/Forter 全部只留 NoOp 端口未接。
**key 卫生好**：仓内无藏于 strings.xml 的 key；仅腾讯 SDKAppID（gradle.properties）+ keystore + API 域名。
SDK 隔离：业务层禁止 import 三方（配置期规则 + SdkIsolationTest）。

## 9. 代码指纹（相似度检测特征点）

- 注释：**330/332 个文件含中文**，论文式注释（⚠️ 坑点、"照 iOS Xxx.swift:179"、"照 naya Xxx"
  逐行出处标注）。UI 文案英文。
- 命名：自研组件 Buzz* 前缀（BuzzBar/BuzzScreen/BuzzTabBar/BuzzSlideFlow）；概念名
  Wisp(Toast)/Veil(Dialog)/Blanka(空态)/Husk(骨架)。
- 结构：layer 分层 + 模块内 port/impl；契约驱动的 Python 工具链是家族特征。
- 测试：107 文件，契约快照/状态机/纯函数钉住。
- git：作者 2 人（姓名与邮箱已脱敏：h***@presence.email、i***@163.com），.mailmap 双身份，
  提交全中文，自建 GitLab（gitlab.lumosolo.com）+ CI 镜像 mingc/android-build-box。

## 10. 主体关联痕迹（rebind 阶段必须全部换新的清单）

| 类型 | 值 |
| --- | --- |
| API/TCP 域名 | api-prod.nobuzzme.com、prod-tcp.nobuzzme.com:8000 |
| 法务域名 | nobuzzme.com/privacy-policy、/terms-of-service |
| 客服邮箱 | buzzmeandfeedback+{userId}_{版本}_{机型}@nobuzzme.com（plus-addressing 拼法是家族习惯） |
| 代码仓 | gitlab.lumosolo.com（组织 lumosolo）；proto submodule gitlab.sitinai.com（组织 sitinai） |
| 签名 | app/keystore/buzzme.jks（alias buzzme，口令曾以明文入库，已脱敏；另有 debug.jks） |
| 线上包名 | com.overthefence.buzz |
| 腾讯 SDKAppID | 1600002475 |
| 家族互引 | naya-android、kira、Lira、sitin-rn(rocco)、BuzzMe iOS 的注释级互引 |
| 结算键名 | buy_coin_count/buy_vip_id（沿用 naya）、buzzme.userpaytimes |
| 上传 | 无 OSS 直传（图片 proto 内嵌字节） |

## 对复刻的关键结论

1. proto-id 单端点协议 + 800 命令号注册表 + proto submodule 是与后端的强耦合点——
   换后端则整体重写；保留后端则协议层是"契约"（见 diverge §4 的两种策略）。
2. 付费链已生产级（七态事件流+三验单+补单+misc 键），是功能蓝本；misc 键名是对账红线。
3. 架构纪律（模块规则配置期强制、SDK 隔离、契约代码生成）是工程资产，**模式值得复用、代码必须重写**。
4. 需要剥离的身份痕迹：域名族、双 gitlab 组织、入库 keystore+口令、包名、邮箱拼法、
   以及 330 个文件里指向 iOS/naya 的出处注释——注释本身就是最强的家族指纹。
