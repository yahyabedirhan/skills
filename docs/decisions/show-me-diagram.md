# Decisions: show-me-diagram

The decisions behind the `show-me-diagram` skill. This file is for maintaining it and is never installed. Entries follow the shape in [index.md](index.md).

## 2026-10-12: a pointer to diagram-design, sibling to show-me

- **Status:** accepted
- **Context:** The maintainer wants one entry point to say "explain this, show the status or a concept, using diagram-design".
- **Options:** Extend `show-me`: it is a fork kept close to humanlayer/skills, and its views are plain text. Restate `diagram-design`'s rules: they would drift from upstream.
- **Choice and why:** A new skill that loads `diagram-design`, names the profile and picks the type. The build rules stay in `diagram-design`.
- **Consequences:** `show-me` stays close to upstream. The skill needs `diagram-design` installed, which the workstation repo's install list does.

## 2026-10-12: the profiles ship with the skill

- **Status:** accepted
- **Context:** The maintainer's Cursor Dark profile first lived in his workstation repo, copied by hand to `$HOME/.diagram-design/profiles/`.
- **Options:** Keep them in the workstation repo: anyone who installs the skill alone gets no profile, and each new machine needs a manual copy.
- **Choice and why:** Keep the profiles in `profiles/` in the skill, with an `index.md` that marks the default and defines the shape. The skill uses the profile the user names, otherwise the default, so adding a profile changes only that folder.
- **Consequences:** The skill reads the profile directly and leaves diagram-design's install and profile library unchanged.

## 2026-10-12: model-invoked, no plugin entry yet

- **Status:** accepted
- **Context:** An agent showing status can pick it from its description, as with `show-me-artifact`.
- **Options:** None considered.
- **Choice and why:** Keep a description, and add no `agents/openai.yaml` or plugin entry.
- **Consequences:** Add a plugin entry once it has been used.
