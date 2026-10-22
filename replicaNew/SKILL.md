---
name: replicaNew
description: >-
  从你拥有源码的原 App 出发，重建一个功能等价、但代码指纹与主体关联全部切断的全新
  App（clean-room 复刻）。七个阶段：源码规格提取 → 差异化设计 → 截图驱动 UI/UX
  立形（token 体系+统一组件）→ 新工程骨架 → 按规格重写 → 主体解绑 → 双门禁审计
  （残留扫描 / 相似度量化 / 行为对等）。Use when the user says "复刻", "基于 XX
  源码做一个新 App", "克隆成无关产品", "clean-room rebuild", "code-distinct
  rebuild", mentions replicaNew, or wants a functionally equivalent app whose code,
  signing, SDK accounts and domains share nothing with the original they own.
---

# replicaNew — 源码在手的功能等价复刻

输入是**你有权使用的源码**，输出是一个**功能等价的全新产品**。原代码在整个流程里只扮演
两个角色：规格提取阶段的**行为参照物**（behavior oracle），审计阶段的**相似度比对基准**。
它永远不是代码模板。

这条线要守住两件事，缺一不可：

1. **功能对等**——用户在新 App 里能做原 App 里的每一件核心的事（按 must/should/could 分级）。
2. **指纹无关**——文本相似度、结构相似度、主体关联（签名/包名/SDK key/域名/证书）全部切断，
   且必须用工具量化验收，不许"我感觉改得够多了"。

## 边界（先读，不可越过）

- 只处理用户**拥有或获得授权**的源码。授权存疑就停下来问。
- 做的是**真正的独立产品**：自己的名字、视觉、代码、账号体系。如果差异化手段只剩下
  "混淆、改名、换色"，按这个 skill 的定义就是失败——停下来重做差异化设计，而不是加壳。
- 不做审核规避：不做 reviewer 检测、cloaking、内容伪装、向商店隐瞒产品间关系的欺诈性
  陈述。产品矩阵用不同主体运营是正常的商业架构，前提是每个主体资料真实、每个产品
  独立成立。参见 references/disassociate.md 的"合规红线"一节。
- 原项目的美术资产、字体、文案、店铺素材**一律不搬运**。复用的是"产品规格"，不是"表达"。

## 核心纪律：单向信息流

```
原项目源码 ──(一次性)──▶ replica/spec.md ──▶ 新项目代码
                │
                └──(审计时比对)──▶ simcheck.py / sweep.py

原项目截图 ──(一次性)──▶ replica/design/（tokens + 组件契约）──▶ 新项目组件 kit
```

- **spec 阶段**把源码翻译成"产品做什么"的规格书，规格书里**禁止**出现原项目的类名、
  文件名、包名、注释。规格书是后续编码的唯一依据。
- **design 阶段**把截图翻译成"视觉文法"，再换骨成全新 token 体系与统一组件契约；
  契约描述"组件有哪些变体/状态"，禁止照抄原 App 的色值、构图与资产。
- **rebuild 阶段**写代码时只看 spec、blueprint 和 design 产出，不回看原项目源码。
  需要确认某个边界行为时，回到 spec 补记录，再按 spec 实现。
- **audit 阶段**才允许把原项目拉回来做机械比对。
- 这套隔离是 clean-room 方法的工程化近似：让"读过原代码"这个事实只沉淀在规格层，
  不沉淀在实现层。

## 七个阶段

| # | 阶段 | 做什么 | 产出 | 详细方法 |
| --- | --- | --- | --- | --- |
| 1 | **spec 溯源** | 读原源码，提取产品规格、功能矩阵、残留特征清单；顺手收原 App 截图 | `replica/spec.md`、`replica/features.csv`、`replica/origin.json`、`replica/screens/` | references/analyze-source.md |
| 2 | **diverge 立异** | 定新 App 身份；做换位矩阵；划契约/表达边界；设计新 API 契约与视觉方向 | `replica/blueprint.md` | references/diverge.md |
| 3 | **design 立形** | 从截图提取视觉文法（色彩/字阶/间距/圆角/阴影）；design.md 视觉章程；换骨设计新 token 体系；立统一组件契约（dialog/toast/sheet/空错载全变体全状态）；gallery 验收 | `replica/design.md`、`replica/design/`（tokens.json、components.md、gallery/） | references/design-system.md |
| 4 | **scaffold 立骨** | 新仓库、新包名、刻意异构的模块骨架、构建与 CI | 可编译的空壳工程 | references/rebuild.md §骨架 |
| 5 | **rebuild 重写** | 按功能矩阵垂直切片，用组件 kit 拼页面，从 spec 出发重写；批量跑 simcheck | 功能逐条落地 + `replica/build-log.md` | references/rebuild.md |
| 6 | **rebind 解绑** | 签名证书、包名、SDK 账号、服务域名、支付、商店主体逐项换新 | `replica/rebind.md` 清单全勾 | references/disassociate.md |
| 7 | **audit 验收** | 残留扫描 + 相似度量 + 行为对等 + 上架品质门槛 + 提交包自检 | `replica/audit-report.md` | references/audit.md |

