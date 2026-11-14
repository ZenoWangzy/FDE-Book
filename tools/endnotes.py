#!/usr/bin/env python3
"""One-off, idempotent (ADR-0006, author 2026-11-14): move every chapter's reference list to book/参考文献.md,
drop in-text [n] marks, and drop the 「⚠️ 需作者确认」 marks. Usage: python3 tools/endnotes.py
"""
import glob, re

MARK = re.compile(r"[ \t]*(?:\[\d+\])(?:[、，,]?\[\d+\])*")


def clean(t, n):
    t = re.sub(r"参考文献 ?\[(\d+)\]", rf"书末参考文献第 {n} 章第 \1 条", t)
    t = MARK.sub("", t)
    t = re.sub(r"\*\*验证\*\*：⚠️ 需作者确认（([^）]*)）", r"**验证**：\1", t)
    t = re.sub(r"(?m)^- ⚠️ 需作者确认（[^）]*）：", "- ", t)
    t = re.sub(r"[ \t]*⚠️ 需作者确认（[^）]*）。?", "", t)
    return t


out = ["# 参考文献", "",
       "本书借鉴的资料都列在这里，按章排列，著录格式按 GB/T 7714—2015。正文里不再逐处标注编号。"
       "每份资料借鉴了什么、许可怎样，见 [附录B-借鉴说明.md](附录B-借鉴说明.md)。", ""]
for f in sorted(glob.glob("book/[01][0-9]-*.md")):
    n = int(f[5:7])
    if n == 0:
        continue
    t = open(f, encoding="utf-8").read()
    title = t.splitlines()[0].lstrip("# ").strip()
    if "\n## 参考文献" in t:
        body, refs = t.split("\n## 参考文献", 1)
        entries = [re.sub(r"^\[(\d+)\]", r"\1.", l.strip()) for l in refs.splitlines() if re.match(r"\[\d+\]", l.strip())]
        assert entries, f
        out += [f"## {title}", ""] + entries + [""]
        t = body.rstrip() + "\n"
    else:
        old = open("book/参考文献.md", encoding="utf-8").read()
        sec = old.split(f"## {title}\n", 1)[1].split("\n## ", 1)[0].strip().splitlines()
        out += [f"## {title}", ""] + [l for l in sec if l.strip()] + [""]
    open(f, "w", encoding="utf-8").write(clean(t, n))
open("book/参考文献.md", "w", encoding="utf-8").write("\n".join(out))

f = "book/98-参考答案.md"
parts = re.split(r"(?m)^(?=## 第 \d+ 章)", open(f, encoding="utf-8").read())
open(f, "w", encoding="utf-8").write("".join(
    clean(p, int(re.match(r"## 第 (\d+) 章", p).group(1))) if p.startswith("## 第") else p for p in parts))
for f in ("book/附录A-dsh安装说明.md", "book/素材/课堂数据集.md"):
    t = open(f, encoding="utf-8").read()
    open(f, "w", encoding="utf-8").write(clean(t, 0))
f = "book/术语表.md"
t = open(f, encoding="utf-8").read()
if "\n## 引文台账" in t:
    open(f, "w", encoding="utf-8").write(t.split("\n## 引文台账")[0].rstrip() + "\n")
