# Machine diff

How to propose, apply and check the one diff that brings a machine in line.

## The diff

Work out what each harness should hold, from `rules.json`, the shared file's shape and the harness's reference, and compare it with what the machine holds. Write the whole diff: per harness and file, the exact entries or a unified diff, each line marked:

- `added`, `tightened` (a stricter entry added where it wins), `removed`;
- `present`, `wired` (the hook), `found` (the MCP tools a mail row matched);
- `stricter` (the machine is stricter than the table: kept), `extra` (not the table's: kept), `gap` (what the harness can't express), `none` (no such feature).

## What may be removed

Use `removed` only for memory files, a harness's own global file whose every line is already in the shared file (it becomes a link), and this skill's own wiring that points at an old script. An entry a dropped row left behind is `extra`, for the user to remove.

## Shared skills

With a `<skills-repo>` value, the diff installs that repo's skills globally: `npx --yes skills add <owner>/<repo> -g -a codex -a claude-code -y`, leaving out `-a claude-code` when `~/.claude/skills` is a link to `~/.agents/skills`. It's `present` once `~/.agents/.skill-lock.json` records a skill from that source. With no value, it's a `none` line.

## Backup

Before writing any file, copy every file the diff changes or removes into `~/.config/agents/backups/<UTC time as YYYYmmddTHHMMSSZ>/`, at its path relative to the home folder (`.claude/settings.json`). Copy a symlink as a link.

## Writing

Run any install command first (a skill the diff installs). If one fails, write nothing and report it. In a JSON file, change only the keys the diff names and keep the rest. Write through a symlink to its target.

## Verifying

Run `python3 <this skill>/scripts/verify.py` (Python 3.9+, standard library only; it writes nothing). It passes when it prints `rules ok`, a `hook wired` line for every harness found, and every `codex differs` line is a row codex.md says gets no rule.

## Trying a change on a copy

To try a change without touching the real machine, run the steps against a copy of the home folder in the project's `.scratch/`, and check it with `verify.py --home <copy>`. Start no harness there, since it would read the real login.
