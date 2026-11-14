#!/usr/bin/env bash
# Runs the TypeSafe chapter judge with the key injected only into the child process.
cd "$(dirname "$0")/.." && exec bash "${VECTA_REPO:-$HOME/project/vecta}/scripts/ops/with-credentials.sh" --env ~/.vecta-agent/typesafe.env -- env NODE_PATH="$PWD/tools/ts/node_modules" node tools/ts/judge_chapter.mjs "$@"
