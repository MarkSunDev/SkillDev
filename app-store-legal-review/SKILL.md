---
name: app-store-legal-review
description: >-
  Draft and QA the four US-market store legal pages — Terms of Service, Privacy
  Policy, Child Safety Policy, Account Deletion — from verified current-build
  facts. Includes a preflight that asks the user for missing facts (developer
  legal name, general and CSAM emails, permissions, deletion method/Google Form
  URL, governing law and arbitration), a Tinder/Bumble/Hily benchmark, and
  mechanical checks. Use for "上架协议审核", "四页协议", "隐私政策", "用户协议",
  "儿童声明", "删除账户页面", "Google Form 删号", "Terms of Service draft",
  "Privacy Policy draft", or "what to send legal before an App Store / Google
  Play release".
---

# App Store Legal Review

Turn verified facts about the submitted build into a store-ready legal package:

1. **Terms of Service**
2. **Privacy Policy**
3. **Child Safety Policy**
4. **Account Deletion** page with a public web request path
5. The completed `App 功能与数据清单`
6. A short brief and mechanical QA report

The pages must describe the same build as the store listing and the Data safety
declaration. Output is a draft for qualified counsel, not legal advice.

## Hard boundaries

- **Current build only.** Describe only features, data flows, permissions, and
  SDKs that exist in the build being submitted. Never include planned IAP, ad
  SDKs, AI, background checks, ID verification, or age-verification technology
  that is not actually shipped.
- **Never invent identity or contacts.** The developer legal name and a
  dedicated child-safety mailbox are required inputs for the four-page set. Ask
  for them; never leave `[COMPANY LEGAL NAME]`, `[CSAM EMAIL]`, or similar
  placeholders.
- **One general contact, plus role addresses.** Terms, Privacy, and Account
  Deletion use the general contact (or a privacy@ address when supplied). The
  Child Safety page must use a **separate, monitored CSAM mailbox**, not the
  general feedback address. Do not create an address that has not been created.
- **No hard promises.** Do not write "we do not collect/sell/share/use", "we
  never share", or a fixed retention period unless it is factually true and
  approved. Use `may` and category-level wording. A cancellation/restore window
  is a product fact and may be stated when confirmed.
- **No SDK or recipient names in the first draft.** Keep providers,
  cross-border destinations, and retention periods at category level for legal
  to fill in from the checklist. The checklist itself names the SDKs.
- **Age gate must match reality.** Do not claim 18+ verification or an age gate
  the build does not enforce. If the gate differs, adapt the eligibility and
  children's-privacy clauses.
- **Do not copy another app's text verbatim.** Use Tinder/Bumble/Hily for
  structure and plain-language patterns only. Their entity names, addresses,
  emails, retention periods, providers, arbitration terms, and safety claims are
  not your facts.
- **Google Forms are a request channel, not a Play requirement.** Play accepts a
  form or a customer-service email. When a Google Form is used, integrate it as
  a **branded form POST to the form's `formResponse` endpoint**; do not embed the
  Google Form in an iframe and do not redirect users to a separate Google Form
  page. Responses go to the form owner's Google account, not to Google Play, and
  do not delete the account automatically.
- **Legal review is a gate.** Never mark an agreement live, publish a URL, or
  ship the build on the strength of this skill alone.

## Step 0 — Preflight: ask for missing facts

Run this before drafting anything:

```bash
python3 scripts/preflight.py --config app-legal.json --scope four-pages
```

If it exits non-zero, send the user the generated `请补齐以下信息` list in one
consolidated message and stop. Do not draft page by page, and do not guess a
legal fact. The required fields and a ready-to-send prompt are in
`references/preflight.md`; the machine-readable example is
`assets/app-legal.example.json`.

Required for all four pages:

- app name and exact store name;
- developer/operator legal name;
- platforms and distribution region;
- general contact email;
- dedicated child-safety (CSAM) email;
- monetization and current-build features;
- actual runtime permissions from the merged manifest (`[]` is valid);
- account model (device/email/phone/username);
- SDK/service-provider categories;
- age gate and actual verification;
- governing law, arbitration provider/venue/opt-out (or "none");
- account deletion path, public web URL, request method, Google Form
  `formResponse` endpoint and all four `entry.*` IDs when using a form,
  cancellation window, retention summary, and subscription-cancellation note.

