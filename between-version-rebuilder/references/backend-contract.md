# Backend contract

All clients must preserve the Romi wire contract even when the implementation language changes. Exact protobuf definitions live in `references/protocols/`.

## Business API

| Setting | Value |
| --- | --- |
| Production endpoint | `https://api-prod.randomanimestore.com` |
| Production app name / tenant | `romi` |
| Target package name | The rebuilt app's own bundle/package identifier |
| Request method | `POST` to the root endpoint |
| Request body | Four-byte big-endian message ID followed by the protobuf payload |
| Successful response | Four-byte big-endian response ID followed by the protobuf payload; size capped at 1 MiB |
| Auth header | `Authorization: Bearer <business token>` |
| Device header | `x-other-uid: <installation/device identifier>` |
| Params header | JSON with `os`, `appver`, `app_name`, `locale`, `package_name` |
| Content-Type | `application/octet-stream` |

The transport must disable shared cache, cookies and redirects. A redirect must never forward a bearer token.

## Session, profile and configuration

| Request → response | Purpose | Success rule |
| --- | --- | --- |
| 4000 → 4001 | Apple LoginUser | `postLoginAction == 0`; embedded profile valid; token present |
| 4004 → 4005 | Apple CreateUser | `code == 1`; creation successful; positive user ID; token present |
| 4198 → 4199 | Device FastLogin | `code` 0 or 1; user info present; positive user ID; token present; user status 0 |
| 4200 → 4201 | Complete a pending device profile | `code == 1`; same user ID; status 0; pending becomes false |
| 4088 → 4089 | RefreshToken | token present; refresh schedule updated |
| 4286 → 4287 | GetUserBasicInfosV2 / profile bootstrap | exactly the requested IDs, unique; `code` 0 or 1 |
| 4308 → 4309 | GetClientConfig | JSON object, kept in memory and not merged into chat storage |
| 4070 → 4071 | Full EditProfile | `code == 1`, then re-read profile and verify the edit |
| 4468 → 4469 | Entitlement status | `code == 1`; unique kinds; non-negative left counts |
| 4470 → 4471 | Claim entitlement | `code == 1`; kinds 4 or 5 only |

Rules:

- Credential scope includes endpoint, app name and package name. A session from another scope must not restore.
- Apple login and device FastLogin are distinct paths. Do not turn a failed Apple authorization into a synthetic Apple identity; fall back to FastLogin explicitly, without Apple profile fields.
- `pending` means profile completion is required, not authenticated social access.
- Token refresh uses the server's Unix-millisecond schedule. If absent, the legacy fallback is 60 days.
- 401 clears the session. A revoked token must not remain active even if secure-store deletion fails.
- Profile edits are full replacements. Read the current profile, preserve fields the user did not edit, submit, then read back.

## Moderation

| Request → response | Purpose | Success rule |
| --- | --- | --- |
| 4230 → 4231 | Block user | `code == 1` |
| 4232 → 4233 | Unblock user | `code == 1` |
| 4234 → 4235 | Paginated block list | `code == 1`; ascending offset cursor; owner and duplicates validated |
| 4226 → 4227 | Report user | `code == 1` |

Do not send `from_user_id` or `delayTime`; the server derives the actor from the bearer session. Block-list pagination uses record offset IDs, not user IDs. Writes never retry automatically. A stale or empty block list must not erase a block that the server already acknowledged.

## Contacts and discovery

| Request → response | Source / purpose | Notes |
| --- | --- | --- |
| 5070 → 5071 | Related contacts | Full snapshot; not a friendship or cursor API. Can be a true empty result. |
| 5094 → 5095 | Suggested friends / stranger discovery | Filter includes gender, age bounds and optional location. Limit 20. |
| 5108 → 5109 | Nearby online male discovery | Cursor pagination. Values are kilometers. Not the eligibility-gated 4492 source. |
| 4554 → 4555 | Wave/swipe | `swipeType = 2`; a wave is not a delivered chat message or accepted friendship |
| 4286 → 4287 | Find by user ID / batch profiles | Up to 50 IDs; exact identity validation |

Discovery rules:

- The default Everyone list combines 5094 and 5108, interleaves the returned people, deduplicates by user ID and excludes self.
- Accept only real, non-pending, active, adult profiles. Never relabel a profile's gender.
- 5094 numeric distance is miles. 5108 numeric distance is kilometers; divide by 1.609344 for miles.
- Zero, negative, non-finite or missing distance is unknown. A selected radius excludes unknown distance.
- Blocked users are filtered from discovery, feed and profile surfaces.
- An account switch resets discovery filters and cancels in-flight work.

## Chats and media gateway

The client uses a user-authenticated gateway, not Tencent administrator credentials and not the HRU/TIM SDK. Configure its HTTPS origin with `ROMI_MESSAGING_ENDPOINT`. Release builds must not permit localhost.

| Route | Body | Result |
| --- | --- | --- |
| `POST /v1/messages/conversations` | optional `cursor` | items with peerID, name, unread, lastMessage; nextCursor |
| `POST /v1/messages/peer` | `peerID` | one conversation summary |
| `POST /v1/messages/history` | `peerID`, optional `cursor` | oldest-first messages; nextCursor |
| `POST /v1/messages/send` | `peerID`, text or mediaID or exchange, UUID `clientID` | messageID, clientID, senderID, text, sentAt |
| `POST /v1/messages/read` | `peerID`, integer `throughTime` | `{"ok":true}` |
| `POST /v1/messages/media` | base64 JPEG | mediaID, HTTPS URL, width, height |
| `GET /v1/messages/media/<43-char-capability>.jpg` | none | JPEG without bearer header |

