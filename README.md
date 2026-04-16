# SkillDev — Claude Code Skill 仓库

存放自定义 Claude Code Skills 的 monorepo。每个 skill 是一个独立目录，包含 `SKILL.md` 及可选的辅助文件。

## 目录结构

```
SkillDev/
├── skills/                          # 所有 skill（主目录）
│   └── <skill-name>/
│       ├── SKILL.md                 # 必须：frontmatter + 正文
│       ├── LICENSE                  # 可选：许可证
│       ├── requirements.txt         # 可选：Python 依赖
│       ├── *.py                     # 可选：辅助脚本
│       ├── tests/                   # 可选：单元测试
│       └── examples/                # 可选：示例图片 / 输出
└── README.md
```

## Skill 列表

| Skill | 描述 |
|-------|------|
| [gemini-figure-prompt-zh-lite](skills/gemini-figure-prompt-zh-lite/SKILL.md) | 将论文 Methodology 或 Raw Data 转为可直接粘贴到 Gemini Web 的学术图提示词 |
| [mobile-code-review](skills/mobile-code-review/SKILL.md) | Flutter / Android / iOS 代码审查，涵盖安全、内存生命周期、UI 性能与架构 |
| [android-app-analyzer](skills/android-app-analyzer/SKILL.md) | 通过包名或本地 APK/XAPK 分析 Android 应用，输出 Manifest 元数据、权限、后台保活策略、推送集成与广告 SDK 报告 |

## 新增 Skill

1. 在 `skills/` 下创建目录，名称只使用字母、数字、连字符
2. 创建 `SKILL.md`，包含 YAML frontmatter（`name` + `description`）
3. `description` 只描述**触发条件**，以 "Use when..." 开头，不描述工作流
4. 安装到本地：`cp -r skills/<name> ~/.claude/skills/<name>`

## 安装

```bash
# 安装单个 skill
cp -r skills/gemini-figure-prompt-zh-lite ~/.claude/skills/

# 安装所有 skill
cp -r skills/* ~/.claude/skills/
```

## SKILL.md 规范摘要

```yaml
---
name: skill-name-with-hyphens        # 只含字母、数字、连字符
description: Use when [触发条件]      # 第三人称；只写 when，不写 how
---
```

- frontmatter 总字符数 ≤ 1024
- `description` 以 `Use when` 开头，描述症状 / 场景，不总结流程
- 参考：[agentskills.io/specification](https://agentskills.io/specification)
