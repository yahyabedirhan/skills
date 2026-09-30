# Closing an effort in Herdr

The Herdr commands a session closing an effort needs. For each one, check `herdr status` first, target explicit IDs from Herdr's JSON, pass `--no-focus`, and never use `--current`, so no command lands on the pane the maintainer is using.

## Find the agents still working

`herdr agent list` shows each agent's state and pane, and `herdr workspace list` shows the worktree behind each workspace; together they show which worktree each agent works in. An agent other than this session that is `working` in one of the effort's worktrees keeps that worktree. This session's workspace is `$HERDR_WORKSPACE_ID`, or, from outside a pane, the workspace whose `checkout_path` is this session's worktree.

## Free this session's worktree from outside it

Freeing the worktree this session runs in stops the session, so it runs from a tab outside it, after the session's report. Open that tab in the repository's own workspace, the one whose `repo_root` is the repository and whose `is_linked_worktree` is false. Label it, and run the command in its root pane:

```bash
herdr tab create --workspace <repo workspace_id> --cwd <main checkout> --no-focus
herdr tab rename <tab_id> "shell · Close · <effort>"
herdr pane run <pane_id> 'sleep 30; <free command>; git worktree list'
```

`<free command>` frees one worktree: the worktree tool's return, or `git worktree remove <path>`. The pause lets the report finish first. The workspace stays open.
