---
name: handover
description: Hand work over to a new session outside this one - an orchestrator to build an effort, or a fresh session to continue - and confirm it started. Use when a session is ready to hand over, or when another skill says to.
argument-hint: "What the new session does (optional)"
---

# Handover

A **handover** starts another session, usually outside this one, that carries the work on from the repository alone: an orchestrator that builds an effort, or a fresh session that continues the thinking. It can happen at any point and from any session. The new session knows only what the repository tells it, so this session leaves everything there first.

A **handoff** is the document the new session starts from; the **handoff** skill writes it. The handover is the whole move: get ready, write the starting prompt, start the session, and confirm it started.

## Parameters

Each comes from the Defaults table, where a project's row overrides the global one. A parameter is unset when it has no row or its row says `none`.

- `<worktree-tool>`: how a new worktree is made. Unset, use `git worktree add`.
- `<session-host>`: where new agent sessions open. Unset, use this session.
- `<agent-to-start>`: the command that starts a new agent session. Unset, use this session's harness.

## 1. Get ready

Check each item, and fix what isn't true yet:

- **The worktree exists.** The work gets its own worktree and branch at the latest now, made with the **treehouse** skill when `<worktree-tool>` is Treehouse, else with `git worktree add` on a new branch with no upstream until its first push, since a branch that tracks the default branch makes a bare `git push` target it. Branch from `origin/<default>`, or from the local default branch when the work builds on commits there that aren't pushed. Uncommitted changes on the default branch that belong to the work move into it, and only those; the rest stay where they are.
- **Every input only the maintainer has is collected** while they are here: answers, accounts, choices. Secrets stay out of chat and files; the handoff says where they live.
- **The handoff is written** with the **handoff** skill. Beyond what that skill asks, it names the worktree and branch, the spec and tickets, and whether the new session can reach this one. This session is unreachable when it can't receive messages, as with a desktop-app session or any session the session host can't prompt, and then the handoff tells the new session to decide open questions itself and list them in the pull request.
- **Everything is committed and pushed**: the worktree is clean and its branch matches its remote. Run each commit and each push as its own call, because a deny rule that matches anything else in a chain blocks the whole chain. After an interrupted or rejected call, check the log before retrying, because the commit or push may have landed anyway.
- **Tracker items exist** for the spec and tickets the handoff names: issues on a hosted tracker, or files in the effort's folder on a local one.
- **QA is settled** for an effort in a project whose instructions opt in to QA by the maintainer. The spec says either "QA: blocking" or that QA is non-blocking, the default. When it doesn't, ask the maintainer while they are here, and write the answer into the spec.

Until the new session starts, this session stays on its own checkout and branch, so the maintainer's thread stays where it is: write into the worktree by absolute path and run git there with `git -C <worktree>`.

Done when every item holds.

## 2. Write the starting prompt

The starting prompt is **one line**, and it starts the new session on the handoff:

| New session | Starting prompt |
|---|---|
| Orchestrator for an effort | `/orchestrate-with-handoff <path to the handoff>` |
| Anything else, such as more thinking | `Continue from the handoff at <path to the handoff>.` |

Everything else the new session needs, such as changes to the plan and rules, goes in the handoff, because a prompt pasted in over several lines arrives as pasted text rather than a command, and its skill never starts.

Codex starts skills with `$` instead of `/`: when the new session runs Codex, write `$orchestrate-with-handoff`.

The new session takes the prompt as the maintainer's go-ahead and starts work without asking for one. So the handoff settles every decision this session can, and carries the inputs it collected from the maintainer.

## 3. Start it

- **When `<session-host>` is Herdr**, hand over with the **handover-to-herdr** skill, passing the worktree, the topic, the new session's role, and the starting prompt. When it can't reach Herdr, the next branch applies.
- **Otherwise**, offer the maintainer two ways and take the one they pick: move this session into the worktree and run the starting prompt here, or print the prompt in a fenced block to paste into a new `<agent-to-start>` session started in the worktree.

## 4. Confirm it started

The handover is done when the new session is working on the prompt: **handover-to-herdr** reports it working, the maintainer says it started, or this session runs it here. The handover is fire-and-forget: tell the maintainer where it runs, then stop. The new session's deliverable, such as an orchestrator's pull request, is how the maintainer hears back.
