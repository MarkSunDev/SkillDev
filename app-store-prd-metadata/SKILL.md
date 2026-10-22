---
name: app-store-prd-metadata
description: Add App Store metadata, reviewer Notes, five-image sets, and English Privacy Policy / Terms of Service drafts to app PRDs; use for listing copy, review credentials, legal/support links, privacy policies, terms, review notes, or gallery assets.
---

# App Store PRD Metadata

Add three submission sections at the beginning of every App Store PRD: an application information table, English App Review Notes, and an App Store five-image plan. When the PRD also needs legal copy, add a fourth section with English Privacy Policy and Terms of Service drafts. Keep this material aligned with the exact build described by the PRD.

If the PRD already has an App Store information, review-notes, or gallery section, update it in place. Do not add a duplicate section.

## 1. Application information

Place a heading such as `1. App Store 基本信息` before the product, workflow, or technical sections. Use one two-column table with these rows, in this order:

| Field | Content |
|---|---|
| App Icon（当前：1 张 1024×1024 PNG；要求：1024×1024、无透明通道） | Icon status or asset reference |
| App Name（当前 X 字符；限制 ≤30 字符） | Name |
| Subtitle（当前 X 字符；限制 ≤30 字符） | Subtitle |
| Promotional Text（当前 X 字符；限制 ≤170 字符，无需发版即可修改） | Promotional text |
| Keywords（当前 X 字节；限制 ≤100 字节，逗号分隔不加空格） | `keyword1,keyword2,keyword3` |
| Category（当前：主类目 / 子类目建议；限制：主类目必填，子类目按 App Store Connect 可选） | Primary category and a concrete secondary-category suggestion |
| 年龄分级（当前：X+；限制：按内容问卷与发行地区） | Age rating |
| 发行地区（当前：X 个地区；限制：按发行计划） | Regions or `全球` |
| Contact email（当前 X 字符；限制：有效邮箱） | App Store review/contact email |
| Support URL（当前 X 字符；限制：有效 HTTPS URL） | Support URL |
| Marketing URL（当前 X 字符；限制：有效 HTTPS URL） | Marketing URL |
| Privacy Policy URL（当前 X 字符；限制：有效 HTTPS URL） | Privacy policy URL |
| Terms URL（当前 X 字符；限制：有效 HTTPS URL） | Terms URL |
| 运营主体（当前 X 字符；限制：与协议、隐私政策及开发者账号一致） | Legal entity |
| 邮箱（当前 X 字符；限制：有效邮箱） | Operations/legal contact email |
| 协议版本号（当前 X 字符；限制：与生效协议一致） | Agreement version |
| Description（当前 X 字符；限制 ≤4,000 字符，纯文本，不支持 HTML） | Description |

Every text row must show both the current count and the limit in the field label. Count Unicode characters with spaces and punctuation included; count keywords as UTF-8 bytes. Do not put the counts only in a separate column or footnote.

### Content rules

- `App Name` must be at most 30 characters.
- `Subtitle` must be at most 30 characters.
- `Promotional Text` must be at most 170 characters and may be changed without shipping a new build.
- `Keywords` must be at most 100 UTF-8 bytes, comma-separated with no spaces after commas, must not repeat the App Name, and must not contain other app or company names.
- `Description` must be at most 4,000 characters, plain text, and must not contain HTML.
- When rendering a long Description in Feishu Docs, put every paragraph in its own `<p>` inside the blockquote. Do not rely on `<br/><br/>` between a heading line and its body; Feishu can collapse them into one line.
- Write `Category` as the current primary App Store Connect category plus a concrete secondary-category or subcategory suggestion. Do not invent a taxonomy that App Store Connect does not expose.
- Draft the creative fields from the PRD when the product premise is clear. Use `[待确认]` for facts that cannot be derived, especially legal entity, contact emails, URLs, agreement version, and demo credentials.
- Never invent a live URL, legal entity, email address, or demo account. Put every unresolved item in a short `待补齐` list immediately after the table.

## 2. App Review Notes

Add `2. App Review Notes` immediately after the information table. Write concise English, no more than 300 words, and keep it easy to scan. Include:

