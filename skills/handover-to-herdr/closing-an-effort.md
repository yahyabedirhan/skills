# Closing an effort in Herdr

The Herdr commands a session closing an effort needs: finding the agents still working, and freeing this session's own worktree. They follow the rules in this skill's `SKILL.md` under *Herdr from anywhere*, which check that Herdr is reachable and keep every command off the pane the maintainer is using.

## Find the agents still working

`herdr agent list` shows each agent's state and pane, and `herdr workspace list` shows the worktree behind each workspace; together they show which worktree each agent works in. Leave this session out: its workspace is `$HERDR_WORKSPACE_ID`, or, from outside a pane, the workspace whose `checkout_path` is this session's worktree.

## Free this session's worktree from outside it

Open a tab in the repository's own workspace, the one whose `repo_root` is the repository and whose `is_linked_worktree` is false. Label it, and run the command in its root pane:

```bash
herdr tab create --workspace <repo workspace_id> --cwd <main checkout> --no-focus
herdr tab rename <tab_id> "shell · Close · <effort>"
herdr pane run <pane_id> 'sleep 30; <free command>; git worktree list'
```

`<free command>` is the command the close's worktree tool uses to free this session's worktree. The pause lets this session finish its report before the command stops it.
