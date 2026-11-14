#!/usr/bin/env python3
"""Replace the first mermaid diagram of a chapter with its picture book/图/图N-1.jpg (ADR-0006).

Usage: python3 tools/use_figure.py <章号>   (idempotent; the picture file must exist)
"""
import glob, os, re, sys

n = int(sys.argv[1])
f = glob.glob(f"book/{n:02d}-*.md")[0]
img = f"图/图{n}-1.jpg"
assert os.path.exists("book/" + img), img
t = open(f, encoding="utf-8").read()
if img in t:
    sys.exit(0)
cap = re.search(rf"(?m)^\*图 {n}-1：(.*?)\*$", t)
alt = f"图 {n}-1：{cap.group(1)}" if cap else f"图 {n}-1"
t, k = re.subn(r"(?s)```mermaid\n.*?\n```", f"![{alt}]({img})", t, count=1)
assert k == 1, "no mermaid block"
open(f, "w", encoding="utf-8").write(t)
print(f, "->", img)
