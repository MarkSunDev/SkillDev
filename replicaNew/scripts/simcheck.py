#!/usr/bin/env python3
"""replicaNew 代码相似度检查器：量化"新项目有多少代码可以追溯到原项目"。

用法:
    python3 simcheck.py /path/to/origin-project /path/to/new-project
    python3 simcheck.py a b --threshold 0.10 --markdown > replica/similarity.md
    python3 simcheck.py a b --exclude-glob '*proto*' --exclude-glob '*generated*'
    python3 simcheck.py a b --ext kt,java        # 只比代码，不把 XML 资源算进来

原理（JPlag/MOSS 的简化版，纯标准库）:
    1. 收集两边 src/ 下的 .kt/.java/.xml 源文件（跳过 build、.git、res 里二进制）
    2. 归一化: 去注释、去 import/package 行、字符串/数字换成占位符——
       这样"改了字符串/常量但结构照抄"依然会被抓到，而真正的重写不会误伤
    3. 词法切分成 token 流，取 8-gram 集合
    4. 主指标 containment = |新∩原| / |新|：新项目里有多少 8-gram 在原项目出现过。
       这是复刻验收要压到接近 0 的数字
    5. 倒排索引做逐文件配对，列出高重合文件对和最高频的共享代码块

注意: 高频样板（协程模板、Retrofit 声明、Compose 组合）会贡献少量天然重合，
所以 5% 以内通常可接受；containment > 15% 或出现整文件级配对就是照抄。
"""

import argparse
import fnmatch
import hashlib
import os
import re
import sys
from collections import Counter, defaultdict

SKIP_DIRS = {".git", ".gradle", ".idea", ".kotlin", "build", "outputs",
             "node_modules", "__pycache__", ".trae", "testFixtures"}
N = 8

COMMENT_BLOCK = re.compile(r"/\*.*?\*/|<!--.*?-->", re.S)
COMMENT_LINE = re.compile(r"//[^\n]*")
IMPORT_LINE = re.compile(r"^\s*(import|package)\s", re.M)
LITERAL_STR = re.compile(r"""'(?:\\.|[^'\\])*'|"(?:\\.|[^"\\])*\"""")
LITERAL_NUM = re.compile(r"\b\d[\d._a-fA-FxL]*\b")
TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|[^\s]")


def strip_code(text):
    text = COMMENT_BLOCK.sub(" ", text)
    text = COMMENT_LINE.sub(" ", text)
    text = IMPORT_LINE.sub(" ", text)
    text = LITERAL_STR.sub("«S»", text)
    text = LITERAL_NUM.sub("«N»", text)
    return TOKEN.findall(text)


def collect(root, excludes=(), exts=(".kt", ".java", ".xml")):
    files = {}
    skipped = 0
    root = os.path.abspath(root)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for fn in sorted(filenames):
            if os.path.splitext(fn)[1].lower() not in exts:
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, root)
            if any(fnmatch.fnmatch(rel, pat) for pat in excludes):
                skipped += 1
                continue
            try:
                with open(path, encoding="utf-8", errors="replace") as fh:
                    toks = strip_code(fh.read())
            except OSError:
                continue
            if len(toks) >= N:
                files[rel] = toks
    return files, skipped


