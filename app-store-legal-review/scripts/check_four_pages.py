#!/usr/bin/env python3
"""Mechanical QA for the four-page store legal set.

Checks Terms + Privacy with the original checker, then adds page-level checks for
Child Safety and Account Deletion. Heuristic only; a lawyer still reviews.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from check_draft import (
    EMAIL_RE,
    Draft,
    check_features,
    check_forbidden,
    check_placeholders,
    check_required,
    check_sdk_names,
    split_sections,
)

NUMBER_WORDS = {
    0: ("0", "zero", "immediately", "immediate"),
    1: ("1", "one"),
    2: ("2", "two"),
    3: ("3", "three"),
    4: ("4", "four"),
    5: ("5", "five"),
    6: ("6", "six"),
    7: ("7", "seven"),
    10: ("10", "ten"),
    14: ("14", "fourteen"),
    28: ("28", "twenty-eight", "twenty eight"),
    30: ("30", "thirty"),
    60: ("60", "sixty"),
    90: ("90", "ninety"),
}


def load_config(path: Optional[Path]) -> Dict[str, Any]:
    if path is None:
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise SystemExit("cannot read config: %s" % exc)
    if not isinstance(data, dict):
        raise SystemExit("config must be a JSON object")
    return data


def read_draft(path: Path) -> Draft:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise SystemExit("draft not found: %s" % path)
    if not text.strip():
        raise SystemExit("draft is empty: %s" % path)
    return Draft(text)


def contains(draft: Draft, pattern: str) -> bool:
    return re.search(pattern, draft.text, re.IGNORECASE) is not None


def email_set(text: str) -> Set[str]:
    return {match.group(0).lower() for match in EMAIL_RE.finditer(text)}


def allowed_emails(config: Dict[str, Any]) -> Set[str]:
    allowed = set()
    for key in ("contact_email", "privacy_email", "dpo_email", "child_safety_email"):
        value = config.get(key)
        if isinstance(value, str) and value.strip():
            allowed.add(value.strip().lower())
    return allowed


def check_terms_extras(tos: Draft, config: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    if not contains(tos, r"\breport"):
        errors.append("Terms of Service does not mention reporting")
    if not contains(tos, r"\bblock"):
        errors.append("Terms of Service does not mention blocking")
    if not contains(tos, r"delete.{0,30}account|account.{0,30}delet"):
        errors.append("Terms of Service does not mention account deletion")
    if not contains(tos, r"app store|\bApple\b|Google Play|platform"):
        errors.append("Terms of Service does not mention the app store/platform terms")
    if not contains(tos, r"DMCA|copyright"):
        errors.append("Terms of Service does not mention copyright/DMCA")

    monetization = set(config.get("monetization") or [])
    if monetization & {"订阅", "内购"}:
        for pattern, label in (
            (r"subscription|auto.renew|renew", "subscriptions/auto-renewal"),
            (r"cancel", "subscription cancellation"),
            (r"refund", "refunds"),
        ):
            if not contains(tos, pattern):
                errors.append("Terms of Service does not mention %s" % label)

    return errors


def check_privacy_extras(privacy: Draft, config: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    if not contains(privacy, r"controller|who we are|data controller"):
        errors.append("Privacy Policy does not identify the controller/operator")
    if not contains(privacy, r"delete|deletion"):
        errors.append("Privacy Policy does not mention deletion")
    if not contains(privacy, r"sell|share|opt.out|targeted advertising"):
        errors.append("Privacy Policy does not address sale/sharing/targeted advertising")
    if not contains(privacy, r"retain|retention"):
        errors.append("Privacy Policy does not mention retention")
    if not contains(privacy, r"\b18\b"):
        errors.append("Privacy Policy does not state the 18+ age requirement")

    permissions = [str(item).upper() for item in (config.get("permissions") or [])]
    if any("LOCATION" in item for item in permissions) and not contains(
        privacy, r"location|geolocation"
    ):
        errors.append("Privacy Policy does not mention location, but the build has a location permission")

    return errors


def check_child_safety(child: Draft, config: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    developer = (config.get("developer_legal_name") or "").strip()
    app_name = (config.get("store_app_name") or config.get("app_name") or "").strip()
    csam_email = (config.get("child_safety_email") or "").strip()

    if not developer:
        errors.append("child safety: developer_legal_name is missing from the config")
    elif not contains(child, re.escape(developer)):
        errors.append(
            "child safety: does not include the developer legal name %r" % developer
        )

    if app_name and not contains(child, re.escape(app_name)):
        errors.append("child safety: does not include the store app name %r" % app_name)

    if not csam_email:
        errors.append("child safety: child_safety_email is missing from the config")
    elif not contains(child, re.escape(csam_email)):
        errors.append(
            "child safety: does not include the dedicated CSAM email %r" % csam_email
        )

    for pattern, label in (
        (r"\b18\b", "18+ age requirement"),
        (r"zero[\s-]+tolerance|prohibit\w*.{0,60}(CSAM|child sexual|sexual exploitation)",
         "zero-tolerance / prohibition statement"),
        (r"CSAM|child sexual abuse material|child sexual exploitation", "CSAM definition"),
        (r"report", "reporting channel"),
        (r"block", "blocking tool"),
        (r"NCMEC|National Center for Missing|law enforcement", "authorities/NCMEC"),
        (r"remove|terminat|\bban\b", "removal/termination"),
        (r"contact", "contact section"),
    ):
        if not contains(child, pattern):
            errors.append("child safety: missing %s" % label)

    return errors


def number_present(text: str, value: int) -> bool:
    for word in NUMBER_WORDS.get(value, (str(value),)):
        if re.search(r"(?<![\w])" + re.escape(word) + r"(?![\w])", text, re.IGNORECASE):
            return True
    return False


def check_deletion(
    deletion: Draft, config: Dict[str, Any], warnings: List[str]
) -> List[str]:
    errors: List[str] = []
    deletion_cfg = config.get("deletion") or {}
    if not isinstance(deletion_cfg, dict):
        deletion_cfg = {}

    path = str(deletion_cfg.get("in_app_path") or "").strip()
    if path:
        for segment in re.split(r"\s*(?:→|->|>)\s*", path):
            segment = segment.strip()
            if segment and not contains(deletion, re.escape(segment)):
                errors.append(
                    "account deletion: in-app path segment %r is missing" % segment
                )

    method = str(deletion_cfg.get("request_method") or "").strip()
    if method == "in_app_only":
        errors.append(
            "account deletion: request_method is in_app_only; Play requires a public "
            "web request path as well"
        )
    elif method == "google_form":
        if not contains(deletion, r"Google Form|\bform\b"):
            errors.append("account deletion: does not mention the Google Form/request form")
        response_url = str(deletion_cfg.get("google_form_response_url") or "").strip()
        if not response_url:
            errors.append(
                "account deletion: google_form_response_url is missing; the branded "
                "POST flow requires it"
            )
        entry_ids = deletion_cfg.get("google_form_entry_ids")
        if not isinstance(entry_ids, dict):
            errors.append(
                "account deletion: google_form_entry_ids is missing; the branded POST "
                "flow requires email/account/reason/details entry IDs"
            )
        else:
            for key in ("email", "account", "reason", "details"):
                if not str(entry_ids.get(key) or "").strip():
                    errors.append(
                        "account deletion: google_form_entry_ids.%s is missing" % key
                    )
    elif method == "email":
        if not contains(deletion, r"e-?mail"):
            errors.append("account deletion: does not mention the email request path")
    elif method == "hosted_form":
        if not contains(deletion, r"\bform\b"):
            errors.append("account deletion: does not mention the hosted form")

    if not contains(deletion, r"uninstall|deleting the app|remove the app"):
        errors.append("account deletion: does not distinguish uninstalling the app")
    if not contains(deletion, r"log out|logging out|sign out"):
        errors.append("account deletion: does not distinguish logging out")
    if not contains(deletion, r"retain|retention|keep"):
        errors.append("account deletion: does not explain what may be retained")

    days = deletion_cfg.get("cancellation_window_days")
    if isinstance(days, int) and days == 0:
        if not contains(deletion, r"immediate|immediately|right away"):
            errors.append("account deletion: does not explain immediate deletion")
    elif not contains(deletion, r"cancel|cancellation|restore"):
        errors.append("account deletion: does not explain the cancellation/restore window")

    monetization = set(config.get("monetization") or [])
    if monetization & {"订阅", "内购"}:
        if not contains(deletion, r"subscription"):
            errors.append("account deletion: does not mention subscriptions")
        if not contains(deletion, r"cancel"):
            errors.append("account deletion: does not explain subscription cancellation")

    if isinstance(days, int) and days > 0 and not number_present(deletion.text, days):
        errors.append(
            "account deletion: cancellation_window_days=%d is not mentioned" % days
        )

    web_url = str(deletion_cfg.get("web_url") or "").strip()
    if web_url and not contains(deletion, re.escape(web_url)):
        # The Markdown source may omit the URL; the built HTML should include it.
        warnings.append(
            "account deletion: web_url %r is not present in the Markdown draft; "
            "verify it appears in the rendered HTML" % web_url
        )

    return errors


def check_email_scope(
    name: str,
    draft: Draft,
    allowed: Set[str],
    required: Set[str],
) -> List[str]:
    errors: List[str] = []
    found = email_set(draft.text)
    extra = found - allowed
    if extra:
        errors.append(
            "%s: unconfigured email(s) found: %s" % (name, ", ".join(sorted(extra)))
        )
    if required and not (found & required):
        errors.append(
            "%s: none of the expected email(s) found: %s"
            % (name, ", ".join(sorted(required)))
        )
    return errors


def build_report(errors: List[str], warnings: List[str], paths: Dict[str, Path]) -> str:
    lines = [
        "# Four-page legal QA",
        "",
        "- Result: %s" % ("FAIL" if errors else "PASS"),
        "- Errors: %d" % len(errors),
        "- Warnings: %d" % len(warnings),
        "",
        "> Heuristic check only. A qualified lawyer must still review the set.",
        "",
        "## Inputs",
        "",
    ]
    for name, path in paths.items():
        lines.append("- %s: `%s`" % (name, path))
    lines.append("")
    if errors:
        lines += ["## Errors", ""] + ["- %s" % item for item in errors] + [""]
    if warnings:
        lines += ["## Warnings", ""] + ["- %s" % item for item in warnings] + [""]
    if not errors and not warnings:
        lines += ["No issues found by the mechanical checks.", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--terms", required=True, type=Path)
    parser.add_argument("--privacy", required=True, type=Path)
    parser.add_argument("--child-safety", type=Path)
    parser.add_argument("--deletion", type=Path)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    config = load_config(args.config)
    terms = read_draft(args.terms)
    privacy = read_draft(args.privacy)
    child = read_draft(args.child_safety) if args.child_safety else None
    deletion = read_draft(args.deletion) if args.deletion else None

    warnings: List[str] = []
    errors: List[str] = []

    # Terms + Privacy: reuse the original checks.
    combined = Draft(terms.text + "\n\n" + privacy.text)
    tos_text, privacy_text, section_errors = split_sections(combined.text)
    errors += section_errors
    errors += check_required(
        combined,
        tos_text,
        privacy_text,
        str(config.get("age_gate") or "18+"),
        governing_law=config.get("governing_law"),
        arbitration_provider=config.get("arbitration_provider"),
        arbitration_venue=config.get("arbitration_venue"),
        advertising="广告" in set(config.get("monetization") or []),
    )
    errors += check_forbidden(combined)
    errors += check_placeholders(combined)
    errors += check_terms_extras(terms, config)
    errors += check_privacy_extras(privacy, config)
    errors += check_features(
        combined, set(config.get("features") or []), warnings
    )
    warnings += check_sdk_names(combined)

    allowed = allowed_emails(config)
    contact = config.get("contact_email")
    privacy_email = config.get("privacy_email")
    general_required = {
        value.strip().lower()
        for value in (contact, privacy_email)
        if isinstance(value, str) and value.strip()
    }
    if allowed:
        errors += check_email_scope("terms", terms, allowed, general_required)
        errors += check_email_scope("privacy", privacy, allowed, general_required)

    if child:
        errors += check_placeholders(child)
        errors += check_child_safety(child, config)
        child_email = config.get("child_safety_email")
        if allowed:
            errors += check_email_scope(
                "child safety",
                child,
                allowed,
                {child_email.strip().lower()} if isinstance(child_email, str) and child_email.strip() else set(),
            )
        if (
            isinstance(contact, str)
            and isinstance(child_email, str)
            and contact.strip().lower() == child_email.strip().lower()
        ):
            errors.append(
                "child safety: child_safety_email must differ from the general contact"
            )
    else:
        warnings.append("child safety page not supplied; skipping child-safety checks")

    if deletion:
        errors += check_placeholders(deletion)
        errors += check_deletion(deletion, config, warnings)
        if allowed:
            errors += check_email_scope("account deletion", deletion, allowed, general_required)
    else:
        warnings.append("account deletion page not supplied; skipping deletion checks")

    paths = {
        "terms": args.terms,
        "privacy": args.privacy,
    }
    if args.child_safety:
        paths["child safety"] = args.child_safety
    if args.deletion:
        paths["account deletion"] = args.deletion

    report = build_report(errors, warnings, paths)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8")
    print(report)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
