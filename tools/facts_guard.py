#!/usr/bin/env python3
"""Compare a chapter with its last committed version: numbers, record IDs and citation marks must not change.

Usage: python3 tools/facts_guard.py <章号>   (exit 1 when a fact token was added or removed)
"""
import collections, glob, re, subprocess, sys

f = glob.glob(f"book/{int(sys.argv[1]):02d}-*.md")[0]
old = subprocess.run(["git", "show", f"HEAD:{f}"], capture_output=True, text=True, check=True).stdout
strip = lambda t: re.sub(r"(?m)^\s*\d+\. ", "", re.sub(r"(?s)```mermaid.*?```", "", t))  # list numbers and replaced diagrams are not facts
tok = lambda t: collections.Counter(re.findall(r"\[\d+\]|[A-Za-z课堂虚构批次]*-?[A-Z]{1,3}-?\d[\d-]*|\d+(?:\.\d+)?", t))
a, b = tok(strip(old)), tok(strip(open(f, encoding="utf-8").read()))
gone, new = a - b, b - a
# chapter-internal references such as 1.1 or 例 1-2 may legitimately move; report everything, fail on any change
print(f, "removed:", dict(gone), "added:", dict(new))
sys.exit(1 if gone or new else 0)
