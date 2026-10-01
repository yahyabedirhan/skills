# Handoff: PR #110, show-me fork upgrade and root assets/ folder

- **Worktree:** this one, `~/.treehouse/skills-22e236/3/skills` (treehouse lease `fork-and-folder-upkeep`), on branch `skills/fork-and-folder-upkeep`, which tracks its remote.
- **Pull request:** #110 "Upgrade show-me's fork and move images to a root assets/ folder", https://github.com/yahyabedirhan/skills/pull/110. It's open and not merged. Its description, saved at `.scratch/pr-110/description.md` in the main checkout, explains the change.
- **Issues it closes:** #106 "Upgrade the show-me fork to humanlayer/skills' latest" (body rewritten on 2026-10-01) and #108 "Folder standard: keep images and screenshots in a root assets/ folder". The commits say `Closes`.
- **Reaching the session that handed over:** it's idle in the main checkout. You're the maintainer's contact for this PR now.

## Done

- `6e3ff5b` chore(show-me): the README row moves the Origin to humanlayer/skills `ca7c808`. Upstream's only change, `bba9d13`, which makes the skill user-invocable only, is left out per step 5 of *Upgrade a fork* in `maintain-environment`. The rebuilt fork matches the current one, so no skill file changed.
- `c8930e2` feat(orchestrating): the folder standard moves `docs/assets/<topic>/` to `assets/images/<topic>/` and `assets/screenshots/<topic>/`, with a migration row. `set-up-project` explores, proposes, confirms and runs the move. There's a decision entry in `docs/decisions/effort-workflow.md`.

## Left

1. **Wait for the maintainer's review.** They'll review this PR together with the others from the same triage, once all are ready. Don't ask for it or merge it before their go.
2. **Fix any review feedback** on this branch, one commit per fix. Push, and rewrite the description with `/to-pr` if the change moves.
3. **After the maintainer says go:** merge, then do the post-merge work yourself. Update the global skill installs on the Mac (`npx skills update`, per `maintain-environment`) and tell the maintainer the VPS needs the same. Check that #106 and #108 closed. Free this worktree and branch with `settle-effort`/`close-effort`, whichever exists by then (#109 renames it).

## Related work running elsewhere (don't touch)

- #109 settle-session and the settle-effort rename: orchestrator on `settle/settle-session`.
- #111 personal setup spec, tickets #113 to #116: orchestrator on `environment/personal-repository`.

## Suggested skills

`to-pr`, `maintain-environment` (shipping, installs after merge), `close-effort` (or `settle-effort` once #109 lands).
