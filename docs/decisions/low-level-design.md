# Decisions: low-level-design

The decisions behind the `low-level-design` skill. This file is for maintaining it and is never installed. Entries follow the shape in [index.md](index.md).

## Maintaining

`SKILL.md` is the Delivery Framework lesson, distilled, plus how to run it with the user and how each kind of session runs. `references/` holds the other lessons' material, one file per lesson, in the skill's own words, each ending with a Source line that cites its lesson; `SKILL.md` ends with the same for the Introduction and Delivery Framework. Write the body as the material itself, without naming the source; the Source line carries the citation. `layout.md` and `session-purposes.md` are the exceptions: they come from practice, not a lesson, so they have no Source line.

To add a newly transcribed lesson, add one reference:

1. Write `references/<lesson-slug>.md` from the lesson: what each idea is, when it applies, and what it costs, with a small example where the idea needs one.
2. Add a row for it to the table in `SKILL.md` > 'Principles, concepts and patterns'.
3. When the lesson deepens a topic an existing reference touches, point the existing reference at the new one instead of repeating it.

Problem walkthroughs (design a parking lot) are examples of the framework, not concepts; add them only when the user asks.

## 2026-10-14: name the other two design skills

- **Status:** accepted
- **Context:** `/cli-design` already names `/low-level-design` and `/system-design`. An agent in `/low-level-design` that reaches a command-line interface had no pointer to the CLI framework, and the skill also never named `/system-design`.
- **Options:** Point only at `/cli-design`: the three skills would still not each name the other two.
- **Choice and why:** Add one routing paragraph that names `/system-design` and `/cli-design`, so each design skill names the other two.
- **Consequences:** None.

## 2026-09-30: the delivery framework stays in SKILL.md

- **Status:** accepted
- **Context:** An audit had moved the stages' detail into `references/delivery-stages.md`.
- **Options:** Keep the stages in a reference: the maintainer wants the framework in the skill, as the Hello Interview lesson lays it out.
- **Choice and why:** The maintainer restored the stages to `SKILL.md`.
- **Consequences:** At the time, only `references/session-purposes.md` held how each kind of session runs. That later moved back too; see [2026-09-30: the session purposes are back in SKILL.md](#2026-09-30-the-session-purposes-are-back-in-skillmd).

## 2026-09-30: the maintainer's notes move out of the skill

- **Status:** accepted
- **Context:** `MAINTAINING.md` sat in the skill's folder, where every install copied it.
- **Options:** None considered.
- **Choice and why:** The notes are now the *Maintaining* section of this file, which is never installed.
- **Consequences:** Installs no longer carry the notes.

## 2026-09-30: a new design is described in SKILL.md itself

- **Status:** replaced by [2026-09-30: the session purposes are back in SKILL.md](#2026-09-30-the-session-purposes-are-back-in-skillmd)
- **Context:** `references/session-purposes.md` had a new-design section that was never read, because the skill sent only the other purposes to it.
- **Options:** None considered.
- **Choice and why:** Describe a new design in `SKILL.md`. `references/session-purposes.md` covers only the other purposes.
- **Consequences:** The other purposes still lived in a reference.

## 2026-09-30: the session purposes are back in SKILL.md

- **Status:** accepted
- **Context:** This replaces [2026-09-30: a new design is described in SKILL.md itself](#2026-09-30-a-new-design-is-described-in-skillmd-itself). `references/session-purposes.md` held how explaining, redesigning and deciding one thing run. Its 22 lines repeated the purpose line in `SKILL.md`, and explaining sessions always read it.
- **Options:** None considered.
- **Choice and why:** Move every session purpose into `SKILL.md`. The maintainer asked for it, alongside the same move in `/system-design`.
- **Consequences:** `references/` now holds only the concept lessons.
