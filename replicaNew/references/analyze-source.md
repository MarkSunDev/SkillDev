# 阶段 1：spec 溯源（从源码提取产品规格）

目标：把原项目读"薄"——产出一份**不含任何实现细节**的产品规格书，让后续阶段可以完全不
打开原项目。原项目在本阶段是只读的行为参照物（behavior oracle）。

产出三件套（放新项目 `replica/` 下，模板在 `templates/`）：
- `spec.md` —— 产品规格书
- `features.csv` —— 功能矩阵
- `origin.json` —— 残留特征清单（给 sweep.py 用）

完整实战样例见 `examples/buzzme-android-analysis.md`。

## 分析顺序（从外到内，别一上来就读业务代码）

1. **构建骨架**：settings.gradle.kts 模块列表、根/app 的 build.gradle.kts、
   libs.versions.toml、AndroidManifest、applicationId/namespace、minSdk/targetSdk。
   这一步确定"它是什么形态的工程"。
2. **文档与 CI**：README、docs/、CHANGELOG、.gitlab-ci.yml/.github workflows、
   scripts/、tools/。文档往往直接暴露产品定位、团队结构、阶段规划。
3. **入口与导航**：Application 类（初始化了什么 SDK）、MainActivity、主导航
   （底部 tab 结构、路由体系）。从这里拉出**页面清单**。
   顺手收集原 App 截图（真机截图优于商店图）：每页面四态 + 每种 dialog/toast 触发
   瞬间，按 `S03-filled.png` 命名存 `replica/screens/`——这是 design 立形阶段
   （references/design-system.md）的输入。
4. **网络层**（社交 App 的心脏）：base URL 与多环境、Retrofit/OkHttp 配置、
   拦截器（鉴权头/签名/UA/设备指纹）、token 刷新、错误统一处理、全部 API 接口定义。
5. **业务域逐个过**：登录注册 → 匹配/推荐 → 聊天/IM → 付费/会员 → 内容/Feed →
   风控/举报。每个域找到 domain/feature 模块和数据模型。
6. **第三方 SDK 盘点**：gradle 依赖 + Manifest + Application 初始化 + 配置文件
   （google-services.json、strings.xml 藏 key、local.properties、BuildConfig）。
7. **git 考古**：git log 作者邮箱、.mailmap、remote URL、submodule 指向——
   主体关联痕迹的主来源之一。

## 各业务域要挖什么（社交 App 通用清单）

| 域 | 必须记录进 spec 的 |
| --- | --- |
| 登录注册 | 支持的方式、每种的流程分支、账号归类规则（审核号/白名单号）、token 生命周期与续期、存储方式 |
| 匹配/推荐 | 拉取接口与参数（limit/窗口）、筛选条件（年龄/性别/距离的口径——经纬度还是邮编）、滑动语义（左/右/超喜欢的请求差异）、每日配额与键名、双向匹配判定字段 |
| 聊天/IM | 消息类型清单、通道（自建 TCP / 三方 IM SDK）、已读回执、正在输入、会话列表排序 |
| 付费/会员 | 商品来源（服务端下发 or 硬编码 SKU）、购买流程（哪个 API 发什么凭据）、验单接口、会员判定字段、权益矩阵、余额不足行为、计费周期（如通话 60s 扣费） |
| 内容/Feed | 发布/点赞/删除/举报流程、媒体上传方式（直传 OSS 还是内嵌字节） |
| 风控 | 举报类型、拉黑生效范围、封禁的错误码表现 |

**业务规则必须精确到字段和数值**（"每日 45 like / 60 nope"、"60 天未同步则静默重登"、
"type=-1 必须停住"）——模糊的规格会在重写时走样。数值不确定就在 spec 里标注置信度。

## origin.json：残留特征清单

spec 阶段顺手挖出"能关联到原项目的所有指纹"，写成 sweep.py 的配置：

```json
{
  "names":       ["Kira", "buzzme", "naya", "Lira"],
  "packages":    ["com.pserver", "com.buzzme.android", "com.overthefence.buzz"],
  "domains":     ["nobuzzme.com", "lumosolo.com", "sitinai.com"],
  "colors":      ["#FF6B35"],
  "keys":        ["1600002475"],
  "certs":       ["buzzme.jks", "<keystore-alias>"]
}
```

挖的位置：域名（gradle.properties/BuildConfig/字符串硬编码）、包名（applicationId
变体、namespace、proto java_package）、家族互引（注释里"照 naya/对齐 kira"）、
SDK appKey、keystore 文件名与口令、客服邮箱拼法、结算 misc 键名。
**兄弟项目也要列入 names**——同一批代码派生的产品互相之间就是最大的相似度来源。

## spec 阶段的红线

- 规格书里禁止出现原项目的类名/文件名/包名/注释内容。写"服务端在响应里返回双向匹配
  标记"，不写"SwipeCardResponse.trigger_match"。
- 低置信度的推断必须标注（"代码里推断，需产品确认"），别把猜测写成事实。
- 别忘了**挖负向信息**：明确不做的功能（如"永不做 silent passthrough"）同样要进 spec，
  否则重写时可能好心加上一个下架风险功能。
- 原项目的构建脚本、CI、契约工具链只记"能力清单"，重写时按新工程自己的习惯重建——
  工具链形态本身也是代码指纹。
