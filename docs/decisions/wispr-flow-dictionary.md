# Decisions: wispr-flow-dictionary

The decisions behind the `wispr-flow-dictionary` skill (named `wispr-flow` until 2026-09-28). This file is for maintaining it and is never installed. Entries follow the shape in [index.md](index.md).

## 2026-09-28: write to Wispr Flow's SQLite database directly

- **Status:** accepted
- **Context:** The app has no CLI or public API for its dictionary.
- **Options:** None considered.
- **Choice and why:** Write to the database. A first batch of 56 entries, written this way with the app running, appeared after a restart and worked in dictation.
- **Consequences:** It is unknown whether a sync can drop entries written this way. Revisit if entries go missing.

## 2026-09-28: one script owns the database

- **Status:** accepted
- **Context:** An app update can change the database.
- **Options:** None considered.
- **Choice and why:** `scripts/wispr.py` holds the table and column names, the timestamp format and the personal dictionary id. `status` checks the columns it relies on before anything is written.
- **Consequences:** An app update is fixed in one file.

## 2026-09-28: every write backs up the dictionary and records a batch

- **Status:** accepted
- **Context:** A bad write must be easy to undo.
- **Options:** None considered.
- **Choice and why:** Back up before each write. New rows in one `dict add` share a `createdAt`, which `dict undo` uses to revert the batch.
- **Consequences:** None.

## 2026-09-28: deletes are soft

- **Status:** accepted
- **Context:** A sync must see a deletion.
- **Options:** Delete the row: a sync sees a row that vanished.
- **Choice and why:** Set `isDeleted = 1`, which matches what the app does.
- **Consequences:** None.

## 2026-09-28: counts come from the script

- **Status:** accepted
- **Context:** Two runs over the same window must agree.
- **Options:** The agent's estimate: it varies.
- **Choice and why:** The report's numbers are `count` output.
- **Consequences:** None.

## 2026-09-28: large windows go through a file, and terms comes first

- **Status:** accepted
- **Context:** A day of dictation is about 30k tokens, past what one read takes.
- **Options:** None considered.
- **Choice and why:** `history --out` writes the window to a file for paging. `terms` pulls the name-like and command-like words into one table, so names are reviewed without reading every sentence.
- **Consequences:** The full read stays, because mishearings that land on ordinary lowercase words ("verb tree") never look like names.

## 2026-09-28: words first, rules only for mistakes that outlive their word

