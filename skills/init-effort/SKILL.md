---
name: init-effort
description: Start a new effort on its own branch and worktree, or a brand-new project in its own repo, and start its thinking session there.
argument-hint: "The idea, in a sentence or a paragraph"
disable-model-invocation: true
---

# Init Effort

An **effort** is work big enough for its own branch and pull request: a feature, a new app, a refactor, a re-architecture. Routine upkeep, such as data edits and small fixes, runs in the current checkout without this skill; the project's instructions may list what counts as routine there.

The effort's whole life happens in the worktree this skill creates: the thinking now, the build later. This skill writes only into that worktree and, for a new project, the new repo, so the repository this session was started in stays as it was.

## Parameters

- `<worktree-tool>`: the tool that makes a new worktree. When it is Treehouse, use `/treehouse` and lease the worktree to the effort. Default: `git worktree add`, with the worktree beside the main checkout unless the project keeps worktrees elsewhere, and the new branch given no upstream until its first push, since a branch that tracks the default branch makes a bare `git push` target it.
- `<session-host>`: where the thinking session opens. When it is Herdr, use `/handover-to-herdr`. Default: run the starting prompt in this session when it can move into the worktree; otherwise print the prompt in a fenced block, and ask the maintainer to start `<agent-to-start>` in the worktree and paste it.
- `<agent-to-start>`: the command that starts a new agent session. Default: this session's harness.

## 1. Decide where it lives

From the idea, tell which it is:

- **An effort in an existing repo**: the current repository, or one the idea names.
- **A new project**: the idea is for something that has no repo yet.

When it isn't clear, ask. Done when the target repo is known, or the idea is a new project.

## 2. Name it

Propose a short kebab-case **effort name** and a branch named the project's way, `<area>/<effort>` by default, and confirm both with the maintainer.

For a new project, first propose a few **project names** and confirm one. When the idea comes with a reference project, the names stand on their own rather than echo it. The project's first effort then gets its own name and branch as above.

Done when the maintainer has confirmed the effort name and branch, and for a new project the project name.

## 3. Create a new project

Only for a new project; otherwise skip to step 4.

The project goes in the maintainer's **projects folder**, named in their instructions. When their instructions don't name one, ask for it, and suggest adding it there. Check that neither a folder nor a GitHub repo already has the project's name.

Ask, every time, whether the GitHub repo is **public or private**, and which licence it takes; recommend MIT in the maintainer's name. Then:

1. Create the folder and a git repository in it, on `main`.
2. Write a `README.md`, with the name as a heading and the idea in a paragraph, and the `LICENSE`.
3. Set it up with `/set-up-project`, in the new folder, with GitHub as its tracker and `<owner>/<name>` as the repo.
4. Commit it all as the first commit, `chore: start <name>`, in its own call, so a refused command stops only itself.
5. Create the GitHub repo with the visibility the maintainer chose, as `origin`, and push `main`.

Done when the repo has one commit on `main` and it is pushed to `origin`. The first commit and `origin` are what let a worktree tool lease worktrees of the new repo.

## 4. Create the worktree

Create a new worktree on the new branch with `<worktree-tool>`, based on the latest default branch.

Done when the worktree exists on the new branch.

## 5. Start the thinking session

Write the idea into a handoff in the worktree, in the project's handoff folder, else at `.handoff/<date>-<effort>.md`. It holds the idea as the maintainer gave it, the effort, the branch, the worktree, and, for a new project, its repo. Leave it uncommitted; the thinking session's handover commits it with the spec.

The **starting prompt** is one line, and names only skills an agent can load:

```text
Think through the effort in <handoff path>: grill me on it with the grilling skill, using the prototype skill when a question needs a runnable answer, then write the spec with to-spec and the tickets with to-tickets, and hand over to an orchestrator with the handover skill.
```

Start the session in the worktree through `<session-host>`, passing the worktree, the effort as the topic, `Thinking` as the role, and the starting prompt.

Done when the thinking session is working on the prompt, or the maintainer says it started. When it runs elsewhere, tell the maintainer where, and stop: this session's part is done.
