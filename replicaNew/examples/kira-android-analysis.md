# Kira-Android 深度代码分析（replicaNew spec 阶段实战样例）

> 2026-10-21 由 replicaNew spec 流程产出。原项目只读，未修改。
> 与 examples/buzzme-android-analysis.md 对照阅读：两者是"同后端、异表达"的兄弟产品。
> 敏感值已脱敏：keystore 口令、个人邮箱、token 值不在本文档中出现。

## 0. 项目定位

View 体系的滑动匹配社交 App（类 Tinder + 金币通话），与 buzzme 共用同一套
proto 协议家族（com.pserver.proto）与同一腾讯 IM SDKAppId。前身产品是 "Romi"
（Firebase 工程 romi-android、埋点残留 romi_ 前缀）。

## 1. 项目骨架

- 模块：`:app` + core×3（mvi/common/network）+ domain×11 + feature×9（feed/login/
  meinfo/chat/tuicallkit-kt/likevisitor/chargemoney/home/ringdialog）。
  另有 7 个空壳残留目录（intimacy/live 等已砍掉的直播/语音房）。
- 100% Kotlin；**纯 View 体系 + ViewBinding/DataBinding，无 Compose**。
- MVI：MviBaseActivity/Fragment/ViewModel，Intent → Action → MviProcessor →
  Result → reducer；Repository + Local/Remote DataSource。
- DI：Koin 4.1.1。路由：自研 URI 路由 io.github.ilittle7/router 2.2.1 + KSP 注解，
  scheme `kira://app`，约 40 个路径，Activity/Fragment/Dialog/Action 全部 @Router 注册。
- 网络：**Ktor Client 2.3.7**（OkHttp 引擎）+ protobuf-kotlin-lite（不是 Retrofit）。
- minSdk 26 / target 36；debug applicationId `com.kira.app`，release 动态切
  `com.meraki.kirasss`（XmlClassGuard 改包）。
- 主要依赖：MMKV、xlog、Gson、EventBus、Coil 3、yuyakaido CardStackView（滑动卡）、
  Google Billing 8.0、Sentry 8.34、腾讯 IMSDK-Plus 8.8/TUICore/TUICallKit、
  BytePlus RangersAppLog 6.17.4、AppsFlyer 6.17.4、Facebook SDK、Firebase BOM 34.3、
  timpush/fcm、Room、ucrop、PermissionX。

## 2. 核心玩法（5 Tab：Home → Feed → Like → Chat → Me）

| 功能 | 实现 |
| --- | --- |
| 滑动匹配（类 Tinder） | feature:home，CardStackView 卡片（左 Dislike 右 Like，超级喜欢=直接进聊天），Hi 次数消耗 |
| 资料页/喜欢他人 | feature:feed，UserDetailsActivity（浏览即 reportVisitor） |
| 动态/朋友圈 | feature:feed，帖子流+点赞+发布 |
| 喜欢/访客列表 | feature:likevisitor，ViewPager2 双 tab |
| 私聊 IM | feature:chat + 腾讯 V2TIM（ChatActivity 1300+ 行），Room 存 chat round |
| 送礼 | ChatActivity（sendGift proto 扣金币 + TIM 自定义礼物消息） |
| 音视频通话（按分钟金币计费） | feature:tuicallkit-kt（腾讯官方源码裁改版），每轮 deductCoinMsg 扣费，金币<150 弹充值，30 秒倒计时强制 |
| 恋爱铃（假来电弹窗） | feature:ringdialog，TCP 长连接推送（自实现 Socket，端口 8000），接听→视频通话 |
| VIP/充值 | feature:chargemoney，普通 VIP+访客 VIP 双体系+金币 |
| 新消息全局弹窗 | app IMManager 任意页面防抖弹窗 |

没有：直播间、语音房、LBS 地图、短视频社区。

## 3. 网络层

- **协议与 buzzme 同族**：私有 Protobuf-over-HTTP，POST 根路径，
  请求体 = [4 字节 protoId][protobuf 字节]；ProtoIdMap 由 proto 子模块的
  ProtoConfig_*.json 生成（"Do Not Edit Manually"）。
- HTTP：api-prod.kiraji.com / api-dev.kiraji.com；TCP（恋爱铃）：
  **prod-tcp.romipro.com**（注意：与 library.gradle 里的 prod-tcp.kiraji.com 不同，
  ringdialog 模块自己的 BuildConfig 生效，实际走 romipro.com）。
