# Version matrix

This is the parity contract for a rebuild. Add a status and evidence link to every row in the target repository. `Shipped` means the behavior exists in the reference release; it does not mean every live backend dependency is deployed.

## Release ladder

| Release | Product position | Core addition | Design position |
| --- | --- | --- | --- |
| 1.0 | Familiar local messenger with a per-chat Private-AI | Local chats, samples, memory window, consent, privacy, reminders | Native, restrained, four tabs |
| 1.1 | Everyday social messenger connected to Romi | Accounts, Chats, Contacts, Feed, Private-AI, moderation, guest mode, five tabs | Lighter social surface; reference used forest/teal, off-white and mint |
| 1.2 | Chat-first, commercially complete release | PYMK filters, compact Feed, chat polish, monetization, visitors, quota, typing, intimacy, photos | Mature editorial surface; reference used wine, paper and citron |

## 1.0 baseline

| ID | Requirement | Status source |
| --- | --- | --- |
| B-01 | Chats, Private-AI, Privacy, You are reachable; Chats is primary. | Reference 1.0 |
| B-02 | Onboarding explains Private-AI consent, memory window and privacy. | Reference 1.0 |
| B-03 | Guest mode can use the Maria, Henderson Crew, Terrence and Mom sample conversations. | Shipped |
| B-04 | Sample edits persist across launches; deleted samples are not recreated. | Shipped |
| B-05 | Account workspace and guest workspace are separate. | Shipped |
| B-06 | Private-AI is off, waiting, active or paused per conversation. | Shipped |
| B-07 | Everyone must agree before Private-AI becomes active. | Shipped |
| B-08 | Memory window is 7 days, 30 days or Everything; shortening is immediate, lengthening waits for agreement. | Shipped |
| B-09 | Removing Private-AI clears its local memory, phrases, stickers and private answers. | Shipped |
| B-10 | Catch up, Find it, Remind, phrase learning, rewrite and quiet nudge work locally. | Shipped |
| B-11 | Every Private-AI answer shows `On this phone · 0 B sent`. | Shipped |
| B-12 | Reminders schedule local notifications and survive relaunch. | Shipped |
| B-13 | Text size, appearance, blocked people, account deletion and privacy copy exist. | Shipped |

The rebuild may replace the 1.0 presentation completely, but these observable behaviors remain the starting point.

## 1.1 release

### Shell and onboarding

| ID | Requirement |
| --- | --- |
| V11-01 | Five tabs: Chats, Contacts, Feed, Private-AI, You. Chats is the default after sign-in and after returning from logout. |
| V11-02 | First run: welcome pages, then account choice. `Continue with Apple` is the primary action, followed by linked Terms and Privacy Policy; `Explore as guest` is secondary. |
| V11-03 | Apple failure, cancellation or invalid credential falls back to device FastLogin without Apple profile details. Only a failed FastLogin shows a sign-in error. |
| V11-04 | New accounts complete name, age, gender and bio before social APIs are available. |
| V11-05 | Guest mode uses only the sample workspace. Signing in switches to the account workspace without merging data. |
| V11-06 | Logout returns to account choice without replaying onboarding. |
| V11-07 | Session restore validates the saved scope, refreshes on the server schedule, and clears invalid sessions. |
| V11-08 | After account switch, late results from the previous account are ignored. |

### Chats

| ID | Requirement |
| --- | --- |
| V11-10 | List shows peer name, latest visible message, timestamp, unread count and supported state badges. Sort pinned first, then last activity. |
| V11-11 | Only the most recently active unread conversation gets a red count badge; other unread counts use the accent color. Do not repeat unread dots or AI locks. |
| V11-12 | Chat rows are at least 68 points tall, with 44-point avatars and one preview line. |
| V11-13 | Opening a chat loads history; older history is paginated; a failed page is retryable. |
| V11-14 | Foreground polling: conversation list about every 8 seconds; open thread about every 4 seconds. Refresh on foreground. |
| V11-15 | Send text with a durable draft UUID. Show sending, sent and failed. Retrying reuses the draft UUID. |
| V11-16 | Merge remote messages by server message ID or original draft UUID. Never deduplicate by text or timestamp alone. |
| V11-17 | `Sent` means accepted, not delivered or read. Read receipts are not fabricated. |
| V11-18 | Mark-read uses a server timestamp. Update unread only after server success. |
| V11-19 | Blocked conversations render as blocked and cannot send. |
| V11-20 | Back navigation may show the unread total for other unblocked chats, hidden at zero, capped at 99+. |
| V11-21 | Unknown or malformed messages fail closed; pure control events are filtered without losing pagination cursors. |

