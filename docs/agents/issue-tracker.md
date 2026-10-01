# Issue tracker: GitHub

Issues, specs and tickets for this repo live as GitHub issues in `yahyabedirhan/skills`, so the repo has no `.efforts/` folder. Use the `gh` CLI for all operations; it infers the repo from `git remote -v`.

## Conventions

- **Create an issue**: `gh issue create --title "..." --body "..."`. Use a heredoc for multi-line bodies.
- **Read an issue**: `gh issue view <number> --comments`.
- **List issues**: `gh issue list --state open --json number,title,labels` with `--label` and `--state` filters.
- **Comment on an issue**: `gh issue comment <number> --body "..."`.
- **Apply or remove labels**: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`.
- **Close**: `gh issue close <number> --comment "..."`.
- **Efforts**: every issue of an effort carries the label `effort:<effort>`; list an effort's tickets with `gh issue list --label effort:<effort>`. Create that label before the first issue that uses it, as the publish section says. `gh issue create --label` fails when the label does not exist yet.
- Refer to an issue by its title, never by its number alone.

## Pull requests as a triage surface

**PRs as a request surface: no.**

## When a skill says "publish to the issue tracker"

Create a GitHub issue. When it belongs to an effort, make sure the `effort:<effort>` label exists before `gh issue create`, because `--label` fails on a label the repo does not have yet. List labels and create it only when that exact name is missing, so a later issue does not try to recreate it:

```bash
gh label list --limit 1000 --json name --jq '.[] | select(.name == "effort:<effort>") | .name'
gh label create "effort:<effort>"
gh issue create --title "..." --body "..." --label "effort:<effort>"
```

Run `gh label create` only when the list prints nothing. An issue that is not part of an effort is `gh issue create --title "..." --body "..."` with no label.

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number> --comments`.
