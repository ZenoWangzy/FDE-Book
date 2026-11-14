#!/usr/bin/env python3
"""Supervisor bookkeeping after a chapter passes review (textbook skill, stage 4 steps 4-5).

Usage: python3 tools/accept_chapter.py <章号>
Runs check_chapter first, then appends the writer report into 术语表.md, 98-参考答案.md and
00-教材设计.md, and advances .progress.json. Refuses to run twice for the same chapter.
"""
import glob, json, re, subprocess, sys, datetime

n = int(sys.argv[1])
if subprocess.run([sys.executable, "tools/check_chapter.py", str(n)]).returncode:
    sys.exit("check_chapter failed; not accepting")
prog = json.load(open("book/.progress.json"))
assert prog["chapters"]["next"] == n and n not in prog["chapters"]["done"], "chapter is not the next one"
title = glob.glob(f"book/{n:02d}-*.md")[0].split("-", 1)[1][:-3]
rep = open(f".scratch/fde-textbook/runs/ch{n:02d}.report.md", encoding="utf-8").read()


def sec(name):
    return rep.split(f"## {name}", 1)[1].split("\n## ", 1)[0].strip()


def rows(name):
    return [l for l in sec(name).splitlines() if l.startswith("|")][2:]


def insert_rows(text, heading, new):
    head, rest = text.split(heading, 1)
    body, sep, tail = rest.partition("\n## ")
    return head + heading + body.rstrip("\n") + "\n" + "\n".join(new) + "\n" + (sep + tail if sep else "")


g = open("book/术语表.md", encoding="utf-8").read()
known = set(re.findall(r"(?m)^\| ([^|]+?) \|", g))
terms = [r for r in rows("新增术语") if r.split("|")[1].strip() not in known]
g = insert_rows(g, "## 术语", terms) if terms else g
g = insert_rows(g, "## 引文台账", rows("引文台账"))
open("book/术语表.md", "w", encoding="utf-8").write(g)

ans = sec("本章独立习题答案")
assert len(re.findall(rf"(?m)^#### 习题 {n}-\d+", ans)) == 4
p = "book/98-参考答案.md"
try:
    a = open(p, encoding="utf-8").read()
except FileNotFoundError:
    a = "# 参考答案\n\n> 建议先独立完成习题再对照。范例研读与引导分析的完整解答在各章正文内。\n"
assert f"## 第 {n} 章" not in a
open(p, "w", encoding="utf-8").write(a.rstrip("\n") + f"\n\n## 第 {n} 章 {title}\n\n{ans}\n")

d = open("book/00-教材设计.md", encoding="utf-8").read()
actual = "；".join(f"{r.split('|')[1].strip()} {r.split('|')[3].strip()}" for r in rows("Bloom标注回写"))
head = f"**第 {n} 章 {title}**\n\n- 范例研读"
assert head in d, "exercise plan heading not found"
d = d.replace(head, f"**第 {n} 章 {title}**\n\n> 实际层级：{actual}\n\n- 范例研读")
use = "\n".join(rows("素材使用记录"))
mark = "\n## 二、UbD 五件套（已确认）"
if "### 素材使用记录" not in d:
    d = d.replace(mark, "\n### 素材使用记录\n" + mark)
d = d.replace(mark, f"\n**第 {n} 章**\n\n| 产出位置 | 素材ID | 原文位置 | 使用方式 | 待核事项 |\n|---|---|---|---|---|\n{use}\n" + mark)
open("book/00-教材设计.md", "w", encoding="utf-8").write(d)

prog["chapters"]["done"].append(n)
prog["chapters"]["next"] = n + 1
if n == prog["chapters"]["total"]:
    prog["current_stage"] = 5
prog["updated_at"] = datetime.date.today().isoformat()
json.dump(prog, open("book/.progress.json", "w"), ensure_ascii=False, indent=2)
print(f"accepted chapter {n}: {len(terms)} terms, 4 answers, next={prog['chapters']['next']}")
