---
name: set-up-machine
description: Set up or audit a machine's coding-agent harnesses from one rule table - the shared global instructions every harness reads, the global rules (deny, ask, allow-and-report) each one enforces, and memory kept off. Use for a new machine or VPS, to audit this machine's agent setup, or when another skill says to check the machine.
---

# Set up machine

Two sources declare the machine:

- the **rule table**, [`rules.json`](rules.json): each global rule once, with its level, reason and instruction;
- the **shared global instructions file**, `~/.config/agents/AGENTS.md`: the one file every harness's global instructions reach. Its shape (the rule line, the Defaults table by role, the generated rule lines, the personal workflow section) and what belongs in it are in [references/global-instructions.md](references/global-instructions.md); read it before writing any line into the file or moving a harness's own global file into it.

`scripts/set_up_machine.py` **reconciles** each harness against them: it compares what the table wants with what's on the machine, shows the diff, and applies it on one approval. Running it again is the **audit**. It needs only Python 3.9+.

It also wires the **pre-tool hook**, `scripts/pre_tool_hook.py`, into each harness that has one; see *Pre-tool hook* below.

Harnesses it covers, each with an adapter reference: [Claude Code](references/claude-code.md). Codex so far for memory only. opencode and Cursor have no memory feature, and the plan says so.

## Steps

1. **Plan.** Run `python3 <this skill>/scripts/set_up_machine.py plan`. It writes nothing, but it starts each harness briefly to list the MCP tools it exposes (see *Mail tools* below). Done when you hold its whole output, which ends in either `No changes.` or a plan id.
2. **Nothing to do?** On `No changes.`, report the audit: memory per harness, what's wired, the gaps, the stricter and extra rules, and the mail tools it found. Stop here.
3. **Ask once.** Show the user the plan output unedited, then ask for one approval of the whole diff. Its lines, per harness:
   - `added`: a rule the harness lacks.
   - `tightened`: a rule the harness has at a looser level; the stricter entry is added beside it.
   - `removed`: an entry this skill wrote earlier that the table no longer has, or a harness memory file. Only these are ever removed.
   - `present`: already in place, as the table's entry or a broader one that covers it.
   - `wired`: the pre-tool hook in place for that harness, and the folder its reports go to.
   - `stricter`: the machine holds the rule at a stricter level than the table. It's kept; to get the table's level, the user removes that entry by hand.
   - `found`: the tools a mail-tool rule matched on this machine. Name them in your report.
   - `gap`: what the harness can't express, named so it isn't mistaken for enforced.
   - `none`: the harness has no such feature (memory), so there's nothing to set.
   - `extra`: a rule on the machine the table doesn't have, or a line in a harness's own global file besides its link to the shared file. It's kept. A rule worth having everywhere is a candidate row for the table; a line moves into the shared file (references/global-instructions.md, *Moving a harness's file*).
4. **Apply** the approved plan: `python3 <this skill>/scripts/set_up_machine.py apply --plan-id <id>`, the command the plan printed. If apply refuses because the machine changed since the plan, go back to step 1 and ask again.
5. **Audit.** Run the plan again. Done when it ends `No changes.` and every harness with a hook shows a `wired` line. Report the backup folder apply printed, what's wired, the gaps, the stricter and extra rules, and the mail tools found.

`--home <dir>` points every step at another home folder, such as a copy of this one in the project's `.scratch/`, to try a change without touching the real machine.

## What reconcile promises

- **It never removes or loosens an entry it didn't write.** The manifest `~/.config/agents/set-up-machine.json` lists every entry it wrote, per harness; everything else is the user's.
- **The stricter rule wins** where two overlap, in the table or on the machine.
- **The shared file is the user's outside the generated block.** The block between the `set-up-machine:rules` markers is regenerated from the table; elsewhere reconcile only adds what the file's shape lacks, and never rewrites a Defaults value or a workflow line.
- **Memory stays off.** Each harness's memory feature is turned off where it has one, and every memory file is listed as `removed`. Apply keeps a copy in the backup folder, so move a memory worth keeping into its layer before approving.
- **Apply writes exactly the approved plan,** after copying each file it changes into `~/.config/agents/backups/<time>/`.

## Changing the rule table

Edit `rules.json`, then run the steps. Each row:

| Field | Holds |
|---|---|
| `id` | a stable kebab-case name |
| `level` | `deny`, `ask` or `allow-and-report` |
| `summary` | what the rule covers, as it reads in the rule line |
| `match` | what it covers, by meaning, in one of the three kinds below |
| `reason` | why the rule exists |
| `instruction` | for `deny`, what the agent does instead: an alternative, or "Stop, say why, and give the user the exact command; never work around it."; for `ask` and `allow-and-report`, how to go ahead |

`match` kinds, told apart by their keys:

- **Command:** `program`, one bare name (`rm`) or a list of them; optional `subcommands`, alternative word lists after the program (`[["repo", "delete"], ["repo", "archive"]]`); optional `flags`, the flag groups the command carries, all of them, each listing one flag's names without dashes, a one-letter name being the short flag (`["r", "R", "recursive"]`); optional `operands`, words after the flags (`["777"]`).
- **File:** `paths`, globs relative to the project (`**/.env`) or starting `~/`, and `access`, `read` or `write`.
- **MCP tool:** `server` and `tool`, case-insensitive regular expressions over the two parts of an MCP tool name (`mcp__<server>__<tool>`). Store the meaning (`mail`, `^(send|reply|forward)`), never one account's server ID.

Adapters expand a row into every native entry it needs (each flag order and spelling, the `/bin/` and `/usr/bin/` paths, the harness's own file-rule kind), and the shared file gets one rule line per row.

## Pre-tool hook

One script, `scripts/pre_tool_hook.py`, reads the same `rules.json` and checks each tool call before it runs:

- **deny** rows: it reads the command the way the shell runs it (any flag order or grouping, flags after the operands, `/bin/rm`, `mkfs.ext4`, the inside of `bash -lc '…'`, `eval`, `sudo`, `xargs`, `find -exec`, every part of `a && b; c | d`), and refuses the call naming each refused part with its rule's reason and instruction. It also checks file tools against file rows and MCP tools against mail-tool rows, including tools connected after the last plan.
- **allow-and-report** rows: it appends one JSON line per call to `<report folder>/<date>.jsonl`, readable by the user alone since a command can carry a secret, and lets the harness's own permissions decide.
- **ask** rows stay native.

The native entries stay underneath, so a hook that fails or is switched off leaves them in force. The report folder is `report_dir` in `~/.config/agents/hook.json`, which the plan creates with `~/.local/state/agents/reports` and then leaves to the user. The script takes `--harness` (which payload and answer format), `--config` and `--rules`; each adapter's reference says how it's wired.

## Mail tools

Only the running harness knows which MCP tools it exposes, and their names differ by harness and by how a connector is attached. So plan asks each harness for its tool list, matches the table's MCP-tool rows against it, and prints a `found` line per row. If a harness can't be asked (not installed, not logged in), the plan says so as a gap and keeps the entries it wrote before. `--tool-names <file>`, one name per line, supplies the list instead.

## Adding a harness

One adapter module in `scripts/setupmachine/adapters/`, registered in its `__init__.py`, owning the harness's memory setting too (move its entry out of `WITHOUT_MEMORY` in `scripts/setupmachine/memory.py`), and one reference file in `references/` covering the same headings as [Claude Code's](references/claude-code.md). Tests: `python3 -m unittest discover -s <this skill>/scripts/tests`.
