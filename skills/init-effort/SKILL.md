---
name: init-effort
description: Start a new effort (a feature, a new app, a refactor, a re-architecture) on its own branch and worktree, or a brand-new project in its own repo, and start its thinking session there.
argument-hint: "The idea, in a sentence or a paragraph"
disable-model-invocation: true
---

# Init Effort

An **effort** is work big enough for its own branch and pull request: a feature, a new app, a refactor, a re-architecture. Routine upkeep (data edits, small fixes) runs in the current checkout and doesn't need this skill; the project's instructions may list what counts as routine there.

The effort's whole life happens in the worktree this skill creates: the thinking now, the build later. This skill writes only into that worktree and, for a new project, the new repo: the repository this session was started in stays untouched.

## Parameters

Each comes from the Defaults table in the environment's instructions, where a project's table overrides the global one for that project. Unset means no row, or `none`.

- `<worktree-tool>`: how a new worktree is made, used through its how-to skill (named for the tool). Unset, or that skill not installed: `git worktree add`.
- `<session-host>`: where new agent sessions open, used through its how-to skill `handover-to-<session-host>`. Unset, that skill not installed, or the host out of reach: this session.
- `<agent-to-start>`: the command and flags that start a new agent session. Unset: the command of this session's harness.

## 1. Decide where it lives

From the idea, tell which it is:

- **An effort in an existing repo**: the current repository, or one the idea names.
- **A new project**: the idea is for something that has no repo yet.

When it isn't clear, ask. Done when the target repo is known, or the idea is a new project.

## 2. Name it

Propose a short kebab-case **effort name** and a branch named the project's way (by default `<area>/<effort>`), and confirm both with the maintainer.

For a new project, first propose a few **project names** and confirm one. When the idea comes with a reference project, the names don't echo it. The project's first effort then gets its own name and branch as above.

## 3. Create a new project

Only for a new project; otherwise skip to step 4.

The project goes in the maintainer's **projects folder**, named in their instructions. When their instructions don't name one, ask for it, and suggest adding it there. Check that `<projects folder>/<name>` doesn't exist and that `gh repo view <name>` finds no repo.

Ask, every time, whether the GitHub repo is **public or private**, and which licence it takes (recommend MIT in the maintainer's name). Then:

1. `mkdir <projects folder>/<name>` and `git -C <path> init -b main`.
2. Write a `README.md` (the name as a heading and the idea in a paragraph) and the `LICENSE`.
3. Set it up with the **set-up-project** skill, in the new folder, with GitHub as its tracker and `<owner>/<name>` as the repo: `AGENTS.md`, the folder standard's `.gitignore` lines, and `docs/agents/`. It commits nothing; the next step does.
4. Commit it all as the first commit, in its own call: `git -C <path> add -A`, then `git -C <path> commit -m "chore: start <name>"`.
5. `gh repo create <name> --public|--private --source <path> --remote origin --push`.

Done when the repo has one commit on `main` and it is pushed to `origin`. The first commit and `origin` are what let a worktree tool lease worktrees of the new repo.

## 4. Create the worktree

Create a new worktree on the new branch, based on the latest default branch, with `<worktree-tool>`:

- **Set**: make it through the **`<worktree-tool>`** skill, leased to the effort when the tool leases.
- **Unset**: git.

  ```bash
  git fetch origin
  git worktree add --no-track -b <branch> ../<repo>-<effort> origin/<default-branch>
  ```

`--no-track` keeps the default branch from becoming the new branch's upstream; the first push sets the real one with `git push -u origin <branch>`.

Done when the worktree exists on the new branch.

## 5. Start the thinking session

Write the idea into a handoff in the worktree (the `.handoff/` path in [orchestrating/folders.md](../orchestrating/folders.md), topic `<effort>`): the idea as the maintainer gave it, the effort, the branch, the worktree, and, for a new project, its repo. Leave it uncommitted; the thinking session's handover commits it with the spec. When that handover's handoff lands on the same path (same day, same topic), it updates this file in place.

The **starting prompt** is one line, and names only skills an agent can load:

```text
Think through the effort in <handoff path>: grill me on it with the grilling skill (the prototype skill when a question needs a runnable answer), then write the spec with to-spec and the tickets with to-tickets, and hand over to an orchestrator with the handover skill.
```

Start the session in the worktree, and suggest the first way that works:

- **`<session-host>`**, when set: start it with the **handover-to-`<session-host>`** skill, passing the worktree, the effort as the topic, `Thinking` as the role, and the starting prompt. For a new project it opens the project's own place in the host.
- **This session**, when `<session-host>` is unset: when it can move into the worktree, it runs the starting prompt here.
- **Paste**: print the starting prompt in a fenced block, and ask the maintainer to start `<agent-to-start>` in the worktree and paste it.

Done when the thinking session is working on the prompt. When it runs elsewhere, tell the maintainer where, and stop: this session's part is done.

## After the pull request merges

When the maintainer says the pull request is good, that it merged, or to merge it, the **close-effort** skill merges it and closes the effort.
