# Android Skills

内部 Android 产品交付 skill 集合。每个子目录都是一个自包含的 agent skill：`SKILL.md` 是入口和工作流，`references/` 放方法论与契约，`scripts/` 放可执行校验工具，`assets/` 放模板与素材。

适用于支持 `SKILL.md` 约定的 agent 运行时（ZCode、Codex、Claude Code 等）。目录名与 `SKILL.md` frontmatter 的 `name` 保持一致。

## 技能目录

### 产品交付

| Skill | 用途 | 典型触发 |
| --- | --- | --- |
| [social-app-delivery](social-app-delivery/) | 跨栈（Android / iOS / Flutter / React Native / Web）构建或移植生产级社交发现 App，以行为契约、垂直切片和证据标准驱动。 | "build/port a social app"、"社交 App 交付" |
| [between-version-rebuilder](between-version-rebuilder/) | 从 Between 1.0 基线规划并重建 1.1 / 1.2 版本阶梯，保持 Romi 后端契约和商业规则。 | "Between 1.1"、"release ladder"、"parity audit" |
| [replicaNew](replicaNew/) | 从自有源码做功能等价、指纹无关的 clean-room 复刻；七阶段 + 原创性 / 行为 / 上架品质门禁。 | "复刻"、"clean-room rebuild"、"code-distinct rebuild" |

### 商店物料

| Skill | 用途 | 典型触发 |
| --- | --- | --- |
| [brand-store-assets](brand-store-assets/) | Logo、App 图标、商店五图、海报、Feature Graphic、设备 mockup 与虚构人物；确定性 HTML/CSS → PNG。 | "logo"、"app icon"、"商店五图"、"store screenshots" |
| [app-store-prd-metadata](app-store-prd-metadata/) | 给 PRD 补 App Store 基本信息、审核备注、五图计划、英文隐私政策 / 条款草稿。 | "App Store metadata"、"review notes"、"privacy policy" |
| [google-play-prd-metadata](google-play-prd-metadata/) | 给 PRD 补 Google Play 元数据、审核备注、五图 + Feature Graphic、App content 声明、法务草稿。 | "Google Play metadata"、"data safety"、"feature graphic" |

### 合规

| Skill | 用途 | 典型触发 |
| --- | --- | --- |
| [legalH5](legalH5/) | 生成隐私政策 / 用户协议 / 删除账户三张响应式 H5，`site.json` 一处改域名与主体。 | "法务页"、"隐私政策"、"删号页" |
| [content-policy-gate](content-policy-gate/) | 透明、确定性的内容可用性门禁（地区 / 年龄 / 账号状态）；只接受声明输入，可解释、可审计。 | "content gate"、"age gate"、"regional gating" |
| [app-store-legal-review](app-store-legal-review/) | 把当前构建的事实整理成英文 ToS、Privacy、儿童安全、删号四页初稿，含 preflight、HTML 清单和法务交接包。 | "上架协议审核"、"四页协议"、"隐私政策草稿"、"删除账户页面"、"app-function-checklist" |

## 仓库结构

```text
android_skills/
├── README.md
├── social-app-delivery/
│   ├── SKILL.md
│   ├── README.md
│   ├── agents/openai.yaml
│   ├── references/
│   └── assets/
├── replicaNew/
│   ├── SKILL.md
│   ├── README.md
│   ├── references/
│   ├── scripts/
│   └── templates/
└── ... 其余 skill 目录
```

每个 skill 目录都可以单独复制或软链到 agent 的 skills 目录，不依赖仓库里的其他目录。

## 安装

```bash
git clone git@gitlab.sitinai.com:sunxiaoyang/android_skills.git
cd android_skills
```

ZCode 从 `~/.agents/skills/` 发现用户级 skill：

```bash
mkdir -p "$HOME/.agents/skills"
for d in */; do
  [ -f "$d/SKILL.md" ] && ln -sfn "$(pwd)/${d%/}" "$HOME/.agents/skills/${d%/}"
done
```

Codex 从 `~/.codex/skills/` 发现：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
for d in */; do
  [ -f "$d/SKILL.md" ] && ln -sfn "$(pwd)/${d%/}" "${CODEX_HOME:-$HOME/.codex}/skills/${d%/}"
