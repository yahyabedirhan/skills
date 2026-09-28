---
name: wispr-flow
description: Read Wispr Flow dictation history and read or change its dictionary through a local CLI. Use when the user asks about their Wispr Flow dictations, wants transcription mistakes found in a time window, or wants its dictionary changed.
---

# Wispr Flow

Wispr Flow is a macOS dictation app. It has no official CLI; it keeps everything in a local SQLite database, and `scripts/wispr.py` is the interface to it. Go through the script for every read and write, so the database internals stay in one place.

```bash
python3 <skill-dir>/scripts/wispr.py <command> --help
```

| Command | What it does |
|---|---|
| `status` | Run it first. A `CHANGED` schema means an app update moved things: stop and read the tables before writing. |
| `history` | Dictations in a window (`--since 30m`, `3h`, `2d`, `1h30m`, or `--from`/`--to`). `--out FILE` for large windows. |
| `terms` | Name-like and command-like words in a window, with counts, raw-only hits, and whether the dictionary has them. |
| `count TERM...` | Dictations containing each term. The source of every count you report. |
| `dict list` / `add` / `remove` / `undo` / `backup` | The dictionary. Every write backs up first; `add` prints a batch id that `undo` reverts. |

Backups go to `~/.local/state/wispr-flow/backups/` (`--backup-dir` or `WISPR_FLOW_BACKUP_DIR` to change it).

## The dictionary

- A **word** (phrase, no replacement) teaches Wispr a spelling. It helps when the word was heard correctly but spelled wrong. It does not stop an accent turning the word into a different one: a word already in the dictionary can still come out wrong.
- A **rule** (phrase plus replacement) rewrites what Wispr heard into what was meant, every time. It is the fix for a consistent mishearing: `Herder` → `Herdr`, `Sila` → `CLI`.
- Matching ignores case. Add each entry once, spelled exactly as it should appear: brand casing for names (`GitHub`, `WebMCP`), lowercase for commands (`npx`, `to-pr`). A second entry in another case does nothing.
- A rule is safe only when its phrase is not something the user also means literally. `city` → `Citi` breaks the word city; add `Citi` as a word instead.
- Entries the app learned from the user's edits have `source: user_edits`, and `observedSource` holds what it had heard. Snippets are rows with long replacements; leave them alone.

## Finding transcription mistakes

The targets are the words speech recognition gets wrong most, and more so with a non-native accent: names of people, companies, products, tools, and CLI commands.

1. **Read.** `status`, `dict list`, and `terms --since <window>`. Default window: 24 hours. Then read the whole window with `history --since <window> --fields raw,formatted`. Past a few hours the output outgrows one read (about 30k tokens a day), so write it with `--out` to the project's temp folder and read the file in pages; `terms` alone misses mishearings that land on ordinary lowercase words ("verb tree", "two PR").
2. **Find candidates.** Go through the `terms` table and every dictation for words that are wrong in context: a real word where a name belongs ("Herder session", "cloud code"), a name spelled several ways, a command turned into a word ("Sila" for CLI). Check the raw text too; formatting sometimes hides a mishearing and sometimes fixes it.
3. **Confirm the intended word** from the surrounding text and the project the user is working in (grep its files for the name). Where the intended word can't be established, list it under **Unclear** and ask.
4. **Count.** Run `count` over the same window with every misheard form and every intended form. Each number in the report comes from it.
5. **Report**, in exactly this shape:

   ```markdown
   ### Rules to add
   | Wispr writes | You meant | Dictations | Example |

   ### Words to add
   | Word | Why |

   ### Not fixable with the dictionary
   - <mishearing>: <why a rule would do harm, or what would fix it instead>

   ### Unclear
   - "<what Wispr wrote>": <the context>. What did you say?
   ```

   Leave out anything already in the dictionary unless it is still being misheard; say so when it is ("`CLI` is a word already, still heard as Sila: add a rule").
6. **Write** only after the user approves the list. Put the approved entries in a JSON file (`[{"phrase": "Herder", "replacement": "Herdr"}, {"phrase": "Teamtailor"}]`), run `dict add --file <file> --dry-run`, then without `--dry-run`, and give the user the batch id.
7. **Hand over** the one step the script can't do: the user restarts Wispr Flow so it loads the new entries, then checks its Dictionary screen.

The app syncs the dictionary to the user's account. Entries written this way have survived a restart; whether a sync ever drops them is not known, so say so when reporting a write.
