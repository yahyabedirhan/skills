# Skill operations

How a skill is created, installed, updated, moved, forked, published, removed and audited, with the `npx skills` CLI. Part of `/maintain-environment`.

A skill is one of two kinds.

- An **installed** skill has one **source**, a GitHub repo that is either someone else's or `<skills-repo>`. It has any number of **installs**: copies the `npx skills` CLI placed in a scope and recorded in that scope's lock file. Make every change at the source and let the CLI carry it to the installs. Never edit an installed copy by hand, because the next `npx skills update` overwrites it.
- A **local** skill is written inside one project and lives only there. No lock file records it and the CLI never touches it, so edit it in place and commit it with the project.

Skills are **private by default**: keep a local skill local, and add a skill to `<skills-repo>` only when the user names that skill for publishing.

## Scopes

| Scope | Folder | Lock file | What belongs there |
|---|---|---|---|
| Global | `~/.agents/skills/` | `~/.agents/.skill-lock.json` | Skills the user reaches for in most projects |
| Project, installed | `<project>/.agents/skills/` | `<project>/skills-lock.json`, committed | Niche or stack-specific skills only that project needs |
| Project, local | `<project>/.agents/skills/` | none; the project's git history | Skills written for that project's own work |
| Skills repo | `<path-to-skills-repo>/skills/<name>/` | git history | The source of the user's own general-purpose skills and forks; installed into a scope like any other repo |

Move a skill from project to global scope once the user wants it in a second project. Keep a niche skill, such as one for a single cloud vendor or UI framework, in the projects that use it, so it doesn't load in every session.

**Reaching both Claude Code and Codex.** Codex reads `.agents/skills/` in both scopes. Claude Code reads `.claude/skills/`. Check the global link first:

- `~/.claude/skills` is a symlink to `~/.agents/skills`: install globally with `-g -a codex`; Claude Code sees the same folder through the link, and adding `-a claude-code` would make the CLI link the folder into itself.
- Otherwise: install globally with `-g -a codex -a claude-code`.
- Project installs always take `-a claude-code -a codex`; the CLI links `.claude/skills/<name>` to the `.agents/skills/<name>` copy.
- A local skill gets that link by hand (see Create a project skill).

## Operations

End each operation that changes an install with a check: list the scope's folder, confirm `SKILL.md` resolves through `~/.claude/skills` (global) or `.claude/skills` (project), and confirm the lock file names the expected source.

**Create a project skill.** Write it under `<project>/.agents/skills/<name>/SKILL.md`, following `/writing-for-agents` when it is installed. Then link it for Claude Code from the project root, and commit the link with the project (the link itself, not a copy of the folder):

```bash
ln -s ../../.agents/skills/<name> .claude/skills/<name>
```

Keep it local until the user asks to publish it. Then publish it through *Add a new skill to the user's repo*, and replace the local folder with the install.

**Install.** `npx skills add <owner>/<repo> -s <name> -y` plus the scope and agent flags above. `npx skills add <owner>/<repo> -l` lists what a repo offers. For a cross-referencing bundle (skills that name each other, a setup skill others point at), install the whole bundle into one scope, so no pointer dangles.

