---
name: set-up-machine
description: Set up or audit a machine's coding-agent harnesses from one rule table - the shared global instructions every harness reads, and the global rules (deny, ask, allow-and-report) each one enforces. Use for a new machine or VPS, to audit this machine's agent setup, or when another skill says to check the machine.
---

# Set up machine

Two sources declare the machine:

- the **rule table**, [`rules.json`](rules.json): each global rule once, with its level, reason and instruction;
- the **shared global instructions file**, `~/.config/agents/AGENTS.md`: the one file every harness's global instructions reach.

`scripts/set_up_machine.py` **reconciles** each harness against them: it compares what the table wants with what's on the machine, shows the diff, and applies it on one approval. Running it again is the **audit**. It needs only Python 3.9+.

Harnesses it covers, each with an adapter reference: [Claude Code](references/claude-code.md).

## Steps

1. **Plan.** Run `python3 <this skill>/scripts/set_up_machine.py plan`. It writes nothing, but it starts each harness briefly to list the MCP tools it exposes (see *Mail tools* below). Done when you hold its whole output, which ends in either `No changes.` or a plan id.
2. **Nothing to do?** On `No changes.`, report the audit: the gaps, the stricter and extra rules, and the mail tools it found. Stop here.
3. **Ask once.** Show the user the plan output unedited, then ask for one approval of the whole diff. Its lines, per harness:
   - `added`: a rule the harness lacks.
   - `tightened`: a rule the harness has at a looser level; the stricter entry is added beside it.
   - `removed`: an entry this skill wrote earlier that the table no longer has. Only these are ever removed.
   - `present`: already in place, as the table's entry or a broader one that covers it.
   - `stricter`: the machine holds the rule at a stricter level than the table. It's kept; to get the table's level, the user removes that entry by hand.
   - `found`: the tools a mail-tool rule matched on this machine. Name them in your report.
   - `gap`: what the harness can't express, named so it isn't mistaken for enforced.
   - `extra`: a rule on the machine the table doesn't have. It's kept. One worth having everywhere is a candidate row for the table.
4. **Apply** the approved plan: `python3 <this skill>/scripts/set_up_machine.py apply --plan-id <id>`, the command the plan printed. If apply refuses because the machine changed since the plan, go back to step 1 and ask again.
5. **Audit.** Run the plan again. Done when it ends `No changes.`. Report the backup folder apply printed, the gaps, the stricter and extra rules, and the mail tools found.

`--home <dir>` points every step at another home folder, such as a copy of this one in the project's `.scratch/`, to try a change without touching the real machine.

## What reconcile promises

- **It never removes or loosens an entry it didn't write.** The manifest `~/.config/agents/set-up-machine.json` lists every entry it wrote, per harness; everything else is the user's.
- **The stricter rule wins** where two overlap, in the table or on the machine.
- **The shared file is the user's outside the generated block.** The block between the `set-up-machine:rules` markers is regenerated from the table; the rest is never touched.
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

## Mail tools

Only the running harness knows which MCP tools it exposes, and their names differ by harness and by how a connector is attached. So plan asks each harness for its tool list, matches the table's MCP-tool rows against it, and prints a `found` line per row. If a harness can't be asked (not installed, not logged in), the plan says so as a gap and keeps the entries it wrote before. `--tool-names <file>`, one name per line, supplies the list instead.

## Adding a harness

One adapter module in `scripts/setupmachine/adapters/`, registered in its `__init__.py`, and one reference file in `references/` covering the same headings as [Claude Code's](references/claude-code.md). Tests: `python3 -m unittest discover -s <this skill>/scripts/tests`.