### Contacts and discovery

| ID | Requirement |
| --- | --- |
| V11-30 | Contacts has two top tabs: People You May Know and My Friends. PYMK is the default. |
| V11-31 | PYMK is a compact single-column list using real account photos, names and a short profile sentence. Never show age in these rows. |
| V11-32 | Default discovery has no filter: Everyone and Any distance. |
| V11-33 | The top-right Filters sheet supports Everyone/Men/Women and Any/10/25/50/100 miles, with Cancel, Apply and Reset. A filled icon and gender badge indicate active filters. |
| V11-34 | A dismissible first-use tip opens the real Filters sheet and stays dismissed. |
| V11-35 | Filters and filter state reset when the account changes. |
| V11-36 | Profile detail shows real account details, photo, age where supplied, city/distance/profession/interests, and a visible message action. |
| V11-37 | Message action opens or creates a chat and does not auto-send. Wave is a distinct action and never appears as a chat message. |
| V11-38 | Greeting sends only after explicit submission; failure preserves the draft and offers retry. |
| V11-39 | My Friends is alphabetical and uses real contact data. Empty, error and loading are distinct. |
| V11-40 | Find by user ID validates a positive numeric ID different from self and does not format it with locale separators. |
| V11-41 | Never fabricate mutual contacts, shared interests, address-book matches or male profiles. |

### Feed

| ID | Requirement |
| --- | --- |
| V11-50 | Feed lists real posts with author, avatar, text, photos, timestamp, like state and count. |
| V11-51 | Pagination preserves the server cursor even when blocked or moderated posts are removed. |
| V11-52 | Publish text of 1–2000 characters with a client token; treat `code 2` as still processing, not as a fresh-success invitation to retry. |
| V11-53 | Like and unlike use the server count; optimistic UI is reversible. |
| V11-54 | Own posts can be deleted and verified by read-back. |
| V11-55 | Posts can be reported; report reasons stay within the backend range. |
| V11-56 | Photos open full-size. Media previews stay thumbnail-sized in the list. |
| V11-57 | Read-only feed requests may retry on 429; writes never retry automatically. |

### Private-AI

| ID | Requirement |
| --- | --- |
| V11-60 | Private-AI remains local and per-conversation. It has no networking dependency. |
| V11-61 | Consent states: off, waiting, active, paused. Only active chats have shared memory. |
| V11-62 | Memory windows: 7 days, 30 days, Everything. Shortening purges immediately. Lengthening sends a request that waits for the other participant's agreement. |
| V11-63 | Purge removes embeddings/index entries and phrase statistics outside the window; counts reflect real rows. |
| V11-64 | Catch up returns the latest distinct incoming messages as 3–5 short bullets or excerpts, never invented content. |
| V11-65 | Find it returns matching excerpts with sender and date; results come only from this chat's allowed memory. Tapping a result jumps to the message where the platform supports it. |
| V11-66 | Remind parses a time, creates a shared reminder and schedules a local notification; wording uses learned phrases when available. |
| V11-67 | Phrase learning is shared and deterministic. Both participants see the same list. Forget removes and suppresses relearning; pin survives window purge. |
| V11-68 | Quiet nudge appears at most once per draft, only for an eligible phrase, and never blocks sending. |
| V11-69 | Say it our way rewrites the draft only; accepting replaces the draft and undo restores it. Draft rewrites never enter shared chat or the shared ledger. |
| V11-70 | Stickers are local and derived from learned phrases; they never imply a generative image service. |
| V11-71 | Removing Private-AI clears memory, private answers, phrases and stickers; shared messages remain. |
| V11-72 | A new device or lost key pauses Private-AI and asks for agreement again. Never show an active lock without the state to support it. |
| V11-73 | Every answer shows `On this phone · 0 B sent`. Expanding may show model/tools, window, duration and bytes. |

### Privacy, You and account

