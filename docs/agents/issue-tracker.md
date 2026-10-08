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

## Title prefixes

Start every issue title with one prefix, then `: ` and a capitalized title with no trailing period, for example `QA: Verify the panel on a VPS`. When more than one prefix fits, use the first one in this order:

1. `QA`: manual work for the maintainer.
2. `VPS`: work on a remote machine.
3. A harness: `Claude` (claude.ai, cloud sessions and managed agents), `Codex`, `OpenCode`, `Cursor` or `Pi`. Claude Code is the default harness, so it gets no prefix.
4. A semantic prefix from the list below: one area of this project.
5. `Bug`, `Feature`, `Chore` or `Spec`: the kind of work.
6. `Research`: a question to answer before the work starts.

Write each prefix the way its maker writes it, so a skill name stays lowercase. Use a semantic prefix before a generic one when one fits.

### Semantic prefixes

- `Publish`: publishing the skills and making them discoverable.
- `Workflow`: how skill changes ship and how sessions get recapped.

Reuse a prefix from this list before you add a new one. Add a new one when no prefix fits and the issue belongs to one tool, product, skill or workflow. Add it to this list in the same change.

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
