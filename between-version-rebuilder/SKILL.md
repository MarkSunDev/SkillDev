---
name: between-version-rebuilder
description: Rebuild or evolve the Between 1.0 messaging app into 1.1 and 1.2 releases with matching product and commercial behavior, Romi backend connectivity, and a code- and design-distinct implementation; use for Between ports, release-ladder planning, parity audits, or App Review clone-risk work.
---

# Between Version Rebuilder

Produce a release ladder from a 1.0 baseline:

- **1.1** — the social/backend release: accounts, Chats, Contacts, Feed, Private-AI, Privacy/You, moderation, guest mode.
- **1.2** — the chat-first commercial release: 1.1 plus People You May Know filters, lighter Feed, chat polish, monetization, visitors, quota, typing, intimacy, photos.

The fixed part is product behavior, commercial rules, wire contracts, and design quality. The implementation stack, internal architecture, visual language, component system, asset set, and copy expression may differ. Treat the original Between code as a behavior oracle, never as a source template.

## Read in this order

For a full rebuild, read all of these before choosing an architecture:

1. `references/source-of-truth.md`
2. `references/version-matrix.md`
3. `references/backend-contract.md`
4. `references/design-quality.md`
5. `references/originality-and-app-review.md`
6. `references/release-workflow.md`

Use `references/protocols/*.proto` as the exact wire definitions.

## Truth hierarchy

1. **Wire contract and shipped release behavior** define parity for 1.1 and 1.2.
2. **The final PRD** defines product intent, principles, and screen-level constraints. It is not proof that a mechanism shipped.
3. **The reference repository** is read-only evidence for edge cases and acceptance behavior. Do not port its file tree, symbols, component names, comments, assets, or screen construction.
4. When PRD and shipped behavior conflict, implement the shipped behavior and record the difference. Do not silently implement the PRD's full MLS, two-key cryptography, or on-device generative model unless the user explicitly asks and the infrastructure exists.

## Non-negotiables

- Use five primary tabs in this order: **Chats, Contacts, Feed, Private-AI, You**.
- Keep signed-in account storage and guest/sample storage separate. Never merge sample conversations into an account or recreate deleted samples.
- Normal launches use real backend data. Fixtures are debug-only, explicitly flagged, and unavailable in Release.
- Private-AI is local, per-conversation, consent-gated, and makes no network requests. Never synthesize a model response, byte count, key state, or agreement state.
- Preserve the distinction between `pending`, `accepted`, `unknown`, and `rejected` for writes. A successful HTTP response is not proof of delivery, payment, entitlement, or read state.
- Writes never retry automatically. Message sends, posts, purchases, blocks, reports, profile edits, and quota clears need durable request identity or an equivalent duplicate guard.
- HTTP 401 clears the active session. Responses that arrive after logout or account switching are discarded, not displayed in the next account.
- Purchases finish only after server verification. Never grant membership, coins, or visitor access locally.
- Use backend-provided profiles, avatars, distances, prices, benefits, rates, and entitlement truth. Never fabricate people, mutual contacts, ages, purchases, or success states.
- The design must be intentionally authored for the target release. A reskin of the reference screens does not satisfy this skill.

## Required artifacts

Create and maintain these in the target repository:

- `PRODUCT.md` — user, promise, five destinations, release scope, non-goals.
- `DESIGN.md` — visual charter, tokens, type roles, layout, motion, accessibility.
- `BASELINE.md` — what exists in 1.0 and exactly what carries forward.
- `VERSION-MATRIX.md` — feature-by-feature 1.1/1.2 parity status with evidence links.
- `BACKEND.md` — endpoints, framing, auth, error mapping, account isolation, deployment gaps.
- `VERIFICATION.md` — test layers, live probes, screenshots, builds, known failures.
- `ORIGINALITY.md` — code/design differentiation audit and App Review rationale.

Use `assets/iteration-brief.template.md` to start `PRODUCT.md`, `DESIGN.md`, `BASELINE.md`, and `VERSION-MATRIX.md`.

## Workflow

### 1. Freeze the 1.0 baseline

Record the source commit or archive hash, screens, local data model, guest samples, Private-AI behavior, reminder behavior, onboarding, and settings. Mark which 1.0 behavior is preserved, replaced, or retired.

Do not begin by reading the reference app top-to-bottom. Inventory observable behavior, then use the reference only to resolve ambiguous edge cases.

### 2. Choose the differentiation strategy

