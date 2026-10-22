# Source of truth

## Product sources

| Source | What it establishes | How to use it |
| --- | --- | --- |
| Final PRD: https://presence.feishu.cn/wiki/XtbYwfkJiiu4DekquUjcpCAqn5c | Product promise, screen intent, visual constraints, privacy claims, acceptance ideas | Product intent. Not proof that a mechanism shipped. |
| PRD document token `AW26dDoYboMwD1xrU7VcbK1jnIg`, fetched revision 193 on 2026-10-19 | Current PRD snapshot, including embedded requirement sheets | Re-fetch before a major rebuild; revisions change. |
| `docs/PRD-source.txt` in the reference repository (revision 23) | Older local extract | Historical only. Do not use as the current full PRD. |
| Shipped 1.1 and 1.2 behavior | Exact release parity | Primary authority for the rebuild. |
| `Protocols/*.proto` | Exact protobuf fields and message IDs | Copy these definitions; reimplement the codec in the target stack. |
| `docs/v1.1-romi-plan.md` | 1.1 implementation order, live results, failures | Evidence and edge-case oracle. |
| `docs/v1.2-monetization-plan.md` | 1.2 commercial and chat behavior, live results, failures | Evidence and edge-case oracle. |
| `PRODUCT.md` and `DESIGN.md` in the reference repository | Final shipped product and design language | Read for intent; do not copy the visual system into a differentiated rebuild. |

## Reference repository

The reference implementation is `/Users/maxzhou/Dev/Between` when present. Treat it as read-only.

Useful baselines:

| Release | Git reference | Note |
| --- | --- | --- |
| 1.0 | `origin/yxh/1.0.0` / `a94ce5b` | Four-tab local app. Guest samples and local Private-AI rules. |
| 1.1 visual baseline | `main` / `62b4185` | Five-tab shell, refreshed onboarding and product shots. Service work is documented rather than cleanly separated in Git. |
| 1.2 integration baseline | `feature/v1.2-monetization` / `80b1ad9` | Backend, commercial, chat-enhancement and visual work collapsed into one integration commit. |

The branch history is not a clean version boundary. Use the shipped behavior, plan documents and tests, not commit order alone.

## PRD intent versus shipped behavior

The PRD describes an ambitious MLS-based, two-key, on-device-model product. The shipped 1.1/1.2 app is different in several important ways. A parity rebuild must follow the shipped behavior unless the user explicitly asks for the full PRD architecture and supplies the missing infrastructure.

| Area | PRD intent | Shipped 1.1/1.2 |
| --- | --- | --- |
| Tabs | Four: Chats, Private-AI, Privacy, You | Five: Chats, Contacts, Feed, Private-AI, You. Privacy lives under You and in privacy surfaces. |
| Message transport | MLS groups, relay, sealed sender | Romi HTTP/protobuf plus a user-authenticated messaging gateway over Tencent; no HRU/TIM SDK in the client. |
| Private-AI | On-device generative model, two-key key split, ledger, Match Check | Local extractive tools over the selected memory window. No network and no generative model. Consent and memory-window states exist. The two-key lock is a visual metaphor, not shipped cryptography. |
| Backend | `POST /v1/msg`, `/v1/inbox`, APNs, S3 blobs | Romi business API at `api-prod.randomanimestore.com`, `romi` tenant; messaging gateway configured by `ROMI_MESSAGING_ENDPOINT`; live typing over `prod-tcp.randomanimestore.com:8000`. |
| Monetization | StoreKit `Transaction.currentEntitlements` plus client-side gating | StoreKit 2 plus server-verified Romi membership, visitor subscription and coins. Server truth controls access. |
| Video | Calls described as a product capability | Only authorization setting read/write. No call signaling or media. Never claim a working call. |
| Push | APNs + NSE | Foreground polling; production push gateway not delivered in the reference. |
| Search/backup | FTS5, encrypted backup | Not part of the shipped 1.1/1.2 parity target. Do not invent them. |

## Conflict rule

If the PRD, plan documents and code disagree:

1. use the wire contract and observed shipped behavior for parity;
2. keep the PRD's user promise and plain-language privacy constraints;
3. record the conflict in `VERSION-MATRIX.md` and `VERIFICATION.md`;
4. never turn an unshipped mechanism into a claim.
