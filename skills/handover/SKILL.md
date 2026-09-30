---
name: handover
description: Hand work over to a new session outside this one - an orchestrator to build an effort, or a fresh session to continue - and confirm it started. Use when a session is ready to hand over, or when another skill says to.
argument-hint: "What the new session does (optional)"
---

# Handover

A **handover** starts another session, usually outside this one, to carry on the work: an orchestrator that builds an effort, or a fresh session that continues the thinking. Hand over at any point, from any session. The new session knows only what the repository holds, and it takes its starting prompt as the maintainer's go-ahead, so settle in the handoff every decision this session can. The handover is fire-and-forget: the new session's deliverable, such as an orchestrator's pull request, is how the maintainer hears back.

[readiness-checklist.md](readiness-checklist.md) holds how to get the worktree, the maintainer's inputs, the handoff and the commits ready. Read it before step 1.

## Parameters

- `<worktree-tool>`: the tool that makes a new worktree. When it is Treehouse, use `/treehouse`. Default: `git worktree add`, with no upstream on the new branch until its first push, since a branch that tracks the default branch makes a bare `git push` target it.
- `<session-host>`: where the new session opens. When it is Herdr, use `/handover-to-herdr`; when that skill can't reach Herdr, use the default. Default: offer the maintainer two ways and take the one they pick: move this session into the worktree and run the starting prompt here, or print the prompt in a fenced block to paste into a new `<agent-to-start>` session started in the worktree.
- `<agent-to-start>`: the command that starts a new agent session. Default: this session's harness.

## Flow

1. **Make the worktree and branch** with `<worktree-tool>` if the work has none yet, and move into it the uncommitted changes that belong to the work.
2. **Collect every input only the maintainer has** for the handoff while they are here: answers, accounts, choices, and for an effort in a project that opts in to QA, whether QA blocks.
3. **Write the handoff** with `/handoff`. It also names the worktree and branch, the spec and tickets, and whether the new session can reach this one.
4. **Make sure the tracker holds the spec and tickets** the handoff names: issues on a hosted tracker, or files in the effort's folder on a local one.
5. **Commit and push everything** in the worktree.
6. **Write the starting prompt as one line** that starts the new session on the handoff. A prompt of several lines arrives as pasted text rather than a command, so its skill never starts; put everything else in the handoff.

   | New session | Starting prompt |
   |---|---|
   | Orchestrator for an effort | `/orchestrate-with-handoff <path to the handoff>` |
   | Anything else, such as more thinking | `Continue from the handoff at <path to the handoff>.` |

   When `<agent-to-start>` is Codex, write `$orchestrate-with-handoff`, since Codex starts skills with `$`.
7. **Start `<agent-to-start>` in `<session-host>`**, passing the worktree, the topic, the new session's role, and the starting prompt.
8. **Confirm it is working on the prompt**: `<session-host>` reports it working, the maintainer says it started, or this session runs it here. Tell the maintainer where it runs, and stop.