Define three independent choices before coding:

- **Stack** — native iOS, Flutter, React Native, Kotlin Multiplatform, or another shippable client.
- **Architecture** — your own module boundaries, naming, state ownership, persistence, and navigation.
- **Visual language** — a distinct scene, palette, type system, composition, motion, and asset direction.

The result must be a genuinely different product expression, not renamed symbols or rearranged files. Read `references/originality-and-app-review.md` before writing UI or copying any asset.

### 3. Build the platform core

Implement these as neutral layers before feature screens:

1. protobuf codec and four-byte big-endian message framing;
2. HTTP transport with no redirects, bounded response size, and typed errors;
3. session store, account namespace, token refresh, and stale-response fencing;
4. secure local storage and schema migration;
5. account-scoped repositories for profile, messaging, contacts, feed, commerce, moderation, and intimacy;
6. a local-only Private-AI engine over the conversation's allowed memory window.

Keep transport DTOs out of views. Keep backend truth in repositories, not in view state.

### 4. Ship 1.1 as vertical slices

Build in this order:

1. onboarding, account choice, Apple login, device FastLogin fallback, guest mode;
2. session restore, profile completion, logout, account isolation;
3. Chats list, thread history, send/retry/read, foreground polling;
4. Contacts: People You May Know, My Friends, profile, wave, find by user ID, greet-to-chat;
5. Feed: list, publish, like, delete, report, photos, own posts;
6. Private-AI: consent, memory window, catch up, find, reminder, phrase learning, rewrite, nudge, receipts;
7. Privacy/You, text size, appearance, blocked users, account deletion, profile editing;
8. moderation and write-path reconciliation.

A slice is complete only when its read path, write path, reload, failure state, account-switch behavior, and evidence are present.

### 5. Stabilize 1.1 before evolving

Run contract tests, domain tests, UI flows, a Release build, and a real read-only account pass. For writes, use only owned QA identities and clean up. Record exact pass/fail counts and failures. A passing read-only probe does not make a write feature complete.

### 6. Evolve the same rewrite into 1.2

Do not fork a second copy of the 1.1 codebase. Add 1.2 as a release state in the same product:

1. redesign the visual system and density without losing navigation or accessibility;
2. add PYMK Everyone/Men/Women and distance filters using both real discovery sources;
3. lighten Feed media and refine author/post presentation;
4. add real avatars, unread aggregation, chat relationship/exchange, photos, and typing state;
5. add membership, visitor subscription, coins, visitors, rates, and purchase verification;
6. add alternating-round prompts and the five-minute successful-send quota;
7. migrate local data and keep old caches readable;
8. re-run the full matrix, including regression of every 1.1 behavior.

### 7. Verify parity and originality

Run both gates:

- **Behavior gate** — every row in `VERSION-MATRIX.md` has a test, live probe, screenshot, or explicit blocked status.
- **Originality gate** — no copied source, assets, strings, symbol names, or screen construction. Use `scripts/audit_originality.py` and the manual review in `references/originality-and-app-review.md`.

Do not mark a feature complete because its UI exists, an endpoint returns 200, or a fixture passes.

### 8. Package the release

Produce five real screenshots per release from the installed build, the listing copy, what's new, review notes, and evidence links. Use `references/release-workflow.md`. If `$app-store-prd-metadata` is available, use it for metadata limits, five-image validation, and legal drafts.

## Stack guidance

- **Native iOS** — rebuild presentation and state ownership around your own design system; do not reuse SwiftUI view bodies, environment keys, or helper names from the reference.
- **Flutter / React Native** — put protobuf framing, session, storage, and domain state behind platform-neutral services. Recreate accessibility, secure storage, media picking, and store billing idiomatically.
- **Kotlin Multiplatform / other shared-core clients** — share the contract and domain rules, not screen structure. Keep platform UI genuinely native to the chosen design direction.
- **Web/PWA** — only when the requested deliverable accepts it. Match keyboard, safe-area, media, and notification behavior honestly; do not claim native parity.

## Stop conditions

Stop and report a blocker when:

- the backend origin, tenant, package identity, or messaging gateway is missing;
- the Apple product IDs or server verification configuration do not exist;
- a required API returns a successful empty result but the product contract requires real data;
- a feature would require inventing server truth, fixtures, or a cryptographic claim;
- the only available differentiation is obfuscation or cosmetic renaming.

A blocked feature stays visibly blocked. It never becomes a fake success.
