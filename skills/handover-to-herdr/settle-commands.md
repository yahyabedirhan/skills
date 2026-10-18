# Settle commands

Inspect live callers and occupants and mark a session settled while leaving its session and all Herdr workspaces, tabs and panes open.

## Live caller and occupants

- **Server and CLI:** check the installed CLI help and the server with `herdr status`.
- **Caller context:** present when `test -n "$HERDR_PANE_ID"` succeeds.
  - **With caller context:** run `herdr pane current --current` and read `.result.pane` for the current pane, terminal, tab and workspace IDs. Refresh this immediately before a mutation.
  - **Moved pane:** a moved pane keeps its inherited environment, so compare other panes with the returned live pane ID, and derive the caller's tab from that response rather than `$HERDR_TAB_ID`.
  - **No caller context:** skip `herdr pane current`, since it can resolve another client's focused pane. Preserve and report an unresolved caller instead of targeting by title or focus.

Find the occupants of each worktree:

- **Inventory:** `herdr agent list`, `herdr workspace list` and `herdr pane list`.
- **Per pane:** inspect each relevant pane with `herdr pane get <pane_id>` and `herdr pane process-info --pane <pane_id>`. Compare the pane's current workspace, tab and pane hierarchy, its `foreground_cwd` and the foreground processes' `cwd` with the canonical worktree path and repository verified by Git.
- **Occupants:** report idle agents, shells and services as occupants too.
- **Location proof:** workspace `checkout_path` and pane `cwd` are metadata, not proof of where a process runs, and a missing process location leaves occupancy uncertain. Foreground information alone cannot exclude detached services, so use `<worktree-tool>`'s process checks before any release, and keep the worktree while its occupants remain uncertain.
- **Credentials:** record identities and locations without copying process arguments, since they can contain credentials.

Then decide what to keep and what to release:

- **Caller:** leave out only the resolved live caller when finding other agents, never its whole workspace. Keep the caller's own worktree leased whatever its agent state.
- **Occupied worktrees:** preserve each worktree a session or service occupies, and report its occupants.
- **Release:** release a proven-merged, unoccupied worktree autonomously only after fresh verification, with `/treehouse`'s pooled-worktree release checks and lease guards when `<worktree-tool>` is `treehouse`, or `<worktree-tool>`'s equivalent. Delete its branch only after a successful release and the calling skill's merge proofs.
- **Interrupted or uncertain operation:** inspect it before a retry.

## Settled marker

When caller resolution succeeds:

1. Inspect `herdr tab get <live tab_id>` for the current label and hierarchy.
2. Immediately before renaming, resolve the caller again and confirm the same terminal still belongs to that tab and workspace. If it moved, inspect the newly returned hierarchy instead.
3. When the label does not already start with `[settled]`, rename the verified live tab with `herdr tab rename <live tab_id> "[settled] <current label>"`. Use explicit IDs for the mutation and preserve focus.

- **Unverified caller or hierarchy:** leave the label alone and report why.
- **Meaning:** the marker says the work is saved and settled; the session remains available for follow-up.

## Keep the session and topology open

Settlement leaves every workspace, tab and pane open and keeps the caller's occupied worktree. Schedule no delayed external release or session-ending command. An explicit cleanup request can authorize closing named topology without another approval, but closing linked or grouped topology is never inferred from that request. Inspect live identities, location, hierarchy and occupants again immediately before any separately authorized cleanup.
