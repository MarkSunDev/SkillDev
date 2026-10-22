---
name: legalH5
description: >-
  为 App 生成三张合规 H5 页面（隐私政策 Privacy Policy / 用户协议 Terms of
  Service / 删除账户 Delete Account），静态响应式单文件 HTML，域名/App 名/联系
  邮箱全部由 site.json 统一配置、一键烘焙替换，页面间互链并对接客户端
  app-config 的 legal URL。Use when the user says "法务页", "隐私政策页面",
  "隐私/协议/删号 H5", "隐私链接", "privacy policy page", "terms page",
  "account deletion page", mentions legalH5, or needs store-listing legal
  URLs for an app release. 通常是 replicaNew rebind/audit 阶段的配套 skill。
---

# legalH5 — App 合规三页（隐私 / 协议 / 删号）

产出三张可直接上传任意静态托管的页面 + 一份 `site.json` 配置。**域名统一替换 =
改 site.json 一处再跑一次烘焙脚本**，全站链接、canonical、og:url 同步换新。

```
legal-site/
├── site.json              唯一配置：域名/App名/邮箱/生效日期/版本
├── templates/             三张模板（占位符形如 {{APP_NAME}}）
└── dist/                  烘焙输出（upload 这个目录）
```

```bash
python3 scripts/build.py site.json          # 烘焙 dist/，占位符缺失即报错
python3 scripts/build.py site.json --check  # 只校验不输出
```

## site.json

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
    "privacy": "/privacy", "terms": "/terms", "delete-account": "/delete-account"
  },
  "paths": { "index": "privacy.html", "outDir": "dist" }
}
```

## 三页各自的必含内容（模板已内置，按 site.json 填）

**privacy.html（隐私政策）**
谁在处理（App 名+联系邮箱）、收集的信息类别（账号资料、UGC 内容、设备标识、
使用数据、交易数据）、用途、共享（服务提供商/法律要求）、广告标识、数据保留、
用户权利（访问/删除，加州 CCPA 段）、儿童隐私（声明 18+ 不 knowingly 收集）、
安全、政策更新、联系方式。**文末显式列出数据接收方类别表**（IM 提供商、支付、
崩溃统计等——从客户端 app-config 的 sdk 清单取，别写客户端没有的）。

**terms.html（用户协议）**
接受条款与资格（18+）、账号（设备匿名账号的说明）、虚拟货币与订阅（金币不可退款
的表述按商店政策口径写、订阅自动续订披露）、用户内容与行为规范（禁止骚扰/未成年/
非法内容）、举报与封禁、IP 与许可、免责声明、责任限制、适用法律与争议解决、
变更与终止、联系方式。

**delete-account.html（删除账户）**
页面目的（申请删除账号及数据）、**应用内路径**（Settings → Delete Account，
GP 审核对"应用内可发起删除"有硬要求，H5 页只是补充说明）、删除范围（账号资料、
UGC、云端数据）与**保留例外**（法律要求的交易记录）、处理时限（如 30 天）、
发起方式（应用内 or 邮件，邮箱给 site.json 的 contactEmail）、与注销登录的区别。

## 起草规则（沿用 app-store-prd-metadata 的法务纪律）

- 只描述**当前构建真实存在**的数据流与功能；SDK 清单以客户端 app-config 为准。
- 措辞用 "may" 和类别级描述，**不写绝对否定句**（"we do not sell" 这种），
  不承诺固定保留期限。
- 一个联系邮箱覆盖所有 privacy/support/deletion/rights 渠道。
- 18+ 年龄门槛写了就必须是构建里真实执行的。
- 输出为交付前草稿：发布前过一次人工/法务复核，版本号与生效日期随 site.json 更新。

## 与客户端/replicaNew 的对接

- 客户端 app-config 的 `legal.privacyPolicyUrl/termsUrl/accountDeletionUrl`
  指向 `https://{domain}{pages.*}`——烘焙后跑一次 sweep 确认客户端没有旧域名字符串。
- 商店提交（GP Data Safety / Apple privacy 承诺）与这三页**描述同一套事实**；
  audit 阶段核对两处一致。
- 换主体：site.json + 客户端 app-config 各改一次，两处跑烘焙 + sweep 即完成。

## 页面工程要求

- 单文件自包含（内联 CSS，无外部字体/脚本），任意静态托管可用；
- 移动端优先响应式（商店审核基本在手机上看），正文 ≥15px、可读排版；
- 三页头部互链（Privacy / Terms / Delete Account）+ 返回 App 的提示；
- `<title>`、canonical、og:url 均烘焙自 site.json；
- 无 cookie、无统计脚本（法务页自己别成为隐私问题）。
