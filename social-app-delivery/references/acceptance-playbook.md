# Acceptance Playbook

The purpose of verification is to make every product claim reproducible. A screenshot of a populated screen is not enough; a read-only probe is not enough; a passing unit test is not enough.

## Test layers

| Layer | What it proves | Minimum coverage |
|---|---|---|
| Pure unit | Parsing, normalization, validation, state transitions | IDs, timestamps, optional fields, success rules, pagination, drafts |
| Contract | Transport and failure semantics | Envelope, content type, non-2xx, redirects, oversized body, stale session, operation-specific success |
| Integration | Real HTTP and persistence | Auth, read pages, write/read-back, restart, idempotency, account isolation |
| UI flow | User-visible path | Five destinations, critical write flows, empty/error/unavailable states |
| Visual | Layout and accessibility | All destinations, critical secondary routes, narrow width, large type, tablet |
| Release | Shippable artifact | Debug/release build, lint, dependency audit, install and launch |

Add tests at the lowest layer that can catch the defect, then prove the end-to-end path at least once.

## Failure injection

Exercise these deliberately:

- connection loss before and after the request is sent;
- timeout and cancellation;
- 401/403 session expiry;
- 404 missing detail;
- 409 duplicate or conflicting intent;
- 429 throttling;
- 503 unavailable backend or provider;
- malformed JSON, wrong content type, wrong envelope, oversized body, and redirect;
- response from an old endpoint or old account;
- repeated taps and rapid tab changes;
- process death after a write but before projection refresh;
- duplicate purchase, gift, post, comment, or message retry.

For an ambiguous network failure, the expected result is a retained draft/pending identity and a reconciliation path, not a blind new submission.

## Evidence matrix

Maintain one row per claim:

| Claim | Service operation / route | Test type | Evidence | Status |
|---|---|---|---|---|
| Real feed loads | Feed read | Integration + installed build | Probe output, screenshot | Connected |
| Post can be created | Create-post write | QA write + read-back | Test log, screenshot | Connected |
| Chat works | User-scoped message route | Integration | Pending service | Blocked |

Status values:

- `Connected`: real read/write path verified.
- `Partial`: some states or operations work; note the gap.
- `Blocked`: backend or platform capability is absent; note the blocker.
- `Deferred`: intentionally out of this release.
- `Not started`: no implementation or evidence.

Never use `Connected` for a feature verified only by a fixture, a local mock, a catalogue response, or an optimistic UI update.

## Real-service rules

- Read-only probes may use a dedicated QA account.
- Writes must target owned QA identities and owned content.
- Clean up created posts, comments, messages, blocks, and test relationships.
- Do not use administrator or provider credentials in the client or test harness.
- Do not send remote error bodies, tokens, provider signatures, or identifiers into user-visible output or logs.
- If the test service lacks an operation, record it as blocked and keep the client state explicit.

## UI and visual checks

Capture screenshots from the installed build, not design mocks. Cover:

- signed-out and signed-in states;
- Swipe, Feed, Likes/Visitors, Chat, and Me;
- profile detail;
- thread and attachment/gift flow;
- edit profile and avatar;
- wallet and purchase state;
- notifications and settings;
- blocked/report/delete confirmation;
- compact width;
- large system type;
- tablet or wide width;
- empty, error, and unavailable states.

Check accessibility independently of screenshots: interaction targets, labels, focus order, scalable text, contrast, and gesture alternatives. A gesture-only primary action fails.

## Idempotency and restart checks

- Draft text survives process death and is scoped to origin + account.
- Pending attachment and message keys survive restart.
- Retrying uses the same key and does not create a duplicate.
- Purchase and gift retries reuse the same transaction/request identity.
- A failed projection refresh does not cause a second charge or send.
- A stale response cannot overwrite a different account or origin.

## Release gate

Before calling the build shippable:

1. Every primary destination is reachable and has a real read or an explicit unavailable state.
2. Core writes are read back from the service and verified with owned QA data.
3. Missing chat, recovery, notification, billing, or call capabilities are visible and disabled honestly.
4. Session storage is secure and endpoint/account scoped.
5. Media size, MIME, image re-encoding, and failure recovery are implemented.
6. Navigation survives in-flight requests and rapid taps.
7. Empty, loading, error, unavailable, pending, and accepted states exist where applicable.
8. Accessibility and responsive checks have evidence.
9. Debug/release builds, lint, and dependency audit pass.
10. `PRODUCT.md`, `DESIGN.md`, `STATUS.md`, and `VERIFICATION.md` agree with the build.

## Handoff

The final handoff states what works, what is blocked, what a reviewer can run, and where the evidence lives. Do not summarize a blocked feature as complete because the rest of the app works. Do not hide a known limitation behind a demo data path.
