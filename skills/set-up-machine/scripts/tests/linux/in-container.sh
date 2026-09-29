#!/usr/bin/env bash
# Inside the throwaway container: install the skills from the repo mounted at /src, then
# plan -> apply -> plan with set-up-machine, and run the rule probes. Output goes to /out.
set -euo pipefail
out=/out
skill=~/.agents/skills/set-up-machine

# What a fresh install leaves behind, before any harness has run.
ls -a ~ ~/.config 2>/dev/null > "$out/home-after-install.txt" || true

mkdir -p ~/src
cp -R /src/skills ~/src/
(cd ~ && npx --yes skills add ~/src -g -a claude-code codex opencode cursor --skill '*' -y) > "$out/skills-add.txt" 2>&1

python3 "$skill/scripts/set_up_machine.py" plan > "$out/plan-1.txt" 2>&1
plan_id=$(sed -n 's/^Plan id: //p' "$out/plan-1.txt")
if [ -n "$plan_id" ]; then
  python3 "$skill/scripts/set_up_machine.py" apply --plan-id "$plan_id" > "$out/apply.txt" 2>&1
fi
python3 "$skill/scripts/set_up_machine.py" plan > "$out/plan-2.txt" 2>&1

python3 /src/skills/set-up-machine/scripts/tests/linux/probe.py --skill "$skill" \
  --codex-rules ~/.codex/rules/set-up-machine.rules > "$out/probes.txt"

grep '^Summary' "$out/plan-1.txt" "$out/plan-2.txt"
tail -n 1 "$out/plan-2.txt"

# set-up-project on a throwaway repository, once the machine passes.
project=$(mktemp -d)/demo
mkdir -p "$project"
git -C "$project" init --quiet
setup_project=~/.agents/skills/set-up-project/scripts/set_up_project.py
python3 "$setup_project" plan --project "$project" > "$out/project-plan-1.txt" 2>&1 || true
project_id=$(sed -n 's/^Plan id: //p' "$out/project-plan-1.txt")
if [ -n "$project_id" ]; then
  python3 "$setup_project" apply --plan-id "$project_id" --project "$project" > "$out/project-apply.txt" 2>&1
fi
python3 "$setup_project" plan --project "$project" > "$out/project-plan-2.txt" 2>&1 || true
grep -E '^(Machine|Audit)|No changes' "$out/project-plan-2.txt"
