#!/usr/bin/env python3
"""Print the textbook-chapter input contract for one chapter, cut from book/00-教材设计.md.

Usage: python3 tools/chapter_slice.py <章号>
Only that chapter's slice is printed (context isolation, see the textbook skill's handoff contract).
"""
import glob, re, sys

n = int(sys.argv[1])
design = open("book/00-教材设计.md", encoding="utf-8").read()


def section(text, start, stop):
    body = text.split(start, 1)[1]
    return body.split(stop, 1)[0].strip() if stop in body else body.strip()


ubd = section(design, "## 二、UbD 五件套（已确认）", "## 三、")
tree = section(design, "### 章节树", "**对齐检查")
row = next(l for l in tree.splitlines() if l.startswith(f"| {n:02d} |"))
title = row.split("|")[2].strip()
goal_ids = re.findall(r"O\d+", row.split("|")[5])
goals = [l for l in section(ubd, "### 学习目标", "层级分布").splitlines() if re.match(r"\| O\d+ ", l) and l.split("|")[1].strip() in goal_ids]
assert len(goals) == len(goal_ids), "learning objective missing from section 二"
head = f"**第 {n} 章 {title}**"
lab = section(design.split("### 各章「本周实训」和素材", 1)[1], head, "\n**第")
lab = lab.split("### 例题习题计划")[0].strip()
plan = section(design.split("### 例题习题计划", 1)[1], head, "\n**第")
plan = plan.split("### 全书 Bloom 梯度报告")[0].strip()
assert plan.count("\n") == 7, "expected 8 planned items"
nxt = next((l for l in tree.splitlines() if l.startswith(f"| {n+1:02d} |")), None)
nxt = f"第 {n+1} 章《{nxt.split(chr(124))[2].strip()}》：{nxt.split(chr(124))[3].strip()}" if nxt else "（本章是最后一章，预告改为全书收束语）"
prev = ""
if n > 1:
    files = glob.glob(f"book/{n-1:02d}-*.md")
    assert files, "previous chapter file missing"
    prev = "## 本章小结" + section(open(files[0], encoding="utf-8").read(), "## 本章小结", "\n## ")

# Chapters 7-12 share one classroom dataset so every chapter uses the same goods and numbers.
data = "\n## 课堂数据集（第 7–12 章共用，全文）\n\n" + open("book/素材/课堂数据集.md", encoding="utf-8").read() if n >= 7 else ""
print(f"""# 第 {n} 章输入契约

- 章号：{n}（全书 12 章）
- 章标题：{title}
- 章文件：book/{n:02d}-{title}.md
- 学科档案：humanities
- 答案排版：separate

## 该章大纲切片

章节树条目：

{row}

承载的学习目标原文：

{chr(10).join(goals)}

本周实训与素材片段引用：

{lab}

例题习题计划：

{plan}

## UbD 五件套（只含大概念、持久理解、核心问题）

### 大概念
{section(ubd, "### 大概念", "### 持久理解")}

### 持久理解
{section(ubd, "### 持久理解", "### 核心问题")}

### 核心问题
{section(ubd, "### 核心问题", "### 迁移目标")}

## 术语表（当前全文）

{open("book/术语表.md", encoding="utf-8").read().strip()}

## 前章小结

{prev or "（第 1 章，无前章）"}

## 下一章（只用于写「下一章预告」）

{nxt}
{data}""")
