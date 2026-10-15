# Decisions: system-design

The decisions behind the `system-design` skill. This file is for maintaining the skill and is never installed. Read it before changing the skill. Entries follow the shape in [index.md](index.md).

## Maintaining

`SKILL.md` is the Delivery Framework lesson, distilled, plus how to run it with the user and how to explain or redesign an existing system. `references/` holds the other lessons' material, one file per lesson, in the skill's own words, each ending with a Source line that cites its lesson; `SKILL.md` ends with the same for the Delivery Framework. Write each body as the material itself, without naming the source.

To add a newly transcribed lesson, add one reference:

1. Write `references/<lesson-slug>.md` from the lesson: the concept, why it matters, its trade-offs, and when to choose which kind of technology. Keep the internals of a specific technology out: the agent researches those when a design adopts it.
2. Add a row for it to the table in `SKILL.md`'s "Concepts and technologies" section.
3. When the lesson deepens a topic an existing reference touches (Scaling Reads and the scaling-reads section of `common-patterns.md`), point the existing reference at the new one instead of repeating it.

Problem walkthroughs (Design Uber) are examples of the framework, not concepts; add them only when the user asks.

## 2026-10-14: name /cli-design beside /low-level-design

- **Status:** accepted
- **Context:** `/cli-design` already names `/system-design`. An agent in `/system-design` that reaches a command-line interface had no pointer to the CLI framework.
- **Options:** None considered.
- **Choice and why:** Add one line beside the existing `/low-level-design` pointer: to design a command-line interface's commands, flags, output and help, use `/cli-design`.
- **Consequences:** Each of the three design skills now names the other two.

## 2026-09-25: the skill is the delivery framework

