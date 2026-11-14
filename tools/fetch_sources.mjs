// Save every source listed in references/chatgpt-fde-research/sources.md to references/web/.
// Opens each URL in a background tab of the local Chrome (CDP on 127.0.0.1:9222, the author's own browser),
// stores HTML pages as Markdown and PDFs as the original file, then writes references/web/README.md as the index.
// Usage: node tools/fetch_sources.mjs [S001 S002 ...]   (no ids = all; existing files are skipped unless ids are given)
import fs from "node:fs";
import path from "node:path";

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const OUT = path.join(ROOT, "references/web");
const CDP = "http://127.0.0.1:9222";
const CONCURRENCY = 4;
fs.mkdirSync(OUT, { recursive: true });

const sources = fs.readFileSync(path.join(ROOT, "references/chatgpt-fde-research/sources.md"), "utf8")
  .split("\n").map(l => l.match(/^\| (S\d{3}) \| (.*) \| (https?:\S+) \|$/)).filter(Boolean)
  .map(m => ({ id: m[1], title: m[2], url: m[3] }));
const only = process.argv.slice(2);
const todo = sources.filter(s => only.length ? only.includes(s.id)
  : !fs.readdirSync(OUT).some(f => f.startsWith(s.id + ".")));

const ws = new WebSocket((await (await fetch(CDP + "/json/version")).json()).webSocketDebuggerUrl);
await new Promise(r => ws.addEventListener("open", r, { once: true }));
let seq = 0; const pending = new Map(); const listeners = new Set();
ws.addEventListener("message", e => {
  const msg = JSON.parse(e.data);
  if (msg.id && pending.has(msg.id)) { const { res, rej } = pending.get(msg.id); pending.delete(msg.id); msg.error ? rej(new Error(msg.error.message)) : res(msg.result); }
  else listeners.forEach(f => f(msg));
});
const send = (method, params = {}, sessionId) => new Promise((res, rej) => {
  const id = ++seq; pending.set(id, { res, rej }); ws.send(JSON.stringify({ id, method, params, sessionId }));
});
const sleep = ms => new Promise(r => setTimeout(r, ms));

// Runs inside the page: main content to Markdown.
const EXTRACT = `(() => {
  // Pick the content container with the most text; a page's first <main> is sometimes just a banner.
  const cands = [...document.querySelectorAll("main, article, [role=main]")];
  const best = cands.sort((a, b) => b.innerText.length - a.innerText.length)[0];
  const root = (best && best.innerText.length > 0.3 * document.body.innerText.length ? best : document.body).cloneNode(true);
  root.querySelectorAll("script,style,noscript,svg,nav,footer,header,aside,form,button,iframe,[aria-hidden=true]").forEach(e => e.remove());
  const abs = h => { try { return new URL(h, location.href).href } catch { return h } };
  const md = (n, depth = 0) => {
    if (n.nodeType === 3) return n.textContent.replace(/\\s+/g, " ");
    if (n.nodeType !== 1) return "";
    const kids = () => [...n.childNodes].map(c => md(c, depth)).join("");
    const t = n.tagName.toLowerCase();
    if (/^h[1-6]$/.test(t)) return "\\n\\n" + "#".repeat(+t[1]) + " " + kids().trim() + "\\n\\n";
    if (t === "p") return "\\n\\n" + kids().trim() + "\\n\\n";
    if (t === "br") return "\\n";
    if (t === "a") { const x = kids().trim(); return x && n.getAttribute("href") && !n.getAttribute("href").startsWith("#") ? "[" + x + "](" + abs(n.getAttribute("href")) + ")" : x; }
    if (t === "strong" || t === "b") { const x = kids().trim(); return x ? "**" + x + "**" : ""; }
    if (t === "em" || t === "i") { const x = kids().trim(); return x ? "*" + x + "*" : ""; }
    if (t === "code" && n.parentElement?.tagName !== "PRE") return "\`" + n.textContent + "\`";
    if (t === "pre") return "\\n\\n\`\`\`\\n" + n.textContent.trim() + "\\n\`\`\`\\n\\n";
    if (t === "ul" || t === "ol") return "\\n" + [...n.children].filter(c => c.tagName === "LI").map((li, i) =>
      "  ".repeat(depth) + (t === "ol" ? (i + 1) + ". " : "- ") + [...li.childNodes].map(c => md(c, depth + 1)).join("").trim()).join("\\n") + "\\n";
    if (t === "table") return "\\n\\n" + [...n.querySelectorAll("tr")].map((tr, i) => {
      const cells = [...tr.children].map(c => c.innerText.replace(/\\s+/g, " ").replace(/\\|/g, "/").trim());
      return "| " + cells.join(" | ") + " |" + (i === 0 ? "\\n|" + cells.map(() => "---|").join("") : "");
    }).join("\\n") + "\\n\\n";
    if (t === "img") return "";
    if (/^(div|section|blockquote|li|dl|dd|dt|figure|figcaption)$/.test(t)) return "\\n" + kids() + "\\n";
    return kids();
  };
  return { title: document.title, md: md(root).replace(/[ \\t]+\\n/g, "\\n").replace(/\\n{3,}/g, "\\n\\n").trim() };
})()`;

