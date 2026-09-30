# What a project's harness files can do to the global rules

The facts behind the audit, per harness. The global rules are the machine's safety rails, written by **set-up-machine** from its rule table; a project's own files are for convenience and add only `allow` entries for the project's own commands. Harness formats change: check the docs set-up-machine's harness references link. Sources: the repo's research, `docs/research/harness-capabilities.md` (each harness's section 5, "Can a project override the global rules?") and `docs/research/auto-mode-semantic-guard.md` (1.3).

## How the audit reads a rule

Each deny and ask row of set-up-machine's `rules.json` carries `samples.covers`: commands (`rm -fr x`, `git push --force-with-lease`), paths (`.env`, `sub/.env.local`, `~/.ssh/id_ed25519`) or MCP tool names. A project entry that matches one of them, by the harness's own matching below, covers the rule; for an MCP row, also check the row's `server` and `tool` regexes against the entry. `allow-and-report` rows are left out: a project allow can't make them looser. Check every harness's files, whether or not that harness is set up on this machine.

## Findings

- `weakens`: in at least one harness, the rule no longer holds as the machine sets it. The audit fails.
- `overlaps`: a project allow covers the rule's command, and the rule still wins everywhere. Listed so the entry can be narrowed; allow-only means a project's allow names its own commands, not a rail's.
- `extra`: a project deny or ask. Kept; a rail every project needs is a row in the rule table instead.
- `gap`: something the audit can't judge, named so it isn't read as passed.

## Claude Code: `.claude/settings.json`, `.claude/settings.local.json`

- **Permissions can't be loosened.** A user deny or ask wins over any project allow.
- **Auto mode:** a project allow over a deny command row is `overlaps`: the user's deny and the pre-tool hook still refuse the command. `autoMode` is read only from user settings, so a project's is a `gap` that does nothing.
- **Switches that weaken:** `"disableAllHooks": true` turns every hook off, the pre-tool hook included; `"autoMemoryEnabled": true` turns memory back on; `"disableAutoMode"` turns auto mode off. Each is `weakens`.
- **Read by the Cursor CLI too:** it unions the `allow` and `deny` lists of the project's `.claude/settings.json` (not `settings.local.json`) with its own, and has no ask level. So an allow there that covers an ask row (`Bash(git push *)` over `git push --force-with-lease`) is `weakens`: the Cursor CLI runs it without a prompt.

## Cursor CLI: `.cursor/cli.json`, from the git root down

- **A list replaces the global one.** The project's `permissions.deny` replaces `~/.cursor/cli-config.json`'s, so a list missing any global entry (`"deny": []`) is `weakens`; the deny lists in `~/.claude/settings.json` and the pre-tool hook still hold. A project deny beyond the global list is `extra`.
- **No ask level:** an allow covering an ask row is `weakens`. One covering a deny row is `overlaps`, since deny wins over allow.
- **Matching:** `Shell(p)` covers `p` alone or followed by a space, `Shell(p:)` `p` alone, `Shell(cmd:args)` a one-word command whose arguments match the glob; `*` matches anything. `Read`, `Write` and `Mcp(server:tool)` as set-up-machine's references/cursor.md says.
- **Hooks** can't be turned off by a project.

## opencode: `opencode.json`, `opencode.jsonc`, `.opencode/opencode.json(c)`

- **Permissions can be loosened.** A project's config merges over the global one: a pattern already in the global config changes level in place, and a new one goes after the global rules, where the last match wins. So the audit merges the project's `permission` over the global config and asks, per sample, which level opencode would apply; a looser one than the global config gives is `weakens`, naming the entry that wins. A tool set to one level (`"read": "allow"`) replaces the tool's whole global object.
- **Agents:** an `agent.<name>.permission` in the project config is merged after, and checked the same way.
- **Plugins:** a project plugin (`plugin` in the config, or a file in `.opencode/plugin/` or `.opencode/plugins/`) runs after the global pre-tool hook and can rewrite a call's arguments once the hook has passed them. The audit can't read what it does, so it's a `gap`: read it.

## Codex: `.codex/config.toml`

- **Rules can't be loosened:** Codex applies the strictest decision across every `.rules` file.
- **Switches that weaken,** in a trusted project: `[features] hooks = false` turns every hook off, the pre-tool hook included; `[features] memories = true` turns memories back on. Each is `weakens`, in either the `[features]` table or a dotted `features.<name>` key.

## Not audited

Named so nothing here reads as checked: opencode agents defined in `.opencode/agent/*.md` and config files below the project root; Cursor IDE's `.cursor/permissions.json` (`allow_instructions` only steer its classifier) and `.cursor/hooks.json` (hooks only add); Claude Code's `env` key in project settings; Codex's approval, sandbox and auto-review settings, which the rule table doesn't set.

## Fixing a line

A project harness file is the project's: change it only with the user's approval. For `weakens`, remove the entry or narrow it to the project's own commands (`Bash(npm test *)` rather than `Bash(npm *)`, never a pattern that reaches a rail's command). For a rail the project wants (a deny, or a stricter level), add it through `/set-up-machine`'s rule table when every project needs it, else keep it as an `extra`.
