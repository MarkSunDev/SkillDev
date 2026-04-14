---
name: mobile-code-review
description: Use when reviewing Flutter, Android, or iOS code — before merging PRs, after implementing UI components or native integrations, or when user asks to review mobile client code for security, performance, memory, or architecture issues.
---

# Mobile Code Review

Structured code review for mobile clients (Flutter / Android / iOS) covering security, UI performance, memory lifecycle, and architecture.

## When to Use

- User says "review this code", "code review", "review mobile code"
- Before merging a PR for client-side features
- After implementing a major UI component or native integration
- Assessing code for security vulnerabilities, memory leaks, or performance regressions

**Not for:**
- Backend-only changes with no mobile client code
- Simple text or asset-only changes

## Core Pattern

Review in priority order — fix CRITICAL first, then HIGH:

| Category | Key Checks |
|---|---|
| **Security** | Hardcoded secrets, insecure storage, exported components, cleartext traffic |
| **Memory & Lifecycle** | Undisposed controllers/streams, retain cycles, async on unmounted widget |
| **UI Performance** | Main thread blocking, missing `const`, un-recycled lists, heavy `build()` |
| **Architecture** | UI/logic separation, platform channel type safety, async SDK init |
| **Maintainability** | State management pattern, code duplication, error handling coverage |

**Severity levels:**

| Level | Meaning | Action |
|---|---|---|
| CRITICAL | Security vuln or guaranteed crash / OOM | Block — fix before merge |
| HIGH | Severe memory leak, ANR / jank risk | Warn — fix before merge |
| MEDIUM | State smell, missing `const`, minor arch issue | Info — fix when possible |
| LOW | Style / naming | Note — optional |

## Implementation

1. Run `git diff` — identify changed files
2. Classify each file by platform: Dart · Kotlin/Java · Swift/ObjC
3. Apply the checklist below per file
4. Report every issue as `file:line` with a concrete, platform-specific fix

### Review Checklist

**Mobile Security**
- [ ] No hardcoded secrets (use `.env` or secure build configs)
- [ ] Sensitive data uses `EncryptedSharedPreferences` / Keychain
- [ ] Android `exported` components reviewed for unintended exposure
- [ ] HTTPS enforced; cleartext traffic disabled

**Memory & Lifecycle**
- [ ] All streams, subscriptions, and controllers disposed / canceled
- [ ] No retain cycles (iOS) or anonymous inner class leaks (Android)
- [ ] Async UI updates check `mounted` / `isFinishing` before `setState`
- [ ] No `Context` passed to long-lived background threads

**UI Performance**
- [ ] `const` constructors used throughout Flutter widgets
- [ ] Heavy work (JSON parsing, file I/O) offloaded to Isolates / background threads
- [ ] Lists use `ListView.builder` / `RecyclerView` — no unbounded column rendering
- [ ] `build()` scope minimized; deep widget trees flattened

**Architecture & Integrations**
- [ ] Business logic decoupled from UI widgets
- [ ] Platform channels handle type errors and missing method exceptions
- [ ] Third-party SDKs (Ads, Analytics) initialized async, not blocking main thread
- [ ] Network / parse errors have fallback UI

## Output Format

```
# MOBILE CODE REVIEW REPORT
Files Reviewed: N   Total Issues: N

## CRITICAL (N)
1. path/to/file.ext:LINE
   Issue: <description>
   Risk:  <impact>
   Fix:   <concrete suggestion with platform syntax>

## HIGH (N)
...

## MEDIUM (N)
...

## LOW (N)
...

RECOMMENDATION: APPROVE | REQUEST CHANGES | COMMENT
<one-line rationale>
```

**Approval criteria:**
- **APPROVE** — No CRITICAL or HIGH issues
- **REQUEST CHANGES** — Any CRITICAL or HIGH issue present
- **COMMENT** — Only LOW / MEDIUM issues, no blockers

## Common Mistakes

| Mistake | Fix |
|---|---|
| Reviewing all files equally | Prioritize files touching security or lifecycle first |
| Reporting MEDIUM before CRITICAL | Always sort issues by severity descending |
| Generic fix suggestions ("add null check") | Provide exact `file:line` with platform-specific syntax |
| Blocking review on external tools | Complete review independently first; external validation is optional |
| Flagging iOS-only issues on Android files | Confirm platform context before citing platform-specific APIs |
