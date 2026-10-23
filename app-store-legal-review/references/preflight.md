# Preflight: ask for missing facts before drafting

The skill must not guess a legal fact and must not leave placeholders. Run the
preflight check before any drafting:

```bash
python3 scripts/preflight.py --config app-legal.json --scope four-pages
```

If it exits non-zero, send the user the generated "请补齐以下信息" list in one
message. Do not proceed page by page or invent values.

## Required fields

### All pages

| Field | Type | Why |
|---|---|---|
| `app_name` | string | Internal/product name |
| `store_app_name` | string | Exact name shown on the store |
| `developer_legal_name` | string | Required on the child safety page and controller sections |
| `platforms` | array | `iOS`, `Google Play` |
| `region` | string | Distribution region |
| `contact_email` | email | General privacy/support/deletion contact |
| `child_safety_email` | email | Dedicated, monitored CSAM mailbox; must differ from the general contact |
| `monetization` | array | `免费`, `订阅`, `内购`, `广告` |
| `features` | array | Current-build features from the checklist vocabulary |
| `age_gate` | string | Actual gate enforced by the build |
| `permissions` | array | Actual runtime permissions from the merged manifest; `[]` is valid |
| `account_model` | string | `device`, `email`, `phone`, `username`, `other` |
| `sdk_categories` | array | Category-level processors/SDKs, e.g. `即时通讯`, `支付`, `崩溃上报` |
| `sells_or_shares` | string | `yes`, `no`, or `unknown`; drives the opt-out wording |
| `sensitive_data` | array | Categories the user may provide, e.g. sexual orientation, ethnicity, beliefs |

### Terms / disputes

| Field | Type | Notes |
|---|---|---|
| `governing_law` | string | State/country; do not assume Delaware |
| `arbitration_provider` | string | `AAA`, `NAM`, `other`, or `none` |
| `arbitration_venue` | string | City/county/state |
| `arbitration_opt_out_days` | integer | 0 if there is no opt-out |

### Account deletion

| Field | Type | Notes |
|---|---|---|
| `deletion.in_app_path` | string | Exact in-app path |
| `deletion.web_url` | https URL | Public page, no login |
| `deletion.request_method` | string | `google_form`, `hosted_form`, `email`, `in_app_only` |
| `deletion.google_form_url` | https URL | Required when method is `google_form`; for reference/verification |
| `deletion.google_form_response_url` | https URL | Required when method is `google_form`; branded POST target |
| `deletion.google_form_entry_ids` | object | Required when method is `google_form`; all four: `email`, `account`, `reason`, `details` |
| `deletion.cancellation_window_days` | integer | 0 if deletion is immediate |
| `deletion.retention_summary` | string | What may be retained and why |
| `deletion.subscription_cancellation` | string | Required if monetization includes subscriptions/IAP |

### Optional

`privacy_email`, `dpo_email`, `company_address`, `website`,
`store_listing_url`, `data_safety_url`, `effective_date`, `version`.

## Example config

See `assets/app-legal.example.json`.

## User-facing prompt template

The script prints the missing fields and this message. Keep the list
consolidated; do not ask the user one question at a time.

```text
为了生成四页协议，请补齐以下信息（缺失项会阻止起草）：

【App 与主体】
1. App 在商店展示的完整名称：
2. 开发者/运营主体的完整法定名称：
3. 上架平台（iOS / Google Play / 两者）：
4. 分发地区：

【联系方式】
5. 通用法务/隐私/支持邮箱：
6. 专门的儿童安全（CSAM）邮箱（必须与通用邮箱不同，且已创建可收信）：
7. 隐私邮箱/DPO 邮箱（可选）：

【当前构建事实】
8. 实际申请的权限（以合并后的 AndroidManifest 为准，没有就写“无”）：
9. 第三方 SDK/处理方类别（广告、分析、崩溃、支付、IM、云存储等）：
10. 账号体系（设备/邮箱/手机号/用户名）：
11. 商业化（免费/订阅/内购/广告）：
12. 年龄门槛及实际执行的验证方式：

【删除账户】
13. App 内删除路径（例如 Settings → Delete account → Delete）：
14. 公开删号网页 URL：
15. 请求方式（Google Form / 自建表单 / 邮箱）：
16. 如用 Google Form，请给已发布表单的公开链接、formResponse 接口，以及四个 entry.* 字段 ID（email/account/reason/details）：
17. 删除前的可取消/可恢复窗口（几天；没有写 0）：
18. 删除范围与保留例外：
19. 订阅是否需要用户另行取消：

【争议解决】
20. 适用法律（州/国家）：
21. 仲裁机构（AAA / NAM / 其他 / 不仲裁）：
22. 仲裁地：
23. 仲裁退出期（几天；没有写 0）：
```

## Rules

- If a required fact is unknown, stop. Do not draft that page.
- If the user supplies a developer legal name, use it exactly; do not invent an
  entity or address.
- If the child-safety mailbox has not been created, do not put it on the page.
- Google Form integration is branded POST only. Do not fall back to an iframe
  embed or a "open the form" button; those are not the standard. If the
  `formResponse` endpoint or any `entry.*` ID is missing, block and ask.
- If the build has no camera/location/camera permission, do not claim it has
  one; do not ask for it as if it were required.
- If `sells_or_shares` is `unknown`, use qualified privacy wording and flag the
  opt-out mechanism for legal review.