- **Status:** accepted
- **Context:** The skill needs a standard layout for a design, so every session reads the same way.
- **Options:** Point at a reference for the stages.
- **Choice and why:** `SKILL.md` carries the framework's stages itself: requirements, core entities, API, optional data flow, high-level design, deep dives.
- **Consequences:** An audit later moved the detail out, and the maintainer restored it; see [2026-09-30: the delivery framework stays in SKILL.md](#2026-09-30-the-delivery-framework-stays-in-skillmd).

## 2026-09-25: the user states the session's purpose

- **Status:** accepted
- **Context:** Sessions differ: new design, explaining an existing system, redesigning, deciding one thing.
- **Options:** A fixed menu of purposes: a session can mix them.
- **Choice and why:** The purposes are examples, not a menu. When the purpose is unclear, the skill asks what to do with the design, whether the system exists, and whether only an explanation is wanted.
- **Consequences:** None.

## 2026-09-25: with no instructions inside a project, write down its design

- **Status:** replaced by [2026-09-30: with no instructions inside a project, explain its design in the conversation](#2026-09-30-with-no-instructions-inside-a-project-explain-its-design-in-the-conversation)
- **Context:** The skill may load inside a project with no instructions.
- **Options:** None considered.
- **Choice and why:** The skill writes down that project's design.
- **Consequences:** A file is written without the user asking.

## 2026-09-25: deep dives depend on the purpose

- **Status:** accepted
- **Context:** Deep dives serve a new design and an explanation differently.
- **Options:** None considered.
- **Choice and why:** For a new design or a redesign, deep dives present trade-offs as options for the user to pick. When explaining a system that won't change, they become a bonus section on each concept: why it matters for this design, and the trade-off it made.
- **Consequences:** None.

## 2026-09-25: sessions are iterative

- **Status:** accepted
- **Context:** Feedback on one part of a design affects other parts.
- **Options:** None considered.
- **Choice and why:** A new design is drafted end to end, and feedback on one part is carried through every part it affects. A redesign explains the current system first, then shows the before and after.
- **Consequences:** None.

## 2026-09-25: references are concept-level, one file per lesson

- **Status:** accepted
- **Context:** The skill draws on many Hello Interview lessons.
- **Options:** Cover each technology's internals: the agent researches those when a design adopts it.
- **Choice and why:** A reference holds what a concept is, why it matters, its trade-offs, and when to choose which kind of technology, in the skill's own words.
- **Consequences:** Adding a newly transcribed lesson means adding one file, as the *Maintaining* section says.

## 2026-09-25: citations go at the end

- **Status:** accepted
- **Context:** The material comes from Hello Interview lessons.
- **Options:** None considered.
- **Choice and why:** Each document reads as the material itself, and ends with a Source line that cites its lesson.
- **Consequences:** None.

## 2026-09-25: the skill describes its own rules for showing and asking

- **Status:** accepted
- **Context:** The skill was first meant to share `low-level-design`'s presenting rules by reference.
- **Options:** Share the rules: they are mostly specific to code layout, and the cross-skill link broke when that skill changed.
- **Choice and why:** Each skill describes its own rules. `system-design` mentions `low-level-design` only to route code-level design there.
- **Consequences:** None.

## 2026-09-25: installed globally

- **Status:** accepted
- **Context:** The skill is general-purpose.
- **Options:** Install per project.
- **Choice and why:** Install into the global scope.
- **Consequences:** None.

## 2026-09-30: the stages' detail moves to a reference

- **Status:** replaced by [2026-09-30: the delivery framework stays in SKILL.md](#2026-09-30-the-delivery-framework-stays-in-skillmd)
- **Context:** The stages' detail crowded the flow in `SKILL.md`.
- **Options:** None considered.
- **Choice and why:** `SKILL.md` keeps the delivery framework as its flow, one short step per stage. `delivery-framework.md` beside it holds what each stage covers and how to show it. `existing-systems.md` holds how to explain or redesign a system from evidence.
- **Consequences:** `/low-level-design` got the same shape, with `references/delivery-stages.md` and `references/session-purposes.md`.

## 2026-09-30: the delivery framework stays in SKILL.md

- **Status:** accepted
- **Context:** This replaces [2026-09-30: the stages' detail moves to a reference](#2026-09-30-the-stages-detail-moves-to-a-reference). An audit had moved the stages' detail into `delivery-framework.md`.
- **Options:** Keep the reference: the framework is the skill's content on purpose, as the Hello Interview lesson lays it out.
- **Choice and why:** The maintainer restored the stages to `SKILL.md`.
- **Consequences:** `existing-systems.md` stayed a reference until [2026-09-30: explaining and redesigning an existing system are in SKILL.md](#2026-09-30-explaining-and-redesigning-an-existing-system-are-in-skillmd). `/low-level-design` is the same: its stages are back in `SKILL.md`, and `references/delivery-stages.md` is gone.

## 2026-09-30: the maintainer's notes move out of the skill

- **Status:** accepted
- **Context:** `MAINTAINING.md` sat in the skill's folder, where every install copied it.
- **Options:** None considered.
- **Choice and why:** The notes are now the *Maintaining* section of this file. Notes for whoever extends a skill belong with its decisions, not with the skill.
- **Consequences:** Installs no longer carry the notes.

## 2026-09-30: with no instructions inside a project, explain its design in the conversation

- **Status:** accepted
- **Context:** This replaces [2026-09-25: with no instructions inside a project, write down its design](#2026-09-25-with-no-instructions-inside-a-project-write-down-its-design).
- **Options:** None considered.
- **Choice and why:** The skill explains the project's design in the conversation. The design is written somewhere only when the user asks.
- **Consequences:** None.

## 2026-09-30: explaining and redesigning an existing system are in SKILL.md

- **Status:** accepted
- **Context:** `existing-systems.md` sat beside `SKILL.md`, outside `references/`, and repeated its two purpose lines at more length.
- **Options:** None considered.
- **Choice and why:** Its content is now the detail under those lines in `SKILL.md`. The maintainer asked for it.
- **Consequences:** `references/` holds only the concept lessons.
