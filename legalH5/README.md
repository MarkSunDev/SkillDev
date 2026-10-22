# legalH5 — App 合规三页

生成三张可直接上传静态托管的响应式页面：隐私政策、用户协议、删除账户。域名、App 名、联系邮箱、生效日期全部由 `site.json` 统一配置，改一处再跑一次烘焙脚本，全站链接、canonical、`og:url` 同步换新。

## 何时使用

- 新 App 上架前需要隐私政策 / 用户协议 / 删除账户页面。
- 换主体、换域名、换 App 名，需要一次性替换所有法务页链接。
- `replicaNew` 的 rebind / audit 阶段，需要把客户端 `app-config` 的 legal URL 指向新域名。
- 商店后台要求提供可公开访问的账户删除 URL。

## 输入

`site.json` 是唯一配置源：

```json
{
  "domain": "legal.newdomain.com",
  "scheme": "https",
  "appName": "NewApp",
  "contactEmail": "support@newdomain.com",
  "effectiveDate": "2026-10-21",
  "version": "1.0",
  "region": "United States",
  "ageGate": "18+",
  "pages": {
    "privacy": "/privacy",
    "terms": "/terms",
    "delete-account": "/delete-account"
  },
  "paths": { "index": "privacy.html", "outDir": "dist" }
}
```

同时准备当前构建真实存在的 SDK / 数据流清单，隐私政策的数据接收方表要与客户端 `app-config` 一致。

## 快速开始

```bash
python3 scripts/build.py site.json          # 烘焙 dist/，占位符缺失即报错
python3 scripts/build.py site.json --check  # 只校验配置与占位符
```

上传 `dist/` 到任意静态托管即可。三页互链，`privacy.html` 作为入口页。

## 目录

```text
legalH5/
├── SKILL.md
├── README.md
├── site.json              唯一配置
├── templates/             三张模板（{{APP_NAME}} 等占位符）
├── scripts/build.py       烘焙 / 校验脚本
└── dist/                  烘焙输出（上传这个目录）
```

## 三页要点

- **privacy.html**：处理者与联系方式、收集的信息类别、用途、共享方类别、广告标识、保留期、用户权利（含 CCPA）、儿童隐私、安全、更新、联系方式；文末列出数据接收方类别表。
- **terms.html**：接受条款与资格（18+）、账号说明、虚拟货币与订阅、用户内容与行为规范、举报与封禁、IP 与许可、免责声明、责任限制、适用法律与争议解决、变更与终止。
- **delete-account.html**：应用内删除路径、删除范围与保留例外、处理时限、邮件申请方式、与注销登录的区别。Google Play 要求应用内可发起删除，H5 只是补充说明。

## 边界

- 只描述当前构建真实存在的数据流和功能；不写路线图里的功能。
- 用 "may" 和类别级描述，不写 "we do not sell" 这类绝对否定句，不承诺固定保留期限。
- 一个联系邮箱覆盖 privacy / support / deletion / rights 所有渠道。
- 写了 18+ 年龄门槛，构建里就必须真实执行。
- 输出是交付前草稿，发布前需人工 / 法务复核，并同步更新版本号与生效日期。

## 关联 skill

- `replicaNew` — rebind / audit 阶段引用本 skill 的产出，客户端 `app-config` 的 `legal` 段指向新域名。
- `app-store-prd-metadata` / `google-play-prd-metadata` — 商店元数据里的隐私政策、条款、账户删除 URL 与本 skill 保持一致。
