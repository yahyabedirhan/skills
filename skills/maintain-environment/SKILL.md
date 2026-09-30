---
name: maintain-environment
description: Change what agents run with - a permission rule, a global or project instruction, or a skill (create, install, update, move, fork, publish, remove, audit, with `npx skills`) - and carry the change to every harness, machine and install. Use when the user wants a rule or instruction added or changed, asks where one belongs, wants a skill created or changed, or asks which skills they use or which name a default tool.
---

# Maintain the environment

The environment is what agents run with: permissions, global instructions, project instructions, and skills. Use this skill to change it; to set up a machine or a project, use `/set-up-machine` or `/set-up-project` instead. Write each change once, at its source, and carry it from there to every harness, machine and install it applies to. Keep harness memory features off, because a memory is invisible to every other harness and lives outside any repository; write what it would hold into one of the layers instead. The skills repo and most projects are public, so write personal detail only in the global instructions: names, accounts, paths on the user's machine, other projects. In a skill or a public `AGENTS.md`, generalise it or make it a parameter.

## Parameters

- `<skills-repo>`: the user's own skills repo on GitHub, as `owner/repo`.
- `<path-to-skills-repo>`: where that repo is cloned.

## Steps

1. Choose the layer the change belongs to, and check it against the team test.
2. Make the change at that layer's source. For a skill, that is its source repo or, for a local skill, the project; never an installed copy, which the next `npx skills update` overwrites.
3. After any skill change, run the team-test audit and judge each hit.
4. Ship a change to the skills repo on a branch, through a pull request opened with `/to-pr`, and stop once it is open. The user merges it or asks you to.
5. Carry the change everywhere it applies, as the table below says. `npx skills` installs from the default branch, so the installs and updates run after the merge, in the session told the pull request merged.
6. Report each step this session can't carry: which set-up skill or `npx skills update` still has to run, and whether it runs on this machine, on each other machine or in each project.

| Change | How it reaches everywhere |
|---|---|
| A permission | Ship the `/set-up-machine` rule-table row; after the merge, update the installed skills and rerun `/set-up-machine` on each machine. |
| A global instruction | Rerun `/set-up-machine` on each machine; every harness reads the one shared file. |
| A project instruction or project permission | Commit it in the project. For a standard every project shares, change `/set-up-project` instead and rerun it in each project. |
| A skill in a source repo | Ship it; after the merge, `npx skills update <name>` in every scope that installs it, on every machine. |
| A local skill | Commit it with the project. |
| A set-up skill itself | Treat it as a skill change first, then rerun that set-up skill wherever it applies. |

## References

- [environment-layers.md](environment-layers.md): read to choose a layer, to apply the team test, to give a skill a parameter, or to run the team-test audit, whether after a change or when the user asks which skills name a default tool.
- [skill-operations.md](skill-operations.md): read to create, install, update, move, remove, fork or publish a skill, for shipping to the skills repo, and when the user asks which skills they use.
- [efficiency-analysis.md](efficiency-analysis.md): read only when the user asks what a run of a skill costs or how to make it cheaper, usually after a new skill's first real run.
