# Decisions: 3d-model-design

This page records the decisions behind the [`3d-model-design`](../../skills/3d-model-design/SKILL.md) skill.
It is for maintaining the skill and is never installed.
Entries follow the shape in [index.md](index.md).

## Maintaining

`SKILL.md` holds the delivery framework, the session purposes and the lessons, because every run needs them.
`references/` holds what only some stages or flows need, one topic per file.
Add a lesson to `SKILL.md` > 'Lessons' only when a real build found it, with the reason that makes it hold beyond that build.
After each model built with the skill, compare its journal with the skill and fold the new lessons back in.

## 2026-11-24: a delivery framework like the other design skills

- **Status:** accepted
- **Context:** The maintainer asked for a reusable, reproducible way to build 3D models, shaped like `/low-level-design`, `/cli-design` and `/system-design`.
- **Options:** A recipe per subject, such as cars or buildings: it would not reach new subjects.
- **Choice and why:** One framework, Brief → References → Scorecard → Plan → Blockout → Passes → Delivery → Journal, kept in `SKILL.md`, with concept references beside it. The stages are the same for every subject and every mode, so the method stays visible whether the run is interactive or all in.
- **Consequences:** The four starting inputs (images, a reference model, a low-detail model, another model) live in `flows.md` and change only References and Blockout.

## 2026-11-24: cumulative construction, measured at every pass

- **Status:** accepted
- **Context:** The maintainer wants models built bit by bit toward a goal, with measured progress, not generated and retried.
- **Options:** Generate and regenerate whole models: nothing learned survives between attempts.
- **Choice and why:** Each pass names one cause, changes only what it needs and is scored on every view. A plateau, under 1 point across three passes, stops the run for diagnosis.
- **Consequences:** Runs are long. Checkpoints after every pass keep them followable without extra reporting.

## 2026-11-24: score against solved cameras, with check views

- **Status:** accepted
- **Context:** The station wagon reached overall 79.8 against orthographic captures, but its perspective views still showed ripples and a stray mirror block that no score view saw.
- **Options:** Score only fixed orthographic views: it overfits them. Score with a semantic similarity alone: it rewards looking similar in kind, not being right.
- **Choice and why:** Solve every reference's camera, score shape, materials and lines from score views, and keep check views the score never tunes on. Add a craft checklist against a quality benchmark, because closeness and detail are different questions.
- **Consequences:** Every reference needs a camera solve before it can count.

## 2026-11-24: free tools by default

- **Status:** accepted
- **Context:** The maintainer allows free tools, such as Blender, `blender-mcp`, fSpy and OpenCV, and public references captured with their browser, but no paid APIs by default.
- **Options:** Paid image-to-3D services: they cost money and lose the scale and repetition that architecture needs.
- **Choice and why:** `toolkit.md` lists only free tools, and asks before any paid one.
- **Consequences:** Generated meshes come only from local models and serve only as blockouts.
