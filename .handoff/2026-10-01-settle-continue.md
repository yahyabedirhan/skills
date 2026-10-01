# Handoff: settle effort, delivered and waiting on the user

- **Worktree:** `~/.treehouse/skills-22e236/1/skills` (treehouse lease `settle`), branch `settle/settle-session`, pushed and clean.
- **Pull request:** [#117 Add settle-session and rename close-effort to settle-effort](https://github.com/yahyabedirhan/skills/pull/117), open, not yet approved. Its description is the full report: what changed, every decision made alone, the reviews and audits, and the open questions. Saved copy: `.scratch/pr-117/description.md` (gitignored).
- **Spec and ticket:** #109 "Add a settle-session skill and rename close-effort to settle-effort". It stays open until #117 merges (`Closes #109`).
- **Earlier handoff:** `.handoff/2026-10-01-settle.md` started this effort.
- **Decision record:** `docs/decisions/effort-workflow.md`, 2026-10-01 entry. It holds the decisions, the first prompt audit, the `writing-for-agents` review and the second prompt audit, with every finding applied or left.
- **The session that wrote this** can't be reached. Everything it knew is here, in #117 or in the decision record.

## Where it stands

The effort is built and delivered. The branch has five commits after the first handoff:

| Commit | What it does |
|---|---|
| `a1beb89` | Adds `settle-session` and renames `close-effort` to `settle-effort` |
| `e8fbab2` | Fixes from the final `/code-review` |
| `6af1d9c` | `writing-for-agents` review of `settle-effort` |
| `a44e09e` | `writing-for-agents` review of `settle-session` |
| `7c8dfec` | Fixes from the second prompt audit |

The user asked for those reviews after delivery. The prompt audit means `/claude-api`'s `prompt-audit`; `/skill-doctor` is a different thing, an Anthropic-built usage and cost report that only the user can run, and it shouldn't be used for this.

## Waiting on the user

These are in #117's *Follow-ups*:

1. Approve #117.
2. Confirm that dropping the "merged / good to merge" trigger from `settle-effort` is what they want. Its only trigger now is "settle the effort".
3. Decide whether the spec should stay open while its QA tickets are open. Today `settle-effort` closes it.

If the user answers 2 or 3 with a change, make it as its own commit on this branch, record it in the decision record, and update #117's description with `/to-pr` before merging.

## Once the user says go

All of this is the agent's work, not the user's:

1. Merge #117 and check that `main`'s CI passes. Don't use `--delete-branch`.
2. Do #112 "Reinstall the skills after the settle rename, on the Mac and the VPS", through `/maintain-environment`. The old `~/.claude/skills/close-effort` is still installed, and `settle-session` and `settle-effort` aren't yet. Until the reinstall, `/settle-effort` isn't available, so reinstall first, or follow `skills/settle-effort/SKILL.md` from the merged `main` directly. Asking before `ssh` to the VPS is a global rule.
3. Try `settle-session` and `settle-effort` once installed, and report the result.
4. Settle the effort with `/settle-effort`. Besides this worktree and its branch, it must free one leftover: the first implement agent's worktree `~/Developer/yahyabedirhan/skills/.claude/worktrees/agent-a21181278acf0bb7d` and its branch `worktree-agent-a21181278acf0bb7d`. The harness locked it, so `git worktree remove` refused. Its commit `7b613b4` landed on the branch as `a1beb89` by cherry-pick, so the proof is the patch match (`git cherry`) or the merged pull request's head. Unlock it with `git worktree unlock` before removing it.

## Suggested skills

- `settle-effort`, once installed: or read its `SKILL.md` until #112 is done.
- `maintain-environment`: for #112's reinstall.
- `to-pr`: if #117's description changes.
- `orchestrating`: for the Settle phase and being the user's one contact.
