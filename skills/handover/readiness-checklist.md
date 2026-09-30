# Readiness Checklist

Get the repository and the handoff ready before the new session starts, fixing each item that isn't true yet.

## Worktree and branch

Branch from the remote default branch, or from the local default branch when the work builds on commits there that aren't pushed. Move the uncommitted changes on the default branch that belong to the work into the worktree, and leave the rest where they are.

Until the new session starts, keep this session on its own checkout and branch, so the maintainer's checkout isn't switched under them. Write into the worktree by absolute path, and run git there with `git -C <worktree>`.

## Maintainer inputs

Keep secrets out of chat and files, and have the handoff say where they live.

QA applies only to an effort, in a project whose instructions opt in to QA by the maintainer. The spec says either "QA: blocking" or that QA is non-blocking, which is the default. When the spec says neither, ask the maintainer while they are here, and write the answer into the spec.

## Reachability

This session is unreachable when it can't receive messages: a desktop-app session, or any session `<session-host>` can't prompt. When it is unreachable, the handoff tells the new session to decide open questions itself and list them in the pull request.

## Commit and push

The worktree is ready when it is clean and its branch matches its remote.

- Run each commit and each push as its own call, because a deny rule that matches anything else in a chain blocks the whole chain.
- After an interrupted or rejected call, check the log before retrying, because the commit or push may have landed anyway.
