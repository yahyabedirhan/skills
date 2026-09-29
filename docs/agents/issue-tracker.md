# Issue tracker: GitHub

Issues, specs and tickets for this repo live as GitHub issues in `yahyabedirhan/skills`, so the repo has no `.efforts/` folder. Use the `gh` CLI for all operations; it infers the repo from `git remote -v`.

## Conventions

- **Create an issue**: `gh issue create --title "..." --body "..."`. Use a heredoc for multi-line bodies.
- **Read an issue**: `gh issue view <number> --comments`.
- **List issues**: `gh issue list --state open --json number,title,labels` with `--label` and `--state` filters.
- **Comment on an issue**: `gh issue comment <number> --body "..."`.
- **Apply or remove labels**: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`.
- **Close**: `gh issue close <number> --comment "..."`.
- **Efforts**: every issue of an effort carries the label `effort:<effort>`; list an effort's tickets with `gh issue list --label effort:<effort>`.
- Refer to an issue by its title, never by its number alone.

## Pull requests as a triage surface

**PRs as a request surface: no.**

## When a skill says "publish to the issue tracker"

Create a GitHub issue, labelled `effort:<effort>` when it belongs to an effort.

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number> --comments`.
