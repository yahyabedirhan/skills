#!/usr/bin/env python3
"""Leave a Claude Code cloud session the steps to set itself up from a private workstation repo.

A cloud environment's setup script runs as root before Claude Code starts, on whatever repo the session is on.
At that point only public repos can be cloned: a private repo is reachable only after the agent attaches it with `add_repo`.
So this script does not set anything up. It writes two files that let the agent do it, as references/claude-code/cloud.md > 'Bootstrap' describes:

1. `~/.claude/CLAUDE.md`: before any other work, attach the workstation repo, clone it, run its setup command, and attach any repo that command reports it can't reach.
2. `~/.claude/settings.json`: an allow rule for exactly that setup command, so auto mode doesn't refuse it. Every other key is kept.

Usage, from the environment's setup script field:

    curl -fsSL https://raw.githubusercontent.com/<owner>/<skills-repo>/main/skills/set-up-machine/scripts/cloud_bootstrap.py | python3 - <workstation-repo> <setup-command>

`<workstation-repo>` is `<owner>/<repo>`. `<setup-command>` is a script path inside that repo; it runs as `bash <clone>/<setup-command> <clone>`.
The clone is `/home/user/<repo>`, where a cloud session keeps its repos.

It is safe to run again, and prints what it wrote. It always exits 0, printing the usage on bad arguments:
a setup script that exits non-zero stops the session from starting, and a session without these files still starts, only without the setup.
Standard library only.
"""
import json
import re
import sys
from pathlib import Path

if len(sys.argv) != 3 or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", sys.argv[1]) \
        or sys.argv[2].startswith("/") or ".." in sys.argv[2].split("/"):
    print("usage: cloud_bootstrap.py <owner>/<repo> <setup-command path inside the repo>; nothing written")
    sys.exit(0)
repo, command = sys.argv[1], sys.argv[2]
clone = f"/home/user/{repo.split('/')[1]}"
run = f"bash {clone}/{command} {clone}"
claude = Path.home() / ".claude"
claude.mkdir(parents=True, exist_ok=True)

# The instruction. The setup command later replaces this file with the full instructions, so it holds only the bootstrap.
# A repo the command can't reach, such as a private skill source, is attached by name from its log, so this file never lists one.
(claude / "CLAUDE.md").write_text(f"""# Cloud bootstrap

Written by the set-up-machine skill's cloud_bootstrap.py, from the cloud environment's setup script.

Before any other work, set up this session from `{repo}`:

1. Call `add_repo` for `{repo}` with read access, and clone it to `{clone}` unless it is already there.
2. Run `{run}`.
3. If its output or log names a repo it has no access to, call `add_repo` for that repo with read access, and run step 2 again, once.
4. Read `~/.claude/CLAUDE.md` and the files in `~/.claude/rules/` again, and follow them.
""")
print(f"wrote {claude / 'CLAUDE.md'}")

# The allow rule, merged into the settings the image may already have: only this one entry is added.
path = claude / "settings.json"
try:
    settings = json.loads(path.read_text()) if path.is_file() else {}
except ValueError:
    print(f"{path} isn't valid JSON, so no allow rule was written; auto mode may refuse the setup command")
    sys.exit(0)
allow = settings.setdefault("permissions", {}).setdefault("allow", [])
rule = f"Bash({run})"
if rule not in allow:
    allow.append(rule)
path.write_text(json.dumps(settings, indent=2) + "\n")
print(f"wrote {path}: allows `{run}`")
