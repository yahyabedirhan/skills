# Environment layers

Write each instruction, rule or piece of know-how in one place only, so changing it later is a one-place edit. Two questions choose the place. Who needs it: only this user, anyone working on one project, or any agent doing a task? And must it be enforced, or is it guidance? The table runs from enforced to guidance; go down it and use the first row that fits. Elsewhere, point at it only where a reader wouldn't otherwise find it.

| Layer | Holds | Where to write it |
|---|---|---|
| **Permission** | A hard rule: deny, ask, or allow-and-report. | A row in `/set-up-machine`'s rule table, which set-up-machine turns into each harness's native entries and the global instructions' rule line. A project may only add allows. |
| **Global instruction** | The user's personal workflow and Defaults table, and one line per global rule with what to do instead. | The shared global instructions file every harness on the machine reads. |
| **Project `AGENTS.md`** | Anything a teammate needs to work on the project: its tracker, its commands, its conventions, its worktree tool. | The project's `AGENTS.md`, with a `CLAUDE.md` holding `@AGENTS.md` so Claude Code reads the same text. |
| **Skill** | How to do a task, written for any team's tools and tracker: a value that differs between setups becomes a parameter. | A `SKILL.md` in the skills repo, or a local skill in one project. |
| **Skill reference** | Detail only some runs need: a branch, a table, a tool's specifics. | A file beside the `SKILL.md`, reached by a pointer that says when to read it. |

**No memory.** Write what a harness memory would hold into one of the rows above, and keep memory features off: a memory is invisible to every other harness and lives outside any repository.

**Public by default.** The skills repo and most projects are public, so write personal detail only in the global instructions: names, accounts, paths on the user's machine, other projects. In a skill or a public `AGENTS.md`, generalise it or turn it into a parameter.

## Team test

Before settling a change, picture a teammate or contributor with a different setup: another harness, tmux instead of the user's session host, and no global instructions at all. After the change they must still be able to work on any of the user's projects using only that project's instructions and the skills.

A change passes when:

- nothing a teammate needs sits in the global instructions;
- the global instructions hold only personal workflow and explanations of global rules;
- no skill depends on the user's default tool. A skill may name a default tool, but write the default itself in the global instructions, and how to use a tool in that tool's own skill.

Flag every place a change fails the test, and move the failing part to the row of the table that fits it.

### Skill parameters

A skill that needs a value from the environment (a tool, a command, a repo) declares it as a **parameter**:

- **One `## Parameters` section, in `SKILL.md`,** added only to a skill that needs such a value. Give each parameter one entry: a `<kebab-case>` placeholder named after its role in the Defaults table, whose roles `/set-up-machine`'s `global-instructions.md` lists; what the value is; the skill each known value uses; and its **Default**, written as "Default: …". The Default is what the skill does when the value isn't set: its neutral way, or asking the user where a guess would do harm.
- **The section holds only the entries.** The Defaults table itself says how its rows resolve, so the section doesn't repeat it.
- **The body uses the placeholder as a noun** ("make the worktree with `<worktree-tool>`"), and never repeats what a value routes to or its Default: that lives only in `## Parameters`.
- **A skill uses only placeholders its `## Parameters` declares;** anywhere else, plain words ("the session host").
- **A tool's skill is named directly, in a line that routes to it:** "when `<session-host>` is Herdr, use `/handover-to-herdr`; otherwise …". A new tool gets its own line once its skill exists.
- **Another skill is named by its slash command,** such as `/to-tickets`, not in bold. A starting prompt is the exception: it names skills in words, so it works in every harness.

Before any skill uses a new role, add it as a row in the Defaults table through `/set-up-machine`.

### Team-test audit

After a skill change, and whenever the user asks whether the skills pass the team test, run:

```bash
python3 <this skill>/scripts/default_tools.py --skills <skills folder>
```

It lists two kinds of line. Both are tolerated, not blocking, so it always exits 0.

- **A default tool named outside its how-to skill.** The script reads the tools from the tool rows of the Defaults table in the shared global file: `session-host`, `worktree-tool` and `notification-method`. To check other tools, or when there's no table, pass `--tool <name>` once per tool. It skips a tool's how-to skill, which is any skill folder whose name contains the tool's name, and any line that routes to that skill by name.
- **"Defaults table" or "global instructions" anywhere in a skill.** The agent already has those files in context, and without them the mention points at nothing. `/set-up-machine`, `/set-up-project` and this skill are exempt: those files are what they describe.

Report every hit, each judged one of:

- **a default**: the skill picks the tool, or reads the table inline. Rewrite it with a parameter, and move the tool's commands into its how-to skill;
- **a mention**: an example or data (a dictionary word, a fixture), not a choice. Keep it, and say so.
