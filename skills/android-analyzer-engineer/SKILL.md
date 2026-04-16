---
name: android-analyzer-engineer
description: Use when the user wants to perform a full Android app investigation — combining manifest analysis (permissions, background strategies, ad SDKs) with decompilation and reverse engineering (jadx/Fernflower, call flow tracing, API extraction). Triggers on requests like "analyze this APK", "reverse engineer and report on this Android app", "find all API endpoints in this app", or any task requiring both surface-level manifest inspection and deep source-level analysis.
---

# Android Analyzer & Engineer

A combined workflow that integrates two skills:

- **android-app-analyzer** — Download by package name or analyze a local APK/XAPK; parse `AndroidManifest.xml` for metadata, permissions, background keep-alive strategies, push integrations, and ad SDKs; produce a structured Markdown report.
- **android-reverse-engineering-re** — Decompile APK/XAPK/JAR/AAR with jadx or Fernflower/Vineflower; trace call flows from UI to network; extract and document HTTP API endpoints (Retrofit, OkHttp, Volley).

## When to Use

- Full competitive analysis: manifest surface + decompiled source
- Security research: permissions + actual network calls + auth patterns
- SDK/integration audit: what's declared vs. what actually executes
- User asks for "full analysis", "deep dive", or "reverse engineer and report"

## Decision Guide

| User intent | Recommended path |
|---|---|
| "What permissions / SDKs does this app use?" | Phase 1 only (manifest analysis) |
| "Decompile this APK / find the API endpoints" | Phase 2 only (reverse engineering) |
| "Full analysis" / "everything you can find" | Both phases |

---

## Phase 1 — Manifest Analysis (`android-app-analyzer`)

### 1.1 Acquire the APK

**Option A — Download by package name:**

```bash
python3 ${SKILL_DIR}/android-app-analyzer/apkcombo_download.py <package.name>
```

**Option B — Use a local APK/XAPK:**

```bash
python3 ${SKILL_DIR}/android-app-analyzer/android_analyzer.py path/to/app.apk
```

**Option C — Analyze by package name (download + analyze in one step):**

```bash
python3 ${SKILL_DIR}/android-app-analyzer/android_analyzer.py <package.name>
```

### 1.2 Workspace

The analyzer stores all artifacts under `.cache/android-app-analyzer/<package>/`:

```
downloads/    — APK or XAPK file
extracted/    — Base APK extracted from XAPK
reports/      — *_manifest.xml, *_analysis.md
run.json      — Run metadata
```

Cache guardrails: warn at 5 workspaces, hard stop at 20.

### 1.3 Report Contents

The generated `*_analysis.md` covers:

1. **Basic Information** — package, version, compileSdk, targetSdk, minSdk
2. **Background & Messaging Signals** — boot receiver, FCM, foreground service, exact alarm, WorkManager, sync adapter, overlay
3. **Advertising SDKs** — AdMob (with App ID), AppLovin, IronSource, Unity Ads, Meta, Mintegral, ByteDance/Pangle, and 15+ more
4. **Third-Party Services** — Firebase Analytics/Crashlytics/RC, Adjust, AppsFlyer, Branch, Sentry, ExoPlayer, etc.
5. **Permissions** — system (with `[sensitive]` flag) and custom/third-party
6. **Component Counts** — Activity, Service, Receiver, Provider

---

## Phase 2 — Reverse Engineering (`android-reverse-engineering-re`)

### 2.1 Check & Install Dependencies

```bash
bash ${SKILL_DIR}/android-reverse-engineering-re/scripts/check-deps.sh
```

Required: **Java 17+**, **jadx**
Optional (recommended): **Vineflower/Fernflower**, **dex2jar**

Install missing deps automatically:

```bash
bash ${SKILL_DIR}/android-reverse-engineering-re/scripts/install-dep.sh jadx
bash ${SKILL_DIR}/android-reverse-engineering-re/scripts/install-dep.sh vineflower
bash ${SKILL_DIR}/android-reverse-engineering-re/scripts/install-dep.sh dex2jar
```

