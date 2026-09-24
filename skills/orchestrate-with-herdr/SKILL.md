---
name: orchestrate-with-herdr
description: Hand a finished thinking session over to a new orchestrator in a Herdr tab in the same workspace. Use when a thinking session running inside Herdr has written its tickets and is ready to hand over.
argument-hint: "Path to the handoff document or the effort folder (optional)"
---

# Orchestrate With Herdr

The Herdr path's handover, run by the thinking session at its end: it finishes its own work, then starts a fresh orchestrator beside it, in the same worktree. Herdr's daily operations are in [herdr.md](../init-effort-with-herdr/herdr.md).

Check that this session runs inside Herdr (`HERDR_ENV=1`). If not, do step 1, print the handover prompt from step 2 for the user to paste into a new session in this worktree, and stop.

## 1. Finish the thinking session

The orchestrator starts from the repository alone, so this session leaves everything there:

1. Write the **handoff** in the repository (the project's handoff folder, else `.handoff/<date>-<effort>.md`): the spec and tickets by path, what the builder should know that they don't, the skills to use, and this session (its Herdr tab and workspace, and its session name or id). Leave out secrets.
2. Commit the spec, tickets, handoff, and every other change from this session, and push the branch.

Done when `git status` is clean and the branch matches its remote.

## 2. Start the orchestrator

1. Mark this tab settled: append ` [settled]` to its current label, unless it already ends with it. The session's work is done, and the marker tells the user the tab is only a record now.
2. Create a tab labelled `<effort> · Orchestrator · <harness>` in this workspace, with this worktree as its directory, without taking focus; the harness is the agent you start next.
3. Start the user's preferred agent in it (from their instructions; default `claude`), named `<effort>-orchestrator`.
4. Send it the **handover prompt**:

   ```text
   /orchestrate-with-handoff <path to the handoff>
   Worktree: <path>   Branch: <branch>
   Thinking session: Herdr tab "<its settled label>" in workspace <workspace>, <session name or id>
   ```

   Codex starts skills with `$` instead of `/`: when the receiving agent is Codex, write `$orchestrate-with-handoff`.

5. Wait until Herdr reports it `working`, then tell the user where the orchestrator runs.

Then stop. This tab stays open as the thinking session's record.
