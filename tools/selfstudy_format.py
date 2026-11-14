#!/usr/bin/env python3
"""One-off, idempotent: make chapter scaffolding friendlier for a student reading alone (ADR-0006).

Renames the four section titles, moves Bloom tags out of headings into HTML comments,
folds author verification records in the examples, and points N.4 at the answer file.
Usage: python3 tools/selfstudy_format.py
"""
import glob, re

NAMES = {"概念与脉络讲解": "先弄明白", "范例研读": "看例子", "引导分析": "跟着练", "独立论述与探究": "自己做"}
for f in sorted(glob.glob("book/[0-9][0-9]-*.md")):
    n = int(f[5:7])
    if n == 0 or n > 12:
        continue
    t = open(f, encoding="utf-8").read()
    for i, (old, new) in enumerate(NAMES.items(), 1):
        t = t.replace(f"## {n}.{i} {old}", f"## {n}.{i} {new}")
    t = re.sub(r"(?m)^(#+ .*?)【Bloom：(\S+?)】[ \t]*$", r"\1\n<!-- Bloom：\2 -->", t)
    t = t.replace("**与持久理解的呼应**", "**和全书主线的关系**")
    t = re.sub(r"（仅借鉴观点；[^）]*许可。）", "", t)
    a, b = f"## {n}.2 看例子", f"## {n}.3 跟着练"
    head, ex, rest = t.split(a)[0], t.split(a)[1].split(b)[0], b + t.split(b)[1]
    if "<summary>这个答案是怎么核对的</summary>" not in ex:
        ex = re.sub(r"(?ms)^(\*\*验证\*\*：[^\n]*\n\n```text\n.*?\n```)\n",
                    r"<details><summary>这个答案是怎么核对的</summary>\n\n\1\n\n</details>\n", ex)
    t = head + a + ex + rest
    tip = "先自己做，做完再翻到 [98-参考答案.md](98-参考答案.md) 对照。\n"
    h4 = f"## {n}.4 自己做\n"
    if tip not in t:
        t = t.replace(h4, h4 + "\n" + tip, 1)
    open(f, "w", encoding="utf-8").write(t)
    print(f, t.count("<!-- Bloom"), t.count("这个答案是怎么核对的"))

f = "book/98-参考答案.md"
t = open(f, encoding="utf-8").read()
t = re.sub(r"(?m)^(#+ .*?)【Bloom：(\S+?)】[ \t]*$", r"\1\n<!-- Bloom：\2 -->", t)
open(f, "w", encoding="utf-8").write(t)
