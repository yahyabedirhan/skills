# Command reference

```bash
python3 <skill-dir>/scripts/wispr.py <command> --help
```

| Command | What it does |
|---|---|
| `status` | Checks the database. A `CHANGED` schema means an app update changed the database tables the script reads and writes. |
| `history` | Dictations in a window (`--since 30m`, `3h`, `2d`, `1h30m`, or `--from`/`--to`). `--diff` shows only the words formatting swapped; `--fields raw,formatted` shows both texts; `--out FILE` writes to a file. |
| `terms` | Name-like and command-like words in a window, with counts, whether the dictionary has them, and hits since it got them. |
| `snippets` | Links, emails and sentences dictated in full again and again, and whether a snippet already expands to them. |
| `count TERM...` | Dictations containing each term, whole word, any case, with hits since its dictionary entry was added. `--field formatted` counts only what was pasted. |
| `dict list` / `add` / `remove` / `undo` / `backup` | The dictionary. Every write backs up first; `add` prints a batch id that `undo` reverts. `--restart` quits Wispr Flow before the write and relaunches it after, which is how the app loads a change. `add --snippet` makes a trigger phrase that expands to `--replace`. |

Backups go to `~/.local/state/wispr-flow/backups/`; the newest 30 are kept. `--backup-dir`, `--keep-backups` or the `WISPR_FLOW_*` variables change that.

Entries the app learned from the user's edits have `source: user_edits`, and `observedSource` holds what it had heard.

## Reading a long window

`history --fields raw,formatted` costs about 30k tokens per day of dictation. For a window longer than a few hours, write it with `--out` to a file in the project's temp folder and read that file in pages.

## Writing a batch

Put the approved entries in a JSON file:

```json
[{"phrase": "Teamtailor"}, {"phrase": "work tree", "replacement": "worktree"}, {"phrase": "my site", "replacement": "https://example.com", "snippet": true}]
```

Run `dict add --file <file> --dry-run`, then `dict add --file <file> --restart`.
