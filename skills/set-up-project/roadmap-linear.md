# Roadmap

This page says how <project> keeps its roadmap in Linear, above the agent specs and tickets on GitHub.
Its presence puts the project in roadmap mode: read it before you plan, start, deliver or settle work here.
The skills speak of the roadmap in shared terms, and this page maps each one to Linear:

- **The roadmap:** the Linear project below.
- **Roadmap issue:** the Linear issue that a change belongs to.
- **Release group:** a release milestone, and its **release note** the milestone's description.

The [`/set-up-project`](https://github.com/yahyabedirhan/skills/tree/main/skills/set-up-project) skill wrote it.

_`/set-up-project` fills in each `<slot>`, removes each line that does not apply, and removes every note in italics like this one._

## Planning layers

| Layer | What it holds | Who reads it |
|---|---|---|
| The notes | History and thinking, as `docs/agents/notes.md` says. | The maintainer, and agents that need the history |
| Linear | The roadmap: what to build and the high-level how, the release groups, the status, screenshots and diagrams. | The maintainer |
| GitHub issues | Agent specs and tickets that are ready to build, planned in waves. | Agents |
| Codebase docs | How the project works today. | Everyone |

- Move work from the notes to Linear, or from Linear to GitHub, only when the maintainer says so.
- Give every change that affects released content a Linear issue: a feature, a bugfix or a chore, also work that an agent finds.
- Size a Linear issue to about one pull request. A Linear issue and the GitHub issues for it do not map one to one.
- Make every change in Linear yourself, so the maintainer only reads and decides there.

## Linear

- **Team:** `<team>`. Reach it through the Linear MCP server, `mcp__linear__*`.
- **Project:** `<project>`.
- **Repo label:** give every issue the label `<repo>` from the team's `Repo` label group.
- **Release milestones:** a milestone named `Release <version>` holds each release group, as `docs/agents/releasing.md` says.
  When the release ships, rewrite the milestone's description as its release note.
  _For a project that holds several repos, name each milestone `<repo> <version>`, and only for a repo that publishes versions._
  _When the project publishes no versions, remove this line._

## Status flow

1. **Todo:** the maintainer decided the work, and no effort builds it yet.
2. **In Progress:** the orchestrator moves the issue here when the effort starts.
3. **`<beta label>`:** add this label when the pull request merges to beta, and keep the status.
4. **Done:** move the issue here when the release that holds it reaches production.

_When the project ships on each merge, with no beta, remove step 3: the issue goes to Done when the merge and its follow-ups are done._

## Maintainer-only steps

A step that only the maintainer can do, such as a manual check, a login, a payment or a decision, goes to Linear as its own issue.

- Assign it to the maintainer.
- Give it the type label `QA` for a check, or `Decision` for a decision.
- Put it in the milestone it blocks, and mark it as blocking the issue it gates.
- Give it the build and how to reach it, numbered try-this steps with known risks marked, and screenshots.
- Say what to do when done: move it to Done if it is good, or comment with the step number and what they saw.

## Linear issues

Write each Linear issue for the maintainer:

- Keep sentences short, in the active voice.
- Use one word for one thing, every time.
- Number the steps.
- Put a warning in the step it belongs to, as a plain sentence. WARNING, CAUTION and NOTE blocks belong to GitHub issues, which use the full rules.
- Put agent detail, such as file lists, plans and logs, in a collapsed section at the end:

```text
+++ Agent notes

Details for agents go here.

+++
```

## Links between layers

- Start a spec from the Linear issue the conversation is about. When the conversation names none, ask the maintainer which one, and create one only when they say so.
- Start the description of each GitHub spec, ticket and pull request with a `Linear:` line that links its Linear issue. Keep the title free of the link.
- Link the GitHub spec and the pull request in the Linear issue's description the same way.
- Comment on the Linear issue when its spec is published, with the spec's link.
- Comment on it when the effort starts, with the plan, and again at delivery, with the pull request, screenshots and a status diagram.
