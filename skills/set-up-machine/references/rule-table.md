# The rule table

`rules.json` holds each global rule once, by meaning, not in any harness's form. Each harness reference turns a row into that harness's entries; the hook and `verify.py` read it through `scripts/setupmachine/rules.py`, which refuses a malformed row.

## A row

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
| `guard` | optional, `deny` rows: `label` and `rule`, prose for a semantic guard (Claude Code's auto mode; claude-code.md says when it's on) |

## `match` kinds

Told apart by their keys:

- **Command:** `program`, a bare name (`rm`) or a list of them, and optionally:
  - `subcommands`: alternative word lists after the program (`[["repo", "delete"], ["repo", "archive"]]`);
  - `flags`: every flag group the command carries, each listing one flag's names without dashes, a one-letter name being the short flag (`["r", "R", "recursive"]`);
  - `operands`: words right after the subcommand and flags (`["777"]`), or alternative word lists (`[["777"], ["a+rwx"]]`);
  - `any_operand`: words any one of which may appear anywhere after the subcommand (`["main", "master"]`);
  - `arguments: "none"`: the program with nothing after it (`env`); `arguments: "flags"`: with flags and nothing else (`declare -x`);
  - `files`: globs one of its operands must match (`cat .env`), with an optional `except`.
- **File:** `paths`, globs relative to the project (`**/.env`), or starting `~/` or `/`; `access`, `read` or `write`; an optional `except` (`**/.env.example`). A `read` row covers writes too.
- **MCP tool:** `server` and `tool`, case-insensitive regular expressions over the two parts of `mcp__<server>__<tool>`. Store the meaning (`mail`, `^(send|reply|forward)`), never one account's server ID.

## Changing it

Edit a row, or add one with its samples, then run `python3 <skill>/scripts/verify.py --no-codex` until `rules ok`, and the unit tests (`python3 -m unittest discover -s <skill>/scripts/tests`). The change reaches a machine when set-up-machine runs there again. A row the hook can't read the way the row means is a hook change first, test-first in `tests/test_hook.py`.
