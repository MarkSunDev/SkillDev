# App Store PRD metadata template

Use this structure when the PRD does not already define a presentation. Replace every placeholder with real content or `[待确认]`.

## 1. App Store 基本信息

| Field | Content |
|---|---|
| App Icon（当前：1 张 1024×1024 PNG；要求：1024×1024、无透明通道） | `[待确认]` |
| App Name（当前 X 字符；限制 ≤30 字符） | `[App Name]` |
| Subtitle（当前 X 字符；限制 ≤30 字符） | `[Subtitle]` |
| Promotional Text（当前 X 字符；限制 ≤170 字符，无需发版即可修改） | `[Promotional Text]` |
| Keywords（当前 X 字节；限制 ≤100 字节，逗号分隔不加空格） | `keyword1,keyword2,keyword3` |
| Category（当前：主类目 / 子类目建议；限制：主类目必填，子类目按 App Store Connect 可选） | `[Primary category] / [Secondary category suggestion]` |
| 年龄分级（当前：X+；限制：按内容问卷与发行地区） | `[Age rating]` |
| 发行地区（当前：X 个地区；限制：按发行计划） | `[Regions]` |
| Contact email（当前 X 字符；限制：有效邮箱） | `[Email]` |
| Support URL（当前 X 字符；限制：有效 HTTPS URL） | `[URL]` |
| Marketing URL（当前 X 字符；限制：有效 HTTPS URL） | `[URL]` |
| Privacy Policy URL（当前 X 字符；限制：有效 HTTPS URL） | `[URL]` |
| Terms URL（当前 X 字符；限制：有效 HTTPS URL） | `[URL]` |
| 运营主体（当前 X 字符；限制：与协议、隐私政策及开发者账号一致） | `[Legal entity]` |
| 邮箱（当前 X 字符；限制：有效邮箱） | `[Email]` |
| 协议版本号（当前 X 字符；限制：与生效协议一致） | `[Version]` |
| Description（当前 X 字符；限制 ≤4,000 字符，纯文本，不支持 HTML） | `[Description]` |

待补齐：

- `[待确认]` field names and required source

## 2. App Review Notes

> Keep this section in English and under 300 words.

Hi App Review Team,

Thank you for reviewing [App Name]. [One sentence describing the app's promise.] To verify it, [the exact first-minute action and expected visible result].

Demo account:

- Email: `[demo email]`
- Password: `[demo password]`

Screen recording: `[URL or 待提供]`

Main areas to test:

- `[Working tab or feature 1]`
- `[Working tab or feature 2]`

Security and privacy: `[Only describe implemented mechanisms, or omit]`

Monetization: `[Only describe implemented purchases/subscriptions, or omit]`

Age rating: `[Rating and brief reason, or omit]`

Thank you,

[Developer or company name]

## 3. App Store 五图

Use five individual portrait images in upload order, plus one overview sheet for the PRD. Keep the same layout grid across all five images. Render at 1320 × 2868 and again at 1206 × 2622 for the required medium-display tier; export flattened RGB PNG/JPEG with no alpha channel. Five is the editorial convention; App Store Connect accepts 3–10 screenshots per device size.

| # | Story beat | Screen / source | Eyebrow | Headline (2 lines) | Supporting copy (2 lines) | Footer | Background | Status |
|---|---|---|---|---|---|---|---|---|
| 01 | Core promise + primary screen | `[screenshot filename]` | `[FEATURE CONTEXT]` | First line / *Second line.* | First line / second line. | `[closing line]` | `[#HEX]` | `[待确认]` |
| 02 | Second product pillar | `[screenshot filename]` | `[FEATURE CONTEXT]` | First line / *Second line.* | First line / second line. | `[closing line]` | `[#HEX]` | `[待确认]` |
| 03 | Third product pillar | `[screenshot filename]` | `[FEATURE CONTEXT]` | First line / *Second line.* | First line / second line. | `[closing line]` | `[#HEX]` | `[待确认]` |
| 04 | Signature differentiator | `[screenshot filename]` | `[FEATURE CONTEXT]` | First line / *Second line.* | First line / second line. | `[closing line]` | `[#HEX]` | `[待确认]` |
| 05 | Personalization / account / trust | `[screenshot filename]` | `[FEATURE CONTEXT]` | First line / *Second line.* | First line / second line. | `[closing line]` | `[#HEX]` | `[待确认]` |

Overview sheet (PRD/review only, not an App Store upload):

- Title: `[App] / [Version] / App Store five-image set`
- Five thumbnails in upload order with labels beneath each image.
- Keep the same palette, typography, and device treatment as the individual assets.

## 4. Privacy Policy & Terms

Use `references/privacy-terms.md` to generate the English drafts. Keep the version and URLs in sync with the application information table.

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
