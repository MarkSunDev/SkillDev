# Google Play PRD metadata template

Use this structure when the PRD does not already define a presentation. Replace every placeholder with real content or `[待确认]`.

## 1. Google Play 基本信息

| Field | Content |
|---|---|
| App Icon（当前：1 张 512×512 PNG；要求：512×512、32-bit PNG 带 Alpha、≤1 MB） | `[待确认]` |
| Feature Graphic（当前：1 张 1024×500；要求：1024×500、JPEG 或 24-bit PNG 无 Alpha、≤15 MB） | `[待确认]` |
| App Name（当前 X 字符；限制 ≤30 字符） | `[App Name]` |
| Short Description（当前 X 字符；限制 ≤80 字符） | `[Short description]` |
| Full Description（当前 X 字符；限制 ≤4,000 字符，纯文本，不支持 HTML） | `[Full description]` |
| Category（当前：X；限制：单一类目，无子类目） | `[Category]` |
| Tags（当前 X 个；限制 ≤5 个，从 Play Console 提供的标签中选择） | `[tag1,tag2]` |
| 内容分级（当前：X；限制：按 IARC 问卷，各地区分级不同） | `[Rating]` |
| 目标受众（当前：X 岁及以上；限制：按 Target audience and content 声明） | `[Audience]` |
| 广告声明（当前：含广告 / 不含广告） | `[Contains ads / No ads]` |
| 发行地区（当前：X 个地区；限制：按发行计划） | `[Regions]` |
| Contact email（当前 X 字符；限制：有效邮箱，公开展示） | `[Email]` |
| Website（当前 X 字符；限制：有效 HTTPS URL，可选） | `[URL or 不适用]` |
| Privacy Policy URL（当前 X 字符；限制：有效 HTTPS URL，必填） | `[URL]` |
| Terms URL（当前 X 字符；限制：有效 HTTPS URL） | `[URL]` |
| 账户删除 URL（当前 X 字符；限制：提供账户的 App 必须同时提供应用内删除入口和网页链接） | `[URL or 不适用]` |
| Promo video（当前 X 字符；限制：公开或未列出的 YouTube URL，可选） | `[YouTube URL or 不适用]` |
| 运营主体（当前 X 字符；限制：与协议、隐私政策及开发者账号一致） | `[Legal entity]` |
| 邮箱（当前 X 字符；限制：有效邮箱） | `[Email]` |
| 协议版本号（当前 X 字符；限制：与生效协议一致） | `[Version]` |

待补齐：

- `[待确认]` field names and required source

## 2. Google Play Review Notes

> Keep this section in English and under 300 words. Copy the App access part into Play Console → App content → App access.

Hi Google Play Review Team,

