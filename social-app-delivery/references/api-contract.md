# API Contract

This is the language-neutral service contract for the reference product. It describes the JSON business gateway used by the current client and the optional local development service. Do not import Android-specific types or a binary Protobuf runtime from this document.

## Test business gateway

```http
POST https://api-dev.tarois.com
Accept: application/json
Content-Type: application/json
Authorization: Bearer <user JWT>
Params: {"app_name":"romi","os":"android"}
User-Agent: <product>/<version> (<platform>)
```

Request and response envelope:

```json
{"protoId": 4284, "body": {"userId": "1234567890"}}
{"protoId": 4285, "body": {"code": "UserServiceCommonCodeNone", "userInfo": {}}}
```

Rules:

- `protoId` is a JSON routing field. It does not require a Protobuf runtime.
- A successful response has a numeric `protoId` equal to the request ID plus one and a JSON-object `body`.
- Send 64-bit IDs, offsets, and durations as decimal strings where the operation defines them as strings.
- Do not follow redirects, retry connections automatically, or expose remote error bodies.
- Reject non-2xx HTTP, malformed JSON, wrong content type, wrong `protoId`, oversized bodies, and responses from a superseded session or endpoint.
- Keep the session scoped to one origin. A debug origin switch must not reuse the old session.

## Success rules

| Rule | Accepted response |
|---|---|
| Default business success | `code="Success"` or numeric `1` |
| `CODE_OR_NONE` | Default success or `code="UserServiceCommonCodeNone"` |
| `FLAG_OR_CODE` | Default success or `isSuccessful=true` |
| `CREATE_POST` | `code="SuccessResult"`, `code="RepeatedSuccess"`, or documented numeric success |
| `ENVELOPE` | Valid envelope only; no business `code` required |
| `BOOLEAN` | Documented boolean success field |

Apply the operation-specific rule; never treat any HTTP 200 as business success. The existing contract has operation-specific exceptions for profile, gift catalogue, post creation, avatar upload, and account deletion.

## Operations

### Identity and profile

| Operation | ID | Request body | Important response / rule |
|---|---:|---|---|
| Fast login | 4198 | `deviceId` | User JWT, `userId`, and test identity credentials; unauthenticated |
| Refresh session | 4088 | none | New token/user state |
| Read profile | 4284 | `userId: string` | `userInfo`; `CODE_OR_NONE` |
| Update profile | 4200 | `username`, `age`, `bio`, `profession`, `location.city` | Re-read the profile after write |
| Upload avatar | 4006 | `userId`, `uploadAvatar.name/file` | `isSuccessful=true` or business success; message may contain the URL |
| Delete account | 4008 | `userId` | `FLAG_OR_CODE`; destructive |

### Discovery, relationships, and safety

| Operation | ID | Request body | Important response / rule |
|---|---:|---|---|
| Discover | 4280 | `limit`, `filter.minAge`, `filter.maxAge` | `userInfos` |
| Likes received | 4296 | `limit`, `filter.minAge`, `filter.maxAge` | `userInfos` |
| Visitors | 4512 | none | `visitorInfos[].user`; no server pagination |
| New visitor count | 4514 | `startTime: string` | Count |
| Match likes delta | 4574 | `reqRecordTime: string`, `limit` | `likedUserInfos[].userInfo`, `lastRecordTime` |
| Mark match likes read | 4576 | none | Read cursor |
| Swipe card | 4554 | `userId`, `swipeType`, `viewDuration: string` | Match/result from server; like and dislike have distinct values |
| Like profile | 4518 | `userId` | Re-read relationship state |
| Unlike profile | 4520 | `userId` | Re-read relationship state |
| Blocked users | 4234 | `limit`, `offsetId` | Nested `targetUser` records |
| Block user | 4230 | `targetUserId: string` | Remove both directions where contract says so |
| Unblock user | 4232 | `targetUserId: string` | Re-read list |
| Report user | 4024 | `userId`, `userIdToReport`, `reason`, `comment` | Boolean/business success |

Superlike must have its own wire intent. If the service has no superlike operation, return an explicit unavailable state instead of sending like.

### Feed, posts, and comments

