#!/usr/bin/env bash
# Inside the throwaway container: install the skills from the repo mounted at /src, then run
# set-up-machine's verify script on a machine where no harness has run yet. Output goes to /out.
set -euo pipefail
out=/out
skill=~/.agents/skills/set-up-machine

mkdir -p ~/src
cp -R /src/skills ~/src/
(cd ~ && npx --yes skills add ~/src -g -a claude-code codex --skill '*' -y) > "$out/skills-add.txt" 2>&1

# The rule samples on Linux, where program names and paths don't fold case; Codex's checker
# has no rules to read yet, and no harness is wired, so those lines say so.
python3 "$skill/scripts/verify.py" > "$out/verify.txt" 2>&1 || true
cat "$out/verify.txt"
python3 -m unittest discover -s "$skill/scripts/tests" > "$out/tests.txt" 2>&1
tail -n 1 "$out/tests.txt"