async function grab(s) {
  const { targetId } = await send("Target.createTarget", { url: "about:blank", background: true });
  const { sessionId } = await send("Target.attachToTarget", { targetId, flatten: true });
  try {
    await send("Page.enable", {}, sessionId);
    const loaded = new Promise(r => { const f = m => { if (m.sessionId === sessionId && m.method === "Page.loadEventFired") { listeners.delete(f); r(); } }; listeners.add(f); });
    await send("Page.navigate", { url: s.url }, sessionId);
    await Promise.race([loaded, sleep(45000)]);
    // client-rendered pages fill in after load; slow SPAs (Databricks, ServiceNow) need up to ~25 s
    for (let t = 0; t < 25 && !(await (async () => (await send("Runtime.evaluate", { expression: "document.body ? document.body.innerText.length : 0", returnByValue: true }, sessionId)).result.value > 1500)()); t++) await sleep(1000);
    const ev = async expr => (await send("Runtime.evaluate", { expression: expr, awaitPromise: true, returnByValue: true }, sessionId)).result.value;
    const ctype = await ev("document.contentType");
    const date = new Date().toISOString().slice(0, 10);
    if (ctype === "application/pdf" || /\.pdf(\?|$)/i.test(s.url)) {
      const b64 = await ev(`fetch(location.href).then(r => r.arrayBuffer()).then(b => { let s = ""; const u = new Uint8Array(b); for (let i = 0; i < u.length; i += 32768) s += String.fromCharCode(...u.subarray(i, i + 32768)); return btoa(s); })`);
      const buf = Buffer.from(b64, "base64");
      if (buf.subarray(0, 4).toString() !== "%PDF") throw new Error("not a PDF body");
      fs.writeFileSync(path.join(OUT, s.id + ".pdf"), buf);
      return { ...s, kind: "pdf", size: buf.length, date };
    }
    const { title, md } = await ev(EXTRACT);
    const finalUrl = await ev("location.href");
    fs.writeFileSync(path.join(OUT, s.id + ".md"), [
      `# ${title || s.title}`, "",
      `- 来源编号：${s.id}`, `- 原始地址：${s.url}`, ...(finalUrl !== s.url ? [`- 实际打开地址：${finalUrl}`] : []),
      `- 抓取日期：${date}（tools/fetch_sources.mjs，经作者本机 Chrome 打开）`,
      `- 版权：内容归原网站所有，仅作编写教材时的参考；教材引用时注明此出处。`, "", "---", "", md, ""].join("\n"));
    return { ...s, kind: "md", size: md.length, date };
  } finally {
    await send("Target.closeTarget", { targetId }).catch(() => {});
  }
}

const results = [];
for (let i = 0; i < todo.length; i += CONCURRENCY) {
  results.push(...await Promise.all(todo.slice(i, i + CONCURRENCY).map(s =>
    grab(s).catch(e => ({ ...s, kind: "error", size: 0, error: e.message })))));
  process.stdout.write(`${Math.min(i + CONCURRENCY, todo.length)}/${todo.length}\r`);
}
ws.close();

// Index: rebuilt from the files on disk so partial reruns keep earlier results.
const byId = Object.fromEntries(results.map(r => [r.id, r]));
const rows = sources.map(s => {
  const f = fs.readdirSync(OUT).find(f => f.startsWith(s.id + "."));
  const size = f ? fs.statSync(path.join(OUT, f)).size : 0;
  const note = byId[s.id]?.error ? "失败：" + byId[s.id].error : !f ? "未抓取" : f.endsWith(".md") && size < 1500 ? "内容过少，可能需登录或被拦截" : "";
  return `| ${s.id} | ${s.title.replace(/\|/g, "/")} | ${f ? `[${f}](${f})` : "—"} | ${s.url} | ${note} |`;
});
fs.writeFileSync(path.join(OUT, "README.md"), ["# 网页资料快照", "",
  "`references/chatgpt-fde-research/sources.md` 中每个来源的本地副本，由 `node tools/fetch_sources.mjs` 生成。网页存为 md，PDF 存原文件。",
  "教材引用时写原始地址，不写本地文件名。", "",
  "| 编号 | 标题 | 本地文件 | 原始地址 | 备注 |", "|---|---|---|---|---|", ...rows, ""].join("\n"));
const bad = results.filter(r => r.kind === "error");
console.log(`\ndone: ${results.length - bad.length} saved, ${bad.length} failed`);
bad.forEach(r => console.log(r.id, r.url, r.error));
