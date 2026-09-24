---
name: maintain-skills
description: Create, install, move, update, fork, publish, remove, or audit agent skills across global scope, project scope, and the user's own skills repo, using the `npx skills` CLI. Use when the user wants a skill created, added, removed, forked, changed, moved between scopes, or published, or asks which skills they actually use.
---

# Maintain Skills

A skill is one of two kinds.

- An **installed** skill has one **source**, a GitHub repo (someone else's, or the user's own skills repo), and any number of **installs**: copies the `npx skills` CLI placed in a scope and recorded in that scope's lock file. Every change goes to the source first and reaches the installs through the CLI; an installed copy is overwritten by the next `npx skills update`, so it is never edited by hand.
- A **local** skill is written inside one project and lives only there. No lock file records it and the CLI never touches it; it is edited in place and committed with the project.

Skills are **private by default**: a local skill stays local, and a skill reaches the user's public skills repo only when the user names that skill for publishing.

## Parameters

Resolve these before acting, in this order: the user's request, the agent instructions files (the project's `AGENTS.md` or `CLAUDE.md`, then the user-level ones), then ask.

- `<skills-repo>`: the user's own skills repo on GitHub, as `<owner>/<repo>`.
- `<path-to-skills-repo>`: its local clone.

When the user supplies them by answer, offer to add one line naming both to their user-level agent instructions file, so the next run finds them there.

## Scopes

| Scope | Folder | Lock file | What belongs there |
|---|---|---|---|
| Global | `~/.agents/skills/` | `~/.agents/.skill-lock.json` | Skills the user reaches for in most projects |
| Project, installed | `<project>/.agents/skills/` | `<project>/skills-lock.json`, committed | Niche or stack-specific skills only that project needs |
| Project, local | `<project>/.agents/skills/` | none; the project's git history | Skills written for that project's own work |
| Skills repo | `<path-to-skills-repo>/skills/<name>/` | git history | The source of the user's own general-purpose skills and forks; installed into a scope like any other repo |

A skill moves from project to global once the user wants it in a second project. A niche skill (one cloud vendor, one UI framework) stays in the projects that use it rather than loading in every session.

**Reaching both Claude Code and Codex.** Codex reads `.agents/skills/` in both scopes. Claude Code reads `.claude/skills/`. Check the global link first:

- `~/.claude/skills` is a symlink to `~/.agents/skills`: install globally with `-g -a codex`; Claude Code sees the same folder through the link, and adding `-a claude-code` would make the CLI link the folder into itself.
- Otherwise: install globally with `-g -a codex -a claude-code`.
- Project installs always take `-a claude-code -a codex`; the CLI links `.claude/skills/<name>` to the `.agents/skills/<name>` copy.
- A local skill gets that link by hand (see Create a project skill).

## Operations

Each operation ends with a check: list the scope's folder, confirm `SKILL.md` resolves through `~/.claude/skills` (global) or `.claude/skills` (project), and confirm the lock file names the expected source.

**Create a project skill.** Write it under `<project>/.agents/skills/<name>/SKILL.md`, following the **writing-for-agents** skill when it is installed. Then link it for Claude Code from the project root, and commit the link with the project (the link itself, not a copy of the folder):

```bash
ln -s ../../.agents/skills/<name> .claude/skills/<name>
```

It stays a local skill until the user asks to publish it; then it becomes an installed skill through Add a new skill to the user's repo, and the local folder is replaced by the install.

**Install.** `npx skills add <owner>/<repo> -s <name> -y` plus the scope and agent flags above. `npx skills add <owner>/<repo> -l` lists what a repo offers. For a cross-referencing bundle (skills that name each other, a setup skill others point at), install the whole bundle into one scope, so no pointer dangles.

**Update.** `npx skills update [<name>...]` with `-g` or `-p`. Before updating, diff the installed copy against its source; a difference means someone edited the install, and the update will erase it. Carry the edit to its home first (see Fork, or move a project-specific edit into the project's agent instructions file).

**Move between scopes.** Install into the new scope, confirm, then `npx skills remove -s <name> -y` in the old one (`-g` for global). Diff first, as for Update: a project copy with local edits is a fork waiting to happen, and a global install from upstream drops those edits.

**Remove.** `npx skills remove -s <name> -y`, with `-g` for global. Before removing, grep the other installed skills and the agent instructions files for the name; fix or report every pointer left behind. A skill that belongs to an installed bundle stays unless the user drops the whole bundle.

**Change one of the user's own skills.** Read the repo's decision records for it first (such as `docs/decisions/`), and add a dated entry for each new decision. Edit it in `<path-to-skills-repo>/skills/<name>/`, commit, push, then `npx skills update <name>` in every scope that installs it.

**Add a new skill to the user's repo.** Only when the user names the skill for publishing. Write it under `<path-to-skills-repo>/skills/<name>/SKILL.md` with `name` and `description` frontmatter, add its row to the repo README, commit, push, then install it. The repo is public: nothing in a skill names the user, their accounts, their machine's paths, or any project of theirs; anything user-specific becomes a parameter like the two above.

**Fork someone else's skill.** Copying a skill folder is not a GitHub fork: nothing links the copy to its origin, so the credit is written by hand.

1. Read the upstream licence. MIT, Apache-2.0, and BSD allow copying, changing, and republishing when the licence notice travels with the copy; other licences have their own terms, read them; with no licence the user may use the skill privately but not republish it.
2. Find the upstream commit the copy starts from: the one whose files match the installed copy, or the latest when copying fresh.
3. Copy the folder to `<path-to-skills-repo>/skills/<name>/`. Keep the upstream licence beside it as `LICENSE.<upstream>`. Rename the skill when its behaviour diverges, so the two can be installed side by side.
4. Make the change, and nothing else, so a later diff against upstream shows only the user's intent.
5. In the README row, name the upstream repo, link the commit, name the licence file, and list what changed.
6. Commit, push, remove the upstream install, and install the fork into the same scope.

## Auditing usage

When the user asks which skills they use, count invocations from local transcripts and report per skill: count per agent, last used, and the date each transcript window starts (older transcripts may have been cleaned up). Pair the counts with every installed skill in both scopes, so never-used skills show as zero.

- **Claude Code**: JSONL transcripts under `~/.claude/projects/`. Count `tool_use` blocks named `Skill` (the skill is `input.skill`) and `<command-name>/<name></command-name>` in user messages.
- **Codex**: JSONL transcripts under `~/.codex/sessions/`. Codex reads a skill by opening its file, so count sessions whose tool calls read `skills/<name>/SKILL.md`; editing sessions inflate this count, so say so.

Write the counting script and its output under the project's scratch or temp folder, not the skills repo. Recommend removals from the counts, and leave each removal to the user's call.

## Publishing

Creating the repo and every push publish to the public. Confirm with the user before creating the repo; after that, pushing changes the user asked for is part of the operation. A new repo gets an MIT `LICENSE` in the user's name unless they choose another, and a README with an install line (`npx skills add <skills-repo>`) and a table of skills with an Origin column.
