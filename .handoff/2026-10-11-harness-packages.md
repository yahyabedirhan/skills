# Handoff: harness packages

Build Spec: Give each harness one package and deliver one pull request.

## Where

- Worktree: `/home/yabepa/.treehouse/skills-22e236/4/skills`
- Branch: `chore/harness-packages`
- Lease id: `b44d378ddcc47cd8276886c7210c240a`. Holder: `harness-packages`.
- Do not return this worktree. Do not switch the maintainer's other checkouts.

## Spec and tickets

- Spec: Give each harness one package, https://github.com/yahyabedirhan/skills/issues/200
- Chore: Move Cursor onto one harness package, https://github.com/yahyabedirhan/skills/issues/202
- Chore: Move Pi onto one harness package, https://github.com/yahyabedirhan/skills/issues/203
- Chore: Move Claude Code onto one harness package, https://github.com/yahyabedirhan/skills/issues/204
- Chore: Move Codex onto one harness package, https://github.com/yahyabedirhan/skills/issues/205
- Chore: Move opencode onto one harness package, https://github.com/yahyabedirhan/skills/issues/206
- Chore: Remove the old harness tables, https://github.com/yahyabedirhan/skills/issues/207
- Chore: Keep the set-up-machine procedure free of harness rules, https://github.com/yahyabedirhan/skills/issues/208

Read each issue in full. The spec is the design. Do not redesign it.

## Decisions already made

- Printed audit lines stay the same. A `FAIL` still fails the run. A `gap` still does not.
- Cursor's package defines the operations. Pi, Claude Code, Codex, and opencode copy those operations.
- Issues 203, 204, 205, and 206 can run in parallel after issue 202. Issue 207 waits for all four. Issue 208 waits for issue 207.
- The pointer, the shared file, and personal permission rows stay shared. One harness's generated instructions move into that harness's package.
- Do not change what the audit accepts or rejects.
- Leave pull request 199 alone. It is another branch and another worktree.
- The maintainer is away. Decide an open question inside this design and list it in the pull request. Do not send this session a prompt.

## Suggested skills

- `/orchestrate-effort`
- `/implement`
- `/to-pr`
- `/treehouse`
- `/writing-for-agents`
- `/show-me`
- `/code-review`
