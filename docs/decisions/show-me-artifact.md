# Decisions: show-me-artifact

The decisions behind the `show-me-artifact` skill. This file is for maintaining it and is never installed. Entries follow the shape in [index.md](index.md).

## 2026-10-01: a new skill on top of show-me, which stays unchanged

- **Status:** accepted
- **Context:** The skill came from a session report, "While You Were Away", that the maintainer read away from the terminal. It had a progress meter and checkpoint list, a tree of where each item stood, comparison tables and twelve decision cards.
- **Options:** Extend `show-me`: it is a fork kept close to humanlayer/skills, and its views are plain text that reads the same in a terminal, an editor or on GitHub.
- **Choice and why:** A hosted page is a different output with its own steps, so it lives in its own skill. The skill loads `/show-me` for the principles instead of restating them.
- **Consequences:** `show-me` stays close to upstream.

## 2026-10-01: named show-me-artifact

- **Status:** accepted
- **Context:** The skill needs a name.
- **Options:** `decision-page`: the skill covers reports with no decisions too.
- **Choice and why:** `show-me-artifact` says it is `show-me` with an artifact as the output, and it sorts beside `show-me` in a listing.
- **Consequences:** None.

## 2026-10-01: model-invoked

- **Status:** accepted
- **Context:** An orchestrator or a long-running session publishes its report without the user typing the name.
- **Options:** None considered.
- **Choice and why:** Keep a description, so the model can load the skill.
- **Consequences:** `/orchestrating` doesn't name it yet. That can follow once it has been used.

## 2026-10-01: the decision card is the core pattern

- **Status:** accepted
- **Context:** The reader must decide without opening a file.
- **Options:** None considered.
- **Choice and why:** Each card holds what is being decided, why it matters, the evidence as the smallest visual, the options and a marked recommendation. Cards get short ids, so an answer fits on one line.
- **Consequences:** None.

## 2026-10-01: a data file and a generator, described but not shipped

- **Status:** accepted
- **Context:** The original page was rebuilt from `data.json` by `build.py` and republished to the same URL seven times.
- **Options:** Ship a shared generator: each report's shape differs, so it would be upkeep with little reuse.
- **Choice and why:** The skill says what the pair does and lets each run write its own.
- **Consequences:** Each run writes its own generator.

## 2026-10-01: theming, phone width and the page contract stay in artifact-design

- **Status:** accepted
- **Context:** The page rules already live in `artifact-design`.
- **Options:** Restate them here: they would drift.
- **Choice and why:** The skill says to load `artifact-design` before writing the generator, so every rebuild carries those rules.
- **Consequences:** None.

## 2026-10-01: the data file lives in .scratch/, not the scratchpad

- **Status:** accepted
- **Context:** A later session must rebuild and republish to the same URL, which it does by reading the page first. The scratchpad is deleted with the session. A fresh audit caught this.
- **Options:** The scratchpad: the data would be lost.
- **Choice and why:** Keep the data file in `.scratch/`.
- **Consequences:** None.

## 2026-10-01: answers come in chat or as page comments, with no answer form

- **Status:** accepted
- **Context:** A page that collects answers itself needs the artifact runtime capabilities, which the source session didn't use.
- **Options:** An answer form on the page.
- **Choice and why:** Answers come in chat or as page comments.
- **Consequences:** Add a form if answering through chat turns out to be the bottleneck.

## 2026-10-01: Claude only, with a fallback

- **Status:** accepted
- **Context:** Only Claude's harness has the `Artifact` tool.
- **Options:** None considered.
- **Choice and why:** The skill has no `agents/openai.yaml` and no plugin entry. Without the tool, it falls back to `/show-me`'s local HTML file.
- **Consequences:** Other harnesses get the local file.