| ID | Requirement |
| --- | --- |
| V11-80 | Privacy surfaces describe the actual transport and local AI boundary. Do not call server-hosted messages end-to-end encrypted. |
| V11-81 | Check it yourself explains Airplane Mode and runs a local-only task when the device is offline. If no local model exists, say what actually happens. |
| V11-82 | Blocked users: paginated remote list, remote unblock, local-only conversations remain local. An acknowledged block is not discarded because a stale list omits it. |
| V11-83 | Report/block paths exist from chat and profile. Report writes require server success; do not show a successful report from local state alone. |
| V11-84 | Account deletion is confirmed, server-backed and clears local account state. |
| V11-85 | Profile editing uses a full-profile read, full replacement payload, then read-back verification. Preserve fields the user did not edit. |
| V11-86 | Text size offsets 0/1/2 apply to messages, lists and Private-AI. Appearance follows System, Light or Dark. |
| V11-87 | Avatar source order is `customAvatar.midURL`, `beautifiedAvatar`, `avatarURL`, `customAvatar.url`, `customAvatar.minURL`; profile photo uses profile mid/url/min first, then avatar. Only HTTPS URLs without user/password are accepted. |
| V11-88 | General settings, blocked people, privacy links, delete account and account identity are reachable within two taps from a tab. |

## 1.2 release

Everything in 1.1 remains a regression requirement. 1.2 adds the following.

### Visual and density

| ID | Requirement |
| --- | --- |
| V12-01 | Redesign the surface as a mature chat-first product; preserve all navigation and accessibility semantics. |
| V12-02 | Compact rows: page headings 28 pt, card titles 19 pt, body/chat 15 pt, detail 13 pt, caption 12 pt in the reference. Scale with Dynamic Type. |
| V12-03 | 16-point horizontal page inset; 44-point message avatars, 52-point recommendation avatars, 36-point Feed avatars in the reference. |
| V12-04 | Use readable editorial headings only where they create hierarchy; utility controls keep native typography. |
| V12-05 | Keep the brand film decorative, muted, paused in background, and static under Reduce Motion or Low Power Mode. Never use it as a person recommendation. |
| V12-06 | Support light/dark appearance, accessibility text sizes, 44-point hit areas, and VoiceOver labels for all stateful controls. |

### People You May Know

| ID | Requirement |
| --- | --- |
| V12-10 | Default list combines real discovery sources: suggested profiles (5094) and nearby online male profiles (5108). Expected reference result: about 20 men and 20 women. |
| V12-11 | Interleave the sources instead of letting one bury the other; deduplicate by user ID and exclude self and blocked users. |
| V12-12 | 5094 distances are miles. 5108 distances are kilometers and must be converted to miles. Zero, negative, non-finite or missing distance is unknown. |
| V12-13 | A distance filter excludes unknown distances. Gender filter uses the real profile gender, never a guessed value. |
| V12-14 | Men uses 5108 plus eligible 5094 results; Women uses 5094; Everyone uses both. Do not route Men through the eligibility-gated 4492 source. |
| V12-15 | Reset filters on account switch. |
| V12-16 | Profiles open to a real detail page; send/continue chat remains the primary action. |

### Feed

| ID | Requirement |
| --- | --- |
| V12-20 | Feed is lighter than 1.1: compact post cards and image previews, with full-size viewing on tap. |
| V12-21 | Keep Everyone/My posts switching fixed above content. |
| V12-22 | Author, image, like and menu controls remain legible at large text sizes and in dark mode. |

### Chat polish

| ID | Requirement |
| --- | --- |
| V12-30 | Incoming avatar is a 32-point visual inside a 44-point target and opens the peer profile; returning restores the thread. |
| V12-31 | Back control shows other unblocked-chat unread total, hidden at zero, capped at 99+, excluding the open chat. |
| V12-32 | Typing indicator is a three-dot incoming bubble driven by live TCP events; supports Reduce Motion and VoiceOver; clears on reply, stop, timeout, disconnect, leaving, backgrounding, blocking or account reset. Never synthesize typing from your own send. |
| V12-33 | Relationship/intimacy reads real score, threshold, order, status and cooldown. Statuses: locked, unlocked, processing, completed, cooldown. |
| V12-34 | Contact exchange: query condition, create order, save own card, read supported platforms and exchanged cards. Only a completed exchange unlocks the peer card for the exchanged platform. |
| V12-35 | Photo messages use the system picker, downsample to at most 1600 px, strip metadata, upload under 1 MiB, and send with a durable client UUID. |
| V12-36 | Retry of a photo or exchange send preserves the original UUID and never duplicates an accepted send. |
| V12-37 | Messages, photos, GIFs and contact events remain backward-compatible with older saved messages. |

