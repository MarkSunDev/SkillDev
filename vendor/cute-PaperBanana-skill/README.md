# cute-PaperBanana-skill (Lite)

一个精简、隐私优先的 prompt-only skill。
输入 `Methodology` 或 `Raw Data`，输出一条可直接粘贴到 Gemini Web 的提示词，用于生成论文图。

## 特性

- 隐私优先：先去敏再生成（姓名/邮箱/手机号/密钥/路径等）
- 双模式：`diagram`（方法图）/`plot`（数据图脚本）
- 单输出：仅一条最终提示词 + 固定使用提示
- 质量闸门：Fidelity / Readability / Style / Safety
- 无 API 调用：纯提示词工作流

## 快速安装

将 `SKILL.md` 复制到你的 skill 目录，例如：

```bash
cp SKILL.md ~/.agents/skills/gemini-figure-prompt-zh-lite/SKILL.md
```

## 使用方式

在会话里提供：
- `Figure Caption`
- `Methodology`（diagram）或 `Raw Data`（plot）
- 可选：`参考图`、`图型`、`语言`、`宽高比`

然后把输出提示词粘贴到 Gemini Web。

## 输出约束

- diagram：生成学术方法图提示词（白底、可发表风格）
- plot：生成让 Gemini 只输出 Python 脚本的提示词（pandas + seaborn + matplotlib）
- 禁止泄露敏感信息、禁止多候选、禁止过程解释

## 已知边界

- Gemini 对复杂布局是近似渲染，不保证像素级一致
- 超大数据建议先聚合或限制可视化范围
- 结果可作为高质量草图，最终投稿可再矢量重绘

## License

MIT（见 `LICENSE`）
