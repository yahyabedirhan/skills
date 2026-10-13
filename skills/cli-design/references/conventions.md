# Conventions

Defaults for the names, codes and layouts a CLI shares with other CLIs. Callers carry these expectations from the tools they already use, so a CLI that follows them is learned faster. A project's own established conventions win over these.

## Verbs

Pick one word per meaning and use it on every noun that supports it.

| Verb | Meaning | Avoid alongside it |
|---|---|---|
| `list` | print many items; changes nothing | `ls`, `show` for many |
| `get` | print one item; changes nothing | `show`, `describe`, `info` for the same thing |
| `create` | make a new item | `new`, `add`, `make` |
| `update` | change fields of an existing item | `edit`, `modify`, `set` for whole items |
| `set` / `unset` | change or clear one value or setting | `update` for single values |
| `delete` | destroy an item | `remove`, `rm`, `destroy` |
| `add` / `remove` | put an existing item into a parent, or take it out | `create`/`delete` for membership |
| `start` / `stop` | run or end a process, a session or a mode | `run`/`kill`, `begin`/`end` |
| `open` / `close` | bring up or dismiss a file, a window, a panel or a connection | `show`/`hide` for the same thing |
| `wait` | block until an event happens, with a timeout | `watch` for a one-shot wait |
| `watch` | print events as they happen until interrupted | |
| `login` / `logout` | start or end an authenticated session | `auth` as a verb |

Avoid two commands whose names look alike and mean different things, such as `update` and `upgrade`.

## Flags

| Flag | Meaning |
|---|---|
| `-h`, `--help` | print help and exit 0 |
| `--version` | print the version and exit 0 |
| `--json` | print machine-readable JSON on standard output |
| `-q`, `--quiet` | print less; errors only |
| `-v`, `--verbose` | print more; repeatable for more detail |
| `-f`, `--force` | skip a confirmation or a safety check |
| `-y`, `--yes` | answer yes to every prompt |
| `-n`, `--dry-run` | say what would happen and change nothing |
| `-o`, `--output <file>` | write the output to a file |
| `--no-input` | never prompt; fail when input is missing |
| `--no-color` | print no colour codes |
| `--timeout <duration>` | give up waiting after this long |

## Exit codes

| Code | Meaning |
|---|---|
| 0 | success |
| 1 | the command failed or was refused |
| 2 | wrong usage; most parsing libraries use it, and `sysexits.h` names 64 for the same meaning |
| 130 | interrupted with Ctrl-C (128 + SIGINT) |

Add a code only for a case a caller handles differently from failure, such as a timeout or "nothing found", and document it in the help.

## Environment variables

- `NO_COLOR`: print no colour when it is set to any value.
- `TERM=dumb`: print no colour or cursor movement.
- `PAGER`, `EDITOR`: the programs to use for paging and editing.
- `TOOL_*`: the CLI's own variables, prefixed with its name in capitals, each one listed in the help and the docs.

## Configuration precedence

From highest to lowest: flags, environment variables, the project's configuration file, the user's configuration file (under `$XDG_CONFIG_HOME` or the platform's equivalent), the system's configuration file, built-in defaults. A command that reads configuration can say which source each value came from.

## Help layouts

The top help, for `tool --help` and `tool` alone:

```text
<tool>: <one line on what it is>

Usage: <tool> <command> [options]
       <tool> <group> <command> [options]

<Section for the main job>:
  <command> <words>     <summary>
  ...

<Section for another job>:
  <group>               <summary>
  ...

Options:
  --json        print JSON
  -h, --help    show help for any command
  --version     print the version

Environment:
  <TOOL>_<NAME>   <what it changes>

Exit codes: 0 success, 1 failed, 2 wrong usage.

Learn more: <docs link>. Run '<tool> <group> --help' for a group's commands.
```

A group's help, for `tool <group> --help` and `tool <group>` alone:

```text
<summary of the group>

Usage: <tool> <group> <command> [options]

Commands:
  <tool> <group> <verb> <words> [--flag <value>]
      <summary>
  ...

Run '<tool> <group> <verb> --help' for a command's details.
```

A command's help, for `tool <group> <verb> --help`:

```text
<summary>

Usage: <tool> <group> <verb> <words> [options]

Examples:
  <tool> <group> <verb> <a typical call>
  <tool> <group> <verb> <a call with options>

<A short description: what it does, what it changes, when to use it.>

Options:
  --flag <value>   <meaning; the default>

Exit codes: <the codes this command can return beyond the usual ones>
```

Align each column to its own section, not to the longest line in the whole help, so one long usage line doesn't push every summary off the screen.

---

Sources: [Command Line Interface Guidelines](https://clig.dev/), [POSIX Utility Conventions](https://pubs.opengroup.org/onlinepubs/9799919799/basedefs/V1_chap12.html), [sysexits.h](https://man.freebsd.org/cgi/man.cgi?query=sysexits), [NO_COLOR](https://no-color.org/) and the [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/latest/).
