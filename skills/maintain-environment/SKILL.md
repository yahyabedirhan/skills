---
name: maintain-environment
description: Change what agents run with - a permission rule, a global or project instruction, or a skill (create, install, update, move, fork, publish, remove, audit, with `npx skills`) - and carry the change to every harness, machine and install. Use when the user wants a rule or instruction added or changed, asks where one belongs, wants a skill created or changed, or asks which skills they use or which name a default tool.
---

# Maintain the environment

The environment is what agents run with: permissions, global instructions, project instructions, and skills. This skill owns change to it. Setting up a machine or a project belongs to **set-up-machine** and **set-up-project**; this skill decides where a change goes, makes it at its source, and carries it everywhere it applies.

## Parameters

Each parameter comes from the user's request, else the Defaults table, where a project's row overrides the global one. It is unset when neither gives it, or its row says `none`.

- `<skills-repo>`: the user's own skills repo on GitHub (`<owner>/<repo>`). Unset, ask the user.
- `<path-to-skills-repo>`: its local clone. Unset, ask the user.

When the user answers one, offer to add it to the Defaults table.

## What's changing?

Read only the references the change needs.

- **A rule, an instruction, or know-how whose home is unsettled**: read [where-things-go.md](where-things-go.md), place it by the layering model and the team test, then edit it at that layer's home.
- **A team-test audit** (which skills name a default tool, after any skill change), or **a skill that needs an environment value**: read the parameter convention and the audit in [where-things-go.md](where-things-go.md).
- **A skill** (create, install, update, move, fork, publish, remove, or an audit of which skills are used, a new skill's prompt, or a run's cost): read [skill-operations.md](skill-operations.md).

## Carry it everywhere

Every change ends by reaching each harness, machine and install it applies to. Read [carrying-a-change.md](carrying-a-change.md) and finish by naming which set-up skill or update still has to run, and where.