### Monetization

| ID | Requirement |
| --- | --- |
| V12-40 | You exposes membership, visitor subscription and coins. |
| V12-41 | Load membership (4258), visitor subscription (4536), catalog (4538), balance (4340), coin packages (4344), coin history (4376), message/call rates (4466) and visitors (4512) from the server. |
| V12-42 | Server catalog is the routing authority. Do not infer a product kind from its title. Price comes from StoreKit `displayPrice`; never render a server USD string or infer price from a product name. |
| V12-43 | Coin first-charge bonus is extra coins, not the final total. A returning buyer receives no first-charge bonus. |
| V12-44 | Coin history direction comes from `changeType`, never the sign of a positive magnitude. Unknown types render as neutral activity and handle `Int64.min`. |
| V12-45 | Rates display text per message, audio/video per minute and Super Like per use. No local price fallback and no local coin deduction. |
| V12-46 | Purchase flow: StoreKit 2, local verification, server verification, then `finish()`. No client-side entitlement or coin grant. |
| V12-47 | Verify membership, visitor and coin transactions on the correct endpoints (4256, 4540, 4342). Bind `appAccountToken` to the server environment and business account namespace, not Apple ID or device. |
| V12-48 | Handle success, cancel, pending, failure, restore, revoked, expired, upgraded and unfinished transactions. Reject local `.xcode` transactions against the live service. |
| V12-49 | On HTTP 401, clear the session and all commerce state. Late purchase results cannot cross accounts. |
| V12-50 | Visitors: full snapshot, sort by server milliseconds descending, deduplicate by user, filter minors, invalid users, self and blocked users. Non-members see at most 15 locked entries; visitors subscription unlocks real names and profiles. |
| V12-51 | Billing rejection (HTTP 402 / business rejection) shows a top-up entry. Never auto-resend the message after purchase. |

### Chat quota and prompts

| ID | Requirement |
| --- | --- |
| V12-60 | Track alternating conversation rounds per peer with message-ID deduplication. History pages establish a baseline; only new polled messages and acknowledged local sends count. |
| V12-61 | For a male non-member at 10 rounds, show one subscription prompt per conversation. The user's current message is still sent; do not auto-resend. |
| V12-62 | For a non-member, 15 successful text sends in the same conversation within five minutes clears free-text entitlement with 4484 kind 4. Failed drafts, retries with the same ID and history reads do not count. |
| V12-63 | Persist quota state per environment and account. Mark synchronization complete only after `code=1`. A failed sync does not turn sent messages into failures. |
| V12-64 | Unknown membership or gender never triggers a commercial gate. A pending sync may be retried on refresh, foreground or an explicit retry action; the HTTP write itself does not retry automatically. |

### Commerce and account lifecycle

| ID | Requirement |
| --- | --- |
| V12-70 | Membership access requires the authoritative subscription/account response, not a locally calculated expiry. |
| V12-71 | Restore purchases and manage-subscription links use the normal StoreKit flow and the same server verification gate. |
| V12-72 | An entitlement or balance refresh failure is visible and retryable; it never becomes zero-value truth that removes paid access. |
| V12-73 | Commerce state is account-scoped and cleared on logout. |

## Shipped gaps that must remain honest

These were not delivered in the reference. A rebuild may include them only with new infrastructure and new evidence; otherwise show them as unavailable or omit them.

| Gap | Consequence |
| --- | --- |
| Production messaging gateway deployment | The client needs `ROMI_MESSAGING_ENDPOINT`; do not ship localhost. |
| Background push and sender read receipts | Foreground polling is not push. `Sent` is not `Read`. |
| Real video signaling/media/billing | The reference only reads and writes call authorization switches. |
| Apple sandbox purchase-to-server verification | Reference tests covered protobuf routes and read-only commerce, not a completed sandbox purchase lifecycle. |
| 5070 related contacts | The reference sometimes returned a successful empty list. Do not substitute local contacts. |
| 4234 block-list consistency | A successful block can be enforced while the list omits the user. Preserve acknowledged blocks and offer real unblock recovery. |
| MLS, key shares, ledger, Match Check, sealed messages | Not shipped. Do not display their claims as working mechanisms. |
| On-device generative model, Image Playground stickers, translate | Not shipped. Local extractive tools and symbol stickers are the shipped behavior. |