done
```

只安装某一个 skill 时，把对应目录单独复制或软链过去即可。

## 使用

安装后可以按名称触发，也可以直接用自然语言描述任务：

```text
/replicaNew        # ZCode 斜杠命令
$replicaNew        # Codex 技能引用
Use replicaNew to rebuild this app from its source.
Use legalH5 to generate privacy, terms, and delete-account pages.
Use google-play-prd-metadata to add the Play submission sections to this PRD.
```

每个 skill 的 `SKILL.md` 都写了触发条件、工作流、硬边界和产出位置；`README.md` 提供更短的入口说明。

## 依赖

- Python 3.9+。大多数脚本只用标准库。
- `brand-store-assets` 需要 Pillow、NumPy 和一个 Chromium 内核浏览器：

```bash
python3 -m pip install -r brand-store-assets/requirements.txt
export BROWSER_BIN="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"  # 可选覆盖
```

- `app-store-prd-metadata` / `google-play-prd-metadata` 的 `--check-files` 需要 Pillow；不做栅格文件校验时不需要。
- `legalH5`、`replicaNew`、`content-policy-gate`、`between-version-rebuilder` 无第三方依赖。
- 不需要 Node.js。

## 校验工具

| Skill | 命令 | 作用 |
| --- | --- | --- |
| replicaNew | `python3 replicaNew/scripts/sweep.py <new-project> --config replica/origin.json` | 扫描原项目名字、包名、域名、色值、key、证书残留 |
| replicaNew | `python3 replicaNew/scripts/simcheck.py <origin> <new> --markdown` | 量化代码 8-gram containment |
| replicaNew | `python3 replicaNew/scripts/contrast.py replica/design/tokens.json` | 校验 token 配色的 WCAG 对比度 |
| app-store-prd-metadata | `python3 scripts/check_metadata.py metadata.json` | 校验 App Store 字段限额 |
| app-store-prd-metadata | `python3 scripts/check_gallery.py gallery.json --pretty` | 校验五图 manifest 与栅格文件 |
| google-play-prd-metadata | `python3 scripts/check_metadata.py metadata.json` | 校验 Play 字段限额 |
| google-play-prd-metadata | `python3 scripts/check_gallery.py gallery.json --pretty --check-files --assets-dir ./assets` | 校验截图、图标和 Feature Graphic |
| brand-store-assets | `python3 scripts/check_assets.py --gallery out/apple/gallery.json --store apple --pretty` | 校验商店素材尺寸、格式和透明度 |
| between-version-rebuilder | `python3 scripts/audit_originality.py --reference <ref> --candidate <new>` | 源码 / 资产近似重复审计 |
| legalH5 | `python3 scripts/build.py site.json --check` | 校验配置与占位符，不输出 |
| app-store-legal-review | `python3 scripts/prepare_brief.py --config app-legal.json --checklist checklist-result.txt --out legal-brief.md` | 校验事实配置、填充 Prompt、与清单交叉核对 |
| app-store-legal-review | `python3 scripts/check_draft.py --draft legal-draft.md --config app-legal.json --checklist checklist-result.txt` | 检查协议必备条款、禁用承诺、占位符、邮箱与功能覆盖 |
| app-store-legal-review | `python3 scripts/preflight.py --config app-legal.json --scope four-pages` | 检查四页协议缺失的法律事实 |
| app-store-legal-review | `python3 scripts/check_four_pages.py --terms terms-of-service.md --privacy privacy-policy.md --child-safety child-safety-policy.md --deletion account-deletion.md --config app-legal.json` | 检查四页协议的儿童安全与删号要求 |

## 分支模型

```text
main        受保护，只通过 Merge Request 合并
develop     日常集成分支
feature/*   从 develop 切出，完成后 MR 回 develop
```

本次技能上传提交在 `develop` 分支，`main` 不做直接提交。发布时从 `develop` 向 `main` 发 MR。

## 不纳入仓库

- `flicker-store/`：约 94MB 的生成商店物料，属于产物而不是 skill。
- `_refs/`：旧版 skill 快照归档，内容与根目录下四个 skill 重复，避免重复发现。
- `.DS_Store`、`__pycache__/`、`.venv/` 等本地产物。

## 安全约定

- 不提交 keystore / `.jks`、`app-config.local.json`、`google-services.json`、API key、token 或真实用户数据。
- 示例和模板只使用占位值；`replicaNew/examples/` 中的 keystore 口令、个人邮箱和 token 已脱敏。
- 新 skill 的脚本从环境变量或本地配置文件读取凭据，不把真值写进仓库。

## 新增 skill

1. 新建目录，目录名与 `SKILL.md` frontmatter 的 `name` 一致。
2. `SKILL.md` 写清触发条件、工作流、硬边界和产出。
3. 补一份 `README.md`，说明何时使用、输入、产出、命令和关联 skill。
4. 需要时增加 `references/`、`scripts/`、`assets/`；脚本保持可直接运行。
5. 更新本 README 的技能目录表。

## 许可与归属

内部使用。各 skill 引用的第三方字体、图标和素材，其许可证与出处记录在对应 skill 的 `references/` 或 `README.md` 中；对外发布前需按各自许可证复核。
