# Commands for starting an effort

The git and gh commands for **init-effort**'s steps. Each entry says what it's for, its alternatives, and when to use each. `<path>` is the new project's folder, `<default>` the default branch. Run each commit and each push as its own call, so a refused one stops only itself.

## Check the name is free (step 3)

- `ls <projects folder>/<name>` fails when no folder has the name.
- `gh repo view <name>` fails when the maintainer's account has no repo by that name. Pass `<owner>/<name>` to check an organisation.

## Create the project (step 3)

- `mkdir <projects folder>/<name>`, then `git -C <path> init -b main`. `-b main` names the first branch whatever git's local default is.
- `git -C <path> add -A`, then `git -C <path> commit -m "chore: start <name>"`: the first commit, holding the README, the licence and what **set-up-project** wrote. Stage by name instead of `-A` when the folder holds anything else.
- `gh repo create <name> --public|--private --source <path> --remote origin --push`: creates the GitHub repo, adds it as `origin` and pushes `main`, in one call. The flag is the maintainer's answer. The alternative is creating the repo on GitHub, then `git remote add origin <url>` and `git push -u origin main`; use it only when `gh` can't create the repo, such as under an organisation it has no rights to.

## Create the worktree (step 4)

- `git fetch origin`: brings the default branch up to date, so the worktree starts from the latest one.
- `git worktree add --no-track -b <branch> ../<repo>-<effort> origin/<default>`: a new worktree on a new branch. `--no-track` keeps `origin/<default>` from becoming the branch's upstream, which would make a bare `git push` target the default branch. The first push sets the real upstream with `git push -u origin <branch>`. The path beside the main checkout is the default; a project that keeps worktrees elsewhere, such as `.claude/worktrees/`, uses that.
- When the worktree tool is Treehouse, the **treehouse** skill leases one and switches its branch instead.
