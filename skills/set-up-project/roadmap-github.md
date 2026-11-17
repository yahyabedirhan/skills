# Roadmap

This page says how <product> keeps its roadmap in GitHub: as issues in its main repository, on the product's GitHub project.
A product is what the roadmap plans, and it can span several repositories: <repos>.
Its presence puts the project in roadmap mode: read it before you plan, start, deliver or settle work here.
The skills speak of the roadmap in shared terms, and this page maps each one to GitHub:

- **The roadmap:** the issues labelled `roadmap` in `<owner>/<main repo>`, on the GitHub project below.
- **Roadmap issue:** one issue labelled `roadmap`.
- **Release group:** a milestone in `<owner>/<main repo>`. Its **release note** is the milestone's description.

The [`/set-up-project`](https://github.com/yahyabedirhan/skills/tree/main/skills/set-up-project) skill wrote it.

_`/set-up-project` fills in each `<slot>`, removes each line that does not apply, and removes every note in italics like this one._

## Planning layers

| Layer | What it holds | Who reads it |
|---|---|---|
| The notes | History and thinking, as `docs/agents/notes.md` says. | The maintainer, and agents that need the history |
| The roadmap | What to build and the high-level how, the release groups, the status and the maintainer-only steps. | The maintainer |
| Specs and tickets | Agent work that is ready to build, planned in waves. | Agents |
| Codebase docs | How the project works today. | Everyone |

- Move work from the notes to the roadmap, or from the roadmap to specs and tickets, only when the maintainer says so.
- Give every change that affects released content a roadmap issue: a feature, a bugfix or a chore, also work that an agent finds.
- Size a roadmap issue to about one pull request. A roadmap issue and the specs and tickets for it do not map one to one.
- Make every change on the roadmap yourself, so the maintainer only reads and decides there.

## Issue kinds

Every issue carries exactly one kind label:

| Label | What it is | Who it is for |
|---|---|---|
| `roadmap` | What to build, a release group's work, deferred work, or a maintainer-only step. | The maintainer |
| `spec` | An effort's spec, a sub-issue of its roadmap issue. | Agents |
| `ticket` | One ticket of a spec, a sub-issue of that spec. | Agents |

- Give each issue one of GitHub's issue types: `Bug`, `Feature` or `Task`.
  Set it with `gh api graphql` and `updateIssue` with its `issueTypeId`.
- Label a roadmap issue `deferred` when it matters but waits on purpose. A deferred issue has no milestone.
- Label each issue with its `area:<name>`: <areas>.
  _When the product has no areas, remove this line._
- Title each issue as `docs/agents/issue-tracker.md` > 'Title prefixes' says, with no serial numbers.
- Write specs and tickets to the one standard that the issue tracker page sets, for agents and with no pictures.

A roadmap issue lives in the main repository, even when its work lands in another repository of the product.
Never create a repository only to hold issues.
_When the product has no repository yet, keep its roadmap issues as draft items on the GitHub project._
_Convert each one to an issue with `convertProjectV2DraftIssueItemToIssue` when the repository exists, as 'Limits' paces it._

## GitHub project

- **Project:** `<project title>`, number `<number>`, owned by `<owner>`, at `<project URL>`. Its node id is `<project id>`.
- **Repositories:** the project is linked to each repository of the product, with `gh project link <number> --owner <owner> --repo <owner>/<repo>`.
- **Access:** use `gh project` and `gh api graphql`. The token needs the `project` scope.
  When a call fails for a missing scope, ask the maintainer to run `gh auth refresh -s project`.

The project holds only roadmap issues.
Add each new roadmap issue with `gh project item-add <number> --owner <owner> --url <issue URL>`.
A new item gets no `Status` by itself, so set it to Todo at once.

The project has two fields of its own:

- **Status:** `Todo`, `In Progress`, `On beta`, `Done` or `Canceled`, as the 'Status flow' says.
- **Priority:** `Urgent`, `High`, `Medium` or `Low`, as the maintainer decides.

GitHub gives the rest from the issue: `Milestone`, `Type`, `Labels` and the sub-issues progress.
Add no other project fields, since each field value costs one change against GitHub's limit, as 'Limits' says.

The commands:

- **List items:** `gh project item-list <number> --owner <owner> --format json --limit 500`
- **Find field and option ids:** `gh project field-list <number> --owner <owner> --format json`
- **Set a field:** `gh project item-edit --project-id <project id> --id <item id> --field-id <field id> --single-select-option-id <option id>`

## Views

Create and change the views yourself, through `gh api graphql`:

1. Create the view with `createProjectV2View`.
2. Set its `name`, `layout` (`BOARD_LAYOUT` or `TABLE_LAYOUT`), `filter` and `configuration.visibleFieldIds` with `updateProjectV2View`.

The API sets no grouping or sorting, so each view is a filter, and each filter starts with `label:roadmap`:

| View | Layout | Filter |
|---|---|---|
| Board | board, with a column for each `Status` | `label:roadmap -status:Canceled` |
| `<milestone>` | board | `label:roadmap milestone:"<milestone>" -status:Canceled` |
| Deferred | table | `label:roadmap label:deferred` |
| Bugs | table | `label:roadmap type:Bug -status:Done,Canceled` |
| Urgent & high | table | `label:roadmap priority:Urgent,High -status:Done,Canceled` |
| Shipped | table | `label:roadmap status:Done` |
| All | table | `label:roadmap` |

Grouping or sorting in the web UI is optional, for the maintainer.

## Release groups

- Give each release group a milestone named `Release <version>`.
  _For a product that spans several repos, name each milestone `<repo> <version>`, and only for a repo that publishes versions._
- Add the milestone's board view when the group starts, and delete it when the group ships.
- Move unfinished work to the next milestone, or label it `deferred` and remove its milestone.
- Write the release note in the milestone's description when the group ships.

_When the product publishes no versions, remove this section._

## Status flow

1. **Todo:** the maintainer decided the work, and no effort builds it yet.
2. **In Progress:** the orchestrator sets this status when the effort starts.
3. **On beta:** set this status when the pull request merges to beta.
4. **Done:** set this status and close the issue when the release that holds the work reaches production.
5. **Canceled:** set this status and close the issue as not planned when the maintainer drops the work.

_When the project ships on each merge, with no beta, remove step 3: the work goes to Done when the merge and its follow-ups are done._

## Maintainer-only steps

A step that only the maintainer can do, such as a manual check, a login, a payment or a decision, goes to the roadmap as its own roadmap issue.

- Assign it to `<maintainer>`.
- Give it the same milestone as the work it gates.
- Mark the roadmap issue it gates as blocked by it, with GitHub's issue dependencies: `--blocked-by` in `gh issue`, or the issue dependencies API.
- Give it the build and how to reach it, numbered try-this steps with known risks marked, and screenshots.
- Say what to do when done: close it if it is good, or comment with the step number and what they saw.

## Roadmap issues

Write each roadmap issue for the maintainer:

- Lead with a picture: an ASCII diagram in a `text` block, or screenshots and rendered diagrams.
  Upload an image with `gh issue create` or `gh issue edit` and one `--attach` per file. Use no Mermaid.
- Keep sentences short, in the active voice.
- Use one word for one thing, every time.
- Number the steps.
- Put a warning in the step it belongs to, as a plain sentence. WARNING, CAUTION and NOTE blocks belong to specs and tickets, which use the full rules.
- Put agent detail, such as file lists, plans and logs, in a collapsed section at the end:

```html
<details><summary>Agent notes</summary>

Details for agents go here.

</details>
```

## Links between layers

- Start a spec from the roadmap issue the conversation is about. When the conversation names none, ask the maintainer which one, and create one only when they say so.
- Start the description of each spec, ticket and pull request with a `Roadmap:` line that names its roadmap issue as `<owner>/<repo>#<n>`. Keep the title free of it.
- Make each spec a sub-issue of its roadmap issue, and each ticket a sub-issue of its spec, with `gh api graphql` and `addSubIssue`.
  The project's card then shows the sub-issues progress.
- Comment on the roadmap issue when its spec is published, with the spec.
- Comment on it when the effort starts, with the plan, and again at delivery, with the pull request, screenshots and a status diagram.

## Limits

- GitHub throttles issue creation harder than field changes.
  Create or convert about 5 issues a request, with a request every 20 seconds.
- GitHub allows about 80 content changes a minute and 500 an hour, and each field value is one change.
  Batch field changes in `gh api graphql` calls with aliased `updateProjectV2ItemFieldValue` mutations.
  About 10 mutations a request, with a request every few seconds, stays under the limit.
- The API cannot set a view's grouping or sorting.
- Linking a spec or ticket as a sub-issue can add it to the parent's project by itself.
  After you link sub-issues, remove each project item without the `roadmap` label with `deleteProjectV2Item`. The issue stays.
  Until then, the `label:roadmap` view filters hide it.
