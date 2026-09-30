# Where things go

Every instruction, rule or piece of know-how has one home, chosen by who needs it and how hard it must hold. Pick the first layer that fits, write it there once, and point at it from anywhere else.

| Layer | Holds | Home |
|---|---|---|
| **Permission** | A hard rule: deny, ask, or allow-and-report. | A row in `/set-up-machine`'s rule table, which set-up-machine turns into each harness's native entries and the global instructions' rule line. A project may only add allows. |
| **Global instruction** | The user's personal workflow and Defaults table, and one line per global rule with what to do instead. | The shared global instructions file every harness on the machine reads. |
| **Project `AGENTS.md`** | Anything a teammate needs to work on the project: its tracker, its commands, its conventions, its worktree tool. | The project's `AGENTS.md`, with a `CLAUDE.md` holding `@AGENTS.md` so Claude Code reads the same text. |
| **Skill** | How to do a task. Neutral about tools, team size and issue tracker: it names a role ("the project's worktree tool") and says what to do when none is named. | A `SKILL.md` in the skills repo, or a local skill in one project. |
| **Skill reference** | Detail only some runs need: a branch, a table, a tool's specifics. | A file beside the `SKILL.md`, reached by a pointer that says when to read it. |

**No memory.** A harness memory is invisible to every other harness and lives outside any repository. What a memory would hold goes into one of the layers above; memory features stay off.

**Public by default.** The skills repo and most projects are public. Personal detail (names, accounts, paths on the user's machine, other projects) lives only in the global instructions; a skill or public `AGENTS.md` generalises it or turns it into a parameter.

## The team test

Before settling a change, check it against a teammate or contributor with a different setup: another harness, tmux instead of the user's session host, no global instructions at all. They can work on any of the user's projects using only that project's instructions and the skills.

A change passes when:

- nothing a teammate needs sits in the global instructions;
- the global instructions hold only personal workflow and explanations of global rules;
- no skill depends on the user's default tool. A skill that names a default tool is tolerated, but the default itself belongs in the global instructions, and how to use a tool belongs in that tool's own skill.

Flag every place a change fails the test, and move the failing part to its layer.

### How a skill names an environment value

A skill that needs a value from the environment (a tool, a command, a repo) declares it as a **parameter**:

- **One `## Parameters` section, in `SKILL.md`,** only in a skill that needs such a value: one entry per parameter, a `<kebab-case>` placeholder named after its Defaults role (`/set-up-machine`'s `global-instructions.md` lists them), what it is, the skill each known value uses, and its **Default**, written as "Default: …": what the skill does when the value isn't set (its neutral way, or asking where a guess does harm).
- **The section holds only the entries.** The Defaults table itself says how its rows resolve, so the section doesn't repeat it.
- **The body uses the placeholder as a noun** ("make the worktree with `<worktree-tool>`"), and never repeats what a value routes to or its Default: that lives only in `## Parameters`.
- **A skill uses only placeholders its `## Parameters` declares;** anywhere else, plain words ("the session host").
- **A tool's skill is named directly, in a line that routes to it:** "when `<session-host>` is Herdr, use `/handover-to-herdr`; otherwise …". A new tool gets its own line once its skill exists.
- **Another skill is named by its slash command,** such as `/to-tickets`, not in bold. A starting prompt is the exception: it names skills in words, so it works in every harness.

A new role is a new row in the Defaults table, added through `/set-up-machine`, before any skill uses it.

### Auditing the skills

After a skill change, and whenever the user asks whether the skills pass the team test, run:

```bash
python3 <this skill>/scripts/default_tools.py --skills <skills folder>
```

It lists two kinds of line, and always exits 0: each is tolerated, not blocking.

- **A default tool named outside its how-to skill.** The tools come from the tool rows of the Defaults table (`session-host`, `worktree-tool`, `notification-method`) in the shared global file; pass `--tool <name>` once per tool to check others, or when there's no table. A skill folder whose name contains the tool's name is its how-to skill and is skipped, and so is a line that routes to that skill by name.
- **"Defaults table" or "global instructions" anywhere in a skill.** The agent already has those files in context, and without them the mention points at nothing. `/set-up-machine`, `/set-up-project` and this skill are exempt: those files are what they describe.

Report every hit, each judged one of:

- **a default**: the skill picks the tool, or reads the table inline. Rewrite it with a parameter, and move the tool's commands into its how-to skill;
- **a mention**: an example or data (a dictionary word, a fixture), not a choice. Keep it, and say so.
