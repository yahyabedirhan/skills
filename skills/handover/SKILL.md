---
name: handover
description: Hand work over to a new session outside this one - an orchestrator to build an effort, or a fresh session to continue - and confirm it started. Use when a session is ready to hand over, or when another skill says to.
argument-hint: "What the new session does (optional)"
---

# Handover

A **handover** starts another session, outside this one, that carries the work on from the repository alone: an orchestrator that builds an effort, or a fresh session that continues the thinking. It can happen at any point and from any session. The new session knows only what the repository tells it, so this session leaves everything there first.

A **handoff** is the document the new session starts from; the **handoff** skill writes it. The handover is the whole move: get ready, write the starting prompt, start the session through a mechanism, and confirm it started.

## 1. Get ready

Check each item, and fix what isn't true yet:

- **The worktree exists.** The work gets its own worktree and branch at the latest now, made with the project's worktree tool (its instructions name it; Treehouse by default, else `git worktree add`). Uncommitted changes on the default branch that belong to the work move into it, and only those: the rest stay where they are.
- **The handoff is written**, with the **handoff** skill. Beyond what that skill asks, it names the worktree and branch, the spec and tickets, and whether the new session can reach this one.
- **Everything is committed and pushed**: `git status` is clean in the worktree and its branch matches its remote.
- **Tracker items exist** for the spec and tickets the handoff names.

Done when every item holds.

## 2. Write the starting prompt

The prompt starts the new session on the handoff:

| New session | Starting prompt |
|---|---|
| Orchestrator for an effort | `/orchestrate-with-handoff <path to the handoff>` |
| Anything else, such as more thinking | `Continue from the handoff at <path to the handoff>.` |

Codex starts skills with `$` instead of `/`: when the new session runs Codex, write `$orchestrate-with-handoff`.

## 3. Start it through a mechanism

- **Herdr**, the default: when `herdr status` reaches a server, hand over with the **handover-to-herdr** skill, passing the worktree, the topic, the new session's role, and the starting prompt.
- **Paste**, the fallback: print the starting prompt in a fenced block, and ask the maintainer to start their preferred agent in the worktree and paste it.

## 4. Confirm it started

The handover is done when the new session is working on the prompt: Herdr reports it `working`, or the maintainer says it started. Tell the maintainer where it runs, then stop: this session doesn't wait on the new one.
