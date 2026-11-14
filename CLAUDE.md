# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

A Chinese-language textbook on FDE (Forward Deployed Engineer, especially enterprise AI / agent FDE), written by an AI-discipline teacher. Not a software project: no build or test suite. All 12 chapters, front matter and appendices are written (stage 5 passed 2026-11-13); open pre-class and pre-publication items are in `.scratch/fde-textbook/issues/10-*.md` and `11-*.md`.

## Layout

- `references/`: borrowed source material, not the author's original work. Read `references/README.md` first: it holds the per-source license table and the citation rules.
  - `references/chatgpt-fde-research/`: the ChatGPT research conversation as Markdown (`conversation.md`) and its cited URLs (`sources.md`, ids S001+). This is a secondary source: cite the original URLs, never the conversation itself.
  - `references/web/`: local snapshots of every URL in `sources.md` (HTML as Markdown, PDF as the original file; index in `references/web/README.md`). Read these instead of re-fetching. Refetch with `node tools/fetch_sources.mjs [S001 ...]`: it drives the author's own Chrome over CDP (127.0.0.1:9222) in background tabs.
  - `references/repos/`: snapshots of 6 FDE GitHub repos (commits in `references/repos-manifest.tsv`, `.git` removed). The XDash book and goday-org/FDE-Handbook are non-commercial only.
- `tools/chatgpt_to_md.py`: converts a ChatGPT `/backend-api/conversation/<id>` JSON export to Markdown with resolved citation links. Usage: `python3 tools/chatgpt_to_md.py <conv.json> <out_dir>`. It asserts that no UI tags are left unconverted.
- `docs/adr/`: settled decisions. 0001 scope (audience, 12 weeks × 4 lessons, GB/T 7714 citations, deliverables); 0002 lab platform and running case; 0003 labs on VectA accounts, data only from the demo ledger; 0004 the adopted textbook skill; 0005 after the two author gates the supervisor session decides (sample chapter, chapter acceptance, final review) without waiting for the author, and maintains this repo long-term. 0006 the book is for self-study, owned and kept improving by the supervisor session, school use only (non-commercial), published as a public repo, pictures instead of mermaid, read-only access to production (mypc) for lab checks. `GLOSSARY.md`: the terms the book uses.
- `.claude/skills/textbook*`: the adopted open-source textbook-writing pipeline (cabbage2000-lab/textbook-writer-skills, MIT, ADR-0004). Write the book through it: stages 1–3 (UbD design, two author gates) then chapter by chapter in `book/`, with state in `book/.progress.json`. Don't invent a parallel process. The idstack plugin (project scope, source in `tools/plugins/idstack/`) checks the work at the two gates and at final review; it never writes into `book/`. How the two fit together: `docs/写作流程.md`. Other candidate skills are kept in `references/skills/` for reference.
- `research/`: findings from research tickets. `docs/`: the running case, table of contents and assessment plan once decided. `book/`: the textbook itself, laid out as the textbook skill defines.
- `.scratch/fde-textbook/`: the wayfinder planning map (`map.md`) and its decision tickets (`issues/NN-*.md`), following the local-markdown tracker convention in `docs/agents/issue-tracker.md`.

## Rules for writing the textbook

- The book's core is FDE: every chapter, objective, example and lab is framed as FDE work. Agent topics (prompts, context, tool permissions, human confirmation, testing) are taught as skills an FDE needs, never as a generic agent course. (Author 2026-11-13: 「核心是FDE，所以所有的内容都围绕FDE，就算是智能体相关的，也是FDE所需要的技能」.)
- The reader is an 18-year-old studying alone: every chapter must be learnable without a teacher. (Author 2026-11-14: 「核心目标是让学生自己看都能自学会的一本教材」.)
- Every borrowed idea, case, figure, framework or chapter structure is listed in the chapter-end references and in `book/附录B-借鉴说明.md`; in-text markers may be kept light (ADR-0006). The author requires the book to show clearly what was borrowed.
- This repo is public. Never commit third-party snapshots, run logs, the real project's case files, customer names or the teacher-only key (see `.gitignore`).
- Lab platform is DeepSeek Harness via the author's product VectA; the running case is the author's real VectA fruit supply-chain project (`docs/adr/0002-*`). Before recommending any tool or platform, check that it is still maintained and in use, and prefer the author's own products. Dify and Coze were proposed once and rejected as dead.
- Respect each source's license as listed in `references/README.md`. No large verbatim copying from the XDash book.
