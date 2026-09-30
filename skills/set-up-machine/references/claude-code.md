# Claude Code

How to set up and audit Claude Code from the rule table. **Check the current docs first**, since the formats change: [permissions](https://code.claude.com/docs/en/permissions), [hooks](https://code.claude.com/docs/en/hooks), [settings](https://code.claude.com/docs/en/settings), [memory](https://code.claude.com/docs/en/memory). Where they differ from this file, follow the docs and name the difference in your report. Background: the repo's `docs/research/harness-capabilities.md` and `docs/research/auto-mode-semantic-guard.md`.

**Found** when `~/.claude/` exists or `claude` is on `PATH`. Every setting below lives in one file, `~/.claude/settings.json`, except the instructions. Keep every key you don't change; a file that isn't valid JSON stops the run until the user fixes it.

## Global instructions

- Claude Code reads `~/.claude/CLAUDE.md` in every session and follows `@path` imports; it has no global `AGENTS.md`. Imports in user-scope files load without an approval dialog.
- The file holds one line, `@~/.config/agents/AGENTS.md`, importing the shared file. Add it when missing; keep the rest of the file.
- Every other line is `extra`: it moves into the shared file (global-instructions.md, *Moving a harness's file*).

## Memory

- Auto memory is on by default and writes `~/.claude/projects/<project>/memory/`. Set `"autoMemoryEnabled": false`, and list every file under `~/.claude/projects/*/memory/` as `removed` (backed up first).
- **Gap:** a project's `.claude/settings.json` can set `autoMemoryEnabled: true` and win (set-up-project's audit checks it); `CLAUDE_CODE_DISABLE_AUTO_MEMORY` outranks the key for one session.

## Permissions

- `permissions` holds the lists `deny`, `ask` and `allow`. A `deny` row goes to `deny`, `ask` to `ask`, `allow-and-report` to `allow` (the hook does the reporting).
- **Evaluation:** deny, then ask, then allow; the first match wins. So tightening adds the stricter entry and leaves the looser one: it stops taking effect, and it isn't yours to remove. An entry already stricter than the table is `stricter`, and kept.
- **Always keep an `allow` list** beside `deny`, even an empty `[]`: the Cursor CLI reads this file too, and skips its whole deny list without one.
- **Covered already:** an entry on the machine that matches everything the wanted one does counts as `present`. `Bash(gh repo delete*)` covers `Bash(gh repo delete *)`; `mcp__<server>` or a matching glob covers that server's tools. An old `Bash(<words>:*)` with a space in `<words>` doesn't count: Claude Code reads it like the ` *` form, but the Cursor CLI matches it only against the bare command. Add the ` *` entry beside it, and list the old one as `extra`.
- **Projects can't loosen it:** a user deny holds against any project `allow`.

## Command rows

`Bash(<prefix> *)` matches the command text as written, so a row becomes one entry per spelling:

- **Programs:** each program as typed, then as `/bin/<program>` and `/usr/bin/<program>`, except shell builtins (`.`, `source`, `set`, `export`, `declare`, `typeset`, `unset`, `eval`, `alias`), which have no path.
- **Flags:** a one-letter name is a short flag (`-r`), a longer one a long flag (`--recursive`). Every order of the groups, every spelling in each group, as separate words; and, when every group has a one-letter name, the one-letter names clustered in every order (`-rf`, `-fr`, `-Rf`, `-fR`).
- **Around the flags:** program, then subcommand words, then flags, then operands: `Bash(git push --force *)`, `Bash(chmod -R 777 *)`. Rows with `any_operand` get one entry per operand word after the subcommand and flags (`Bash(git push --delete origin main *)` covers only that remote, so name the gap).
- **Worked example,** `rm-recursive-force` (flags `[r, R, recursive]` and `[f, force]`): `Bash(rm -rf *)`, `Bash(rm -Rf *)`, `Bash(rm -fr *)`, `Bash(rm -fR *)`, `Bash(rm -r -f *)`, `Bash(rm -r --force *)`, `Bash(rm -R -f *)`, … `Bash(rm --force --recursive *)`, then the same under `/bin/rm` and `/usr/bin/rm`.
- **The space is a word boundary:** `Bash(git push --force *)` doesn't match `git push --force-with-lease`, which the ask row covers. A trailing ` *` that is the only wildcard also matches the bare command (`printenv`).
- **` *`, never `:*`:** the Cursor CLI reads this file and matches `Bash(rm -rf:*)` only against the bare `rm -rf`.
- **No entry, and a gap instead:**
  - `arguments: "none"` (`env`, `export`, `set` alone): an exact `Bash(env)` reads as a prefix in the Cursor CLI, refusing `env FOO=1 cmd` and `set -e` too. The hook refuses the bare commands.
  - `arguments: "flags"` (`declare -x`): a rule on `declare -x` would refuse `declare -x NAME=value` too.
  - `files` (`cat .env`): Bash rules match text, not paths. Claude Code's own Read rules refuse `cat`, `head`, `tail` and `grep` on a denied file; the hook refuses the rest (`less`, `source`, `.`).
- Deny and ask rules apply to each part of `a && b`, `a; b`, pipes and subshells, and past `timeout`, `nice` and `nohup`.

## File rows

- A `read` row becomes `Read(<path>)`, a `write` row `Edit(<path>)`. Project paths get `./` (`./**/.env`); `~/` and `/` paths stay as they are. A path with no `/` after the `./` matches at any depth, as in `.gitignore`: `Read(./.env.*)` refuses `sub/.env.local` too. A `Read` deny also blocks edits.
- **`Write(...)` is never checked by Claude Code** (it warns at startup), but the Cursor CLI checks it on its own file tools, against absolute paths. So a `write` row also gets plain `Write(**/<glob>)` entries (`Write(**/.env)`), with no exception, since Cursor's globs know only `*`. An old `Write(./…)` entry is `extra`: neither harness uses it.
- **No negation.** Globs have positive character classes only (`[!e]` lists `!` and `e`), matched case-insensitively on macOS. So an `except` of literal names becomes the globs around them. For `**/.env.*` minus `.env.example`, `.env.sample` and `.env.template`:
  - each name the literals start with but none of them is: `.env.`, `.env.e`, `.env.ex`, … `.env.exampl`, `.env.s`, … `.env.templat`;
  - after each of those, a class of every letter (both cases), digit, `_` and `.` except the literals' next letters, then `*`: `.env.[0-9A-DF-RU-Za-df-ru-z_.]*` (not `e`, `s`, `t`), `.env.exa[0-9A-LN-Za-ln-z_.]*` (not `m`);
  - each literal followed by more: `.env.example?*`.

  A name that leaves the literals through any other character, and a glob exception (`**/.env*.md`), stay refused natively; the hook leaves them open. An entry on the machine that refuses an exception (`Read(./.env.*)` refuses `.env.example`) is `extra`, with a note that the user removes it to open the exception.

## MCP-tool rows

- Tools are named `mcp__<server>__<tool>`; a claude.ai connector shows as `mcp__claude_ai_<Name>__<tool>` in the CLI.
- **List the tools:** in an empty folder, run `claude -p "List nothing." --output-format stream-json --verbose --tools "" --no-session-persistence --max-turns 1` and read the `tools` of the first event with `"type": "system", "subtype": "init"`; stop it there, before it calls the model. No output (not logged in, not installed) is a `gap`: keep the MCP entries already there.
- Each row's `server` and `tool` regexes (case-insensitive) pick the names; each match is an exact `deny` entry, and a `found` line names them. A denied MCP tool is removed from the session.

## Pre-tool hook

- **Wiring:** one match-all group in `hooks.PreToolUse`:

  ```json
  {"matcher": "*", "hooks": [{"type": "command", "timeout": 10,
    "command": "[ -f <script> ] && python3 <script> --harness claude-code || true"}]}
  ```

  `<script>` is the installed skill's absolute `scripts/pre_tool_hook.py` (under `~/.agents/skills` or `~/.claude/skills`), never a checkout or worktree that can go away. The `[ -f … ] && … || true` makes it fail open: a script that's gone, or an error, exits 0 with no decision, since exit 2 would block every call.
- **Audit:** `wired` when a match-all group runs exactly that command. A handler that runs `pre_tool_hook.py` from another path is this skill's old wiring: `removed`, with the new one `added`. Other hooks are the user's and stay.
- **Input:** `tool_name`, `tool_input` (`command` for Bash; `file_path` or `notebook_path` for Read, Edit, MultiEdit, Write and NotebookEdit; `path` and `glob` for Grep), `cwd`, `session_id`.
- **Answer:** a deny is `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "<the refusal>"}}` with exit 0; Claude Code shows the agent the reason. Otherwise nothing, exit 0, so the native permissions decide. It never answers `allow`, which would skip them, and leaves `ask` rows to the native `ask` list.
- **Reports** are written when the call is submitted, before any permission prompt.
- **Cursor runs this hook too:** it loads `~/.claude/settings.json` hooks (Claude's `PreToolUse` as `preToolUse`). The hook still refuses what it recognises there, and leaves reporting to Cursor's own hook when the payload carries `cursor_version`, so no call is reported twice.
- **Gap:** `"disableAllHooks": true` in this file or a project's turns every hook off. In this file, name it and leave it to the user.

## Auto mode (optional, off)

A deny row's `guard` is prose for auto mode's classifier, for what patterns can't list (a variable read by `python3 -c`). **Leave it off** until the probes in `docs/research/auto-mode-semantic-guard.md`, section 7, have run (tracked in #65); list each guard as `none` meanwhile. When it's turned on:

- `autoMode.hard_deny` in `~/.claude/settings.json` (Claude Code reads `autoMode` only from user, managed and `--settings` files) gets each guard as `"<label>: <rule>"`. A new array starts with `"$defaults"`, which keeps the built-in rules; an existing one is the user's, and one without `$defaults` is a `gap`, left alone.
- `autoMode.classifyAllShell: true` sends every shell command to the classifier, past a project's narrow allow rule.
- The agent sees the label (`[Environment Variable Access]`), not the rule, so the instruction reaches it through the shared file's rule line. `claude auto-mode config` prints the rules in effect.
- **Gaps:** it applies only in a session running in auto mode, and a project can set `disableAutoMode`; in a `-p` or SDK session, read-only commands (`echo $TOKEN`, `cat .env`) and file reads skip the classifier.

## Gaps

Name each in the diff, per row where it applies. With the native entries alone these get through; the hook closes them for deny and allow-and-report rows, so list them only for `ask` rows:

- more flags in the same word (`rm -rfv`) or after the operands (`rm x -rf`); options before the subcommand (`git -C dir push --force`); the command inside another program's string (`bash -lc "…"`, `eval`, a script);
- a script or another program that opens a denied file itself;
- a tool connected after the run, until the next run (the hook matches it by name).

The hook's own misses, listed once: a command inside a script file or another interpreter (`python -c`), one built from variables (`$cmd -rf x`), an alias or function defined elsewhere, an abbreviated long option (`--recur`), a force push by refspec (`git push origin +main`), a glob the shell expands (`cat .env*`), and each row's own `gap`.

## What the agent sees

A native refusal says `Permission to use Bash with command <command> has been denied.` or `File is in a directory that is denied by your permission settings.`, naming no rule, so the instruction reaches the agent through the shared file's rule line. The hook runs first; its refusal names each refused part, its rule, reason and instruction.

## Checking it

`verify.py` checks the rows against the hook and that the hook is wired. To see Claude Code itself enforce them, in a throwaway folder with `--setting-sources project,local --settings <a copy of settings.json>`:

- `claude -p "Run exactly: rm -fr x" --allowedTools Bash` leaves `x` and quotes the hook's refusal; allowing `Bash` proves a rule refused it. With a settings file holding only `hooks`, `bash -lc "rm -rf x"` is refused too, which proves the hook.
- `gh api rate_limit` runs, and its line appears in the report folder.
- Writes to `.env` and `secrets/k` with `--allowedTools Write` leave them unchanged; a Read of `sub/.env.example` works.
- For environment rows, use fake `.env` files and a fake variable, and start the session with a scrubbed environment (`HOME`, `PATH`, `USER` and the fake variable), since a sample that gets through prints whatever the shell holds.
- Against the real login, `claude -p "Without tools: quote your rule about rm -rf and the file it came from."` quotes the rule line from the shared file.
