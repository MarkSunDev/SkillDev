---
name: gemini-figure-prompt-zh-lite
description: Use when the user provides academic paper methodology or raw data and wants a ready-to-paste Gemini Web prompt to generate a publication-ready diagram or data plot. Triggers on requests like "生成论文图提示词", "帮我画方法图", "生成数据可视化提示词", or when Methodology/Raw Data fields are present.
---

# Gemini 学术图提示词 Skill（Lite）

## 目标

输入论文方法或数据，输出一条可直接粘贴到 Gemini Web 的提示词：
- `diagram`：方法/系统框架图
- `plot`：数据图（要求 Gemini 只输出 Python 脚本）

输出必须是：
1. 一条最终提示词
2. 一个固定"使用提示"块

禁止输出：过程解释、多候选、内部推理。

---

## 1) 隐私优先（先去敏）

先替换敏感信息，再进入生成流程。

敏感信息包括：
- 个人信息：姓名、邮箱、手机号、微信/QQ、地址、证件号
- 凭据：API Key、Token、Secret、Cookie、私钥、数据库连接串
- 组织内部信息：内网地址、私有链接、本地绝对路径

替换规则：
- 使用占位符：`[PERSON_1]`、`[EMAIL_1]`、`[PHONE_1]`、`[SECRET_1]`、`[ORG_1]`、`[PATH_1]`
- 保留语义，不保留可识别细节
- 最终输出中禁止出现原始敏感值

---

## 2) 输入与自动路由

支持字段：
`任务类型`、`参考图`、`领域`、`图型`、`宽高比`、`语言`、`Figure Caption`、`Methodology`、`Raw Data`

自动判定：
- 仅有 `Raw Data` => `plot`
- 仅有 `Methodology` => `diagram`
- 两者都有且未指定 => 只问 1 个问题：本次要 `diagram` 还是 `plot`？

默认值：
- 宽高比：`16:9`
- 语言：`中文`
- diagram 图型：`流程/管线`
- plot 图型：`柱状图`

---

## 3) 精简流程（R-P-S-C）

- Retriever：选图型（流程/系统/泳道/对比；柱/线/散点/热力等）
- Planner：整理模块、连线、变量映射（`x/y/hue/style/facet`）
- Stylist：应用论文风格（白底、低饱和、统一线宽/字号）
- Critic：输出前自检并修订

### 强制质量闸门

四项评分（100 分）：
- Fidelity 40：是否忠实原文/原数据
- Readability 25：是否清晰不拥挤
- Style 20：是否风格一致
- Safety 15：是否仍有敏感信息

通过阈值：
- `diagram >= 88`
- `plot >= 90`

不达标：只做最小修订，不整体重写。

---

## 4) 长输入降级策略

- Methodology 过长：提取"模块-连线-训练信号"骨架，不粘贴原文
- Raw Data 过大（>300 行或 >25KB）：只问 1 个问题（聚合方式或是否限制前 N 行）
- 未确认前，不擅自截断核心数据

---

## 5) 模板 A（diagram）

````
你是一名资深学术图示绘制专家。
请根据以下规格生成论文发表级方法图。

生成前内部校验：
1) 模块与连线完整且忠实；
2) 无标题/图注/编号（如 Figure 1）；
3) 无敏感或可识别个人信息。

{若有参考图：仅迁移视觉风格（配色/线宽/圆角/留白/图标风格），禁止复刻具体内容、Logo、水印或独特角色。}

【Figure Description】
{按"全局结构 -> 分区 -> 模块 -> 连线 -> 训练要素"写清楚：位置、形状、颜色、线型语义。}

【Visual Spec】
- 画布：白底，宽高比 {16:9 默认}
- 语言：{中文/English}
- 字体：标签无衬线；数学变量衬线斜体
- 颜色：主文本 #111827；强调 #2563EB/#10B981；分区底色 10-15% 低饱和
- 几何：圆角 10-14px；线宽 1.8-2.0px；虚线 dash 6/gap 4
- 禁止：标题、图注、编号、水印、重阴影、彩虹色图、无意义装饰
````

---

## 6) 模板 B（plot）

````
你是一名资深科研可视化工程师。
请根据以下规格输出可运行 Python 脚本（pandas + seaborn + matplotlib，可选 numpy）。

生成前内部校验：
1) 数值与 Raw Data 完全一致；
2) 不臆造列名或数据点；
3) 代码自包含可运行。

硬性要求：
- 只输出一个 Python fenced code block（开头为 \`\`\`python）。
- Raw Data 必须嵌入脚本字符串解析，不读外部文件。
- 导出 `figure.pdf` 和 `figure.svg`（tight_layout）。

【Plot Description】
{图型理由、变量映射、可读性策略}

【Plot Spec】
- 图型：{柱状/折线/散点/热力/雷达/甜甜圈/组合}
- 宽高比：{16:9 默认}
- 语言：{中文/English}
- x/y/hue/style/facet：{列名或无}
- 风格：paper context，色盲友好，despine
- 中文：若为中文，配置 YaHei/SimHei + axes.unicode_minus=False
- 禁止：3D、重阴影、Figure 1、Jet/Rainbow、仅靠颜色区分

Raw Data（必须原样嵌入）：
```text
{Raw Data}
```
````

---

## 7) 固定使用提示（必须追加）

```text
---
💡 提升效果的技巧：
1. 把上方提示词完整复制到 Gemini Web，建议重新生成 2-3 次。
2. 若不满意，附上结果截图 + 原提示词，要求定向修正。
3. 有参考图时，务必与提示词在同一条消息发送。
4. 若出现标题/编号，追加：请去掉图中的标题和编号。
```

---

## 8) 结束标准

- 无敏感信息泄露
- 内容与数据忠实
- 用户可直接复制使用