For the older two-page flow, run `--scope tos-privacy`; it requires only the
original Terms/Privacy facts.

## Step 1 — Collect and verify the facts

Read from the project, not from memory:

- `AndroidManifest.xml` and the **merged** release/debug manifest for
  permissions;
- Gradle dependencies and SDK manifests for third-party processors;
- app config for the legal URLs and contact addresses;
- the current store listing and Data safety answers;
- the account-deletion implementation (in-app path, cancellation window,
  whether an email/form path exists).

If a fact is unknown, stop and ask. Do not fill it with a plausible default.

## Step 2 — Prepare the Terms + Privacy brief

```bash
python3 scripts/prepare_brief.py \
  --config app-legal.json \
  --checklist checklist-result.txt \
  --out legal-brief.md
```

`prepare_brief.py` fills `references/drafting-prompt.txt` and cross-checks the
HTML checklist. It is the two-page (Terms + Privacy) tool; the four-page outlines
are in `references/four-page-set.md`.

The prompt is tuned for a US-market, 18+ app. For a different age model, edit
the age clauses and pass the edited template with `--template` plus
`--allow-age-gate-mismatch`.

## Step 3 — Draft the four pages

### Terms of Service

Use the outline in `references/four-page-set.md`. The minimum expected sections
are acceptance/eligibility, accounts, license and restrictions, user content,
prohibited conduct, reporting/blocking/moderation, purchases/subscriptions,
account termination and deletion, safety/interactions, IP and copyright/DMCA,
third-party content and app stores, disclaimers, limitation of liability,
indemnification, governing law, dispute resolution, changes, termination and
survival, electronic communications, miscellaneous, and contact.

Make governing law and arbitration match the facts: Tinder uses Delaware/NAM,
Bumble uses Texas, Hily uses California/NAM. Do not hard-code
Delaware/AAA/Wilmington.

### Privacy Policy

Use the outline in `references/four-page-set.md`. Cover the controller/operator
identity, data categories, sources, purposes, sharing/processors, sale/share/
targeted-advertising choices, cookies/SDKs, retention categories, user rights
(including CCPA/CPRA and other applicable state rights), account deletion,
children, international transfers, security, third-party links, changes, and
contact.

If the build has no camera, microphone, contacts, or precise-location
permission, do not claim it does. Describe only the photo the user selects
through the system picker. Distinguish approximate region derived from a postal
code from device location.

### Child Safety Policy

Required content:

- developer legal name and the app name exactly as shown on the store;
- 18+ only and the actual age gate;
- zero tolerance for CSAM, grooming, sexual exploitation of minors, and
  content that sexualizes or endangers a minor;
- in-app Report action and a **dedicated CSAM email** (not the general inbox);
- Block and moderation tools;
- removal, account termination, and appeals;
- cooperation with law enforcement and NCMEC or the relevant authority;
- policy updates and contact.

Use Tinder/Bumble/Hily as structural references. Hily's terms, for example,
combine a zero-tolerance statement with NCMEC reporting and in-app reporting;
do not copy their text. Do not claim background checks or ID verification unless
the build performs them.

### Account Deletion page

The page must work for users who cannot access the app:

- exact in-app path first;
- public web URL, no install and no sign-in;
- request method: Google Form, hosted form, or email;
- what is deleted and what may be retained;
- cancellation/restore window and when deletion starts;
- subscription cancellation as a separate step;
- logout, uninstall, and pause/hide are not deletion;
- confirmation/reference number and contact.

For a Google Form, use the branded POST flow in
`references/google-form-deletion.md`: keep our own fields, POST to the form's
`formResponse` endpoint, and show our own confirmation with a reference number.
The public page URL goes into Play Console → App content → Data safety → Data
deletion. The same URL belongs in the app config's `accountDeletionUrl`.

## Step 4 — Fill the checklist

Open `assets/app-function-checklist.html` in a browser and select only what the
current build actually does. The tool produces the `【App 信息清单】` text.
Paste it unchanged into `checklist-result.txt`; do not retype or "clean up" the
result. Replace `其他（待补充）` with the real SDK/provider before handoff.

