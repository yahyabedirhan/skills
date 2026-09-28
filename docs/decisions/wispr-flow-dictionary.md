# Decisions: wispr-flow-dictionary

The decisions behind the `wispr-flow-dictionary` skill (named `wispr-flow` until 2026-09-28). This file is for maintaining it and is never installed. Add an entry for each new decision: the date, what was decided, and why.

## 2026-09-28

- **The skill writes to Wispr Flow's SQLite database directly.** The app has no CLI or public API for its dictionary. A first batch of 56 entries written this way, with the app running, appeared after a restart and worked in dictation.
- **One script owns the database.** `scripts/wispr.py` holds the table and column names, the timestamp format, and the personal dictionary id, so an app update is fixed in one file. `status` checks the columns it relies on before anything is written.
- **Every write backs up the dictionary and records a batch.** New rows in one `dict add` share a `createdAt`, which `dict undo` uses to revert the batch.
- **Deletes are soft** (`isDeleted = 1`), matching what the app does, so a sync sees a deletion rather than a row that vanished.
- **Counts come from the script.** The report's numbers are `count` output, not the agent's estimate, so two runs over the same window agree.
- **Unknown: whether a sync can drop entries written this way.** Revisit if entries go missing.
- **Large windows go through a file, and `terms` comes first.** A day of dictation is about 30k tokens, past what one read takes, so `history --out` writes the window for paging. `terms` pulls the name-like and command-like words into one table, so names are reviewed without reading every sentence; the full read stays because mishearings that land on ordinary lowercase words ("verb tree") never look like names.
- **Words first, rules only for mistakes that outlive their word.** The user prefers plain dictionary words; a rule is proposed when a mistake comes back after its word was added, which `count` and `terms` now show as hits since the entry was added. This reverses the first version's rule-heavy default, whose 26 rules were replaced by words the same day.
- **`history --diff` shows only the formatter's vocabulary swaps.** Deleted fillers, inserted grammar words, list markup, digits, and hyphenation are dropped, which takes 48 hours from about 285 KB to 14 KB. It catches mishearings the formatter fixed or caused, not the ones it left alone, so the full read stays.
- **`dict remove` matches the exact spelling first.** Matching any case would delete `Claude` along with a duplicate `claude`.

## 2026-09-28 (rename)

- **Renamed `wispr-flow` to `wispr-flow-dictionary`.** Two other published skills are named `wispr-flow` (artemxtech, cathrynlavery), so the old name clashed on skills.sh and in an installer's skills folder. The new name keeps "wispr flow" for search and says what the skill owns. `wispr-flow-analyzer` was rejected because it reads as glebis's `wispr-analytics`, which covers analytics.
- **The skill owns the dictionary loop; analytics stay out.** Usage stats, recaps and wellbeing reflection are covered by other skills (glebis `wispr-analytics`, cathrynlavery and artemxtech `wispr-flow`). A recap of what the user worked on, if wanted, becomes a separate skill.
- **Fixes the user reports mid-task are applied in the same turn**, after a whole-history count shows whether the wrong form is also meant literally. Idea from glebis `wispr-fix`, which queues them instead; with `--restart` a queue isn't needed.
- **Writes can quit and relaunch the app (`--restart`).** glebis's skills refuse to write while the app runs; writing live worked here but the app only loads changes on launch, so restarting in the same command saves the user a step. The app bundle nests a helper app with the same executable name, so quitting targets the main bundle id `com.electron.wispr-flow`, and the running check skips paths under `Resources/`.
- **Backups keep the newest 30** of those the script made.
- **Snippet candidates are links, emails and sentences of 8+ words repeated in 2+ dictations.** Idea from glebis `wispr-analytics` `propose`.
