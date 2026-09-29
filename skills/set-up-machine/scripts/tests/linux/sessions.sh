#!/usr/bin/env bash
# Inside the container, after in-container.sh: the checks that start a harness without a login.
# Codex runs real `codex exec` turns against a local stand-in model; opencode prints its merged
# rules. Claude Code and the Cursor CLI need a login for any session, so they aren't run.
set -uo pipefail
out=/out
here=/src/skills/set-up-machine/scripts/tests/linux
work=$(mktemp -d)
mkdir -p "$work/project/x"
cd "$work/project"

codex_turn() {  # codex_turn <label> <command> [codex flags...]
  local label=$1 command=$2; shift 2
  python3 "$here/stand_in_model.py" --port 8765 --command "$command" --out "$out/codex-$label.json" &
  local server=$!
  sleep 1
  timeout 120 codex exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox "$@" \
    -c model_provider=stand-in -m stand-in \
    -c 'model_providers.stand-in={name="stand-in",base_url="http://127.0.0.1:8765/v1",wire_api="responses"}' \
    "Run it." > "$out/codex-$label.log" 2>&1
  kill "$server" 2>/dev/null; wait "$server" 2>/dev/null
  printf 'codex %-24s x %s\n' "$label" "$([ -d x ] && echo kept || echo removed)"
  mkdir -p x
}

codex_turn hook-rm 'rm -rf x'
codex_turn hook-bash-lc "bash -lc 'rm -fr x'"
codex_turn rules-only-rm 'rm -rf x' --disable hooks
codex_turn control-ls 'ls'
codex_turn report-gh-api 'gh api rate_limit'
printf 'codex gh api report lines: %s\n' "$(cat ~/.local/state/agents/reports/*.jsonl 2>/dev/null | grep -c '"harness": "codex"')"

codex debug prompt-input hello > "$out/codex-prompt-input.txt" 2>&1
printf 'codex prompt holds the rule line: %s\n' "$(grep -c 'set-up-machine:rules' "$out/codex-prompt-input.txt")"

opencode debug agent build > "$out/opencode-agent-build.txt" 2>&1
printf 'opencode build agent denies rm -rf: %s\n' "$(grep -c '"rm -rf \*"' "$out/opencode-agent-build.txt")"
