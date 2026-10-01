# Decisions: show-me-artifact

The decisions behind the `show-me-artifact` skill. This file is for maintaining it and is never installed. Add an entry for each new decision: the date, what was decided, and why.

## 2026-10-01

- **A new skill on top of `show-me`, which stays unchanged.** `show-me` is a fork kept close to humanlayer/skills, and its views are plain text that reads the same in a terminal, an editor or on GitHub. Publishing a hosted page is a different output with its own steps, so it lives in its own skill, which loads `/show-me` for the principles instead of restating them. It came from a session report, "While You Were Away", that the maintainer read away from the terminal: a progress meter and checkpoint list, a tree of where each item stood, comparison tables and twelve decision cards.
- **Named `show-me-artifact`.** The name says it is `show-me` with an artifact as the output, and it sorts beside `show-me` in a listing. `decision-page` was the other candidate, but the skill covers reports with no decisions too.
- **Model-invoked.** An orchestrator or a long-running session publishes its report without the user typing the name, so the skill keeps a description. It is not yet named from `/orchestrating`; that can follow once it has been used.
- **The decision card is the core pattern.** Each card holds what is being decided, why it matters, the evidence as the smallest visual, the options and a marked recommendation, so the reader decides without opening a file. Cards get short ids so an answer fits on one line.
- **A data file and a generator when the page changes, described but not shipped.** The original page was rebuilt from `data.json` by `build.py` and republished to the same URL seven times. Each report's shape differs, so a shared generator would be upkeep with little reuse; the skill says what the pair does and lets each run write its own.
- **Theming, phone width and the page contract stay in `artifact-design`.** The skill only says to load it before writing the generator, so every rebuild carries those rules; restating them here would drift.
- **The data file lives in `.scratch/`, not the scratchpad.** The scratchpad is deleted with the session, and a later session must rebuild and republish to the same URL, which it does by reading the page first. A fresh audit caught this.
- **Answers come in chat or as page comments; no answer form.** A page that collects answers itself needs the artifact runtime capabilities, which the source session didn't use; add it if answering through chat turns out to be the bottleneck.
- **Claude only, with a fallback.** Only Claude's harness has the `Artifact` tool, so the skill has no `agents/openai.yaml` and no plugin entry; without the tool it falls back to `/show-me`'s local HTML file.
