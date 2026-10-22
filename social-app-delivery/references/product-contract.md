# Product Contract

This is the platform-neutral product definition for the reference social app. Replace the product-specific facts when building a different social product; retain the contract structure and the non-negotiable state rules.

## Product job

The app helps an adult meet people through profiles, express interest, share moments, and sustain private conversations. It is an installed social product, not a marketing site. Profiles, safety, media, calls, purchases, and account lifecycle are part of the product, not decoration.

The audience is 18+. Age eligibility and account lifecycle must be enforced by the real account path. Do not add an age gate only in the UI while the service accepts underage accounts.

## Primary destinations

Keep exactly five fixed primary destinations:

1. **Swipe** — discovery and person-to-person decisions.
2. **Feed** — editorial moments, comments, and reactions.
3. **Likes / Visitors** — inbound interest and profile visitors, with relationship filters where supported.
4. **Chat** — conversation list and private threads.
5. **Me** — own profile, preferences, safety, wallet, and settings.

Secondary routes may be pushed above these destinations: profile detail, edit profile, filters, settings, blocked users, wallet, gifts, notifications, account deletion, and call screens. A secondary route must have an obvious back path and must not silently change the meaning of a primary tab.

## Feature inventory

### Identity and session

- Installation-scoped fast login or email/password login, depending on the available backend.
- Session refresh, sign-out, and account deletion.
- Password recovery and email verification only if the service exposes user-scoped endpoints.
- Session state scoped to one service origin. Changing origin invalidates the old session.
- Tokens and provider credentials stored in platform secure storage, never in source or build config.

### Discovery and profiles

- Discover real profiles with photos, age, name, bio, city, profession, interests, and availability where supplied.
- Age and preference filters validated before sending.
- Open a profile without losing the current discovery context.
- Dislike, like, and superlike are distinct user intents. The centre action must never be reported as a normal like.
- Persist the server response, not only the local removal of a card.
- Profile details distinguish real content from development samples.

### Social graph and safety

- Likes received, visitors, and other relationship groups only when the backend supports them.
- Mark inbound likes read only after a successful service call.
- Block, unblock, list blocked users, and report a user or post.
- Blocking removes both directions of visibility where the service contract says it does; do not assume a one-sided hide.
- Confirmation is contextual and names the person or content being acted on.

### Feed and comments

- Feed pages with opaque cursors or server-provided offsets, preserving already loaded pages.
- Post detail may fall back to the feed item only when the detail endpoint is unavailable; the fallback must not fabricate extra fields.
- Create and delete a post, with a stable client token for retries.
- Like and unlike a post, then refresh or read back the authoritative count and state.
- List, create, and delete comments with cursor preservation.
- Media picking, image re-encoding, size limits, upload, and failure recovery.

### Chat

- Conversation list and thread history only when a user-scoped chat transport exists.
- Text and supported attachments with durable drafts and idempotency keys.
- Sending state is separate from delivery and read state.
- A missing chat gateway disables chat honestly; it does not fall back to fixtures or administrator provider credentials.
- Attachment retries reuse the same request identity and survive process restart.
- Gifts are not marked delivered merely because a wallet debit succeeded.

### Wallet, membership, and gifts

- Keep coins, reward tokens, subscription state, and purchase catalogues separate.
- Show live catalogues even when purchase verification is not deployed.
- A purchase is complete only after the service records and verifies the transaction.
- Restore must not double-grant rights.
- Gift sending checks balance, membership, block state, and conversation eligibility atomically on the server.
- Development entitlements and purchases must be visibly marked as development.

### Calls and notifications

- Calls require signalling and media transport independently; a catalogue or chat adapter does not imply call readiness.
- Without TURN, report local-network-only connectivity rather than claiming reliable calling.
- Calls end when the app leaves the foreground unless background calling is actually implemented.
- Installation registration is not push delivery. Do not invent a push token or claim notifications work because a device row exists.
- Notification rows may link to a thread, post, profile, wallet, or relationship view only when the target exists.

## State and concurrency rules

- A load has one of: loading, ready, empty, error, or unavailable.
- A submission has one of: idle, pending, accepted, unknown, rejected, or failed-with-known-no-effect.
- A refresh re-reads the loaded window and drops records the server says are gone. It preserves older pages and their continuation where possible.
- Deduplicate records by stable server ID; do not deduplicate by display text.
- A response from an old endpoint or old session must not overwrite current state.
- The last requested primary destination wins, even if an earlier request finishes later.
- A global busy flag may be used for a prototype, but it must not swallow navigation. Production-quality ports should prefer operation-scoped request state.
- Preserve loaded content during refresh; do not replace a populated screen with a fake loading list.

## Definition of done for one feature

A feature is done only when all applicable items are true:

1. The happy-path read or write uses the real service contract.
2. Validation and permission failures are visible and retryable where appropriate.
3. Empty, loading, error, and unavailable states are designed.
4. Writes persist across relaunch or are explicitly read back from the service.
5. Ambiguous writes retain their draft and request identity for reconciliation.
6. The feature has a unit, contract, integration, or installed-build evidence artifact.
7. The status ledger records the exact limitation if the backend is incomplete.

## Explicit non-goals

- Do not copy another app's source, assets, UI, or proprietary model.
- Do not describe a local fixture or development purchase as a real user, delivery, or payment.
- Do not add a binary codec or vendor SDK when the service contract is ordinary JSON.
- Do not expose internal provider routes, administrator routes, fake-payment routes, or test-only credentials in a shippable client.
