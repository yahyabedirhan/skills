# Decisions: system-design

The decisions behind the `system-design` skill. This file is for maintaining the skill and is never installed. Read it before changing the skill, and add an entry for each new decision: the date, what was decided, and why. When a decision is reversed, keep the old entry and add a new one that says so.

## 2026-09-25

- **The skill is the delivery framework.** `SKILL.md` carries the framework's stages (requirements, core entities, API, optional data flow, high-level design, deep dives) itself, rather than pointing at a reference for them. The framework standardizes how a design is laid out, so every session reads the same way.
- **The user states the session's purpose.** New design, explaining an existing system, redesigning, and deciding one thing are examples, not a menu; a session can mix them. With no instructions inside a project, the skill writes down that project's design. When the purpose is unclear, it asks what to do with the design, whether the system exists, and whether only an explanation is wanted.
- **Deep dives depend on the purpose.** For a new design or a redesign they present trade-offs as options for the user to pick; when explaining a system that won't change, they become a bonus section on each concept, why it matters for this design, and the trade-off it made.
- **Sessions are iterative.** A new design is drafted end to end, and feedback on one part is carried through every part it affects; a redesign explains the current system first, then shows the before and after.
- **References are concept-level, one file per lesson.** They hold what a concept is, why it matters, its trade-offs, and when to choose which kind of technology, in the skill's own words. A specific technology's internals are left to the agent's research when a design adopts it. Adding a newly transcribed lesson means adding one file (see the skill's `MAINTAINING.md`).
- **Citations go at the end.** Each document reads as the material itself and ends with a Source line citing the Hello Interview lesson.
- **The skill describes its own rules for showing and asking.** It was first meant to share `low-level-design`'s presenting rules by reference, but those rules are mostly specific to code layout and the cross-skill link broke when that skill changed. Each skill now describes its own; `system-design` mentions `low-level-design` only to route code-level design there.
- **Installed globally.** The skill is general-purpose, so it installs into the global scope rather than into a project.
