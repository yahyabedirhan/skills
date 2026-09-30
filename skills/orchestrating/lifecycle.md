# Effort Lifecycle

How one **effort**, such as a feature, a new app, a refactor or a re-architecture, travels from an idea to a merged pull request. The thinking runs on `/grilling`, `/prototype`, `/tdd` and `/code-review` from Matt Pocock's [mattpocock/skills](https://github.com/mattpocock/skills), and on this repo's forks of his `handoff`, `to-spec`, `to-tickets` and `setup-matt-pocock-skills`, which replace the upstream four; the last is forked as `/set-up-project`. The building runs on the orchestrate skills. Run routine upkeep, such as data edits and small fixes, in the current checkout without any of this.

An effort passes through five phases in one worktree on one branch:

```text
START      decide the worktree once; everything after follows it
THINKING   settle what to build; leave a spec, tickets, and a handoff
HANDOVER   the session commits everything and starts a fresh orchestrator
BUILD      orchestrate the tickets through delegates; open the pull request
CLOSE      the user approves; the agent merges, follows up, and cleans up
```

The session host, the program where new agent sessions open, decides which of two paths an effort takes. When the host is `herdr`, take the host path: `/handover-to-herdr` automates every step between phases. Otherwise take the plain path, which runs anywhere: this session carries on, or the user pastes each starting prompt.

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

`/init-effort` names the effort and creates its branch and worktree. The worktree is decided here, before any thinking, so the spec, tickets, and handoff are written on the effort's branch rather than on the default branch. The build later runs in the same worktree.

For a brand-new project it first creates the repository, and the project's first effort then starts like any other. It writes the idea into a handoff in the worktree and starts the thinking session on it.

## Thinking

```text
grilling     sharpen the idea, one round of questions at a time
  prototype  when a question needs a runnable answer; the user reviews it
to-spec      the thread becomes a spec
to-tickets   tracer-bullet tickets, each naming what blocks it
handover     hand over to an orchestrator
```

The starting prompt names these skills and the agent loads each one itself: the user types no slash command. Run it in one unbroken context window, so the spec and tickets build on the same reasoning. [folder-standard.md](folder-standard.md) says where the spec and tickets land.

## Handover

The session that hands over finishes its own work cleanly, through `/handover`. A handover can run from any session at any point, not only at the end of the thinking: a desktop-app session on the default branch can hand an effort to an orchestrator in the session host without leaving its own checkout. It gets the session ready, starts the new session on the handoff with a one-line prompt, and confirms it started. The handing session then stops, and stays open for reference.

## Build

`/orchestrate-with-handoff` picks up the handoff and runs `/orchestrate-effort`, which delegates the tickets to sub-agents in parallel, each building its ticket with `/implement` in its own worktree, integrates each ticket as its own commit, and opens the pull request with `/to-pr` after one branch review. In a project that opts in to QA, a ticket the user can try stays open and goes to them with try-this steps; the merge waits for it only when the spec says "QA: blocking".

## Close

The user reviews and approves the pull request: that is their only step. The agent then merges it and closes the effort with `/close-effort`, whether it is the orchestrator that delivered or any session told the pull request merged or to merge it. Workspaces and agent sessions stay open for the user to close.

## Why two sessions

The thinking session fills its context with debate, dead ends, and prototype output. The builder needs none of it: the spec, tickets, and handoff carry the conclusions. Starting fresh leaves the orchestrator's context free for the long run, and each ticket's delegate starts even fresher, from one ticket file.
