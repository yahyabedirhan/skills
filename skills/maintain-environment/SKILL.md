---
name: maintain-environment
description: Change what agents run with - a permission rule, a global or project instruction, or a skill (create, install, update, move, fork, publish, remove, audit, with `npx skills`) - and carry the change to every harness, machine and install. Use when the user wants a rule or instruction added or changed, asks where one belongs, wants a skill created or changed, asks which skills they use or which name a default tool, or wants a workstation repo for their personal setup.
---

# Maintain the environment

The environment is what agents run with: permissions, global instructions, project instructions and skills. This skill is the starting point for a change to it. Choose the source the change belongs in, then follow that source's own guide. To set up a machine or a project, use `/set-up-machine` or `/set-up-project` instead.

- **Write each change once, at its source,** so changing it later is a one-place edit.
- **Keep personal detail out of public files.** The skills repo and most projects are public. Names, accounts, paths on the user's machine and other projects go only in the workstation repo, or in the shared global instructions file on a machine without one. In a skill or a public `AGENTS.md`, generalise the detail or make it a parameter.
- **Keep harness memory features off.** A memory is invisible to every other harness and lives outside any repository. Write what it would hold into a source instead.

## Parameters

- `<skills-repo>`: the user's own skills repo on GitHub, as `owner/repo`.
- `<path-to-skills-repo>`: where that repo is cloned.
- `<workstation-repo>`: the user's own repo for their personal agent setup, usually private, as `owner/repo`.
- `<path-to-workstation-repo>`: where that repo is cloned, e.g. `~/code/agent-setup`.

## Where a change goes

Two questions choose the source. Who needs it: only this user, anyone on one project, or any agent doing a task? Must it be enforced, or is it guidance? The table runs from enforced to guidance. Go down it and use the first row that fits.

| Change | Source | Guide |
|---|---|---|
| A rule for anybody: deny, ask or allow-and-report | `/set-up-machine`'s `rules.json`, in `<skills-repo>` | `<path-to-skills-repo>/docs/design/set-up-machine.md`, also for any other change to `/set-up-machine` |
| Anything only this user wants: a working-agreement or workflow line, a tool for a role, a personal permission, a harness default, a plugin, what every machine installs | `<workstation-repo>`, in its clone at `<path-to-workstation-repo>` | that repo's `DESIGN.md`: copy the shape of the files it names |
| What a teammate needs on one project | the project's `AGENTS.md`, with `CLAUDE.md` holding `@AGENTS.md`; a project may only add allows | the project's `AGENTS.md` |
| How to do a task, for any team's tools | a skill in `<skills-repo>`, or a local skill in one project | `<path-to-skills-repo>/docs/design/<skill>.md` when it exists, and [references/skill-operations.md](references/skill-operations.md) |

- **When the detail is only for some runs of a skill:** put it in a reference beside the `SKILL.md`. The body says when to read it, and a closing `## References` line says what it covers.
- **When the user has no workstation repo:** write a personal instruction in the shared file itself. A personal permission has no home there, so offer to start a workstation repo, as [references/workstation.md](references/workstation.md) says.
- **When this machine has no pointer** (`~/.config/agents/source.md`): run `/set-up-machine` first, which writes it.
- **When the user asks to improve their workflow:** read `<path-to-workstation-repo>/AGENTS.md` and the documents it names, such as their principles. Name each principle the change conflicts with before you make it.

**The team test.** Picture a teammate with another harness, another session host, and a machine set up with `/set-up-machine` but none of the user's personal workflow. After the change, they must still work on any of the user's projects with only the project's instructions, the skills and the roles `/set-up-machine` writes. So nothing a teammate needs sits in the global instructions, and no skill depends on the user's default tool. A value that differs between setups becomes a `<kebab-case>` parameter in the skill, and a new role goes in `/set-up-machine`'s roles table first. Move each part that fails to the row that fits.

## Steps

1. Choose the row, and check the change against the team test.
2. Make the change at its source, following its guide. Write every instruction and skill with `/writing-for-agents`. Change an installed skill in its source repo, never in an installed copy, since the next `npx skills update` overwrites it.
3. When the change touches the global instructions, show the user the whole shared file as it will read, with each changed line marked. Wait for their approval before it is committed or shipped, since these lines shape every agent.
4. After a skill change, run the team-test audit. Grep the skills for each tool in the user's environment defaults, and for "environment defaults". Skip each tool's own skill, the two set-up skills and this one.
   - **When a skill picks the tool itself:** make it a parameter, and move the tool's commands into the tool's own skill.
   - **When it is an example or data:** keep it.
   - **When it names the environment defaults:** remove the mention.
5. Ship a skills-repo change on a branch, through a pull request opened with `/to-pr`, and stop. The user merges it or asks you to.
6. Carry the change everywhere, as the table below says. `npx skills` installs from the default branch, so installs and updates run after the merge.
7. Report each step this session can't carry, and whether it runs on this machine, on each other machine or in each project.

| Change | How it reaches everywhere |
|---|---|
| A rule for anybody, or a set-up skill | After the merge, `npx skills update`, then rerun `/set-up-machine` on each machine, or `/set-up-project` in each project. |
| A personal change | The user commits and pushes it. Each machine pulls it and reruns `/set-up-machine`. |
| A global instruction with no workstation repo | Rerun `/set-up-machine` on each machine. |
| A project instruction or permission | Commit it in the project. For a standard every project shares, change `/set-up-project` and rerun it in each project. |
| A skill in a source repo | After the merge, `npx skills update <name>` in every scope that installs it, on every machine. A machine whose workstation repo lists it also gets it from `/set-up-machine`. |
| A local skill | Commit it with the project. |

When the user asks what a skill costs to run, follow [references/efficiency-analysis.md](references/efficiency-analysis.md).

## References

- [references/skill-operations.md](references/skill-operations.md): the kinds of skill, and creating, installing, updating, moving, removing, forking, shipping, auditing and publishing them.
- [references/efficiency-analysis.md](references/efficiency-analysis.md): measuring what one run of a skill costs, and making the next run cheaper.
- [references/workstation.md](references/workstation.md): what a workstation repo is for, and how to start one.

## Scripts

- [scripts/session-usage.py](scripts/session-usage.py): token and time use of a session transcript, split at given moments, for the efficiency analysis.
