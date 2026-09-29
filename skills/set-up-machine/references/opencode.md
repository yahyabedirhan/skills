# opencode adapter

What set-up-machine writes for opencode, and why. The code is `scripts/setupmachine/adapters/opencode.py`. Sources: the opencode docs on [rules](https://opencode.ai/docs/rules/), [permissions](https://opencode.ai/docs/permissions/), [config](https://opencode.ai/docs/config/) and [plugins](https://opencode.ai/docs/plugins/), and the repo's research, `docs/research/harness-capabilities.md` (section 3). With no `~/.config/opencode/` folder, the plan says opencode isn't set up and writes nothing for it.

## Global instructions

- opencode reads the first that exists of `~/.config/opencode/AGENTS.md` and `~/.claude/CLAUDE.md`. It doesn't follow `@` imports, so the fallback would load Claude Code's file with its import line unexpanded.
- The adapter makes `~/.config/opencode/AGENTS.md` a symlink to `../agents/AGENTS.md`, the shared file. The link is relative, so it holds in any home.
- An existing `AGENTS.md` there (a file, or a link elsewhere) is kept and listed as `extra`, with a gap: opencode reads it instead of the shared file until its lines move into the shared file (references/global-instructions.md, *Moving a harness's file*) and it's deleted. The next run then links it.

## Memory

- opencode has no memory feature, so the plan prints a `none` line. Some models get a prompt asking them to keep a memory file in the repo (`.github/instructions/memory.instruction.md`); that file is the project's, like any other.

## Permissions

- **File:** the global folder loads `config.json`, `opencode.json` and `opencode.jsonc`, in that order, so the adapter writes the last of them that exists, else a new `opencode.json`. Key `permission`: a tool name (a wildcard: `bash`, `read`, `edit`, `external_directory`, `playwright_*`) mapped to a level (`allow`, `ask`, `deny`) or to `{pattern: level}`. Everything else in the file is kept; opencode adds a `$schema` key to a file without one.
- **Comments:** JSON comments can't survive a rewrite by the standard library, so a file holding comments isn't rewritten: the plan lists the rules as a gap until the comments move out (or into a `$comment` key). Trailing commas are read and dropped.
- **Evaluation:** opencode's defaults first, then every rule in the order written; the last match wins. `*` matches anything, `/` included, and a trailing ` *` also matches the command with nothing after it. So the adapter appends: allow entries first, then ask, then deny, so where two overlap the stricter sits later and wins.
- **Tightening:** a looser entry the user wrote stays where it is, and the stricter one goes after it. The same pattern at a looser level is moved to the end at the table's level. When a later tool-wide entry (`"*": "allow"`) would override the tool's rules, the tool's whole object moves after it. The plan lists each as `tightened`.
- **Covered already:** a broader entry at the same level (`"rm *": "deny"`) counts as present; one at a stricter level is listed as `stricter` and kept.
- **Projects can loosen it:** a project's `opencode.json` merges over the global one; a pattern new to the project comes after the global rules and wins, and the same pattern replaces the level. So does an agent's own `permission`. Only managed config holds against a project. The plan lists both as gaps; set-up-project's audit checks each project.

## Command rows

- Each spelling the row expands to becomes one `bash` pattern ending in ` *`: `rm -rf *`, `rm -fr *`, `/bin/rm -rf *`, `git push --force *`. The space before `*` keeps a word boundary: `git push --force *` doesn't match `git push --force-with-lease`, which the ask row covers.
- A row with `arguments: "none"` becomes the exact command, without ` *`: `env`, so `env FOO=1 cmd` still runs.
- opencode checks each plain command of a compound (`a && rm -rf x`, pipes, `$(…)`) by its text, but not a declaration: `export -p`, `declare -p` and `typeset -p` never meet their patterns (probed). The hook refuses them, and the plan names that gap.
- A row with `files` (`cat .env`) gets no pattern: bash patterns match text, not paths. The hook refuses it, and the plan names that gap.

## File rows

- A `read` row becomes `read` patterns and a `write` row `edit` patterns (edit, write and patch tools), matched against the path relative to the project. `**/.env` becomes `.env` and `*/.env`, since `*/` alone would miss the project's own folder.
- A `~/` path becomes an `external_directory` pattern (`~/.ssh/*`), which binds file tools and the file arguments of bash commands outside the project, for reads and writes alike.
- **Exceptions:** opencode has no negation, but the last match wins, so each `except` glob becomes an `allow` after the row's deny entries (`read ".env.example": "allow"`). opencode's own defaults leave `.env.example` readable the same way. Where the user's own entry refuses the exception (`"*.env*": "deny"`), the allow isn't added, since it would loosen that entry; the plan lists it as `stricter`.

## MCP-tool rows

- Tools are named `<server>_<tool>`. opencode lists them only inside a running session (neither `opencode debug` nor the server's tool list includes them), so the plan matches each row's `server` regex against the MCP servers in the global config. No match prints a `found` line saying so; a match prints a gap: there's no native entry, and the hook refuses the matching tools when they're called. `--tool-names` isn't used for opencode.

## Semantic guard

- opencode has no semantic guard, so each row's `guard` gets a `none` line: the deny rules and the hook are the whole cover.

## Gaps

Native entries alone let these through:

- **Commands:** more flags in the same token (`rm -rfv`) or after the operands (`git push origin main --force`, probed), options before a subcommand (`git -C dir push --force`), a command inside another program's string (`bash -lc "…"`, `eval`, a script), declarations (`export -p`), and commands on a `.env` file (`cat .env`, probed).
- **Files:** a bash command (`sed`, `echo … > .env`), a script or another program opening the file; for `~/` paths, a session whose project is the home folder itself.
- **MCP tools:** every tool, natively; the hook covers them.
- **Precedence:** a project's `opencode.json` or an agent's `permission`, as above.
- **`$VAR` expansion:** a variable expanded inside another command (`echo $TOKEN`) prints its value, and no rule can tell that from ordinary use.

The pre-tool hook closes the command and MCP-tool gaps for deny and allow-and-report rows, so the plan lists, per row, only the command gaps of `ask` rows, the file gaps, the rows only the hook covers, and each row's own `gap`. The hook's own gaps, listed once in its plan section:

- a command inside a script file or another interpreter (`python -c`), built from variables (`$cmd -rf x`), or behind an alias or function defined elsewhere; an abbreviated long option (`--recur`); a force push by refspec (`git push origin +main`);
- a project's plugin runs after this one and can rewrite a call's arguments once the hook has passed them; `--pure` or `OPENCODE_PURE` starts opencode without plugins (probed: the hook doesn't run). The native rules still hold in both.

## Pre-tool hook

- **Wiring:** a plugin file, `~/.config/opencode/plugins/set-up-machine.js`, which opencode loads from its global plugin folder. Its `tool.execute.before` runs before every tool call, built-in and MCP, and before the permission check. It hands the call to `python3 <skill>/scripts/pre_tool_hook.py --harness opencode` on stdin, waits up to 10 seconds, and throws the hook's output as an error when there is any, which stops the call. Against a `--home` other than the user's own, the command adds `--config <home>/.config/agents/hook.json`, and a plan run with `--rules <table>` adds `--rules <table>`.
- **Audit:** `wired` when the file holds exactly the plugin the plan would write. The file starts with a marker line; when the command changes (the skill moved), the plugin is rewritten. A file of that name without the marker is someone else's: kept, and the hook listed as not wired.
- **Input:** `{"tool", "sessionID", "args", "directory"}`, the plugin's view of the call. `args.command` (and `args.workdir`) for `bash`; `filePath` for `read`, `edit` and `write`; `path` for `grep`, `glob` and `list`; the `*** Add/Update/Delete File:` and `*** Move to:` lines of `apply_patch`'s `patchText`. A tool that isn't built in is read as an MCP tool, trying each `_` as the split between server and tool.
- **Answer:** a refusal is the plain refusal text, and the plugin throws it. Otherwise the hook prints nothing and the plugin returns, so the native permissions decide. The hook fails open: if it exits non-zero, can't start or times out, the plugin lets the call through to the native rules.
- **Reports** are written before the permission check, so a report means the agent asked to run it.

## What the agent sees

A command the native rules refuse returns `The user has specified a rule which prevents you from using this specific tool call. Here are some of the relevant rules [...]`, with the whole ruleset for that tool as JSON: every bash pattern, not the one that matched. An `ask` rule prompts in the TUI; `opencode run` auto-rejects it, and the agent reads `The user rejected permission to use this specific tool call.`

The hook runs first. A thrown error becomes the tool's result as its message, unwrapped (probed), so the agent reads the refusal naming each refused part, its rule, reason and instruction.

## Checking it

With a sandbox: `OPENCODE_CONFIG_DIR=<a copy of the generated config folder>` layers it over the real global config (read, not written), and `XDG_DATA_HOME`, `XDG_STATE_HOME` and `XDG_CACHE_HOME` pointed into the sandbox keep sessions and logs out of the real ones. `opencode run` takes the session's folder from `PWD`, so set it to the throwaway folder. Start the session with a scrubbed environment (no tokens or keys), since a sample that gets through prints whatever the shell holds.

- **Merged rules:** `opencode debug agent build` prints the ruleset in the order opencode evaluates it.
- **Commands:** in a throwaway folder with a folder `x`, `opencode run --format json "Run exactly: rm -rf x"` leaves `x` in place, and the tool result is the hook's refusal; so for `echo a && rm -rf x` and `git push --force <a remote that doesn't exist> HEAD`. `git push --force-with-lease …` is auto-rejected as an ask, and `gh api rate_limit` runs and its line appears in the report folder.
- **Native alone:** with a config folder holding only the `opencode.jsonc`, the same samples get opencode's own refusal, and `git push <remote> HEAD --force` runs (a gap the hook closes).
- **Files:** a `read` of `.env` is refused; a `read` of `.env.example` works.

Against the real setup, `opencode run "Without tools: quote your rule about rm -rf and the file it came from."` quotes the rule line from the shared file.
