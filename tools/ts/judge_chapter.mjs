#!/usr/bin/env node
// Advisory TypeSafe (Jev) pass over one chapter: per subsection, is it framed as FDE work, and can an
// 18-year-old with no coding background read it. Prints a table and the flagged subsections.
// Usage: tools/ts_judge.sh <章号>   (the wrapper injects TYPESAFE_API_KEY)
import { readFileSync, readdirSync } from "node:fs";
import { noul, score, TypeSafeClient } from "@typesafe-ai/sdk";

const n = String(process.argv[2]).padStart(2, "0");
const file = readdirSync("book").find((f) => f.startsWith(`${n}-`) && f.endsWith(".md"));
if (!file) throw new Error(`no book/${n}-*.md`);
const text = readFileSync(`book/${file}`, "utf8");
// Units: intro, each ### subsection of N.1, and the lab section. Exercises are checked by the reviewer.
const body = text.split(/^## \d+\.2 /m)[0];
const units = body.split(/^(?=#{2,3} )/m).map((u) => u.trim()).filter((u) => u.replace(/\s/g, "").length > 80);
const lab = text.match(/^## \d+\.5 本周实训[\s\S]*?(?=^## )/m);
if (lab) units.push(lab[0].trim());

const questions = {
  fde: noul(
    "Is `passage` written from the viewpoint of a forward deployed engineer's (FDE) work with a customer — what the FDE observes, decides, delivers or is responsible for — rather than as a generic tutorial about AI or agent tools?",
  ),
  readable: score(
    "How hard is `passage` to read for an 18-year-old vocational student with no programming background?",
    [
      "Short plain sentences, everyday words, concrete examples; no unexplained term",
      "Mostly plain, with one or two long sentences or lightly explained terms",
      "Dense or abstract; several long sentences or terms a beginner would not know",
      "Reads like a paper for specialists; a beginner would stop reading",
    ],
  ),
  jargon: noul("Does `passage` use a technical term without explaining it in plain words at or before its first use in the passage?"),
};
const client = new TypeSafeClient({ timeout: 20000, retry: { maxRetries: 1 } });
const rows = await Promise.all(units.map(async (passage) => {
  const title = passage.split("\n")[0].replace(/^#+ /, "").slice(0, 24);
  const { answers: a } = await client.systemOne({ state: { passage, book: "FDE 入门教材", chapter: file }, questions, model: "jev-latest" });
  return { title, fde: a.fde.noul, readable: a.readable.score, jargon: a.jargon.noul };
}));
console.log("| 小节 | FDE 视角 | 难读程度(0易-3难) | 有未解释术语 |\n|---|---|---|---|");
for (const r of rows) console.log(`| ${r.title} | ${r.fde.toFixed(2)} | ${r.readable.toFixed(2)} | ${r.jargon.toFixed(2)} |`);
// Thresholds set from chapter 1 (2026-11-13): its hardest subsection scored 1.75, its generic-sounding lab 0.17.
// jargon is printed but not flagged: it fired on the learning-objectives list, so it is too noisy alone.
// 2026-11-13: a rewrite into short sentences moved readable only 1.75 -> 1.72 while fde moved 0.17 -> 0.93,
// so readable is a weak signal here; flag only the clear outliers.
const flagged = rows.filter((r) => r.fde < 0.5 || r.readable >= 1.9);
console.log(flagged.length ? `\nFLAGGED: ${flagged.map((r) => r.title).join("；")}` : "\nFLAGGED: none");
