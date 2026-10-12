# Decisions: show-me-diagram

The decisions behind the `show-me-diagram` skill. This file is for maintaining it and is never installed. Entries follow the shape in [index.md](index.md).

## 2026-10-12: a pointer to diagram-design, sibling to show-me

- **Status:** accepted
- **Context:** The maintainer wants one entry point to say "explain this, show the status or a concept, using diagram-design".
- **Options:** Extend `show-me`: it is a fork kept close to humanlayer/skills, and its views are plain text. Restate `diagram-design`'s rules: they would drift from upstream.
- **Choice and why:** A new skill that loads `diagram-design`, names the profile and picks the type. The build rules stay in `diagram-design`.
- **Consequences:** `show-me` stays close to upstream. The skill needs `diagram-design` installed, which the workstation repo's install list does.

## 2026-10-12: the profile comes from the profiles index

- **Status:** accepted
- **Context:** The maintainer keeps his profiles in the workstation repo, with an `index.md` that marks the default, copied to `$HOME/.diagram-design/profiles/`.
- **Options:** Name one profile file: a new default or a second profile would mean a change here.
- **Choice and why:** Use the profile the user names, otherwise the default the index lists, so adding a profile changes only the index.
- **Consequences:** None.

## 2026-10-12: model-invoked, no plugin entry yet

- **Status:** accepted
- **Context:** An agent showing status can pick it from its description, as with `show-me-artifact`.
- **Options:** None considered.
- **Choice and why:** Keep a description, and add no `agents/openai.yaml` or plugin entry.
- **Consequences:** Add a plugin entry once it has been used.