## Step 5 — QA

Run both checks:

```bash
python3 scripts/check_draft.py \
  --draft legal-draft.md \
  --config app-legal.json \
  --checklist checklist-result.txt \
  --out qa-report.md

python3 scripts/check_four_pages.py \
  --terms terms-of-service.md \
  --privacy privacy-policy.md \
  --child-safety child-safety-policy.md \
  --deletion account-deletion.md \
  --config app-legal.json \
  --out qa-four-pages.md
```

`check_draft.py` checks the Terms/Privacy topics, forbidden absolute wording,
placeholders, configured emails, feature coverage, and SDK-name leakage.
`check_four_pages.py` adds child-safety and deletion checks (developer legal
name, CSAM mailbox, zero tolerance, reporting/blocking, authorities, in-app
path, uninstall/logout distinction, retention, cancellation window, app-store
and DMCA sections). Both are heuristics; fix every error and read every warning.

Manual checks:

- every checklist `是` feature has a matching clause; every `否` feature is
  absent or explicitly excluded;
- data categories match the privacy policy and the Data safety form;
- SDK groups match the category-level sharing wording;
- the child safety page uses the dedicated CSAM mailbox, not the general one;
- the deletion page's in-app path and web URL match the build and Play Console;
- the age gate and children's sections match the build;
- no page promises a feature or a retention period the team cannot meet.

## Step 6 — Hand off and deploy

Send legal:

1. the four drafts;
2. the checklist result exactly as generated;
3. the one-page facts brief;
4. the QA reports.

After legal review:

- deploy the pages under the app domain and verify each URL returns 200 without
  login or an app install;
- enter the public deletion URL in Play Console → App content → Data safety →
  Data deletion;
- put the same URL in the app config;
- record version, effective date, and live URLs;
- re-run the preflight and QA when a feature, permission, SDK, contact, or
  deletion method changes.

## Mature dating-app benchmark

See `references/mature-dating-app-benchmark.md` for the Tinder/Bumble/Hily page
structures and the gaps this skill now covers. Key lessons:

- 18+ and CSAM zero tolerance are standard; a dedicated child-safety contact
  and authority/NCMEC cooperation are expected.
- Reporting, blocking, moderation, and appeals belong in the Terms.
- Account deletion needs an in-app path plus a public web/support path,
  a restore/cancellation window, subscription cancellation, and an
  uninstall/logout distinction.
- Governing law and arbitration vary by company; ask, do not assume.
- Mature policies use role-based emails and identify the contracting entity.
- Add app-store, copyright/DMCA, electronic-records, entire-agreement,
  severability, and state-specific sections where applicable.
- Never copy another app's facts or wording verbatim.

## Files

| Path | Purpose |
|---|---|
| `assets/app-function-checklist.html` | Self-contained feature/data/permission/SDK checklist |
| `assets/app-legal.example.json` | Expanded facts config, including the four-page fields |
| `references/drafting-prompt.txt` | Verbatim Terms + Privacy source prompt |
| `references/checklist.md` | Full checklist inventory and output contract |
| `references/four-page-set.md` | Page-by-page outlines for all four pages |
| `references/mature-dating-app-benchmark.md` | Tinder/Bumble/Hily structure and lessons |
| `references/google-form-deletion.md` | Google Form creation and integration |
| `references/preflight.md` | Required facts and the user-facing missing-data prompt |
| `references/source.md` | Source, revision, and provenance |
| `scripts/preflight.py` | Validate facts and print missing fields before drafting |
| `scripts/prepare_brief.py` | Fill the Terms + Privacy prompt and cross-check the checklist |
| `scripts/check_draft.py` | Terms + Privacy mechanical QA |
| `scripts/check_four_pages.py` | Four-page mechanical QA |

## Output shape

```text
legal-review/
├── legal-brief.md
├── terms-of-service.md
├── privacy-policy.md
├── child-safety-policy.md
├── account-deletion.md
├── checklist-result.txt
├── qa-report.md
└── qa-four-pages.md
```

Keep the checklist and the drafts together. Legal needs both to see which facts
the draft was based on.
