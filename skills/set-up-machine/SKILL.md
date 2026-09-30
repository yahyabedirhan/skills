---
name: set-up-machine
description: Set up or audit a machine's coding-agent harnesses from one rule table - the shared global instructions every harness reads, the global rules (deny, ask, allow-and-report) each one enforces, the pre-tool hook, and memory kept off. Use for a new machine or VPS, to audit this machine's agent setup, or when another skill says to check the machine.
---

# Set up machine

Make every coding-agent harness on the machine (Claude Code, Codex, opencode, Cursor's IDE and CLI) match two sources: the **rule table**, [`rules.json`](rules.json), which holds each global rule once as what it covers; and the **shared global instructions file**, `~/.config/agents/AGENTS.md`, which every harness reads. Each harness also runs the **pre-tool hook**, `scripts/pre_tool_hook.py`, before every tool call, and keeps its memory off. Never remove or loosen an entry the table didn't produce: it's the user's. Harness formats change, so check the docs a harness reference links before writing; where they differ, follow the docs and name the difference in your report. Running the skill again is the **audit**: the same steps, ending with a diff that changes nothing.

## Parameters

- `<skills-repo>`: the user's own skills repo on GitHub, as `owner/repo`.

## Steps

1. **Inspect.** Find each harness on the machine, read its reference, then every file that reference names. Read the shared file too.
   - **When trying a change without touching the real machine:** run the steps against a copy of the home folder in the project's `.scratch/`, and check it with `verify.py --home <copy>`. Start no harness there, since it would read the real login.
2. **Propose one diff** that brings each harness in line with the rule table, the shared file's shape, memory off, the hook wired, and the `<skills-repo>` skills installed. Give every harness found its own section, listing each gap its reference names and the hook's blind spots. Read `references/global-instructions.md` whenever a global instructions file is in the diff.

   Work out what each harness should hold, from `rules.json`, the shared file's shape and the harness's reference, and compare it with what the machine holds. Write the whole diff: per harness and file, the exact entries or a unified diff, each line marked:

   - `added`, `tightened` (a stricter entry added where it wins), `removed`;
   - `present`, `wired` (the hook), `found` (the MCP tools a mail row matched);
   - `stricter` (the machine is stricter than the table: kept), `extra` (not the table's: kept), `gap` (what the harness can't express), `none` (no such feature).

   Use `removed` only for memory files, a harness's own global file whose every line is already in the shared file (it becomes a link), and this skill's own wiring that points at an old script. An entry a dropped row left behind is `extra`, for the user to remove.
   - **With a `<skills-repo>` value:** the diff installs that repo's skills globally: `npx --yes skills add <owner>/<repo> -g -a codex -a claude-code -y`, leaving out `-a claude-code` when `~/.claude/skills` is a link to `~/.agents/skills`. It's `present` once `~/.agents/.skill-lock.json` records a skill from that source. With no value, it's a `none` line.
3. **Ask once** for one approval of the whole diff. A change after that needs a new approval.
4. **Back up** every file the diff changes or removes. Before writing any file, copy each one into `~/.config/agents/backups/<UTC time as YYYYmmddTHHMMSSZ>/`, at its path relative to the home folder (`.claude/settings.json`). Copy a symlink as a link.
5. **Write** exactly the approved diff. Run any install command first, such as a skill the diff installs. If one fails, write nothing and report it. In a JSON file, change only the keys the diff names and keep the rest. Write through a symlink to its target.
6. **Verify** with `scripts/verify.py`, then inspect again until the diff changes nothing: no `added`, `tightened` or `removed` line. Report the backup folder, what's wired, the gaps, and the stricter and extra entries.

   Run `python3 <this skill>/scripts/verify.py` (Python 3.9+, standard library only; it writes nothing). It passes when it prints `rules ok`, a `hook wired` line for every harness found, and every `codex differs` line is a row codex.md says gets no rule.

## Rule table

`rules.json` holds each global rule once, by meaning, not in any harness's form. Each harness reference turns a row into that harness's entries; the hook and `verify.py` read it through `scripts/setupmachine/rules.py`, which refuses a malformed row.

### A row

| Field | Holds |
|---|---|
| `id` | a stable kebab-case name |
| `level` | `deny`, `ask` or `allow-and-report` |
| `summary` | what the rule covers, as it reads in the rule line |
| `match` | what it covers, in one of the three kinds below |
| `reason` | why the rule exists |
| `instruction` | for `deny`, what the agent does instead: an alternative, or "Stop, say why, and give the user the exact command; never work around it."; for `ask` and `allow-and-report`, how to go ahead |
| `samples` | `covers`: calls the row must catch; `leaves`: near misses it must let through. A shell command for a command row, a path for a file row, a tool name for an MCP row. `verify.py` checks them against the hook |
| `gap` | optional: what no harness can catch for the row (`echo $TOKEN`); every audit names it |

### `match` kinds

A `match` object's keys say which kind it is:

- **Command:** `program`, a bare name (`rm`) or a list of them, and optionally:
  - `subcommands`: alternative word lists after the program (`[["repo", "delete"], ["repo", "archive"]]`);
  - `flags`: every flag group the command carries, each listing one flag's names without dashes, a one-letter name being the short flag (`["r", "R", "recursive"]`);
  - `operands`: words right after the subcommand and flags (`["777"]`), or alternative word lists (`[["777"], ["a+rwx"]]`);
  - `any_operand`: words any one of which may appear anywhere after the subcommand (`["main", "master"]`);
  - `arguments: "none"`: the program with nothing after it (`env`); `arguments: "flags"`: with flags and nothing else (`declare -x`);
  - `files`: globs one of its operands must match (`cat .env`), with an optional `except`;
  - `variables`: globs over the names of the variables an argument expands (`*TOKEN*` covers `echo $API_TOKEN`, not `echo '$API_TOKEN'`).
- **File:** `paths`, globs relative to the project (`**/.env`), or starting `~/` or `/`; `access`, `read` or `write`; an optional `except` (`**/.env.example`). A `read` row covers writes too.
- **MCP tool:** `server` and `tool`, case-insensitive regular expressions over the two parts of `mcp__<server>__<tool>`. Store the meaning (`mail`, `^(send|reply|forward)`), never one account's server ID, so the row matches on every machine and account.

### Spellings

A harness that matches a command's text catches only the spellings it lists, so give it one entry per way of writing a command row:

- **Programs:** each program as typed, then as `/bin/<program>` and `/usr/bin/<program>`, except shell builtins (`.`, `source`, `set`, `export`, `declare`, `typeset`, `unset`, `eval`, `alias`), which have no path.
- **Flags:** a one-letter name is a short flag (`-r`), a longer one a long flag (`--recursive`). Every order of the groups, every spelling in each group, as separate words; and, when every group has a one-letter name, the one-letter names clustered in every order (`-rf`, `-fr`, `-Rf`, `-fR`).
- **Order:** program, then subcommand words, then flags, then operands (`git push --force`, `chmod -R 777`).
- **`find`'s options** (`-delete`) are one-dash words written after the path, so no prefix entry catches them: a command row on `find` gets no native entry, a gap the hook covers on every harness.

## Pre-tool hook

`scripts/pre_tool_hook.py` (Python 3.9+, standard library only) is the hook every harness runs before each tool call. It reads `rules.json` and checks the call:

- **deny** rows: it reads a command the way the shell runs it, and checks file tools, redirects and MCP tools too. It refuses the call, naming each refused part with its rule's reason and instruction.
- **allow-and-report** rows: it writes one JSON line per call to `<report folder>/<date>.jsonl`, readable by the user alone; the harness's permissions decide.
- **ask** rows: the harness's native ask entries do the asking.

### Wiring

Each harness reference shows its wiring with `<script>` in place of the script's path. Replace it with the absolute path of `scripts/pre_tool_hook.py` in the installed skill (under `~/.agents/skills` or `~/.claude/skills`), never in a checkout or worktree, which can be deleted. If there is no installed copy, name the gap.

The wiring fails open (`[ -f <script> ] && … || true`, or the form a harness reference gives): if the script is gone, each call goes on under the native entries. Without it, `python3` would exit 2 on the missing script, which blocks every call.

The report folder is `~/.local/state/agents/reports`, or `report_dir` in `~/.config/agents/hook.json`.

### What it can't see

Name these once in every audit:

- a command inside a script file or another interpreter (`python -c`);
- a command built from variables (`$cmd -rf x`);
- an alias or function defined elsewhere;
- an abbreviated long option (`--recur`);
- a force push by refspec (`git push origin +main`);
- a glob the shell expands (`cat .env*`);
- each row's own `gap`.

## References

- [references/global-instructions.md](references/global-instructions.md): the shared file's shape, the roles table, what counts as personal workflow, moving a harness's own file, and why memory stays off.
- [references/rule-table.md](references/rule-table.md): changing a row of the rule table, changing the hook's code and its tests, and adding a harness.
- One reference per harness, read for each harness found. Each says how the harness is found, where it keeps each setting, a row's native form with worked examples, the hook's wiring, and its gaps:
  - [references/claude-code.md](references/claude-code.md): Claude Code.
  - [references/codex.md](references/codex.md): Codex.
  - [references/opencode.md](references/opencode.md): opencode.
  - [references/cursor.md](references/cursor.md): Cursor's IDE and CLI.

## Scripts

- [scripts/verify.py](scripts/verify.py): checks, without writing anything, that the rules work on this machine: each row's samples through the hook, and through Codex's own policy check.
- [scripts/pre_tool_hook.py](scripts/pre_tool_hook.py): the pre-tool hook every harness calls before each tool call.
- [references/opencode-plugin.js](references/opencode-plugin.js): the opencode plugin that calls the hook.
