---
name: maintain-environment
description: Change what agents run with - a permission rule, a global or project instruction, or a skill (create, install, update, move, fork, publish, remove, audit, with `npx skills`) - and carry the change to every harness, machine and install. Use when the user wants a rule or instruction added or changed, asks where one belongs, wants a skill created or changed, or asks which skills they use or which name a default tool.
---

# Maintain the environment

The environment is what agents run with: permissions, global instructions, project instructions, and skills. Use this skill to change it; to set up a machine or a project, use `/set-up-machine` or `/set-up-project` instead. Write each change once, at its source, and carry it from there to every harness, machine and install it applies to. Keep harness memory features off, because a memory is invisible to every other harness and lives outside any repository; write what it would hold into one of the layers instead. The skills repo and most projects are public, so write personal detail only in the global instructions: names, accounts, paths on the user's machine, other projects. In a skill or a public `AGENTS.md`, generalise it or make it a parameter.

## Parameters

- `<skills-repo>`: the user's own skills repo on GitHub, as `owner/repo`.
- `<path-to-skills-repo>`: where that repo is cloned.

## Environment layers

Write each instruction, rule or piece of know-how in one place only, so changing it later is a one-place edit. Two questions choose the place. Who needs it: only this user, anyone working on one project, or any agent doing a task? And must it be enforced, or is it guidance? The table runs from enforced to guidance; go down it and use the first row that fits. Elsewhere, point at it only where a reader wouldn't otherwise find it.

| Layer | Holds | Where to write it |
|---|---|---|
| **Permission** | A hard rule: deny, ask, or allow-and-report. | A row in `/set-up-machine`'s rule table, which `/set-up-machine` turns into each harness's native entries and the global instructions' rule line. A project may only add allows. |
| **Global instruction** | The user's personal workflow and environment defaults, and one line per global rule with what to do instead. | The shared global instructions file every harness on the machine reads. |
| **Project `AGENTS.md`** | Anything a teammate needs to work on the project: its tracker, its commands, its conventions, its worktree tool. | The project's `AGENTS.md`, with a `CLAUDE.md` holding `@AGENTS.md` so Claude Code reads the same text. |
| **Skill** | How to do a task, written for any team's tools and tracker: a value that differs between setups becomes a parameter. | A `SKILL.md` in the skills repo, or a local skill in one project. |
| **Skill reference** | Detail only some runs need, such as one branch of the flow or one tool's specifics; anything every run needs stays in `SKILL.md`. | A file beside the `SKILL.md`. The skill's body says when to read it, and its closing `## References` section says in one line what each file covers; scripts get a `## Scripts` section the same way. |

### The "team test"

Before settling a change, picture a teammate or contributor with a different setup: another harness, tmux instead of herdr, and a machine set up with `/set-up-machine` but none of the user's personal workflow. After the change they must still be able to work on any of the user's projects using only that project's instructions, the skills and the roles `/set-up-machine` writes.

A change passes when:

- nothing a teammate needs sits in the global instructions;
- the global instructions hold only the user's personal workflow, their environment defaults, and explanations of global rules;
- no skill depends on the user's default tool. The user's choice of tool sits in their environment defaults, and how to use a tool sits in that tool's own skill.

Flag every place a change fails the test, and move the failing part to the row of the table that fits it.

### Skill parameters

A skill that needs a value from the environment (a tool, a command, a repo) declares it as a **parameter**:

- **One `## Parameters` section, in `SKILL.md`,** added only to a skill that needs such a value, with one short line per parameter: the `<kebab-case>` placeholder named after its role, what it is, and a few examples after "e.g.". For instance: "`<session-host>`: where agent sessions run, e.g. `herdr`, Claude Code Desktop, Codex Desktop."
- **Write what to do when a role has no tool once,** in `/set-up-machine`'s roles table, which `/set-up-machine` copies into the environment defaults on every machine. Never repeat it in a skill, since a copy drifts from the table.
- **Say when to use a tool in the tool's own skill,** in its description ("Use when the project's worktree tool is `treehouse`"), along with anything specific to that tool. No other skill routes to it.
- **In the body, use the placeholder as a noun** ("make the worktree with `<worktree-tool>`"). Anywhere else, use plain words ("the session host").
- **Name another skill by its slash command,** such as `/to-tickets`, not in bold. A starting prompt is the exception: it names skills in words, so it works in every harness.

Before any skill uses a new role, add it to `/set-up-machine`'s roles table, with what it is and what to do when it has no tool.

## Steps

1. Choose the layer the change belongs to, and check it against the team test.
2. Make the change at that layer's source. For any operation on a skill, read `skill-operations.md`.
   - **For an installed skill:** that is its source repo, never an installed copy, which the next `npx skills update` overwrites.
   - **For a local skill:** that is the project.
3. After any skill change, run the team-test audit: grep the skills for the name of each tool in the user's environment defaults, and for "environment defaults". Skip each tool's own skill, and `/set-up-machine`, `/set-up-project` and this skill, which manage the instruction files. Judge each hit:
   - **When it is a default,** the skill picks the tool itself: make it a parameter, and move the tool's commands into the tool's own skill.
   - **When it is a mention,** an example such as a parameter's "e.g.", or data: keep it.
   - **When it names the environment defaults:** remove the mention. An agent that has them loaded already sees them, and one that doesn't is pointed at nothing.
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

When the user asks what a skill costs to run, or how to make it cheaper, follow `efficiency-analysis.md`.

## References

- [skill-operations.md](skill-operations.md): the kinds of skill, and creating, installing, updating, moving, removing, forking, shipping, auditing and publishing them.
- [efficiency-analysis.md](efficiency-analysis.md): measuring what one run of a skill costs, and making the next run cheaper.

## Scripts

- [scripts/session-usage.py](scripts/session-usage.py): token and time use of a session transcript, split at given moments, for the efficiency analysis.
