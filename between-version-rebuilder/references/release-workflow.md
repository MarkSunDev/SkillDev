# Release workflow

## Release gates

A release is not complete until all four gates are green or explicitly blocked with evidence.

| Gate | Required evidence |
| --- | --- |
| Contract | Fixed request/response bytes, IDs, headers, status mapping and protobuf decode tests |
| Domain | Account isolation, state machines, pagination, deduplication, quota, commerce and local Private-AI tests |
| Product | Installed-build UI flows for onboarding, five tabs, chat, discovery, Feed, Private-AI, settings and commerce states |
| Originality | Automated audit plus manual source/screen/asset review |

## Build order

1. contract codec and transport;
2. session, secure storage and account namespace;
3. 1.1 onboarding, account choice and guest mode;
4. 1.1 social read surfaces;
5. 1.1 write paths and reconciliation;
6. 1.1 Private-AI and privacy;
7. 1.1 release evidence;
8. 1.2 visual redesign and density;
9. 1.2 discovery, Feed and chat enhancements;
10. 1.2 commerce and quota;
11. full regression, originality audit and release package.

Do not build screens against fixtures and call the feature done. Use fixtures only for deterministic UI states, clearly debug-only.

## Test layers

### Unit

- protobuf framing and golden bytes;
- response-ID validation, size bounds and malformed payload rejection;
- response code rules, unknown enums and missing fields;
- token scope, refresh schedule and invalid-session behavior;
- account namespace and late-response discard;
- message merge by server ID or draft UUID;
- distance conversion, filter boundaries and unknown distance;
- unread aggregation, overflow and exclusion;
- quota round counting, message-ID deduplication, five-minute window and persisted sync state;
- commerce catalog validation, first-charge bonus, history direction and `Int64.min`;
- Private-AI consent, memory windows, purge counts, phrase learning, nudge limit and removal.

### Integration

- authenticated real read-only profile/config;
- conversation list, history and peer summary;
- feed pagination and own-post read-back;
- discovery source combination and real gender validation;
- moderation pagination and acknowledged-block reconciliation;
- commerce read-only membership, visitor, catalog, balance, rates, history and visitors;
- live typing heartbeat, frame splitting/coalescing, stop and expiry;
- optional writes using owned QA identities only.

Never use a production account for a write test without a clean-up plan. Never put administrator credentials in the client.

### UI

- first-run onboarding and account choice;
- guest samples, sign-in, session restore, logout;
- Chats list, history, send, failure and retry;
- contacts tabs, filters, profile, wave and greeting;
- Feed list, publish, like, delete, report and full-size photo;
- Private-AI add, agree, change window, catch up, find, remind, phrase forget/pin, remove;
- Privacy/You, text size, appearance, blocked users, delete account;
- 1.2 typing, relationship, exchange, photo message, unread badge;
- commerce: available, unavailable, pending, cancel, failure, restore;
- visitor locked and unlocked states;
- accessibility sizes, dark mode, Reduce Motion and VoiceOver labels.

### Live evidence

Record exact commands, pass/fail counts, build artifacts and result bundles. A screenshot is not evidence of a write. A read-only probe is not evidence of a write. A successful HTTP call is not evidence of delivery or entitlement.

## VERSION-MATRIX.md status

Use one status per row:

| Status | Meaning |
| --- | --- |
| `verified` | Test, live probe or inspected build proves the behavior |
| `partial` | Some path works; name the missing subpath |
| `blocked` | External dependency or missing configuration; name it |
| `not-started` | No implementation |
| `not-in-scope` | Deliberately omitted; name the replacement or consequence |

Every `verified` row needs an evidence link or command. Every `partial` and `blocked` row needs a concrete reason.

## Build artifacts

For iOS/native:

- Debug and Release build logs;
- `.xcresult` or equivalent UI result bundles;
- signed or simulator build as applicable;
- screenshots from the installed build.

For Flutter/React Native/KMP:

- release-mode build log;
- platform integration test results;
- device or simulator screenshots;
- proof that secure storage, billing, media and accessibility use real platform adapters.

## App Store package

Use `$app-store-prd-metadata` when available. Otherwise produce:

- app information table with character and byte counts;
- English review notes under 300 words;
- five real screenshots at 1290 × 2796;
- what's new;
- demo path and credentials, if safe;
- privacy policy and terms drafts if requested;
- a short screen recording of the signature action.

### 1.1 listing facts

- Name: Between: Chat & Private-AI
- Subtitle: Good things start with hello
- Promise: messages, new people and everyday moments; Private-AI one conversation at a time.
- Five images: Hello, Conversation, Meet people, Everyday Feed, Private-AI.

### 1.2 listing facts

- Name: Between: Chat & Private-AI
- Subtitle: Less noise. More conversation.
- Promise: a simpler inbox, People You May Know, a lighter Feed and Private-AI inside the chat.
- Five images: Chats first, People You May Know, Life lately, Private-AI, Your space.

Do not reuse the reference screenshot files in a differentiated rebuild. Recreate the screenshots from the candidate build.

## Release note template

```text
Release: 1.x
Build: <build number>
Stack: <stack>
Design direction: <one sentence>
Backend: <endpoint / tenant / gateway>
Verified: <count> checks
Blocked: <count> checks
Known gaps: <short list>
Evidence: <paths or links>
Originality audit: <path>
```

## Claim discipline

Never write “works end to end” when only read-only or fixture evidence exists. State exactly what was tested:

- “read-only production profile fetch verified”;
- “real gateway round trip with owned QA accounts verified”;
- “StoreKit route fixtures verified; sandbox purchase not run”;
- “settings read/write verified; media call not implemented”.

This is not hedging. It is the difference between evidence and fiction.
