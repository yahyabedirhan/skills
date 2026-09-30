# Skill operations

Creating, installing, updating, moving, removing, forking, publishing and auditing skills with the `npx skills` CLI.

## Kinds of skill

A skill is one of three kinds:

| Kind | Folder | Lock file | What belongs there |
|---|---|---|---|
| Global, installed | `~/.agents/skills/` | `~/.agents/.skill-lock.json` | Skills the user reaches for in most projects |
| Project, installed | `<project>/.agents/skills/` | `<project>/skills-lock.json`, committed | Niche or stack-specific skills only that project needs |
| Project, local | `<project>/.agents/skills/` | none; the project's git history | Skills written for that project's own work |

An **installed** skill is a copy the CLI made from its **source**: a GitHub repo that is either someone else's or `<skills-repo>`, whose skills are written in `<path-to-skills-repo>/skills/<name>/`. Make every change at the source, never in an installed copy, because the next `npx skills update` overwrites it.

A **local** skill has no source and no lock file, so edit it in place and commit it with the project.

Keep a skill local until the user names it for publishing to `<skills-repo>`. Move a skill to global once the user wants it in a second project; keep a niche one, such as for a single cloud vendor, in the projects that use it, so it doesn't load in every session.

## Reaching Claude Code and Codex

Codex reads `.agents/skills/`; Claude Code reads `.claude/skills/`.

- When `~/.claude/skills` is a symlink to `~/.agents/skills`, install globally with `-g -a codex` only: adding `-a claude-code` makes the CLI link the folder into itself.
- Otherwise install globally with `-g -a codex -a claude-code`.
- Install into a project with `-a claude-code -a codex`, which links `.claude/skills/<name>` to the `.agents/skills/<name>` copy. Link a local skill the same way by hand.

After every change to an install, check that the skill's `SKILL.md` resolves through the Claude Code folder and that the lock file names the expected source.

## Operations

**Create a project skill.** Write it under `<project>/.agents/skills/<name>/`, following `/writing-for-agents`. Link it for Claude Code, and commit the link, not a copy of the folder:

```bash
ln -s ../../.agents/skills/<name> .claude/skills/<name>
```

**Install.** `npx skills add <owner>/<repo> -s <name> -y`, with the flags above. Install a bundle of skills that name each other into one scope, so no pointer dangles.

**Update.** First diff each installed copy against its source: a difference is a hand edit the update would erase. Keep it by forking the skill, or by moving a project-specific edit into the project's `AGENTS.md`.

**Move between scopes.** Diff as for Update, install into the new scope, then remove the old install.

**Remove.** Grep the other skills and the instructions files for the name first, and fix or report each pointer left behind. Keep a skill that belongs to an installed bundle unless the user drops the whole bundle.

**Change one of the user's own skills.** Read the repo's decision records for it first. Edit it in the skills repo, add a dated decision entry for each new decision, and ship it.

**Add a skill to the user's repo.** Write it in the skills repo, add its row to the README, and ship it.

**Fork someone else's skill.** Copying a folder keeps no link to its origin, so record the credit by hand:

1. Check the upstream licence allows republishing; without a licence, the user may use the skill privately but not republish it.
2. Find the upstream commit the copy starts from.
3. Copy the folder into the skills repo on a branch, with the upstream licence beside it as `LICENSE.<upstream>`. Rename the skill once its behaviour diverges, so both can be installed.
4. Make only the intended change, so a diff against upstream shows just that.
5. In the README row, name the upstream repo, the commit, the licence file and what changed.
6. Ship it, then replace the upstream install with the fork in the same scope.

## Shipping to the skills repo

1. Branch from an up-to-date default branch: `<skill>/<topic>` for one skill, `skills/<topic>` for several.
2. For a new skill or a fork that changes behaviour, audit it as below, and commit the fixes and the full findings to its decision record.
3. In the pull request for an audited skill, summarise the audit in the description's notes for reviewers and link the decision record.

## Auditing a new skill

After creating or forking a skill, have a fresh sub-agent audit it, because the author reads what it meant to write and the auditor reads only what is on disk. Tell it to run `/claude-api`'s `prompt-audit` on the skill folder and report without editing. Apply the fixes you accept, and say why each other finding was left.

## Auditing usage

When the user asks which skills they use, count invocations in local transcripts. Report per skill the count per agent and the last use, list installed skills with no use as zero, and give the date each transcript window starts, since older transcripts may be gone.

- **Claude Code**: `~/.claude/projects/`. Count `Skill` tool calls by `input.skill`, and `<command-name>/<name></command-name>` in user messages.
- **Codex**: `~/.codex/sessions/`. Codex loads a skill by reading its `SKILL.md`, so count sessions that read it, and say that editing sessions inflate the count.

Keep the counting script and its output out of the skills repo. Recommend removals, and leave each one to the user.

## Publishing the skills repo

Creating the repo and every push publish to the public, so confirm with the user before creating it. Give a new repo an MIT `LICENSE` in the user's name unless they choose another, and a README with an install line and a table of skills with an Origin column.
