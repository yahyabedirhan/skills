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
- **Covered already:** a broader entry on the machine counts as the table's entry: `Bash(gh repo delete*)` covers `Bash(gh repo delete *)`, and `mcp__<server>` or a matching glob covers one tool. An old `Bash(<words>:*)` entry doesn't count when its prefix has a space: Claude Code reads it like the ` *` form, but the Cursor CLI matches it only against the bare command, so the ` *` entry is added beside it and the old one listed as an extra.
- **Projects can't loosen it:** a user-level deny holds against any project `allow`.

## Command rows

- `Bash(<prefix> *)` matches the command text as written, not its parsed arguments. The adapter writes one entry per spelling the row expands to: `rm -rf`, `rm -fr`, `rm -R -f`, `rm --recursive --force`, `/bin/rm -rf`, `git push -f`, and the rest.
- The space holds a word boundary: `Bash(git push --force *)` doesn't match `git push --force-with-lease`, which the ask row covers. A trailing ` *` that is the rule's only wildcard also matches the command with nothing after it (`printenv`).
- ` *`, not the equivalent `:*`: the Cursor CLI reads this file too, and matches `Bash(rm -rf *)` against every `rm -rf …`, but `Bash(rm -rf:*)` only against the bare `rm -rf` (references/cursor.md).
- A row with `arguments: "none"` (`env`, `export`, `set` on their own) gets no `Bash` entry. An exact `Bash(env)` would refuse only `env` here, but the Cursor CLI reads this file and matches it as a prefix, refusing `env FOO=1 cmd`, `export FOO=1` and `set -e` too. The hook refuses the bare commands, and the plan names the gap. Shell builtins (`set`, `export`, `source`, `.`) get no `/bin/` spelling.
- A row with `files` (`cat` on a `.env` file) gets no `Bash` entries: they match text, not paths. Claude Code's own Read rules already refuse `cat`, `head`, `tail` and `grep` on a denied file; the hook refuses the rest (`less`, `source`, `.`).
- Deny and ask rules apply to each part of `a && b`, `a; b`, pipes and subshells, and past wrappers such as `timeout`, `nice` and `nohup`.

## File rows

- A `read` row becomes `Read(<path>)`, a `write` row `Edit(<path>)`. Project paths get `./` (the working directory), and `**/` reaches the root and every subfolder; `~/` paths stay as they are. A path with no `/` after the `./` matches at any depth, as in `.gitignore`: `Read(./.env.*)` refuses `sub/.env.local` too.
- **`Write(...)` rules are never checked by Claude Code.** It accepts them and warns at startup; `Edit` covers every file-editing tool. The Cursor CLI reads this file and checks `Write` on its own file tools, against absolute paths, so a `write` row also gets plain `Write(**/<glob>)` entries, which Cursor matches. Cursor's globs know only `*`, so these keep no exception: Cursor refuses writes to `.env.example` too. An old `Write(./…)` entry is listed as an extra: Claude Code ignores it and Cursor never matches a `./` path.
- A `Read` deny also blocks edits to that path.
- **No negation.** Path globs have positive character classes only: `[!e]` and `[^e]` list `!` or `^` and `e`, and on macOS classes match case-insensitively. So an `except` becomes the globs around it: `**/.env.*` minus `**/.env.example` is `.env.`, `.env.e` … `.env.exampl`, each name that leaves `example` at some letter through a class of the other letters, digits, `_` and `.` (`.env.exa[0-9A-LN-Za-ln-z_.]*`), and `.env.example?*`. A name that leaves it through any other character is covered by the hook only. The plan lists an entry on the machine that also refuses the exception as an extra, with a note to remove it by hand.

## MCP-tool rows

