# Project creation

Create a new project's repo only after the maintainer has confirmed its name, its visibility and its licence.

1. Put the project in the maintainer's **projects folder**. When you don't know where that is, ask. Check that neither a folder nor a GitHub repo already has the project's name.
2. Create the folder and a git repository in it, on `main`.
3. Write a `README.md`, with the name as a heading and the idea in a paragraph, and the `LICENSE`.
4. Set it up with `/set-up-project`, in the new folder, with GitHub as its tracker and `<owner>/<name>` as the repo.
5. Commit it all as the first commit, `chore: start <name>`, in its own call, so a refused command stops only itself.
6. Create the GitHub repo with the visibility the maintainer chose, as `origin`, and push `main`. A worktree tool needs both the first commit and `origin` before it can make worktrees of the new repo.
