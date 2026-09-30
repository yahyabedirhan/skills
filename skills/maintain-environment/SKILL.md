---
name: maintain-environment
description: Change what agents run with - a permission rule, a global or project instruction, or a skill (create, install, update, move, fork, publish, remove, audit, with `npx skills`) - and carry the change to every harness, machine and install. Use when the user wants a rule or instruction added or changed, asks where one belongs, wants a skill created or changed, or asks which skills they use or which name a default tool.
---

# Maintain the environment

The environment is what agents run with: permissions, global instructions, project instructions, and skills. Use this skill to change it: decide where the change goes, make it at its source, and carry it everywhere it applies. To set up a machine or a project, use `/set-up-machine` or `/set-up-project` instead.

## Parameters

- `<skills-repo>`: the user's own skills repo on GitHub (`<owner>/<repo>`). Default: ask the user.
- `<path-to-skills-repo>`: its local clone. Default: ask the user.

## What's changing?

Read only the references the change needs.

- **A rule, an instruction, or know-how when it isn't clear which file it goes in**: read [environment-layers.md](environment-layers.md), choose the file with its table and the team test, then edit it there.
- **A team-test audit** (which skills name a default tool, after any skill change), or **a skill that needs an environment value**: read *Skill parameters* and *Team-test audit* in [environment-layers.md](environment-layers.md).
- **A skill** (create, install, update, move, fork, publish, remove, or an audit of which skills are used, a new skill's prompt, or a run's cost): read [skill-operations.md](skill-operations.md).

## Carry it everywhere

Carry every change to each harness, machine and install it applies to: read [change-propagation.md](change-propagation.md), and finish by naming which set-up skill or update still has to run, and where.
