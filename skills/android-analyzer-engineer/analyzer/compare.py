"""Compare two versions of the same Android app using archived history reports.

Usage:
    python3 compare.py <package>                  # compare latest two versions
    python3 compare.py <package> --list           # list all recorded versions
    python3 compare.py <package> -a v1 -b v2      # compare specific version_name strings
    python3 compare.py <package> -i 0 -j 1        # compare by index in versions.json

Output: a Markdown diff report printed to stdout (and saved to history/).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

from workspace_manager import USER_CACHE_ROOT, resolve_workspace_root


# ---------------------------------------------------------------------------
# Load helpers
# ---------------------------------------------------------------------------

def load_versions(package_dir: Path) -> list[dict]:
    path = package_dir / "versions.json"
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _extract_permissions(text: str) -> set[str]:
    """Pull every `android.permission.*` or `com.*.permission.*` from report text."""
    return set(re.findall(r'`([A-Za-z][A-Za-z0-9_.]+\.permission\.[A-Z_]+)`', text))


def _extract_ad_sdks(text: str) -> set[str]:
    """Parse the 广告 SDK table rows."""
    sdks = set()
    in_section = False
    for line in text.splitlines():
        if "## 四、广告 SDK" in line:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section and line.startswith("| ") and "SDK" not in line and "---|" not in line:
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if parts:
                sdks.add(parts[0])
    return sdks


def _extract_third_party(text: str) -> set[str]:
    """Parse the 第三方���务 bullet list."""
    svcs = set()
    in_section = False
    for line in text.splitlines():
        if "## 五、第三方服务" in line:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section and line.startswith("- "):
            svcs.add(line[2:].strip())
    return svcs


def _extract_strategies(text: str) -> dict[str, str]:
    """Parse the 保活策略 table → {strategy_name: status}."""
    strategies = {}
    in_section = False
    for line in text.splitlines():
        if "## 三、后台保活" in line:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section and line.startswith("| ") and "策略" not in line and "---|" not in line:
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 2:
                strategies[parts[0]] = parts[1]
    return strategies


def _extract_components(text: str) -> dict[str, str]:
    """Parse the 组件统计 table → {component: count}."""
    components = {}
    in_section = False
    for line in text.splitlines():
        if "## 七、组件统计" in line:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section and line.startswith("| ") and "组件" not in line and "---|" not in line:
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 2:
                components[parts[0]] = parts[1]
    return components


def _extract_apk_info(text: str) -> dict[str, str]:
    """Parse the APK 基本信息 table."""
    info = {}
    in_section = False
    for line in text.splitlines():
        if "## 二、APK 基本信息" in line:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section and line.startswith("| **"):
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 2:
                key = parts[0].strip("*").strip()
                info[key] = parts[1]
    return info


# ---------------------------------------------------------------------------
# Diff helpers
# ---------------------------------------------------------------------------

def _set_diff(label: str, old: set[str], new: set[str]) -> list[str]:
    added = sorted(new - old)
    removed = sorted(old - new)
    lines = []
    if added or removed:
        lines.append(f"\n### {label}\n")
        for item in added:
            lines.append(f"- ➕ `{item}`")
        for item in removed:
            lines.append(f"- ➖ `{item}`")
    return lines


def _dict_diff(label: str, old: dict[str, str], new: dict[str, str]) -> list[str]:
    lines = []
    all_keys = sorted(set(old) | set(new))
    changes = []
    for k in all_keys:
        o, n = old.get(k, "（无）"), new.get(k, "（无）")
        if o != n:
            changes.append(f"- **{k}**：{o} → {n}")
    if changes:
        lines.append(f"\n### {label}\n")
        lines.extend(changes)
    return lines


# ---------------------------------------------------------------------------
# Main diff
# ---------------------------------------------------------------------------

def diff_versions(
    package_dir: Path,
    entry_old: dict,
    entry_new: dict,
) -> str:
    """Build a Markdown diff report between two version entries."""

    def load_report(entry: dict) -> str:
        report_file = package_dir / "history" / entry["report"]
        if not report_file.exists():
            raise FileNotFoundError(f"Report not found: {report_file}")
        return report_file.read_text(encoding="utf-8")

    old_text = load_report(entry_old)
    new_text = load_report(entry_new)

    v_old = entry_old.get("version_name", "?")
    v_new = entry_new.get("version_name", "?")
    pkg = package_dir.name
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines: list[str] = [
        f"# 版本对比报告：{entry_old.get('app_name', pkg)}",
        "",
        f"> **生成时间：** {now}",
        f"> **包名：** `{pkg}`",
        f"> **对比版本：** `{v_old}` → `{v_new}`",
        f"> **旧版分析时间：** {entry_old.get('analyzed_at', '?')[:10]}",
        f"> **新版分析时间：** {entry_new.get('analyzed_at', '?')[:10]}",
        "",
        "---",
    ]

    any_change = False

    # APK 基本信息
    apk_diff = _dict_diff(
        "APK 基本信息变化",
        _extract_apk_info(old_text),
        _extract_apk_info(new_text),
    )
    if apk_diff:
        lines += apk_diff
        any_change = True

    # 保活策略
    strat_diff = _dict_diff(
        "后台保活策略变化",
        _extract_strategies(old_text),
        _extract_strategies(new_text),
    )
    if strat_diff:
        lines += strat_diff
        any_change = True

    # 广告 SDK
    ad_diff = _set_diff(
        "广告 SDK 变化",
        _extract_ad_sdks(old_text),
        _extract_ad_sdks(new_text),
    )
    if ad_diff:
        lines += ad_diff
        any_change = True

    # 第三方服务
    tp_diff = _set_diff(
        "第三方服务变化",
        _extract_third_party(old_text),
        _extract_third_party(new_text),
    )
    if tp_diff:
        lines += tp_diff
        any_change = True

    # 权限
    perm_diff = _set_diff(
        "权限变化",
        _extract_permissions(old_text),
        _extract_permissions(new_text),
    )
    if perm_diff:
        lines += perm_diff
        any_change = True

    # 组件统计
    comp_diff = _dict_diff(
        "组件统计变化",
        _extract_components(old_text),
        _extract_components(new_text),
    )
    if comp_diff:
        lines += comp_diff
        any_change = True

    lines += ["", "---", ""]
    if not any_change:
        lines.append("> ✅ 两个版本之间未检测到可比较的变化。")
    else:
        lines.append(f"*对比报告由 android-analyzer-engineer 自动���成 · {now}*")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Compare two recorded versions of an Android app.",
    )
    parser.add_argument("package", help="Android package name, e.g. com.whatsapp")
    parser.add_argument("--output", "-o", default=None,
                        help="Workspace root (default: ~/.cache/android-app-analyzer/)")
    parser.add_argument("--list", "-l", action="store_true",
                        help="List all recorded versions and exit")
    parser.add_argument("-a", "--version-a", default=None,
                        help="Version name for the older side (default: second-to-last)")
    parser.add_argument("-b", "--version-b", default=None,
                        help="Version name for the newer side (default: latest)")
    parser.add_argument("-i", "--index-a", type=int, default=None,
                        help="Index in versions.json for the older side (0-based)")
    parser.add_argument("-j", "--index-b", type=int, default=None,
                        help="Index in versions.json for the newer side (0-based)")
    parser.add_argument("--save", "-s", action="store_true",
                        help="Save the diff report to history/ in addition to printing")
    args = parser.parse_args()

    workspace_root = resolve_workspace_root(
        output_root=Path(args.output) if args.output else None,
    )
    package_dir = workspace_root / args.package

    if not package_dir.exists():
        print(f"Error: no workspace found for '{args.package}' under {workspace_root}")
        sys.exit(1)

    versions = load_versions(package_dir)
    if not versions:
        print(f"Error: no versions recorded for '{args.package}'. Run a full analysis first.")
        sys.exit(1)

    # --list
    if args.list:
        print(f"版本历史：{args.package}（共 {len(versions)} 次分析）\n")
        for i, v in enumerate(versions):
            print(f"  [{i}] v{v.get('version_name', '?')} "
                  f"(code {v.get('version_code', '?')}) "
                  f"· 分析时间：{v.get('analyzed_at', '?')[:10]} "
                  f"· {v.get('report', '')}")
        return

    if len(versions) < 2:
        print("Error: need at least 2 recorded versions to compare.")
        sys.exit(1)

    # Resolve entries
    def find_by_version(vname: str) -> dict | None:
        for v in reversed(versions):
            if v.get("version_name") == vname:
                return v
        return None

    if args.index_a is not None:
        entry_old = versions[args.index_a]
    elif args.version_a:
        entry_old = find_by_version(args.version_a)
        if not entry_old:
            print(f"Error: version '{args.version_a}' not found.")
            sys.exit(1)
    else:
        entry_old = versions[-2]

    if args.index_b is not None:
        entry_new = versions[args.index_b]
    elif args.version_b:
        entry_new = find_by_version(args.version_b)
        if not entry_new:
            print(f"Error: version '{args.version_b}' not found.")
            sys.exit(1)
    else:
        entry_new = versions[-1]

    try:
        report = diff_versions(package_dir, entry_old, entry_new)
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    print(report)

    if args.save:
        date_str = datetime.now().strftime("%Y-%m-%d")
        v_old = (entry_old.get("version_name") or "?").replace(" ", "_")
        v_new = (entry_new.get("version_name") or "?").replace(" ", "_")
        out_path = package_dir / "history" / f"{date_str}_diff_{v_old}_to_{v_new}.md"
        out_path.write_text(report, encoding="utf-8")
        print(f"\n[saved] {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
