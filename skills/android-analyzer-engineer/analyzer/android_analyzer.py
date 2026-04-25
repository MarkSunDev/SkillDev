"""Analyze an Android app by package name: fetch store data, download APK, parse manifest,
and generate a fixed-format Markdown report."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path
import sys
import zipfile
from datetime import datetime

from dependency_bootstrap import DependencyBootstrapError, DependencySpec, ensure_dependencies
from workspace_manager import (
    WorkspaceLimitError,
    create_package_workspace,
    ensure_workspace_capacity,
    resolve_workspace_root,
)

SCRIPT_DIR = Path(__file__).parent.resolve()
APK = None
etree = None


# ---------------------------------------------------------------------------
# Lazy-load heavy analysis deps
# ---------------------------------------------------------------------------

def ensure_analysis_dependencies():
    """Load androguard / lxml only when actually needed."""
    global APK, etree
    if APK is not None and etree is not None:
        return

    ensure_dependencies(
        [
            DependencySpec("androguard"),
            DependencySpec("lxml"),
        ]
    )

    try:
        from loguru import logger as _loguru_logger
        _loguru_logger.disable("androguard")
    except ImportError:
        pass

    from androguard.core.apk import APK as apk_class
    from lxml import etree as etree_module

    APK = apk_class
    etree = etree_module


# ---------------------------------------------------------------------------
# Google Play store data via google-play-scraper (Node.js)
# ---------------------------------------------------------------------------

def fetch_store_info(package_name: str) -> dict | None:
    """Call store_fetcher.js and return parsed JSON, or None on failure."""

    fetcher = SCRIPT_DIR / "store_fetcher.js"
    if not fetcher.exists():
        print(f"  [store] store_fetcher.js not found at {fetcher}")
        return None

    node_bin = shutil.which("node") or shutil.which("nodejs")
    if not node_bin:
        print("  [store] Node.js not found in PATH — skipping store info.")
        return None

    print(f"  [store] Fetching Google Play metadata for {package_name} …")
    try:
        result = subprocess.run(
            [node_bin, str(fetcher), package_name],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        print("  [store] Timed out fetching store info — skipping.")
        return None
    except Exception as exc:
        print(f"  [store] Unexpected error: {exc} — skipping.")
        return None

    if result.returncode != 0:
        stderr_msg = result.stderr.strip().splitlines()[0] if result.stderr.strip() else "(no error output)"
        print(f"  [store] store_fetcher.js failed: {stderr_msg}")
        return None

    try:
        data = json.loads(result.stdout)
        print(f"  [store] OK — {data.get('app_name', package_name)} "
              f"v{data.get('version', '?')} · "
              f"★{data.get('rating', '?')} · "
              f"{data.get('installs', '?')} installs")
        return data
    except json.JSONDecodeError as exc:
        print(f"  [store] Could not parse store_fetcher.js output: {exc} — skipping.")
        return None


# ---------------------------------------------------------------------------
# APK download
# ---------------------------------------------------------------------------

def check_apkeep() -> bool:
    if shutil.which("apkeep"):
        return True
    print("Error: apkeep is not installed or not in PATH.")
    print("Install:  brew install apkeep   |   cargo install apkeep")
    print("          https://github.com/EFForg/apkeep/releases/latest")
    return False


def download_apk(package_name: str, downloads_dir: Path) -> Path:
    """Download the latest APK/XAPK via apkeep (APKPure, no credentials)."""
    print("=" * 60)
    print("Step 1: Download APK")
    print("=" * 60)

    if not check_apkeep():
        sys.exit(1)

    print(f"  [apkeep] Downloading {package_name} from APKPure …")
    result = subprocess.run(
        ["apkeep", "-a", package_name, "-d", "apk-pure", str(downloads_dir)],
        capture_output=False,
    )
    if result.returncode != 0:
        print(f"Error: apkeep exited with code {result.returncode}.")
        sys.exit(1)

    for ext in (".xapk", ".apk"):
        candidate = downloads_dir / f"{package_name}{ext}"
        if candidate.exists():
            print(f"  Downloaded: {candidate}")
            return candidate

    # Fallback: most recently modified file
    candidates = sorted(
        list(downloads_dir.glob("*.apk")) + list(downloads_dir.glob("*.xapk")),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if candidates:
        print(f"  Downloaded: {candidates[0]}")
        return candidates[0]

    print("Error: apkeep succeeded but no APK/XAPK file was found.")
    sys.exit(1)


# ---------------------------------------------------------------------------
# XAPK extraction
# ---------------------------------------------------------------------------

def extract_apk_from_xapk(xapk_path: Path, extracted_root: Path) -> Path | None:
    """Extract the base APK from an XAPK archive."""
    print(f"\n  Processing XAPK: {xapk_path.name}")
    if not zipfile.is_zipfile(xapk_path):
        print("  Error: not a valid ZIP archive.")
        return None

    extract_dir = extracted_root / xapk_path.stem
    extract_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(xapk_path, "r") as archive:
        names = archive.namelist()
        xapk_manifest = None
        if "manifest.json" in names:
            with archive.open("manifest.json") as mf:
                try:
                    xapk_manifest = json.loads(mf.read())
                    print(f"  Package: {xapk_manifest.get('package_name', '')} "
                          f"v{xapk_manifest.get('version_name', '')}")
                except json.JSONDecodeError:
                    xapk_manifest = None

        apk_files = [n for n in names if n.endswith(".apk")]
        target_apk = None
        if xapk_manifest:
            pkg_apk = f"{xapk_manifest.get('package_name', '')}.apk"
            if pkg_apk in apk_files:
                target_apk = pkg_apk
        if not target_apk and "base.apk" in apk_files:
            target_apk = "base.apk"
        if not target_apk and apk_files:
            target_apk = max(apk_files, key=lambda n: archive.getinfo(n).file_size)

        if not target_apk:
            print("  Error: no APK payload found in XAPK.")
            return None

        archive.extract(target_apk, extract_dir)
        extracted_path = extract_dir / target_apk
        print(f"  Extracted: {extracted_path}")
        return extracted_path


# ---------------------------------------------------------------------------
# Manifest parsing
# ---------------------------------------------------------------------------

def parse_apk(apk_path: Path, reports_dir: Path):
    """Parse AndroidManifest.xml; export XML copy; return (info, manifest_text, manifest_file)."""
    ensure_analysis_dependencies()

    try:
        apk = APK(str(apk_path))
    except Exception as exc:
        print(f"  Error: could not parse APK: {exc}")
        return None, None, None

    xml_root = apk.get_android_manifest_xml()
    manifest_xml = etree.tostring(xml_root, pretty_print=True, encoding="unicode")
    manifest_file = reports_dir / f"{apk_path.stem}_manifest.xml"
    manifest_file.write_text(manifest_xml, encoding="utf-8")
    print(f"  Manifest exported: {manifest_file}")

    android_ns = "http://schemas.android.com/apk/res/android"
    info = {
        "package":          apk.get_package() or "",
        "version_code":     apk.get_androidversion_code() or "",
        "version_name":     apk.get_androidversion_name() or "",
        "min_sdk":          apk.get_min_sdk_version() or "",
        "target_sdk":       apk.get_target_sdk_version() or "",
        "compile_sdk":      xml_root.get(
                                f"{{{android_ns}}}compileSdkVersion",
                                xml_root.get("compileSdkVersion", ""),
                            ),
        "application_name": "",
        "permissions":      apk.get_permissions() or [],
        "activities":       apk.get_activities() or [],
        "services":         apk.get_services() or [],
        "receivers":        apk.get_receivers() or [],
        "providers":        apk.get_providers() or [],
        "meta_data":        [],
    }

    app_element = xml_root.find("application")
    if app_element is not None:
        info["application_name"] = app_element.get(f"{{{android_ns}}}name", "")

    for meta in xml_root.iter("meta-data"):
        name = meta.get(f"{{{android_ns}}}name", "")
        value = (meta.get(f"{{{android_ns}}}value", "")
                 or meta.get(f"{{{android_ns}}}resource", ""))
        if name:
            info["meta_data"].append({"name": name, "value": value})

    return info, manifest_xml, manifest_file


# ---------------------------------------------------------------------------
# Manifest analysis
# ---------------------------------------------------------------------------

def analyze_strategies(manifest_text: str, info: dict) -> dict:
    """Detect background keep-alive and scheduling strategies."""
    strategies = {}

    has_sync = "android.content.SyncAdapter" in manifest_text
    strategies["sync_adapter"] = {
        "name": "Sync adapter (keep-alive)",
        "detected": has_sync,
        "details": [s for s in info["services"] if "sync" in s.lower()] if has_sync else [],
        "description": (
            "滥用 Android SyncAdapter 机制绕过 Doze 模式和电池优化。"
            "声明同步适配器会让系统将该应用豁免于待机限制并定期唤醒——"
            "即便用户从未开启任何真实的同步功能。"
        ),
    }

    has_contact_dir = any(
        m["name"] == "android.content.ContactDirectory" for m in info["meta_data"]
    )
    strategies["contact_directory"] = {
        "name": "Contact directory provider (keep-alive)",
        "detected": has_contact_dir,
        "details": [],
        "description": (
            "滥用 ContactDirectory Provider 机制绕过 Doze。"
            "注册联系人目录强迫系统将应用视为持久数据提供者，阻止其进入 App Standby 休眠。"
        ),
    }

    has_boot = "android.permission.RECEIVE_BOOT_COMPLETED" in info["permissions"]
    strategies["boot_completed"] = {
        "name": "Boot completed receiver",
        "detected": has_boot,
        "details": [r for r in info["receivers"] if "boot" in r.lower()],
        "description": "设备重启后自动拉起，恢复后台任务。",
    }

    has_fcm = (
        any("FirebaseMessaging" in s for s in info["services"])
        or any("FirebaseMessagingRegistrar" in m["name"] for m in info["meta_data"])
        or "com.google.firebase.messaging" in manifest_text
    )
    has_firebase_any = any("firebase" in s.lower() for s in info["services"] + info["providers"])
    strategies["fcm"] = {
        "name": "Firebase Cloud Messaging",
        "detected": has_fcm,
        "details": [s for s in info["services"] if "firebase" in s.lower() and "messag" in s.lower()],
        "has_firebase_any": has_firebase_any,
        "description": "通过 FCM 接收服务端推送，实现远程唤醒。",
    }

    has_fsi = "android.permission.USE_FULL_SCREEN_INTENT" in info["permissions"]
    strategies["full_screen_intent"] = {
        "name": "Full-screen intent",
        "detected": has_fsi,
        "details": [],
        "description": "可弹出全屏通知（来电、闹钟等紧急场景）。",
    }

    has_overlay = "android.permission.SYSTEM_ALERT_WINDOW" in info["permissions"]
    strategies["system_alert_window"] = {
        "name": "System alert window",
        "detected": has_overlay,
        "details": [],
        "description": "可在其他应用之上绘制悬浮窗口。",
    }

    has_fg = "android.permission.FOREGROUND_SERVICE" in info["permissions"]
    fg_perms = [p for p in info["permissions"] if p.startswith("android.permission.FOREGROUND_SERVICE_")]
    strategies["foreground_service"] = {
        "name": "Foreground service",
        "detected": has_fg,
        "details": fg_perms,
        "description": "通过前台服务 + 常驻通知保持长期任务运行。",
    }

    has_alarm = (
        "android.permission.SCHEDULE_EXACT_ALARM" in info["permissions"]
        or "android.permission.USE_EXACT_ALARM" in info["permissions"]
    )
    strategies["exact_alarm"] = {
        "name": "Exact alarm",
        "detected": has_alarm,
        "details": [p for p in info["permissions"] if "EXACT_ALARM" in p or "SET_ALARM" in p],
        "description": "使用精确闹钟调度定时任务或时间敏感型唤醒。",
    }

    has_wm = any("androidx.work" in s for s in info["services"])
    strategies["workmanager"] = {
        "name": "WorkManager / JobScheduler",
        "detected": has_wm,
        "details": [s for s in info["services"] if "androidx.work" in s],
        "description": "使用系统托管后台调度（WorkManager / JobScheduler）执行延迟或周期性任务。",
    }

    return strategies


def detect_ad_sdks(info: dict, manifest_text: str) -> dict:
    """Detect advertising SDKs from manifest signals."""
    known_sdks = {
        "Google AdMob":            ["com.google.android.gms.ads"],
        "AppLovin / MAX":          ["com.applovin"],
        "IronSource / LevelPlay":  ["com.ironsource", "LevelPlay"],
        "Unity Ads":               ["com.unity3d.ads", "com.unity3d.services"],
        "Chartboost":              ["com.chartboost"],
        "Mintegral (Mbridge)":     ["com.mbridge"],
        "ByteDance / Pangle":      ["com.bytedance.sdk.openadsdk", "com.pangle"],
        "BigoAds":                 ["sg.bigo.ads"],
        "BidMachine":              ["io.bidmachine"],
        "Vungle / Liftoff":        ["com.vungle"],
        "Meta / Facebook Audience":["com.facebook.ads"],
        "InMobi":                  ["com.inmobi"],
        "Mopub":                   ["com.mopub"],
        "AdColony":                ["com.adcolony"],
        "Tapjoy":                  ["com.tapjoy"],
        "PubMatic":                ["com.pubmatic"],
        "Digital Turbine":         ["com.digitalturbine"],
        "Yandex Ads":              ["com.yandex.mobile.ads"],
        "Amazon Ads":              ["com.amazon.device.ads"],
        "Criteo":                  ["com.criteo"],
        "Smaato":                  ["com.smaato"],
        "Fyber":                   ["com.fyber"],
    }

    all_components = " ".join(
        info["activities"] + info["services"] + info["receivers"] + info["providers"]
    ).lower()
    lowered = manifest_text.lower()

    detected = {}
    for sdk_name, identifiers in known_sdks.items():
        for ident in identifiers:
            if ident.lower() in lowered or ident.lower() in all_components:
                extra = ""
                if sdk_name == "Google AdMob":
                    for m in info["meta_data"]:
                        if m["name"] == "com.google.android.gms.ads.APPLICATION_ID":
                            extra = m["value"]
                            break
                detected[sdk_name] = extra
                break

    return detected


def detect_third_party_services(info: dict, manifest_text: str) -> list:
    """Detect non-advertising third-party SDKs from manifest signals."""
    known = {
        "Firebase Analytics":     ["com.google.firebase.analytics", "AppMeasurement"],
        "Firebase Installations": ["FirebaseInstallationsRegistrar"],
        "Firebase Crashlytics":   ["com.google.firebase.crashlytics"],
        "Firebase Remote Config": ["com.google.firebase.remoteconfig"],
        "Firebase Performance":   ["com.google.firebase.perf"],
        "Google Sign-In":         ["com.google.android.gms.auth.api.signin"],
        "Google Play Services":   ["com.google.android.gms"],
        "Google Cast":            ["com.google.android.gms.cast"],
        "Facebook SDK":           ["com.facebook"],
        "Adjust SDK":             ["com.adjust"],
        "AppsFlyer":              ["com.appsflyer"],
        "Branch.io":              ["io.branch"],
        "Singular":               ["com.singular"],
        "Kochava":                ["com.kochava"],
        "Sentry":                 ["io.sentry"],
        "Bugsnag":                ["com.bugsnag"],
        "Picasso":                ["com.squareup.picasso"],
        "Glide":                  ["com.bumptech.glide"],
        "OkHttp":                 ["com.squareup.okhttp", "okhttp3"],
        "Retrofit":               ["retrofit2"],
        "ExoPlayer / Media3":     ["com.google.android.exoplayer", "androidx.media3"],
        "Room Database":          ["androidx.room"],
        "WorkManager":            ["androidx.work"],
    }

    lowered = manifest_text.lower()
    return [
        name for name, idents in known.items()
        if any(i.lower() in lowered for i in idents)
    ]


# ---------------------------------------------------------------------------
# Report generation — fixed format
# ---------------------------------------------------------------------------

SENSITIVE_PERMISSIONS = {
    "ACCESS_FINE_LOCATION", "ACCESS_COARSE_LOCATION", "ACCESS_BACKGROUND_LOCATION",
    "READ_CONTACTS", "WRITE_CONTACTS",
    "READ_PHONE_STATE", "READ_PHONE_NUMBERS", "CALL_PHONE",
    "CAMERA",
    "RECORD_AUDIO",
    "READ_SMS", "SEND_SMS", "RECEIVE_SMS",
    "READ_EXTERNAL_STORAGE", "WRITE_EXTERNAL_STORAGE", "MANAGE_EXTERNAL_STORAGE",
    "READ_CALENDAR", "WRITE_CALENDAR",
    "BODY_SENSORS", "ACTIVITY_RECOGNITION",
    "READ_CALL_LOG", "WRITE_CALL_LOG",
    "PROCESS_OUTGOING_CALLS",
    "GET_ACCOUNTS",
    "USE_BIOMETRIC", "USE_FINGERPRINT",
}

STRATEGY_NAMES_ZH = {
    "sync_adapter":       "滥用同步适配器保活（SyncAdapter）",
    "contact_directory":  "滥用联系人目录提供者保活（ContactDirectory）",
    "boot_completed":     "开机自启广播接收器",
    "fcm":                "Firebase 云消息推送（FCM）",
    "full_screen_intent": "全屏意图（Full-screen Intent）",
    "system_alert_window":"悬浮窗（System Alert Window）",
    "foreground_service": "前台服务（Foreground Service）",
    "exact_alarm":        "精确闹钟（Exact Alarm）",
    "workmanager":        "WorkManager / JobScheduler",
}


def _section(title: str) -> list[str]:
    return ["", f"## {title}", ""]


def _divider() -> list[str]:
    return ["", "---", ""]


def generate_report(
    info: dict,
    strategies: dict,
    ad_sdks: dict,
    third_party: list,
    store: dict | None,
    output_path: Path,
) -> str:
    """Render the fixed-format Markdown report and write it to output_path."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pkg = info.get("package", "")
    app_name = (store or {}).get("app_name") or pkg

    lines: list[str] = []

    # ── Header ──────────────────────────────────────────────────────────────
    lines += [
        f"# 竞品分析报告：{app_name}",
        "",
        f"> **分析时间：** {now}",
        f"> **包名：** `{pkg}`",
        f"> **数据来源：** {'Google Play + APK 静态分析' if store else 'APK 静态分析（商店数据不可用）'}",
    ]
    lines += _divider()

    # ── Section 1: 商店信息 ──────────────────────────────────────────────────
    lines += ["## 一、商店信息", ""]
    if store:
        icon = store.get("icon", "")
        gplay_url = store.get("google_play_url", "")
        rating = store.get("rating", "")
        rating_count = store.get("rating_count", "")
        histogram = store.get("rating_histogram", {})

        lines += [
            "| 字段 | 值 |",
            "|---|---|",
            f"| **图标** | {'![icon](' + icon + ')' if icon else '—'} |",
            f"| **应用名称** | {store.get('app_name', '—')} |",
            f"| **包名** | `{pkg}` |",
            f"| **开发者** | {store.get('developer', '—')} |",
            f"| **开发者邮箱** | {store.get('developer_email', '—') or '—'} |",
            f"| **开发者网站** | {store.get('developer_website', '—') or '—'} |",
            f"| **评分** | ★ {rating}（{rating_count:,} 条评价）|" if rating_count else f"| **评分** | ★ {rating} |",
            f"| **下载量** | {store.get('installs', '—')} |",
            f"| **价格** | {store.get('price', '免费')} {'（含内购）' if store.get('offers_iap') else ''} |",
            f"| **分类** | {store.get('genre', '—')} |",
            f"| **内容分级** | {store.get('content_rating', '—')} |",
            f"| **适配 Android** | {store.get('android_version', '—')} 及以上 |",
            f"| **最近更新** | {store.get('last_update', '—')} |",
            f"| **当前版本** | {store.get('version', '—')} |",
            f"| **Google Play** | [查看页面]({gplay_url}) |",
        ]

        # 评分分布
        if histogram:
            lines += [
                "",
                "**评分分布：**",
                "",
                "| 星级 | 数量 |",
                "|---|---|",
            ]
            for star in range(5, 0, -1):
                count = histogram.get(star, 0)
                lines.append(f"| {'★' * star} | {count:,} |")

        # 近期更新说明
        recent = store.get("recent_changes", "").strip()
        if recent:
            lines += ["", "**近期更新说明：**", "", f"> {recent.replace(chr(10), '  ').replace(chr(13), '')}"]

        # 隐私政策
        privacy = store.get("privacy_policy", "")
        if privacy:
            lines += ["", f"**隐私政策：** [{privacy}]({privacy})"]
    else:
        lines.append("> ⚠️ 商店数据不可用（Node.js 未安装或网络受限）")

    lines += _divider()

    # ── Section 2: APK 基本信息 ──────────────────────────────────────────────
    lines += ["## 二、APK 基本信息", ""]
    lines += [
        "| 字段 | 值 |",
        "|---|---|",
        f"| **包名** | `{info['package']}` |",
        f"| **版本名** | {info['version_name']} |",
        f"| **版本号** | {info['version_code']} |",
        f"| **compileSdk** | {info['compile_sdk']} |",
        f"| **targetSdk** | {info['target_sdk']} |",
        f"| **minSdk** | {info['min_sdk']} |",
        f"| **Application 类** | `{info['application_name']}` |",
    ]
    lines += _divider()

    # ── Section 3: 后台保活与推送策略 ────────────────────────────────────────
    lines += ["## 三、后台保活与推送策略", ""]
    detected_strategies = {k: v for k, v in strategies.items() if v["detected"]}
    not_detected = {k: v for k, v in strategies.items() if not v["detected"]}

    lines += [
        f"共检测到 **{len(detected_strategies)}** 项策略（共 {len(strategies)} 项）：",
        "",
        "| 策略 | 状态 | 说明 |",
        "|---|---|---|",
    ]
    for key, s in strategies.items():
        status = "✅ 已检测" if s["detected"] else "➖ 未发现"
        name_zh = STRATEGY_NAMES_ZH.get(key, s["name"])
        desc = s["description"]
        lines.append(f"| {name_zh} | {status} | {desc} |")

    if detected_strategies:
        lines += ["", "### 已检测策略详情", ""]
        for key, s in detected_strategies.items():
            name_zh = STRATEGY_NAMES_ZH.get(key, s["name"])
            lines += [f"#### {name_zh}", ""]
            lines.append(f"- **说明：** {s['description']}")
            if s.get("details"):
                lines.append("- **相关组件：**")
                for d in s["details"]:
                    lines.append(f"  - `{d}`")
            lines.append("")

    lines += _divider()

    # ── Section 4: 广告 SDK ──────────────────────────────────────────────────
    lines += ["## 四、广告 SDK", ""]
    if ad_sdks:
        lines.append(f"共检测到 **{len(ad_sdks)}** 个广告 SDK：")
        lines += ["", "| SDK | 备注 |", "|---|---|"]
        for sdk_name, extra in sorted(ad_sdks.items()):
            note = f"App ID：`{extra}`" if extra else "—"
            lines.append(f"| {sdk_name} | {note} |")
    else:
        lines.append("未检测到常见广告 SDK。")
    lines += _divider()

    # ── Section 5: 第三方服务 ────────────────────────────────────────────────
    lines += ["## 五、第三方服务与 SDK", ""]
    if third_party:
        lines.append(f"共检测到 **{len(third_party)}** 个第三方服务：")
        lines.append("")
        for svc in sorted(third_party):
            lines.append(f"- {svc}")
    else:
        lines.append("未检测到常见第三方服务。")
    lines += _divider()

    # ── Section 6: 权限列表 ──────────────────────────────────────────────────
    lines += ["## 六、权限列表", ""]

    perms = info.get("permissions", [])
    system_perms = sorted(p for p in perms if p.startswith("android.permission."))
    custom_perms = sorted(p for p in perms if not p.startswith("android.permission."))
    sensitive_found = [p for p in system_perms
                       if p.replace("android.permission.", "") in SENSITIVE_PERMISSIONS]

    lines.append(f"共 **{len(perms)}** 个权限（系统 {len(system_perms)}，自定义/第三方 {len(custom_perms)}）")

    if sensitive_found:
        lines += [
            "",
            f"⚠️ **敏感权限（{len(sensitive_found)} 个）：**",
            "",
        ]
        for p in sensitive_found:
            lines.append(f"- `{p}` 【敏感】")

    # Play Store 权限声明对比
    store_perms_raw = (store or {}).get("permissions", [])
    if store_perms_raw:
        # google-play-scraper permissions() returns list of {permission, type, description}
        store_perm_names = set()
        for item in store_perms_raw:
            if isinstance(item, dict):
                name = item.get("permission", "")
                if name:
                    store_perm_names.add(name)
            elif isinstance(item, str):
                store_perm_names.add(item)

        # Permissions in APK but not declared on Play Store (potential hidden)
        apk_perm_short = {p.replace("android.permission.", ""): p for p in system_perms}
        undeclared = [
            full for short, full in apk_perm_short.items()
            if short in SENSITIVE_PERMISSIONS and short not in store_perm_names
            and full.replace("android.permission.", "") not in store_perm_names
        ]
        if undeclared:
            lines += [
                "",
                "⚠️ **以下敏感权限存在于 APK 中，但未在 Google Play 商店页面声明：**",
                "",
            ]
            for p in undeclared:
                lines.append(f"- `{p}`")

    if system_perms:
        lines += ["", f"### 系统权限（{len(system_perms)} 个）", ""]
        for p in system_perms:
            short = p.replace("android.permission.", "")
            suffix = " 【敏感】" if short in SENSITIVE_PERMISSIONS else ""
            lines.append(f"- `{p}`{suffix}")

    if custom_perms:
        lines += ["", f"### 自定义 / 第三方权限（{len(custom_perms)} 个）", ""]
        for p in custom_perms:
            lines.append(f"- `{p}`")

    lines += _divider()

    # ── Section 7: 组件统计 ──────────────────────────────────────────────────
    lines += ["## 七、组件统计", ""]
    lines += [
        "| 组件类型 | 数量 |",
        "|---|---|",
        f"| Activity（界面）| {len(info['activities'])} |",
        f"| Service（服务）| {len(info['services'])} |",
        f"| Receiver（广播接收器）| {len(info['receivers'])} |",
        f"| Provider（内容提供者）| {len(info['providers'])} |",
    ]
    lines += _divider()

    # ── Section 8: 数据安全声明 ──────────────────────────────────────────────
    lines += ["## 八、数据安全声明（Google Play）", ""]
    safety = (store or {}).get("data_safety", [])
    if safety:
        for item in safety:
            if isinstance(item, dict):
                category = item.get("category", "")
                data_type = item.get("data", "")
                purposes = item.get("purposes", "")
                optional = item.get("optional", True)
                flag = "（可选）" if optional else "（必需）"
                lines.append(f"- **{category}** › {data_type}{flag}：{purposes}")
            else:
                lines.append(f"- {item}")
    else:
        lines.append("暂无数据安全声明信息。")

    lines += ["", "---", ""]
    lines.append(f"*报告由 android-analyzer-engineer v3.0.0 自动生成 · {now}*")

    content = "\n".join(lines)
    output_path.write_text(content, encoding="utf-8")
    return content


# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------

def write_run_metadata(workspace, source_target, info, apk_path, report_path, manifest_path):
    metadata = {
        "source_target":  source_target,
        "workspace":      str(workspace.package_dir),
        "package":        info.get("package", ""),
        "version_name":   info.get("version_name", ""),
        "version_code":   info.get("version_code", ""),
        "apk_path":       str(apk_path),
        "report_path":    str(report_path),
        "manifest_path":  str(manifest_path),
        "generated_at":   datetime.now().isoformat(),
    }
    path = workspace.package_dir / "run.json"
    path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Main analysis orchestration
# ---------------------------------------------------------------------------

def analyze_apk(apk_path: Path, workspace, source_target: str, store: dict | None) -> bool:
    """Parse manifest, run all detections, generate fixed-format report."""

    print(f"\n{'=' * 60}")
    print("Step 2: Parse manifest")
    print("=" * 60)

    info, manifest_text, manifest_file = parse_apk(apk_path, workspace.reports_dir)
    if not info:
        return False

    print(f"\n{'=' * 60}")
    print("Step 3: Analyze manifest")
    print("=" * 60)
    print(f"  Package:     {info['package']}")
    print(f"  Version:     {info['version_name']} ({info['version_code']})")
    print(f"  SDK:         min={info['min_sdk']} target={info['target_sdk']} compile={info['compile_sdk']}")
    print(f"  Permissions: {len(info['permissions'])}")
    print(f"  Components:  {len(info['activities'])} Activity / {len(info['services'])} Service / "
          f"{len(info['receivers'])} Receiver / {len(info['providers'])} Provider")

    strategies   = analyze_strategies(manifest_text, info)
    ad_sdks      = detect_ad_sdks(info, manifest_text)
    third_party  = detect_third_party_services(info, manifest_text)

    detected_count = sum(1 for s in strategies.values() if s["detected"])
    print(f"\n  Strategies:   {detected_count}/{len(strategies)} detected")
    for s in strategies.values():
        print(f"    {'[+]' if s['detected'] else '[-]'} {s['name']}")
    print(f"  Ad SDKs:      {len(ad_sdks)}")
    print(f"  3P Services:  {len(third_party)}")

    print(f"\n{'=' * 60}")
    print("Step 4: Generate report")
    print("=" * 60)

    pkg = info["package"] or apk_path.stem
    report_path = workspace.reports_dir / f"{pkg}_report.md"
    generate_report(info, strategies, ad_sdks, third_party, store, report_path)
    meta_path = write_run_metadata(
        workspace=workspace,
        source_target=source_target,
        info=info,
        apk_path=apk_path,
        report_path=report_path,
        manifest_path=manifest_file,
    )

    print(f"  Report:    {report_path}")
    print(f"  Manifest:  {manifest_file}")
    print(f"  Metadata:  {meta_path}")
    print(f"\n{'=' * 60}")
    print("Done")
    print("=" * 60)
    print(f"  Workspace: {workspace.package_dir}")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Analyze an Android app by package name.",
    )
    parser.add_argument(
        "package",
        help="Android package name, e.g. com.whatsapp",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Workspace root (default: .cache/android-app-analyzer/)",
    )
    parser.add_argument(
        "--skip-download", "-s",
        action="store_true",
        help="Reuse a cached APK/XAPK instead of downloading",
    )
    parser.add_argument(
        "--skip-store",
        action="store_true",
        help="Skip Google Play store data fetch",
    )
    args = parser.parse_args()

    # Validate: only package names allowed
    import re
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*(\.[a-zA-Z][a-zA-Z0-9_]*){1,}$', args.package):
        print(f"Error: '{args.package}' is not a valid Android package name.")
        print("Expected format: com.example.app")
        sys.exit(1)

    try:
        workspace_root = resolve_workspace_root(
            repo_root=SCRIPT_DIR,
            output_root=Path(args.output) if args.output else None,
        )
        warning = ensure_workspace_capacity(workspace_root)
        if warning:
            print(f"Warning: {warning}")

        workspace = create_package_workspace(workspace_root, args.package)
        print(f"Workspace: {workspace.package_dir}")

        # Step 0: Fetch store info
        store = None
        if not args.skip_store:
            print(f"\n{'=' * 60}")
            print("Step 0: Fetch Google Play store info")
            print("=" * 60)
            store = fetch_store_info(args.package)

        # Step 1: Download APK
        if args.skip_download:
            candidates = sorted(
                list(workspace.downloads_dir.glob("*.apk")) +
                list(workspace.downloads_dir.glob("*.xapk")),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            if not candidates:
                print("Error: no cached APK/XAPK found. Remove --skip-download to download.")
                sys.exit(1)
            apk_path = candidates[0]
            print(f"Reusing cached: {apk_path}")
        else:
            apk_path = download_apk(args.package, workspace.downloads_dir)

        # XAPK extraction
        if apk_path.suffix.lower() == ".xapk":
            extracted = extract_apk_from_xapk(apk_path, workspace.extracted_dir)
            if not extracted:
                print("Error: could not extract base APK from XAPK.")
                sys.exit(1)
            apk_path = extracted

        success = analyze_apk(apk_path, workspace, source_target=args.package, store=store)
        if not success:
            sys.exit(1)

    except DependencyBootstrapError as exc:
        print(exc)
        sys.exit(1)
    except WorkspaceLimitError as exc:
        print(f"Error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
