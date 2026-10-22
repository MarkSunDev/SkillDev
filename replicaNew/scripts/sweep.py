#!/usr/bin/env python3
"""replicaNew 残留扫描器：检查新项目里是否还残留原项目的痕迹。

用法（在新项目根目录下）:
    python3 sweep.py . --config replica/origin.json
    python3 sweep.py . --names "Kira,buzzme" --packages "com.kira.app" \
        --domains "kira-api.com" --keys "AIzaSyxxxx,umeng_appkey"
    python3 sweep.py . --config replica/origin.json \
        --allow-glob "*proto*" --allow-glob "app-config.json"

--config 读 JSON: {"names": [], "packages": [], "domains": [],
"colors": [], "keys": [], "certs": []}，由 spec 阶段自动生成到
replica/origin.json，扫描前先补全。

--allow-glob：豁免"契约/生成文件"（proto、生成代码、集中配置文件）。豁免不是隐藏：
报告会单独列出豁免文件数，audit 阶段必须把这些规则和理由写进报告。注释里提到原项目
名字（"对齐 Kira""移植自 Kira"）永远不豁免——那是真实指纹。

会检查: 文件内容、文件名/目录名（包括标识符内部的残留，如 KiraApiService）、
十六进制颜色（含缩写形式 #06f）、硬编码的 appKey/token 串、签名证书引用。

跳过: .git/.gradle/.idea/build 等构建产物、二进制文件、replica/ 规划目录。
退出码 1 表示有残留，可以挂在 CI 上阻断发布。
"""

import argparse
import fnmatch
import json
import os
import re
import sys

SKIP_DIRS = {".git", ".gradle", ".idea", ".kotlin", "build", "outputs", ".cra",
             "node_modules", "__pycache__", ".trae", ".DS_Store"}
SKIP_FILES = {"local.properties", ".gitignore"}
BINARY_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".icns", ".pdf",
              ".zip", ".gz", ".jar", ".so", ".dylib", ".apk", ".aab", ".keystore",
              ".jks", ".ttf", ".otf", ".mp4", ".mp3", ".wav", ".psd", ".sketch"}
HEX_COLOR = re.compile(r"#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})(?![0-9a-zA-Z])")
KEY_MIN_LEN = 12  # 短于这个长度的"key"误报太多


def norm_hex(h):
    h = h.lower().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return "#" + h


def name_patterns(names):
    """'Kira Chat' 也要命中 KiraChat、kira_chat、kira-chat。"""
    pats = []
    for name in names:
        name = name.strip()
        if not name:
            continue
        parts = [re.escape(p) for p in re.split(r"[\s._-]+", name) if p]
        pats.append(("name", name, re.compile(r"[\s._-]?".join(parts), re.I)))
    return pats


def literal_patterns(packages, domains, keys, certs):
    pats = []
    for p in packages:
        if p.strip():
            pats.append(("package", p.strip(), re.compile(re.escape(p.strip()), re.I)))
    for d in domains:
        d = d.strip().lower()
        if d:
            pats.append(("domain", d, re.compile(re.escape(d), re.I)))
    for k in keys:
        k = k.strip()
        if len(k) >= KEY_MIN_LEN:
            pats.append(("key", k[:8] + "...", re.compile(re.escape(k))))
    for c in certs:
        c = c.strip()
        if c:
            pats.append(("cert", c, re.compile(re.escape(c), re.I)))
    return pats


def is_binary(path):
    if os.path.splitext(path)[1].lower() in BINARY_EXT:
        return True
    try:
        with open(path, "rb") as fh:
            return b"\0" in fh.read(4096)
    except OSError:
        return True


def sweep(root, cfg, allow_globs=(), allow_values=()):
    pats = (name_patterns(cfg.get("names", []))
            + literal_patterns(cfg.get("packages", []), cfg.get("domains", []),
                               cfg.get("keys", []), cfg.get("certs", [])))
    colors = {norm_hex(c) for c in cfg.get("colors", []) if HEX_COLOR.fullmatch(c.strip())}
    allow_values = {v.strip().lower() for v in allow_values if v.strip()}
    hits = []
    allowed_files = 0
    allowed_occurrences = 0
    root = os.path.abspath(root)
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        keep = []
        for d in dirnames:
            if d in SKIP_DIRS:
                continue
            if d == "replica" and rel_dir == ".":
                continue
            keep.append(d)
        dirnames[:] = sorted(keep)
        for d in dirnames:
            for kind, label, rx in pats:
                if rx.search(d):
                    hits.append({"file": os.path.join(rel_dir, d) + "/",
                                 "line": 0, "kind": "path", "match": label,
                                 "text": "目录名残留"})
        for fn in sorted(filenames):
            if fn in SKIP_FILES:
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.normpath(os.path.join(rel_dir, fn))
            if any(fnmatch.fnmatch(rel, pat) for pat in allow_globs):
                allowed_files += 1
                continue
            for kind, label, rx in pats:
                if rx.search(fn):
                    hits.append({"file": rel, "line": 0, "kind": "path",
                                 "match": label, "text": "文件名残留"})
            try:
                if os.path.getsize(path) > 2_000_000 or is_binary(path):
                    continue
                with open(path, encoding="utf-8", errors="replace") as fh:
                    lines = fh.readlines()
            except OSError:
                continue
            for i, line in enumerate(lines, 1):
                for kind, label, rx in pats:
                    if rx.search(line):
                        if label.lower() in allow_values:
                            allowed_occurrences += 1
                            continue
                        hits.append({"file": rel, "line": i, "kind": kind,
                                     "match": label, "text": line.strip()[:160]})
                if colors:
                    for m in HEX_COLOR.finditer(line):
                        if norm_hex(m.group(0)) in colors:
                            if norm_hex(m.group(0)).lower() in allow_values:
                                allowed_occurrences += 1
                                continue
                            hits.append({"file": rel, "line": i, "kind": "color",
                                         "match": norm_hex(m.group(0)),
                                         "text": line.strip()[:160]})
    return hits, allowed_files, allowed_occurrences