- 公共头：Bearer token、x-other-uid（AndroidId 的 SHA256，MMKV 键
  local_device_id_20251219）、params JSON 头（os/app_version/locale/app_name/package_name）。无签名。
- token：MMKV 明文存储；AutoRefreshTokenAction 按 nextTokenRefreshTime 定时
  refreshToken(4088)；401 → Toast + 强制登出路由。
- 错误处理：ensureSuccess 比对 UserServiceCommonCode + ViewModel Effect → Toast。
- 关键端点（protoId）：fastLogin 4198、createUser 4004、refreshToken 4088、
  uploadUserInfo 4200、getMatchFeedsV3 4552、swipeCard 4554、likeUser 4274、
  reportVisitor 4510、getVisitorList 4512、createPost 19006、getPostFeed 19036、
  sendGift 4356、deductCoinMsg 4448、getCoinProductInfos 4344、buyCoin 4342、
  getSubscriptionsV3 4538、verifyAndroid 4312、verifyVisitorSubscription 4540、
  createCallOrder 4450 等——**protoId 与 buzzme 完全一致**（同一后端协议）。
- IM 走腾讯 V2TIM（SDKAppId=1600002475，与 buzzme 共用！userSig 服务端下发）。

## 4. 页面布局与导航

- 启动：SplashActivity 停 1.5 秒 → pending==false 进 main 否则登录（无 onboarding 页）。
- 登录→注册：分步 Fragment（Account→Nickname→Gender→MatchGender→Age→Looking→
  Photo(ucrop)→Religion/Smoking/Drinking→ZipCode(定位)→uploadUserInfo）。
- 主导航：DisableScrollViewPager（禁滑动 ViewPager1）+ BottomNavigationView，
  FragmentStatePagerAdapter 预加载全部 5 tab；页面跳转全走 URI 路由
  （Dialog 经 DialogContainerActivity 容器）；MatchInterceptor 防充值页/聊天页再弹恋爱铃。

## 5. 登录注册

- **唯一登录方式：设备 ID 一键登录**（fastLogin(deviceId)，10 秒无操作自动登录）。
- fbLogin/gpLogin 是假的——实现仍是 fastLogin + storeUserMisc(login_type)，
  只是**买量渠道标记**；无任何真实 OAuth 调用。
- 账号删除：7 天后重登自动 deleteUser。
- 风控：中国时区直接不登录；登录页上报时区/语言/SIM/充电状态。
- token/MMKV 未加密（无 DataStore/EncryptedSharedPreferences）。

## 6. 匹配规则

- getMatchFeedsV3{limit, zipCode} → user_infos+ext_infos；swipeCard{userId, swipeType}，
  服务端判互配返回成功 → 弹匹配弹窗。
- LBS：客户端不算距离（服务端字段 distance，客户端只格式化"less than 3 miles"）；
  定位只为拿 zip code（FusedLocation+Geocoder 反解，失败回退手工输入+本地 zipcode.json）。
- 筛选：客户端只有 zip code；性别偏好注册期问一次；推荐逻辑全在服务端
  （reportExposure 4568 / uploadUserBehavior 17000 供算法）。
- 配额（UserMisc）：left/right_swipe_count、reward_hi_count、vip_hi_count 同步服务端。
- TCP 侧 C2S_StartMatch/CancelMatch/AddToBoost/AddToVipBoost 用于通话匹配加权。

## 7. 付费订阅

- BillManagerV2（object 单例）：Billing 8.0、PendingPurchases、自动重连、
  连接后自动补单 queryUnfinishedPurchases、订阅带 offerToken、
  obfuscatedAccountId=userId。
- **SKU 服务端下发**：金币 kira_coins*、VIP 订阅 premium*、访客订阅 visitor*
  （前缀从埋点与 startsWith 判断逻辑确认）。
- 验单：金币 buyCoin(androidProductId, purchaseToken)、VIP verifyAndroid、
  访客 verifyVisitorSubscription；无本地 acknowledge（服务端消费语义）。
- VIP：双 VIP（普通+Visitor），VipManager LiveData 广播；权益含周期额度
  （CycleEntitlement 系列）、Hi 次数、等级 4378、签到 streak 4584。
- Paywall：ChargeVipActivity 网格+送金币+防重复；余额不足半屏（视频 30 秒倒计时强充）。
- PaymentControlConfig（iap/waffo/air + paypal/googlepay 三方路由）是 PSP 预留未启用。

## 8. 第三方 SDK

