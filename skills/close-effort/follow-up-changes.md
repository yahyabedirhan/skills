# Follow-up changes

The close itself changes tracked files: a local tracker's done marks, files saved from a worktree.

- Leave the maintainer's main checkout on whatever branch it is on, since they may be working there. Pull there only when it is clean and already on the default branch; otherwise work from the remote default branch.
- Land every change through a pull request, never straight on the default branch. Unless the project says otherwise, put the close's changes on one small follow-up branch, in its own worktree, and open its pull request through `/to-pr`. Changes too small for a pull request go in the report instead.
- Make the follow-up worktree with `git worktree add --no-track -b` from the remote default branch. `--no-track` leaves the branch without an upstream until its first push, since a branch that tracks the default branch makes a bare `git push` target it.
- Once the follow-up branch is pushed and its pull request is open, free its worktree to save disk space, and delete its local branch when the remote holds it. The pushed branch is the proof its work is safe.
- Run each commit and each push as its own call, so a refused one stops only itself.
