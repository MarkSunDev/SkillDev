#!/usr/bin/env python3
"""replicaNew design token 对比度校验（WCAG）。

用法:
    python3 contrast.py replica/design/tokens.json
    python3 contrast.py tokens.json --pretty

tokens.json 里 colors 是角色表，pairs 是要校验的前景/背景组合，fg/bg 可写角色名
或直接十六进制色值。level 三档: AA(正文 4.5:1)、AA_LARGE(大字/加粗大字 3:1)、
COMPONENT(非文本控件 3:1)。任何一对不达标 exit 1，可挂 CI。
"""

import argparse
import json
import sys

LEVELS = {"AA": 4.5, "AA_LARGE": 3.0, "COMPONENT": 3.0}


def parse_hex(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        raise ValueError("非法颜色: %s" % h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def luminance(rgb):
    def chan(c):
        c = c / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (chan(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(fg, bg):
    lf, lb = luminance(fg), luminance(bg)
    hi, lo = max(lf, lb), min(lf, lb)
    return (hi + 0.05) / (lo + 0.05)


def resolve(ref, colors):
    ref = str(ref).strip()
    return parse_hex(colors.get(ref, ref))


def main(argv=None):
    ap = argparse.ArgumentParser(description="校验 design tokens 的 WCAG 对比度")
    ap.add_argument("tokens", help="tokens.json 路径")
    ap.add_argument("--pretty", action="store_true", help="只打表不退出非零")
    args = ap.parse_args(argv)
    try:
        with open(args.tokens, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        print("contrast: %s" % exc, file=sys.stderr)
        return 2
    colors = data.get("colors", {})
    pairs = data.get("pairs", [])
    if not pairs:
        print("contrast: tokens.json 没有 pairs 数组，没东西可校验", file=sys.stderr)
        return 2
    failures = []
    print("%-28s %-9s %-9s %-8s %s" % ("pair", "fg", "bg", "ratio", "level"))
    for p in pairs:
        name = p.get("name", "?")
        level = p.get("level", "AA")
        need = LEVELS.get(level)
        if need is None:
            print("%-28s level 非法: %s（用 AA/AA_LARGE/COMPONENT）" % (name, level))
            failures.append(p)
            continue
        try:
            fg = resolve(p["fg"], colors)
            bg = resolve(p["bg"], colors)
        except (KeyError, ValueError) as exc:
            print("%-28s 解析失败: %s" % (name, exc))
            failures.append(p)
            continue
        r = ratio(fg, bg)
        ok = r >= need
        print("%-28s %-9s %-9s %6.2f:1  %s %s" %
              (name, p["fg"], p["bg"], r, level, "OK" if ok else "FAIL"))
        if not ok:
            failures.append(p)
    print("")
    if failures:
        print("%d/%d 对不达标。" % (len(failures), len(pairs)))
        print("在 tokens.json 里改值，不要在组件里绕过。")
        return 0 if args.pretty else 1
    print("全部 %d 对达标。" % len(pairs))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        sys.exit(0)
