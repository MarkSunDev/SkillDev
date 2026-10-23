#!/usr/bin/env python3
"""Validate app facts, fill the legal drafting prompt, and assemble a brief."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TEMPLATE = ROOT / "references" / "drafting-prompt.txt"

PLATFORMS = {"iOS", "Google Play"}
MONETIZATION = {"免费", "订阅", "内购", "广告"}
FEATURES = [
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
]
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
PLACEHOLDER_RE = re.compile(r"\{[^{}\n]+\}")

CHECKLIST_FEATURES = {
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


class ValidationError(Exception):
    pass


def load_config(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValidationError(f"config not found: {path}")
    except json.JSONDecodeError as exc:
        raise ValidationError(f"config is not valid JSON: {exc}")
    if not isinstance(data, dict):
        raise ValidationError("config must be a JSON object")
    return data


def require_string(config: dict, key: str) -> str:
    value = config.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"'{key}' must be a non-empty string")
    return value.strip()


def require_list(config: dict, key: str, allowed: set[str] | None = None) -> list[str]:
    value = config.get(key)
    if not isinstance(value, list) or not value:
        raise ValidationError(f"'{key}' must be a non-empty array")
    if not all(isinstance(item, str) for item in value):
        raise ValidationError(f"'{key}' must contain only strings")
    if len(set(value)) != len(value):
        raise ValidationError(f"'{key}' contains duplicates")
    if allowed is not None:
        unknown = [item for item in value if item not in allowed]
        if unknown:
            raise ValidationError(
                f"'{key}' has unsupported values: {', '.join(unknown)}; "
                f"allowed: {', '.join(sorted(allowed))}"
            )
    return value


def validate(config: dict, allow_age_gate_mismatch: bool = False) -> dict:
    app_name = require_string(config, "app_name")
    platforms = require_list(config, "platforms", PLATFORMS)
    region = require_string(config, "region")
    email = require_string(config, "contact_email")
    monetization = require_list(config, "monetization", MONETIZATION)
    features = require_list(config, "features", set(FEATURES))
    age_gate = config.get("age_gate", "18+")
    if not isinstance(age_gate, str):
        raise ValidationError("'age_gate' must be a string")

    if not EMAIL_RE.match(email):
        raise ValidationError(f"'contact_email' is not a valid email address: {email}")
    if age_gate != "18+" and not allow_age_gate_mismatch:
        raise ValidationError(
            "the bundled prompt assumes 18+ with age verification; edit the age "
            "clauses in references/drafting-prompt.txt, pass the edited file with "
            "--template, and add --allow-age-gate-mismatch"
        )

    if region == "仅美国":
        region_value = "仅美国"
    elif region.startswith("其他"):
        region_value = region
    else:
        region_value = f"其他：{region}"

    return {
        "app_name": app_name,
        "platforms": platforms,
        "region": region_value,
        "email": email,
        "monetization": monetization,
        "features": features,
        "age_gate": age_gate,
    }


def fill_prompt(template: str, facts: dict) -> str:
    replacements = {
        "{App 名称}": facts["app_name"],
        "{iOS / Google Play / 两者都有}": " + ".join(facts["platforms"]),
        "{仅美国 / 其他：___}": facts["region"],
        "{contact@example.com}": facts["email"],
        "{免费 / 订阅 / 内购 / 广告，可多选}": "、".join(facts["monetization"]),
        "{账号注册登录 / 社交或 UGC / 支付 / AI 生成功能 / 定位 / 相机或麦克风 / 通讯录或相册 / 推送通知 / 健康或健身数据 / 云存储}": " / ".join(
            facts["features"]
        )
        or "无（不使用上述功能）",
    }
    for old, new in replacements.items():
        if old not in template:
            raise ValidationError(
                f"template is missing expected placeholder: {old}; "
                "use the bundled references/drafting-prompt.txt or update the script"
            )
        template = template.replace(old, new)

    leftovers = sorted(set(PLACEHOLDER_RE.findall(template)))
    if leftovers:
        raise ValidationError(
            "template still has unresolved placeholders: " + ", ".join(leftovers)
        )
    return template


def parse_checklist(text: str) -> dict:
    fields: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        for key in (
            "App 名称",
            "联系邮箱",
            "上架平台",
            "商店分发",
            "商业化",
            "年龄门槛",
            "核心功能（是）",
            "数据收集（是）",
            "权限（是）",
        ):
            prefix = key + "："
            if stripped.startswith(prefix):
                fields[key] = stripped[len(prefix) :].strip()
    return fields


def split_items(value: str) -> set[str]:
    if not value or value == "无":
        return set()
    return {item.strip() for item in value.split("、") if item.strip()}


def cross_check(checklist_text: str, facts: dict) -> list[str]:
    warnings: list[str] = []
    fields = parse_checklist(checklist_text)
    if not fields:
        warnings.append(
            "checklist result could not be parsed; confirm it starts with 【App 信息清单】"
        )
        return warnings

    if fields.get("App 名称") != facts["app_name"]:
        raise ValidationError(
            "checklist app name does not match config: "
            f"{fields.get('App 名称')!r} != {facts['app_name']!r}"
        )
    if fields.get("联系邮箱", "").lower() != facts["email"].lower():
        raise ValidationError(
            "checklist contact email does not match config: "
            f"{fields.get('联系邮箱')!r} != {facts['email']!r}"
        )

    checklist_platforms = {
        item.strip() for item in fields.get("上架平台", "").split("+") if item.strip()
    }
    if checklist_platforms and checklist_platforms != set(facts["platforms"]):
        raise ValidationError(
            "checklist platforms do not match config: "
            f"{sorted(checklist_platforms)} != {sorted(facts['platforms'])}"
        )

    checklist_region = fields.get("商店分发", "")
    if checklist_region and checklist_region != facts["region"] and not (
        checklist_region == "其他地区" and facts["region"].startswith("其他")
    ):
        warnings.append(
            f"checklist distribution region ({checklist_region}) differs from "
            f"config ({facts['region']})"
        )

    checklist_modes = split_items(fields.get("商业化", ""))
    if checklist_modes and checklist_modes != set(facts["monetization"]):
        raise ValidationError(
            "checklist monetization does not match config: "
            f"{sorted(checklist_modes)} != {sorted(facts['monetization'])}"
        )

    checklist_feature_names = split_items(fields.get("核心功能（是）", ""))
    unknown = [name for name in checklist_feature_names if name not in CHECKLIST_FEATURES]
    if unknown:
        warnings.append(
            "checklist has feature labels the script does not know: " + ", ".join(unknown)
        )
    mapped_features = {
        CHECKLIST_FEATURES[name] for name in checklist_feature_names if name in CHECKLIST_FEATURES
    }
    if mapped_features != set(facts["features"]):
        raise ValidationError(
            "checklist core features do not match config: "
            f"{sorted(mapped_features)} != {sorted(facts['features'])}"
        )

    if "其他（待补充）" in checklist_text:
        warnings.append(
            "checklist contains '其他（待补充）'; replace it with the actual SDK name "
            "and provider before sending to legal"
        )
    if fields.get("年龄门槛", "").startswith("无限制"):
        warnings.append(
            "checklist says there is no age gate, but the bundled prompt assumes 18+; "
            "edit the prompt's age clauses before generating"
        )
    return warnings


def build_brief(facts: dict, prompt: str, checklist_text: Optional[str]) -> str:
    age_gate = facts["age_gate"]
    if age_gate == "18+":
        age_display = "18+"
    elif age_gate in {"none", "无限制"}:
        age_display = "无限制"
    else:
        age_display = age_gate
    lines = [
        "# App 上架协议审核 · 生成简报",
        "",
        f"- App 名称：{facts['app_name']}",
        f"- 上架平台：{' + '.join(facts['platforms'])}",
        f"- 分发地区：{facts['region']}",
        f"- 联系邮箱：{facts['email']}",
        f"- 商业化：{'、'.join(facts['monetization'])}",
        f"- 年龄门槛：{age_display}",
        f"- 当前版本功能：{' / '.join(facts['features']) or '无（不使用上述功能）'}",
        f"- 生成日期：{dt.date.today().isoformat()}",
        "",
        "> 这是一份提交法务前的初稿材料，不构成法律意见。发布或提审前必须由合格律师复核。",
        "",
        "## 1. 已填充 Prompt",
        "",
        "```text",
        prompt.rstrip(),
        "```",
    ]
    if checklist_text:
        lines += [
            "",
            "## 2. 研发填写清单",
            "",
            "```text",
            checklist_text.rstrip(),
            "```",
        ]
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path, help="JSON file with app facts")
    parser.add_argument("--out", required=True, type=Path, help="markdown brief to write")
    parser.add_argument("--checklist", type=Path, help="text copied from the HTML checklist")
    parser.add_argument(
        "--template",
        type=Path,
        default=DEFAULT_TEMPLATE,
        help="prompt template (default: references/drafting-prompt.txt)",
    )
    parser.add_argument(
        "--allow-age-gate-mismatch",
        action="store_true",
        help="allow a non-18+ age gate after you have edited the template's age clauses",
    )
    args = parser.parse_args()

    if (
        args.allow_age_gate_mismatch
        and args.template.resolve() == DEFAULT_TEMPLATE.resolve()
    ):
        print(
            "warning: --allow-age-gate-mismatch is set but --template is still the "
            "bundled 18+ prompt; confirm its age clauses were edited",
            file=sys.stderr,
        )

    try:
        facts = validate(load_config(args.config), args.allow_age_gate_mismatch)
        if facts["region"] != "仅美国":
            print(
                "warning: the bundled prompt is tuned for the US market; "
                f"distribution region is {facts['region']}",
                file=sys.stderr,
            )
        template = args.template.read_text(encoding="utf-8")
        prompt = fill_prompt(template, facts)

        checklist_text = None
        warnings: list[str] = []
        if args.checklist:
            checklist_text = args.checklist.read_text(encoding="utf-8").strip()
            warnings = cross_check(checklist_text, facts)

        brief = build_brief(facts, prompt, checklist_text)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(brief, encoding="utf-8")
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except ValidationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(f"wrote {args.out}")
    if checklist_text:
        print("checklist appended and cross-checked against config")
    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
