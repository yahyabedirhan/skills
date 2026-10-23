# Design: maintain-environment

This page explains how [`maintain-environment`](../../skills/maintain-environment/SKILL.md) is built, for whoever changes it.
A newcomer needs two facts first:

- It is the **starting point** for any change to what agents run with.
It decides which source the change belongs in, then hands over to that source's own guide.
It repeats nothing the source already says.
- It owns only what no other place owns: the layer choice, the team test, personal against public, and operations on skills.

## Requirements

1. **Route.** For a change, name its layer and its source: a permission, a global instruction, a project instruction, a skill, or a skill reference.
2. **Guard.** Apply the team test, keep personal detail out of public files, and keep memory features off.
3. **Hand over.** After the change, say what carries it everywhere: apply `setup/` on each machine, `npx skills update`, or rerun set-up-project.
4. **Skills.** Create, install, update, move, fork, publish, remove and audit skills.
5. **Stay small.** A change to the workstation layout or to set-up-machine needs no edit here.
6. **Out of scope:** the workstation repo's layout and file shapes, which its `DESIGN.md` covers; the format of `setup/` files, which set-up-machine's `references/workstation.md` covers; how a harness is set up, which set-up-machine covers; and how a project is set up, which set-up-project covers.

## Entities and relationships

- **Layer**: permission, global instruction, project `AGENTS.md`, skill, skill reference.
- **Source**: where a layer is written: the rule table, the workstation repo, a project, the skills repo.
- **Guide**: the document that says how to write in a source: the workstation repo's `DESIGN.md`, a skill's design in `docs/design/`, a project's `AGENTS.md`.

```text
maintain-environment ──picks──▶ layer ──names──▶ source ──whose guide is──▶ DESIGN.md | docs/design/<skill>.md | AGENTS.md
maintain-environment ──says what reruns──▶ set-up-machine | npx skills update | set-up-project
```

## Class design

```text
skills/maintain-environment/
├── SKILL.md                     # layers table, team test, the routing steps, how a change reaches everywhere
├── references/
│   ├── skill-operations.md      # every operation on a skill
│   ├── efficiency-analysis.md   # what one run of a skill costs
│   └── workstation.md           # starting a workstation repo; after that its DESIGN.md is the guide
└── scripts/
    └── session-usage.py         # token and time use of a transcript, for the efficiency analysis
```

## Implementation (traced)

**"Add Exa to Codex":**

```text
maintain-environment
  layer      personal: a plugin only this user wants on a harness → workstation repo
  guide      read the workstation repo's DESIGN.md; copy the shape of the files it names
  write      the files DESIGN.md's Extensibility table lists for that change
  hand over  apply setup/ on each machine
```

**"Never let an agent run `git push --force`":**

```text
maintain-environment
  layer      a rule for anybody → set-up-machine's rules.json
  guide      read docs/design/set-up-machine.md in the skills repo
  write      one row with samples; ship it as a pull request
  hand over  after the merge: npx skills update, then apply setup/ on each machine
```

## Extensibility

| Change | What you touch |
|---|---|
| A new kind of personal file | the workstation repo's `DESIGN.md`; nothing here |
| A new harness | set-up-machine; nothing here |
| A new layer | the layers table and the team test in `SKILL.md` |
| A new skill operation | `references/skill-operations.md` |
