# Design: set-up-machine

How `set-up-machine` is built. A newcomer needs three facts first:

- The **agent** sets up a machine. It reads the workstation repo's `setup/` and one reference per harness, proposes one diff, and writes it. No script writes a harness file.
- Two scripts exist. The **hook** (`scripts/pre_tool_hook.py`) runs before every tool call and refuses what the rule table denies. The **verifier** (`scripts/verify.py`) reads the machine and prints one table: a harness environment on each row, a setup area in each of five columns, and the declared config in a sixth.
- `scripts/setupmachine/harnesses/__init__.py` holds `ALL`, the one list of harness environments. Everything about one harness sits in `harnesses/<harness>/` and `references/<harness>/`: one module and one page per environment, and the shared code and page beside them.

## Requirements

1. **Apply.** Bring every harness found on the machine in line with the rule table and the workstation repo's `setup/`: the shared global instructions, each harness's own instructions, permissions, the hook, memory off, declared config, plugins, skills and commands. One approval for one diff, a backup, then the write.
2. **Reapply.** A second run on a set-up machine proposes only what changed.
3. **Enforce.** The hook refuses each tool call a deny row matches, in every harness, and names the row's instruction.
4. **Verify.** One run answers "did every harness get what `setup/` asks for?" It exits 1 when any cell is `FAIL`.
5. **Readable.** A person who opens a script reads, at its top, what it is for and the steps it takes.
6. **Error handling.** A missing or malformed workstation file is a `FAIL` line that names the file. The hook fails open when its script is missing, except in Pi, which has no native rules under it.
7. **Out of scope:** writing harness files from a script, pinned versions, unit tests kept in the repo, and checking upstream release versions from the verifier, which the agent does in Inspect.

## Entities and relationships

- **Rule table** (`rules.json`): every global rule once, by meaning, with samples. Personal rows from `setup/permissions.json` join it.
- **Workstation setup**: `setup/` in the workstation repo, found through the pointer `~/.config/agents/source.md`, and the source of every personal part.
- **Harness**: one coding agent, with the environments it runs in; SKILL.md > *Harnesses* lists them. Each environment knows its own paths, its hook payload, and how to check each setup area.
- **Setup area**: instructions, guardrails, sandbox, plugins, skills. Five of the verifier's six columns.
- **Declared config**: the keys a harness's `config` file in the workstation repo sets, such as its default model, merged into the harness's own config file. The verifier's last column, `config`.
- **Hook**: decides one tool call against the rule rows.
- **Verifier**: runs the global checks, then each harness's area checks, and prints the table.

```text
agent ──reads──▶ SKILL.md ──▶ references/<harness>/<env>.md ──▶ writes the environment's files
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
│   ├── <harness>/              # one folder per harness
│   │   ├── index.md            #   what its environments share, when it has more than one
│   │   └── <env>.md            #   one per environment, same headings: Found, Instructions, Guardrails,
│   │                           #   Sandbox, Plugins, Skills, Config, Hook wiring, Gaps, Checking it
│   ├── workstation.md          # the format of every setup/ file, and the run without one
│   ├── global-instructions.md  # the shared file's shape
│   ├── rule-table.md           # a row's fields, match kinds, spellings
│   ├── remote-machine.md, new-remote-machine.md
│   # opencode/opencode-plugin.js, pi/pi-extension.ts: the hook's wiring files for those harnesses
└── scripts/
    ├── pre_tool_hook.py        # entry: payload in → decide → the harness's answer out
    ├── verify.py               # entry: global checks, the table, the exit code
    └── setupmachine/
        ├── rules.py            # load and validate rows; glob and MCP-name helpers
        ├── commands.py         # read shell text the way the shell runs it
        ├── hook.py             # decide(call, rows) → deny, ask, report or nothing
        ├── workstation.py      # the pointer, the setup/ files, the generated shared file
        ├── checks.py           # Cell, Context and the helpers every harness check shares
        └── harnesses/
            ├── __init__.py     # ALL: the one list of environments; --harness and --env select from it
            ├── <harness>/
            │   ├── __init__.py # what its environments share, such as the hook payload
            │   └── <env>.py    # one environment: paths, read/write hook payload, check per area
            └── codex/         # shared local checks, cli.py and desktop.py
```

