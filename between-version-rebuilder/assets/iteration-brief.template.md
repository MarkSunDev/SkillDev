# Between rebuild brief

## Product

**User:** [Who this release serves]

**Promise:** [One sentence]

**Primary destination:** Chats

**Five destinations:** Chats · Contacts · Feed · Private-AI · You

**Release scope:** [1.1 / 1.2]

**Non-goals:** [Explicit omissions]

**Truth notes:** [PRD versus shipped behavior differences]

## Differentiation

**Target stack:** [Native iOS / Flutter / React Native / KMP / other]

**Architecture:** [Layers and state ownership]

**Visual scene:** [One sentence]

**Anti-references:** [What this must not look like]

**Palette roles:** [Canvas / surface / ink / secondary / accent / state]

**Type roles:** [Display / title / body / detail / caption]

**Composition:** [Grid, insets, density, media rules]

**Motion:** [State transitions and Reduce Motion]

**Originality statement:** [Why this is not a port or reskin]

## 1.0 baseline

**Source:** [Commit, archive hash or installed build]

**Screens:** [Inventory]

**Local data:** [Storage, encryption, migration]

**Guest samples:** [Names and lifecycle]

**Private-AI:** [Consent, windows, tools, receipts]

**Preserved:** [Behaviors that carry forward]

**Replaced:** [Behaviors intentionally rewritten]

**Retired:** [Behaviors removed and why]

## Version matrix

| ID | Requirement | 1.1 status | 1.2 status | Evidence |
| --- | --- | --- | --- | --- |
| V11-01 | Five tabs | | | |
| V11-03 | Apple fallback to FastLogin | | | |
| V11-15 | Durable message draft UUID | | | |
| V11-38 | Greeting failure preserves draft | | | |
| V11-62 | Memory window agreement rules | | | |
| V11-73 | 0 B receipt | | | |
| V12-10 | Combined PYMK sources | | | |
| V12-32 | Live typing state | | | |
| V12-46 | Server-verified purchase | | | |
| V12-62 | Five-minute text quota | | | |

Add every applicable row from `references/version-matrix.md`.

## Backend

**Business endpoint:** `https://api-prod.randomanimestore.com`

**Tenant:** `romi`

**Messaging gateway:** [HTTPS origin or blocked]

**Live TCP:** `prod-tcp.randomanimestore.com:8000`

**Package identity:** [Target app's own identifier]

**StoreKit products:** [IDs or blocked]

**Unresolved configuration:** [List]

## Evidence

**Contract tests:** [Paths / counts]

**Domain tests:** [Paths / counts]

**UI tests:** [Paths / counts]

**Release build:** [Path]

**Live read-only:** [Result bundle]

**Live writes:** [Owned QA identities and result]

**Screenshots:** [Paths]

**Originality audit:** [Path]

**Known failures:** [Exact failures, not summaries that hide them]
