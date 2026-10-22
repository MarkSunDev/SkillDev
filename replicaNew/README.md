# replicaNew — 源码在手的功能等价复刻

从你拥有或获授权的源码出发，重建一个功能等价、但代码指纹和主体关联都与原项目切断的新 App。原项目只扮演两个角色：spec 提取阶段的行为参照物，audit 阶段的相似度比对基准；它不是代码模板。

## 两条必须同时守住的线

1. **功能对等**：must / should / could 分级，must 全过才可发布。
2. **指纹无关**：文本相似度、结构相似度、主体关联（签名、包名、SDK key、域名、证书）全部切断，并用工具量化验收。

## 核心纪律：单向信息流

```text
原项目源码 ──(一次性)──▶ replica/spec.md ──▶ 新项目代码
                │
                └──(只在审计时)──▶ simcheck / sweep

原项目截图 ──(一次性)──▶ replica/design/ ──▶ 新项目组件 kit
```

写代码时只看 spec、blueprint、design token 和功能矩阵；遇到 spec 没写清的行为，回原项目只读确认，把结论补进 spec，再合上原项目实现。禁止开着原文件逐行翻译。

## 七个阶段

| # | 阶段 | 产出 |
| --- | --- | --- |
| 1 | spec 溯源 | `replica/spec.md`、`features.csv`、`origin.json`、`screens/` |
| 2 | diverge 立异 | `replica/blueprint.md`（身份、契约/表达边界、换位矩阵、协议策略） |
| 3 | design 立形 | `replica/design.md`、`design/`（tokens、组件契约、gallery） |
| 4 | scaffold 立骨 | 新仓库、新包名、可编译空壳、集中配置 |
| 5 | rebuild 重写 | 垂直切片功能落地、`build-log.md` |
| 6 | rebind 解绑 | `rebind.md` 清单全勾（签名、包名、SDK 账号、域名、支付、仓库） |
| 7 | audit 验收 | `audit-report.md`（原创性 / 行为对等 / 上架品质） |

## 工具

纯标准库 Python 3：

```bash
# 残留扫描：新项目里还有没有原项目的名字/包名/域名/颜色/key/证书
python3 scripts/sweep.py <新项目> --config replica/origin.json

# 相似度量化：新项目有多少 8-gram token 可溯源到原项目
python3 scripts/simcheck.py <原项目> <新项目> --markdown > replica/similarity.md

# 对比度校验：design token 的 WCAG AA
python3 scripts/contrast.py replica/design/tokens.json
```

阈值口径：containment 目标 < 5%，> 8% 不通过，> 15% 说明有整块翻译；sweep 零残留；contrast 任一失败即 exit 1。三个工具都可挂 CI。

## 快速开始

1. 确认源码授权和目标形态：只换客户端，还是连后端一起独立。
2. 收集原 App 截图：每个关键页面四态，每种 dialog / toast / sheet 的触发瞬间，存 `replica/screens/`。
3. 按七阶段顺序执行；4/5 可滚动重叠。
4. 每阶段结束向用户汇报产出和发现，尤其是付费、匹配、风控规则与视觉换骨决策。
5. 双门禁通过才算完成；未通过就在 `audit-report.md` 如实写原因。

## 目录

```text
replicaNew/
├── SKILL.md
├── README.md
├── references/      analyze-source / diverge / design-system / rebuild / disassociate / audit
├── scripts/         sweep.py / simcheck.py / contrast.py
├── templates/       spec-template.md / features.csv / app-config.example.json
└── examples/        buzzme / kira 实战分析 + toy 反面案例
```

## 边界

- 只处理你拥有或获得授权的源码；授权存疑就停下来确认。
- 做真正的独立产品：自己的名字、视觉、代码、账号体系。差异化不能只剩混淆、改名、换色。
- 不做审核规避：不做 reviewer 检测、cloaking、内容伪装，不向商店隐瞒产品间关系。
- 原项目的美术资产、字体、文案、商店素材一律不搬运。

## 关联 skill

- `social-app-delivery` — 功能完成定义和证据标准与其契约式思路一致。
- `legalH5` — rebind / audit 阶段生成并托管隐私、条款、删号三页。
- `app-store-prd-metadata` / `google-play-prd-metadata` — 上架物料与元数据校验。
- `brand-store-assets` — 新 App 的图标和商店五图。
- `content-policy-gate` — 需要地区 / 年龄 / 账号状态门控时的透明实现。
