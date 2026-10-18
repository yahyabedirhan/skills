# Rule table

The format of a row of the rule table, `rules.json`, and of a personal permission: its fields, its `match` kinds, and the spellings a harness that matches text needs. This file describes each field once.

## Row

| Field | Holds |
|---|---|
| `id` | a stable kebab-case name |
| `level` | `deny`, `ask` or `allow-and-report`; a personal permission may also be `allow` |
| `summary` | what the rule covers, shown in rejection messages |
| `match` | what it covers, in one of the three kinds below |
| `reason` | why the rule exists |
| `instruction` | for `deny`, what the agent does instead: an alternative, or "Stop, say why, and give the user the exact command; never work around it."; for `ask` and `allow-and-report`, how to go ahead |
| `samples` | `covers`: calls the row must catch; `leaves`: near misses it must let through. A shell command for a command row, a path for a file row, a tool name for an MCP row. `verify.py` checks them against the hook |
| `gap` | optional: what no harness can catch for the row (`echo $TOKEN`); every audit names it |
| `approver` | optional, on an `ask` row only: `user` when each call needs the user's own approval, which an automatic reviewer's or a remembered answer's doesn't replace |

## `match` kinds

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

## Spellings

A harness that matches a command's text catches only the spellings it lists, so give it one entry per way of writing a command row:

- **Programs:** each program as typed, then as `/bin/<program>` and `/usr/bin/<program>`, except shell builtins (`.`, `source`, `set`, `export`, `declare`, `typeset`, `unset`, `eval`, `alias`), which have no path.
- **Flags:** a one-letter name is a short flag (`-r`), a longer one a long flag (`--recursive`). Every order of the groups, every spelling in each group, as separate words; and, when every group has a one-letter name, the one-letter names clustered in every order (`-rf`, `-fr`, `-Rf`, `-fR`).
- **Order:** program, then subcommand words, then flags, then operands (`git push --force`, `chmod -R 777`).
- **`find`'s options** (`-delete`) are one-dash words written after the path, so no prefix entry catches them: a command row on `find` gets no native entry, a gap the hook covers on every harness.
