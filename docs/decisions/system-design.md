# Decisions: system-design

The decisions behind the `system-design` skill. This file is for maintaining the skill and is never installed. Read it before changing the skill, and add an entry for each new decision: the date, what was decided, and why. When a decision is reversed, keep the old entry and add a new one that says so.

## Maintaining

`SKILL.md` is the Delivery Framework lesson, distilled, plus how to run it with the user. `existing-systems.md`, beside it, holds how to explain or redesign a system from evidence. `references/` holds the other lessons' material, one file per lesson, in the skill's own words, each ending with a Source line that cites its lesson; `SKILL.md` ends with the same for the Delivery Framework. Write each body as the material itself, without naming the source.

To add a newly transcribed lesson, add one reference:

1. Write `references/<lesson-slug>.md` from the lesson: the concept, why it matters, its trade-offs, and when to choose which kind of technology. Keep the internals of a specific technology out: the agent researches those when a design adopts it.
2. Add a row for it to the table in `SKILL.md`'s "Concepts and technologies" section.
3. When the lesson deepens a topic an existing reference touches (Scaling Reads and the scaling-reads section of `common-patterns.md`), point the existing reference at the new one instead of repeating it.

Problem walkthroughs (Design Uber) are examples of the framework, not concepts; add them only when the user asks.

## 2026-09-25

- **The skill is the delivery framework.** `SKILL.md` carries the framework's stages (requirements, core entities, API, optional data flow, high-level design, deep dives) itself, rather than pointing at a reference for them. The framework standardizes how a design is laid out, so every session reads the same way.
- **The user states the session's purpose.** New design, explaining an existing system, redesigning, and deciding one thing are examples, not a menu; a session can mix them. With no instructions inside a project, the skill writes down that project's design. When the purpose is unclear, it asks what to do with the design, whether the system exists, and whether only an explanation is wanted.
- **Deep dives depend on the purpose.** For a new design or a redesign they present trade-offs as options for the user to pick; when explaining a system that won't change, they become a bonus section on each concept, why it matters for this design, and the trade-off it made.
- **Sessions are iterative.** A new design is drafted end to end, and feedback on one part is carried through every part it affects; a redesign explains the current system first, then shows the before and after.
- **References are concept-level, one file per lesson.** They hold what a concept is, why it matters, its trade-offs, and when to choose which kind of technology, in the skill's own words. A specific technology's internals are left to the agent's research when a design adopts it. Adding a newly transcribed lesson means adding one file (see the skill's `MAINTAINING.md`).
- **Citations go at the end.** Each document reads as the material itself and ends with a Source line citing the Hello Interview lesson.
- **The skill describes its own rules for showing and asking.** It was first meant to share `low-level-design`'s presenting rules by reference, but those rules are mostly specific to code layout and the cross-skill link broke when that skill changed. Each skill now describes its own; `system-design` mentions `low-level-design` only to route code-level design there.
- **Installed globally.** The skill is general-purpose, so it installs into the global scope rather than into a project.
- **2026-09-30: the stages' detail moves to a reference.** `SKILL.md` keeps the delivery framework as its flow, one short step per stage, and `delivery-framework.md` beside it holds what each stage covers and how to show it; `existing-systems.md` holds how to explain or redesign a system from evidence. This supersedes the entry above that `SKILL.md` carries the stages itself: it still does, as steps, but the detail no longer crowds the flow. `/low-level-design` got the same shape, with `references/delivery-stages.md` and `references/session-purposes.md`.
- **2026-09-30: the delivery framework stays in `SKILL.md`.** An audit had moved the stages' detail into `delivery-framework.md`; the maintainer restored it, since the framework is the skill's content on purpose, as the Hello Interview lesson lays it out. Only `existing-systems.md` stays a reference. `/low-level-design` is the same: its stages are back in `SKILL.md`, and `references/delivery-stages.md` is gone.
- **2026-09-30: the maintainer's notes move out of the skill.** `MAINTAINING.md` sat in the skill's folder, where every install copied it; it is now the *Maintaining* section of this file, since notes for whoever extends a skill belong with its decisions, not with the skill.
