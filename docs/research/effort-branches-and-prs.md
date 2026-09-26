# Effort branches and pull requests

> Moved from the job-search vault's `.scratch/skill-improvements/research/` on 2026-09-26. Paths under `tmp/`, `~/.claude/` and the vault point at the user's machine and are not in this repo. The VPS host, user and machine ID are redacted.

How an effort's branch and pull request are started, continued, stacked and delivered with git, GitHub, `gh` and treehouse, as input for skill-improvement issues [#3](https://github.com/yahyabedirhan/skills/issues/3), [#6](https://github.com/yahyabedirhan/skills/issues/6), [#14](https://github.com/yahyabedirhan/skills/issues/14) and [#15](https://github.com/yahyabedirhan/skills/issues/15). Researched 2026-09-25.

Legend: **[doc]** stated by the cited primary source; **[tested]** reproduced in a throwaway repo under `tmp/effort-branches/lab/` (no remote); **[observed]** read from the real shipyard or vault repos with read-only commands; **[unverified]** inferred, not tested.

## 1. Treehouse worktrees

**What it is.** Treehouse (`github.com/kunchenguid/treehouse`) keeps a pool of reusable, pre-warmed git worktrees per repository under `~/.treehouse/` so parallel agents each get an isolated checkout. No daemon; pool state is a locked file. [doc: [README, How It Works](https://github.com/kunchenguid/treehouse#how-it-works)]

**Version gap.** The installed binary is v2.3.0 (`treehouse --version`; `treehouse status` offers v3.0.0). v3.0.0 was released 2026-09-25 and adds `get -b/--branch`, `get --base`, `treehouse lease <name>`, `return <name>` and `return --all`, and changes `return` to exit 3 on a dirty abort. [doc: [CHANGELOG 3.0.0](https://github.com/kunchenguid/treehouse/blob/main/CHANGELOG.md)] Everything below marked v3 is absent from the local `--help`.

**How `get` creates a worktree.** It fetches origin, then reuses an idle, unleased, clean slot whose HEAD is merged into the reset target, or creates a new one. The result is a **detached HEAD** at whichever of local or remote default branch is further ahead. [doc: README, How It Works]

**Leases.** `treehouse get --lease [--lease-holder <label>] [--json]` reserves the slot durably and prints only its path. A leased slot is never handed out by a later `get`, never pruned, and never removed by `destroy --all`; only `destroy <exact path> --include-leased --yes` removes it. [doc: `treehouse get --help`; README, Leasing a worktree] `--no-fetch` skips the fetch. v3 adds `treehouse lease <name>` to lease an existing slot in place without touching its files. [doc: README]

**Returning.** `treehouse return <path>` terminates lingering processes, verifies none remain, resets the slot, clears the lease and returns it to the pool. A dirty non-interactive return aborts (v3: exit 3) unless `--force`. `--if-lease-id` / `--if-lease-holder` make it conditional. The branch the slot had checked out is **not deleted**: return detaches and resets. [doc: `treehouse return --help`; README, Base branch and Returning everything at once]

**Getting a worktree for an existing remote branch.** Treehouse has no "check out an existing branch" option; v3 `-b` creates a new branch and fails if it already exists. [doc: README, Flags] So the pattern is lease, then let git switch:

```bash
path=$(treehouse get --lease --lease-holder <effort>)     # detached at default branch, origin fetched
git -C "$path" switch <branch>                             # DWIM: creates <branch> tracking origin/<branch>
```

`git switch <branch>` with the default `--guess` behaves as `git switch -c <branch> --track <remote>/<branch>` when only a remote branch of that name exists. [doc: [git-switch --guess](https://git-scm.com/docs/git-switch#Documentation/git-switch.txt---guess)] It refuses if the branch is already checked out in another worktree of the same clone ("already used by worktree at ..."). [tested] This matches the shipyard Mac worktree: slot 1, leased by `shipyard-macos`, on `build/shipyard-core-0.0.x` tracking `origin/build/shipyard-core-0.0.x`. [observed: `git worktree list`, `treehouse status`, `git config branch.<b>.merge`] With v3, `treehouse get --lease --base <effort-branch>` would cut the slot at the further-ahead of `<b>` and `origin/<b>` (base takes a branch name, never `origin/<b>`) and fails closed if it resolves to neither. [doc: README, Base branch] [unverified locally: v3 not installed]

**Stacked branch with treehouse.** Today: `get --lease`, then `git -C "$path" switch --no-track -c <new-branch> origin/<effort-branch>`. v3: `treehouse get --lease --base <effort-branch> -b <new-branch>`. [doc: README; unverified locally] Note that a slot acquired with `--base` is parked back on that base when returned, and prune/destroy accept a clean slot merged into its recorded explicit base. [doc: README, Base branch]

## 2. Taking over a branch safely

**Same machine.** A branch can be checked out in only one worktree of a clone; `git worktree add` and `git switch` refuse otherwise unless forced. [doc: [git-worktree --force](https://git-scm.com/docs/git-worktree#Documentation/git-worktree.txt---force); tested] Reuse the existing worktree (`treehouse enter <name>` opens it even if in use, without changing pool state [doc: `treehouse enter --help`]), or free it first.

**Another machine (Mac vs VPS).** Each machine is its own clone, so git offers no lock. Two writers on one branch cause non-fast-forward rejections on push, then merges or rebases of each other's work, or lost work if anyone forces. `git push` refuses non-fast-forward updates unless forced; `--force-with-lease` only protects against overwriting a ref that moved since your last fetch. [doc: [git-push --force-with-lease](https://git-scm.com/docs/git-push#Documentation/git-push.txt---force-with-leaseltrefnamegt)] The real guard is that only one orchestrator is live.

**Checks before the new orchestrator commits** (in order):

1. **Old side is stopped or idle.** Confirm in Herdr (or with the user) that the previous orchestrator's tab is not working and no delegate is mid-ticket. [unverified: needs a Herdr check per issue [#16](https://github.com/yahyabedirhan/skills/issues/16)]
2. **Old side has nothing uncommitted or unpushed.** On the old machine, in its worktree:
   ```bash
   git fetch origin
   git status --porcelain                 # empty = no uncommitted or untracked files
   git log --oneline @{u}..               # empty = nothing unpushed
   ```
   `@{u}` is the branch's upstream. [doc: [gitrevisions @{upstream}](https://git-scm.com/docs/gitrevisions#Documentation/gitrevisions.txt-emltbranchgtemupstreamemegemmasterupstreamememuem)] Tested locally: `?? new.txt` and one ahead commit were both reported. [tested] Example from today: the Mac shipyard worktree is level with origin (`d831d00` on both sides) but has six modified files, so it is not ready to hand over. [observed]
3. **New side matches origin.**
   ```bash
   git fetch origin
   git rev-parse HEAD @{u}                # identical
   git rev-list --left-right --count @{u}...HEAD   # "0 0" = neither behind nor ahead
   ```
   [doc: [git-rev-list --left-right --count](https://git-scm.com/docs/git-rev-list); tested]
4. **PR is still open on that branch.** `gh pr view <branch> --json number,state,baseRefName,headRefName`. [doc: `gh pr view --help`; observed for shipyard PR #21: OPEN, base `main`]
5. If step 2 found work, push it from the old side (or commit it there in its own commit, per issue [#6](https://github.com/yahyabedirhan/skills/issues/6)) before step 3.

## 3. Stacked PRs and what merging does to them

**Creating one.** From the new branch: `gh pr create --base <effort-branch>`. Without `--base`, gh uses `git config branch.<current>.gh-merge-base`, else the repo default branch. [doc: `gh pr create --help`] Setting `gh-merge-base` once lets a later bare `gh pr create` (such as the one in **to-pr**) pick the right base. [doc; unverified in practice] The stacked PR's diff shows only the new branch's commits against the lower branch. [doc: [gh-stack README, How it works](https://github.com/github/gh-stack)]

**CI.** A `pull_request` workflow with a `branches:` filter runs only for PRs targeting those branches, so a filter like `branches: [main]` skips a stacked PR. [doc: [Triggering a workflow](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow)] Shipyard's `ci.yml` has bare `push:` and `pull_request:`, so a stacked PR there would run CI. [observed]

**When the lower PR merges, the upper PR:**

- **Is retargeted only if the lower branch is deleted.** "If you delete a head branch after its pull request has been merged, GitHub checks for any open pull requests in the same repository that specify the deleted branch as their base branch" and changes their base to the merged PR's base. [doc: [Merging a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/merging-a-pull-request); [changelog 2020-05-19](https://github.blog/changelog/2020-05-19-pull-request-retargeting/)] Both shipyard and the vault have `delete_branch_on_merge: false` [observed], and **init-effort-with-herdr**'s closing step deletes only the local branch, so the upper PR would keep pointing at the merged branch until someone deletes the remote branch (`gh pr merge --delete-branch`) or runs `gh pr edit --base main`. Whether deleting with `git push origin --delete` also triggers retargeting is [unverified].
- **Merge commit:** the lower commits become ancestors of `main`, so the upper PR's diff against `main` is just its own commits and no rebase is needed; a later `git rebase main` would replay only commits not already reachable from main. [unverified by test; follows from rebase replaying `upstream..branch`, [git-rebase](https://git-scm.com/docs/git-rebase)] The vault merges with merge commits (`Merge pull request #13 ...`). [observed]
- **Squash merge:** `main` gains one new commit whose SHA matches none of the lower branch's commits, so the upper branch still carries the originals. GitHub warns that continuing on a squashed head branch "can force you to resolve the same conflicts more than once." [doc: [About pull request merges](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/about-pull-request-merges)] Tested: after a squash of `lower`, `git log main..upper` listed both lower commits plus the upper one, and a plain `git rebase main` stopped with a conflict on the first lower commit. The fix replays only the upper commits:
  ```bash
  git rebase --onto origin/main <old-lower-tip> <upper-branch>
  git push --force-with-lease
  ```
  This produced a clean history (`upper1` on top of `squash of lower`) with the right diff. [tested; doc: [git-rebase --onto](https://git-scm.com/docs/git-rebase)] Record `<old-lower-tip>` before merging (for example `gh pr view <lower> --json headRefOid`). [doc: `gh pr view --json` fields]
- **Rebase merge:** GitHub "creates new commit SHAs", so the same `--onto` rebase applies. [doc: About pull request merges]
- **Changing a base** can drop commits from the PR timeline and outdate review comments. [doc: [Changing the base branch](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/changing-the-base-branch-of-a-pull-request)]
- **Deleting the lower branch before its PR merges** is blocked in the UI while other open PRs reference it. [doc: [Deleting and restoring branches in a pull request](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-branches-in-your-repository/deleting-and-restoring-branches-in-a-pull-request)]

**Tools built for this (context only, not evaluated):** `gh stack` (official extension `github/gh-stack`; `gh pr create --help` points to it) creates the branches, sets each PR's base, and its `rebase` switches to `--onto` mode when a lower PR was merged. [doc: gh-stack README] `git rebase --update-refs` moves every branch pointing into the rebased range in one go, but not branches checked out in a worktree, which is exactly how efforts live. [doc: [git-rebase --update-refs](https://git-scm.com/docs/git-rebase#Documentation/git-rebase.txt---update-refs)] Graphite and git-town offer the same stack model. [not researched]

## 4. Same branch vs stacked branch

| | Same branch (continue shipyard PR #21) | Stacked branch (new PR based on `build/shipyard-core-0.0.x`) |
|---|---|---|
| Open PR | Keeps growing; new commits land in it | Unchanged; frozen for review |
| Review size | One PR, everything since `main` | Two PRs, each only its own layer |
| Merge order | One merge | Lower first; upper must then be retargeted to `main` (delete the lower branch or `gh pr edit --base main`) |
| After a squash merge | Nothing to fix | Upper needs `git rebase --onto` and a force push |
| After a merge commit | Nothing to fix | Retarget only; no rebase needed [unverified] |
| CI | Runs as before | Runs only if `pull_request` has no `branches:` filter excluding the base |
| Two-writer risk | High: both orchestrators push to one ref; confirm the old one is stopped | Low: the new orchestrator owns a new ref; the old branch can still receive fixes |
| Worktree | Tracking worktree on the existing branch; same-machine reuse, or `switch <branch>` on another clone | New branch from `origin/<effort-branch>` in a fresh lease |
| Fits when | The old orchestrator is finished or stopped and the PR is not yet under review | The open PR is under review or should merge on its own |

## 5. Delivery ending in a clean tree

**Is `.humanlayer/` meant to be tracked?** HumanLayer's own design is **not git**: task files under `.humanlayer/tasks/<task-slug>/` sync to HumanLayer's cloud through their daemon and agent hooks. [doc: [How HumanLayer tasks keep related work together](https://docs.humanlayer.com/explanation/tasks)] Their workspace setup writes "an optional `.gitignore` entry", and release 0.148.0 says it "Only edits `.gitignore` when Git doesn't already ignore its task-artifacts path", which implies the task-artifacts path is meant to be ignored. [doc: [Workspace config reference](https://docs.humanlayer.com/reference/workspace-config), [Release notes](https://docs.humanlayer.com/release-notes)] Their older `describe_pr` command saved to `thoughts/shared/prs/{number}_description.md`, a separate repo kept out of the code repo by a pre-commit hook. [doc: [describe_pr.md](https://github.com/humanlayer/humanlayer/blob/main/.claude/commands/describe_pr.md), [hlyr/THOUGHTS.md](https://github.com/humanlayer/humanlayer/blob/main/hlyr/THOUGHTS.md)] The **to-pr** final-answer template's "cloud permalink from hook" is a leftover of that sync. [observed]

**Without HumanLayer's cloud, nothing syncs**, so an untracked file is lost when the worktree is destroyed. This user already tracks them: the vault has `.humanlayer/tasks/pr-10`, `pr-11`, `pr-12` committed and no ignore rule, and shipyard later committed `pr-21` as `0646a5a docs(pr): save the description of pull request 21`. [observed] So: track them, or ignore them deliberately; do not leave them untracked.

**Ordering.** The file name needs the PR number, so the description can only be committed after `gh pr create`. That commit lands on the PR and reruns CI. [unverified: CI rerun follows from `on: push` / `pull_request`] Acceptable, or have **to-pr** use a task-slug folder known before the PR exists.

**Verifying a clean tree after delivery:**

```bash
git status --porcelain            # must print nothing (includes untracked files)
git fetch origin
git log --oneline @{u}..          # must print nothing (all commits pushed)
```

`--porcelain` is the stable, script-friendly format. [doc: [git-status --porcelain](https://git-scm.com/docs/git-status#_porcelain_format_version_1)] Ignored files do not appear, so anything under an ignored `tmp/` is not "unfinished" to git, and treehouse `destroy` removes it without warning. [doc: skills repo `init-effort-with-herdr/treehouse.md`; tested for porcelain]

## 6. gh commands reference

| Need | Command |
|---|---|
| PR for the current branch | `gh pr view --json number,state,baseRefName,headRefName,headRefOid,url` |
| Open a stacked PR | `gh pr create --base <lower-branch> --title ... --body-file <file>` |
| Default base for a branch | `git config branch.<branch>.gh-merge-base <lower-branch>` |
| Rewrite the description | `gh pr edit <n> --body-file <file>` (`-` reads stdin) |
| Retarget after the lower PR merges | `gh pr edit <n> --base main` |
| Merge and delete the branch (triggers retargeting of stacked PRs) | `gh pr merge <n> --merge --delete-branch` (or `--squash`, `--rebase`) |
| Repo merge settings | `gh api repos/<owner>/<repo> --jq '{delete_branch_on_merge,allow_squash_merge,allow_merge_commit}'` |

[doc: `gh pr create --help`, `gh pr edit --help`, `gh pr merge --help`, gh 2.92.0; `gh api` read observed]

## What this means for the tickets

- **#3 (commit without asking again).** Commit and push should be one narrow command, never bundled with `rm -rf`. A normal push is safe to allow standing: it cannot overwrite remote work, it is rejected on non-fast-forward. Only a stacked rebase needs `--force-with-lease`, and that one deserves its own explicit ask.
- **#6 (start from a committed worktree).** The check is `git status --porcelain` empty plus `git log @{u}..` empty (or no upstream yet on a fresh branch). The same check is step 2 of a takeover in issue [#15](https://github.com/yahyabedirhan/skills/issues/15), run on the old side.
- **#14 (clean tree after the PR).** HumanLayer ignores `.humanlayer/` and syncs it to its cloud; this user has no cloud sync and already commits the files in the vault and shipyard. Recommend **to-pr** own the rule "commit and push the saved description after `gh pr edit`", since it writes the file and reruns rewrite it, and **orchestrate-effort**'s deliver step end with the porcelain plus `@{u}..` check, reporting a clean tree or naming each left-out file.
- **#15 (continue an unfinished effort).** Detect a continuation by the handoff living on a non-default branch with an open PR (`gh pr view <branch>`). Ask one question, with the table in section 4 as the explanation. Same branch: section 2 checks, then `treehouse get --lease` plus `git switch <branch>`, or reuse the worktree if the branch is already checked out on this machine. Stacked: new branch from `origin/<effort-branch>`, set `gh-merge-base`, and warn that after the lower PR merges the upper needs a retarget (branch deletion is off in both repos) and, after a squash, a `rebase --onto`.

## Open questions

- TODO: Update treehouse to v3.0.0 and verify `get --lease --base <branch> -b <new>` for the stacked case, and whether `--base <effort-branch>` followed by `git switch <effort-branch>` is the cleanest same-branch path.
- TODO: Check whether deleting a merged branch with `git push origin --delete` (not the UI or `gh pr merge --delete-branch`) triggers GitHub's retargeting.
- TODO: Decide whether shipyard and the vault turn on `delete_branch_on_merge` so stacked PRs retarget themselves, and whether **init-effort-with-herdr**'s closing step should delete the remote branch.
- TODO: Decide the user's merge style for effort PRs (the vault uses merge commits; shipyard unknown), since squash is what makes stacking costly.
- TODO: Decide whether to-pr should save under a task-slug folder that exists before the PR, so the description can ride in the last ticket commit instead of an extra commit.
- TODO: Define how a skill confirms the old orchestrator on the VPS is idle before a same-branch takeover (issue [#16](https://github.com/yahyabedirhan/skills/issues/16) territory).
- TODO: Verify with a real remote (the lab here had none) that `git switch <branch>` in a fresh treehouse slot sets upstream to `origin/<branch>`, as the docs say and the shipyard slot shows.
