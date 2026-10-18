# Decisions: show-me-diagram

The decisions behind the `show-me-diagram` skill. This file is for maintaining it and is never installed. Read it before changing the skill. Entries follow the shape in [index.md](index.md).

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

## 2026-10-12: a profile is one choice per layer

- **Status:** accepted
- **Context:** A profile copied as a full upstream style guide was 246 lines, mostly restated upstream rules. Another project of the maintainer's had the same problem with styles and replaced them with layers, each with options, and presets that pick one option per layer.
- **Options:** Full upstream style guides: long, and they drift from upstream.
- **Choice and why:** A profile picks one option per layer, from what the diagram is to how it looks: diagram types, diagram style, look, palette, typography. It names upstream types, variants and roles, and leaves the rest to upstream defaults. The shape lives only in `profiles/index.md`.
- **Consequences:** Profiles are short and comparable. Cursor Dark is the default; Navy Blue, Shipyard Green and Parchment ship beside it.

## 2026-10-12: model-invoked, no plugin entry yet

- **Status:** accepted
- **Context:** An agent showing status can pick it from its description, as with `show-me-artifact`.
- **Options:** None considered.
- **Choice and why:** Keep a description, and add no `agents/openai.yaml` or plugin entry.
- **Consequences:** Add a plugin entry once it has been used.

## 2026-10-12: a Graphite profile in the logos' origami look

- **Status:** accepted
- **Context:** Diagrams should match the look of the project logos: folded white paper on a dark granite tile.
- **Options:** Re-skin Cursor Dark: its serif title and orange accent don't match the logos.
- **Choice and why:** A new profile, Graphite. It takes the logos' grey palette and the tile's gradient and double rim. White replaces the orange accent. Only the focal nodes and arrows fold, so the folds keep the accent's role. The fonts are geometric sans faces with no serif, to match the crisp folds.
- **Consequences:** The profile adds three roles that upstream lacks: `shade` for the folded faces, `fold-muted` for secondary text on a folded node, and `line` for node outlines. A first build of three diagrams showed the gaps. Two rules came from it: the diagram itself is the tile, and label masks take the tile's gradient.
