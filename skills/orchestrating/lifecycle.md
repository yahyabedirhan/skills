# Effort Lifecycle

How one **effort** (a feature, a new app, a refactor, a re-architecture) travels from an idea to a merged pull request. The thinking builds on Matt Pocock's skills from [mattpocock/skills](https://github.com/mattpocock/skills) (`grilling`, `prototype`, `tdd`, `code-review`) and on forks of his `handoff`, `to-spec`, `to-tickets` and `setup-matt-pocock-skills` (as **set-up-project**), which replace the upstream four; the building runs on the orchestrate skills. Routine upkeep (data edits, small fixes) doesn't need any of this: it runs in the current checkout.

An effort passes through five phases in one worktree on one branch:

```text
START      decide the worktree once; everything after follows it
THINKING   settle what to build; leave a spec, tickets, and a handoff
HANDOVER   the session commits everything and starts a fresh orchestrator
BUILD      orchestrate the tickets through delegates; open the pull request
CLOSE      the user says "go"; the agent merges, follows up, and cleans up
```

There are two paths through it, chosen by the session host, where new agent sessions open (a parameter of **init-effort**, **handover** and **close-effort**). The host path, when it's Herdr, automates every step between phases through the **handover-to-herdr** skill; the plain path runs anywhere, with this session carrying on or the user pasting each starting prompt. The worktree comes from the **treehouse** skill when the worktree tool is Treehouse, else `git worktree add`.

```text
                START                          HANDOVER                        BUILD
Host path       init-effort                    handover                        orchestrate-with-handoff
                worktree tool;                 → handover-to-herdr:            → orchestrate-effort
                  → handover-to-herdr:           new "Orchestrator" tab,
                  "Thinking" tab,                agent started, prompted
                  agent started, prompted

Plain path      init-effort                    handover                        orchestrate-with-handoff
                worktree tool,                 runs the prompt here,           → orchestrate-effort
                or git worktree;               or prints it; the user
                thinks here, or prints         pastes it into a new
                the starting prompt            session
```

## Start

**init-effort** names the effort and creates its branch and worktree. The worktree is decided here, before any thinking, so the spec, tickets, and handoff are born on the effort's branch rather than on the default branch. The build later runs in the same worktree.

For a brand-new project it first creates the repo: a folder under the maintainer's projects folder, a README and licence, the [folder standard](folders.md)'s setup, a first commit, and a GitHub repo (public or private, asked each time). The project's first effort then starts like any other.

It writes the idea into a handoff in the worktree and starts the thinking session on it with a one-line prompt: in a `Thinking` tab of the session host, else in its own session or a pasted prompt.

## Thinking

```text
grilling     sharpen the idea, one round of questions at a time
  prototype  when a question needs a runnable answer; the user reviews it
to-spec      the thread becomes a spec
to-tickets   tracer-bullet tickets, each naming what blocks it
handover     hand over to an orchestrator
```

The starting prompt names these skills and the agent loads each one itself: the user types no slash command. Run it in one unbroken context window, so the spec and tickets build on the same reasoning. On a local tracker the artifacts land in an **effort folder**, `.efforts/<effort>/` with `spec.md` and `issues/`, per the [folder standard](folders.md).

## Handover

The session handing over owns the clean ending, through the **handover** skill. A handover can run from any session at any point, not only at the end of the thinking: a desktop-app session on the default branch can hand an effort to an orchestrator in the session host without leaving its own checkout. It checks the session is ready: the worktree exists, a **handoff** is written in the repository by the **handoff** skill (`.handoff/<date>-<topic>.md`, per the [folder standard](folders.md)), everything is committed and pushed, and the tracker items exist. It then writes a short **starting prompt** that starts the new session on the handoff, starts that session in the session host (else here, or through a pasted prompt), and confirms it started. The handing session then stops, and stays open for reference.

## Build

The orchestrator reads the handoff, shows the plan with `/show-me`, delegates the unblocked tickets in parallel to sub-agents, each in its own worktree, building it the way `/implement` does (`/tdd`, checks, a review at the depth the orchestrator sets), integrates and commits each one, and ends with one branch review and `/to-pr`. In a project that opts in to QA, a ticket the user can try stays open and goes to them with try-this steps; the merge waits for it only when the spec says "QA: blocking". It follows the `orchestrating` discipline throughout.

## Close

The user reviews the pull request and says "go": that is their only step. The agent then merges it and closes the effort with the **close-effort** skill, whether it is the orchestrator that delivered or any session told the pull request merged or to merge it. It reads the pull request's *Things to be aware of* first, runs the post-merge follow-ups, carries unfinished work into the next effort's tickets, leaves QA tickets open for the user, closes the tracker, removes only branches and worktrees proven merged, and closes the effort's workspaces in the session host. It returns its own worktree last, from a shell the host opens outside it; with no session host, that one step is the user's.

## Why two sessions

The thinking session fills its context with debate, dead ends, and prototype output. The builder needs none of it: the spec, tickets, and handoff carry the conclusions. Starting fresh keeps the orchestrator sharp for the long run, and each ticket's delegate starts even fresher, from one ticket file.
