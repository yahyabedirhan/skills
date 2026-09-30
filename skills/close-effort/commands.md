# Commands for closing an effort

The git and gh commands for **close-effort**'s steps. Each entry says what it's for, its alternatives, and when to use each. `<default>` is the default branch, `<n>` the pull request's number. Run each commit, push and deletion as its own call, so a refused one stops only itself.

## Find the pull request (step 1)

- `gh pr view [<n>] --json number,url,state,headRefName,baseRefName,mergeCommit,body`: the pull request, its branches, its merge commit and its description. Without `<n>` it takes the current branch's.
- `gh pr list --head <branch> --state all`: when this session isn't on the effort branch (such as in the main checkout) and no number was given.

## Find the tickets, worktrees and branches (step 1)

- `gh issue list --label effort:<effort> --state all`: the effort's tickets on GitHub. On a local tracker, read `.efforts/<effort>/` instead.
- `git worktree list --porcelain`: every worktree with its branch. The plain `git worktree list` is easier to read and enough when branches aren't needed. When the worktree tool is Treehouse, `treehouse status` also shows which worktrees it leases.
- `git branch -vv`: local branches with their upstream; `[gone]` marks one whose remote branch was deleted. `git branch -r` lists the remote ones.

## Merge (step 2)

- `gh pr checks <n>`: whether the checks pass. Add `--watch` to wait for pending ones.
- `gh pr merge <n> --merge|--squash|--rebase`: the flag is the project's method. `--auto` merges once pending checks pass, when the repo allows it. Leave out `--delete-branch`: it deletes branches before step 7 proves them, and switches the current checkout to the default branch.
- `gh run list --commit <merge sha>`: the default branch's CI on the merge commit; `gh run watch <run id>` waits for one still running.
- `git merge-base --is-ancestor <pinned sha> origin/<default>`: a commit pinned somewhere (such as an image URL) still resolves after a squash or rebase. It succeeds when the commit is on the default branch.

## Update without moving the main checkout (step 4)

- `git -C <main checkout> status --short --branch`: whether the checkout is clean and on the default branch.
- `git -C <main checkout> pull --prune`: only when it is both. Otherwise `git -C <main checkout> fetch --prune`, and work from `origin/<default>`.

## The follow-up branch (step 4)

- `git worktree add --no-track -b <effort>-close <path> origin/<default>`: a worktree on a new branch from the default branch. When the worktree tool is Treehouse, lease one and switch its branch as the **treehouse** skill says.

## Carry over and close the tracker (steps 4 and 5)

- `gh label list --search effort:<next>`, then `gh label create effort:<next>` when it's missing.
- `gh issue create --title <title> --body <body> --label effort:<next>`: a next-effort ticket; the body links where the item came from. `--body-file` suits a long body.
- `gh issue comment <n> --body <text>`: the note on a QA ticket that the work is on the default branch.
- `gh issue close <n> --comment <text>`: a finished ticket, or a carried-over one with a link to the ticket that continues it.
- `gh issue edit <n> --body-file <file>`: ticks a criterion that could only be shown after the merge.

## Files and work only here (step 6)

- `git -C <path> status --short --ignored`: a worktree's untracked (`??`) and ignored (`!!`) files, which removing it deletes.
- `git -C <path> status --short`: uncommitted work; empty means clean.
- `git log --branches --not --remotes --oneline`: commits on any local branch that no remote holds yet.

## Prove merged (step 7)

Fetch first with `git fetch --prune`, so `origin/<default>` is current and deleted remote branches drop out.

- **Reachable**: `git merge-base --is-ancestor <branch> origin/<default>` succeeds. Cheapest; use it first.
- **Matched by patch**: `git cherry origin/<default> <branch>` prints no `+` line. A `+` proves nothing either way: a squash merge or a changed commit leaves one.
- **In the merged pull request's head**: `gh pr view <n> --json state,headRefOid` shows `MERGED`, and `git merge-base --is-ancestor <branch> <headRefOid>` succeeds. When that commit is missing locally, `git fetch origin pull/<n>/head` first. For a leftover delegate branch, `git log <headRefOid> --grep <ticket>` finds its ticket's commit, and `git log --oneline <headRefOid>..<branch>` shows only the one ticket commit the delegate made.

## Free worktrees and branches (steps 7 and 8)

- `git worktree remove <path>`: removes a clean worktree. Leave out `--force`: a worktree that needs it isn't clean, so it isn't proven. `git worktree prune` drops entries whose folder is already gone.
- When the worktree tool is Treehouse, `treehouse return <path>` gives it back to the pool, warm for the next effort; `treehouse destroy` removes it for good and suits only a worktree the pool shouldn't keep. The **treehouse** skill has both.
- `git branch -d <branch>`: deletes a local branch git sees as merged, so it fits the reachable proof. `git branch -D <branch>` when only the patch match or the merged pull request's head proves it.
- `git push origin --delete <branch>`: deletes the remote branch. `git ls-remote --heads origin <branch>` shows whether the remote still holds it; a repo that deletes head branches on merge may already have.

This session's own worktree is freed with the same command, from outside it: when the session host is Herdr, as the **handover-to-herdr** skill's `closing-an-effort.md` says; otherwise the maintainer runs it once this session is closed.