- A short thank-you to the reviewer.
- One sentence explaining the app's promise and the exact first-minute path to verify it.
- A screen-recording link. If it is not available yet, write `[待提供]` rather than inventing one.
- A working demo account with email and password. Use the normal sign-in path used by real users.
- Optional, when relevant: the main tabs/features to test, security and privacy behavior, monetization, and age rating.

Only list features, tabs, purchases, or AI behavior that work in the submitted build. Do not describe reviewer-only behavior, seeded users as real users, or future functionality. Use the template in `references/metadata-template.md` when a ready-to-copy structure helps.

## 3. Five-image App Store set

Add `3. App Store 五图` after the review Notes whenever the PRD includes submission assets or screenshot planning. Record five individual portrait images plus one overview sheet for the PRD. Five is this skill's editorial convention: App Store Connect accepts 3–10 screenshots per device size. Use `references/five-image-style.md` for the full style system and `references/metadata-template.md` for the planning table.

The set uses one shared editorial wrapper, not five unrelated posters:

1. Brand lockup at top left: app icon or logo mark plus app name.
2. Small uppercase eyebrow naming the feature or context.
3. A two-line display headline: first line roman, second line italic in the accent color.
4. A two-line supporting sentence with concrete product copy.
5. A short accent rule, slide number, and a large device mockup containing a real app screenshot.
6. A small footer line that closes the story.

Keep the layout grid, margins, type scale, and device treatment identical across all five images. Vary the background color and screenshot, not the structure. The reference implementation uses `Instrument Serif` for headlines, a restrained editorial palette, and 1320 × 2868 RGB PNG masters (no alpha channel or transparency) in upload order.

### Screenshot sizes

Never treat one pixel size as permanent. Check the App Store Connect screenshot specifications at submission time and export the same layout at the sizes that are currently required. As of October 2026:

- Required iPhone tier: “iPhone with Dynamic Island (medium display)” — at least one screenshot at 1179 × 2556 or 1206 × 2622.
- “iPhone with Dynamic Island (large display)” is accepted at 1260 × 2736 (iPhone Air), 1290 × 2796 (iPhone 14/15 Pro Max, iPhone 16 Plus), or 1320 × 2868 (iPhone 16 Pro Max and later). Use 1320 × 2868 as the master canvas.
- iPad 13-inch is required when the app supports iPad: 2064 × 2752 or 2048 × 2732.
- Portrait or landscape is accepted; this set is portrait. Images must be PNG or JPEG with no alpha channel or transparency.
- Export the five images at 1320 × 2868 and again at 1206 × 2622 so the required medium tier is covered. Do not redesign per size.

### Selection rules

- Use real screenshots from the exact submitted build. Do not redraw UI, AI-generate the app screen, or substitute a concept screen for a shipped screen.
- Make image 01 the core promise plus the primary screen. Use images 02–05 for four distinct product pillars; do not repeat the same screen or feature.
- For a chat-first product, the first image is the Chats screen and the remaining images cover discovery, content, AI/utility, and account/personalization. For other products, replace those pillars with the actual primary tabs and differentiators.
- Headline copy states a benefit; supporting copy makes it concrete; the footer is a brand line. Keep each text block to two lines and readable at App Store thumbnail size.
- The overview sheet is for the PRD and review only. Do not upload the overview sheet as one of the five App Store screenshots.
- Record each image in the PRD with its order, story beat, source screen, eyebrow, headline, supporting copy, footer, background color, and status.
- If real screenshots exist, produce the five composed images. If they do not, write the complete plan and mark each source `[待截图]`; never substitute a concept screen or an AI-generated UI.
- Render the wrapper deterministically with HTML/CSS or an image compositor so all five images share the exact same grid. Keep the real screenshot as a separate raster layer inside the device frame.

## 4. Privacy Policy and Terms of Service

Add `4. Privacy Policy & Terms` when the PRD needs legal copy, or when the user asks for a Privacy Policy / Terms of Service draft. Use `references/privacy-terms.md` for the full workflow, required clauses, and reusable prompt.