阶段顺序执行，但 4/5 可滚动重叠（骨架立完就可以开写第一切片）。**任何阶段都不要删除
或污染原项目**——它是只读证据。

## 工具（scripts/，纯标准库 Python 3）

```bash
# 残留扫描：新项目里还有没有原项目的名字/包名/域名/颜色/key/证书
python3 scripts/sweep.py <新项目> --config replica/origin.json

# 相似度量化：新项目有多少 8-gram token 可溯源到原项目（headline 指标，压到 <5%）
python3 scripts/simcheck.py <原项目> <新项目> --markdown > replica/similarity.md

# 对比度校验：design 阶段 token 配色必须 WCAG AA 全过（原色值还会被 sweep 反查）
python3 scripts/contrast.py replica/design/tokens.json
```

三个工具都可以挂 CI：sweep 有残留、simcheck 超阈值、contrast 有失败对就 exit 1。
用法细节和阈值解读见 references/audit.md。

## 工作目录约定

全部规划产物放在**新项目**的 `replica/` 目录（不进原项目，发布时整目录排除出打包）：

```
replica/
├── spec.md          产品规格书（templates/spec-template.md）
├── features.csv     功能矩阵（templates/features.csv），clone 列随进度更新
├── origin.json      原项目残留特征（names/packages/domains/colors/keys/certs）
├── blueprint.md     新 App 身份 + 换位矩阵 + 契约边界 + API/视觉设计
├── screens/         原 App 截图（按页面ID命名，永不入包）
├── design.md        视觉风格章程（场景/anti-reference/形面语言/密度）
├── design/          tokens.json、components.md、gallery/ 验收截图
├── shots/           切片验收截图（视觉过目用）
├── build-log.md     每个切片一行：功能ID、状态、缺口、意外
├── rebind.md        解绑清单执行记录
└── audit-report.md  最终验收报告（similarity.md 由工具生成）
```

## 与其他 skill 的配合

- 上架物料（商店五图、审核备注、隐私政策/条款草案）交给 `app-store-prd-metadata`
  ——它有完整的字段限额与校验脚本，audit 阶段直接引用其结果。
- **法务三页（privacy/terms/delete-account H5）交给 `legalH5`**——独立 skill，
  site.json 统一域名，烘焙脚本一键换新主体；rebind 和 audit 阶段引用其产出。
- 社交产品的交付纪律（功能状态机、证据标准、跨栈移植协议）参考 `social-app-delivery`
  的契约式思路，rebuild 阶段的功能完成定义与其一致。
- Android 侧的构建/装机/截图验证可用会话里的 android-dev / android-cli skill。

## 快速启动

用户给出原项目路径后：

1. 确认两件事再动工：**源码授权**（是用户自己的/已购源码吗）和**目标形态**（同后端新客户端，
   还是连后端一起独立？——这决定 diverge 阶段的协议策略，见 references/diverge.md §4）。
2. **请用户顺手提供原 App 截图**（真机截图优于商店图；每个关键页面四态 + 每种
   dialog/toast 的触发瞬间；直接丢图或放进 `replica/screens/` 都行）。截图是
   design 阶段的输入，没有也能做（从源码布局文件反推文法），但量过的体系比猜的准。
3. 按阶段表顺序走，每阶段结束向用户汇报产出与发现，尤其是 spec 阶段挖出的业务规则
   （付费、匹配、风控）和 design 阶段的换骨决策（色相族、圆角/阴影策略、间距基准）——
   这些值得用户过目。
4. 全部阶段走完、双门禁通过，才算"复刻完成"。任何一项没过就在 audit-report.md 里
   如实写"未通过"及原因，不粉饰。
