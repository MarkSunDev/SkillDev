---
name: android-app-analyzer
description: Use when analyzing an Android app by package name or local APK/XAPK to inspect manifest metadata, permissions, background keep-alive strategies, push integrations, and ad SDK usage.
---

# Android App Analyzer

## Overview

This skill analyzes Android application packages and exports a structured Markdown report from `AndroidManifest.xml`. It supports both package-name downloads via `apkeep` and direct analysis of local APK/XAPK files.

## When to Use

- You need a fast view of an Android app's permissions, component counts, and SDK targets.
- You want to inspect boot receivers, foreground services, exact alarms, FCM, or WorkManager usage.
- You need a lightweight check for ad SDKs and common third-party services.
- You only have a package name or an APK/XAPK file and want a reusable report.

## Prerequisites

**apkeep** must be installed and available in PATH:

```bash
# macOS / Linux
brew install apkeep

# Windows — download the prebuilt binary from:
# https://github.com/EFForg/apkeep/releases/latest
# apkeep-x86_64-pc-windows-msvc.exe

# Any platform (requires Rust)
cargo install apkeep
```

## Workspace Rules

The skill always uses a managed cache workspace.

- Default workspace root: `.cache/android-app-analyzer/`
- Package workspace: `.cache/android-app-analyzer/<package-or-input-name>/`
- Subdirectories:
  - `downloads/`
  - `extracted/`
  - `reports/`
  - `temp/`

Cache guardrails:

- More than 5 package workspaces: print a warning and continue.
- More than 20 package workspaces: stop immediately and require manual cleanup before the next run.

The tool will not auto-delete old cache folders in this version. Users must clear old workspaces manually when the cache grows too large.

## Quick Start

```bash
python3 android_analyzer.py com.example.app
python3 android_analyzer.py com.example.app --skip-download
python3 android_analyzer.py path/to/app.apk
```

## Dependency Handling

- `apkeep` handles APK downloads (system binary, must be installed separately).
- Python dependencies (`androguard`, `lxml`) are loaded lazily and installed only when needed.
- If automatic installation fails, the script prints an exact manual install command.
- You can install Python dependencies up front with:

```bash
python3 -m pip install -r requirements.txt
```

## Outputs

Each managed workspace may contain:

- `downloads/*.apk` or `downloads/*.xapk`
- `extracted/<xapk-name>/...`
- `reports/*_manifest.xml`
- `reports/*_analysis.md`
- `run.json`

## Common Mistakes

- `apkeep` is missing: install it via Homebrew, cargo, or download the binary from GitHub releases.
- `python` points to Python 2: use `python3` or `py -3` explicitly.
- The workspace already has too many package folders: clear old cache folders before rerunning.
- An XAPK package does not include a usable base APK: that is usually an upstream package issue.
