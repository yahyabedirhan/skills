# Environment layers

Write each instruction, rule or piece of know-how in one place only, so changing it later is a one-place edit. Two questions choose the place. Who needs it: only this user, anyone working on one project, or any agent doing a task? And must it be enforced, or is it guidance? The table runs from enforced to guidance; go down it and use the first row that fits. Elsewhere, point at it only where a reader wouldn't otherwise find it.

| Layer | Holds | Where to write it |
|---|---|---|
| **Permission** | A hard rule: deny, ask, or allow-and-report. | A row in `/set-up-machine`'s rule table, which set-up-machine turns into each harness's native entries and the global instructions' rule line. A project may only add allows. |
| **Global instruction** | The user's personal workflow and Defaults table, and one line per global rule with what to do instead. | The shared global instructions file every harness on the machine reads. |
| **Project `AGENTS.md`** | Anything a teammate needs to work on the project: its tracker, its commands, its conventions, its worktree tool. | The project's `AGENTS.md`, with a `CLAUDE.md` holding `@AGENTS.md` so Claude Code reads the same text. |
| **Skill** | How to do a task, written for any team's tools and tracker: a value that differs between setups becomes a parameter. | A `SKILL.md` in the skills repo, or a local skill in one project. |
| **Skill reference** | Detail only some runs need: a branch, a table, a tool's specifics. | A file beside the `SKILL.md`, reached by a pointer that says when to read it. |

## Team test

Before settling a change, picture a teammate or contributor with a different setup: another harness, tmux instead of the user's session host, and a machine set up with `/set-up-machine` but none of the user's personal workflow. After the change they must still be able to work on any of the user's projects using only that project's instructions, the skills and the roles `/set-up-machine` writes.

A change passes when:

- nothing a teammate needs sits in the global instructions;
- the global instructions hold only personal workflow and explanations of global rules;
- no skill depends on the user's default tool. The user's choice of tool sits in the global Defaults, and how to use a tool sits in that tool's own skill.

Flag every place a change fails the test, and move the failing part to the row of the table that fits it.

### Skill parameters

A skill that needs a value from the environment (a tool, a command, a repo) declares it as a **parameter**:

- **One `## Parameters` section, in `SKILL.md`,** added only to a skill that needs such a value, with one short line per parameter: the `<kebab-case>` placeholder named after its role, what it is, and a few examples after "e.g.". For instance: "`<session-host>`: where agent sessions run, e.g. Herdr, Claude Code Desktop, Codex Desktop."
- **What to do when a role has no tool is written once,** in the roles table of `/set-up-machine`'s `global-instructions.md`, which that skill copies into the global Defaults on every machine. A skill never repeats it.
- **A tool's own skill says when to use it,** in its description ("Use when the project's worktree tool is Treehouse"), along with anything specific to that tool. No other skill routes to it.
- **The body uses the placeholder as a noun** ("make the worktree with `<worktree-tool>`"). Anywhere else, plain words ("the session host").
- **Another skill is named by its slash command,** such as `/to-tickets`, not in bold. A starting prompt is the exception: it names skills in words, so it works in every harness.

Before any skill uses a new role, add it to `/set-up-machine`'s roles table, with what it is and what to do when it has no tool.

### Team-test audit

Run:

```bash
python3 <this skill>/scripts/default_tools.py --skills <skills folder>
```

It lists two kinds of line. Both are tolerated, not blocking, so it always exits 0.

- **A default tool named outside its how-to skill.** The script reads the tools from the tool rows of the Defaults table in the shared global file: `session-host`, `worktree-tool` and `notification-method`. To check other tools, or when there's no table, pass `--tool <name>` once per tool. It skips a tool's how-to skill, which is any skill folder whose name contains the tool's name, and any line that routes to that skill by name.
- **"Defaults table" or "global instructions" anywhere in a skill.** The agent already has those files in context, and without them the mention points at nothing. `/set-up-machine`, `/set-up-project` and this skill are exempt: those files are what they describe.

Report every hit, each judged one of:

- **a default**: the skill picks the tool, or reads the table inline. Rewrite it with a parameter, and move the tool's commands into its how-to skill;
- **a mention**: an example or data (a dictionary word, a fixture), not a choice. Keep it, and say so.
