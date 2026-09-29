# Codex adapter

What set-up-machine writes for Codex, and why. The code is `scripts/setupmachine/adapters/codex.py`. Sources: the Codex docs on [rules](https://learn.chatgpt.com/docs/agent-configuration/rules), [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md), [hooks](https://learn.chatgpt.com/docs/hooks) and [memories](https://learn.chatgpt.com/docs/customization/memories), the `openai/codex` source, and the repo's research, `docs/research/harness-capabilities.md` (section 2).

Every path below is under `CODEX_HOME`, `~/.codex` by default. Without that folder the plan says Codex isn't set up and writes nothing for it.

## Global instructions

- Codex reads `~/.codex/AGENTS.md` in every session and follows a symlink; it has no imports. The adapter makes the file a **symlink to the shared file**.
- It links only once nothing in the old file would be lost: each line (headings aside) must already be in the shared file, or sit in a known block that an external skill replaces. Any other line is listed as `extra`, with a `gap` saying Codex still reads its own file; move those lines first (references/global-instructions.md, *Moving a harness's file*), then plan again. Apply keeps the old file in the backup folder.
- A non-empty `~/.codex/AGENTS.override.md` is read instead of `AGENTS.md`; the plan names it as a gap and leaves it.

## External skills

A block a tool wrote into the old file becomes the upstream skill it came from, installed the way **maintain-environment** installs upstream skills:

| Block | Skill | Source |
|---|---|---|
| `<!-- context7 -->` … `<!-- context7 -->` | `find-docs` | `upstash/context7` |

- While `~/.agents/skills/<skill>/SKILL.md` is missing, the plan lists `added external skill …` with the exact command, and apply runs it before writing any file: `npx --yes skills add <source> -s <skill> -g -a codex -y`, plus `-a claude-code` unless `~/.claude/skills` links to `~/.agents/skills`. `HOME` is set to the planned home, so a `--home` trial installs there. If the command fails, nothing is written.
- The Context7 block's advice to run `ctx7` outside the sandbox needs no line of its own: an `allow` rule for `npx ctx7@latest` does that, and the plan lists one as `extra` where the machine has it.

## Memory

- Local memories are off by default. The adapter sets `[features] memories = false` in `config.toml`, editing only that line, and lists every file under `memories/` as `removed`.
- **Gap:** a trusted project's `.codex/config.toml` can set `memories = true` and win; only a system `requirements.toml` pins it.

## Rules

- **File:** `~/.codex/rules/set-up-machine.rules`, owned by the skill and regenerated whole from the table on every run. Codex loads every `*.rules` file in the folder and applies the strictest matching decision, so the user's own files (`default.rules`, where Codex saves "always allow" choices) are read, compared and never written.
- **Levels:** `deny` → `forbidden`, `ask` → `prompt`, `allow-and-report` → `allow`. Codex runs an `allow`ed command outside the sandbox without a prompt; the report half needs the pre-tool hook.
- **Justification:** every rule carries `<reason> Instead: <instruction> (set-up-machine rule <id>)`, which Codex shows the agent on a refusal. Where another file forbids the same prefix without one, the longest matching prefix wins and, on a tie, the file that sorts last, so `set-up-machine.rules` outranks `default.rules`.
- **Compared with the other files:** `tightened` where another file is looser, `stricter` where every spelling is stricter there (kept; the user removes it by hand for the table's level), `extra` for a rule no table row covers. A narrower rule a row covers, such as `rm -rf /`, isn't extra.

## Command rows

- `prefix_rule` matches the argv word by word from the start; a word may be a list of alternatives. The adapter writes one rule for the clustered short flags (`rm [-rf|-Rf|-fr|-fR]`) and one per flag order for separate flags (`rm [-r|-R|--recursive] [-f|--force]`, and the reverse).
- Codex resolves an absolute program path to its basename, so `/bin/rm -rf x` meets the `rm` rules with no rule of its own.
- **Shell rows get no rule.** Codex runs every command as `[<shell>, "-lc", <command>]` (`-c` when the model or `allow_login_shell = false` turns login off), and checks rules against that wrapper whenever the command isn't a plain chain of words (a redirect, `$(…)`). A rule on `bash -c`, `zsh -c` or `bash -lc` would refuse Codex's own wrapper; `codex execpolicy check -- /bin/zsh -c "ls > out"` against `["zsh","-c"]` returns `forbidden`. The pre-tool hook enforces the row instead, since it sees the command before Codex wraps it.

- **Bare rows get no rule** (`arguments: "none"`, such as `env` alone): a prefix rule on `env` would also refuse `env FOO=1 cmd`. The hook enforces them.
- **Rows on files get no rule** (`files`, such as `cat .env`): a prefix rule names one literal word in one position, not a path glob among the operands. The hook enforces them, `except` included, so `cat .env.example` runs. A machine rule that is one case of such a row (`cat .env`) counts as covered, not `extra`.
- A row's own `gap` is printed on its line, and a row's `guard` gets a `none` line: Codex has no semantic guard to carry it.

## File rows

Codex has no file rules: it reads through the shell and writes through the shell and `apply_patch`. The pre-tool hook refuses `apply_patch` edits to a row's paths (the patch's `Add`, `Update`, `Delete` and `Move to` headers). A shell read or write of the path gets through, and the plan lists that gap per row.

## MCP-tool rows

Codex's MCP tools aren't listed before a session starts, so no native entry is written. The hook matches `mcp__<server>__<tool>` against the row's regexes when a tool is called.

## Gaps

Rules alone let these through: flags after the operands (`git push origin main --force`), options before a subcommand (`git -C dir push --force`), and anything inside a script that isn't a plain chain of words. The pre-tool hook closes them for deny and allow-and-report rows, so the plan lists command gaps only for `ask` rows, plus the shell, file and MCP-tool rows above. The hook's own gaps are listed once, in its section: what it can't read (see references/claude-code.md, *Gaps*), and a trusted project's `.codex/config.toml` setting `[features] hooks = false`, which turns every hook off there while the rules still hold. A user `hooks = false` is named as a gap too, and left.

## Pre-tool hook

- **Wiring:** one `hooks.PreToolUse` group in `~/.codex/hooks.json`, matcher `*`, one command handler `python3 <skill>/scripts/pre_tool_hook.py --harness codex`, wrapped to fail open as for Claude Code, timeout 10 seconds, with `--config` and `--rules` added as for Claude Code. Other hooks in the file are the user's and stay; a command the skill wrote before is replaced when the skill moves.
- **Trust:** Codex runs a user hook only once it's trusted in `/hooks`, which records `[hooks.state."<hooks.json path>:pre_tool_use:<group>:<handler>"] trusted_hash = "sha256:…"` in `config.toml`. The plan writes that entry itself: the hash is sha256 over the canonical JSON of the hook's identity (`event_name`, `matcher`, the handler with `type`, `command`, `timeout`, `async`), and Codex's own `hooks/list` reports the hook `trusted`. Approving the plan is the review `/hooks` would ask for. The hash covers the command, not the script's content, so updating the skill in place keeps the trust.
- **Audit:** `wired` when the group runs exactly that command and its trust entry holds the current hash.
- **Input:** `tool_name` is `Bash` for the shell tools, with `tool_input.command` as the model wrote it (before the `-lc` wrapper); `apply_patch` with the patch in `tool_input.command`; or `mcp__<server>__<tool>`. Also `cwd` and `session_id`.
- **Answer:** the same as Claude Code's, `hookSpecificOutput.permissionDecision: "deny"` with the refusal in `permissionDecisionReason`. Codex passes it to the model as `Command blocked by PreToolUse hook: <reason>. Command: <command>`.

## What the agent sees

- A forbidden rule: `` exec_command failed: … `/bin/zsh -lc 'rm -fr x'` rejected: <justification> ``.
- The hook, which runs first: its refusal, naming each refused part, its rule, reason and instruction.

## Checking it

- **Rules:** `codex execpolicy check --resolve-host-executables --rules <home>/.codex/rules/set-up-machine.rules -- <command>` for each sample; add `--rules` for each other file there to see what Codex decides. The check doesn't unwrap `bash -lc`, so pass the inner command.
- **Hook trust:** `codex app-server` with `CODEX_HOME=<home>/.codex`, then `hooks/list` for a throwaway folder: the group is `trusted`.
- **A session without a login:** `codex exec` with `CODEX_HOME` and `HOME` at the trial home and a `model_providers` entry pointing at a local stand-in that answers the Responses API with one `exec_command` (or `apply_patch`) call; the next request's `function_call_output` is what the agent read. With `--disable hooks` it shows the rule's justification, and with hooks on the hook's refusal.
- **Instructions:** `codex debug prompt-input hello` in a throwaway folder shows the shared file's rule line, and no Context7 block.