Use the current build only. Collect the app name, platforms, distribution regions, one contact email for all privacy/support/deletion/rights requests, monetization, actual age gate, and the feature inventory. Use the HTML feature checklist linked in the source document; mark only features present in the current build and never pre-select future features.

Generate two complete English drafts in this order:

1. Terms of Service — acceptance/eligibility, accounts, purchases/subscriptions/IAP, user content/UGC, AI features, IP/license, warranty disclaimer, limitation of liability, indemnification, Delaware governing law, AAA consumer arbitration with class-action waiver and standard exceptions, changes, contact.
2. Privacy Policy — who/contact, categories of information collected, uses, sharing, cookies/advertising identifiers, retention, US/California rights, children's privacy, international transfers, security, updates, contact.

Drafting rules:

- Do not insert company legal name, address, website, or `[COMPANY LEGAL NAME]`-style placeholders. Refer to the app by its store name or “we / us / our”.
- Use one contact email for every external legal/privacy/support/deletion/rights channel.
- Use “may” and category-level descriptions. Do not make absolute negative commitments such as “we do not collect”, “we do not sell”, “we never share”, or a fixed retention period.
- Do not name SDKs, data recipients, transfer destinations, or retention periods in the first draft; leave them for the completed feature/SDK checklist and legal review.
- Default the source prompt to 18+ with age verification. State an age gate only if the submitted build actually enforces it.
- Output plain English Markdown with numbered sections. Return Terms first, then Privacy Policy.
- Send the draft and the HTML checklist “生成结果” to legal before publishing. Record the document version and live URLs in the PRD table.

## 5. PRD alignment

Before finishing, check that the table and Notes agree with the rest of the PRD:

- The listing copy, screenshots, legal/support surfaces, and review Notes describe the same build.
- The review path demonstrates the signature action and its visible consequence within the first minute.
- The five images use real screens from the same build, follow one shared layout system, and match the PRD's gallery plan.
- Screenshot files match the currently required App Store Connect tiers, including the iPhone medium display, and are flattened RGB with no alpha channel.
- Demo credentials, support links, privacy policy, terms, and purchase paths work in the submitted build.
- Privacy Policy and Terms describe the same data flows, SDKs, monetization, age gate, and features as the submitted build.
- The agreement version, contact email, Privacy Policy URL, and Terms URL are consistent across the PRD and both legal documents.
- No legal draft claims a mechanism, age gate, retention period, or data practice that the build does not implement.
- For UGC, report/block/account deletion/support paths are real where the PRD claims them.
- For AI features, describe the AI role and processing boundary only as implemented.

See `references/prd-integration.md` for the distilled App Store PRD standards from the referenced Feishu documents.

## 6. Validate before returning

Run the validator when numeric limits matter:

```bash
python3 scripts/check_metadata.py metadata.json
```

The JSON may contain any of: `app_name`, `subtitle`, `promotional_text`, `keywords`, `description`, `review_notes`, `support_url`, `marketing_url`, `privacy_policy_url`, `terms_url`, `contact_email`. The script reports character counts, keyword byte counts, word counts, and concrete violations. Fix every reported error before returning the PRD.

When a gallery manifest exists, validate the five-image plan too:

```bash
python3 scripts/check_gallery.py gallery.json --pretty
python3 scripts/check_gallery.py gallery.json --pretty --check-files --assets-dir ./screenshots --size 1320x2868
```

The manifest is either an array of five image objects or an object with an `images` array. Each object uses `slug`, `feature`, `title` (two strings), `body` (two strings), `src`, `bg`, `ink`, `accent`, `footer`, and optionally `artwork` and `size` (`"1320x2868"`). The script checks count, order, uniqueness, required fields, two-line copy, and hex colors.

Add `--check-files` to verify the actual raster files: existence, PNG/JPEG format, no alpha channel or transparency, and exact dimensions. Resolve relative `src` paths with `--assets-dir`; a per-image `size` overrides the global `--size`. File checking requires Pillow (`python3 -m pip install Pillow`).

For legal drafts, run the manual QA checklist in `references/privacy-terms.md` before handing the draft to legal.
