# Maintaining the low-level-design skill

For whoever extends this skill; an agent running a session never needs it.

`SKILL.md` is the Delivery Framework lesson, distilled, plus how to run it with the user. `references/` holds the other lessons' material, one file per lesson, in the skill's own words, each ending with a Source line that cites its lesson; `SKILL.md` ends with the same for the Introduction and Delivery Framework. The body reads as the material itself, without naming the source. `layout.md` is the exception: it comes from practice, not a lesson, so it has no Source line.

**Adding a newly transcribed lesson** means adding one reference:

1. Write `references/<lesson-slug>.md` from the lesson: what each idea is, when it applies, and what it costs, with a small example where the idea needs one.
2. Add a row for it to the table in `SKILL.md`'s "Principles, concepts and patterns" section.
3. When the lesson deepens a topic an existing reference touches, point the existing reference at the new one instead of repeating it.

Problem walkthroughs (design a parking lot) are examples of the framework, not concepts; add them only when the user asks.
