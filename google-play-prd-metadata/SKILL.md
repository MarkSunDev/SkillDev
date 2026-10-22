---
name: google-play-prd-metadata
description: Add Google Play metadata, review notes with App access instructions, a five-image screenshot plan with the required feature graphic, App content declarations, and English Privacy Policy / Terms of Service drafts to app PRDs; use for Play listing copy, review credentials, data safety, content ratings, account deletion, legal/support links, privacy policies, terms, review notes, or gallery assets.
---

# Google Play PRD Metadata

Add four Google Play submission sections at the beginning of every Google Play PRD: an application information table, review notes with App access instructions, a five-image screenshot plan with a required feature graphic, and App content declarations. When the PRD also needs legal copy, add a fifth section with English Privacy Policy and Terms of Service drafts. Keep this material aligned with the exact build described by the PRD.

If the PRD already has a Google Play information, review-notes, declarations, or gallery section, update it in place. Do not add a duplicate section.

## 1. Application information

Place a heading such as `1. Google Play 基本信息` before the product, workflow, or technical sections. Use one two-column table with these rows, in this order:

| Field | Content |
|---|---|
| App Icon（当前：1 张 512×512 PNG；要求：512×512、32-bit PNG 带 Alpha、≤1 MB） | Icon status or asset reference |
| Feature Graphic（当前：1 张 1024×500；要求：1024×500、JPEG 或 24-bit PNG 无 Alpha、≤15 MB） | Feature graphic status or asset reference |
| App Name（当前 X 字符；限制 ≤30 字符） | Name |
| Short Description（当前 X 字符；限制 ≤80 字符） | Short description |
| Full Description（当前 X 字符；限制 ≤4,000 字符，纯文本，不支持 HTML） | Full description |
| Category（当前：X；限制：单一类目，无子类目） | One Play category |
| Tags（当前 X 个；限制 ≤5 个，从 Play Console 提供的标签中选择） | `tag1,tag2` or `[待确认]` |
| 内容分级（当前：X；限制：按 IARC 问卷，各地区分级不同） | Rating and region mapping |
| 目标受众（当前：X 岁及以上；限制：按 Target audience and content 声明） | Age groups / audience |
| 广告声明（当前：含广告 / 不含广告） | Ads declaration |
| 发行地区（当前：X 个地区；限制：按发行计划） | Regions or `全球` |
| Contact email（当前 X 字符；限制：有效邮箱，公开展示） | Public support/contact email |
| Website（当前 X 字符；限制：有效 HTTPS URL，可选） | Website |
| Privacy Policy URL（当前 X 字符；限制：有效 HTTPS URL，必填） | Privacy policy URL |
| Terms URL（当前 X 字符；限制：有效 HTTPS URL） | Terms URL |
| 账户删除 URL（当前 X 字符；限制：提供账户的 App 必须同时提供应用内删除入口和网页链接） | Web deletion URL or `不适用` |
| Promo video（当前 X 字符；限制：公开或未列出的 YouTube URL，可选） | YouTube URL or `不适用` |
| 运营主体（当前 X 字符；限制：与协议、隐私政策及开发者账号一致） | Legal entity |
| 邮箱（当前 X 字符；限制：有效邮箱） | Operations/legal contact email |
| 协议版本号（当前 X 字符；限制：与生效协议一致） | Agreement version |

Every text row must show both the current count and the limit in the field label. Count Unicode characters with spaces and punctuation included. Do not put the counts only in a separate column or footnote.

### Content rules

- `App Name` must be at most 30 characters. Use the product name only: no emoji or decorative symbols, no `download` / `install` / `free` / `best` / `top` call-to-action words, no ranking or award claims, no other company or app names, and no Google, Android, or Play trademarks.
- `Short Description` must be at most 80 characters, one sentence, and must not contain emoji, keyword stuffing, price claims, or promotions that are not true in the build.
- `Full Description` must be at most 4,000 characters, plain text, and must not contain HTML. The first two lines are visible before “Read more”, so put the core promise and primary use case there. Use blank lines between paragraphs; do not repeat keyword variants.
- `Category` is one Play category. Play has no secondary category; use `Tags` for discoverability. Select up to five tags from the list the Play Console exposes for that category and do not invent a taxonomy.
- `Contact email` is shown publicly and must be monitored. Do not publish a personal address that nobody answers.
- Draft the creative fields from the PRD when the product premise is clear. Use `[待确认]` for facts that cannot be derived, especially legal entity, contact emails, URLs, deletion URL, agreement version, and demo credentials.
- Never invent a live URL, legal entity, email address, demo account, rating, or tag. Put every unresolved item in a short `待补齐` list immediately after the table.