Rules:

- Every request except media GET uses `Authorization: Bearer <business token>` and POST JSON.
- Status mapping: 200 OK, 401 unauthorized, 402 billing rejected, 403 blocked, 409 ambiguous, other unavailable.
- Reserve the durable draft before send authorization. A completed UUID returns its original acknowledgement; conflicting or unresolved attempts return 409 and are not silently re-sent.
- Text is 1–4096 UTF-8 bytes. Photos are JPEG under 1 MiB and at most 2048 px per side; the client downsamples to 1600 px and strips metadata.
- Merge remote messages by server message ID or original draft UUID. Never by text.
- Polling creates a baseline; it must not double-count rounds or unread.
- Only foreground polling is shipped in the reference. Do not label it push.

## Live typing TCP

| Setting | Value |
| --- | --- |
| Host | `prod-tcp.randomanimestore.com:8000` |
| Header | Four big-endian 32-bit words: total length including header, user ID, command, sequence number, then protobuf |
| 60001 | Client heartbeat: index, active status, call occupancy |
| 60002 | Server heartbeat acknowledgement |
| 60026 | Peer typing: peer user ID, delay seconds |

Heartbeat every five seconds. Positive delay shows the peer typing for that interval; zero stops; negative is ignored. Only the open chat's peer may trigger the bubble. Clear state on reply, expiry, disconnect, leaving, backgrounding, blocking or account reset. Never persist typing state or invent it for outgoing messages.

## Commerce

| Request → response | Purpose | Notes |
| --- | --- | --- |
| 4258 → 4259 | Membership state | Authoritative membership truth |
| 4536 → 4537 | Visitor subscription state | Authoritative visitor truth |
| 4538 → 4539 | Subscription catalog | Normal and visitor plans |
| 4340 → 4341 | Coin balance | Int64 |
| 4344 → 4345 | Coin packages | Response has no `code`; validate values directly |
| 4376 → 4377 | Coin history | Direction from `changeType` |
| 4466 → 4467 | Message/call rates | Text per message; audio/video per minute; Super Like per use |
| 4512 → 4513 | Visitor snapshot | Server milliseconds; full snapshot |
| 4484 → 4485 | Clear free text entitlement | `kind = 4`; `code == 1` |
| 4256 → 4257 | Verify membership transaction | Server confirmation required |
| 4540 → 4541 | Verify visitor transaction | Server confirmation required |
| 4342 → 4343 | Verify coin transaction | Server confirmation required |

Rules:

- Success requires `code == 1` where the response has a code. A missing code is not success unless the endpoint contract explicitly omits it.
- Price display comes from StoreKit `displayPrice`; no server USD string and no name-based inference.
- First-charge bonus is additional coins, not the final balance. Returning buyers receive no bonus.
- Do not infer coin direction from the sign of a positive magnitude.
- Unknown `changeType` renders neutrally; handle `Int64.min` without trapping.
- StoreKit transactions use an `appAccountToken` bound to the business account namespace and server environment. Reject local `.xcode` transactions against production.
- Finish a transaction only after server verification. Handle cancel, pending, failure, revocation, expiry, upgrade and unfinished transactions.
- HTTP 401 clears session and commerce state. Late responses cannot cross accounts.

### Required client configuration

| Build setting | Info.plist key |
| --- | --- |
| `BETWEEN_APPLE_ISSUER_ID` | `BetweenAppleIssuerID` |
| `BETWEEN_APPLE_KEY_ID` | `BetweenAppleKeyID` |
| `BETWEEN_APPLE_APP_ID` | `BetweenAppleAppID` |

Use the rebuilt app's own bundle ID and App Store products. Never copy another app's Apple identity. The private key stays on the server.

## Intimacy and contact exchange

| Request → response | Purpose |
| --- | --- |
| 21000 → 21001 | Check free exchange condition: score, threshold, order, cooldown, status |
| 21002 → 21003 | Create free exchange order |
| 21004 → 21005 | Save own contact card |
| 21006 → 21007 | Get contact cards |
| 21014 → 21015 | Get supported card types |

Status: locked 0, unlocked 1, processing 2, completed 3, cooldown 4. Platforms: Instagram 1, Snapchat 2, X 3. Pair order follows actual genders: male user first, female user second. Peer cards are requested only after a completed exchange and only for the exchanged platform. Own cards remain editable separately.

## Error and isolation rules

- Business rejection: preserve the code in diagnostics, never log tokens, request bodies, raw responses or profile data.
- Unknown outcome: keep the draft or operation reserved and expose reconciliation instead of re-sending.
- Cancellation and account switch invalidate late responses.
- The same rule applies to reads: a late feed, chat, visitor or commerce response from another account is discarded.
- Do not show a locally cached success as server truth.

## Contract tests worth porting

At minimum, test:

- fixed request bytes and response IDs for auth, moderation, discovery, feed, commerce and intimacy;
- unknown enum values and missing fields fail closed;
- 401 clears the session;
- 429 retry only on read paths;
- 402 becomes billing rejection;
- 409 becomes ambiguous, not a second write;
- pagination cycles, cursor regressions and duplicate IDs are rejected;
- account switching discards in-flight results;
- message merge uses server ID or draft UUID, never text;
- distance units, unknown distance and filter boundaries;
- `changeType` direction and `Int64.min` formatting;
- remote messages, photos, GIFs and contact events remain backward-compatible.