腾讯 IM/TUICallKit（**SDKAppId 1600002475 硬编码，与 buzzme 同一个**）；
腾讯 timpush+FCM（timpush-configs.json，fcmPushBussinessId=46178）；
Firebase（debug 工程 **romi-android**（含前代 Romi 客户端）/ release 工程 kira-android，
google-services.json 双份入库）；BytePlus appId=812405 硬编码 App.kt；
AppsFlyer afAppId（**afSdkKey 传空串，归因实际存疑**）；Facebook 仅归因初始化；
Sentry（DSN 在 Manifest，org=presence-2h，**auth token 曾以明文入库，已脱敏**）；
Google Billing 8.0；XmlClassGuard 1.2.7。

## 9. 代码指纹（相似度特征点）

- 注释中文为主（网络核心层英文）；commit message 全中文。
- 命名：内部包故意用 `com.kkk.*`；历史前缀残留——`Rm/RM`（前身 Romi）、`Kira`、
  `Presence`、proto 包 `com.pserver`；埋点前缀 g_/d_ **+ 残留 romi_ 前缀事件**。
- 结构：严格 feature/domain 成对模块；domain 内统一 data/source/{local,remote} +
  middleware/{action,result} 模板——同一套脚手架批量复制的产物。
- 工具类指纹：DeviceUtil（sha256 AndroidId+日期化 mmkv 键）、ZipCodeUtil（asset 表）、
  Toaster/KeyboardUtil/VibrateUtil/Gsons/TypeConverter/MmkvWrapper/PresenceLogger
  （保留上游作者注释 "Created by dss886"）。
- 复制粘贴特征：LocalUserInfo 转换函数在 TempUserManager 与 UserInfoManager
  逐字段重复两份（约 125 行 ×2）。
- 开源痕迹：tuicallkit-kt 是腾讯官方源码裁改（保留 GenerateTestUserSig、
  liteav 资源 URL）；router 用核心开发者个人开源库 io.github.ilittle7/router。
- 日期化 mmkv 键（swipe_card_show_guide_20260105）是团队特有习惯。

## 10. 主体关联痕迹（rebind 全清单）

| 类型 | 值 |
| --- | --- |
| API 域名 | api-prod.kiraji.com（kiraji.com 族） |
| TCP 域名 | prod-tcp.romipro.com（romipro.com 族——**又一张家族域名网**） |
| CDN/调试 | file.storiesmymotion.com、file.archat.us、tinyurl 外链 |
| 政策页 | sites.google.com/view/privacy-policy-for-kira |
| 代码仓 | gitlab.sitinai.com（sitinai 组织）；proto 子模块 github presence-io/proto（**presence** 线索） |
| 签名 | app/keystore/kira.jks（alias kira，口令曾以明文入库，已脱敏） |
| 线上包名 | com.meraki.kirasss（XmlClassGuard 改包） |
| 腾讯 SDKAppId | 1600002475（与 buzzme 共用） |
| Firebase | 工程 romi-android（前代）+ kira-android；双 google-services.json 入库 |
| 崩溃/埋点 | Sentry org presence-2h（token 曾以明文入库，已脱敏）；BytePlus 812405；timpush 46178 |
| git 作者 | s***@presence.email、l***@sina.com、i***@163.com（与 buzzme 共同作者！）、2***@qq.com（邮箱已脱敏） |
| 前代产品 | Romi（Firebase 工程名、埋点前缀、romipro.com 域名、com.romiandroid.app） |

## 对复刻的关键结论

1. **Kira 与 buzzme 是同一协议家族的两个异构客户端**（protoId 4198/4552/4342 完全一致、
   共用腾讯 SDKAppId、共同作者 ilittle7），互为"换 UI 框架复刻"的实例——
   Kira=View/MVI/Ktor，buzzme=Compose/MVI 变体/Retrofit。这验证了"同后端异表达"
   的可行性，但**也暴露了家族关联点：SDKAppId 共用 + protoId 一致 + 域名族交叉
   （romipro/archat/kiraji/nobuzzme）+ 共同作者邮箱**。
2. 若新 App 要求"账号关联角度毫无关系"，必须连 IM SDKAppId、Sentry org、
   BytePlus appId、Firebase 工程全部换新——这正是 rebind 清单 D 节的来源。
3. 敏感信息先处置：gradle.properties 的 Sentry token、入库的 keystore 与明文密码。
4. TUICallKit 是官方源码裁改——复刻时按"重新集成官方 SDK"处理而不是搬运裁改版。