- Tools are named `mcp__<server>__<tool>`; a claude.ai connector shows as `mcp__claude_ai_<Name>__<tool>` in the CLI, and a rule naming the server any other way matches nothing there.
- The adapter asks Claude Code for its tools: it starts `claude -p` with `--output-format stream-json --verbose`, reads the tool list from the session's `init` event, and stops the session before it calls the model. Each row's regexes pick the matching names, which become exact deny entries.
- A denied MCP tool is removed from the session, so the agent never sees it.

## Auto mode

A row's `guard` is written as a semantic guard for what its patterns can't list, such as a variable read by `python3 -c` or a script. Source: the repo's research, `docs/research/auto-mode-semantic-guard.md` (6.1).

- **Where:** `autoMode` in `~/.claude/settings.json`, in the same write as the permissions. Claude Code reads `autoMode` only from user, managed and `--settings` files, never from a project's.
- **What:** each guard, as `<label>: <rule>`, in `autoMode.hard_deny`, which the classifier applies whatever the user says and no `allow` entry clears. A new `hard_deny` array starts with `"$defaults"`, which keeps the built-in hard-deny rules; an existing array is the user's, and one without `$defaults` is reported as a gap and left. `autoMode.classifyAllShell: true` sends every shell command to the classifier, so a project's narrow allow rule (`Bash(printenv *)`) can't route around it.
- **Audit:** each guard and `classifyAllShell` show as `present`; the user's other `autoMode` entries (`soft_deny`, `allow`, `environment`, their own `hard_deny` rules) are left alone. The manifest records the guards written, and only those are removed when the table drops them. `claude auto-mode config` prints the rules in effect.
- **What the agent sees:** the rule's label in the denial (`[Environment Variable Access]`), not its text, so the instruction reaches the agent through the rule line in the shared file.
- **Gaps:** it applies only in a session running in auto mode, and a project can set `disableAutoMode`; in a `-p` or SDK session, read-only commands (`echo $TOKEN`, `cat .env`) and file reads skip the classifier. The deny entries and the hook stay the primary guard.

## Gaps

Native entries alone let these through:

- **Commands:** more flags in the same token (`rm -rfv`) or after the operands (`rm x -rf`), options before a subcommand (`git -C dir push --force`), and a command inside another program's string (`bash -lc "…"`, `eval`, a script).
- **Files:** a script or another program that opens the file itself, and `less`, `source` or `.` on a `.env` file.
- **Commands with nothing after them:** `env`, `export` and `set` alone, which have no native entry (see *Command rows*).
- **MCP tools:** a tool connected after the run, until the next run.
- **`$VAR` expansion:** a variable expanded inside another command (`echo $TOKEN`) prints its value, and no rule can tell that from ordinary use. The rule line asks the agent not to, and the auto-mode guard covers interpreters and scripts, not `echo` or `cat` in a `-p` session.

The pre-tool hook closes the command and MCP-tool gaps for deny and allow-and-report rows, so the plan lists, per row, only the command gaps of `ask` rows and the file gap. The hook's own gaps, listed once in its plan section:

- a command inside a script file or another interpreter (`python -c`), built from variables (`$cmd -rf x`), or behind an alias or function defined elsewhere; an abbreviated long option (`--recur`); a force push by refspec (`git push origin +main`);
- a project's `.claude/settings.json` with `"disableAllHooks": true`, which turns every non-managed hook off there.

## Pre-tool hook

