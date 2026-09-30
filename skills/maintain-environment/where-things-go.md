# Where things go

Every instruction, rule or piece of know-how has one home, chosen by who needs it and how hard it must hold. Pick the first layer that fits, write it there once, and point at it from anywhere else.

| Layer | Holds | Home |
|---|---|---|
| **Permission** | A hard rule: deny, ask, or allow-and-report. | A row in **set-up-machine**'s rule table, which set-up-machine turns into each harness's native entries and the global instructions' rule line. A project may only add allows. |
| **Global instruction** | The user's personal workflow (their Defaults: session host, worktree tool, notifications, agent to start, skills repo location), and one line explaining each global deny or ask with what to do instead. | The shared global instructions file every harness on the machine reads. |
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

- **One `## Parameters` section, in `SKILL.md`**, never in a reference, and only in a skill that needs such a value. Its lead sentence says the values come from the Defaults table in the environment's instructions, where a project's table overrides the global one for that project.
- **Each parameter is a `<kebab-case>` placeholder named after its Defaults role** (`<session-host>`, `<worktree-tool>`, `<notification-method>`, `<agent-to-start>`, `<skills-repo>`, `<path-to-skills-repo>`; **set-up-machine**'s `global-instructions.md` lists the roles), with a one-line meaning and its fallback when unset: the skill's own neutral way (this session, `git worktree add`, the harness's tool), or asking, only where a guess does harm.
- **The body and the references use only the placeholder.** A tool's how to is reached through the resolved value: the **handover-to-`<session-host>`** skill, the **`<worktree-tool>`** skill. Other skills are named directly, in bold.

A new role is a new row in that table, added through **set-up-machine**, before any skill uses it.

### Auditing the skills

After a skill change, and whenever the user asks whether the skills pass the team test, run:

```bash
python3 <this skill>/scripts/default_tools.py --skills <skills folder>
```

It lists two kinds of line, and always exits 0: each is tolerated, not blocking.

- **A default tool named outside its how-to skill.** The tools come from the tool rows of the Defaults table (`session-host`, `worktree-tool`, `notification-method`) in the shared global file; pass `--tool <name>` once per tool to check others, or when there's no table. A skill folder whose name contains the tool's name is its how-to skill and is skipped.
- **"Defaults table" or "global instructions" outside a `## Parameters` section**, where a placeholder belongs. **set-up-machine**, **set-up-project** and this skill are exempt: those files are what they describe.

Report every hit, each judged one of:

- **a default**: the skill picks the tool, or reads the table inline. Rewrite it with a parameter, and move the tool's commands into its how-to skill;
- **a mention**: an example or data (a dictionary word, a fixture), not a choice. Keep it, and say so.
