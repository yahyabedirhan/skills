---
name: handover
description: Hand work over to a new session outside this one - an orchestrator to build an effort, or a fresh session to continue - and confirm it started. Use when a session is ready to hand over, or when another skill says to.
argument-hint: "What the new session does (optional)"
---

# Handover

A **handover** starts another session, usually outside this one, to carry on the work: an orchestrator that builds an effort, or a fresh session that continues the thinking. Hand over at any point, from any session. The new session knows only what the repository holds, and it takes its starting prompt as the maintainer's go-ahead, so settle in the handoff every decision this session can. The handover is fire-and-forget: the new session's deliverable, such as an orchestrator's pull request, is how the maintainer hears back.

## Parameters

- `<worktree-tool>`: the tool that makes and frees worktrees, e.g. `treehouse`, or plain git worktrees.
- `<session-host>`: where agent sessions run, e.g. `herdr`, Claude Code Desktop, Codex Desktop.
- `<agent-to-start>`: the command that starts a new agent session, e.g. `claude` or `codex`, with its flags.

## Flow

1. **Give the work its own worktree and branch,** and move into it the uncommitted changes on the default branch that belong to the work, leaving the rest where they are. Until the new session starts, keep this session on its own checkout and branch, so the maintainer's checkout isn't switched under them: write into the worktree by absolute path, and run git there with `git -C <worktree>`.
   - **When it has none yet:** make them with `<worktree-tool>`. Branch from the remote default branch, or from the local default branch when the work builds on commits there that aren't pushed.
2. **Collect every input only the maintainer has** for the handoff while they are here: answers, accounts, choices. Keep secrets out of chat and files, and have the handoff say where they live.
   - **For an effort in a project whose instructions opt in to QA by the maintainer:** the spec says either "QA: blocking" or that QA is non-blocking, which is the default. When it says neither, ask the maintainer whether QA blocks, and write the answer into the spec.
3. **Write the handoff** with `/handoff`. It also names the worktree and branch, the spec and tickets, and whether the new session can reach this one.
   - **When the new session can't reach this one:** a desktop-app session, or any session `<session-host>` can't prompt, can't receive messages. Have the handoff tell the new session to decide open questions itself and list them in the pull request.
4. **Make sure the tracker holds the spec and tickets** the handoff names: issues on a hosted tracker, or files in the effort's folder on a local one.
5. **Commit and push everything** in the worktree, until it is clean and its branch matches its remote.
   - Run each commit and each push as its own call, because a deny rule that matches anything else in a chain blocks the whole chain.
   - **After an interrupted or rejected call:** check the log before retrying, because the commit or push may have landed anyway.
6. **Write the starting prompt as one line** that starts the new session on the handoff. A prompt of several lines arrives as pasted text rather than a command, so its skill never starts; put everything else in the handoff.

   | New session | Starting prompt |
   |---|---|
   | Orchestrator for an effort | `/orchestrate-with-handoff <path to the handoff>` |
   | Anything else, such as more thinking | `Continue from the handoff at <path to the handoff>.` |

   - **When `<agent-to-start>` is Codex:** write `$orchestrate-with-handoff`, since Codex starts skills with `$`.
7. **Start `<agent-to-start>` in `<session-host>`**, passing the worktree, the topic, the new session's role, and the starting prompt.
8. **Confirm it is working on the prompt**: `<session-host>` reports it working, the maintainer says it started, or this session runs it here. Tell the maintainer where it runs, and stop.
