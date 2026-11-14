#!/usr/bin/env bash
# Runs chapters <from>..<to> in order: agent team, then supervisor bookkeeping. Stops at the first chapter
# whose mechanical check fails. The supervisor audits each review afterwards and fixes forward.
set -euo pipefail
main() {
  cd "$(dirname "$0")/.."
  for n in $(seq "$1" "$2"); do
    tools/run_chapter.sh "$n"
    python3 tools/accept_chapter.py "$n"
  done
}
main "$@"
