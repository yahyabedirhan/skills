# Where things go

Every instruction, rule or piece of know-how has one home, chosen by who needs it and how hard it must hold. Pick the first layer that fits, write it there once, and point at it from anywhere else.

| Layer | Holds | Home |
|---|---|---|
| **Permission** | A hard rule: deny, ask, or allow-and-report. | A row in **set-up-machine**'s rule table, which generates each harness's native entries and the global instructions' rule line. A project may only add allows. |
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
