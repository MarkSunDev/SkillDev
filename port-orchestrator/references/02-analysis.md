# 02 分析模板

## 1. Recon 角色

| Agent | 读取 | 产出 |
|---|---|---|
| `recon-shell` | 入口/导航/DI/构建/权限/深链/推送/后台 | shell 报告 |
| `recon-feature-*` | feature 页面/状态/use case/API/存储/埋点/文案 | feature 报告 |
| `recon-data` | API/proto/DTO/错误码/存储 key/迁移 | data 报告 |
| `recon-platform` | SDK/通道/推送/支付/IM/通话/图片/定位 | platform 报告 |
| `recon-risk` | 历史 bug/平台限制/审核约束 | risk 报告 |

## 2. Active / Native / Dead

每个文件标：

- `active`：当前生产路径引用。
- `active-native`：活跃但为原生/系统/SDK 宿主。
- `dead`：无生产引用。

规则：

- dead 不进入行为契约。
- active-native 只复用触发/状态/规则，UI 按目标栈重写（除非用户同意复用）。
- 注释/旧文档可能过期，以引用链为准。

## 3. 每个 Feature 必须回答

1. 入口有哪些？同一动作几个入口？
2. 状态：登录/会员/会话/批次/已消费/一次性。
3. 状态转移与失败回退。
4. API：protoId/字段/参数/顺序/错误码/幂等。
5. 额度/计费/权益：谁扣、扣多少、共享范围、服务端权威字段。
6. 持久化：key/跨天/跨进程/切号。
7. 埋点：事件/参数/顺序/用户属性。
8. 文案：按钮/Toast/空态/错误/Loading。
9. 平台差异：源能力/目标能力/缺口。
10. 历史 bug：能否转回归用例。

## 4. 规则矩阵

```text
入口 × 登录态 × 会员态 × 会话态 × 批次 × 服务端返回 × 持久化 × 文案 × 埋点
```

每行必须有测试 ID；没有测试 ID 的规则不算完成。

## 5. 服务端语义

必须逐条确认，不按字段名猜：

- `limit` 是页大小还是撮合上限？
- 服务端是否排除已消费？
- `matched` 在哪个接口返回？
- `isFree` 与 `leftCoin` 的关系？
- `leftFreeMsgCount` / entitlement 谁是权威？
- 写操作是否幂等？重复回调怎么处理？
- 每日/每周边界用服务端还是客户端时区？

## 6. 平台差异

对每项列：

| 源行为 | 目标能力 | 缺口 | 处理 | 测试 |
|---|---|---|---|---|

重点：生命周期/进程死亡、返回键、键盘/insets、权限、后台/FGS、通知、推送冷启动、浮窗、图片方向、深链、支付回跳、WebView、实时音视频、IM、埋点、存储、角标、字体缩放。

## 7. 分析报告结构

```text
# Analysis Report
1. 基线事实
2. Active / Native / Dead
3. 业务动作清单（入口/API/额度/状态）
4. 规则矩阵
5. 状态机
6. API 契约
7. 文案/埋点
8. 平台差异
9. 源项目已知 bug/不一致
10. 1.0.0/1.1.0 候选划分
11. 风险/spike
```

## 8. G1 清单

- [ ] 核心 flow 有 behavior contract
- [ ] 每个动作有 rule matrix + 测试 ID
- [ ] 核心状态机
- [ ] API fixture/smoke
- [ ] copy deck
- [ ] analytics contract
- [ ] platform capability matrix
- [ ] 历史 bug → 回归用例
- [ ] 未决问题有 owner/截止