- **Wiring:** one `hooks.PreToolUse` group in `~/.claude/settings.json` with matcher `*` (every tool) and one command handler, `python3 <skill>/scripts/pre_tool_hook.py --harness claude-code` wrapped so it fails open: `[ -f <script> ] && python3 <script> … || true`, so a script that's gone (the skill moved or was removed) or an error exit lets the call through instead of exit 2 blocking it, timeout 10 seconds. Against a `--home` other than the user's own, it adds `--config <home>/.config/agents/hook.json`, so a trial reports into that home, and a plan run with `--rules <table>` adds `--rules <table>`, so the hook reads the table the plan used. Settings.json gets one write carrying the permissions, the hook and `autoMemoryEnabled`.
- **Audit:** `wired` when a match-all group runs exactly that command. The manifest records the command; when the skill moves, the old command is removed and the new one added. Other hooks are the user's and stay.
- **Input:** Claude Code's PreToolUse JSON: `tool_name`, `tool_input` (`command` for Bash; `file_path` or `notebook_path` for Read, Edit, MultiEdit, Write and NotebookEdit; `path` for Grep), `cwd`, `session_id`.
- **Answer:** a deny is `hookSpecificOutput.permissionDecision: "deny"` with the refusal in `permissionDecisionReason`, which Claude Code shows the agent. Otherwise it prints nothing and exits 0, so the native permissions decide: it never answers `allow`, which would skip them. It exits 1 when the input or the table can't be read, and the wired command's `|| true` turns that into a silent exit 0; a deny is JSON with exit 0, so it passes through.
- **Reports** are written when the call is submitted, before any permission prompt, so a report means the agent asked to run it.
- **Cursor runs this hook too** (the IDE and the CLI read hooks from `~/.claude/settings.json`, Claude's `PreToolUse` as `preToolUse`). Its payload is read as far as it fits, and a call it recognises is still refused (Cursor passes `permissionDecisionReason` on as `user_message`, which the CLI shows the agent). It writes no report there, seeing `cursor_version` in the payload: the hook Cursor's adapter wires in `~/.cursor/hooks.json` reports each call once.

## What the agent sees

A command the native rules refuse returns `Permission to use Bash with command <command> has been denied.`, and a refused file `File is in a directory that is denied by your permission settings.` Neither names the rule, so the instruction also reaches the agent through the shared file's rule line, loaded at the start of every session.

The hook runs first, and its refusal names each refused part, its rule, reason and instruction, and says nothing else in the call ran.

## Read by other harnesses

The Cursor CLI also reads the `allow` and `deny` lists in `~/.claude/settings.json`, only when both lists are there (so the adapter adds an empty `allow` beside a `deny`), and a project can't remove them. There `Bash(<prefix> *)` matches every use of the prefix with something after it; `Bash(x:*)` with a space in `x` matches only the bare command, and an exact `Bash(env)` would match `env` with any arguments, which is why bare rows get no entry. For its file tools it checks `Read(...)` and `Write(...)` against absolute paths, so it matches the plain `Write(**/…)` entries, but not the `./` Read and Edit entries. What Cursor makes of the rest is in references/cursor.md.

## Checking it

After an apply, in a throwaway folder, with `--setting-sources project,local --settings <the settings.json>` so only the generated entries apply:

- **Commands:** `claude -p "Run exactly: rm -fr x" --allowedTools Bash` leaves `x` in place and quotes the hook's refusal. Allowing `Bash` proves a rule refused it, not the lack of an allow. With a settings file holding only the `hooks` key, `bash -lc "rm -rf x"` is refused too, which proves the hook, not a native entry.
- **Reports:** `gh api rate_limit` runs, and its line appears in the report folder.
- **Files:** asking for a Write to `.env`, `sub/.env.local` and `secrets/k` with `--allowedTools Write` leaves them unchanged, and a Read of `sub/.env.example` still works.
- **Environment:** with fake `.env` files and a fake variable only, and the session started with a scrubbed environment (`HOME`, `PATH`, `USER` and the fake variable), since a sample that gets through prints whatever the shell holds: `printenv`, `env`, `cat .env` and a Read of `sub/.env` are refused, `env FAKE=1 true` runs. With the hooks-only settings file, `bash -c "printenv FAKE"` and `/usr/bin/env | grep FAKE` are refused by the hook, naming the rule's instruction.
- **Mail tools:** a found tool, such as a trash tool, is absent from the session.

Against the real login, `claude -p "Without tools: quote your rule about rm -rf and the file it came from."` quotes the rule line from `~/.config/agents/AGENTS.md`.
