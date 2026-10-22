#!/usr/bin/env python3
"""legalH5 烘焙脚本：把 site.json 烘进三张模板，输出 dist/。

用法:
    python3 scripts/build.py site.json            # 烘焙到 dist/
    python3 scripts/build.py site.json --check    # 只校验配置与占位符

规则: 模板里 {{KEY}} 占位符必须全部被解析；任何未识别占位符或缺失配置
都会报错并 exit 1（宁可不产出，不产出半成品页面）。
"""

import argparse
import json
import os
import re
import sys

PAGES = ["privacy.html", "terms.html", "delete-account.html"]
PLACEHOLDER = re.compile(r"\{\{\s*([A-Z_][A-Z0-9_]*)\s*\}\}")


def build_vars(cfg):
    pages = cfg.get("pages", {})
    legal = {
        "PRIVACY_URL": "%s://%s%s" % (cfg.get("scheme", "https"),
                                      cfg["domain"], pages.get("privacy", "/privacy")),
        "TERMS_URL": "%s://%s%s" % (cfg.get("scheme", "https"),
                                    cfg["domain"], pages.get("terms", "/terms")),
        "DELETE_URL": "%s://%s%s" % (cfg.get("scheme", "https"), cfg["domain"],
                                     pages.get("delete-account", "/delete-account")),
    }
    flat = {
        "APP_NAME": cfg["appName"],
        "CONTACT_EMAIL": cfg["contactEmail"],
        "DOMAIN": cfg["domain"],
        "EFFECTIVE_DATE": cfg["effectiveDate"],
        "VERSION": cfg.get("version", "1.0"),
        "REGION": cfg.get("region", "United States"),
        "AGE_GATE": cfg.get("ageGate", "18+"),
    }
    flat.update(legal)
    return flat


def bake(text, vars_, where):
    missing = []

    def sub(m):
        key = m.group(1)
        if key in vars_:
            return str(vars_[key])
        missing.append(key)
        return m.group(0)

    out = PLACEHOLDER.sub(sub, text)
    if missing:
        raise SystemExit("build: %s 有未解析占位符: %s（检查 site.json）"
                         % (where, sorted(set(missing))))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="legalH5 烘焙脚本")
    ap.add_argument("config", help="site.json 路径")
    ap.add_argument("--check", action="store_true", help="只校验不写文件")
    args = ap.parse_args(argv)
    try:
        with open(args.config, encoding="utf-8") as fh:
            cfg = json.load(fh)
    except (OSError, ValueError) as exc:
        print("build: %s" % exc, file=sys.stderr)
        return 2
    for key in ("domain", "appName", "contactEmail", "effectiveDate"):
        if not cfg.get(key):
            print("build: site.json 缺少必填字段 %s" % key, file=sys.stderr)
            return 2
    if "@" not in cfg["contactEmail"]:
        print("build: contactEmail 不是有效邮箱: %s" % cfg["contactEmail"], file=sys.stderr)
        return 2

    root = os.path.dirname(os.path.abspath(args.config))
    tpl_dir = os.path.join(root, "templates")
    out_dir = os.path.join(root, cfg.get("paths", {}).get("outDir", "dist"))
    vars_ = build_vars(cfg)

    baked = {}
    for page in PAGES:
        tpl_path = os.path.join(tpl_dir, page)
        if not os.path.isfile(tpl_path):
            print("build: 缺模板 %s" % tpl_path, file=sys.stderr)
            return 2
        with open(tpl_path, encoding="utf-8") as fh:
            baked[page] = bake(fh.read(), vars_, page)

    if args.check:
        print("check: 三页占位符全部解析通过，未写出文件。")
        return 0

    os.makedirs(out_dir, exist_ok=True)
    for page, html in baked.items():
        with open(os.path.join(out_dir, page), "w", encoding="utf-8") as fh:
            fh.write(html)
        print("baked: %s" % os.path.join(out_dir, page))
    print("done: 上传 %s 目录到 %s 即生效。" % (out_dir, vars_["PRIVACY_URL"]))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        sys.exit(0)
