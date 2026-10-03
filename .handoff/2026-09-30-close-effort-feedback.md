# Handoff: close-effort feedback on PR #66

Continue a discussion with the maintainer about the **close-effort** skill on [PR #66](https://github.com/yahyabedirhan/skills/pull/66) (branch `skills/environment`, this worktree). The maintainer is reviewing #66 one skill at a time, giving feedback and asking for corrections per skill, so the PR thread doesn't grow into a wall of text. close-effort is the first one.

**This is a discussion, not a build.** Don't edit the skill yourself. The previous session started writing without being asked and was stopped. The agreed flow:

1. Discuss the feedback with the maintainer, and ask anything that's unclear. Confirm you understand what kind of skill content they want (below) before moving on.
2. Update the right issue with the agreed feedback. Either a new issue that is part of #49, like #81–#83, or a comment on an existing one; ask which if unsure.
3. Delegate the rewrite to a sub-agent that commits and pushes to `skills/environment`. Every commit and push is its own call.

The previous session ran in the Claude desktop app and can't receive messages. Ask the maintainer directly.

## The maintainer's feedback

- close-effort is thorough and describes the right workflow, but it **over-constrains the how**: about 25 literal git and gh commands inline (`git merge-base --is-ancestor`, `git cherry`, `headRefOid`, `gh pr merge --merge|--squash|--rebase`, `git -C … pull --prune`, `git branch -d`/`-D`, `git push origin --delete`, and so on).
  - An inline command breaks the flow of the explanation.
  - It gives no reason for being used and no alternatives.
  - Nothing verifies it makes sense.
- **Keep in the body:** the outcomes, the maintainer's preferences, the workflow and its order, and the lessons "we lived through together" (the pain points).
- **Move the commands** to an appendix or a reference file inside the skill. Each command there says what it's for, the alternatives, and whether it makes sense. The Herdr commands already live in `skills/handover-to-herdr/closing-an-effort.md`, which is the model to follow.
- **Parameters stay, and why they exist matters.** The effort workflow skills must not be hard-wired to Herdr and Treehouse. Those are the maintainer's *defaults*, declared in their global instructions (the Defaults table: `session-host`, `worktree-tool`, and so on) so that a teammate with other tools can use the same skills (see #59 and `docs/decisions/effort-workflow.md`, 2026-09-29 "name roles, not tools"). Don't collapse the parameters into tool names.
- **But no skill names built from a placeholder**, like `handover-to-<session-host>`. There is only one handover skill, `handover-to-herdr`, and no convention for more has been decided. Write it in plain words that keep the intent, such as "hand over to the default session host" (with Herdr, that's the **handover-to-herdr** skill). #83 already removed the built names on this branch. Check the wording still reads the way the maintainer wants.

## What the previous session proposed (the maintainer agreed with the direction)

The skill has three kinds of content:

- **Keep: outcomes and preferences.**
  - After the maintainer's "go", the agent does everything and hands them nothing to paste.
  - Merge only when checks pass, and when QA is blocking, only after its tickets close. Afterwards, check the merge broke nothing (CI, pinned commit URLs).
  - Read *Things to be aware of* first and route each item.
  - Run the post-merge follow-ups.
  - Carry unfinished work into linked next-effort tickets. QA tickets stay open.
  - Close the tracker.
  - Never move the main checkout, and never commit straight to the default branch.
  - Save what's worth keeping before removing a worktree.
  - Delete only proven-merged work, and treat a refusal as final: a cleanup script, not a variant.
  - Return its own worktree last, from outside it.
  - End with a short report.
- **Keep as one-line lessons:**
  - Squash merges and cherry-picks can't be seen by reachability or `git cherry`; the merged PR's head proves them. The decision record once got this wrong.
  - Removing a worktree deletes its ignored and untracked files.
  - Returning your own worktree kills the session.
- **Move to a reference:** all the literal commands.

Still open, never answered by the maintainer:

- Which ordering constraints are real? The proposal: *Things to be aware of* before any cleanup, saving files before removal, and its own worktree last. Everything else is free.
- Should the cleanup-script fallback stay?

## Where the skill came from

Read these before proposing changes, since the pain points come from them:

- [#21](https://github.com/yahyabedirhan/skills/issues/21), including its three comments: the original request, two other projects' closes ("don't hand the maintainer commands"), the "go" rule, and the decision to make close-effort its own skill.
- #23 (*Things to be aware of*), #20 (QA tickets), #3 (no `rm -rf`, and one call per commit and push), #83.
- Commits `4a37188` and `7fc27ad`.
- `docs/decisions/effort-workflow.md`, under "2026-09-29: closing" and the entries after it.

## State of this worktree

- `skills/close-effort/SKILL.md` has an **uncommitted one-line edit, not made by the previous session**: `("go")` was removed from the frontmatter description. Ask the maintainer whether it's theirs and whether to keep it before committing anything.
- The branch matches `origin/skills/environment` at `9e7be32`. This handoff is its own commit.
- The PR-level context (which issues #66 touches, what's closed, what follows in #89) is in the PR description and [#89](https://github.com/yahyabedirhan/skills/issues/89). Don't repeat it.

## Suggested skills

- **grilling**: when the maintainer's intent is unclear (they invited `/grill-me`).
- **writing-for-agents**: for the shape of the rewritten skill and its reference.
- **orchestrating**: for the question shape, and for delegating the rewrite to a sub-agent.
