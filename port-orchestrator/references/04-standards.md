# 04 开发规范

## 1. 通用架构

```text
app/shell        # Router、Shell、全局 Overlay、DI
core/            # 网络、存储、埋点、平台适配、设计系统
domain/          # 纯业务：实体、状态机、service、port
data/            # repository、DTO、mapper、fixture
features/        # 页面、controller/notifier、widgets
test/            # unit/contract/widget/golden
integration_test/
tool/            # 架构/契约/差分/文案检查
docs/port/
```

规则：

- domain 不依赖 UI/框架/SDK。
- feature 不互相依赖；跨 feature 由 app 装配。
- 三方 SDK 只在 adapter。
- 业务判断只在 domain service/state machine。
- 一个动作一个 service；所有入口共用。
- 状态不可变；sealed/enum + exhaustive。
- 用户可见文案集中管理。
- 埋点事件/参数由契约生成。

## 2. 状态所有权

每个状态：

- 唯一 owner。
- 生命周期。
- 持久化方式。
- reset 触发（登出/切号/跨天/跨周/会员变化/支付/通话结束/进程死亡）。
- 测试。

禁止：

- Widget 里存业务状态。
- 多个单例各存一份。
- 本地加减服务端权威字段。
- 一次性/冷却/批次只放内存。

## 3. 埋点

- 契约 YAML 是唯一源。
- 生成事件名/参数/枚举/页面 key/用户属性。
- 禁止手写字符串。
- 1.0.0 Local JSONL；1.1.0 real adapter。
- 事件序列/重复点击/页面曝光/登录解绑测试。
- 双端 diff + 数据侧签字。

## 4. 文案

- 所有用户可见字符串进 copy deck/ARB。
- 按钮/Toast/空态/错误/Loading 逐字对齐。
- 文案是产品契约，不是 UI 细节。
- 刻意偏差登记。

## 5. SDK 边界

1.0.0/1.1.0 都遵守：

- 核心闭环 SDK 可以真实接入（网络、IM、RTC、支付、Push）。
- 增长/观测/风控 SDK 按阶段接。
- **UI SDK 不进生产**，除非用户明确同意。
- 平台通道只包基础 SDK/系统能力，不包页面。
- SDK 版本锁死；升级走 ADR + 全量回归。

## 6. 目标栈适配

| 目标 | 重点 |
|---|---|
| **Flutter** | domain 纯 Dart；Widget 不写业务；平台通道只包基础 SDK；不用 TUICallKit/TUIKit 等 UI SDK |
| **Android Compose** | ViewModel/StateFlow；Composable 不写业务；导航/insets/生命周期 |
| **Android Java XML** | Activity/Fragment/Adapter 薄；状态在 ViewModel/domain；生命周期/线程/nullability |
| **React Native** | TS domain；screen 薄；native module 只包 SDK；导航/列表/键盘/后台 |
| **iOS** | VC 薄；domain/状态机独立；权限/后台/推送/图片管线 |

## 7. 测试与门禁

| 层 | 内容 |
|---|---|
| domain | 每条规则/状态转移/跨入口不变量 |
| data | DTO/API 契约/fixture/错误码 |
| UI | widget/golden/状态 |
| integration | 主路径/失败/冷启动/推送/深链/进程死亡 |
| parity | 基线 vs 目标差分 |
| device | 真机矩阵 |

工具（按目标栈）：

```text
tool/check_architecture
tool/check_sdk_imports
tool/check_copy
tool/check_analytics_contract
tool/check_no_todos
tool/parity_diff
```

## 8. Definition of Done

- [ ] 所有入口
- [ ] 所有状态/失败分支
- [ ] 规则/状态测试
- [ ] API fixture/契约
- [ ] 文案
- [ ] 埋点事件序列
- [ ] 持久化/重启/切号
- [ ] 平台边界（返回/键盘/权限/后台/推送）
- [ ] golden/E2E/差分
- [ ] parity 报告签字
- [ ] feature flag/回滚
