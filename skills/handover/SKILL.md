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

- **The worktree exists.** The work gets its own worktree and branch at the latest now, made with the project's worktree tool (its instructions name it; Treehouse by default, else `git worktree add`). Branch from `origin/<default>`, or from the local default branch when the work builds on commits there that aren't pushed. Uncommitted changes on the default branch that belong to the work move into it, and only those: the rest stay where they are.
- **Every input only the maintainer has is collected** while they are here: answers, accounts, choices. Secrets stay out of chat and files; the handoff says where they live.
- **The handoff is written**, with the **handoff** skill. Beyond what that skill asks, it names the worktree and branch, the spec and tickets, and whether the new session can reach this one. A session that can't receive messages (a desktop-app session, or any session outside Herdr) says so, and tells the new session to decide open questions itself and list them in the pull request.
- **Everything is committed and pushed**: `git status` is clean in the worktree and its branch matches its remote. Run each commit, and the push, as its own call, never chained with a deletion, because a deny rule that matches the deletion blocks the whole chain; after an interrupted or rejected call, check `git log` before retrying, because a chain can stop halfway.
- **Tracker items exist** for the spec and tickets the handoff names: issues, or files on a local tracker.

This session stays on its own checkout and branch throughout, so the maintainer's thread stays where it is: write into the worktree by absolute path and run git there with `git -C <worktree>`.

Done when every item holds.

## 2. Write the starting prompt

The starting prompt is **one line**, and it starts the new session on the handoff:

| New session | Starting prompt |
|---|---|
| Orchestrator for an effort | `/orchestrate-with-handoff <path to the handoff>` |
| Anything else, such as more thinking | `Continue from the handoff at <path to the handoff>.` |

Everything else the new session needs goes in the handoff: the worktree and branch, whether this session is reachable, changes to the plan, rules. A prompt pasted in over several lines arrives as pasted text rather than a command, so its skill never starts.

Codex starts skills with `$` instead of `/`: when the new session runs Codex, write `$orchestrate-with-handoff`.

The new session takes the prompt as the maintainer's go-ahead and starts work without asking for one. So the handoff settles every decision this session can, and carries the maintainer's inputs from step 1.

## 3. Start it through a mechanism

- **Herdr**, the default: when `herdr status` reaches a server, whether or not this session runs in a Herdr pane, hand over with the **handover-to-herdr** skill, passing the worktree, the topic, the new session's role, and the starting prompt.
- **Paste**, the fallback: print the starting prompt in a fenced block, and ask the maintainer to start their preferred agent in the worktree and paste it.

## 4. Confirm it started

The handover is done when the new session is working on the prompt: Herdr reports it `working`, or the maintainer says it started. Tell the maintainer where it runs, then stop. The handover is fire-and-forget: this session doesn't wait on the new one, message it, or check on it; the new session's deliverable (for an orchestrator, its pull request) is how the maintainer hears back.
