#!/usr/bin/env python3
"""Check the app-facts config and print the facts the user still needs to supply.

The skill must not draft with guessed legal facts or placeholders. Run this
before any drafting:

    python3 scripts/preflight.py --config app-legal.json --scope four-pages

Exit codes: 0 complete, 1 missing/invalid facts, 2 unreadable config.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
PLACEHOLDER_WORDS = ("TBD", "TODO", "待补充", "your company", "example", "replace")

ALLOWED_PLATFORMS = {"iOS", "Google Play"}
ALLOWED_MONETIZATION = {"免费", "订阅", "内购", "广告"}
ALLOWED_FEATURES = {
    "账号注册登录",
    "社交或 UGC",
    "支付",
    "AI 生成功能",
    "定位",
    "相机或麦克风",
    "通讯录或相册",
    "推送通知",
    "健康或健身数据",
    "云存储",
}
ALLOWED_METHODS = {"google_form", "hosted_form", "email", "in_app_only"}
ALLOWED_SELL = {"yes", "no", "unknown"}
ALLOWED_ACCOUNT_MODELS = {"device", "email", "phone", "username", "other"}

MESSAGES = {
    "app_name": "App 的内部/产品名称",
    "store_app_name": "App 在商店展示的完整名称",
    "developer_legal_name": "开发者/运营主体的完整法定名称",
    "platforms": "上架平台（iOS / Google Play / 两者）",
    "region": "分发地区",
    "contact_email": "通用法务/隐私/支持邮箱",
    "child_safety_email": "专门的儿童安全（CSAM）邮箱（需已创建、可收信，且与通用邮箱不同）",
    "monetization": "商业化模式（免费/订阅/内购/广告）",
    "features": "当前构建实际包含的核心功能",
    "age_gate": "年龄门槛及实际执行的验证方式",
    "permissions": "实际申请的运行时权限（以合并后的 AndroidManifest 为准；没有就写空数组）",
    "account_model": "账号体系（device/email/phone/username/other）",
    "sdk_categories": "第三方 SDK/处理方类别（广告、分析、崩溃、支付、IM、云存储等）",
    "sells_or_shares": "是否出售/共享个人数据（yes/no/unknown）",
    "sensitive_data": "用户可能提供的敏感数据类别（没有写空数组）",
    "governing_law": "适用法律（州/国家）",
    "arbitration_provider": "仲裁机构（AAA / NAM / 其他 / 不仲裁）",
    "arbitration_venue": "仲裁地",
    "arbitration_opt_out_days": "仲裁退出期（天；没有写 0）",
    "deletion.in_app_path": "App 内删除路径（例如 Settings → Delete account → Delete）",
    "deletion.web_url": "公开删号网页 URL（https，无需登录即可访问）",
    "deletion.request_method": "删号请求方式（google_form/hosted_form/email/in_app_only）",
    "deletion.google_form_url": "已发布 Google Form 的公开链接",
    "deletion.google_form_response_url": "Google Form 的 formResponse 接口（品牌表单 POST 目标）",
    "deletion.google_form_entry_ids": "Google Form 的 entry.* 字段映射",
    "deletion.google_form_entry_ids.email": "Contact email 字段的 entry ID（如 entry.123）",
    "deletion.google_form_entry_ids.account": "Account identifier/profile name 字段的 entry ID",
    "deletion.google_form_entry_ids.reason": "Reason 字段的 entry ID",
    "deletion.google_form_entry_ids.details": "Details/others 字段的 entry ID",
    "deletion.cancellation_window_days": "删除前的可取消/可恢复窗口（天；立即删除写 0）",
    "deletion.retention_summary": "删除范围与保留例外",
    "deletion.subscription_cancellation": "订阅是否需要用户另行取消（如适用）",
}

GROUPED_ORDER = [
    ("App 与主体", ["app_name", "store_app_name", "developer_legal_name",
                    "platforms", "region"]),
    ("联系方式", ["contact_email", "child_safety_email"]),
    ("当前构建事实", ["permissions", "account_model", "sdk_categories",
                     "monetization", "features", "age_gate", "sells_or_shares",
                     "sensitive_data"]),
    ("删除账户", ["deletion.in_app_path", "deletion.web_url",
                 "deletion.request_method", "deletion.google_form_url",
                 "deletion.google_form_response_url",
                 "deletion.google_form_entry_ids",
                 "deletion.google_form_entry_ids.email",
                 "deletion.google_form_entry_ids.account",
                 "deletion.google_form_entry_ids.reason",
                 "deletion.google_form_entry_ids.details",
                 "deletion.cancellation_window_days",
                 "deletion.retention_summary",
                 "deletion.subscription_cancellation"]),
    ("争议解决", ["governing_law", "arbitration_provider",
                 "arbitration_venue", "arbitration_opt_out_days"]),
]

TOS_PRIVACY_FIELDS = [
    "app_name",
    "platforms",
    "region",
    "contact_email",
    "monetization",
    "features",
    "age_gate",
]


class PreflightError(Exception):
    pass


def load_config(path: Path) -> Dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise PreflightError("config not found: %s" % path)
    except json.JSONDecodeError as exc:
        raise PreflightError("config is not valid JSON: %s" % exc)
    if not isinstance(data, dict):
        raise PreflightError("config must be a JSON object")
    return data


def value_at(config: Dict[str, Any], path: str) -> Any:
    current: Any = config
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def string_value(config: Dict[str, Any], path: str) -> Optional[str]:
    value = value_at(config, path)
    if not isinstance(value, str) or not value.strip():
        return None
    return value.strip()


def list_value(config: Dict[str, Any], path: str) -> Optional[List[str]]:
    value = value_at(config, path)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        return None
    return value


def int_value(config: Dict[str, Any], path: str) -> Optional[int]:
    value = value_at(config, path)
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


def is_placeholder(value: str) -> bool:
    lowered = value.lower()
    return any(word.lower() in lowered for word in PLACEHOLDER_WORDS)


def collect(config: Dict[str, Any], scope: str) -> Tuple[List[str], List[str]]:
    missing: List[str] = []
    warnings: List[str] = []

    def need(path: str) -> None:
        if path in missing:
            return
        value = string_value(config, path)
        if value is None:
            missing.append(path)
        elif is_placeholder(value):
            missing.append(path)

    def need_list(path: str) -> None:
        if list_value(config, path) is None:
            missing.append(path)

    def need_int(path: str) -> None:
        if int_value(config, path) is None:
            missing.append(path)

    for path in ("app_name", "platforms", "region", "contact_email",
                 "monetization", "features", "age_gate"):
        if path in {"platforms", "monetization", "features"}:
            need_list(path)
        else:
            need(path)

    if scope == "tos-privacy":
        return missing, warnings

    for path in ("store_app_name", "developer_legal_name", "child_safety_email",
                 "permissions", "account_model", "sdk_categories",
                 "sells_or_shares", "sensitive_data", "governing_law",
                 "arbitration_provider", "arbitration_venue",
                 "deletion.in_app_path", "deletion.web_url",
                 "deletion.request_method", "deletion.cancellation_window_days",
                 "deletion.retention_summary"):
        if path in {"permissions", "sdk_categories", "sensitive_data"}:
            need_list(path)
        elif path == "deletion.cancellation_window_days":
            need_int(path)
        else:
            need(path)

    need_int("arbitration_opt_out_days")

    platforms = set(list_value(config, "platforms") or [])
    if platforms - ALLOWED_PLATFORMS:
        missing.append("platforms")

    monetization = set(list_value(config, "monetization") or [])
    if monetization - ALLOWED_MONETIZATION:
        missing.append("monetization")

    features = set(list_value(config, "features") or [])
    if features - ALLOWED_FEATURES:
        missing.append("features")

    account_model = string_value(config, "account_model")
    if account_model and account_model not in ALLOWED_ACCOUNT_MODELS:
        missing.append("account_model")

    sells = string_value(config, "sells_or_shares")
    if sells and sells not in ALLOWED_SELL:
        missing.append("sells_or_shares")
    if sells == "unknown":
        warnings.append(
            "sells_or_shares is 'unknown'; use qualified privacy wording and have "
            "legal confirm the opt-out mechanism"
        )

    method = string_value(config, "deletion.request_method")
    if method and method not in ALLOWED_METHODS:
        missing.append("deletion.request_method")

    if method == "google_form":
        need("deletion.google_form_url")
        need("deletion.google_form_response_url")
        entry_ids = value_at(config, "deletion.google_form_entry_ids")
        if not isinstance(entry_ids, dict):
            missing.append("deletion.google_form_entry_ids")
        else:
            for key in ("email", "account", "reason", "details"):
                value = entry_ids.get(key)
                if not isinstance(value, str) or not value.strip() or is_placeholder(value):
                    missing.append("deletion.google_form_entry_ids." + key)

    if monetization & {"订阅", "内购"}:
        if string_value(config, "deletion.subscription_cancellation") is None:
            missing.append("deletion.subscription_cancellation")

    contact = string_value(config, "contact_email")
    child = string_value(config, "child_safety_email")
    if contact and not EMAIL_RE.match(contact):
        missing.append("contact_email")
    if child:
        if not EMAIL_RE.match(child):
            missing.append("child_safety_email")
        elif contact and child.lower() == contact.lower():
            missing.append("child_safety_email")
            warnings.append(
                "child_safety_email must be a dedicated, monitored CSAM mailbox, "
                "not the general contact address"
            )

    web_url = string_value(config, "deletion.web_url")
    if web_url and not web_url.startswith("https://"):
        missing.append("deletion.web_url")

    permissions = [item.upper() for item in (list_value(config, "permissions") or [])]
    has_camera = any("CAMERA" in item for item in permissions)
    has_location = any("LOCATION" in item for item in permissions)
    if "相机或麦克风" in features and not has_camera and not any(
        "RECORD_AUDIO" in item for item in permissions
    ):
        warnings.append(
            "features includes 相机或麦克风 but permissions has no CAMERA/RECORD_AUDIO; "
            "confirm the feature and the permission story"
        )
    if "定位" in features and not has_location:
        warnings.append(
            "features includes 定位 but permissions has no location permission; "
            "confirm whether this is device location or approximate region from a "
            "postal code"
        )

    # Preserve stable order and uniqueness.
    seen = set()
    ordered_missing = []
    for path in missing:
        if path not in seen:
            seen.add(path)
            ordered_missing.append(path)
    return ordered_missing, warnings


def render_missing(missing: List[str]) -> str:
    lines = [
        "为了生成四页协议，请补齐以下信息（缺失项会阻止起草）：",
        "",
    ]
    assigned = set()
    for group, paths in GROUPED_ORDER:
        group_items = [path for path in paths if path in missing and path not in assigned]
        if not group_items:
            continue
        lines.append("【%s】" % group)
        for path in group_items:
            assigned.add(path)
            lines.append("%d. %s：" % (len(assigned), MESSAGES.get(path, path)))
        lines.append("")
    leftovers = [path for path in missing if path not in assigned]
    if leftovers:
        lines.append("【其他】")
        for path in leftovers:
            lines.append("- %s（%s）" % (MESSAGES.get(path, path), path))
        lines.append("")
    lines.append("请把答案直接按编号回复；涉及邮箱、URL、权限和删除窗口的，请给准确值。")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path,
                        help="app facts JSON")
    parser.add_argument(
        "--scope",
        choices=("tos-privacy", "four-pages"),
        default="four-pages",
        help="tos-privacy checks only the original two-page facts; four-pages "
             "also requires child safety and deletion facts (default)",
    )
    parser.add_argument("--message", action="store_true",
                        help="print only the user-facing missing-facts message")
    parser.add_argument("--json", action="store_true",
                        help="print a machine-readable report")
    args = parser.parse_args()

    try:
        config = load_config(args.config)
    except PreflightError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2

    missing, warnings = collect(config, args.scope)

    if args.json:
        print(json.dumps(
            {
                "scope": args.scope,
                "complete": not missing,
                "missing": missing,
                "warnings": warnings,
            },
            indent=2,
            ensure_ascii=False,
        ))
        return 0 if not missing else 1

    if args.message:
        if missing:
            print(render_missing(missing))
            return 1
        print("Preflight complete: no missing required facts.")
        return 0

    if missing:
        print("Preflight: FAIL — %d required fact(s) missing or invalid.\n" % len(missing))
        print(render_missing(missing))
    else:
        print("Preflight: PASS — all required facts for %s are present." % args.scope)

    if warnings:
        print("\nWarnings (review before drafting):")
        for warning in warnings:
            print("- %s" % warning)

    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
