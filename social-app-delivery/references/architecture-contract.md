# Architecture Contract

The architecture must survive a change of UI toolkit. Use the target framework's idioms, but preserve these boundaries.

## Layers

| Layer | Responsibility | Must not own |
|---|---|---|
| Presentation | Screens, navigation, accessibility, visual states | Business success rules or raw transport types |
| State coordinator | View state, route/tab intent, request lifecycle, drafts | Platform UI widgets or provider secrets |
| Domain/usecases | User actions, validation, state transitions, intent semantics | HTTP, secure storage, camera, or billing APIs |
| Gateway/normalizer | Convert wire payloads into stable app models | Screen layout or navigation decisions |
| Transport | HTTP/WebSocket, envelope checks, timeouts, size limits | Product copy or list rendering |
| Persistence | Secure session, drafts, pending requests, cached account-scoped data | UI state as the source of truth |
| Platform adapters | Media, camera, storage, billing, push, calls, lifecycle | Product rules that belong in domain code |

The concrete pattern may be ViewModel + state flow, Bloc, Riverpod, Redux, MVVM, or another idiomatic approach. The invariant is that the UI observes a stable app model and calls explicit user intents; it does not assemble raw service payloads.

## Platform-neutral model

At minimum, model these concepts explicitly:

- `Session`: endpoint, user identity, token, expiry, disposition.
- `Profile`: id, display name, age, bio, city, profession, interests, photos, verification, sample flag.
- `DiscoveryState`: current profile, filters, loaded queue, action result.
- `FeedPage`: posts, cursor, has-more, refresh disposition.
- `Post`: author, text, media, like state and count, comment count, timestamp.
- `Comment`: author, text, parent, timestamp, cursor identity.
- `RelationshipGroup`: likes, visitors, sent likes, blocked, or other server-defined group.
- `Conversation` and `Message`: peer, message kind, submission state, timestamp, attachment, read state.
- `Wallet`: coin balance, reward balance, membership, catalogues, transactions.
- `Gift`: catalogue item, price, recipient, delivery state.
- `Call`: mode, peer, signalling state, media state, connectivity.
- `Notification`: kind, target, read state, cursor.
- `Capability`: explicit booleans for chat, calls, notifications, billing, recovery, and other externally blocked features.

Use strings for identifiers that may exceed the target language's safe integer range. Normalize timestamps to one documented unit. Keep server IDs opaque unless the contract explicitly defines them as numeric.

## Wire boundary

For the reference JSON gateway:

- Send a strict JSON envelope with `protoId` and `body`; `protoId` is a routing field, not a requirement to add a binary runtime.
- Accept only a numeric response `protoId` equal to the request ID plus one.
- Require a JSON-object `body`.
- Apply an operation-specific success rule. Do not assume every operation uses `code="Success"`.
- Accept documented alternatives such as `isSuccessful=true` or `code="UserServiceCommonCodeNone"` only where the contract permits them.
- Treat non-2xx HTTP, redirects, invalid content type, oversized bodies, malformed JSON, wrong envelope IDs, and stale session responses as failures.
- Do not surface remote error bodies or provider secrets in user-facing messages.
- Disable automatic redirects and connection retries at the transport layer; retry only at the intent layer with the same request identity.
- Scope a session snapshot to its endpoint and generation. Discard a response if the endpoint or session changed while it was in flight.

For another backend, keep the same boundary: a strict transport adapter plus a pure normalizer plus operation-specific success semantics.

## Normalization rules

- Keep normalization pure and testable without a UI.
- Normalize optional fields to explicit null/empty values once, not in each screen.
- Normalize server casing, numeric/string ID differences, timestamps, nested user objects, media arrays, and boolean/string booleans in one place.
- Preserve source priority when a profile has multiple image fields.
- Never let an unknown field crash a page; never silently turn a malformed required field into a plausible value.
- Keep raw provider payloads out of logs and out of the domain model.

## State ownership

The state coordinator may own:

- current primary tab and secondary route;
- current account-scoped lists and cursors;
- selected detail entities;
- action status and safe error copy;
- drafts and pending request keys;
- capability flags;
- refresh and polling lifecycle.

Keep large payloads out of long-lived global state where the target framework makes that costly. Scope caches to origin and account. Clear or re-key account-scoped drafts when the user changes.

## Request identity and drafts

- Derive a draft slot from the service origin and account identity, not only the device.
- Persist text drafts, staged attachments, pending keys, and enough metadata to survive process death.
- Generate one stable request key per logical intent. Retry the same intent with the same key.
- If the server returns `unknown`, keep the key and reconcile rather than creating a new submission.
- If the server returns a known validation failure, the user may edit and create a new intent.
- For purchases and gifts, the transaction/request key must survive an app restart and remain stable across retries.

## Pagination and refresh

- Use the server's cursor/offset exactly as defined; do not invent page numbers.
- Append unique records by stable ID.
- Preserve the loaded window when refreshing a page.
- Re-read enough pages to retain the current window when removed or blocked records disappear.
- Track whether more pages exist separately from whether the current page loaded.
- Never acknowledge a read cursor before the projection that depends on it has refreshed.

## Platform adapter table

Choose the target framework's normal implementation; these are examples, not dependencies.

| Capability | Neutral contract | Typical adapters |
|---|---|---|
| Secure session | Read/write/clear token and endpoint; account scoping | Android Keystore, iOS Keychain, Flutter secure storage |
| Durable drafts | Account-scoped atomic write and recovery | SQLite, file store, key-value store with durable mode |
| HTTP | Strict JSON, cancellation, timeout, byte limit | OkHttp, URLSession, Dart `http`/Dio, fetch |
| Media | Pick/capture, read bytes, MIME/size validation, re-encode | Android Photo Picker, PHPicker, image_picker, camera |
| Calls | Signalling plus media peer connection, lifecycle cleanup | Native WebRTC, flutter_webrtc, platform call APIs |
| Billing | Store transaction, verify server-side, restore, reconcile | Play Billing, StoreKit, in_app_purchase |
| Push | Obtain a real provider token and bind it server-side | FCM, APNs, platform push plugin |
| Navigation | Destination intent, back stack, deep links | Platform router, go_router, NavigationStack |

If a capability is absent, expose an `unavailable` state and disable the dependent actions. Do not fake the adapter.

## Concurrency checklist

- Use a request generation or cancellation token for route and session changes.
- Let the latest explicit tab request win.
- Keep previously loaded content visible while refreshing.
- Do not let a failed background poll erase user-visible data.
- Ignore responses from a superseded endpoint or account.
- Make polling idempotent and stop it when signed out or when the screen no longer needs it.
- Cancel or ignore in-flight uploads and calls when the user leaves the relevant lifecycle scope.
