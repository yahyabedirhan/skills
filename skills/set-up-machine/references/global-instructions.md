# The shared global instructions file

`~/.config/agents/AGENTS.md` is the one global instructions file every harness on the machine reads. It holds this person's workflow and the explanation of each global rule, and nothing a teammate would need: that goes in the project's `AGENTS.md` or a skill (`/maintain-environment`'s `where-things-go.md` has the layers and the team test).

## Its shape

set-up-machine owns the shape; everything outside the generated block is the user's. In order:

1. `# Global agent instructions`
2. **The rule line:** `Only what describes this person's own workflow and explains a global rule. Anything a teammate would need goes in the project or a skill.`
3. **`## Defaults`**, with the line "The tools this person uses, by role. `none` means the skill's fallback. A project's Defaults table overrides a row.", then a table, `| Role | Default |`, one row per role below.
4. **The generated block**, rewritten from `rules.json` on every run:

   ```markdown
   <!-- set-up-machine:rules start. Generated from set-up-machine's rule table: change the table, not these lines. -->
   ## Global rules

   Every harness on this machine enforces these as far as it can. A harness refuses the whole command when any part of it matches a rule, so run each risky step as its own command, and read a refusal as a refusal of that step only.

   - **Denied:** `rm -rf` and its variants. A recursive forced delete can't be undone, … Instead: Move what's no longer needed into …
   - **Asks first:** `git push --force-with-lease`. It rewrites the remote's history, … Say in one line why …
   - **Allowed and reported:** `gh api`, `gh secret` and `gh variable`. They reach anything … Go ahead; each call is logged …
   <!-- set-up-machine:rules end -->
   ```

   One line per row, in table order: `- **<Denied | Asks first | Allowed and reported>:** <summary>. <reason> <instruction>`, with `Instead: ` before the instruction on deny rows only.
5. **`## Personal workflow`**, with the line `Rules for how this person works that pass the team test. Anything a project or a skill needs goes there instead.`, then this person's rules, one per line.

A new file gets all five, every role `none` and the workflow section empty. On an existing file, only **add** what the shape lacks (the rule line, a section, a missing role row as `none`) and regenerate the block; never rewrite a value or a workflow line. A start marker without its end marker stops the run until the user restores it.

## The Defaults roles

A skill declares a role it uses as a placeholder of the same name (`<session-host>`) in its `## Parameters`; the row here says which tool this person uses.

| Role | Names |
|---|---|
| `session-host` | where new agent sessions open |
| `worktree-tool` | how a new worktree is made |
| `notification-method` | how a skill notifies this person: a command, or the harness's own tool |
| `agent-to-start` | the command and flags that start a new agent session |
| `skills-repo` | this person's own skills repo, as `<owner>/<repo>` |
| `path-to-skills-repo` | where that repo is cloned |

A value is a tool name or the exact command. A project's `AGENTS.md` may hold its own Defaults table, whose rows override these.

## Personal workflow

A line belongs here only when it's about this person, not the work: how they like reports, what they approve and what they leave to the agent, what stays out of public repositories. It passes the team test when a teammate with no global instructions loses nothing they need. A line that fails goes to its layer:

- a teammate needs it on this project → the project's `AGENTS.md`;
- it's how to do a task → the skill for that task, neutral about tools;
- it's how to use one tool → that tool's skill;
- a skill or a rule-table row already carries it → drop it.

## Moving a harness's file

When a harness still keeps its own global file (`~/.claude/CLAUDE.md` with more than the import line, an old `~/.codex/AGENTS.md`), move it line by line before the harness's file becomes a link or a single import:

1. Decide each line's home by the list above: a Defaults row, a personal workflow line, a skill, a project's `AGENTS.md`, or dropped because a skill or rule already carries it. Name the skill or project.
2. Write the Defaults values and workflow lines into the shared file; make each skill edit at its source, as `/maintain-environment` says.
3. Leave the harness's file holding only its link to the shared file.

Done when every line of the old file has a named home.

## Memory

Memory stays off in every harness: a memory is invisible to the other harnesses and lives outside any repository, so what one would hold goes into a layer above. Each harness reference says how to turn its memory off and where its memory files are; every file is `removed` in the diff and backed up first. Before approving, move any memory worth keeping into its layer.
