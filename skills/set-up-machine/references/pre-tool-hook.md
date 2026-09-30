# Pre-tool hook

`scripts/pre_tool_hook.py` (Python 3.9+, standard library only) is the hook every harness runs before each tool call. It reads `rules.json` and checks the call:

- **deny** rows: it reads a command the way the shell runs it, and checks file tools, redirects and MCP tools too. It refuses the call, naming each refused part with its rule's reason and instruction.
- **allow-and-report** rows: it writes one JSON line per call to `<report folder>/<date>.jsonl`, readable by the user alone; the harness's permissions decide.
- **ask** rows: the harness's native ask entries do the asking.

## Wiring

Each harness reference shows its wiring with `<script>` in place of the script's path. Replace it with the absolute path of `scripts/pre_tool_hook.py` in the installed skill (under `~/.agents/skills` or `~/.claude/skills`), never in a checkout or worktree, which can be deleted. If there is no installed copy, name the gap.

The wiring fails open (`[ -f <script> ] && … || true`): if the script is gone, each call goes on under the native entries, where an exit 2 would block every call.

The report folder is `~/.local/state/agents/reports`, or `report_dir` in `~/.config/agents/hook.json`.

## What it can't see

Name these once in every audit:

- a command inside a script file or another interpreter (`python -c`);
- a command built from variables (`$cmd -rf x`);
- an alias or function defined elsewhere;
- an abbreviated long option (`--recur`);
- a force push by refspec (`git push origin +main`);
- a glob the shell expands (`cat .env*`);
- each row's own `gap`.

## Changing the code

Run the tests with `python3 -m unittest discover -s <this skill>/scripts/tests`. `scripts/tests/linux/run.sh <repo> <output folder>` runs them and `verify.py` in a fresh Linux container.

To add a harness, write one reference with the same headings as [Claude Code's](claude-code.md), and add its wiring check to `HARNESSES` in `scripts/verify.py`.
