# app-store-legal-review

把 App 当前版本的真实功能、数据、权限和 SDK 事实，整理成上架用的四页英文法务包：
**用户协议（Terms of Service）**、**隐私政策（Privacy Policy）**、
**儿童安全声明（Child Safety Policy）**、**删除账户（Account Deletion）**，
外加 HTML 功能清单、事实简报和机械 QA 报告。

来源是飞书文档《App 上架协议审核 · 操作指引》（revision 47）。这个目录把其中的
Prompt、清单工具和交接流程补成了可执行 skill，并按 Tinder / Bumble / Hily 的公开
页面补齐了四页规范、删号 Google Form 流程和缺失信息预检。

## 安装

仓库根目录执行：

```bash
ln -sfn "$PWD/app-store-legal-review" "$HOME/.agents/skills/app-store-legal-review"
```

ZCode 会从 `~/.agents/skills/` 发现它；也可以只复制本目录，skill 不依赖仓库里的
其他 skill。

## 四页流程

```bash
# 1. 写事实配置（字段说明见 references/preflight.md）
cp app-store-legal-review/assets/app-legal.example.json app-legal.json
$EDITOR app-legal.json

# 2. 预检：缺什么会直接列出来，缺失时不要开始起草
python3 app-store-legal-review/scripts/preflight.py \
  --config app-legal.json --scope four-pages

# 3. 用浏览器打开清单，按当前构建勾选，点「生成结果」后粘贴到文件
open app-store-legal-review/assets/app-function-checklist.html
pbpaste > checklist-result.txt

# 4. 生成 Terms + Privacy 简报
python3 app-store-legal-review/scripts/prepare_brief.py \
  --config app-legal.json \
  --checklist checklist-result.txt \
  --out legal-brief.md

# 5. 生成四页 Markdown：
#    terms-of-service.md / privacy-policy.md /
#    child-safety-policy.md / account-deletion.md
#    页面大纲见 references/four-page-set.md；
#    Google Form 删号见 references/google-form-deletion.md。

# 6. 机械检查
python3 app-store-legal-review/scripts/check_draft.py \
  --draft legal-draft.md \
  --config app-legal.json \
  --checklist checklist-result.txt \
  --out qa-report.md

python3 app-store-legal-review/scripts/check_four_pages.py \
  --terms terms-of-service.md \
  --privacy privacy-policy.md \
  --child-safety child-safety-policy.md \
  --deletion account-deletion.md \
  --config app-legal.json \
  --out qa-four-pages.md
```

把四页草稿、`checklist-result.txt`、两份 QA 报告和事实简报一起交给法务。

如果只需要旧的 Terms + Privacy 两页流程，预检加 `--scope tos-privacy`，
其余命令不变。

## 关键规则

- 只写当前构建真实存在的功能、数据流、权限和 SDK；不预勾内购、广告 SDK、AI、
  背景调查、ID 验证等未上线能力。
- **不能编造主体和邮箱。** 四页版本必须由用户提供开发者法定名称和专门的儿童安全
  邮箱；缺失就停下来问，不写占位符。
- Terms / Privacy / Deletion 用同一个通用联系邮箱；Child Safety 必须用独立的、
  已创建可收信的 CSAM 邮箱（如 `childsafety@...`），不能用通用反馈邮箱。
- 不写 "we do not collect/sell/share" 或未经核实的固定保留天数；用 `may` 和
  类别级措辞。删除前的可取消/可恢复窗口是产品事实，可以写，但必须准确。
- 初稿不列具体 SDK / 数据接收方 / 跨境目的地，留给法务按清单补。
- 18+ 年龄门槛必须与构建实际执行的验证一致；没有相机/定位权限就不要声明。
- 适用法律、仲裁机构、仲裁地不写死。Tinder 用 Delaware/NAM，Bumble 用 Texas，
  Hily 用 California；按用户确认的事实写。
- Google Form 只是删号请求渠道，不是 Play 的硬性要求；统一用**品牌表单 POST 到
  `formResponse`**，不嵌入 Google Form、不跳转 Google Form 页面。responses 进
  表单所有者的 Google 账号，不会到 Google Play，也不会自动删号。
- 用 Google Form 时，preflight 会强制要求 `formResponse` 接口和四个 `entry.*`
  字段 ID（email/account/reason/details）；缺一个就阻塞起草。
- 别逐字照抄 Tinder / Bumble / Hily 的文本、主体、地址、邮箱、保留期限或承诺。
- 这不是法律意见；发布或提审前必须由合格律师复核。

## 目录

```text
app-store-legal-review/
├── SKILL.md
├── README.md
├── assets/
│   ├── app-function-checklist.html
│   └── app-legal.example.json
├── references/
│   ├── drafting-prompt.txt
│   ├── checklist.md
│   ├── four-page-set.md
│   ├── mature-dating-app-benchmark.md
│   ├── google-form-deletion.md
│   ├── preflight.md
│   └── source.md
└── scripts/
    ├── preflight.py
    ├── prepare_brief.py
    ├── check_draft.py
    └── check_four_pages.py
```

`preflight.py` 只做事实完整性检查：缺失字段、邮箱格式、Google Form URL、删除
窗口、仲裁字段等。`check_draft.py` 检查 Terms/Privacy 的必备章节、禁用承诺、
占位符、邮箱一致性、清单功能/数据类别覆盖和 SDK 名称泄漏。
`check_four_pages.py` 额外检查儿童声明的开发者名称/CSAM 邮箱/零容忍/举报/执法，
以及删号页的应用内路径、网页 URL、卸载/退出登录区分、保留说明和取消窗口。
它们都是机械检查，不能替代律师审阅。
