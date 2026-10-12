# Design: set-up-machine

How `set-up-machine` is built. A newcomer needs three facts first:

- The **agent** sets up a machine. It reads the workstation repo's `setup/` and one reference per harness, proposes one diff, and writes it. No script writes a harness file.
- Two scripts exist. The **hook** (`scripts/pre_tool_hook.py`) runs before every tool call and refuses what the rule table denies. The **verifier** (`scripts/verify.py`) reads the machine and prints one table: a harness on each row and a setup area in each column.
- `scripts/setupmachine/harnesses/__init__.py` holds `ALL`, the one list of harnesses. Everything about one harness sits in `harnesses/<harness>.py` and `references/<harness>.md`.

## Requirements

1. **Apply.** Bring every harness found on the machine in line with the rule table and the workstation repo's `setup/`: the shared global instructions, each harness's own instructions, permissions, the hook, memory off, declared config, plugins, skills and commands. One approval for one diff, a backup, then the write.
2. **Reapply.** A second run on a set-up machine proposes only what changed.
3. **Enforce.** The hook refuses each tool call a deny row matches, in every harness, and names the row's instruction.
4. **Verify.** One run answers "did every harness get what `setup/` asks for?" It exits 1 when any cell is `FAIL`.
5. **Readable.** A person who opens a script reads, at its top, what it is for and the steps it takes.
6. **Error handling.** A missing or malformed workstation file is a `FAIL` line that names the file. The hook fails open when its script is missing, except in Pi, which has no native rules under it.
7. **Out of scope:** writing harness files from a script, pinned versions, unit tests kept in the repo, and checking upstream release versions from the verifier (the agent does that in Inspect).

## Entities and relationships

- **Rule table** (`rules.json`): every global rule once, by meaning, with samples. Personal rows from `setup/permissions.json` join it.
- **Workstation setup** (`setup/` in the workstation repo, found through the pointer `~/.config/agents/source.md`): the source of every personal part.
- **Harness**: one coding agent (Claude Code, Codex, opencode, Cursor, Pi). It knows its own paths, its hook payload, and how to check each setup area.
- **Setup area**: instructions, guardrails, sandbox, plugins, skills. The columns of the verifier's table.
- **Hook**: decides one tool call against the rule rows.
- **Verifier**: runs the global checks, then each harness's area checks, and prints the table.

```text
agent ──reads──▶ SKILL.md ──▶ references/<harness>.md ──▶ writes the harness's files
agent ──reads──▶ workstation setup/   (the skill never writes the workstation repo)
harness ──calls──▶ pre_tool_hook.py ──▶ hook.decide ──▶ rules + personal rows
verify.py ──▶ global checks (pointer, shared file, rule samples)
          ──▶ for h in ALL: h.check_<area>() ──▶ table
```

## Class design

```text
skills/set-up-machine/
├── SKILL.md                    # sources, outputs, the steps, what verify must show
├── rules.json                  # the rule table, with samples per row
├── references/
│   ├── <harness>.md            # one per harness, same headings: Found, Instructions, Guardrails,
│   │                           #   Sandbox, Plugins, Skills, Hook wiring, Gaps, Checking it
│   ├── workstation.md          # the format of every setup/ file, and the run without one
│   ├── global-instructions.md  # the shared file's shape
│   ├── rule-table.md           # a row's fields, match kinds, spellings
│   ├── remote-machine.md, new-remote-machine.md
│   └── opencode-plugin.js, pi-extension.ts   # the hook's wiring files for those harnesses
└── scripts/
    ├── pre_tool_hook.py        # entry: payload in → decide → the harness's answer out
    ├── verify.py               # entry: global checks, the table, the exit code
    └── setupmachine/
        ├── rules.py            # load and validate rows; glob and MCP-name helpers
        ├── commands.py         # read shell text the way the shell runs it
        ├── hook.py             # decide(call, rows) → deny, ask, report or nothing
        ├── workstation.py      # the pointer, the setup/ files, the generated shared file
        ├── checks.py           # shared helpers the harness checks use: read JSON, compare files
        └── harnesses/
            ├── __init__.py     # ALL: the one list of harnesses
            └── <harness>.py    # one harness: paths, read/write hook payload, check per area
```

**A harness module** exposes the same names, so a reader learns one and knows them all:

| Name | What it is |
|---|---|
| `ID`, `LABEL` | `"cursor"`, `"Cursor"` |
| `present(home)` | whether the harness is set up here |
| `read(payload)` | the hook payload as one `ToolCall` |
| `write(denials, asks)` | the harness's answer to the hook |
| `check_instructions(ctx)` … `check_skills(ctx)` | one `Cell(status, detail)` per setup area |

**Statuses:** `ok`, `FAIL`, `gap` (the harness can't do it, or the check can't see it), `n/a` (the area does not apply). Only `FAIL` sets exit code 1.

## Implementation (traced)

**A new machine:**

```text
agent
  Inspect   read setup/ through the pointer, each references/<h>.md for each harness found
  Diff      per harness: shared file link or copy, own instructions, rule entries, hook wiring,
            memory off, declared config keys, plugins, skills and commands from installs.json
  Approve   one approval (installs-only diffs need none)
  Back up   ~/.config/agents/backups/<UTC time>/
  Write     exactly the approved diff
  Verify    python3 scripts/verify.py
```

**The verifier:**

```text
verify.main
  workstation.load(home)              → pointer, setup files, or FAIL naming the bad file
  global lines
    setup    pointer + shared file match the generated text
    rules    every rule sample gets its row's answer from hook.decide
  for h in ALL if h.present(home)
    row = [h.check_instructions(ctx), …, h.check_skills(ctx)]
  print the table, then one line per FAIL and gap cell
  exit 1 if any FAIL
```

**A refused call (Cursor runs `rm -rf x`):**

```text
pre_tool_hook.py --harness cursor
  cursor.read(payload)        → ToolCall(tool="Shell", command="rm -rf x")
  hook.decide(call, rows)     → deny: row rm-rf, with its instruction
  cursor.write(denials)       → {"permission": "deny", ...}
```

## Extensibility

| Change | What you touch |
|---|---|
| Add a harness | `harnesses/<h>.py` with the names above; one line in `ALL`; `references/<h>.md` with the same headings |
| Add a global rule | one row with samples in `rules.json`; each harness reference already says how a row becomes native entries |
| Add a setup area | the glossary's setup areas first; one `check_<area>` in every harness module; one column |
| A harness changes its file format | its `references/<h>.md` and its `harnesses/<h>.py` only |

Not now: unit tests in the repo. A maintainer writes throwaway tests in `.scratch/` while changing a script, and the rule samples, run by the verifier, are the check that stays.
