# Decisions: show-me-diagram

The decisions behind the `show-me-diagram` skill. This file is for maintaining it and is never installed. Entries follow the shape in [index.md](index.md).

## 2026-10-12: a pointer to diagram-design, sibling to show-me

- **Status:** accepted
- **Context:** The maintainer wants one entry point to say "explain this, show the status or a concept, using diagram-design".
- **Options:** Extend `show-me`: it is a fork kept close to humanlayer/skills, and its views are plain text. Restate `diagram-design`'s rules: they would drift from upstream.
- **Choice and why:** A new skill that loads `diagram-design`, names the profile and picks the type. The build rules stay in `diagram-design`.
- **Consequences:** `show-me` stays close to upstream. The skill needs `diagram-design` installed, which the workstation repo's install list does.

## 2026-10-12: the profile path is fixed

- **Status:** accepted
- **Context:** The maintainer uses one profile, Cursor Dark, kept in the workstation repo and copied to `$HOME/.diagram-design/profiles/`.
- **Options:** Ask for a profile each run: one more question with one answer.
- **Choice and why:** Name `$HOME/.diagram-design/profiles/cursor-dark.md`, and fall back to the default with a note when it is missing.
- **Consequences:** A new profile means a change here.

## 2026-10-12: model-invoked, no plugin entry yet

- **Status:** accepted
- **Context:** An agent showing status can pick it from its description, as with `show-me-artifact`.
- **Options:** None considered.
- **Choice and why:** Keep a description, and add no `agents/openai.yaml` or plugin entry.
- **Consequences:** Add a plugin entry once it has been used.
