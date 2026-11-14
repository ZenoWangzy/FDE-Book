#!/usr/bin/env python3
"""Mechanical acceptance check for one chapter and its writer report.

Usage: python3 tools/check_chapter.py <章号>
Exit 0 when every check passes. It checks structure and bookkeeping only; a reviewer still checks content and sources.
"""
import glob, re, sys

n = int(sys.argv[1])
files = glob.glob(f"book/{n:02d}-*.md")
bad = []
if len(files) != 1:
    sys.exit(f"FAIL: expected one book/{n:02d}-*.md, found {files}")
ch = open(files[0], encoding="utf-8").read()
rep = open(f".scratch/fde-textbook/runs/ch{n:02d}.report.md", encoding="utf-8").read()

want = ["## 本章学习目标", f"## {n}.1 先弄明白", f"## {n}.2 看例子", f"## {n}.3 跟着练",
        f"## {n}.4 自己做", f"## {n}.5 本周实训", "## 本章小结", "## 参考文献"]
got = [l.strip() for l in ch.splitlines() if l.startswith("## ")]
if got != want:
    bad.append(f"二级标题应为 {want}，实际 {got}")


def part(a, b):
    return ch.split(a, 1)[1].split(b, 1)[0] if a in ch and b in ch else ""


ex, guide, indep = part(want[2], want[3]), part(want[3], want[4]), part(want[4], want[5])
ids = lambda t: sorted(set(re.findall(rf"(?m)^#+ .*?{n}-(\d+)", t)), key=int)
for name, text, k in (("看例子", ex, 2), ("跟着练", guide, 2), ("自己做", indep, 4)):
    if len(ids(text)) != k:
        bad.append(f"{name} 应有 {k} 题，题号标题找到 {ids(text)}")
for name, text in (("看例子", ex), ("跟着练", guide)):
    v = len(re.findall(r"✅ 已验证|⚠️ 需作者确认", text))
    if v < 2:
        bad.append(f"{name} 的验证状态行少于 2 条（找到 {v}）")
for word in ("参考答案", "解题路径", "参考要点", "✅ 已验证"):
    if word in indep.replace("98-参考答案.md", ""):  # the pointer to the answer file is allowed
        bad.append(f"{n}.4 段内出现「{word}」，答案或验证没有搬干净")
if "<details>" not in guide:
    bad.append("引导分析没有用 <details> 折叠提示和解答")
if "```mermaid" not in ch and "](图/" not in ch:
    bad.append("全章没有图")
for img in re.findall(r"\]\((图/[^)]+)\)", ch):
    if not glob.glob("book/" + img):
        bad.append(f"图片文件不存在：{img}")

cited = set(re.findall(r"\[(\d+)\]", ch.split("## 参考文献")[0]))
listed = set(re.findall(r"(?m)^\[(\d+)\]", ch.split("## 参考文献")[-1]))
if cited != listed:
    bad.append(f"正文引用编号 {sorted(cited, key=int)} 与参考文献条目 {sorted(listed, key=int)} 不一致")
if re.search(r"\bS\d{3}\b|references/web", ch):
    bad.append("章内出现来源编号 S### 或本地快照路径")
if re.search(r"\b[XRDVAC]\d{1,2}\b", ch):
    bad.append("章内出现素材 ID（X01、D2 一类），应写作者和书名")
if re.search(r"前沿部署|现场工程师|综合案例|大作业", ch):
    bad.append("章内出现术语表禁用的写法（前沿部署工程师、现场工程师、综合案例、大作业）")
if re.search(r"Dify|Coze|扣子", ch):
    bad.append("章内出现 Dify 或 Coze")

for h in ("## 新增术语", "## 引文台账", "## Bloom标注回写", "## 本章独立习题答案", "## 素材使用记录", "## 给 supervisor 的说明"):
    if h not in rep:
        bad.append(f"回报文件缺少「{h}」")
ans = rep.split("## 本章独立习题答案")[-1].split("## 素材使用记录")[0]
ans_ids = re.findall(rf"(?m)^#### 习题 {n}-(\d+)", ans)
if sorted(ans_ids, key=int) != ids(indep):
    bad.append(f"回报的答案题号 {ans_ids} 与章内独立题号 {ids(indep)} 对不上")
if len(re.findall(r"\*\*验证\*\*：(✅ 已验证|⚠️ 需作者确认)", ans)) != len(ans_ids):
    bad.append("回报的答案里验证状态行与题数不等")
bloom = re.findall(rf"(?m)^\|[^|]*{n}-\d+ *\|", rep.split("## Bloom标注回写")[-1].split("## 本章独立习题答案")[0])
if len(bloom) != 8:
    bad.append(f"Bloom标注回写应为 8 行，实际 {len(bloom)}")

body = re.sub(r"\s", "", ch.split(want[2])[0])
print(f"{files[0]}: 正文约 {len(body)} 字，全章 {len(re.sub(chr(92)+'s', '', ch))} 字，⚠️ {ch.count('⚠️')} 处")
print("\n".join("FAIL: " + b for b in bad) or "PASS")
sys.exit(1 if bad else 0)
