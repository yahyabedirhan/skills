# opencode

How to set up and audit opencode from the rule table. **Check the current docs first**, since the formats change: [rules](https://opencode.ai/docs/rules/), [permissions](https://opencode.ai/docs/permissions/), [config](https://opencode.ai/docs/config/), [plugins](https://opencode.ai/docs/plugins/). Where they differ from this file, follow them and name the difference in your report. Background: the repo's `docs/research/harness-capabilities.md`, section 3.

**Found** when `~/.config/opencode/` exists or `opencode` is on `PATH`.

## Global instructions

- opencode reads the first that exists of `~/.config/opencode/AGENTS.md` and `~/.claude/CLAUDE.md`. It doesn't follow `@` imports, so the fallback would load Claude Code's import line unexpanded.
- `~/.config/opencode/AGENTS.md` becomes a **relative symlink**, `../agents/AGENTS.md`, to the shared file.
- An existing `AGENTS.md` there (a file, or a link elsewhere) is kept and `extra`, with a `gap`: opencode reads it instead until its lines move into the shared file (global-instructions.md, *Moving a harness's file*) and the user deletes it.

## Memory

No memory feature: a `none` line. Some models are prompted to keep a memory file in the repo (`.github/instructions/memory.instruction.md`); that file is the project's.

## Permissions

- **File:** the global folder loads `config.json`, `opencode.json` and `opencode.jsonc`, in that order; write the last that exists, else create `opencode.json`. Key `permission`: a tool name (a wildcard: `bash`, `read`, `edit`, `external_directory`, `playwright_*`) mapped to a level (`allow`, `ask`, `deny`) or to `{pattern: level}`. Keep every other key; opencode adds `$schema` itself.
- **Comments:** a file holding `//` or `/* */` comments can't be rewritten without losing them. Leave it, and name the rules as a `gap` until the user moves the comments out (or into a `$comment` key). Trailing commas are fine to drop.
- **Evaluation:** opencode's defaults first, then every rule in the order written; the **last match wins**. `*` matches anything, `/` included; `?` one character; a trailing ` *` also matches the command with nothing after it. So write allow entries first, then ask, then deny: where two overlap, the stricter sits later and wins.
- **Tightening:** a looser user entry stays where it is, and the stricter one goes after it. The same pattern at a looser level moves to the end at the table's level. When a later tool-wide entry (`"*": "allow"`, or `"bash": "allow"` written as a string) would override the tool's rules, move the tool's whole object after it (a string level becomes `{"*": <level>}` first).
- **Covered already:** ask which entry opencode would apply, by last match, to the texts the wanted entry matches (for `rm -rf *`: `rm -rf` and `rm -rf x`). At the table's level, `present` (maybe covered by a broader entry); at a stricter one, `stricter`, kept.
- **Projects can loosen it:** a project's `opencode.json` merges over the global one; a pattern new to the project comes after the global rules and wins, and the same pattern replaces the level. So does an agent's own `permission`. Only managed config holds. Both are `gap`s; set-up-project's audit checks each project.

## Command rows

- Each spelling (SKILL.md, *Spellings*) becomes one `bash` pattern ending in ` *`: `"rm -rf *": "deny"`, `"/bin/rm -rf *": "deny"`, `"git push --force *": "deny"`. The space keeps a word boundary: `git push --force *` doesn't match `git push --force-with-lease`.
- `arguments: "none"` becomes the exact command, with no ` *`: `"env": "deny"`, so `env FOO=1 cmd` still runs.
- **No pattern, and a gap instead:** `arguments: "flags"` rows and `files` rows (`cat .env`); patterns match text, not paths or "only flags".
- opencode checks each plain command of a compound (`a && rm -rf x`, pipes, `$(…)`) by its text, but never a declaration: `export -p`, `declare -p` and `typeset -p` (and `local`, `readonly`) don't meet their patterns (probed). A `gap` for those rows; the hook refuses them.

## File rows

- A `read` row becomes `read` patterns, a `write` row `edit` patterns (edit, write and patch tools), matched against the path relative to the project. `**` is `*` here, since `*` crosses `/`, and `**/.env` becomes two patterns, `.env` and `*/.env`, since `*/` alone misses the project's own folder.
- A `~/` path becomes an `external_directory` pattern (`"~/.ssh/*": "deny"`), which binds file tools and the file arguments of bash commands outside the project, reads and writes alike.
- **Exceptions:** no negation, but the last match wins, so each `except` glob becomes an `allow` after the row's deny entries (`read: {".env.example": "allow", "*/.env.example": "allow"}`), as opencode's own defaults do for `.env.example`. Where a user entry refuses the exception (`"*.env*": "deny"`), leave it refused: `stricter`.

## MCP-tool rows

Tools are named `<server>_<tool>`, and opencode lists them only inside a session. So match each row's `server` regex against the servers in the global config's `mcp` key: no match is a `found` line saying so; a match is a `gap` (no native entry; the hook refuses the matching tools when called).

## Pre-tool hook

- **Wiring:** the plugin `~/.config/opencode/plugins/set-up-machine.js`, which opencode loads from its global plugin folder. Write it from [opencode-plugin.js](opencode-plugin.js), with `__HOOK_COMMAND__` replaced by the JSON array `["python3", "<script>", "--harness", "opencode"]` (`<script>` as in SKILL.md, *The pre-tool hook*). Its `tool.execute.before` runs before every tool call, built-in and MCP, and before the permission check; it throws the hook's refusal, which stops the call. When the script is gone, can't start, exits non-zero or takes over 10 seconds, it lets the call through.
- **Audit:** `wired` when the file is the template with the current command. A file there without the template's first line is someone else's: a `gap`, left alone. A plugin with an old command is rewritten.
- **Input:** `{"tool", "sessionID", "args", "directory"}`: `args.command` (and `args.workdir`) for `bash`; `filePath` for `read`, `edit` and `write`; `path` for `grep`, `glob` and `list`; the file headers of `apply_patch`'s `patchText`. A tool that isn't built in is read as an MCP tool, trying each `_` as the split between server and tool.
- **Answer:** the refusal as plain text, which the plugin throws; the agent reads the error's message as the tool's result. Otherwise nothing, so the native permissions decide.
- **Gaps:** a project's plugin runs after this one and can rewrite a call's arguments once the hook has passed them; `--pure` or `OPENCODE_PURE` starts opencode without plugins (probed). The native rules still hold in both.

## Gaps

With native entries alone these get through; the hook closes the command and MCP gaps for deny and allow-and-report rows, so list those only for `ask` rows:

- more flags in the same word (`rm -rfv`) or after the operands (`git push origin main --force`, probed); options before a subcommand (`git -C dir push --force`); a command inside another program's string (`bash -lc "…"`, `eval`, a script);
- a bash command (`sed`, `echo … > .env`), a script or another program opening a file; for `~/` paths, a session whose project is the home folder;
- the rows with no pattern above, and each row's `guard` (no semantic guard: a `none` line).

The hook's own misses are in SKILL.md, *The pre-tool hook*.

## What the agent sees

A native refusal: `The user has specified a rule which prevents you from using this specific tool call. Here are some of the relevant rules [...]`, with every bash pattern as JSON, not just the one that matched (about 150, which costs the agent tokens). An `ask` rule prompts in the TUI; `opencode run` auto-rejects it (`The user rejected permission to use this specific tool call.`). The hook runs first, and its refusal names each refused part, its rule, reason and instruction.

## Checking it

In a sandbox: `OPENCODE_CONFIG_DIR=<a copy of the config folder>` layers it over the real global config (read, not written), and `XDG_DATA_HOME`, `XDG_STATE_HOME` and `XDG_CACHE_HOME` pointed into the sandbox keep sessions and logs out. `opencode run` takes the session's folder from `PWD`. Start it with a scrubbed environment.

- `opencode debug agent build` prints the ruleset in the order opencode evaluates it.
- `opencode run --format json "Run exactly: rm -rf x"` leaves `x`, and the tool result is the hook's refusal; `git push --force-with-lease …` is auto-rejected as an ask; `gh api rate_limit` runs and gets a report line.
- With only the permissions (no plugin), the same samples get opencode's own refusal, and `git push <remote> HEAD --force` runs: the gap the hook closes.
- A `read` of `.env` is refused; a `read` of `.env.example` works.
- `opencode run "Without tools: quote your rule about rm -rf and the file it came from."` quotes the shared file's rule line.
