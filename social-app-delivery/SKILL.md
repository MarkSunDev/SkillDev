---
name: social-app-delivery
description: Build or port a production-shaped social discovery app across any UI stack or visual direction; use for Android, iOS, Flutter, React Native, or web implementations, including rebuilding an existing social app in another framework.
---

# Social App Delivery

Build the product as a set of behavior contracts, not as a translation of one codebase. The reference product is an 18+ social-discovery app with profiles, swipe decisions, an editorial feed, likes and visitors, private chat, wallet and gifts, calls, safety tools, and account lifecycle. It has exactly five primary destinations: **Swipe → Feed → Likes / Visitors → Chat → Me**.

No toolkit or visual language is authoritative. The current Android/Kotlin/Compose implementation and its visual direction are one implementation and one design choice. Flutter, native iOS, React Native, web, or a different visual direction must be able to satisfy the same product contract.

## Non-negotiables

- Persist real state server-side. A local list, optimistic update, or successful HTTP status is not proof that a business action happened.
- Never silently fall back from a real service to fixtures. Sample data and development purchases must stay visibly labelled.
- Treat backend readiness as data. Missing chat, notifications, billing, recovery, or calls must produce an explicit unavailable state, not a fake success.
- Keep ambiguous submission states distinct: `pending`, `accepted`, `unknown`, and `rejected`. `accepted` is not delivered and is not read.
- Preserve intent across retries. Drafts, attachments, purchase attempts, gifts, posts, and messages need durable idempotency keys or equivalent request identity.
- Do not put provider administrator credentials or server secrets in any client. A client may use only user-scoped credentials.
- Preserve separate interaction semantics. For this product, left swipe is dislike, right swipe is like, and the centre action is superlike; superlike must not be sent as an ordinary like.
- Destructive actions require contextual confirmation. A failed password confirmation must not sign the user out or destroy unrelated state.
- Navigation is not a loading lock. A user can request a new destination while work is in flight; the latest explicit destination wins.
- Do not call a feature complete until its read path, write path, reload behaviour, failure behaviour, and evidence are all accounted for.

## Before implementation

Read the relevant references before choosing architecture or writing feature work:

- `references/product-contract.md` for the product boundary, feature inventory, state rules, and definition of done.
- `references/api-contract.md` for the operation IDs, request shapes, success rules, and current backend gaps.
- `references/architecture-contract.md` for platform-neutral layers, data boundaries, concurrency, and adapter responsibilities.
- `references/delivery-playbook.md` for build order, vertical slices, and the cross-stack porting protocol.
- `references/acceptance-playbook.md` for test layers, evidence requirements, and release gates.

For a full build or port, create four repository artifacts from `assets/` and keep them current:

1. `PRODUCT.md` from `assets/product-brief.template.md`
2. `DESIGN.md` from `assets/visual-direction.template.md`
3. `STATUS.md` from `assets/delivery-status.template.md`
4. `VERIFICATION.md` from `assets/acceptance-matrix.template.md`

The documents are part of the implementation. Update them when a feature becomes connected, partial, blocked, or intentionally deferred.

## Working method

1. **Lock the product contract.** Record the user job, five destinations, feature groups, backend capabilities, and explicit non-goals. Separate the product from the current design and current framework.
2. **Choose one visual direction.** Define a scene, emotional promise, anti-references, colour roles, type roles, composition, interaction, and accessibility constraints. Do not copy another app's UI or assets. Translate roles, not pixel values, when moving stacks.
3. **Define the platform-neutral model.** Model session, profile, relationship, post, comment, conversation, message, wallet, subscription, gift, call, notification, and capability state. Keep transport DTOs out of the presentation layer.
4. **Map the wire contract at one boundary.** Normalize fields into the app model and unit-test that normalization without the UI. Validate envelopes, success codes, identifiers, body limits, redirects, retries, and stale responses.
5. **Build vertical slices.** Start with shell, navigation, authentication, and session recovery. Then add real read surfaces. Then add writes with drafts, confirmations, idempotency, and read-back. Chat, media, commerce, notifications, and calls come after the core social loop works.
6. **Implement platform adapters.** Secure storage, HTTP, media picking, camera, image processing, durable local storage, WebRTC, billing, push, lifecycle, and accessibility are ports behind neutral interfaces. Pick the target framework's normal libraries; do not leak their types into domain logic.
7. **Verify with evidence.** Use unit tests for normalization, contract tests for transport and failure injection, integration tests for real HTTP and persistence, UI flows for the five destinations, and screenshots from the installed build for responsive and accessibility checks.
8. **Ship with a status ledger.** Every row says what works, what is partial, what the backend lacks, and what evidence exists. A passing read-only probe does not make write features complete.

## Porting to another stack

When rebuilding in Flutter or another framework:

- Inventory behaviour from the installed app, product docs, status ledger, acceptance matrix, and tests. Do not translate file structure or framework-specific state management line by line.
- Reuse the wire contract and business semantics. Rebuild presentation, navigation, state ownership, and platform adapters in the target stack's idiomatic form.
- Recreate the visual direction independently from role-based tokens unless the user explicitly asks for pixel parity. Never reuse another app's source, assets, or proprietary UI.
- Keep the same feature state machine, idempotency rules, failure states, and capability disclosure.
- Re-run the acceptance matrix on the target platform. A Flutter build is not complete because the Android build passed.

## Feature-state rules

Use explicit, user-visible states:

| State | Meaning | UI obligation |
|---|---|---|
| Loading | No successful read yet | Show a stable loading surface, not fabricated content |
| Ready | Real data loaded | Show real values and preserve them during refresh |
| Empty | Successful read with no records | Explain the state and offer a relevant next action |
| Error | Request failed | Show a retryable error without remote error bodies or secrets |
| Unavailable | Backend capability is absent | Explain what is pending and disable the action honestly |
| Pending | Submission is in flight or ambiguous | Keep the draft, request identity, and retry path |
| Accepted | Server accepted the intent | Do not label it delivered, read, or completed |

## Evidence standard

A release claim needs a reproducible artifact: a test, a probe result, a screenshot, a build log, or a signed-off manual check. Prefer evidence from an installed build and a real service. Use only owned QA identities for writes and clean up created records. Never use production accounts or administrator credentials to manufacture evidence.

## References

- `references/product-contract.md`
- `references/api-contract.md`
- `references/architecture-contract.md`
- `references/delivery-playbook.md`
- `references/acceptance-playbook.md`
- `assets/product-brief.template.md`
- `assets/visual-direction.template.md`
- `assets/delivery-status.template.md`
- `assets/acceptance-matrix.template.md`
