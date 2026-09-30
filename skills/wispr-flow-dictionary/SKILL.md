---
name: wispr-flow-dictionary
description: Tune the Wispr Flow dictionary from real dictation history through a local CLI - find the names, products and commands it mishears, fix them safely, and check the fixes worked. Use when the user reports a Wispr Flow transcription mistake ("I said X, it wrote Y"), wants mistakes found in a time window, asks about their Wispr Flow dictations, or wants dictionary words, rules or snippets changed.
---

# Wispr Flow dictionary

Wispr Flow is a macOS dictation app. It has no CLI, and its remote MCP server covers meetings, not dictation history or the dictionary. It keeps both in a local SQLite database, and `scripts/wispr.py` is the interface to it. Go through the script for every read and write, so the database internals stay in one place.

```bash
python3 <skill-dir>/scripts/wispr.py <command> --help
```

| Command | What it does |
|---|---|
| `status` | Run it first. A `CHANGED` schema means an app update changed the database tables the script reads and writes: stop and inspect those tables before any write. |
| `history` | Dictations in a window (`--since 30m`, `3h`, `2d`, `1h30m`, or `--from`/`--to`). `--diff` shows only the words formatting swapped; `--out FILE` for large windows. |
| `terms` | Name-like and command-like words in a window, with counts, whether the dictionary has them, and hits since it got them. |
| `snippets` | Links, emails and sentences dictated in full again and again, and whether a snippet already expands to them. |
| `count TERM...` | Dictations containing each term, whole word, any case, with hits since its dictionary entry was added. `--field formatted` counts only what was pasted. Take every count you report from this command. |
| `dict list` / `add` / `remove` / `undo` / `backup` | The dictionary. Every write backs up first; `add` prints a batch id that `undo` reverts. `--restart` quits Wispr Flow before the write and relaunches it after, which is how the app loads a change. `add --snippet` makes a trigger phrase that expands to `--replace`. |

Backups go to `~/.local/state/wispr-flow/backups/`; the newest 30 are kept (`--backup-dir`, `--keep-backups`, or the `WISPR_FLOW_*` variables to change it).

## The dictionary

- A **word** (phrase, no replacement) teaches Wispr the term. Fix with a word first, for a mishearing as much as a misspelling: add `Herdr`, not `Herder` → `Herdr`.
- A **rule** (phrase plus replacement) rewrites a phrase every time it is heard. Propose one only when the mistake keeps coming after its word was added (`Since added` above zero in formatted text), or when the intended word is an ordinary one a word entry can't teach (`work tree` → `worktree`). The user decides.
- A rule's phrase matches whole words, so a plural needs its own rule (`cloud sessions`).
- Matching ignores case. Add each entry once, spelled exactly as it should appear: brand casing for names (`GitHub`, `WebMCP`), lowercase for commands (`npx`, `to-pr`). A second entry in another case does nothing.
- A rule is safe only when its phrase is not something the user also means literally. `city` → `Citi` breaks the word city; add `Citi` as a word instead.
- A **snippet** is a short trigger phrase that expands to longer text (`my email address` → the address). Propose one only for text the user dictates in full again and again.
- Entries the app learned from the user's edits have `source: user_edits`, and `observedSource` holds what it had heard.

## Fixing a mistake the user just reported

When the user says a word came out wrong ("I said skill, it wrote SQL"), fix it in the same turn:

1. `count` both forms over the full history (`--since 26w`), to see whether the wrong form is also a word the user means (SQL was: several dictations meant it).
2. If the intended word is missing, `dict add <word> --restart`. If the word is there and `Since added` shows the mistake returning, propose a rule instead. If the wrong form is also a word the user means, propose no rule and tell the user why a rule would do harm.
3. Tell the user what was added, and that the next review will show whether it held.

## Finding transcription mistakes

Look for the words speech recognition gets wrong most, and more so with a non-native accent: names of people, companies, products, tools, and CLI commands.

1. **Read.** `status`, `dict list`, `terms --since <window>`, and `history --since <window> --diff`. Unless the user names a window, use the last 24 hours. Then read the whole window with `history --since <window> --fields raw,formatted`: `terms` and `--diff` miss mishearings that came out as ordinary words the formatter left unchanged ("verb tree", "two PR"). For a window longer than a few hours this output is too large for one call (about 30k tokens per day of dictation), so write it with `--out` to a file in the project's temp folder and read that file in pages.
2. **Find candidates.** Go through the `terms` table and every dictation for words that are wrong in context: a real word where a name belongs ("Herder session", "cloud code"), a name spelled several ways, a command turned into a word ("Sila" for CLI). Check the raw text too; formatting sometimes hides a mishearing and sometimes fixes it.
3. **Confirm the intended word** from the surrounding text and the user's projects: the one open now, and any other the dictation was about (the `app` column shows where it went). Grep them for the name. Where the intended word can't be established, list it under **Unclear** and ask.
4. **Count.** Run `count` over the same window with every misheard form and every intended form, and `snippets --since 30d`. Take each number in the report from these two commands.
5. **Report**, in exactly this shape:

   ```markdown
   ### Words to add
   | Word | Wispr wrote | Dictations | Example |

   ### Rules to add
   | Wispr writes | You meant | Dictations | Since its word was added | Example |

   ### Snippets to add
   | Trigger | Expands to | Dictations |

   ### Not fixable with the dictionary
   - <mishearing>: <why a rule would do harm, or what would fix it instead>

   ### Unclear
   - "<what Wispr wrote>": <the context>. What did you say?
   ```

   Leave out anything already in the dictionary unless it is still being misheard after it was added; then it moves to **Rules to add** ("`CLI` is a word since 09-28, heard as Sila twice since"). Drop any section that is empty.
6. **Write** only after the user approves the list. Put the approved entries in a JSON file (`[{"phrase": "Teamtailor"}, {"phrase": "work tree", "replacement": "worktree"}, {"phrase": "my site", "replacement": "https://example.com", "snippet": true}]`), run `dict add --file <file> --dry-run`, then `dict add --file <file> --restart` (Wispr Flow is closed for a few seconds, so say so first), and give the user the batch id.

The app syncs the dictionary to the user's account. Entries written this way have survived a restart; whether a sync ever drops them is not known, so say so when reporting a write.
