#!/usr/bin/env bash
# Refuse to publish when a tracked file contains a real name, customer identifier or local path (ADR-0006).
# The pattern list is itself sensitive, so it lives outside the repo: .scratch/fde-textbook/public-scan-patterns.txt
# (one extended regex, built from docs/贯穿案例-敏感信息清单.md). Usage: tools/public_scan.sh  (exit 1 on a hit)
cd "$(dirname "$0")/.." || exit 2
PF=.scratch/fde-textbook/public-scan-patterns.txt
[ -s "$PF" ] || { echo "FAIL: pattern file $PF is missing; cannot scan"; exit 2; }
if git ls-files -z | xargs -0 grep -n -I -E -f "$PF"; then echo "FAIL: sensitive text in tracked files"; exit 1; fi
if git log -p --all | grep -q -E -f "$PF"; then echo "FAIL: sensitive text in git history"; exit 1; fi
echo "PASS: no sensitive text in $(git ls-files | wc -l) tracked files or in history"
