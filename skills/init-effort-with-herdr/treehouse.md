# Treehouse: daily operations

`treehouse` keeps a pool of pre-warmed git worktrees (dependencies already installed) so a new worktree is ready in seconds. It owns the worktree's life; git owns the branch inside it. These are its everyday commands and gotchas; `treehouse <command> --help` has the rest.

| Need | Command | Notes |
|---|---|---|
| A durable worktree for an effort | `treehouse get --lease --lease-holder <effort>` | Prints only the path. `--json` adds the lease identity. A leased worktree is never handed out again or pruned until returned. Fetches origin first unless `--no-fetch`. |
| See the pool | `treehouse status` | `--json` for scripts. |
| Give a worktree back, keeping it in the pool | `treehouse return <path>` | Terminates lingering processes. `--force` cleans and resets without prompting. |
| Remove a worktree for good | `treehouse destroy <path> --include-leased --yes` | A dry run without `--yes`. Refuses unlanded work unless `--include-unlanded` (data loss). |

## Gotchas

- `destroy` treats any shell or agent running in the worktree as a live process and skips the worktree. Close whatever runs there (such as its Herdr workspace) first.
- Ignored folders (`tmp/`, build output) don't count as unfinished work, so `destroy` removes them with the worktree without warning. Copy out anything worth keeping first.
- A leased worktree is removed only when its exact path is named with `--include-leased`; `--all` never touches it.
- `get --lease` fetches origin, so a branch started from `origin/<default-branch>` right after it is current.