- **Status:** accepted
- **Context:** The first version defaulted to rules. Its 26 rules were replaced by words the same day.
- **Options:** Rules by default: the user prefers plain dictionary words.
- **Choice and why:** Add a dictionary word first. Propose a rule only when a mistake comes back after its word was added.
- **Consequences:** This entry said `count` and `terms` show a returning mistake as hits since the entry was added. That was wrong; see [2026-09-30: a returning mistake is counted from the wrong form](#2026-09-30-a-returning-mistake-is-counted-from-the-wrong-form).

## 2026-09-28: history --diff shows only the formatter's vocabulary swaps

- **Status:** accepted
- **Context:** The full history is large: 48 hours is about 285 KB.
- **Options:** None considered.
- **Choice and why:** `history --diff` drops deleted fillers, inserted grammar words, list markup, digits and hyphenation. That takes 48 hours to 14 KB.
- **Consequences:** It catches mishearings the formatter fixed or caused, not the ones it left alone, so the full read stays.

## 2026-09-28: dict remove matches the exact spelling first

- **Status:** accepted
- **Context:** Matching any case would delete `Claude` along with a duplicate `claude`.
- **Options:** None considered.
- **Choice and why:** Match the exact spelling first.
- **Consequences:** None.

## 2026-09-28: renamed wispr-flow to wispr-flow-dictionary

- **Status:** accepted
- **Context:** Two other published skills are named `wispr-flow` (artemxtech, cathrynlavery). The old name clashed on skills.sh and in an installer's skills folder.
- **Options:** `wispr-flow-analyzer`: it reads as glebis's `wispr-analytics`, which covers analytics.
- **Choice and why:** `wispr-flow-dictionary` keeps "wispr flow" for search and says what the skill owns.
- **Consequences:** None.

## 2026-09-28: the skill owns the dictionary loop, and analytics stay out

- **Status:** accepted
- **Context:** Usage stats, recaps and wellbeing reflection are covered by other skills: glebis `wispr-analytics`, and cathrynlavery and artemxtech `wispr-flow`.
- **Options:** None considered.
- **Choice and why:** Keep the skill to the dictionary.
- **Consequences:** A recap of what the user worked on, if wanted, becomes a separate skill.

## 2026-09-28: fixes reported mid-task are applied in the same turn

- **Status:** accepted
- **Context:** The user reports mistakes while working. The idea comes from glebis `wispr-fix`, which queues them instead.
- **Options:** A queue, as in `wispr-fix`: with `--restart`, a queue isn't needed.
- **Choice and why:** Apply the fix in the same turn, after a whole-history count shows whether the wrong form is also meant literally.
- **Consequences:** None.

## 2026-09-28: writes can quit and relaunch the app

- **Status:** accepted
- **Context:** glebis's skills refuse to write while the app runs. Writing live worked here, but the app loads changes only on launch.
- **Options:** Refuse to write while the app runs, as glebis does.
- **Choice and why:** `--restart` quits and relaunches the app in the same command, which saves the user a step.
- **Consequences:** The app bundle nests a helper app with the same executable name. Quitting targets the main bundle id `com.electron.wispr-flow`, and the running check skips paths under `Resources/`.

## 2026-09-28: backups keep the newest 30

- **Status:** accepted
- **Context:** Every write makes a backup.
- **Options:** None considered.
- **Choice and why:** Keep the newest 30 of those the script made.
- **Consequences:** None.

## 2026-09-28: snippet candidates

- **Status:** accepted
- **Context:** Some repeated text is better as a snippet. The idea comes from glebis `wispr-analytics` `propose`.
- **Options:** None considered.
- **Choice and why:** Snippet candidates are links, emails, and sentences of 8 or more words repeated in 2 or more dictations.
- **Consequences:** None.

## 2026-09-28: also a Claude Code plugin, from a marketplace in this repo

- **Status:** accepted
- **Context:** Claude Code users could install the skill as a plugin.
- **Options:** A `source` of `./`: it would load every skill in the repo.
- **Choice and why:** `.claude-plugin/marketplace.json` lists one plugin whose `source` is the skill's own folder, so nothing is copied. A plugin root that holds `SKILL.md`, with no `skills/` folder and no `skills` key, loads as a single skill. An entry without `plugin.json` is the manifest itself. No `version` is set, so each push reaches users as a new commit.
- **Consequences:** The plugin name is permanent. `claude-plugins.md` later noted the marketplace's `renames` map.

## 2026-09-28: not submitted to Anthropic's directory

- **Status:** accepted
- **Context:** The skill reads a database on the user's Mac.
- **Options:** Submit it: a claude.ai sandbox can't reach the database.
- **Choice and why:** Don't submit it.
- **Consequences:** None.

## 2026-09-30: a returning mistake is counted from the wrong form

- **Status:** accepted
- **Context:** This corrects [2026-09-28: words first, rules only for mistakes that outlive their word](#2026-09-28-words-first-rules-only-for-mistakes-that-outlive-their-word). The since-added columns of `count` and `terms` count the entry's own phrase, so they show the word in use, not the mistake returning. A prompt audit found this by reading `scripts/wispr.py`.
- **Options:** None considered.
- **Choice and why:** Count the wrong form in pasted text from the day the word was added.
- **Consequences:** None.

## 2026-09-30: global options go before the command

- **Status:** accepted
- **Context:** The script's top-level parser owns `--backup-dir` and `--keep-backups`.
- **Options:** None considered.
- **Choice and why:** Put `--backup-dir` and `--keep-backups` before the command. The full-history count uses no window, not `--since 26w`.
- **Consequences:** None.