**An environment module** exposes the same names, so a reader learns one and knows them all:

| Name | What it is |
|---|---|
| `ID`, `LABEL` | `"cursor"`, `"Cursor"`: the harness, the same for each of its environments; the key in `setup/harnesses.json` and `installs.json`, and the hook's `--harness` |
| `ENV` | `"cloud"`: the environment, what `--env` selects; the row reads `Cursor / cloud`. A module not yet split has no `ENV` |
| `present(home)` | its folder exists, or its CLI is on `PATH` |
| `read(payload)` | the hook payload as one `ToolCall` |
| `write(denials, asks)` | the harness's answer to the hook |
| `check_instructions(ctx)` … `check_skills(ctx)`, `check_config(ctx)` | one `Cell(status, detail)` per column |

- **Statuses:** `ok`; `FAIL`; `gap` when the harness can't do it or the check can't see it; and `n/a` when the area does not apply.
- **Exit code:** only `FAIL` sets exit code 1.
- **Cell:** the worst of its checks: `FAIL`, then `gap`, then `ok`.
- **Declared config:** `checks.declared_problems` compares a declared config with the harness's file for every harness, key by key, each value as a whole.
  - Codex reads both sides as TOML, and the other harnesses as JSON.
  - Codex's declared `sandbox_mode`, `approval_policy` and `approvals_reviewer` are checked in its sandbox column, and its other keys in config, so one wrong value is one `FAIL`.
- **Codex trust hash:** `verify.py --codex-trust-hash COMMAND` prints the hash Codex needs to trust the hook, since `references/codex/index.md` gives it to the user.

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
  Live      a real session of each harness in the session host, one probe each,
            then the disk and the screen read (references/live-check.md)
```

**The verifier:**

```text
verify.main
  workstation.load(home)              → pointer, setup files, or FAIL naming the bad file
  global lines
    setup    pointer + shared file match the generated text
    rules    every rule sample gets its row's answer from hook.decide
  for h in ALL if h.present(home)
    row = [h.check_instructions(ctx), …, h.check_skills(ctx), h.check_config(ctx)]
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

## Decisions

- **One package per harness, one module per environment.** Cursor runs as a CLI, a desktop app and a cloud agent; each reads different files, so each is graded on its own row. What they share, such as the hook payload, sits once in the package's `__init__.py`. A harness with one environment is a package too, so a second environment is one new module. An id names a harness only, never an environment: the environment is its own dimension, in `ENV`, in `--env` and in `setup/harnesses.json`'s `environments`.

- **`config` is a verifier column beside the five setup areas, not a sixth setup area.** A default model or reasoning effort is a personal choice, not part of setting a harness up: it is neither instructions, guardrails, sandbox, plugins nor skills. Before, Pi's declared settings sat in its sandbox column and Codex allowed only sandbox keys, so a declared model had nowhere to go. Now every harness can declare a config, the sandbox column holds sandbox state only, and the last column checks the declared keys, `n/a` without a declared config.

## Extensibility

| Change | What you touch |
|---|---|
| Add a harness | a row in SKILL.md > *Harnesses*; `harnesses/<h>/<env>.py` with the names above; one line in `ALL`; `references/<h>/<env>.md` with the same headings |
| Add an environment to a harness | its name in its row of SKILL.md > *Harnesses*; `harnesses/<h>/<env>.py`, moving shared code into `harnesses/<h>/__init__.py`; one line in `ALL`; `references/<h>/<env>.md`, and `references/<h>/index.md` for what the environments share |
| Add a Codex environment | add its adapter and reference page; keep local shared configuration separate from hosted execution |
| Add a global rule | one row with samples in `rules.json`; each harness reference already says how a row becomes native entries |
| Add a setup area | the glossary's setup areas first; one `check_<area>` in every harness module; one column |
| Declare a new config key | the workstation repo's `config` file only; the `config` column compares every key it sets |
| A harness changes its file format | its `references/<h>/` and its `harnesses/<h>/` only |

Not now: unit tests in the repo. A maintainer writes throwaway tests in `.scratch/` while changing a script, and the rule samples, run by the verifier, are the check that stays.
