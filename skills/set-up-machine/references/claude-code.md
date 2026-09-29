# Claude Code adapter

What set-up-machine writes for Claude Code, and why. The code is `scripts/setupmachine/adapters/claude_code.py`. Sources: the Claude Code docs on [permissions](https://code.claude.com/docs/en/permissions), [memory](https://code.claude.com/docs/en/memory) and [settings](https://code.claude.com/docs/en/settings), and the repo's research, `docs/research/harness-capabilities.md`.

## Global instructions

- Claude Code reads `~/.claude/CLAUDE.md` in every session. It has no global `AGENTS.md`.
- The adapter adds one line to that file: `@~/.config/agents/AGENTS.md`, importing the shared file. Imports in user-scope files load without an approval dialog. The rest of `CLAUDE.md` is left as it is.
- Against a `--home` other than the user's own, the line holds the absolute path instead, since `~` would name the real home.

- The plan lists any other line in `CLAUDE.md` as `extra`: global instructions belong in the shared file, where every harness reads them.

## Memory

- Auto memory is on by default and writes `~/.claude/projects/<project>/memory/`. The adapter sets `"autoMemoryEnabled": false` in `~/.claude/settings.json`, in the same write as the permissions, and lists every file under a `projects/*/memory/` folder as `removed`.
- **Gap:** a project's `.claude/settings.json` can set `autoMemoryEnabled: true` and win, and `CLAUDE_CODE_DISABLE_AUTO_MEMORY` outranks the key for one session. The project audit checks the first.

## Permissions

- **File:** `~/.claude/settings.json`, key `permissions` with the lists `deny`, `ask` and `allow`. Everything else in the file is kept as it is.
- **Levels:** `deny` rows go to `deny`, `ask` rows to `ask`, and `allow-and-report` rows to `allow`. The report half needs the pre-tool hook.
- **Evaluation:** deny, then ask, then allow; the first match wins. So tightening adds the stricter entry and leaves the looser one in place: it no longer takes effect, and it isn't the skill's to remove. An entry already stricter than the table stays, and the plan lists it as `stricter`.
- **Covered already:** a broader entry on the machine counts as the table's entry: `Bash(gh repo delete*)` covers `Bash(gh repo delete:*)`, and `mcp__<server>` or a matching glob covers one tool.
- **Projects can't loosen it:** a user-level deny holds against any project `allow`.

## Command rows

- `Bash(<prefix>:*)` matches the command text as written, not its parsed arguments. The adapter writes one entry per spelling the row expands to: `rm -rf`, `rm -fr`, `rm -R -f`, `rm --recursive --force`, `/bin/rm -rf`, `git push -f`, and the rest.
- `:*` holds a word boundary: `Bash(git push --force:*)` doesn't match `git push --force-with-lease`, which the ask row covers.
- Deny and ask rules apply to each part of `a && b`, `a; b`, pipes and subshells, and past wrappers such as `timeout`, `nice` and `nohup`.

## File rows

- A `read` row becomes `Read(<path>)`, a `write` row `Edit(<path>)`. Project paths get `./` (the working directory), and `**/` reaches the root and every subfolder; `~/` paths stay as they are.
- **`Write(...)` rules are never checked.** Claude Code accepts them and warns at startup. `Edit` covers every file-editing tool. An old `Write(...)` entry on the machine is listed as an extra that does nothing.
- A `Read` deny also blocks edits to that path.

## MCP-tool rows

- Tools are named `mcp__<server>__<tool>`; a claude.ai connector shows as `mcp__claude_ai_<Name>__<tool>` in the CLI, and a rule naming the server any other way matches nothing there.
- The adapter asks Claude Code for its tools: it starts `claude -p` with `--output-format stream-json --verbose`, reads the tool list from the session's `init` event, and stops the session before it calls the model. Each row's regexes pick the matching names, which become exact deny entries.
- A denied MCP tool is removed from the session, so the agent never sees it.

## Gaps

Native entries alone let these through:

- **Commands:** more flags in the same token (`rm -rfv`) or after the operands (`rm x -rf`), options before a subcommand (`git -C dir push --force`), and a command inside another program's string (`bash -lc "…"`, `eval`, a script).
- **Files:** a script or another program that opens the file itself.
- **MCP tools:** a tool connected after the run, until the next run.

The pre-tool hook closes the command and MCP-tool gaps for deny and allow-and-report rows, so the plan lists, per row, only the command gaps of `ask` rows and the file gap. The hook's own gaps, listed once in its plan section:

- a command inside a script file or another interpreter (`python -c`), built from variables (`$cmd -rf x`), or behind an alias or function defined elsewhere; an abbreviated long option (`--recur`); a force push by refspec (`git push origin +main`);
- a project's `.claude/settings.json` with `"disableAllHooks": true`, which turns every non-managed hook off there.

## Pre-tool hook

- **Wiring:** one `hooks.PreToolUse` group in `~/.claude/settings.json` with matcher `*` (every tool) and one command handler, `python3 <skill>/scripts/pre_tool_hook.py --harness claude-code`, timeout 10 seconds. Against a `--home` other than the user's own, it adds `--config <home>/.config/agents/hook.json`, so a trial reports into that home, and a plan run with `--rules <table>` adds `--rules <table>`, so the hook reads the table the plan used. Settings.json gets one write carrying the permissions, the hook and `autoMemoryEnabled`.
- **Audit:** `wired` when a match-all group runs exactly that command. The manifest records the command; when the skill moves, the old command is removed and the new one added. Other hooks are the user's and stay.
- **Input:** Claude Code's PreToolUse JSON: `tool_name`, `tool_input` (`command` for Bash; `file_path` or `notebook_path` for Read, Edit, MultiEdit, Write and NotebookEdit; `path` for Grep), `cwd`, `session_id`.
- **Answer:** a deny is `hookSpecificOutput.permissionDecision: "deny"` with the refusal in `permissionDecisionReason`, which Claude Code shows the agent. Otherwise it prints nothing and exits 0, so the native permissions decide: it never answers `allow`, which would skip them. It exits 1, which Claude Code treats as a non-blocking error, when the input or the table can't be read.
- **Reports** are written when the call is submitted, before any permission prompt, so a report means the agent asked to run it.
- **The Cursor CLI runs this hook too** (it reads hooks from `~/.claude/settings.json`). Its payload is read as far as it fits, so the hook doesn't crash on it, but Cursor passes `permissionDecisionReason` to the user, not the agent. The Cursor adapter decides how to wire the hook for Cursor itself.

## What the agent sees

A command the native rules refuse returns `Permission to use Bash with command <command> has been denied.`, and a refused file `File is in a directory that is denied by your permission settings.` Neither names the rule, so the instruction also reaches the agent through the shared file's rule line, loaded at the start of every session.

The hook runs first, and its refusal names each refused part, its rule, reason and instruction, and says nothing else in the call ran.

## Read by other harnesses

The Cursor CLI also reads the `allow` and `deny` lists in `~/.claude/settings.json`, but a rule whose command part has a space, such as `Bash(rm -rf:*)`, matches only the bare command there. Its adapter decides how to cover those rules.

## Checking it

After an apply, in a throwaway folder, with `--setting-sources project,local --settings <the settings.json>` so only the generated entries apply:

- **Commands:** `claude -p "Run exactly: rm -fr x" --allowedTools Bash` leaves `x` in place and quotes the hook's refusal. Allowing `Bash` proves a rule refused it, not the lack of an allow. With a settings file holding only the `hooks` key, `bash -lc "rm -rf x"` is refused too, which proves the hook, not a native entry.
- **Reports:** `gh api rate_limit` runs, and its line appears in the report folder.
- **Files:** asking for a Write to `.env`, `sub/.env.local` and `secrets/k` with `--allowedTools Write` leaves them unchanged.
- **Mail tools:** a found tool, such as a trash tool, is absent from the session.

Against the real login, `claude -p "Without tools: quote your rule about rm -rf and the file it came from."` quotes the rule line from `~/.config/agents/AGENTS.md`.