## 2. Google Play Review Notes and App access

Add `2. Google Play Review Notes` immediately after the information table. Write concise English, no more than 300 words (this skill's editorial cap; Play has no documented word limit), and keep it easy to scan. Include:

- A short thank-you to the reviewer.
- One sentence explaining the app's promise and the exact first-minute path to verify it.
- App access: the exact navigation path and working credentials for any login-gated content, plus which parts are open without an account. If nothing is restricted, say so explicitly.
- Any region restriction and how a reviewer outside that region should test.
- Non-obvious test steps: permissions, seeded content, test purchases, invite or approval flows.
- Optional, when available: an unlisted YouTube screen recording.
- Optional, when relevant: sensitive permissions and their in-app rationale, age gate, monetization, and UGC controls.

Only list features, tabs, purchases, or AI behavior that work in the submitted build. Do not describe reviewer-only behavior, seeded users as real users, or future functionality.

Google Play review is driven by structured declarations, not a free-form notes field. Copy these instructions into Play Console → App content → App access, and repeat any remaining context in the release review notes field when the Console offers one. Use the template in `references/metadata-template.md` when a ready-to-copy structure helps.

## 3. Google Play five-image set and feature graphic

Add `3. Google Play 五图与 Feature Graphic` after the review Notes whenever the PRD includes submission assets or screenshot planning. Record five individual portrait screenshots plus one overview sheet, and one separate feature graphic, for the PRD. Five is this skill's editorial convention: Google Play accepts 2–8 screenshots per device type. The feature graphic is required and is not a sixth screenshot. Use `references/screenshot-style.md` for the full style system and `references/metadata-template.md` for the planning table.

The set uses one shared editorial wrapper, not five unrelated posters:

1. Brand lockup at top left: app icon or logo mark plus app name.
2. Small uppercase eyebrow naming the feature or context.
3. A two-line display headline: first line roman, second line italic in the accent color.
4. A two-line supporting sentence with concrete product copy.
5. A short accent rule, slide number, and a large device mockup containing a real app screenshot.
6. A small footer line that closes the story.

Keep the layout grid, margins, type scale, and device treatment identical across all five images. Vary the background color and screenshot, not the structure. The reference implementation uses `Instrument Serif` for headlines, a restrained editorial palette, and 1440 × 2560 RGB masters in upload order.

### Screenshot sizes

Never treat one pixel size as permanent. Check the Play Console screenshot specifications at submission time and export the layout at the sizes that are currently required. As of October 2026:

- Phone screenshots: 2–8 per device type, each side between 320 and 3840 px, aspect ratio no wider than 2:1.
- Use **1440 × 2560** (9:16) as the master canvas and export **1080 × 1920** for lighter files. Both are accepted.
- A raw 20:9 or 19.5:9 phone capture (for example 1080 × 2400) exceeds the 2:1 limit. Do not upload raw captures; compose them on a 9:16 canvas with the screenshot fitted inside a device frame.
- 7-inch and 10-inch tablet tiers accept up to 8 screenshots each. Supply them when the app supports tablets and the Console lists them for your app; do not reuse phone compositions without checking the tablet layout.
- Chromebook and Android XR listings have their own counts, ratios, and minimum resolutions. Check the device catalog in Play Console.
- Screenshots must be JPEG or 24-bit PNG with no alpha channel or transparency.
- Feature graphic: **1024 × 500**, JPEG or 24-bit PNG with no alpha channel, at most 15 MB.

### Selection rules

- Use real screenshots from the exact submitted build. Do not redraw UI, AI-generate the app screen, or substitute a concept screen for a shipped screen.
- Make image 01 the core promise plus the primary screen. Use images 02–05 for four distinct product pillars; do not repeat the same screen or feature.
- For a chat-first product, the first image is the Chats screen and the remaining images cover discovery, content, AI/utility, and account/personalization. For other products, replace those pillars with the actual primary tabs and differentiators.
- Headline copy states a benefit; supporting copy makes it concrete; the footer is a brand line. Keep each text block to two lines and readable at Play thumbnail size.
- The overview sheet is for the PRD and review only. Do not upload the overview sheet as one of the screenshots.
- Record each image in the PRD with its order, story beat, source screen, eyebrow, headline, supporting copy, footer, background color, and status.
- If real screenshots exist, produce the five composed images. If they do not, write the complete plan and mark each source `[待截图]`; never substitute a concept screen or an AI-generated UI.
- Render the wrapper deterministically with HTML/CSS or an image compositor so all five images share the exact same grid. Keep the real screenshot as a separate raster layer inside the device frame.

### Feature graphic rules

- Use one message and the brand lockup. It appears in placements where screenshots are not shown, so it must stand alone.
- Keep critical text and the logo inside the central safe area; some placements crop the edges.
- Keep text large and short: one headline plus at most one supporting line. Do not shrink paragraphs to fit 1024 × 500.
- Do not put star ratings, awards, “Editor's Choice”, rankings, prices, or download call-to-actions on the graphic.
- Do not build a screenshot collage or stretch a single screenshot. Use the app palette and one clear product promise.
- Export RGB at exactly 1024 × 500; no alpha channel and no transparency.

## 4. App content declarations

Add `4. App content 声明` after the screenshot section. Google Play publishes only after these declarations are complete and consistent with the build. Record each one in the PRD:

| Declaration | When required | What the PRD must record |
|---|---|---|
| Data safety | Always | Data types collected and shared, purposes, encryption in transit, deletion request method, account deletion URL |
| Content rating (IARC) | Always | Questionnaire answers summary and the resulting ratings by region |
| Target audience and content | Always | Age groups; whether the app is designed for children; Families policy status |
| Ads | Always | `Contains ads` or `No ads`; ad SDK categories when ads exist |
| App access | When any content requires login or approval | Working credentials and exact reviewer instructions |
| Account deletion | When users can create accounts | In-app deletion path plus a publicly reachable web URL |
| News app | When applicable | Yes/no and justification |
| Government app | When applicable | Yes/no and justification |
| Financial features | When applicable | Yes/no and the feature set |
| Health apps | When applicable | Yes/no and the health data or functionality |
| Sensitive permissions | When the manifest requests them | Declaration status and in-app rationale for SMS/Call Log, background location, all-files access, package visibility, and similar restricted permissions |

Declaration rules:

- Declare the submitted build, not the roadmap. Remove features from the declaration when they are not live.
- Data safety must match the SDK inventory, the runtime behavior, and the Privacy Policy. When the build adds or removes an SDK, update Data safety and the legal drafts before release.
- Content rating answers must account for UGC, AI-generated content, ads, purchases, and any mature themes the build actually contains.
- Do not select an audience that includes children unless the build, ads, and data practices comply with the Families policy. If the app is for 18+, say so consistently in the listing, declarations, and legal copy.
- Account deletion must work both in-app and through the public web link. The same link is used in Data safety and the Privacy Policy.
- Every restricted permission needs a declaration and a visible in-app rationale. Do not request a restricted permission that the current feature set does not use.

## 5. Privacy Policy and Terms of Service

Add `5. Privacy Policy & Terms` when the PRD needs legal copy, or when the user asks for a Privacy Policy / Terms of Service draft. Use `references/privacy-terms.md` for the full workflow, required clauses, and reusable prompt.

Use the current build only. Collect the app name, platforms, distribution regions, one contact email for all privacy/support/deletion/rights requests, monetization, actual age gate, feature inventory, Data safety answers, and the account deletion mechanism. Mark only features present in the current build and never pre-select future features.

Generate two complete English drafts in this order:

1. Terms of Service — acceptance/eligibility, accounts, purchases/subscriptions/IAP with Google Play billing and refund rules, user content/UGC, AI features, IP/license, warranty disclaimer, limitation of liability, indemnification, Delaware governing law, AAA consumer arbitration with class-action waiver and standard exceptions, changes, contact.
2. Privacy Policy — who/contact, categories of information collected, uses, sharing, cookies/advertising identifiers such as GAID, retention, US/California rights, children's privacy, international transfers, security, updates, contact, and the account deletion route.

Drafting rules:

- Do not insert company legal name, address, website, or `[COMPANY LEGAL NAME]`-style placeholders. Refer to the app by its store name or “we / us / our”.
- Use one contact email for every external legal/privacy/support/deletion/rights channel.
- Use “may” and category-level descriptions. Do not make absolute negative commitments such as “we do not collect”, “we do not sell”, “we never share”, or a fixed retention period.
- Do not name SDKs, data recipients, transfer destinations, or retention periods in the first draft; leave them for the completed feature/SDK checklist and legal review.
- Default the source prompt to 18+ with age verification. State an age gate only if the submitted build actually enforces it.
- Describe purchases as processed by Google Play where that is how the build bills, with cancellation and refunds governed by Google Play policy. Do not describe a billing path the build does not use.
- Describe account deletion as available both in-app and through the published web URL when the build provides both.
- Output plain English Markdown with numbered sections. Return Terms first, then Privacy Policy.
- Send the draft and the HTML checklist “生成结果” to legal before publishing. Record the document version and live URLs in the PRD table.

## 6. PRD alignment

Before finishing, check that the table, Notes, declarations, and gallery agree with the rest of the PRD:

- The listing copy, screenshots, feature graphic, App content declarations, legal/support surfaces, and review instructions describe the same build.
- The review path demonstrates the signature action and its visible consequence within the first minute.
- The five images use real screens from the same build, follow one shared layout system, and match the PRD's gallery plan.
- The icon is 512 × 512, 32-bit PNG with alpha, at most 1 MB; it is not a flattened downscale of an App Store icon.
- The feature graphic is exactly 1024 × 500, RGB with no alpha, and is not one of the screenshots.
- Phone screenshots are 2–8 images, JPEG or 24-bit PNG, within 320–3840 px per side, and no wider than 2:1.
- Tablet, Chromebook, and XR assets exist for every device tier the Console lists for the app.
- The Android App Bundle meets the current target API level requirement, and the submitted track contains the build shown in the screenshots.
- App access instructions and demo credentials work through the normal sign-in path.
- Data safety matches the SDK inventory, runtime behavior, Privacy Policy, and account deletion URL.
- Content rating answers match the actual UGC, AI, ads, and purchase behavior.
- Account deletion works in-app and at the published web URL.
- Demo credentials, support links, privacy policy, terms, and purchase paths work in the submitted build.
- Privacy Policy and Terms describe the same data flows, SDKs, monetization, age gate, and features as the submitted build.
- The agreement version, contact email, Privacy Policy URL, Terms URL, and account deletion URL are consistent across the PRD and both legal documents.
- No legal draft claims a mechanism, age gate, retention period, or data practice that the build does not implement.
- For UGC, report/block/account deletion/support paths are real where the PRD claims them.
- For AI features, describe the AI role and processing boundary only as implemented.
- Localized listings use the same build and the same claims; do not localize screenshots and descriptions independently.
- If this is a new personal developer account, account for the closed-testing requirement before production access; check the current tester count and duration in Play Console.

See `references/prd-integration.md` for the distilled Google Play PRD standards.

## 7. Validate before returning

Run the validator when numeric limits matter:

```bash
python3 scripts/check_metadata.py metadata.json
python3 scripts/check_metadata.py metadata.json --pretty
```

The JSON may contain any of: `app_name`, `short_description`, `full_description`, `review_notes`, `contact_email`, `website`, `privacy_policy_url`, `terms_url`, `account_deletion_url`, `promo_video_url`, and `has_accounts` (boolean). The script reports character counts, word counts, URL/email validity, emoji and metadata-policy warnings, and whether a required account deletion URL is missing. Fix every reported error before returning the PRD.

When a gallery manifest exists, validate the screenshot plan and the store assets:

```bash
python3 scripts/check_gallery.py gallery.json --pretty
python3 scripts/check_gallery.py gallery.json --pretty --check-files --assets-dir ./assets --size 1440x2560
```

The manifest is either an array of 2–8 image objects or an object with an `images` array. Each object uses `slug`, `feature`, `title` (two strings), `body` (two strings), `src`, `bg`, `ink`, `accent`, `footer`, and optionally `artwork` and `size` (`"1440x2560"`). The object form may also carry `icon` (`{"src": "icon-512.png"}`) and `feature_graphic` (`{"src": "feature-graphic-1024x500.png"}`). The script checks count, order, uniqueness, required fields, two-line copy, and hex colors, and warns when the set is not the five-image convention.

Add `--check-files` to verify the raster files: existence, PNG/JPEG format, alpha-channel rules, Play's 320–3840 px range and 2:1 ratio, the 512 × 512 32-bit alpha icon, and the 1024 × 500 feature graphic. Resolve relative `src` paths with `--assets-dir`; a per-image `size` or `--size` asserts exact dimensions. File checking requires Pillow (`python3 -m pip install Pillow`).

For legal drafts, run the manual QA checklist in `references/privacy-terms.md` before handing the draft to legal.