**Update.** `npx skills update [<name>...]` with `-g` or `-p`. Before updating, diff the installed copy against its source; a difference means someone edited the install, and the update will erase it. Save the edit before updating: fork the skill (see *Fork someone else's skill*), or move a project-specific edit into the project's `AGENTS.md`.

**Move between scopes.** Install into the new scope, confirm, then `npx skills remove -s <name> -y` in the old one (`-g` for global). Diff first, as for Update: a global install from upstream drops any local edits in the project copy, so fork the skill or move those edits into the project first.

**Remove.** `npx skills remove -s <name> -y`, with `-g` for global. Before removing, grep the other installed skills and the agent instructions files for the name; fix or report every pointer left behind. A skill that belongs to an installed bundle stays unless the user drops the whole bundle.

**Change one of the user's own skills.** First read the repo's decision records for it, such as those in `docs/decisions/`. Then, on a branch (see *Shipping to the skills repo*), edit it in `<path-to-skills-repo>/skills/<name>/`, add a dated decision entry for each new decision, and ship it; after the merge, `npx skills update <name>` in every scope that installs it.

**Add a new skill to the user's repo.** Only when the user names the skill for publishing. On a branch (see Shipping to the skills repo), write it under `<path-to-skills-repo>/skills/<name>/SKILL.md` with `name` and `description` frontmatter, add its row to the repo README, and ship it; install it after the merge. Because the repo is public, keep the user's name, accounts, machine paths and projects out of the skill, and make anything user-specific a parameter, as `where-things-go.md` sets out.

**Fork someone else's skill.** Copying a skill folder is not a GitHub fork: nothing links the copy to its origin, so write the credit by hand.

1. Read the upstream licence. MIT, Apache-2.0 and BSD allow copying, changing and republishing when the licence notice travels with the copy. Other licences have their own terms, so read them. With no licence, the user may use the skill privately but not republish it.
2. Find the upstream commit the copy starts from: the one whose files match the installed copy, or the latest when copying fresh.
3. Branch the skills repo (see Shipping to the skills repo, step 1), then copy the folder to `<path-to-skills-repo>/skills/<name>/`. Keep the upstream licence beside it as `LICENSE.<upstream>`. Rename the skill when its behaviour diverges, so the two can be installed side by side.
4. Make the change, and nothing else, so a later diff against upstream shows only the user's intent.
5. In the README row, name the upstream repo, link the commit, name the licence file, and list what changed.
6. Ship it. After the merge, remove the upstream install and install the fork into the same scope.

## Shipping to the skills repo

Every operation that changes `<path-to-skills-repo>` starts on a branch and ends with a pull request into `main`:

1. Before the first edit, branch from an up-to-date `main`: `<skill>/<topic>` for one skill, `skills/<topic>` when the change spans skills.
2. Make the change and commit it on the branch.
3. For a new skill or a fork that changes behaviour, run Auditing a new skill; on the same branch, commit the applied fixes and the audit's full findings (applied, and left with the reason) in the skill's decision record (such as `docs/decisions/<name>.md`).
4. Push the branch and open the pull request through `/to-pr`. For an audited skill, summarise the audit in the description's *Special things to note* and link the decision record that holds the full findings.

Stop once the pull request is open: the user merges it, or asks the agent to. Because `npx skills` installs from the default branch, run installs and updates only after the merge. The session that is told "merged" or "merge it" runs them, in every scope that installs the skill.

## Auditing usage

When the user asks which skills they use, count invocations from local transcripts and report per skill: count per agent, last used, and the date each transcript window starts (older transcripts may have been cleaned up). Pair the counts with every installed skill in both scopes, so never-used skills show as zero.

- **Claude Code**: JSONL transcripts under `~/.claude/projects/`. Count `tool_use` blocks named `Skill` (the skill is `input.skill`) and `<command-name>/<name></command-name>` in user messages.
- **Codex**: JSONL transcripts under `~/.codex/sessions/`. Codex reads a skill by opening its file, so count sessions whose tool calls read `skills/<name>/SKILL.md`; editing sessions inflate this count, so say so.

Write the counting script and its output under the project's scratch or temp folder, not the skills repo. Recommend removals from the counts, and leave each removal to the user's call.

## Auditing a new skill

After creating a skill (Create a project skill, Add a new skill to the user's repo, or a fork that changes behaviour), dispatch a fresh sub-agent as an objective auditor: the author's context is anchored on what it meant to write, and the auditor reads only what is on disk. Its prompt names the skill folder and tells it to invoke the bundled `/claude-api` skill's `prompt-audit` subcommand on that folder (the audit `/doctor prompt-audit <path>` runs) and to report findings without editing. Review the report, apply the accepted fixes in the skill's own folder, and name what was left and why. Done when every finding is applied or answered.

## Efficiency analysis

Only when the user asks what a skill costs to run (tokens, minutes, plan usage) or how to make it cheaper, follow [efficiency-analysis.md](efficiency-analysis.md).

## Publishing

Creating the repo and every push publish to the public. Confirm with the user before creating the repo; after that, a change the user asked for ships as in Shipping to the skills repo. A new repo gets an MIT `LICENSE` in the user's name unless they choose another, and a README with an install line (`npx skills add <skills-repo>`) and a table of skills with an Origin column.
