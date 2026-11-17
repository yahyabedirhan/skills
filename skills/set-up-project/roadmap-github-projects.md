# Roadmap

This page says how <product> keeps its roadmap in a GitHub project, above the agent specs and tickets in GitHub issues.
A product is what the roadmap plans, and it can span several repositories: <repos>.
Its presence puts the project in roadmap mode: read it before you plan, start, deliver or settle work here.
The skills speak of the roadmap in shared terms, and this page maps each one to GitHub Projects:

- **The roadmap:** the GitHub project below, one per product.
- **Roadmap issue:** a draft item on that project. It has no number, and it never appears in a repository's issue list.
- **Release group:** an option of the project's `Release` field. Its **release note** goes in the repository's GitHub release.

The [`/set-up-project`](https://github.com/yahyabedirhan/skills/tree/main/skills/set-up-project) skill wrote it.

_`/set-up-project` fills in each `<slot>`, removes each line that does not apply, and removes every note in italics like this one._

## Planning layers

| Layer | What it holds | Who reads it |
|---|---|---|
| The notes | History and thinking, as `docs/agents/notes.md` says. | The maintainer, and agents that need the history |
| The roadmap | What to build and the high-level how, the release groups and the status. | The maintainer |
| GitHub issues | Agent specs and tickets that are ready to build, planned in waves. | Agents |
| Codebase docs | How the project works today. | Everyone |

- Move work from the notes to the roadmap, or from the roadmap to GitHub issues, only when the maintainer says so.
- Give every change that affects released content a roadmap issue: a feature, a bugfix or a chore, also work that an agent finds.
- Size a roadmap issue to about one pull request. A roadmap issue and the GitHub issues for it do not map one to one.
- Make every change on the roadmap yourself, so the maintainer only reads and decides there.

## GitHub project

- **Project:** `<project title>`, number `<number>`, owned by `<owner>`, at `<project URL>`. Its node id is `<project id>`.
- **Repositories:** the project is linked to each repository of the product, with `gh project link <number> --owner <owner> --repo <owner>/<repo>`, so it shows in each repository's Projects tab.
- **Access:** use `gh project` and `gh api graphql`. The token needs the `project` scope.
  When a call fails for a missing scope, ask the maintainer to run `gh auth refresh -s project`.
- **Views:** the API cannot create views, so a new view is a maintainer step.
  _List the views the maintainer keeps, such as a board by `Status` or a table by `Release`._

Fill these fields on every roadmap issue:

| Field | Kind | Value |
|---|---|---|
| `Status` | built in | A step of the 'Status flow' below. |
| `Release` | single select | The release group, or `Unplanned` when it has none yet. |
| `Work type` | single select | `Bug`, `Feature`, `Improvement`, `Chore`, `Decision` or `QA`. |
| `Lands in` | single select | The main repository of the change. Name any other repository in the body. |

_When the product has only one repository, remove the `Lands in` row._

Keep the fields to these, since each field value costs one change against GitHub's limit, as 'Limits' says.
Write the part of the product that the change touches as an `Area:` line in the body.

The commands:

- **List items:** `gh project item-list <number> --owner <owner> --format json --limit 500`
- **Find field and option ids:** `gh project field-list <number> --owner <owner> --format json`
- **Add a roadmap issue:** `gh project item-create <number> --owner <owner> --title "<title>" --body "<body>" --format json`.
  A new draft item gets no `Status`, so set it to Todo and fill the other fields at once.
- **Set a field:** `gh project item-edit --project-id <project id> --id <item id> --field-id <field id> --single-select-option-id <option id>`.
- **Edit the title or body:** `gh project item-edit --id <draft issue id> --title "<title>" --body "<body>"`. The draft issue id starts with `DI_`.

## Release groups

- Give each release group a `Release` option named `Release <version>`.
  _For a product that spans several repos, name each option `<repo> <version>`, and only for a repo that publishes versions._
- Move unfinished work to the next release group: set its `Release` to the next option.
- Write the release note in the repository's GitHub release, with `gh release create` or `gh release edit --notes`.

_When the product publishes no versions, remove this section._

## Status flow

1. **Todo:** the maintainer decided the work, and no effort builds it yet.
2. **In Progress:** the orchestrator sets this status when the effort starts.
3. **On beta:** set this status when the pull request merges to beta.
4. **Done:** set this status when the release that holds the work reaches production.
5. **Canceled:** set this status when the maintainer drops the work.

_When the project ships on each merge, with no beta, remove step 3: the work goes to Done when the merge and its follow-ups are done._

Set each status yourself, as 'Limits' says.

## Maintainer-only steps

A step that only the maintainer can do, such as a manual check, a login, a payment or a decision, goes to the roadmap as its own roadmap issue.

- Assign it to `<maintainer>`, through `gh api graphql` with `updateProjectV2DraftIssue` and its `assigneeIds`.
  A draft item sends no notification, so tell the maintainer in your report too.
- Set `Work type` to `QA` for a check, or `Decision` for a decision.
- Set the same `Release` as the work it gates.
- Start its body with a `Blocks:` line that links the roadmap issue it gates.
- Give it the build and how to reach it, numbered try-this steps with known risks marked, and links to screenshots in the spec issue or the pull request.
- Say what to do when done: set `Status` to Done if it is good, or add a line under `## Progress` with the step number and what they saw.

## Roadmap issues

Write each roadmap issue for the maintainer:

- Keep sentences short, in the active voice.
- Use one word for one thing, every time.
- Number the steps.
- Put a warning in the step it belongs to, as a plain sentence. WARNING, CAUTION and NOTE blocks belong to GitHub issues, which use the full rules.
- Put agent detail, such as file lists, plans and logs, in a collapsed section at the end:

```html
<details><summary>Agent notes</summary>

Details for agents go here.

</details>
```

## Links between layers

Link a roadmap issue as `<project URL>?pane=issue&itemId=<item id>`.

- Start a spec from the roadmap issue the conversation is about. When the conversation names none, ask the maintainer which one, and create one only when they say so.
- Start the description of each GitHub spec, ticket and pull request with a `Roadmap:` line that links its roadmap issue. Keep the title free of the link.
- Link the GitHub spec and the pull request in the roadmap issue's body the same way.

A draft item takes no comments, so record progress in its body, in a `## Progress` section above the agent notes:

- Add a dated line when the spec is published, with the spec's link.
- Add a dated line when the effort starts, with the plan in one sentence, and set `Status` to In Progress.
- Add a dated line at delivery, with the pull request's link.
  Keep screenshots, diagrams and other detail in the spec issue and the pull request.

## Limits

- A draft item has no labels, no milestone and no repository.
- Assigning a draft item sends no notification.
- GitHub's built-in project workflows, such as "set Done when a pull request merges", act only on issues and pull requests. They skip draft items, so agents set every status.
- The API cannot create views.
- GitHub allows about 80 content changes a minute and 500 an hour, and each field value is one change. Batch the changes: set an item's fields in one `gh api graphql` call with several aliased mutations, rather than one call per field.
- A new draft item gets no `Status` by itself. The agent sets it, unless the maintainer turns on the project's "Item added to project" workflow in the web UI.
