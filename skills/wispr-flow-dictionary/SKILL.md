---
name: wispr-flow-dictionary
description: Tune the Wispr Flow dictionary from real dictation history through a local CLI - find the names, products and commands it mishears, fix them safely, and check the fixes worked. Use when the user reports a Wispr Flow transcription mistake ("I said X, it wrote Y"), wants mistakes found in a time window, asks about their Wispr Flow dictations, or wants dictionary words, rules or snippets changed.
---

# Wispr Flow dictionary

Wispr Flow is a macOS dictation app. It has no CLI, and its remote MCP server covers meetings, not dictation history or the dictionary. It keeps both in a local SQLite database, and `scripts/wispr.py` is the interface to it. Go through the script for every read and write, so the database internals stay in one place.

Run `status` first. When it reports a `CHANGED` schema, stop and inspect the changed tables before any write. Take every count you report from `count`. Read `command-reference.md` before the first command.

## The dictionary

- A **word** (phrase, no replacement) teaches Wispr the term. Fix with a word first, for a mishearing as much as a misspelling: add `Herdr`, not `Herder` → `Herdr`.
- A **rule** (phrase plus replacement) rewrites a phrase every time it is heard. Propose one only when the mistake keeps coming after its word was added, that is `Since added` above zero in formatted text, or when the intended word is an ordinary one a word entry can't teach, such as `work tree` → `worktree`. The user decides.
- A rule's phrase matches whole words, so a plural needs its own rule (`cloud sessions`).
- Matching ignores case. Add each entry once, spelled exactly as it should appear: brand casing for names (`GitHub`, `WebMCP`), lowercase for commands (`npx`, `to-pr`). A second entry in another case does nothing.
- A rule is safe only when its phrase is not something the user also means literally. `city` → `Citi` breaks the word city; add `Citi` as a word instead.
- A **snippet** is a short trigger phrase that expands to longer text, such as `my email address` → the address. Propose one only for text the user dictates in full again and again.

## Fixing a mistake the user just reported

When the user says a word came out wrong ("I said skill, it wrote SQL"), fix it in the same turn:

1. `count` both forms over the full history (`--since 26w`), to see whether the wrong form is also a word the user means. SQL was: several dictations meant it.
2. Choose the fix:
   - **If the intended word is missing:** add it as a word with `--restart`.
   - **If the word is there and `Since added` shows the mistake returning:** propose a rule instead.
   - **If the wrong form is also a word the user means:** propose no rule, and tell the user why a rule would do harm.
3. Tell the user what was added, and that the next review will show whether it held.

## Finding transcription mistakes

Look for the words speech recognition gets wrong most, and more so with a non-native accent: names of people, companies, products, tools, and CLI commands.

1. **Read** the dictionary, the `terms` table and the `--diff` history for the window, the last 24 hours by default. Then read every dictation in the window, raw and formatted: `terms` and `--diff` miss mishearings that came out as ordinary words the formatter left unchanged ("verb tree", "two PR").
   - **When the user names a window:** use that window instead.
2. **Find candidates:** words that are wrong in context, such as a real word where a name belongs ("Herder session", "cloud code"), a name spelled several ways, or a command turned into a word ("Sila" for CLI). Check the raw text too; formatting sometimes hides a mishearing and sometimes fixes it.
3. **Confirm the intended word** from the surrounding text and the user's projects: the one open now, and any other the dictation was about, which the `app` column shows. Grep them for the name.
   - **Where the intended word can't be established:** list it under **Unclear** and ask.
4. **Count** every misheard form and every intended form over the same window, and repeated snippets over the last 30 days.
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

   Leave out anything already in the dictionary.
   - **When an entry is still being misheard after it was added:** it moves to **Rules to add** ("`CLI` is a word since 09-28, heard as Sila twice since").
   - **When a section is empty:** drop it.
6. **Write** only after the user approves the list: dry-run the batch first, tell the user Wispr Flow will close for a few seconds, write it with `--restart`, and give the user the batch id.

The app syncs the dictionary to the user's account. Entries written this way have survived a restart; whether a sync ever drops them is not known, so say so when reporting a write.

## References

- [command-reference.md](command-reference.md): the script's commands and flags, reading a long window, and the batch file format.

## Scripts

- [scripts/wispr.py](scripts/wispr.py): the one interface to Wispr Flow's database.
