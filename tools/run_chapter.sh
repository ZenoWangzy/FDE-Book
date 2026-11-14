#!/usr/bin/env bash
# One chapter through the agent team: slice -> Codex writer -> mechanical check -> Codex reviewer -> one revision.
# Usage: tools/run_chapter.sh <章号>. The supervisor reads the review and the chapter, then runs tools/accept_chapter.py.
set -euo pipefail
# Body sits in main() so bash parses the whole file first; editing it during a run is then safe.
main() {
cd "$(dirname "$0")/.."
n=$(printf '%02d' "$1"); r=.scratch/fde-textbook/runs
cx() { codex exec --skip-git-repo-check -s "$1" -C "$PWD" -o "$2" "$3" < /dev/null > "${2%.md}.log" 2>&1; }
python3 tools/chapter_slice.py "$1" > "$r/ch$n.input.md"
echo "$(date -u +%T) write"
cx workspace-write "$r/ch$n.last.md" "你是 FDE 教材第 $1 章的写手。先完整阅读 $r/writer-brief.md 并严格照做；本章输入契约是 $r/ch$n.input.md，回报文件写到 $r/ch$n.report.md。交稿前运行 python3 tools/check_chapter.py $1，输出 PASS 才算写完。"
python3 tools/check_chapter.py "$1" || true
tools/ts_judge.sh "$1" > "$r/ch$n.ts.md" 2>&1 || echo "ts judge failed (advisory, continuing)"
tail -1 "$r/ch$n.ts.md"
echo "$(date -u +%T) review"
cx read-only "$r/ch$n.review.md" "你是 FDE 教材第 $1 章的独立审稿人。先完整阅读 $r/reviewer-brief.md 并严格照做。待审：book/$n-*.md，写手回报 $r/ch$n.report.md，输入契约 $r/ch$n.input.md。只审不改，最后的回复就是审稿意见。"
head -1 "$r/ch$n.review.md"
if ! head -1 "$r/ch$n.review.md" | grep -q '结论：通过' || ! grep -q 'FLAGGED: none' "$r/ch$n.ts.md"; then
  echo "$(date -u +%T) revise"
  cx workspace-write "$r/ch$n.revise.last.md" "你是 FDE 教材第 $1 章的写手，现在做一次返工。重读 $r/writer-brief.md。审稿意见在 $r/ch$n.review.md：逐条处理其中的「必须改」，「建议改」能改的也改。另外 $r/ch$n.ts.md 是一个快速判读模型对各小节的打分（FDE 视角 0–1 越高越好；难读程度 0–3 越低越好）：最后一行 FLAGGED 点名的小节，FDE 视角低于 0.5 的要改成从 FDE 的工作讲起，难读程度不低于 1.6 的要拆短句、换日常用语；打分只是提示，你认为判错的在说明里写理由。例外：要求在课堂环境实测 dsh 或 VectA 的意见不处理，保留「⚠️ 需作者确认」标注（开课前才验证）。只改被点名的地方；改了题干、解答或引文的题要重新核验并更新验证记录。同步更新回报文件 $r/ch$n.report.md，并在「给 supervisor 的说明」里逐条写明每条审稿意见怎么处理的。改完运行 python3 tools/check_chapter.py $1 直到输出 PASS。"
fi
echo "$(date -u +%T) done"; python3 tools/check_chapter.py "$1"
}
main "$@"
