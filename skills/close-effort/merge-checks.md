# Merge checks

## Finding the pull request

Use the pull request given as the argument, or the current branch's. From a checkout that isn't on the effort's branch, list pull requests by head branch with `gh pr list --head` and `--state all`; without `--state all`, a merged pull request doesn't show.

## Before merging

Merge once the checks pass. When the spec says "QA: blocking", every QA ticket must also be closed; if one is still open, tell the maintainer which one and stop.

Merge with the method the project uses. Leave out `gh pr merge --delete-branch`: it deletes branches before they are proven merged, and switches the current checkout to the default branch.

## After merging

Check that the default branch's CI passes on the merge commit. After a squash or a rebase, check that anything pinned to a branch commit still resolves, such as an image URL that carries a commit SHA. A red run or a broken pin becomes unfinished work to carry over.
