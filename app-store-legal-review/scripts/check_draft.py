#!/usr/bin/env python3
"""Mechanical QA for a ToS + Privacy Policy draft produced by this skill."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
PLACEHOLDER_RE = re.compile(r"\{[^{}\n]+\}")
BRACKET_PLACEHOLDER_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\[COMPANY LEGAL NAME\]",
        r"\[WEBSITE URL\]",
        r"\[ADDRESS\]",
        r"\[COMPANY NAME\]",
        r"\[LEGAL ENTITY\]",
        r"\[CONTACT EMAIL\]",
        r"\[EFFECTIVE DATE\]",
        r"\[DATE\]",
        r"\[URL\]",
        r"\[EMAIL\]",
    )
]
RETENTION_DAYS_RE = re.compile(
    r"\b(?:retain|retention|store|keep)\b[^.\n]{0,100}\b\d+\s*(?:days?|months?|years?)\b",
    re.IGNORECASE,
)
NO_MORE_THAN_RE = re.compile(r"\bno more than\s+\d+\s*(?:days?|months?|years?)\b", re.IGNORECASE)

FORBIDDEN_PATTERNS: List[Tuple[str, str]] = [
    (r"\bwe do not collect\b", "absolute negative commitment: 'we do not collect'"),
    (r"\bwe do not sell\b", "absolute negative commitment: 'we do not sell'"),
    (r"\bwe do not share\b", "absolute negative commitment: 'we do not share'"),
    (r"\bwe do not use\b", "absolute negative commitment: 'we do not use'"),
    (r"\bwe never (?:collect|sell|share|use)\b", "absolute negative commitment: 'we never ...'"),
    (r"\bwe will not (?:collect|sell|share|use)\b", "absolute negative commitment: 'we will not ...'"),
]

SDK_NAMES = [
    "AdMob",
    "AppLovin",
    "AppsFlyer",
    "Adjust",
    "Crashlytics",
    "Sentry",
    "Firebase",
    "Stripe",
    "Google Analytics",
    "Facebook SDK",
    "Meta Audience Network",
]

FEATURE_PATTERNS: Dict[str, str] = {
    "账号注册登录": r"\baccount\b",
    "社交或 UGC": r"user content|user-generated|\bUGC\b",
    "支付": r"\bpurchase|subscription|in-app purchase|\bpayment",
    "AI 生成功能": r"\bAI\b|artificial intelligence",
    "定位": r"\blocation\b|geolocation|\bGPS\b",
    "相机或麦克风": r"\bcamera\b|\bmicrophone\b",
    "通讯录或相册": r"\bcontacts\b|photo library|\bphotos\b",
    "推送通知": r"push notification",
    "健康或健身数据": r"\bhealth\b|\bfitness\b",
    "云存储": r"cloud storage",
}

FEATURE_ABSENCE_PATTERNS: Dict[str, str] = {
    "AI 生成功能": r"\bAI\b|artificial intelligence",
    "定位": r"precise location|geolocation|\bGPS\b|your location",
    "相机或麦克风": r"\bcamera\b|\bmicrophone\b",
    "通讯录或相册": r"address book|\bcontacts\b|photo library",
    "推送通知": r"push notification",
    "健康或健身数据": r"health data|fitness data",
    "云存储": r"cloud storage",
}

CHECKLIST_DATA_PATTERNS: Dict[str, str] = {
    "注册信息": r"account information|\baccount\b",
    "个人资料": r"profile",
    "广告标识符": r"advertising identifier|IDFA|GAID",
    "设备信息": r"device information|\bdevice\b",
    "IP/网络": r"\bIP address\b|network status|\bnetwork\b",
    "精确位置": r"precise location|\bGPS\b",
    "模糊位置": r"approximate location|coarse location",
    "使用行为": r"usage|browsing|click|search history",
    "崩溃日志": r"crash|diagnostic",
    "用户内容": r"user content|user-generated|\bUGC\b",
    "通讯录内容": r"\bcontacts\b|address book",
    "相册照片/视频": r"\bphotos?\b|photo library|\bvideos?\b",
    "麦克风录音": r"\bmicrophone\b",
    "支付信息": r"\bpayment",
}

CHECKLIST_FEATURE_MAP = {
    "账号注册/登录": "账号注册登录",
    "社交/社区/UGC": "社交或 UGC",
    "支付/电商": "支付",
    "AI 功能": "AI 生成功能",
    "定位服务": "定位",
    "相机/麦克风": "相机或麦克风",
    "通讯录/相册": "通讯录或相册",
    "推送通知": "推送通知",
    "健康/健身数据": "健康或健身数据",
    "文件存储/云同步": "云存储",
}


class Draft:
    def __init__(self, text: str):
        self.text = text
        self.lines = text.splitlines()

    def find_line(self, pattern: str, flags: int = re.IGNORECASE) -> Optional[int]:
        regex = re.compile(pattern, flags)
        for number, line in enumerate(self.lines, start=1):
            if regex.search(line):
                return number
        return None

    def has(self, pattern: str, flags: int = re.IGNORECASE) -> bool:
        return re.search(pattern, self.text, flags) is not None


def split_sections(text: str) -> Tuple[str, str, List[str]]:
    errors: List[str] = []

    def heading_positions(name: str) -> List[int]:
        pattern = re.compile(
            r"(?im)^\s{0,3}#{1,6}\s*.*?" + re.escape(name) + r".*$"
        )
        return [match.start() for match in pattern.finditer(text)]

    tos_positions = heading_positions("terms of service")
    privacy_positions = heading_positions("privacy policy")

    if not tos_positions:
        errors.append("missing a 'Terms of Service' heading")
    if not privacy_positions:
        errors.append("missing a 'Privacy Policy' heading")

    if tos_positions and privacy_positions:
        tos_start, privacy_start = tos_positions[0], privacy_positions[0]
        if privacy_start < tos_start:
            errors.append("Privacy Policy appears before Terms of Service")
            return text, text, errors
        return text[tos_start:privacy_start], text[privacy_start:], errors

    return text, text, errors


def check_required(
    draft: Draft,
    tos_text: str,
    privacy_text: str,
    age_gate: str = "18+",
    governing_law: Optional[str] = None,
    arbitration_provider: Optional[str] = None,
    arbitration_venue: Optional[str] = None,
    advertising: bool = True,
) -> List[str]:
    errors: List[str] = []

    tos_required = [
        ("acceptance / eligibility", r"acceptance|\beligib"),
        ("accounts", r"\baccount"),
        ("purchases / subscriptions / IAP", r"purchase|subscription|in-app"),
        ("intellectual property / license", r"intellectual property|\blicense"),
        ("AS IS warranty disclaimer", r"\bAS IS\b|disclaimer of warranties"),
        ("limitation of liability", r"limitation of liability|limit.{0,20}liability"),
        ("indemnification", r"indemnif"),
        ("changes to terms / notice",
         r"changes to (?:the |these )?terms|modif|update (?:the |these )?terms"),
        ("contact section", r"\bcontact\b"),
    ]
    privacy_required = [
        ("information we collect", r"information we collect|\bcollect"),
        ("how we use information", r"how we use|use of information|\buse\b"),
        ("how we share information", r"how we share|\bshar"),
        ("cookies / similar technologies", r"cookies?|similar technologies"),
        ("data retention", r"retain|retention"),
        ("user rights", r"your rights|right to know|right to delete"),
        ("CCPA / CPRA", r"\bCCPA\b|\bCPRA\b"),
        ("children's privacy and age 13", r"children"),
        ("security safeguards", r"security|safeguard"),
        ("contact section", r"\bcontact\b"),
    ]
    if advertising:
        privacy_required.append(
            ("advertising identifiers", r"advertising identifier|IDFA|GAID")
        )

    for label, pattern in tos_required:
        if not re.search(pattern, tos_text, re.IGNORECASE):
            errors.append(f"Terms of Service is missing: {label}")

    for label, pattern in privacy_required:
        if not re.search(pattern, privacy_text, re.IGNORECASE):
            errors.append(f"Privacy Policy is missing: {label}")

    if governing_law:
        if not re.search(re.escape(governing_law), tos_text, re.IGNORECASE):
            errors.append(
                "Terms of Service is missing the configured governing law: "
                f"{governing_law}"
            )
    elif not re.search(r"governing law|laws of the state", tos_text, re.IGNORECASE):
        errors.append("Terms of Service is missing: governing law")

    provider = (arbitration_provider or "").strip()
    arbitrates = bool(provider) and provider.lower() not in {
        "none",
        "no",
        "n/a",
        "不仲裁",
    }
    if arbitrates:
        if not re.search(r"arbitrat", tos_text, re.IGNORECASE):
            errors.append("Terms of Service is missing: arbitration")
        if provider.lower() in {"aaa", "american arbitration association"}:
            if not re.search(
                r"American Arbitration Association|\bAAA\b", tos_text, re.IGNORECASE
            ):
                errors.append(
                    "Terms of Service is missing: American Arbitration Association (AAA)"
                )
        elif provider.lower() in {"nam", "national arbitration and mediation"}:
            if not re.search(
                r"National Arbitration and Mediation|\bNAM\b", tos_text, re.IGNORECASE
            ):
                errors.append(
                    "Terms of Service is missing: National Arbitration and Mediation (NAM)"
                )
        elif not re.search(re.escape(provider), tos_text, re.IGNORECASE):
            errors.append(
                "Terms of Service is missing the configured arbitration provider: "
                f"{provider}"
            )
        if not re.search(r"class[\s-]+action", tos_text, re.IGNORECASE):
            errors.append("Terms of Service is missing: class-action waiver")
    elif not re.search(r"dispute|small claims|court", tos_text, re.IGNORECASE):
        errors.append("Terms of Service is missing: dispute resolution / forum")

    if arbitration_venue:
        if not re.search(re.escape(arbitration_venue), tos_text, re.IGNORECASE):
            city = arbitration_venue.split(",")[0].strip()
            if not city or not re.search(re.escape(city), tos_text, re.IGNORECASE):
                errors.append(
                    "Terms of Service is missing the configured arbitration venue: "
                    f"{arbitration_venue}"
                )

    if not re.search(r"\b13\b", privacy_text):
        errors.append("Privacy Policy does not mention children under 13")
    if age_gate == "18+" and not re.search(r"\b18\b", tos_text):
        errors.append("Terms of Service does not mention the 18+ age threshold")

    return errors


def check_forbidden(draft: Draft) -> List[str]:
    errors: List[str] = []
    for pattern, message in FORBIDDEN_PATTERNS:
        if re.search(pattern, draft.text, re.IGNORECASE):
            line = draft.find_line(pattern)
            errors.append(f"{message} (line {line})")

    for match in RETENTION_DAYS_RE.finditer(draft.text):
        line = draft.text[: match.start()].count("\n") + 1
        errors.append(f"fixed retention period found (line {line}): {match.group(0)!r}")
    for match in NO_MORE_THAN_RE.finditer(draft.text):
        line = draft.text[: match.start()].count("\n") + 1
        errors.append(f"fixed retention period found (line {line}): {match.group(0)!r}")

    return errors


def check_placeholders(draft: Draft) -> List[str]:
    errors: List[str] = []
    seen: Set[str] = set()
    regexes = [PLACEHOLDER_RE] + BRACKET_PLACEHOLDER_PATTERNS
    for regex in regexes:
        for match in regex.finditer(draft.text):
            value = match.group(0)
            if value in seen:
                continue
            seen.add(value)
            line = draft.text[: match.start()].count("\n") + 1
            errors.append(f"unresolved placeholder {value!r} (line {line})")
    for token in ("TBD", "TODO", "待补充"):
        if token in draft.text:
            line = draft.find_line(re.escape(token), 0)
            errors.append(f"unresolved marker {token!r} (line {line})")
    return errors


def check_email(
    draft: Draft,
    expected: Optional[str],
    allowed_extra: Optional[Set[str]] = None,
) -> List[str]:
    emails = {match.group(0).lower() for match in EMAIL_RE.finditer(draft.text)}
    errors: List[str] = []
    if not emails:
        errors.append("no contact email found in the draft")
        return errors

    allowed: Set[str] = set()
    if expected:
        allowed.add(expected.lower())
    for value in allowed_extra or set():
        if value:
            allowed.add(value.lower())

    if expected:
        if expected.lower() not in emails:
            errors.append(
                "configured contact email %r is missing from the draft" % expected
            )
        extra = emails - allowed
        if extra:
            errors.append(
                "unconfigured email(s) found: " + ", ".join(sorted(extra))
            )
    elif len(emails) > 1:
        errors.append("multiple contact emails found: " + ", ".join(sorted(emails)))
    return errors


def check_features(draft: Draft, configured: Set[str], warnings: List[str]) -> List[str]:
    errors: List[str] = []
    for feature in sorted(configured):
        pattern = FEATURE_PATTERNS.get(feature)
        if pattern is None:
            warnings.append(f"no keyword mapping for feature: {feature}")
            continue
        if not draft.has(pattern):
            errors.append(f"draft does not cover configured feature: {feature}")

    for feature, pattern in FEATURE_ABSENCE_PATTERNS.items():
        if feature not in configured and draft.has(pattern):
            line = draft.find_line(pattern)
            warnings.append(
                f"draft mentions {feature!r} but the checklist says it is absent "
                f"(line {line}); verify it is only qualified 'if applicable' wording"
            )
    return errors


def check_sdk_names(draft: Draft) -> List[str]:
    warnings: List[str] = []
    case_sensitive = {"Adjust", "Sentry", "Stripe"}
    for name in SDK_NAMES:
        flags = 0 if name in case_sensitive else re.IGNORECASE
        pattern = r"\b" + re.escape(name) + r"\b"
        if re.search(pattern, draft.text, flags):
            line = draft.find_line(pattern, flags)
            warnings.append(
                f"first draft names a third-party SDK/provider {name!r} (line {line}); "
                "the drafting prompt asks for category-level wording"
            )
    return warnings


def parse_checklist(text: str) -> Dict[str, str]:
    fields: Dict[str, str] = {}
    keys = (
        "App 名称",
        "联系邮箱",
        "上架平台",
        "商店分发",
        "商业化",
        "年龄门槛",
        "核心功能（是）",
        "数据收集（是）",
        "权限（是）",
    )
    for line in text.splitlines():
        stripped = line.strip()
        for key in keys:
            prefix = key + "："
            if stripped.startswith(prefix):
                fields[key] = stripped[len(prefix) :].strip()
    return fields


def split_checklist_items(value: str) -> Set[str]:
    if not value or value == "无":
        return set()
    return {item.strip() for item in value.split("、") if item.strip()}


def check_checklist(
    draft: Draft, checklist_text: str, warnings: List[str]
) -> List[str]:
    errors: List[str] = []
    fields = parse_checklist(checklist_text)
    if not fields:
        warnings.append("could not parse checklist result; skipping checklist cross-check")
        return errors

    features = {
        CHECKLIST_FEATURE_MAP[name]
        for name in split_checklist_items(fields.get("核心功能（是）", ""))
        if name in CHECKLIST_FEATURE_MAP
    }
    for feature in sorted(features):
        pattern = FEATURE_PATTERNS.get(feature)
        if pattern and not draft.has(pattern):
            errors.append(
                f"checklist says the build has {feature!r}, but the draft does not mention it"
            )

    data_items = split_checklist_items(fields.get("数据收集（是）", ""))
    for item in sorted(data_items):
        pattern = CHECKLIST_DATA_PATTERNS.get(item)
        if pattern and not draft.has(pattern):
            errors.append(
                f"checklist says the build collects {item!r}, but the Privacy Policy "
                "does not mention that category"
            )
        elif pattern is None:
            warnings.append(f"no privacy keyword mapping for checklist data item: {item}")

    if "其他（待补充）" in checklist_text:
        warnings.append(
            "checklist still contains '其他（待补充）'; name the SDK and provider before handoff"
        )
    return errors


def build_report(
    draft_path: Path,
    errors: List[str],
    warnings: List[str],
    section_errors: List[str],
) -> str:
    all_errors = section_errors + errors
    lines = [
        "# Legal draft QA",
        "",
        f"- Draft: `{draft_path}`",
        f"- Result: {'FAIL' if all_errors else 'PASS'}",
        f"- Errors: {len(all_errors)}",
        f"- Warnings: {len(warnings)}",
        "",
        "> Heuristic check only. A qualified lawyer must still review the draft.",
        "",
    ]
    if all_errors:
        lines += ["## Errors", ""]
        lines += [f"- {item}" for item in all_errors]
        lines.append("")
    if warnings:
        lines += ["## Warnings", ""]
        lines += [f"- {item}" for item in warnings]
        lines.append("")
    if not all_errors and not warnings:
        lines += ["No issues found by the mechanical checks.", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draft", required=True, type=Path, help="ToS + Privacy Policy markdown")
    parser.add_argument("--config", type=Path, help="optional app facts JSON")
    parser.add_argument("--checklist", type=Path, help="optional checklist result text")
    parser.add_argument("--out", type=Path, help="optional QA report output path")
    args = parser.parse_args()

    try:
        text = args.draft.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"error: draft not found: {args.draft}", file=sys.stderr)
        return 2

    if not text.strip():
        print("error: draft is empty", file=sys.stderr)
        return 2

    expected_email: Optional[str] = None
    privacy_email: Optional[str] = None
    dpo_email: Optional[str] = None
    configured_features: Set[str] = set()
    age_gate = "18+"
    governing_law: Optional[str] = None
    arbitration_provider: Optional[str] = None
    arbitration_venue: Optional[str] = None
    if args.config:
        try:
            config = json.loads(args.config.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            print(f"error: cannot read config: {exc}", file=sys.stderr)
            return 2
        expected_email = config.get("contact_email")
        privacy_email = config.get("privacy_email")
        dpo_email = config.get("dpo_email")
        configured_features = set(config.get("features", []))
        age_gate = config.get("age_gate", "18+")
        governing_law = config.get("governing_law")
        arbitration_provider = config.get("arbitration_provider")
        arbitration_venue = config.get("arbitration_venue")
        advertising = "广告" in set(config.get("monetization") or [])
    else:
        advertising = True

    draft = Draft(text)
    tos_text, privacy_text, section_errors = split_sections(text)

    warnings: List[str] = []
    errors: List[str] = []
    errors += check_required(
        draft,
        tos_text,
        privacy_text,
        age_gate,
        governing_law=governing_law,
        arbitration_provider=arbitration_provider,
        arbitration_venue=arbitration_venue,
        advertising=advertising,
    )
    errors += check_forbidden(draft)
    errors += check_placeholders(draft)
    errors += check_email(draft, expected_email, {privacy_email, dpo_email})
    errors += check_features(draft, configured_features, warnings)
    warnings += check_sdk_names(draft)

    if args.checklist:
        try:
            checklist_text = args.checklist.read_text(encoding="utf-8")
        except FileNotFoundError:
            print(f"error: checklist not found: {args.checklist}", file=sys.stderr)
            return 2
        errors += check_checklist(draft, checklist_text, warnings)

    report = build_report(args.draft, errors, warnings, section_errors)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8")
    print(report)
    return 1 if (section_errors or errors) else 0


if __name__ == "__main__":
    raise SystemExit(main())
