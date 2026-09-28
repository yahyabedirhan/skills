---
name: init-effort
description: Start a new effort (a feature, a new app, a refactor, a re-architecture) on its own branch in a new worktree, and run its thinking session there, ending with a handover prompt for the orchestrator.
argument-hint: "The idea, in a sentence or a paragraph"
disable-model-invocation: true
---

# Init Effort

An **effort** is work big enough for its own branch and pull request: a feature, a new app, a refactor, a re-architecture. Routine upkeep (data edits, small fixes) runs in the current checkout and doesn't need this skill; the project's instructions may list what counts as routine there.

The effort's whole life happens in the worktree this skill creates: the thinking now, the build later.

## 1. Name the effort

From the idea, propose a short kebab-case **effort name** and a branch named the project's way (by default `<area>/<effort>`), and confirm both with the user.

## 2. Create the worktree

Create a new worktree on the new branch, based on the latest default branch: with your environment's own worktree feature when it has one (the session moves into the worktree), else:

```bash
git fetch origin
git worktree add --no-track -b <branch> ../<repo>-<effort> origin/<default-branch>
```

`--no-track` keeps the default branch from becoming the new branch's upstream; the first push sets the real one with `git push -u origin <branch>`.

When the session cannot move into the new worktree, print the idea with this skill's steps 3 and 4 as a prompt for the user to paste into a new session there, and stop.

Done when this session runs inside the new worktree on the new branch.

## 3. Think

The thinking runs here, in this one context window: the user drives it with `/grill-with-docs <idea>`, a `/prototype` when a question needs a runnable answer, then `/to-spec` and `/to-tickets`. Suggest each next step when the previous one ends.

## 4. Hand over

When the tickets are written, hand the effort to an orchestrator with the **handover** skill: it writes the handoff, commits and pushes, and starts the orchestrator with a one-line prompt.

Then stop: this session's work is done, and it stays available for reference.