Thank you for reviewing [App Name]. [One sentence describing the app's promise.] To verify it, [the exact first-minute action and expected visible result].

App access:

- Everything is available without an account: `[yes / no]`
- If restricted, sign in at: `[exact path]`
- Email: `[demo email]`
- Password: `[demo password]`
- Additional step: `[invite code, approval, region, or 不适用]`

Screen recording: `[unlisted YouTube URL or 待提供]`

Main areas to test:

- `[Working tab or feature 1]`
- `[Working tab or feature 2]`

Permissions and rationale: `[Only restricted permissions the build requests, or omit]`

Security and privacy: `[Only describe implemented mechanisms, or omit]`

Monetization: `[Google Play billing products and test steps, or omit]`

Age rating: `[Rating and brief reason, or omit]`

Thank you,

[Developer or company name]

## 3. Google Play 五图与 Feature Graphic

Use five individual portrait screenshots in upload order, plus one overview sheet for the PRD, plus one separate feature graphic. Keep the same layout grid across all five screenshots. Render at 1440 × 2560 and again at 1080 × 1920; export flattened RGB JPEG or 24-bit PNG with no alpha channel. Five is the editorial convention; Google Play accepts 2–8 screenshots per device type.

| # | Story beat | Screen / source | Eyebrow | Headline (2 lines) | Supporting copy (2 lines) | Footer | Background | Status |
|---|---|---|---|---|---|---|---|---|
| 01 | Core promise + primary screen | `[screenshot filename]` | `[FEATURE CONTEXT]` | First line / *Second line.* | First line / second line. | `[closing line]` | `[#HEX]` | `[待确认]` |
| 02 | Second product pillar | `[screenshot filename]` | `[FEATURE CONTEXT]` | First line / *Second line.* | First line / second line. | `[closing line]` | `[#HEX]` | `[待确认]` |
| 03 | Third product pillar | `[screenshot filename]` | `[FEATURE CONTEXT]` | First line / *Second line.* | First line / second line. | `[closing line]` | `[#HEX]` | `[待确认]` |
| 04 | Signature differentiator | `[screenshot filename]` | `[FEATURE CONTEXT]` | First line / *Second line.* | First line / second line. | `[closing line]` | `[#HEX]` | `[待确认]` |
| 05 | Personalization / account / trust | `[screenshot filename]` | `[FEATURE CONTEXT]` | First line / *Second line.* | First line / second line. | `[closing line]` | `[#HEX]` | `[待确认]` |

Feature graphic:

- File: `[feature-graphic-1024x500.png]`
- Size and format: 1024 × 500, RGB, JPEG or 24-bit PNG, no alpha, ≤15 MB.
- Headline: `[one short line]`
- Supporting line: `[optional single line]`
- Background: `[#HEX]`
- Status: `[待确认]`

Overview sheet (PRD/review only, not a Play upload):

- Title: `[App] / [Version] / Google Play five-image set`
- Five thumbnails in upload order with labels beneath each image.
- Keep the same palette, typography, and device treatment as the individual assets.

## 4. App content 声明

| Declaration | Current answer | Evidence / notes | Status |
|---|---|---|---|
| Data safety | `[Data types, purposes, encryption, deletion]` | `[SDK inventory reference]` | `[待确认]` |
| Content rating (IARC) | `[Questionnaire summary]` | `[Resulting ratings by region]` | `[待确认]` |
| Target audience and content | `[Age groups]` | `[Families policy status]` | `[待确认]` |
| Ads | `[Contains ads / No ads]` | `[Ad SDKs, if any]` | `[待确认]` |
| App access | `[All open / Some restricted]` | `[Credentials and path]` | `[待确认]` |
| Account deletion | `[In-app path + web URL]` | `[URL]` | `[待确认]` |
| News app | `[Yes / No]` | `[Justification]` | `[待确认]` |
| Government app | `[Yes / No]` | `[Justification]` | `[待确认]` |
| Financial features | `[Yes / No]` | `[Feature set]` | `[待确认]` |
| Health apps | `[Yes / No]` | `[Feature set]` | `[待确认]` |
| Sensitive permissions | `[List and declaration status]` | `[In-app rationale]` | `[待确认]` |

## 5. Privacy Policy & Terms

Use `references/privacy-terms.md` to generate the English drafts. Keep the version and URLs in sync with the application information table and the App content declarations.

| Document | Version | Status | Effective date | Live URL | Notes |
|---|---|---|---|---|---|
| Terms of Service | `[Version]` | `[Draft / Legal review / Live]` | `[Date or 待确认]` | `[HTTPS URL or 待提供]` | `[Draft link or 待提供]` |
| Privacy Policy | `[Version]` | `[Draft / Legal review / Live]` | `[Date or 待确认]` | `[HTTPS URL or 待提供]` | `[Draft link or 待提供]` |

Legal handoff:

- Use one contact email for privacy, support, deletion, rights, and all other external legal contacts.
- Generate Terms of Service first, then Privacy Policy.
- Complete the HTML feature/SDK checklist from the source document using only the current build.
- Send both drafts and the checklist “生成结果” to legal together.
- Do not mark either document `Live` until legal review is complete and the URL resolves.
- Re-check Data safety, the account deletion URL, and both legal documents together whenever an SDK or feature changes.
