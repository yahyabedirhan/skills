# Effort Lifecycle

How one **effort** (a feature, a new app, a refactor, a re-architecture) travels from an idea to a merged pull request. It builds on Matt Pocock's skills ([mattpocock/skills](https://github.com/mattpocock/skills)) for the thinking, and on the orchestrate skills for the building. Routine upkeep (data edits, small fixes) doesn't need any of this: it runs in the current checkout.

An effort passes through five phases in one worktree on one branch:

```text
START      decide the worktree once; everything after follows it
THINKING   settle what to build; leave a spec, tickets, and a handoff
HANDOVER   the thinking session commits everything and starts a fresh orchestrator
BUILD      orchestrate the tickets through delegates; open the pull request
CLOSE      after the merge, remove the worktree and the branch
```

There are two paths through it. The Herdr path automates every step between phases; the plain path runs anywhere, with the user carrying the handover.

```text
                START                    HANDOVER                  BUILD
Herdr path      init-effort-with-herdr   orchestrate-with-herdr    orchestrate-with-handoff
                treehouse worktree,      new "Orchestrator" tab,     → orchestrate-effort
                Herdr workspace,         agent started, prompted
                thinking agent started

Plain path      init-effort              the thinking session      orchestrate-with-handoff
                the environment's own    prints a handover prompt;   → orchestrate-effort
                worktree, or git         the user pastes it into
                worktree                 a new session
```

## Start

The worktree is decided here, before any thinking, so the spec, tickets, and handoff are born on the effort's branch rather than on the default branch. The build later runs in the same worktree.

## Thinking

```text
/grill-with-docs <idea>   sharpen it; terms land in CONTEXT.md, decisions in ADRs
  /prototype              when a question needs a runnable answer; the user reviews it
/to-spec                  the thread becomes a spec
/to-tickets               tracer-bullet tickets, each naming what blocks it
```

Run it in one unbroken context window, so the spec and tickets build on the same reasoning. On a local tracker the artifacts land in an **effort folder**, `.scratch/<effort>/` with `spec.md` and `issues/`.

## Handover

The thinking session owns the clean ending: it writes a **handoff** in the repository (by convention `.handoff/<date>-<effort>.md`) that points at the spec and tickets and names the thinking session, commits and pushes everything, and then hands over with a short **handover prompt** that starts the orchestrator on the handoff. The thinking session then stops, and stays open for reference.

## Build

The orchestrator reads the handoff, shows the plan with `/show-me`, delegates each ticket to a sub-agent that builds it the way `/implement` does (`/tdd`, checks, `/code-review`), commits each one, and ends with `/to-pr`. It follows the `orchestrating` discipline throughout.

## Close

After the user merges the pull request, the effort's worktree and branch go, in the way they were created: on the Herdr path, `init-effort-with-herdr` holds the steps.

## Why two sessions

The thinking session fills its context with debate, dead ends, and prototype output. The builder needs none of it: the spec, tickets, and handoff carry the conclusions. Starting fresh keeps the orchestrator sharp for the long run, and each ticket's delegate starts even fresher, from one ticket file.
