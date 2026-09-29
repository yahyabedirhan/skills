# The shared global instructions file

`~/.config/agents/AGENTS.md` is the one global instructions file every harness on the machine reads. It holds this person's workflow and the explanation of each global rule, and nothing a teammate would need: that goes in the project's `AGENTS.md` or a skill (**maintain-environment**'s `where-things-go.md` has the layers and the team test).

## Its shape

set-up-machine owns the shape; the content outside the generated block is the user's. In order:

1. **The rule line**, at the top: "Only what describes this person's own workflow and explains a global rule. Anything a teammate would need goes in the project or a skill."
2. **`## Defaults`**: a table, one row per role, naming this person's tool for it.
3. **The generated block** between the `set-up-machine:rules` markers: one line per rule-table row, with its reason and instruction. Rewritten from the table on every apply.
4. **`## Personal workflow`**: how this person works, one rule per line.

A new file gets all four, every role `none` and the workflow section empty. On an existing file, reconcile only **adds** what the shape lacks (the rule line, the section, a missing role row as `none`) and regenerates the block; it never rewrites a value or a workflow line. Every addition shows in the plan's diff.

## The Defaults roles

A skill names a role as a placeholder of the same name (`<session-host>`) in its `## Parameters` section, with what it does when the role is unset; the row here says which tool this person uses. Changing a tool is one row here plus that tool's how-to skill, never an edit to every skill. A session host's how-to skill is named `handover-to-<session-host>`; a worktree tool's is named for the tool.

| Role | Names | With `none` |
|---|---|---|
| `session-host` | where new agent sessions open: a terminal multiplexer or agent host | the skill works in the same session, or prints a prompt to paste |
| `worktree-tool` | how a new worktree is made | `git worktree add` |
| `notification-method` | how to reach this person when a skill says to notify: a command, or the harness's own tool | the harness's notification tool, else a line in the chat |
| `agent-to-start` | the command and flags that start a new agent session | the skill's own: the current harness's command, or `claude` |
| `skills-repo` | this person's own skills repo, as `<owner>/<repo>` | the skill asks |
| `path-to-skills-repo` | where that repo is cloned | the skill asks |

A value is a tool name or the exact command, with a short why when the choice isn't obvious (a notification command that works around the harness's own tool). A project's `AGENTS.md` may hold its own Defaults table, and its rows override these for that project: a project that names its worktree tool uses it.

## Personal workflow

A line belongs here only when it's about this person, not the work: how they like reports, what they approve and what they leave to the agent, what stays out of public repositories. It passes the team test when a teammate with no global instructions loses nothing they need. A line that fails goes to its layer:

- a teammate needs it on this project → the project's `AGENTS.md`;
- it's how to do a task → the skill for that task, neutral about tools;
- it's how to use one tool → that tool's skill;
- a skill or a rule-table row already carries it → drop it.

## Moving a harness's file

When a harness still keeps its own global file (`~/.claude/CLAUDE.md` with more than the import line, or an old `~/.codex/AGENTS.md`), move it line by line, before the harness's file becomes a link or a single import:

1. For each line, decide its home by the list above: a Defaults row, a personal workflow line, a skill, a project's `AGENTS.md`, or dropped because a skill or rule already carries it. Name the skill or project.
2. Write the Defaults values and workflow lines into the shared file; make each skill edit at its source, as **maintain-environment** says.
3. Leave the harness's file holding only its link to the shared file. The plan reports any other line there as `extra` until it's gone.

Done when every line of the old file has a named home.

## Memory

Memory stays off in every harness: a memory is invisible to the other harnesses and lives outside any repository, so what one would hold goes into a layer above. Each adapter turns its harness's memory feature off, and each plan lists every memory file on the machine as `removed`; apply keeps a copy in the backup folder. Before approving, move any memory worth keeping into its layer.
