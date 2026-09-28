# Decisions: wispr-flow

The decisions behind the `wispr-flow` skill. This file is for maintaining it and is never installed. Add an entry for each new decision: the date, what was decided, and why.

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
