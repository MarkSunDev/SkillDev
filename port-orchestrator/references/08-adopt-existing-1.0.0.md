# 08 接管已有 1.0.0（port adopt）

## 1. 什么时候用

- 你已经自己做了一个 1.0.0，想用 `port status` / `port plan 1.1.0` 管理后续。
- 项目没有 `docs/port/state.yaml`，或 state 与代码不一致。
- 你想先审计，再决定 1.1.0 做什么。

**不要**直接对没有 state 的项目跑 `port status` 然后声称“已完成”。

## 2. 最小输入

不要一上来让用户填长模板。只要：

```text
port adopt
基线：/path/to/source 或 git URL（可选；有就对照）
目标：默认当前目录；不在当前目录才给路径
```

然后**只读扫描目标项目**并推断；不要扫描电脑/家目录/桌面。

### 只问 3 个无法推断的问题

1. **推断出的 1.0.0 范围对不对？**  
   展示从代码/文档/包/路由扫描出来的 as-built 清单，让用户增删。
2. **哪些是你真机/发布验证过的？**  
   区分“代码写了 / 能构建 / 有单测 / 真机验过 / 已发布”。
3. **1.1.0 目标是什么？**  
   如果基线可用，自动对照生成候选，让用户改。

其他（技术栈、版本、入口、API、配置、TODO、测试文件、构建变体）都自己扫描。

默认：

- 先在只读模式扫描，不改代码。
- gate 先标 `claimed`/`partial`，不标 `passed`。
- 用户确认后再规划 1.1.0。

## 3. 扫描清单

只读：

- README / docs / CHANGELOG / release tags
- package/build 文件（Flutter/Android/RN/iOS）
- tests / CI / scripts
- TODO/FIXME/HACK
- feature flags / disabled entries
- config placeholders / `.env.example` / `google-services.json` / keystore
- 最近 release/提测记录
- 已知 bug/issue 文档

不做：

- 不把“有代码”当“已验证”。
- 不把“用户说完成”当“G5 passed”。
- 不擅自改业务代码。

## 4. 产出

```text
docs/port/
  state.yaml                 # adopted: true; phase: ADOPTED_1_0
  adopt/
    00-as-built.md           # 实际范围/入口/未做项
    01-evidence.md           # 构建/测试/CI/真机/发布证据
    02-gaps.md               # 缺口/未验证/风险
    03-1.1.0-plan.md         # 基于缺口生成
    04-completeness.md       # 完整性矩阵
  manual-config.md
```

`00-as-built.md` 必须区分：

- 代码存在
- 能构建
- 有测试
- 真机验证
- 已发布

这五件事不是一回事。

## 5. Gate 语义

| 状态 | 含义 |
|---|---|
| `pending` | 没做/没查 |
| `claimed` | 用户说做了，代码/文档有迹象；未验证 |
| `partial` | 部分完成/部分验证 |
| `verified` | 有构建/测试/真机/差分证据 |
| `failed` | 验证失败 |
| `waived` | 明确接受风险 |

接管时：

- G4 默认 `claimed` 或 `partial`。
- G5 默认 `pending`，除非有完整 parity/真机证据。
- 1.1.0 计划必须把 `claimed` 的缺口列出来。

## 5.1 完整性矩阵（你不需要先知道完不完整）

`port completeness` 对照基线生成 `adopt/04-completeness.md`：

| 状态 | 含义 |
|---|---|
| `verified` | 有测试/真机/差分证据 |
| `implemented` | 代码存在，未验证 |
| `missing` | 基线有，目标没有 |
| `unknown` | 无法判断（缺基线/缺证据/缺入口） |
| `not-in-scope` | 明确不在 1.0.0 |

规则：

- 没有基线 → 只能做“目标自身一致性审计”，完整性标 `unknown`。
- 有基线 → 按 active 入口/规则/状态/API/文案/埋点逐项对照。
- `unknown` 必须列出“缺什么证据”，不能藏。
- 只有全部 1.0.0 scope 项 `verified`，G4 才能 `verified`。
- 有 `missing/unknown` → G4 `partial`；先决定补 1.0.0 还是接受债务进 1.1.0。

## 6. 审计（port audit）

按目标栈跑可自动检查：

```bash
# Flutter
flutter analyze
flutter test
flutter test integration_test
flutter build apk --debug

# Android
./gradlew testDebugUnitTest
./gradlew assembleDebug
./gradlew detekt

# RN
npm test
npm run lint
npx tsc --noEmit
```

同时检查：

- TODO/FIXME
- 硬编码 key/域名
- 配置缺失
- 测试覆盖的模块
- 构建变体
- 发布包/签名

审计结果写到 `adopt/01-evidence.md`；不通过就标 `failed`/`partial`，不掩盖。

## 7. 1.1.0 规划

从 `02-gaps.md` 生成：

- 未验证的 1.0.0 规则 → 回归测试
- 缺失的 SDK/配置 → adapter/config 任务
- 未做的业务 → 垂直切片
- 平台缺口 → spike/channel
- 手动配置 → `manual-config.md`

然后：

```text
port status
port plan 1.1.0
port build 1.1.0
```

## 8. 示例交互

```text
用户：port adopt，基线 /path/to/source，目标当前目录。
Agent：自动扫描 → 展示推断的 1.0.0 as-built → 只问 3 个问题
      （范围对不对 / 哪些真机验过 / 1.1.0 目标）。
用户：修正/确认。
Agent：产出 state/adopt 报告 → 跑 port audit → 汇总 claimed/verified。
用户：确认。
Agent：port status 可读；可以 plan/build 1.1.0。
```

## 9. 风险

- 用户记忆与代码不一致 → 以代码/证据为准。
- 没有测试 → 不能标 verified。
- 没有 parity → 不能标 G5 passed。
- 配置缺失 → 功能可能假可用。
- 1.1.0 直接开工 → 先把 1.0.0 缺口列清。
