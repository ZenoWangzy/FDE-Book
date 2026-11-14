"""Convert a ChatGPT backend-api conversation JSON export to Markdown with resolved source links.

Usage: python3 tools/chatgpt_to_md.py conv.json out_dir
Writes out_dir/conversation.md (cleaned transcript) and out_dir/sources.md (every cited URL).
"""
import json, re, sys, datetime, pathlib

def load(path):
    t = open(path, encoding="utf-8").read()
    return json.loads(t[t.index("{"):t.rindex("}") + 1])  # file may carry a tool preamble

def ref_map(d):
    refs = {}
    def walk(o):
        if isinstance(o, dict):
            r = o.get("ref_id")
            if isinstance(r, dict) and o.get("url"):
                refs[f"turn{r['turn_index']}{r['ref_type']}{r['ref_index']}"] = (o["url"], o.get("title") or o["url"])
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(d["mapping"])
    return refs

def clean(text, refs, used):
    def link(ref, title=None):
        if ref not in refs:
            return f"{title or ref}（来源未解析：{ref}）"
        url, t = refs[ref]
        used.setdefault(url, t)
        return f"[{title or t}]({url})"
    text = re.sub(r'<Link ref="([^"]+)" title="([^"]*)"\s*/>', lambda m: link(m[1], m[2]), text)
    text = re.sub(r'<Cite refs=\{\[([^\]]*)\]\}\s*/>',
                  lambda m: " （来源：" + "；".join(link(r) for r in re.findall(r'"([^"]+)"', m[1])) + "）", text)
    text = re.sub(r'<Link url="([^"]+)" title="([^"]*)"\s*/>', lambda m: used.setdefault(m[1], m[2]) and f"[{m[2]}]({m[1]})", text)
    text = re.sub(r'<title[^>]*>(.*?)</title>', r'### \1', text)
    text = re.sub(r'<badge[^>]*>(.*?)</badge>', r'【\1】', text)
    text = re.sub(r'<AsyncImage[^>]*/>\n?', '', text)
    text = re.sub(r'<Entity value="([^"]*)"[^>]*/>', r'\1', text)
    text = re.sub(r'<divider[^>]*/>', '---', text)
    text = re.sub(r'</?(row|box|text|col|grid|card|stack|list|list-item)\b[^>]*>', '', text)
    return re.sub(r'\n{3,}', '\n\n', text)

def report_deep_research(mapping, out, url, used):
    """The Deep Research report lives in the app widget's state, not on the message path."""
    for n in mapping.values():
        sdk = ((n.get("message") or {}).get("metadata") or {}).get("chatgpt_sdk") or {}
        if not sdk.get("widget_state"): continue
        rm = json.loads(sdk["widget_state"]).get("report_message")
        if not rm: continue
        txt = rm["content"]["parts"][0]
        # replace from the end so earlier start/end indexes stay valid
        for r in sorted(rm["metadata"].get("content_references", []), key=lambda r: -r["start_idx"]):
            items = [(i.get("title") or i["url"], i["url"]) for i in r.get("items", []) if i.get("url")]
            for t, u in items: used.setdefault(u, t)
            rep = " （来源：" + "；".join(f"[{t}]({u})" for t, u in items) + "）" if items else ""
            txt = txt[:r["start_idx"]] + rep + txt[r["end_idx"]:]
        assert not re.search(r"[-]", txt), "unresolved citation markers in Deep Research report"
        (out / "deep-research-report.md").write_text("\n".join([
            "# ChatGPT Deep Research 报告", "",
            f"- 来源：{url} 中 Deep Research 插件生成的报告（从插件状态 widget_state.report_message 导出）",
            f"- 导出时间：{datetime.date.today()}，脚本 tools/chatgpt_to_md.py",
            "- 性质：AI 生成的二手资料。教材引用时回到原始网页核对，不直接引用本报告。", "", "---", "", txt, ""]), encoding="utf-8")
        print("deep research report written")

def main(src, out):
    d = load(src); refs = ref_map(d); used = {}
    m = d["mapping"]; node = d["current_node"]; path = []
    while node: path.append(m[node]); node = m[node].get("parent")
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    cid = d["conversation_id"]; url = f"https://chatgpt.com/c/{cid}"
    lines = [f"# {d['title']}", "",
             f"- 来源：ChatGPT 对话 {url}",
             f"- 对话时间：{datetime.datetime.fromtimestamp(d['create_time'], datetime.timezone.utc):%Y-%m-%d}（UTC）",
             f"- 导出时间：{datetime.date.today()}，经 CDP 从对话 API 导出，脚本 tools/chatgpt_to_md.py",
             "- 性质：AI 检索整理的二手资料。教材引用时须回到下列原始来源核对，不直接引用本对话。", ""]
    for n in reversed(path):
        msg = n.get("message")
        if not msg or msg["content"].get("content_type") != "text": continue
        role = msg["author"]["role"]
        txt = "".join(p for p in msg["content"].get("parts", []) if isinstance(p, str)).strip()
        if role not in ("user", "assistant") or not txt: continue
        lines += [f"## {'提问' if role == 'user' else 'ChatGPT 回答'}", "", clean(txt, refs, used), ""]
    (out / "conversation.md").write_text("\n".join(lines), encoding="utf-8")
    report_deep_research(m, out, url, used)
    src_lines = [f"# 来源清单：{d['title']}", "", f"摘自 {url} 中 ChatGPT 回答所引用的网页，按首次出现排序。", "",
                 "| # | 标题 | URL |", "|---|---|---|"]
    for i, (u, t) in enumerate(used.items(), 1):
        src_lines.append(f"| S{i:03d} | {t.replace('|', '/')} | {u} |")
    (out / "sources.md").write_text("\n".join(src_lines) + "\n", encoding="utf-8")
    unresolved = len(re.findall("来源未解析", (out / "conversation.md").read_text(encoding="utf-8")))
    print(f"messages written, {len(used)} sources, {unresolved} unresolved refs")
    assert len(used) > 0, "no citations resolved: export format changed?"
    left = sorted(set(re.findall(r"<[A-Z][A-Za-z]*|<[a-z]+-?[a-z]*(?=[ >/])", (out / "conversation.md").read_text(encoding="utf-8"))))
    assert not left, f"unconverted UI tags left: {left}"

if __name__ == "__main__":
    main(*sys.argv[1:3])