def render(hits, allowed_files=0, allowed_occurrences=0):
    allowed_note = ""
    if allowed_files:
        allowed_note += ("\n另有 %d 个契约/生成文件按 --allow-glob 豁免"
                         "（规则与理由须写进 audit 报告）。" % allowed_files)
    if allowed_occurrences:
        allowed_note += ("\n另有 %d 处按 --allow-value 豁免（仅限契约值，"
                         "须在 audit 报告里列出）。" % allowed_occurrences)
    if not hits:
        return "干净。未发现原项目的名字、包名、域名、颜色、key 或证书残留。" + allowed_note
    out = []
    by_kind = {}
    for h in hits:
        by_kind.setdefault(h["kind"], 0)
        by_kind[h["kind"]] += 1
        loc = h["file"] if not h["line"] else "%s:%d" % (h["file"], h["line"])
        out.append("%-8s %-22s %s  %s" % (h["kind"], h["match"][:22], loc, h["text"]))
    out.append("")
    out.append("共 %d 处残留（%s）。全部清掉之前不许打包。" %
               (len(hits), ", ".join("%s %d" % kv for kv in sorted(by_kind.items())))
               + allowed_note)
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="扫描新项目中原项目的残留痕迹")
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--config", help="JSON 配置（replica/origin.json）")
    ap.add_argument("--names", default="", help="逗号分隔: 原 App 名")
    ap.add_argument("--packages", default="", help="逗号分隔: 原包名")
    ap.add_argument("--domains", default="", help="逗号分隔: 原 API/CDN 域名")
    ap.add_argument("--keys", default="", help="逗号分隔: 原 SDK appKey")
    ap.add_argument("--colors", default="", help="逗号分隔: 原品牌色(十六进制)")
    ap.add_argument("--certs", default="", help="逗号分隔: 原 keystore 路径/别名")
    ap.add_argument("--allow-glob", action="append", default=[],
                    help="豁免匹配的文件（契约/生成代码），可重复。如 '*proto*'")
    ap.add_argument("--allow-value", action="append", default=[],
                    help="豁免具体的契约值（如服务端 proto 包名 com.pserver），可重复；"
                         "不允许豁免原 App 名")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    cfg = {}
    if args.config:
        try:
            with open(args.config, encoding="utf-8") as fh:
                cfg = json.load(fh)
        except (OSError, ValueError) as exc:
            print("sweep: %s" % exc, file=sys.stderr)
            return 2
    for field, arg in [("names", args.names), ("packages", args.packages),
                       ("domains", args.domains), ("keys", args.keys),
                       ("colors", args.colors), ("certs", args.certs)]:
        cfg.setdefault(field, [])
        cfg[field] += [x for x in arg.split(",") if x.strip()]
    if not any(cfg.values()):
        print("sweep: 没有可查的模式。先填 replica/origin.json 或传 --names。", file=sys.stderr)
        return 2
    names_lower = {n.strip().lower() for n in cfg.get("names", []) if n.strip()}
    bad_names = [v for v in args.allow_value if v.strip().lower() in names_lower]
    if bad_names:
        print("sweep: 不允许用 --allow-value 豁免原 App 名（会隐藏真实指纹）: %s"
              % ", ".join(bad_names), file=sys.stderr)
        return 2
    broad = [p for p in args.allow_glob if p.strip() in {"*", "**", "*/*"}]
    if broad:
        print("sweep: --allow-glob 不能是通配全部文件: %s" % ", ".join(broad), file=sys.stderr)
        return 2
    hits, allowed_files, allowed_occ = sweep(args.root, cfg, args.allow_glob, args.allow_value)
    if args.json:
        print(json.dumps({"hits": hits, "allowedFiles": allowed_files,
                          "allowedOccurrences": allowed_occ}, indent=2, ensure_ascii=False))
    else:
        print(render(hits, allowed_files, allowed_occ))
    return 1 if hits else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        sys.exit(0)
