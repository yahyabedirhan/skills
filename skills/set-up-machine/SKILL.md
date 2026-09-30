---
name: set-up-machine
description: Set up or audit a machine's coding-agent harnesses from one rule table - the shared global instructions every harness reads, the global rules (deny, ask, allow-and-report) each one enforces, the pre-tool hook, and memory kept off. Use for a new machine or VPS, to audit this machine's agent setup, or when another skill says to check the machine.
---

# Set up machine

You bring each harness on the machine in line with two sources:

- the **rule table**, [`rules.json`](rules.json): each global rule once, by meaning. [references/rule-table.md](references/rule-table.md) explains a row;
- the **shared global instructions file**, `~/.config/agents/AGENTS.md`, which every harness reads: [references/global-instructions.md](references/global-instructions.md).

Each harness has a reference that says where it keeps each setting, the native form of a row with worked examples, how the hook is wired, and the known gaps: [Claude Code](references/claude-code.md), [Codex](references/codex.md), [opencode](references/opencode.md), [Cursor](references/cursor.md) (IDE and CLI). Harness formats change: check the docs a reference links before writing, and where they differ, follow the docs and name the difference in your report.

Two scripts ship with the skill (Python 3.9+, standard library only): `scripts/pre_tool_hook.py`, the **pre-tool hook** every harness runs before each tool call, and `scripts/verify.py`, which checks the result. Running this skill again is the **audit**: the same steps, ending with an empty diff.

## Steps

1. **Inspect.** A harness is on the machine when its config folder exists or its program is on `PATH` (each reference says which). For each one found, read its reference, then every file it names: instructions, permissions, hooks, memory setting and memory files, and the MCP tools it exposes. Read the shared file too. Done when you hold, per harness, the current content of every file its reference names.

2. **Propose one diff.** Work out what each harness should hold, from `rules.json`, the shared file's shape and the reference, and compare. Write the whole diff: per harness and file, the exact entries or a unified diff, each line marked:
   - `added`, `tightened` (stricter entry added where it wins), `removed`;
   - `present`, `wired` (the hook), `found` (the MCP tools a mail row matched);
   - `stricter` (the machine is stricter than the table: kept), `extra` (not the table's: kept), `gap` (what the harness can't express), `none` (no such feature).

   The diff never removes or loosens what the table didn't produce. `removed` is only for memory files, a harness's own global file whose every line is already in the shared file (it becomes a link), and this skill's own wiring that points at an old script. An entry a dropped row left behind is `extra`, for the user to remove. Done when every harness found has a section and each section lists the gaps its reference names.

3. **Ask once.** Show the diff and ask for one approval of all of it. A change you make after that needs a new approval.

4. **Back up.** Before writing any file, copy every file the diff changes or removes into `~/.config/agents/backups/<UTC time as YYYYmmddTHHMMSSZ>/`, at its path relative to the home folder (`.claude/settings.json`); copy a symlink as a link. Done when each of those files has its copy.

5. **Write** exactly the approved diff. Run any install command first (a skill the diff installs); if one fails, write nothing and report it. In a JSON file, change only the keys the diff names and keep the rest; write through a symlink to its target.

6. **Verify.** Run `python3 <this skill>/scripts/verify.py`. Done when it prints `rules ok`, a `hook wired` line for every harness found, and every `codex differs` line is a row references/codex.md says gets no rule. Then inspect again: the diff is empty. Report the backup folder, what's wired, the gaps, and the stricter and extra entries.

To try a change without touching the real machine, run the steps against a copy of the home folder in the project's `.scratch/`, and `verify.py --home <copy>`; start no harness there, since it would read the real login.

## Spellings

Harnesses that match a command's text need one entry per way of writing a command row:

- **Programs:** each program as typed, then as `/bin/<program>` and `/usr/bin/<program>`, except shell builtins (`.`, `source`, `set`, `export`, `declare`, `typeset`, `unset`, `eval`, `alias`), which have no path.
- **Flags:** a one-letter name is a short flag (`-r`), a longer one a long flag (`--recursive`). Every order of the groups, every spelling in each group, as separate words; and, when every group has a one-letter name, the one-letter names clustered in every order (`-rf`, `-fr`, `-Rf`, `-fR`).
- **Order:** program, then subcommand words, then flags, then operands (`git push --force`, `chmod -R 777`).

## Shared skills

With a `skills-repo` value in the Defaults table (`<owner>/<repo>`), the diff installs that repo's skills globally: `npx --yes skills add <owner>/<repo> -g -a codex -a claude-code -y`, leaving out `-a claude-code` when `~/.claude/skills` is a link to `~/.agents/skills`. It's `present` once `~/.agents/.skill-lock.json` records a skill from that source. With no value, a `none` line.

## The pre-tool hook

It reads `rules.json` and checks each tool call before it runs:

- **deny** rows: it reads a command the way the shell runs it, and checks file tools, redirects and MCP tools too. It refuses the call, naming each refused part with its rule's reason and instruction.
- **allow-and-report** rows: one JSON line per call in `<report folder>/<date>.jsonl`, readable by the user alone; the harness's permissions decide.
- **ask** rows: the harness's native ask entries do the asking.

Each reference shows its wiring, around `<script>`: the installed skill's absolute `scripts/pre_tool_hook.py` (under `~/.agents/skills` or `~/.claude/skills`), never a checkout or worktree that can go; name the gap if you can't. The wiring fails open (`[ -f <script> ] && … || true`), since exit 2 would block every call when the script is gone, so the native entries stay underneath. The report folder is `~/.local/state/agents/reports`, or `report_dir` in `~/.config/agents/hook.json`.

What it can't see, named once in every audit: a command inside a script file or another interpreter (`python -c`), one built from variables (`$cmd -rf x`), an alias or function defined elsewhere, an abbreviated long option (`--recur`), a force push by refspec (`git push origin +main`), a glob the shell expands (`cat .env*`), and each row's own `gap`.

## Changing the code

Tests: `python3 -m unittest discover -s <this skill>/scripts/tests`; `scripts/tests/linux/run.sh <repo> <output folder>` runs them and `verify.py` in a fresh Linux container. A new harness is one reference with the same headings as [Claude Code's](references/claude-code.md), and its wiring check in `scripts/verify.py` (`HARNESSES`).
