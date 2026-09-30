# Decisions: low-level-design

The decisions behind the `low-level-design` skill. This file is for maintaining the skill and is never installed. Read it before changing the skill, and add an entry for each new decision: the date, what was decided, and why. When a decision is reversed, keep the old entry and add a new one that says so.

## Maintaining

`SKILL.md` is the Delivery Framework lesson, distilled, plus how to run it with the user and how each kind of session runs. `references/` holds the other lessons' material, one file per lesson, in the skill's own words, each ending with a Source line that cites its lesson; `SKILL.md` ends with the same for the Introduction and Delivery Framework. Write the body as the material itself, without naming the source; the Source line carries the citation. `layout.md` and `session-purposes.md` are the exceptions: they come from practice, not a lesson, so they have no Source line.

To add a newly transcribed lesson, add one reference:

1. Write `references/<lesson-slug>.md` from the lesson: what each idea is, when it applies, and what it costs, with a small example where the idea needs one.
2. Add a row for it to the table in `SKILL.md`'s "Principles, concepts and patterns" section.
3. When the lesson deepens a topic an existing reference touches, point the existing reference at the new one instead of repeating it.

Problem walkthroughs (design a parking lot) are examples of the framework, not concepts; add them only when the user asks.

## 2026-09-30

- **The delivery framework stays in `SKILL.md`,** as the Hello Interview lesson lays it out; an audit had moved the stages' detail into `references/delivery-stages.md`, and the maintainer restored it. Only `references/session-purposes.md` holds how each kind of session runs.
- **The maintainer's notes move out of the skill.** `MAINTAINING.md` sat in the skill's folder, where every install copied it; it is now the *Maintaining* section of this file.
- **A new design is described in `SKILL.md` itself;** `references/session-purposes.md` covers only the other purposes. Its new-design section was never read, because the skill sent only the other purposes to it.
- **The session purposes are back in `SKILL.md` too.** `references/session-purposes.md` held how explaining, redesigning and deciding one thing run, 22 lines that repeated the purpose line in `SKILL.md` and that explaining sessions always read. `references/` now holds only the concept lessons. The maintainer asked for it, alongside the same move in `/system-design`.