def ngrams(toks, n=N):
    out = set()
    for i in range(len(toks) - n + 1):
        g = " ".join(toks[i:i + n])
        out.add(hashlib.blake2b(g.encode(), digest_size=8).hexdigest())
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="对比两个 Android 项目的代码相似度")
    ap.add_argument("origin", help="原项目根目录")
    ap.add_argument("new", help="新项目根目录")
    ap.add_argument("--threshold", type=float, default=0.08,
                    help="containment 超过此值判定失败（默认 0.08）")
    ap.add_argument("--top", type=int, default=25, help="列出前 N 个可疑文件对")
    ap.add_argument("--exclude-glob", action="append", default=[],
                    help="排除匹配的文件，可重复。如 '*proto*' '*generated*'（契约/生成代码）")
    ap.add_argument("--ext", default="kt,java,xml",
                    help="参与统计的扩展名，逗号分隔（默认 kt,java,xml；只查代码用 kt,java）")
    ap.add_argument("--markdown", action="store_true")
    args = ap.parse_args(argv)
    exts = tuple("." + e.strip().lstrip(".") for e in args.ext.split(",") if e.strip())

    orig_files, orig_skipped = collect(args.origin, args.exclude_glob, exts)
    new_files, new_skipped = collect(args.new, args.exclude_glob, exts)
    if not orig_files or not new_files:
        print("simcheck: 两边都要有源文件（.kt/.java/.xml）", file=sys.stderr)
        return 2

    orig_grams = {f: ngrams(t) for f, t in orig_files.items()}
    new_grams = {f: ngrams(t) for f, t in new_files.items()}

    orig_all = set().union(*orig_grams.values())
    new_all = set().union(*new_grams.values())
    inter = orig_all & new_all
    containment = len(inter) / len(new_all) if new_all else 0.0

    # 倒排索引: gram -> 出现它的原项目文件
    index = defaultdict(list)
    for f, gs in orig_grams.items():
        for g in gs:
            index[g].append(f)

    pairs = []
    shared_counter = Counter()
    for nf, gs in new_grams.items():
        # 跳过微小样板文件（空 manifest 等），只看真代码
        if len(new_files[nf]) < 30:
            continue
        hits = Counter()
        for g in gs:
            if g in index:
                for of in index[g]:
                    if len(orig_files[of]) >= 30:
                        hits[of] += 1
                shared_counter[g] += 1
        for of, cnt in hits.items():
            cov = cnt / len(gs)
            if cov >= 0.20:
                pairs.append((cov, nf, of, cnt, len(gs)))
    pairs.sort(reverse=True)

    # 定位最高频共享 gram 的原文片段，便于人工检查
    gram_text = {}
    if shared_counter:
        for g, _ in shared_counter.most_common(10):
            for f, toks in orig_files.items():
                joined = " ".join(toks)
                if ngrams(toks) and g in orig_grams[f]:
                    i = None
                    for j in range(len(toks) - N + 1):
                        if hashlib.blake2b(" ".join(toks[j:j + N]).encode(),
                                           digest_size=8).hexdigest() == g:
                            i = j
                            break
                    if i is not None:
                        gram_text[g] = " ".join(toks[max(0, i - 2):i + N + 2])
                        break

    verdict = "通过" if containment <= args.threshold else "不通过"
    lines = []
    lines.append("# simcheck 相似度报告")
    lines.append("")
    lines.append("- 原项目: %s（%d 个源文件, %d 个 %d-gram%s）" %
                 (args.origin, len(orig_files), len(orig_all), N,
                  "，排除 %d 个文件" % orig_skipped if orig_skipped else ""))
    lines.append("- 新项目: %s（%d 个源文件, %d 个 %d-gram%s）" %
                 (args.new, len(new_files), len(new_all), N,
                  "，排除 %d 个文件" % new_skipped if new_skipped else ""))
    if args.exclude_glob:
        lines.append("- 排除规则（契约/生成代码，须在 audit 报告里单独说明）: %s" %
                     ", ".join(args.exclude_glob))
    lines.append("- **containment（新项目可溯源到原项目的比例）: %.1f%%**（阈值 %.1f%%，%s）" %
                 (containment * 100, args.threshold * 100, verdict))
    lines.append("")
    if pairs:
        lines.append("## 可疑文件对（单文件重合 ≥ 20%%）")
        lines.append("")
        lines.append("| 重合度 | 新项目文件 | 原项目文件 | 共享gram/新文件gram |")
        lines.append("| --- | --- | --- | --- |")
        for cov, nf, of, cnt, tot in pairs[:args.top]:
            lines.append("| %.0f%% | %s | %s | %d/%d |" % (cov * 100, nf, of, cnt, tot))
    else:
        lines.append("## 可疑文件对: 无（没有任何新文件与原文件重合 ≥ 20%）")
    lines.append("")
    if shared_counter:
        lines.append("## 高频共享代码块（前 10，多为照抄的工具函数/模板）")
        lines.append("")
        for g, c in shared_counter.most_common(10):
            frag = gram_text.get(g, "?")
            lines.append("- ×%d: `%s`" % (c, frag[:120]))
    lines.append("")
    print("\n".join(lines))

    return 1 if containment > args.threshold else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        sys.exit(0)
