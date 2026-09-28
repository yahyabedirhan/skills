# Effort Lifecycle

How one **effort** (a feature, a new app, a refactor, a re-architecture) travels from an idea to a merged pull request. It builds on Matt Pocock's skills ([mattpocock/skills](https://github.com/mattpocock/skills)) for the thinking, and on the orchestrate skills for the building. Routine upkeep (data edits, small fixes) doesn't need any of this: it runs in the current checkout.

An effort passes through five phases in one worktree on one branch:

```text
START      decide the worktree once; everything after follows it
THINKING   settle what to build; leave a spec, tickets, and a handoff
HANDOVER   the session commits everything and starts a fresh orchestrator
BUILD      orchestrate the tickets through delegates; open the pull request
CLOSE      after the merge, remove the worktree and the branch
```

There are two paths through it. The Herdr path automates every step between phases; the plain path runs anywhere, with the user carrying the handover. The **handover** skill picks the path's mechanism itself: Herdr whenever `herdr status` reaches a server, else a prompt the user pastes.

```text
                START                    HANDOVER                  BUILD
Herdr path      init-effort-with-herdr   handover                  orchestrate-with-handoff
                treehouse worktree,        → handover-to-herdr:      → orchestrate-effort
                Herdr workspace,           new "Orchestrator" tab,
                thinking agent started     agent started, prompted

Plain path      init-effort              handover                  orchestrate-with-handoff
                the environment's own      prints the starting       → orchestrate-effort
                worktree, or git           prompt; the user pastes
                worktree                   it into a new session
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

Run it in one unbroken context window, so the spec and tickets build on the same reasoning. On a local tracker the artifacts land in an **effort folder**, `.efforts/<effort>/` with `spec.md` and `issues/`, per the [folder standard](folders.md).

## Handover

The session handing over owns the clean ending, through the **handover** skill. A handover can run from any session at any point, not only at the end of the thinking: a desktop-app session on the default branch can hand an effort to a Herdr orchestrator without leaving its own checkout. It checks the session is ready: the worktree exists, a **handoff** is written in the repository by the **handoff** skill (`.handoff/<date>-<topic>.md`, per the [folder standard](folders.md)), everything is committed and pushed, and the tracker items exist. It then writes a short **starting prompt** that starts the new session on the handoff, starts that session through a mechanism (**handover-to-herdr** by default, else a pasted prompt), and confirms it started. The handing session then stops, and stays open for reference.

## Build

The orchestrator reads the handoff, shows the plan with `/show-me`, delegates the unblocked tickets in parallel to sub-agents, each in its own worktree, building it the way `/implement` does (`/tdd`, checks, a review at the depth the orchestrator sets), integrates and commits each one, and ends with one branch review and `/to-pr`. It follows the `orchestrating` discipline throughout.

## Close

After the user merges the pull request, the effort's worktree and branch go, in the way they were created: on the Herdr path, `init-effort-with-herdr` holds the steps.

## Why two sessions

The thinking session fills its context with debate, dead ends, and prototype output. The builder needs none of it: the spec, tickets, and handoff carry the conclusions. Starting fresh keeps the orchestrator sharp for the long run, and each ticket's delegate starts even fresher, from one ticket file.
