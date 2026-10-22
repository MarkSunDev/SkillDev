# Delivery Playbook

Use this order for a new build or a rebuild in another stack. The goal is a working vertical slice with real evidence, not a large horizontal scaffold.

## Phase 0 — establish the contract

Create `PRODUCT.md`, `DESIGN.md`, `STATUS.md`, and `VERIFICATION.md` from the templates. Record:

- the user job and age boundary;
- exactly five primary destinations;
- the feature inventory and explicit non-goals;
- which backend capabilities exist and which do not;
- one visual direction with anti-references;
- what evidence will count as done.

Do not start by translating an existing file tree. For a port, inventory screens, user actions, side effects, failure states, and tests from the installed app and its documents.

## Phase 1 — shell, navigation, and session

Build and verify:

- app shell with five fixed destinations and predictable back behavior;
- signed-out, loading, expired-session, and unavailable-service states;
- secure session storage and endpoint-scoped session reset;
- sign-in, refresh, sign-out, and account deletion boundaries;
- no secrets in source, build config, logs, or error messages.

Acceptance: a real account can enter the shell, navigate while requests are running, restart without losing the session, and recover from an expired session.

## Phase 2 — real read surfaces

Add the read path in this order:

1. own profile and capabilities;
2. discovery profiles and filters;
3. feed and pagination;
4. likes, visitors, and supported relationship groups;
5. public profile detail;
6. wallet and catalogues.

For every page, implement loading, ready, empty, error, and unavailable. Mark any sample content explicitly. Do not let an empty response pull fixtures into a real environment.

Acceptance: each read reaches the real service, survives refresh, preserves loaded pages, and has a screenshot or contract evidence.

## Phase 3 — core writes

Implement one vertical slice at a time:

- swipe dislike/like/superlike with distinct semantics;
- profile like/unlike and read-back;
- profile edit and avatar upload;
- block/unblock/report;
- create/delete post;
- like/unlike post;
- create/delete comment.

Each slice needs:

- a stable intent identity for retry-safe writes;
- validation before the request;
- a visible pending state;
- an authoritative reload or response merge;
- explicit failure copy;
- cleanup for owned QA records.

Acceptance: a real QA account performs the write, another read confirms it, and the status ledger records the service operation used.

## Phase 4 — chat and media

Only enable chat when a user-scoped transport exists. Build:

- conversation list and thread history;
- text send with a durable draft and idempotency key;
- attachment pick/capture, size and type validation, image re-encode, upload, and retry;
- submission state rendering;
- read cursor handling;
- block interaction and unavailable-state behaviour.

If the transport is missing, keep the screen and show an explicit pending-service state. Do not attach administrator provider credentials or pretend a local outbox is delivered chat.

Acceptance: restart during an ambiguous send preserves the same request identity; retry does not create a duplicate; a block removes access in both directions where the service says it does.

## Phase 5 — commerce, notifications, and calls

Add only after the core social loop works:

- coins, reward tokens, membership, product catalogues, purchase, restore;
- gift catalogue and atomic send/balance update;
- notification list, unread cursor, and target navigation;
- call signalling, media connection, TURN disclosure, and foreground lifecycle;
- settings, recovery, verification, and account deletion as supported.

Each capability must be gated by a real capability flag. Catalogue visibility is not purchase readiness. Device registration is not push delivery. A wallet debit is not gift delivery.

## Phase 6 — hardening

- Inject network loss, timeout, 401, 403, 404, 409, 429, and 503 failures.
- Test stale responses after origin/account changes.
- Test rapid tab changes and repeated taps.
- Test process death with drafts, attachments, purchases, gifts, and posts.
- Test empty, very long, malformed, and missing optional data.
- Check large type, narrow width, tablet width, contrast, focus order, labels, and gesture alternatives.
- Audit runtime dependencies against the product's forbidden SDK and codec boundary.

## Phase 7 — release evidence

Produce:

- debug and release builds;
- unit, contract, integration, and UI test results;
- real-service read probe output;
- controlled QA write evidence;
- screenshots from the installed build for all primary destinations and critical flows;
- a status ledger with connected, partial, blocked, and deferred rows;
- a verification document with reproducible commands or steps.

## Porting protocol

When rebuilding in another stack, follow these steps in order:

1. **Inventory.** List every user-visible action, its side effect, its success rule, and its failure state. Use the installed app and acceptance artifacts, not file names.
2. **Separate product from presentation.** Copy the product contract and wire semantics. Recreate the visual direction from role-based decisions unless pixel parity was explicitly requested.
3. **Choose target idioms.** Pick the target framework's normal navigation, state, storage, media, and testing tools. Do not reproduce the source framework's class graph.
4. **Map adapters.** Write a table from each neutral capability to the target library or platform API. Mark gaps before feature work.
5. **Build in slices.** Repeat phases 1–7 on the target stack. Do not mark a port complete because the original platform's tests pass.
6. **Compare behaviour.** Check destinations, state transitions, request identity, persistence, accessibility, and capability disclosure. Visual comparison is secondary unless requested.

## Visual direction selection

Before building screens, define:

- the scene in which the app is used;
- the emotional promise;
- the anti-references and ownership boundary;
- colour roles rather than only hex values;
- type roles rather than only font names;
- composition and spacing rhythm;
- primary action semantics;
- motion and feedback rules;
- responsive and accessibility constraints.

Use one coherent direction. Do not mix a restrained system with an editorial one or copy another product's visual identity. The design document must let a different framework produce the same intent without copying pixel values.

## Build order for the reference Flutter port

If the task is specifically to rebuild this product in Flutter, use this order:

1. Flutter shell, router, theme roles, secure session, and API client.
2. Auth/session state and real profile.
3. Discovery and swipe semantics.
4. Feed, comments, media, and post writes.
5. Likes/visitors, profile detail, and safety actions.
6. Chat and attachment outbox.
7. Wallet, gifts, notifications, calls, settings, and account deletion.
8. Responsive, large-type, failure-injection, and installed-build screenshot pass.

Keep the same wire adapter contract and status vocabulary. Replace Compose-specific state and rendering with Flutter-native patterns; do not port the Android view model or composable structure literally.
