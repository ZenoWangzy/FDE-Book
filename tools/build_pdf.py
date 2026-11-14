#!/usr/bin/env python3
"""Build the whole book as one PDF: book/*.md -> one HTML -> headless Chrome print.

Usage: .scratch/venv/bin/python tools/build_pdf.py [out.pdf]   (needs the `markdown` package and google-chrome)
Folded <details> are printed open, because paper cannot unfold them.
"""
import glob, os, re, subprocess, sys
import markdown

out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "dist/FDE教材.pdf")
os.makedirs(os.path.dirname(out), exist_ok=True)
files = (["book/00-前言.md"] + sorted(glob.glob("book/[01][0-9]-*.md"))[2:] + ["book/98-参考答案.md", "book/99-表现性任务.md",
         "book/素材/任务1-社区餐馆材料包.md", "book/素材/任务2-物业报修材料包.md", "book/素材/课堂数据集.md",
         "book/术语表.md", "book/附录A-dsh安装说明.md", "book/附录B-借鉴说明.md", "book/参考文献.md"])
assert len(files) == 22 and all(os.path.exists(f) for f in files), files


def mermaid_to_text(m):
    labels = re.findall(r'\["([^"]+)"\]', m.group(1))
    seen = list(dict.fromkeys(l.replace("<br/>", "｜") for l in labels))
    return "<p class='flow'>" + " → ".join(seen) + "</p>"


parts = []
for f in files:
    t = open(f, encoding="utf-8").read()
    t = re.sub(r"<!-- Bloom：\S+ -->\n?", "", t)
    t = t.replace("<details>", '<details markdown="1">').replace("✅ ", "")   # render Markdown inside folds; the font has no emoji
    t = re.sub(r"(?s)```mermaid\n(.*?)\n```", mermaid_to_text, t)
    t = re.sub(r"\]\(<?(?!http)([^)>]*\.md)>?\)", "](#)", t)          # cross-file links mean nothing on paper
    t = t.replace("](图/", "](" + os.path.abspath("book/图") + "/")
    html = markdown.markdown(t, extensions=["tables", "fenced_code", "md_in_html", "sane_lists"])
    parts.append(f"<section>{html}</section>")
body = "\n".join(parts).replace("<details>", "<details open>").replace('href="#"', "")
css = """
@page { size: A4; margin: 18mm 16mm; }
body { font-family: "Noto Sans CJK SC", sans-serif; font-size: 11pt; line-height: 1.75; color: #222; }
section { page-break-before: always; } section:first-child { page-break-before: avoid; }
h1 { font-size: 22pt; border-bottom: 3px solid #f0a020; padding-bottom: 6px; }
h2 { font-size: 15pt; margin-top: 1.4em; color: #b35c00; } h3 { font-size: 12.5pt; } h4 { font-size: 11.5pt; }
img { max-width: 100%; display: block; margin: 10px auto; border-radius: 8px; }
table { border-collapse: collapse; width: 100%; font-size: 9.5pt; margin: 10px 0; }
th, td { border: 1px solid #bbb; padding: 4px 6px; vertical-align: top; } th { background: #fdf1dc; }
pre, code { font-family: "Noto Sans Mono CJK SC", monospace; font-size: 9pt; }
pre { background: #f6f6f6; padding: 8px; white-space: pre-wrap; word-break: break-all; border-radius: 6px; }
blockquote { border-left: 4px solid #f0a020; margin: 8px 0; padding: 2px 12px; background: #fffaf0; }
details { border: 1px dashed #c9a25a; border-radius: 6px; padding: 4px 10px; margin: 8px 0; background: #fffdf7; }
summary { font-weight: bold; color: #b35c00; list-style: none; }
.flow { background: #f6f6f6; padding: 8px; border-radius: 6px; font-size: 10pt; }
h2, h3, h4 { page-break-after: avoid; } table, img, pre { page-break-inside: avoid; }
"""
html = f"<!doctype html><html lang='zh-CN'><head><meta charset='utf-8'><title>FDE 教材</title><style>{css}</style></head><body>{body}</body></html>"
tmp = out[:-4] + ".html"
open(tmp, "w", encoding="utf-8").write(html)
subprocess.run(["google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                f"--print-to-pdf={out}", "file://" + tmp], check=True, capture_output=True, timeout=300)
print(out, os.path.getsize(out), "bytes")
