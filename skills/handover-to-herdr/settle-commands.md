# Settle commands

Inspect live callers and occupants and mark a session settled while leaving its session and all Herdr workspaces, tabs and panes open.

## Live caller and occupants

Check the installed CLI help and server with `herdr status`. Check whether caller context exists with `test -n "$HERDR_PANE_ID"`; when it does, run `herdr pane current --current` and read `.result.pane` for the current pane, terminal, tab and workspace IDs. Refresh this immediately before a mutation. A moved pane keeps its inherited environment, so compare other panes with the returned live pane ID, and derive the caller's tab from that response rather than `$HERDR_TAB_ID`. Without caller context, skip this command: it can resolve another client's focused pane. Preserve and report an unresolved caller instead of targeting by title or focus.

Run `herdr agent list`, `herdr workspace list` and `herdr pane list`. Inspect each relevant pane with `herdr pane get <pane_id>` and `herdr pane process-info --pane <pane_id>`. Compare its current workspace/tab/pane hierarchy and `foreground_cwd`, and the foreground processes' `cwd`, with the canonical worktree path and repository verified by Git. Report idle agents, shells and services as occupants too. Workspace `checkout_path` and pane `cwd` are metadata, not proof of where a process runs; missing process location leaves occupancy uncertain. Foreground information alone also cannot exclude detached services: use the worktree tool's process checks before any release, and keep the worktree when its occupants remain uncertain. Record identities and locations without copying process arguments that may contain credentials.

Leave out only the resolved live caller when finding other agents; never leave out its whole workspace. Keep the caller's own worktree leased regardless of its agent state. Preserve worktrees occupied by any session or service, and report their occupants. Use `/treehouse` for pooled-worktree release checks and lease guards, or the configured worktree tool's equivalent. A proven-merged, unoccupied worktree may be released autonomously only after fresh verification; delete its branch only after successful release and the calling skill's merge proofs. An interrupted or uncertain operation requires inspection before a retry.

## Settled marker

When caller resolution succeeds, inspect `herdr tab get <live tab_id>` for the current label and hierarchy. Immediately before renaming, resolve the caller again and confirm the same terminal still belongs to that tab and workspace; if it moved, inspect the newly returned hierarchy instead. When the label does not already start with `[settled]`, rename the verified live tab with `herdr tab rename <live tab_id> "[settled] <current label>"`. Use explicit IDs for the mutation and preserve focus. If the caller or hierarchy cannot be verified, leave the label alone and report why. The marker says the work is saved and settled; the session remains available for follow-up.

## Keep the session and topology open

Settlement leaves every workspace, tab and pane open and keeps the caller's occupied worktree. Schedule no delayed external release or session-ending command. An explicit cleanup request can authorize closing named topology without another approval, but closing linked or grouped topology is never inferred from that request. Inspect live identities, location, hierarchy and occupants again immediately before any separately authorized cleanup.