| Operation | ID | Request body | Important response / rule |
|---|---:|---|---|
| Feed | 19036 | `limit`, `offset: string` | `posts`, `nextOffset` |
| Post detail | 19046 | `postId: string` | Often unavailable in the test service; fall back only to the loaded list item |
| Create post | 19006 | `clientToken`, `content`, `pictures[{name,file}]` | `CREATE_POST` success; stable client token for retry |
| Delete post | 19008 | `postId: string` | Business success; destructive |
| Like post | 19002 | `postId: string` | Read back like state and count |
| Unlike post | 19004 | `postId: string` | Read back like state and count |
| Comments | 19020 | `postId`, `commentIdOffset: string`, `limit` | `comments`, `hasMore`; opaque cursor |
| Create comment | 19000 | `postId`, `content` | Prepend/merge returned record |
| Delete comment | 19026 | `commentId` | Business success; destructive |
| Report post | 19040 | `postId`, `reason` | Boolean/business success |

### Wallet, membership, and gifts

| Operation | ID | Request body | Important response / rule |
|---|---:|---|---|
| Subscriptions | 4258 | none | Current membership |
| Subscription catalogue | 4260 | none | Live catalogue only; catalogue is not purchase readiness |
| Reward token balance | 4118 | none | Reward tokens, distinct from coins |
| Coin balance | 4340 | none | `coin` is a string; distinct from reward tokens |
| Coin products | 4344 | none | `ENVELOPE`; catalogue only |
| Gift catalogue | 4354 | none | `CODE_OR_NONE`; catalogue is not delivery readiness |
| Send gift | 4356 | `giftId`, `toUserId` | Atomic balance/eligibility result; not delivery |

### Known unavailable operations

| Capability | Situation | Required client state |
|---|---|---|
| User-scoped chat | Test provider rejects ordinary user credentials; administrator credentials cannot ship | Explicit messaging-unavailable state |
| Email registration/recovery/verification | No user-scoped test endpoints | Hide/disable until available |
| Follow/unfollow/relationship list | Test routes return 404 | Do not fabricate a relationship graph |
| Post detail | Test route returns 404 | Use loaded feed item without inventing fields |
| In-app notifications/push | No event or push-token binding service | Explicit pending state; device ID is not a push token |
| Google Play purchase verification/restore | No verification service | Show catalogue, disable purchase/restore |
| Call signalling | No deployed signalling service | Explicit pending state |
| Gift delivery through chat | Chat gateway missing | Do not mark delivery after a wallet debit |

## Operation-specific failure handling

- `401` or `403`: clear the session only for a real unauthorized response or session-boundary failure. A failed deletion-password confirmation must not sign out.
- `409`: treat as a duplicate/conflict or ambiguous state; retain the request key and reconcile.
- `429` and `503`: show retryable unavailable/error state; do not fabricate success.
- Network loss after submission: keep the draft and request identity, then reconcile before resubmitting.
- Remote error bodies: do not display them. Map to safe product copy and keep the code for diagnostics.

## Local `/v2` development service

Use this only for loopback development and failure testing. It is not a fallback for the test business gateway.

```text
python3 -m gateway.product_server --local-chat --local-calls --port 8787
```

The listener is loopback-only. Debug builds may use loopback HTTP through the platform's port forwarding; release builds require HTTPS. All routes except capabilities, registration, login, and password-reset request/completion require `Authorization: Bearer <product session>`.

Key route groups:

| Group | Routes |
|---|---|
| Capabilities and auth | `GET /v2/capabilities`; `POST /v2/auth/register`, `/login`, `/refresh`, `/logout` |
| Profile and preferences | own profile, preferences, discovery filters, avatar/media |
| Discovery and relationships | discover, likes, visitors, blocks, reports, profile likes |
| Feed | list, detail, create/delete, like/unlike, comments |
| Conversations | list, thread, messages, read cursor, media |
| Wallet and commerce | wallet, purchases, restore, gift catalogue/send |
| Notifications | list, unread count, mark read, device registration |
| Calls | create, incoming, accept/reject/end, offer/answer/candidate signals |

The local service separates submission `pending`, `accepted`, `unknown`, and `rejected`. A local `stored` or `accepted` state is not provider delivery or remote read. Local purchases and entitlements are development-only. The local outbox is not a production message transport.