### 2.2 Decompile

Use the APK from Phase 1 (or a separately provided file):

```bash
# Default: jadx (APK/XAPK/JAR/AAR)
bash ${SKILL_DIR}/android-reverse-engineering-re/scripts/decompile.sh <file>

# Better Java output on complex code (JAR/AAR preferred)
bash ${SKILL_DIR}/android-reverse-engineering-re/scripts/decompile.sh --engine fernflower <file>

# Side-by-side comparison
bash ${SKILL_DIR}/android-reverse-engineering-re/scripts/decompile.sh --engine both --deobf <file>
```

Engine selection:

| Input | Strategy |
|---|---|
| APK / XAPK | `jadx` first; add `--deobf` if obfuscated |
| JAR / AAR library | `fernflower` |
| jadx output has warnings | `both` — compare per class |

### 2.3 Analyze Structure

After decompilation:

1. Read `<output>/resources/AndroidManifest.xml` — identify launcher Activity, Application class, permissions
2. Survey `<output>/sources/` — find `api`, `network`, `data`, `repository` packages
3. Identify architecture pattern (MVP / MVVM / Clean Architecture)

### 2.4 Trace Call Flows

Follow the execution path from UI to network:

```
Activity.onCreate() → click handler → ViewModel → Repository → ApiService → HTTP
```

Reference: `${SKILL_DIR}/android-reverse-engineering-re/references/call-flow-analysis.md`

### 2.5 Extract & Document APIs

```bash
# Full sweep
bash ${SKILL_DIR}/android-reverse-engineering-re/scripts/find-api-calls.sh <output>/sources/

# Targeted
bash ${SKILL_DIR}/android-reverse-engineering-re/scripts/find-api-calls.sh <output>/sources/ --retrofit
bash ${SKILL_DIR}/android-reverse-engineering-re/scripts/find-api-calls.sh <output>/sources/ --urls
bash ${SKILL_DIR}/android-reverse-engineering-re/scripts/find-api-calls.sh <output>/sources/ --auth
```

Document each endpoint:

```markdown
### `METHOD /path`

- **Source**: `com.example.api.ApiService` (file:line)
- **Base URL**: `https://api.example.com/v1`
- **Path params**: `id` (String)
- **Query params**: `page` (int), `limit` (int)
- **Headers**: `Authorization: Bearer <token>`
- **Request body**: `{ "email": "string", "password": "string" }`
- **Response**: `ApiResponse<User>`
- **Called from**: `LoginActivity → LoginViewModel → UserRepository → ApiService`
```

Reference: `${SKILL_DIR}/android-reverse-engineering-re/references/api-extraction-patterns.md`

---

## Combined Output

Deliver the following at the end of a full analysis:

1. **Manifest Report** (`*_analysis.md`) — permissions, SDKs, background strategies
2. **Decompiled Source** — in the output directory
3. **Architecture Summary** — main packages, pattern used
4. **API Documentation** — all discovered endpoints in the format above
5. **Call Flow Map** — key paths from UI to network (especially auth and core features)
6. **Cross-Reference Findings** — e.g., "AdMob declared in manifest + confirmed in `MobileAds.initialize()` call at `Application.onCreate()`"

## Common Mistakes

| Mistake | Fix |
|---|---|
| Running Phase 2 before Phase 1 | Manifest report is fast and often answers the question without decompilation |
| Using `--engine fernflower` on APK without dex2jar | Install dex2jar first (`install-dep.sh dex2jar`) |
| Cache workspace too large | Clear `.cache/android-app-analyzer/` manually before re-running |
| Reporting obfuscated class names as findings | Use `--deobf` or navigate via string literals and library calls |
| Documenting endpoints without call chain | Always trace back to the Activity/Fragment entry point |
