# Maintaining the system-design skill

Read this only when extending the skill; a design session never needs it.

`SKILL.md` is the Delivery Framework lesson, distilled, plus how to run it with the user. `references/` holds the other lessons' material, one file per lesson, in the skill's own words, each ending with a Source line that cites its lesson; `SKILL.md` ends with the same for the Delivery Framework. Write each body as the material itself, without naming the source.

To add a newly transcribed lesson, add one reference:

1. Write `references/<lesson-slug>.md` from the lesson: the concept, why it matters, its trade-offs, and when to choose which kind of technology. Keep the internals of a specific technology out: the agent researches those when a design adopts it.
2. Add a row for it to the table in `SKILL.md`'s "Concepts and technologies" section.
3. When the lesson deepens a topic an existing reference touches (Scaling Reads and the scaling-reads section of `common-patterns.md`), point the existing reference at the new one instead of repeating it.

Problem walkthroughs (Design Uber) are examples of the framework, not concepts; add them only when the user asks.
