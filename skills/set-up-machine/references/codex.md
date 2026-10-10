# Codex

How to set up and audit Codex from the rule table. Docs: [rules](https://learn.chatgpt.com/docs/agent-configuration/rules), [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md), [hooks](https://learn.chatgpt.com/docs/hooks), [memories](https://learn.chatgpt.com/docs/customization/memories), and the `openai/codex` source where the docs are silent. Background: the repo's `docs/research/harness-capabilities.md`, section 2.

**Found** when the resolved Codex config home exists or `codex` is on `PATH`; a fresh install makes the folder only on first start. Resolve the non-secret `CODEX_HOME` internally, falling back to `~/.codex`, without printing its environment value. Use that one folder for `config.toml`, instructions, profiles, rules, hooks and trust checks. Every relative Codex path below is under it. For a fixture home, pass `verify.py --home <fixture>`; it uses `<fixture>/.codex` and ignores ambient `CODEX_HOME`. Pass `--codex-home <fixture config folder>` when testing a different layout.

## CLI defaults

When the personal source pointer names a repository, load its optional `agents/codex.toml` as `workstation.md` specifies. Validate the entire file before proposing preference writes. `scripts/setupmachine/codex_config.py` supplies allowlisted parsing, a pure proposal and persisted audit; it never writes configuration. Its TOML checks require Python 3.11+; on an older Python, report the parser support gap and leave preferences unchanged.

### Installed support

Check `codex --version`, current help and the [official configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference) for each declared key and value. Use the installed CLI's configuration schema or a synthetic configuration check with one invalid-value negative control per declared key, without authentication or secrets. The checker uses an isolated temporary config home for `codex features list`; it must accept the declared value and reject its negative control. A successful parse alone is insufficient: unknown keys and some conflicts may be ignored. Report unsupported keys, values or an unavailable validation mechanism as gaps and leave those preferences unchanged.

The inspected CLI was 0.159.3 on 2026-10-01. That snapshot supported:

| Key | Values accepted for this source |
|---|---|
| `sandbox_mode` | `read-only`, `workspace-write`, `danger-full-access` |
| `approval_policy` | `on-request`, `never` |
| `approvals_reviewer` | `user`, `auto_review` |

Treat the snapshot as evidence to recheck, not a permanent version gate. Explicit `untrusted` is unsupported and `on-failure` deprecated in this version. Codex also supports granular approval policies, but this initial private source accepts scalar policies only. Report a granular source as unsupported; preserve an existing granular target policy and report the need for review.

### Propose and apply

Compare each declared preference with its top-level persisted value in `config.toml`. Mark matches `present, personal` and show the exact current and proposed entries for each safe difference, marked `personal`. Mark a stricter replacement `tightened` only when its ordering is established; report drift as a failed audit. Omitted keys remain user-managed. Compose preference edits with this adapter's existing memory and hook trust edits in the same proposed diff. `propose(text, preferences)` returns proposed TOML without writing and raises `ConfigError` for preservation or support gaps; its fixture tests exercise fresh setup, preservation and repeat audit. Then use the skill's approval and backup steps before writing. When the config home is outside the user's home, include an explicit destination under the backup folder in the diff and preserve that config home's relative paths there, so the backup does not escape its folder or collide with another file.

Preserve unrelated keys, comments, profiles, hooks, rules and TOML sections. Keep an existing stricter sandbox restriction or enforced constraint and report `stricter` or `gap`; do not infer that every difference between approval policies can be ordered. Report policy conflicts whose effect cannot be established. Leave unfamiliar or uneditable TOML syntax unchanged and name the gap instead of rewriting the whole file.

**When `default_permissions` conflicts with a proposed legacy sandbox key:** preserve the permission configuration and report the incompatibility. The [configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference#configtoml) forbids `default_permissions` together with `sandbox_mode` or `[sandbox_workspace_write]`; setup does not silently migrate between permission models. Inspect applicable enforced requirements through documented non-secret configuration fields, and report restrictions that prevent the preference from taking effect.

### Overrides and activation

Report persisted defaults separately from effective settings. The [official precedence order](https://learn.chatgpt.com/docs/config-file/config-basic#configuration-precedence) is CLI flags and `--config`, trusted project config from the nearest project outward, the selected profile, user config, cloud defaults, system config and built-in defaults. The [managed configuration guide](https://learn.chatgpt.com/docs/enterprise/managed-configuration#admin-enforced-requirements-requirementstoml) describes enforced requirements that constrain the result separately. Identify observed overrides without claiming every layer was verified; cloud settings, active CLI arguments and existing session state and MDM requirements may be unavailable to a file audit.

Read profile and trusted-project configuration only when needed to check declared defaults, using non-secret fields and reporting inaccessible layers as unverified. Preserve profile files. The [advanced configuration guide](https://learn.chatgpt.com/docs/config-file/config-advanced) places profiles in separate `<name>.config.toml` files under the config home; legacy inline `[profiles]` and top-level `profile` are unsupported from 0.134.0 and must be reported rather than migrated.

Explain that persisted changes affect subsequent sessions. Keep running sessions open; the user can start a new session or adjust permissions through `/permissions` where that installed version supports it. `auto_review` routes eligible `on-request` or granular approvals to a reviewer; it keeps sandbox boundaries and does not guarantee approval. A matching persisted reviewer is not proof that an existing session or every approval uses it.

## Global instructions

- Codex reads `AGENTS.md` in every session and follows a symlink; it has no imports. It becomes a **symlink to the shared file**, `~/.config/agents/AGENTS.md`.
- Link it only once nothing in the old file would be lost: each line (headings aside) is already in the shared file, or sits in a known block below. Every other line is `extra`, with a `gap` saying Codex still reads its own file; move those lines first (global-instructions.md, *Moving a harness's file*), then run again. The old file is `removed` (backed up).
- A non-empty `AGENTS.override.md` is read instead of `AGENTS.md`: a `gap`, left alone.

### Blocks that become a skill

A block a tool wrote into the old file becomes the upstream skill it came from, installed globally before any file is written:

| Block | Skill | Command |
|---|---|---|
| `<!-- context7 -->` … `<!-- context7 -->` | `find-docs` | `npx --yes skills add upstash/context7 -s find-docs -g -a codex [-a claude-code] -y` |

Add `-a claude-code` unless `~/.claude/skills` is a link to `~/.agents/skills`. It's `present` once `~/.agents/skills/find-docs/SKILL.md` exists. The block's advice to run `ctx7` outside the sandbox needs no line: an `allow` rule for `npx ctx7@latest` does that, and is `extra` where the machine has it.

## Memory

- Local memories are off by default and write `memories/`. Set `memories = false` in the `[features]` table of `config.toml` (or tighten `features.memories = …` where the file uses the dotted form), editing only that line; list every file under `memories/` as `removed`. A `features = { … }` inline table is edited by the user.
- **Gap:** a trusted project's `.codex/config.toml` can set `memories = true` and win; only a system `requirements.toml` pins it.

## Rules

- **File:** `rules/set-up-machine.rules`, this skill's own, written whole from the table and the personal permissions every run. Codex loads every `*.rules` file in `rules/` and applies the **strictest** matching decision, so the user's files (`default.rules`, where "always allow" choices land) are read and compared, never written.
- **Levels:** `deny` → `forbidden`, `ask` → `prompt`, `allow-and-report` → `allow` (runs outside the sandbox without a prompt; the hook reports).
- **Form:** the file starts with two comment lines (`# Generated by set-up-machine from its rule table and the workstation repo's rows: change those, not this file.` and `# Codex loads every *.rules file here; the strictest matching decision wins.`), then one `prefix_rule` per line:

  ```python
  prefix_rule(pattern=["rm", ["-rf", "-Rf", "-fr", "-fR"]], decision="forbidden", justification="A recursive forced delete can't be undone, and one wrong path loses work outside the task. Instead: Move what's no longer needed into … (set-up-machine rule rm-recursive-force)")
  ```

  The `justification` is `<reason> Instead: <instruction> (set-up-machine rule <id>)` (no `Instead:` for ask and allow-and-report rows); Codex shows it to the agent on a refusal.
- **Compared with the other files:** `tightened` where another file is looser (the strictest wins, so this file's rule takes over), `stricter` where every case is stricter there (kept; the user removes it by hand), `extra` for a rule no row covers. A narrower rule a row covers (`rm -rf /`) isn't extra.

## Command rows

- `prefix_rule` matches the argv word by word from the start; an element is one word or a list of alternatives. Codex resolves an absolute program path to its basename, so `/bin/rm` needs no rule.
- **Flags:** one rule with the clustered one-letter flags as alternatives (`["rm", ["-rf", "-Rf", "-fr", "-fR"]]`), and, when a row has two or more flag groups, one rule per order of the groups, each group its spellings (`["rm", ["-r", "-R", "--recursive"], ["-f", "--force"]]` and the reverse). A single group is one element of its spellings: `["git", "push", ["-f", "--force"]]`.
- **Operands:** one-word alternatives share one element (`["chmod", "-R", ["777", "0777", "a+rwx", …]]`); longer ones are a rule each. `any_operand` rows can only name the word right after the flags (`["git", "push", ["-d", "--delete"], "origin", ["main", "master"]]`): name the gap for other remotes and positions.
- **No rule, and a gap instead:**
  - **Shell rows** (`bash -c`): Codex runs every command as `[<shell>, "-lc", <command>]` and checks rules against that wrapper whenever the command isn't a plain chain of words, so a rule on `bash -c`, `zsh -c` or `bash -lc` would refuse its own wrapper (`codex execpolicy check -- /bin/zsh -c "ls > out"` against `["zsh","-c"]` returns `forbidden`).
  - `arguments: "none"` or `"flags"` rows: a prefix rule on `env` would refuse `env FOO=1 cmd` too.
  - `variables` rows (`echo $API_TOKEN`): a prefix rule can't match a variable's name inside an argument.
  - `files` rows (`cat .env`): a prefix rule names a literal word in one place, not a path glob. A machine rule that is one case of such a row (`["cat", ".env"]`) is covered, not `extra`.

The hook enforces each of these, since it sees the command before Codex wraps it.

## File rows

Codex has no file rules: it reads through the shell and writes through the shell and `apply_patch`. The hook refuses `apply_patch` edits to a row's paths (its `Add File`, `Update File`, `Delete File` and `Move to` headers); a shell read or write gets through, a `gap` per row.

## MCP-tool rows

Codex configures each MCP tool in `config.toml` ([configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference); the `openai/codex` source at `2685e3a`, `codex-rs/config/src/mcp_types.rs` and `types.rs`). A connector such as Gmail or Google Calendar is an **app**, under `[apps.<app-id>]`; any other server is under `[mcp_servers.<server-id>]`. Match each row's `server` regex against those IDs and its `tool` regex against the tool names a session lists; with no tool listing, a matching row is a `gap` and the hook still matches `mcp__<server>__<tool>` when a tool is called.

| Row | `[mcp_servers.<id>]` | `[apps.<id>]` |
|---|---|---|
| `deny` | the tool in `disabled_tools = [...]` | `[apps.<id>.tools.<tool>]` `enabled = false` |
| `ask` | `[mcp_servers.<id>.tools.<tool>]` `approval_mode = "prompt"` | `[apps.<id>.tools.<tool>]` `approval_mode = "prompt"` |
| `ask` with `approver: "user"` | as `ask`, and a `gap` while the top-level `approvals_reviewer` is `auto_review`: a server has no reviewer of its own | as `ask`, plus `approvals_reviewer = "user"` in `[apps.<id>]`, so the automatic reviewer never answers it |

- **Reviewer order for an app:** a connected account's `[apps.<id>.links.<link-id>]`, then `[apps.<id>]`, then `[apps._default]`, then the top-level `approvals_reviewer`. Mark a lower layer that sets `auto_review` a `gap` when it wins.
- **`codex exec`:** it runs with approval policy `never`. A `prompt` tool is then refused, except under a full-access, disabled or external permission profile (such as `danger-full-access`), where it runs without asking; only `disabled_tools` or `enabled = false` stop it there. The hook reads `permission_mode`, which Codex sets to `bypassPermissions` under `never`, and refuses `approver: "user"` rows.
- `approval_mode = "approve"` runs a tool without asking: on a tool a `deny` or `ask` row matches, it's looser than the table, so tighten it.

## Personal permissions

A personal permission (workstation.md) becomes `prefix_rule`s the way a table row of its kind does above, in `rules/set-up-machine.rules` after the table's rules, each marked `personal`. An `allow` row gets `decision="allow"`, as an `allow-and-report` row does: the command runs outside the sandbox without a prompt.

- **Its tool exists** for a command row when one of its programs is on `PATH`; otherwise the row is `n/a` here. File rows, and MCP-tool rows without a tool listing, get no rule, as above: a `gap` for a `deny` or `allow-and-report` row, which the hook still enforces, and for an `allow` row, which Codex then leaves to its own approval settings.
- **It can't loosen a table row:** the strictest matching decision wins, so a personal `allow` never overrides the table's `forbidden` or `prompt`.
- The `justification` takes the table's form and ends `(set-up-machine personal rule <id>)`, so the agent can tell a personal rule from the table's.

## Plugins

Install bundles from their declared marketplace with the installed CLI. Check [developer commands](https://learn.chatgpt.com/docs/developer-commands) before writing.

1. Register a missing marketplace with `codex plugin marketplace add <owner>/<repo> --json`.
2. Install the declared bundle with `codex plugin add <plugin>@<marketplace> --json`.
3. Inspect its manifest for components Codex supports.
4. Report unsupported components as gaps, even when the install succeeds.

Codex 0.162.1 accepts portable Claude-compatible bundles. A Claude LSP declaration or harness-specific mod API does not establish working Codex tools. Read the bundle's manifest before claiming parity.

For a standalone MCP entry, merge `server` into `[mcp_servers.<name>]`. Preserve fields the entry does not declare. Authenticate through `codex mcp login <name>` when required.

A bundle can declare `codex_mcp`, keyed by its server names. Merge each policy into `[plugins."<plugin>@<marketplace>".mcp_servers.<server>]`. Supported fields are `enabled`, `enabled_tools`, `disabled_tools`, `default_tools_approval_mode`, and `tools.<tool>.approval_mode`. `require_oauth` is an audit requirement, not a Codex setting.

Use `scripts/setupmachine/codex_plugins.py`'s pure `propose(text, entry)` before writing. It preserves undeclared settings and comments. It keeps existing stricter tool lists. It refuses unfamiliar TOML forms instead of rewriting the file. Apply the skill's backup and approval steps to its returned diff.

For `require_oauth: true`, keep the server disabled until the CLI confirms OAuth. Never test by making an anonymous tool call. Disabled servers report `unsupported` in `codex mcp list --json`. Temporarily enable the server for a listing-only check, then restore it unless authentication is confirmed. Codex 0.162.1 serializes the authenticated status as `o_auth`.

On a headless machine, the browser's callback points at the wrong machine. Keep the login process running. Have the user forward the callback to the listener on the machine running Codex. Treat its URL as a secret. Never put it in repository files, logs, or shell history.

`verify.py` checks configured enablement, a matching cached manifest, and each declared transport or policy field. It uses the resolved Codex home. With a CLI, it checks OAuth through `codex mcp list --json`, without reading credentials. A missing sign-in is a `gap` with the user's login command. The file audit cannot prove current-session tool discovery, account identity, credit balance, or remote catalog freshness. Verify discovery in a new session.

Honor excluded features in every setup phase. Never invoke an excluded tool, including for a capability test. An exclusion is a personal choice, independent of the approval reviewer. Verify its configured restriction without calling the service. Match personal permissions against the observed server name.

Official sources: [MCP configuration](https://learn.chatgpt.com/docs/extend/mcp), [developer commands](https://learn.chatgpt.com/docs/developer-commands), and [plugin formats](https://developers.openai.com/plugins/build/plugins).

## Pre-tool hook

- **Wiring:** one match-all group in `hooks.json` (keep the user's groups):

  ```json
  {"hooks": {"PreToolUse": [{"matcher": "*", "hooks": [{"type": "command", "timeout": 10,
    "command": "[ -f <script> ] && python3 <script> --harness codex || true"}]}]}}
  ```

  `<script>` and the fail-open wrapping are in SKILL.md, *Wiring*.
- **Trust:** Codex runs a user hook only once it's trusted, which `/hooks` records in `config.toml`. Write that entry yourself, as part of the approved diff: approving the whole diff stands in for Codex's own hook review.

  ```toml
  [hooks.state."<absolute path of hooks.json>:pre_tool_use:<group index>:<handler index>"]
  trusted_hash = "sha256:…"
  ```

  Indexes count from 0 in `hooks.json`'s `PreToolUse` list and that group's `hooks`. Get the hash with `python3 <this skill>/scripts/verify.py --codex-trust-hash '<command>'`: sha256 over the canonical JSON (sorted keys, no spaces) of the hook's identity, `{"event_name": "pre_tool_use", "matcher": "*", "hooks": [{"type": "command", "command": <command>, "timeout": 10, "async": false}]}`. It covers the command, not the script's content, so updating the skill in place keeps the trust; a changed command needs a new entry, and the old one is `removed`.
- **Audit:** `wired` when the group runs exactly that command and its trust entry holds the current hash; `verify.py` checks both. `[features] hooks = false` in `config.toml` turns every hook off: a `gap`, left to the user.
- **Input:** `tool_name` is `Bash` for the shell tools, with `tool_input.command` as the model wrote it (before the `-lc` wrapper); `apply_patch`, with the patch in `tool_input.command`; or `mcp__<server>__<tool>`. Also `cwd`, `session_id` and `permission_mode`: `bypassPermissions` when the approval policy is `never`, otherwise `default`. Nothing in it shows the reviewer.
- **Answer:** the same as Claude Code's (`permissionDecision: "deny"` with the reason). Codex passes it on as `Command blocked by PreToolUse hook: <reason>. Command: <command>`.
- **Gap:** a trusted project's `.codex/config.toml` can set `[features] hooks = false`; the rules still hold.

## Gaps

Rules alone let through flags after the operands (`git push origin main --force`), options before a subcommand (`git -C dir push --force`), and anything that isn't a plain chain of words. The hook closes them for deny and allow-and-report rows, so list them only for `ask` rows, beside the rows above that get no rule. The hook's own misses are in SKILL.md, *What it can't see*.

## What the agent sees

A forbidden rule: `` exec_command failed: … `/bin/zsh -lc 'rm -fr x'` rejected: <justification> ``. The hook, which runs first: its refusal, naming each refused part, its rule, reason and instruction.

## Checking it

- `verify.py` runs each plain command sample through `codex execpolicy check --resolve-host-executables --rules <each rules file> -- <argv>`. A `differs` line should be a row this file says gets no rule; any other is a mistake in the rules file. The check doesn't unwrap `bash -lc`.
- **Hook trust:** `codex app-server` with `CODEX_HOME` at the folder, then `hooks/list` for a throwaway folder: the group is `trusted`.
- **A session without a login:** `codex exec` with `CODEX_HOME` and `HOME` at a trial home and a `model_providers` entry pointing at a local stand-in that answers the Responses API with one `exec_command` (or `apply_patch`) call; the next request's `function_call_output` is what the agent read. With `--disable hooks` it shows the rule's justification, and with hooks on the hook's refusal.
- **Instructions:** `codex debug prompt-input hello` in a throwaway folder shows the shared file's rejection guidance, and no Context7 block.
