# Decisions: set-up-machine

The decisions behind the `set-up-machine` skill. This file is for maintaining it and is never installed. Add an entry for each new decision, in the shape from [index.md](index.md). The spec is "Spec: every harness and project is set up and audited from the skills" (#49).

## 2026-10-11: checks and steps run cursor-agent

- **Status:** accepted
- **Context:** The skill runs the Cursor CLI for MCP enable and for the headless checks. The name `agent` belongs to another CLI.
- **Options:** Run `agent`: a step can start the wrong program.
- **Choice and why:** Run `cursor-agent` in every check and step, since that name is the Cursor CLI's alone.
- **Consequences:** Earlier entries that say `agent` keep the old name as a record.

## 2026-10-11: the audit checks Cursor's copy of the global instructions

- **Status:** accepted
- **Context:** Cursor reads `~/.cursor/rules/global-instructions.mdc`, a copy of the shared file. The other harnesses follow a link, so they cannot drift. The audit checked Auto-review and the sandbox, and a stale copy still passed.
- **Options:** None considered.
- **Choice and why:** `verify.py` fails when the copy is missing or differs from the shared file. It leaves alone a file that lacks the generated comment, since that file is not the skill's.
- **Consequences:** A stale Cursor copy now fails the audit.

## 2026-10-10: install the latest release and reproduce the setup process

- **Status:** accepted
- **Context:** Reproducibility could mean freezing machine software at recorded versions. Earlier recommendations preferred fixed Pi package versions or tags. This entry replaces them.
- **Options:** Freeze each tool at a recorded version: it keeps old software as the desired state.
- **Choice and why:** Reproduce the selected tools, configuration, guardrails and installation steps, not the versions. Use the latest stable release for released tools. Use the latest default branch for code distributed from a repository. Apply this to every selected harness, skill, plugin, package and command-line tool.
- **Consequences:**
  - Installed versions and source commits stay as audit history. Historical citations, test fixtures and application lockfiles stay as evidence.
  - An update keeps local modifications, installation channels, authentication and unrelated settings.
  - The agent checks compatibility and guardrails against the new version. A failed check is reported. It never makes an old version the desired state.

## 2026-10-10: the verifier proves configuration, not installed code

- **Status:** accepted
- **Context:** A declaration that matches the machine proves configuration, but not that the installed code is current.
- **Options:** Let the verifier check upstream versions: it would need to download, and the verifier is read-only.
- **Choice and why:** The read-only verifier reports the difference and downloads or modifies nothing. The agent checks upstream freshness separately, during inspection.
- **Consequences:** Unavailable version metadata is a gap, not proof of latest.

## 2026-10-01: the session-host fallback keeps the occupied caller open

- **Status:** accepted
- **Context:** The session-host role's fallback had an example that gave the user a command to release the caller's own worktree. That contradicts the settlement decisions in [Workflow: Make Herdr and Treehouse settlement reliable without closing topology](https://github.com/yahyabedirhan/skills/issues/123).
- **Options:** None considered.
- **Choice and why:** Remove the example. The fallback keeps the caller and its occupied worktree open.
- **Consequences:** This changes the source role guidance only. Reconciling each machine stays a follow-up after the merge.

## 2026-09-29: the rule table is JSON

- **Status:** accepted
- **Context:** The reconcile script and the pre-tool hook read the rule table with Python 3's standard library. macOS ships Python 3.9, which has no TOML reader (`tomllib` is 3.11+).
- **Options:** TOML: no reader in the standard library on macOS.
- **Choice and why:** JSON, which every supported Python reads.
- **Consequences:** The reconcile script went with [2026-09-30: the agent sets each harness up from its reference](#2026-09-30-the-agent-sets-each-harness-up-from-its-reference-81). The hook and `verify.py` still read the JSON table.

## 2026-09-29: a row describes a command by its meaning

- **Status:** accepted
- **Context:** Claude Code matches text, Codex matches token prefixes, and the hook matches normalised commands. A row in one native form serves only one of them.
- **Options:** Store native patterns: each harness would need its own copy, and one would become the source.
- **Choice and why:** `match` names the program and the flag groups it carries. Each harness expands that into its own native form. For Claude Code that is one entry per flag order, spelling and `/bin/` or `/usr/bin/` path. One row then serves every harness, and no native form is the source.
- **Consequences:** Each harness needs a way to expand a row.

## 2026-09-29: the shared global instructions file is ~/.config/agents/AGENTS.md

- **Status:** accepted
- **Context:** Every harness needs one global instructions file that no harness owns.
- **Options:** `~/.agents/`: it belongs to the `skills` CLI, which owns what is in it.
- **Choice and why:** `~/.config/agents/AGENTS.md`. It sits in no harness's folder, so no harness update or reinstall overwrites it. `~/.config` is the usual place for user config on Linux, the VPS's system. Codex and opencode read the name `AGENTS.md`, so they can link to it directly.
- **Consequences:** Each harness needs a link, an import or a copy to reach the file.

## 2026-09-29: Claude Code reaches the shared file by an @ import

- **Status:** replaced by [2026-09-30: ~/.claude/CLAUDE.md is a symlink to the shared file](#2026-09-30-claudeclaudemd-is-a-symlink-to-the-shared-file-89)
- **Context:** Claude Code has no global `AGENTS.md`.
- **Options:** None considered.
- **Choice and why:** Add an `@` import line to `~/.claude/CLAUDE.md`. Imports in user-scope files load without approval. The adapter adds only that line, since the rest of that file is rewritten under its own ticket.
- **Consequences:** `~/.claude/CLAUDE.md` holds one line the skill owns.

## 2026-09-29: the skill owns a marked block in the shared file

- **Status:** accepted
- **Context:** The shared file holds generated rule lines and the person's own workflow.
- **Options:** None considered.
- **Choice and why:** The skill regenerates the rule lines between `set-up-machine:rules` markers and touches nothing outside them.
- **Consequences:** The person can keep their own workflow in the same file.

## 2026-09-29: a manifest records what the skill wrote

- **Status:** replaced by [2026-09-30: no manifest](#2026-09-30-no-manifest)
- **Context:** The skill must never remove or loosen an entry it did not write, and that must be checkable.
- **Options:** None considered.
- **Choice and why:** A manifest beside the shared file (`~/.config/agents/set-up-machine.json`) names what the skill wrote. An entry is the skill's only if the manifest names it, and only those entries are removed when the table drops them.
- **Consequences:** An entry that was on the machine before the skill stays the user's, even when it matches the table.

## 2026-09-29: tightening adds an entry and never moves one

- **Status:** accepted
- **Context:** A rule on the machine can be looser than the table asks for.
- **Options:** Move the looser entry to the stricter level: that removes an entry the skill did not write.
- **Choice and why:** Add the stricter entry only. Claude Code checks deny before ask before allow, so the added entry is enough.
- **Consequences:** The looser entry stays on the machine.

## 2026-09-29: apply takes the plan's id

- **Status:** replaced by [2026-09-30: the agent sets each harness up from its reference](#2026-09-30-the-agent-sets-each-harness-up-from-its-reference-81)
- **Context:** Time can pass between the plan and the apply, so "one approval" must still mean the diff the user saw.
- **Options:** None considered.
- **Choice and why:** The plan's id is a hash of every write it would make. Apply takes the id, writes exactly that diff, and refuses if anything changed in between.
- **Consequences:** A changed machine needs a new plan.

## 2026-09-29: every step takes --home

- **Status:** replaced by [2026-09-30: the agent sets each harness up from its reference](#2026-09-30-the-agent-sets-each-harness-up-from-its-reference-81)
- **Context:** Tests and trials of a table change must not touch the real machine.
- **Options:** None considered.
- **Choice and why:** Every step takes `--home`, so tests run against a copy of the home folder. The real machine changes only through a plan the user approved.
- **Consequences:** Trials need a copied home folder.

## 2026-09-29: extras and gaps are reported, not changed

- **Status:** accepted
- **Context:** The machine can hold rules the table lacks, and a harness can lack a way to express a row.
- **Options:** None considered.
- **Choice and why:** A rule on the machine that the table lacks is listed as `extra`, so the table can grow from it. What a harness cannot express is listed as a `gap`, so no one reads it as enforced.
- **Consequences:** The user decides what to do with each extra.

## 2026-09-29: checking a live session needs the real login

- **Status:** accepted
- **Context:** A session pointed at a copied config folder (`CLAUDE_CONFIG_DIR`, or `HOME`) is not logged in.
- **Options:** None considered.
- **Choice and why:** The end-to-end check that the rule line reaches a session runs after the real apply. Before it, a `claude -p` run with the copied `settings.json` proves the generated deny entries refuse `rm -rf` and its variants.
- **Consequences:** Part of the check waits until after the real write.

## 2026-09-29: match has three kinds (#53)

- **Status:** accepted
- **Context:** The full rule table covers commands, files and MCP tools.
- **Options:** None considered.
- **Choice and why:** `match` has three kinds, told apart by their keys: a command (`program`, `subcommands`, `flags`, `operands`), a file (`paths`, `access`) and an MCP tool (`server`, `tool` regexes). Each still says what a rule covers by meaning, so the adapters and the hook read the same row with the standard library.
- **Consequences:** Each harness and the hook handle all three kinds.

## 2026-09-29: rows group a family, not one command (#53)

- **Status:** accepted
- **Context:** Many commands share one meaning, such as `gh repo delete`, `archive`, `unarchive` and `rename`.
- **Options:** One row per command: the shared file would get one line per command.
- **Choice and why:** One row per family, so the shared file gets one line per meaning. The families are today's Claude Code deny list, read by meaning.
- **Consequences:** A command pattern that named one account (a connector ID) is not carried over.

## 2026-09-29: zsh -c joins bash -c and sh -c (#53)

- **Status:** accepted
- **Context:** The spec names `bash -c`, `sh -c` and `zsh -c` as ways around the `rm -rf` rule.
- **Options:** None considered.
- **Choice and why:** Add `zsh -c` to the row, beside `bash -c` and `sh -c`.
- **Consequences:** None beyond the row.

## 2026-09-29: writes to .env and secrets/ are Edit rules (#53)

- **Status:** accepted
- **Context:** Claude Code accepts `Write(...)` rules and never checks them. A probe with only `Write` denies let every write through. A probe with only `Edit` denies refused them.
- **Options:** `Write(...)` rules: they do nothing.
- **Choice and why:** Use `Edit(...)` rules for writes.
- **Consequences:** An old `Write(...)` entry is reported as an extra that does nothing, and kept, since the skill did not write it.

## 2026-09-29: secret paths reach every folder (#53)

- **Status:** accepted
- **Context:** Root-only entries miss `.env` files in subfolders.
- **Options:** Root-only entries: they miss `sub/.env`.
- **Choice and why:** Use globs such as `**/.env`. A probe confirmed `./**/.env` refuses both `.env` and `sub/.env`.
- **Consequences:** The old root-only entries are listed as extras.

## 2026-09-29: mail tools are matched against the harness's own tool list (#53)

- **Status:** accepted
- **Context:** Mail tool names depend on how a connector is attached. A claude.ai connector is `mcp__claude_ai_<Name>__…` in the CLI, and only the running harness knows the names.
- **Options:** A glob like `mcp__*__send_message`: it also catches unrelated servers' tools of the same name.
- **Choice and why:** The table stores the meaning: a server containing `mail`, and tools starting `send`, `reply`, `forward`, `trash` and so on. The tools are found at plan time from the harness's own list. Claude Code's list comes from a `claude -p` session's `init` event, stopped before the model is called.
- **Consequences:** When the list cannot be read, the entries written before stay.

## 2026-09-29: allow-and-report rows get a native allow (#53)

- **Status:** accepted
- **Context:** An allow-and-report row must run without a prompt and still be reported.
- **Options:** None considered.
- **Choice and why:** Write a native `allow` entry. The report half comes from the pre-tool hook, which reads the same table.
- **Consequences:** Reporting depends on the hook being wired.

## 2026-09-29: a stricter entry on the machine is reported, not replaced (#53)

- **Status:** accepted
- **Context:** The machine can deny what the table only asks for, such as today's `git push --force-with-lease` and `gh repo edit`.
- **Options:** Replace the stricter entry: it removes an entry the skill did not write.
- **Choice and why:** List it as `stricter` and keep it.
- **Consequences:** To get the table's level, the user removes that entry by hand.

## 2026-09-29: a broader entry counts as present (#53)

- **Status:** accepted
- **Context:** `Bash(gh repo delete*)` already covers `Bash(gh repo delete:*)`.
- **Options:** Add the table's entry anyway: it duplicates the broader one.
- **Choice and why:** A broader entry counts as present. The adapter adds no duplicate and does not list the broader entry as extra.
- **Consequences:** The adapter must tell when one entry covers another.

## 2026-09-29: the hook imports the setupmachine package (#54)

- **Status:** accepted
- **Context:** The hook and the adapters must read a row the same way.
- **Options:** One self-contained hook file: the hook and the plan could read a row differently.
- **Choice and why:** The hook imports the setupmachine package and reads rows through `rules.py`, the loader the adapters use. It ships in the same skill folder, so the import always resolves. Its core takes a harness-neutral `ToolCall` and returns denials and reports.
- **Consequences:** The hook depends on the package staying beside it.

## 2026-09-29: each harness adds a reader and a writer to hook.HARNESSES (#54)

- **Status:** replaced by [2026-10-11: one harness setup per harness](#2026-10-11-one-harness-setup-per-harness)
- **Context:** Codex, opencode and Cursor need the same hook core with their own payloads and answers.
- **Options:** A copy of the hook per harness.
- **Choice and why:** Each harness has a reader and a writer in `hook.HARNESSES`, so a new harness adds a pair, not a copy.
- **Consequences:** The hook keeps its own list of harnesses.

## 2026-09-29: the hook reads a command the way the shell runs it (#54)

- **Status:** accepted
- **Context:** Matching text misses commands hidden behind wrappers, flags in another order or nested shells.
- **Options:** Match the command as text.
- **Choice and why:** The hook splits the text into simple commands and drops wrappers and assignments. It names programs by basename (`mkfs` covers `mkfs.ext4`). It reads flags anywhere until `--` and matches them per group. It finds subcommands anywhere in the words (`git -C dir push`). Shell strings, `eval`, `sudo`, `xargs`, `find -exec`, command substitutions, heredocs and here-strings fed to a shell, and `echo … | sh` are read as commands of their own.
- **Consequences:** Heredoc bodies fed to anything else, such as a commit message, are skipped, so writing about `rm -rf` is not refused.

## 2026-09-29: allow-and-report prints nothing (#54)

- **Status:** accepted
- **Context:** An `allow` answer from the hook skips Claude Code's native permission check, deny rules included.
- **Options:** Answer `allow`: the native denies stop working.
- **Choice and why:** The hook logs the call and stays silent. The native `allow` entry lets the call run.
- **Consequences:** None beyond the log.

## 2026-09-29: a deny anywhere in the call wins (#54)

- **Status:** accepted
- **Context:** One call can match both deny and report rows.
- **Options:** None considered.
- **Choice and why:** A deny anywhere in the call wins, and nothing is reported, since the call does not run.
- **Consequences:** None.

## 2026-09-29: the hook fails open (#54)

- **Status:** accepted
- **Context:** The hook can meet input or a table it cannot read.
- **Options:** Fail closed: a broken table would stop every tool call.
- **Choice and why:** The hook exits 1, a non-blocking error in Claude Code. The native deny entries underneath still refuse.
- **Consequences:** Protection then rests on the native entries alone. [2026-09-29: every wired hook command fails open](#2026-09-29-every-wired-hook-command-fails-open) extends this to the wiring.

## 2026-09-29: the hook also checks file and MCP-tool rows (#54)

- **Status:** accepted
- **Context:** Native entries can miss file paths and MCP tools connected after the last plan.
- **Options:** None considered.
- **Choice and why:** The hook checks file tools against the path globs. A read rule also covers writes, as Claude Code's `Read` deny does. It checks MCP tools against the row's regexes at call time.
- **Consequences:** A mail tool connected after the last plan is still covered.

## 2026-09-29: the hook's report folder is set in hook.json (#54)

- **Status:** replaced by [2026-09-30: hook.json is optional](#2026-09-30-hookjson-is-optional-81)
- **Context:** Allow-and-report calls need a place to be logged.
- **Options:** None considered.
- **Choice and why:** `~/.config/agents/hook.json` holds `report_dir`, beside the manifest. The plan creates it once with `~/.local/state/agents/reports` and never rewrites it. That is the XDG state folder, since reports are state, not config. Against another `--home`, the wired command names that home's config file.
- **Consequences:** Reports are one JSON line per call, in one file per UTC day.

## 2026-09-29: the hook is wired for every tool (#54)

- **Status:** accepted
- **Context:** The hook checks commands, files and MCP tools.
- **Options:** Wire it per tool: a new tool would need a new plan.
- **Choice and why:** Wire the hook for every tool (`*`), so a new tool is covered without a new plan.
- **Consequences:** Python's start-up costs a few tens of milliseconds per call.

## 2026-09-29: the hook's gaps are listed once (#54)

- **Status:** accepted
- **Context:** Command rows carried the same hook gap again and again.
- **Options:** None considered.
- **Choice and why:** List the hook's gaps once, in its plan section. Deny and allow-and-report command rows no longer carry a gap per row.
- **Consequences:** None.

## 2026-09-29: the hook reads the table the plan used (#54)

- **Status:** accepted
- **Context:** A plan can run with another table, through `--rules <file>`.
- **Options:** None considered.
- **Choice and why:** A plan run with `--rules <file>` wires the hook with `--rules <file>`. With the skill's own table, the command stays short.
- **Consequences:** None.

## 2026-09-29: role names are the placeholders (#59)

- **Status:** accepted
- **Context:** Skills use kebab-case placeholders such as `<session-host>`, but the Defaults rows had other names.
- **Options:** None considered.
- **Choice and why:** Name the rows in kebab-case, the same as the placeholders: `session-host`, `worktree-tool`, `notification-method`, `agent-to-start`, `skills-repo` and `path-to-skills-repo`. The old "Skills repo" row held both the repo and its clone, so it split in two, as `maintain-environment` already used two placeholders. A skill then reads a placeholder's value from the row of the same name.
- **Consequences:** A file written before the rename keeps its old rows. The next apply adds the new ones as `none`, and the user moves the values across. [2026-09-30: the role agent-to-start is now agent](#2026-09-30-the-role-agent-to-start-is-now-agent) renamed one role.

## 2026-09-29: a project's own table overrides the global one (#59)

- **Status:** accepted
- **Context:** A project can name its own tools for some roles.
- **Options:** None considered.
- **Choice and why:** A project's own table overrides the global one for that project. Both are in the agent's context, so the reference and the table's intro say so.
- **Consequences:** A skill's Parameters section repeats it once.

## 2026-09-29: the env-var family is six rows (#64)

- **Status:** accepted
- **Context:** Agents must never read environment variables, and a row has one command shape.
- **Options:** None considered.
- **Choice and why:** Six rows: `.env` reads and writes (file rows); `cat`, `less`, `head`, `tail`, `grep`, `source` and `.` on a `.env` file; `env`, `export` and `set` on their own; `printenv` in any form; and `export -p`, `declare -p` and `typeset -p`. `declare -p` and `typeset -p` list the same variables as `export -p`.
- **Consequences:** `.env` moved out of the `secret-files` rows, which now hold `secrets/` only.

## 2026-09-29: three table fields for the env-var rows (#64)

- **Status:** accepted
- **Context:** The table could not say "the program alone", "an operand matching these files" or "except these files".
- **Options:** None considered.
- **Choice and why:** Add three fields, read the same by every adapter and the hook:
  - `arguments: "none"`: the program alone. The hook reads a wrapper that runs no command as itself, so `env -u X` is `env`, and `env FOO=1 cmd` stays allowed.
  - `files` on a command row: an operand matching the globs.
  - `except` on either kind: the globs left out.
- **Consequences:** A row's `gap` names what no harness catches, and every adapter prints it.

## 2026-09-29: .env.example stays open through positive globs (#64)

- **Status:** accepted
- **Context:** A probe showed Claude Code's path globs read `[!e]` and `[^e]` as plain classes that list `!` or `^` and `e`. They also match classes case-insensitively on macOS, and they have no other negation.
- **Options:** A negated glob: Claude Code has none.
- **Choice and why:** `except` becomes the globs around the exception (`rules.without`): 15 per glob, exact for names built from letters, digits, `_` and `.`. The hook applies the exception exactly.
- **Consequences:** Each exception adds many native entries.

## 2026-09-29: write rows also write Write(**/…) entries (#64)

- **Status:** replaced by [2026-10-12: Claude Code gets no Write(...) entries](#2026-10-12-claude-code-gets-no-write-entries)
- **Context:** The Cursor CLI checks `Write` against absolute paths, so it never matches `./`.
- **Options:** None considered.
- **Choice and why:** Write rows also write `Write(**/…)` entries for the Cursor CLI. They keep the plain globs with no exception, since Cursor's globs have only `*` (#57 confirmed it).
- **Consequences:** A Cursor write to `.env.example` is refused.

## 2026-09-29: an existing ./.env.* entry is named as extra (#64)

- **Status:** accepted
- **Context:** A probe showed `Read(./.env.*)` refuses `sub/.env.local` and `sub/.env.example`. A path with no `/` after `./` matches at any depth, as in `.gitignore`. So such an entry also refuses `.env.example`.
- **Options:** None considered.
- **Choice and why:** The plan names this on the entry's `extra` line.
- **Consequences:** To open `.env.example`, the user removes the entry by hand.

## 2026-09-29: the $VAR expansion gap is named on the printenv row (#64)

- **Status:** accepted
- **Context:** No row catches a variable expanded by the shell.
- **Options:** None considered.
- **Choice and why:** Name the gap on the `printenv` row and explain it in its rule line. On Claude Code, the gap line adds what the auto-mode guard covers.
- **Consequences:** [2026-09-30: a command row can match the variables it expands](#2026-09-30-a-command-row-can-match-the-variables-it-expands-97) later closed part of this gap.

## 2026-09-29: command rows with files get no Claude Code Bash entries (#64)

- **Status:** accepted
- **Context:** Bash rules match text, not paths.
- **Options:** None considered.
- **Choice and why:** Write no `Bash` entries for these rows. Claude Code's Read rules already refuse `cat`, `head`, `tail` and `grep` on a denied file (probed).
- **Consequences:** `less`, `source` and `.` are left to the hook and named as a gap.

## 2026-09-29: a row's guard goes into autoMode.hard_deny (#64)

- **Status:** replaced by [2026-09-30: the auto-mode guard is optional and stays off](#2026-09-30-the-auto-mode-guard-is-optional-and-stays-off-81)
- **Context:** Research (auto-mode-semantic-guard, 6.1) suggested a semantic guard for the env-var rows.
- **Options:** None considered.
- **Choice and why:** A row's `guard` goes into Claude Code's `autoMode.hard_deny`, with `classifyAllShell: true`, in the same settings write. `$defaults` is added only when the skill creates the array. The user's other `autoMode` entries are never touched, and the manifest's `auto_mode` list names what the skill may remove. The guard's text says `.env.example` is not an env file, since a hard deny cannot be cleared. The guard sits on the `printenv` row, the one row of the family with a gap.
- **Consequences:** The other harnesses read `rule.guard` if they gain a semantic guard.

## 2026-09-29: Codex's rules live in their own file (#55)

- **Status:** accepted
- **Context:** Codex loads every `*.rules` file, and the strictest decision wins. Codex saves "always allow" choices in `default.rules`.
- **Options:** Edit `default.rules`: Codex writes to it too.
- **Choice and why:** Regenerate `~/.codex/rules/set-up-machine.rules` whole. It holds every row, even where another file already covers it, so the table's rules do not depend on anyone else's file. On a tie in prefix length, Codex shows the justification of the file that sorts last, which is this one.
- **Consequences:** The skill never edits `default.rules`.

## 2026-09-29: Codex gets one rule per flag order (#55)

- **Status:** accepted
- **Context:** Codex prefix rules are token-exact and in order, so `rm -f -r` needs its own pattern.
- **Options:** None considered.
- **Choice and why:** Separate flags get one rule per order. Clustered short flags share one rule of alternatives. There are no `/bin/` spellings, since Codex resolves an absolute program path to its basename.
- **Consequences:** None.

## 2026-09-29: no Codex rule for bash -c, sh -c or zsh -c (#55)

- **Status:** accepted
- **Context:** Codex wraps every command in `<shell> -lc`, or `-c` with login off, and checks non-plain commands against that wrapper.
- **Options:** A Codex rule: it would refuse ordinary commands with a redirect or `$(…)`.
- **Choice and why:** Write no Codex rule. The hook sees the command before the wrapper and enforces the row.
- **Consequences:** Codex relies on the hook for these rows.

## 2026-09-29: allow-and-report is allow in Codex (#55)

- **Status:** accepted
- **Context:** Codex needs a level for allow-and-report rows.
- **Options:** None considered.
- **Choice and why:** Use `allow`, Codex's no-prompt level.
- **Consequences:** It also runs the command outside the sandbox, which `gh api` needs for the network anyway.

## 2026-09-29: the plan writes Codex's hook trust entry (#55)

- **Status:** replaced by [2026-09-30: the agent writes Codex's trusted_hash](#2026-09-30-the-agent-writes-codexs-trusted_hash-81)
- **Context:** Codex skips an untrusted user hook. Trusting it in `/hooks` would be a second approval outside the plan.
- **Options:** Trust in `/hooks`: a second approval.
- **Choice and why:** The plan writes the trust entry. The hash is reproduced from Codex's source and checked against Codex's own `hooks/list`. The plan line says that approving it is the review.
- **Consequences:** The skill must keep Codex's hashing in step.

## 2026-09-29: the hook wires into Codex's hooks.json (#55)

- **Status:** accepted
- **Context:** Codex takes hooks in `hooks.json` or inline in `config.toml`.
- **Options:** Inline `[hooks]` in `config.toml`: TOML is harder to edit safely, and Codex warns when both hold hooks.
- **Choice and why:** `hooks.json`. The standard library edits JSON safely, and Codex users already keep hooks there.
- **Consequences:** None.

## 2026-09-29: ~/.codex/AGENTS.md becomes a link only when no line is lost (#55)

- **Status:** accepted
- **Context:** Codex's own `AGENTS.md` may hold lines the shared file lacks.
- **Options:** Replace it and keep a backup: the deletion hides in the backup.
- **Choice and why:** Link it only when no line would be lost. A line counts as kept when it is already in the shared file, or inside a known block that an external skill replaces. Otherwise the plan lists the file as `extra` and leaves it.
- **Consequences:** Moving lines stays a reviewed step.

## 2026-09-29: Context7 is the upstream find-docs skill (#55)

- **Status:** accepted
- **Context:** A block in Codex's file copied Context7's text, and the skill needs to install the real thing.
- **Options:** None considered.
- **Choice and why:** Install the upstream `find-docs` skill from `upstash/context7`, the one the block copied. The plan shows the install as an `added` line with its `npx skills add` command. Apply runs it before writing files, with `HOME` set to the planned home. It follows maintain-environment's scope rule.
- **Consequences:** A trial installs into the trial home.

## 2026-09-29: a real Codex session is checked without a login (#55)

- **Status:** accepted
- **Context:** Copying the real `auth.json` into a trial home could refresh and rotate its token, which logs the real Codex out.
- **Options:** Copy `auth.json`: it can log the real Codex out.
- **Choice and why:** Point `codex exec` at a local stand-in model that asks for one command.
- **Consequences:** The check never touches the real login.

## 2026-09-29: bare rows and file rows get no Codex rule (#55)

- **Status:** accepted
- **Context:** #64 added rows for a bare program (`env` alone) and rows on files (`cat .env`). Codex prefix rules can say neither "nothing after it" nor "a path anywhere in the operands".
- **Options:** None considered.
- **Choice and why:** Write no Codex rule for them. The hook enforces both, with the `.env.example` exception. Each row's `gap` is printed, and a `guard` gets a `none` line, since Codex has no semantic guard.
- **Consequences:** Codex relies on the hook for these rows.

## 2026-09-29: opencode's AGENTS.md is a symlink to the shared file (#56)

- **Status:** accepted
- **Context:** opencode does not follow `@` imports and reads files with a plain read, which follows links.
- **Options:** A copy: it can drift.
- **Choice and why:** A relative symlink (`../agents/AGENTS.md`), with the same symlink write as Codex's link (`FileWrite.link_to`).
- **Consequences:** An existing `AGENTS.md` there is the user's. It is listed as `extra`, with the gap that opencode reads it instead, until its lines move into the shared file.

## 2026-09-29: the adapter writes opencode's last global config file (#56)

- **Status:** accepted
- **Context:** opencode loads `config.json`, `opencode.json` and `opencode.jsonc`, in that order.
- **Options:** Rewrite a file with comments: the standard library cannot keep them.
- **Choice and why:** Write the last of those files that exists, else a new `opencode.json`. A file that holds comments is not rewritten. The plan lists its rules as a gap instead.
- **Consequences:** Nothing is lost without the user seeing it.

## 2026-09-29: opencode entries are appended loosest first (#56)

- **Status:** accepted
- **Context:** In opencode the last match wins, so a stricter entry must come after anything it overrides.
- **Options:** Compare keys: that misses wildcards and order.
- **Choice and why:** Append loosest first. The plan evaluates a sample of each pattern against the file's rules the way opencode does (wildcards over tool names and patterns, `findLast`). That decides present, covered, stricter or tightened. The same pattern at a looser level moves to the end at the table's level, since a key cannot appear twice. A tool whose rules a later tool-wide entry overrides moves after it.
- **Consequences:** The adapter models opencode's matching.

## 2026-09-29: an except becomes an opencode allow (#56)

- **Status:** accepted
- **Context:** opencode's patterns have no character classes, so `rules.without`'s globs do not apply.
- **Options:** None considered.
- **Choice and why:** Write an `allow` after the row's deny entries, the way opencode's own defaults open `.env.example`.
- **Consequences:** Where the user's own entry refuses the exception, the allow is not added, since it would loosen that entry. The plan lists it as `stricter`.

## 2026-09-29: opencode leaves file-operand rows and declarations to the hook (#56)

- **Status:** accepted
- **Context:** opencode patterns match text, not paths. A probe showed `export -p` ran under a matching deny, since opencode checks only plain command nodes.
- **Options:** None considered.
- **Choice and why:** Command rows with `files` get no bash pattern, and declaration rows only name a gap. The hook covers both.
- **Consequences:** The plan says so per row.

## 2026-09-29: opencode mail rows match configured MCP servers (#56)

- **Status:** accepted
- **Context:** opencode lists MCP tools only inside a session, not in `opencode debug agent` or the server's tool list.
- **Options:** Exact tool denies: there is no list to write them from.
- **Choice and why:** A configured server that matches is a gap left to the hook. The hook reads a non-built-in tool name as `<server>_<tool>`, trying each `_` as the split.
- **Consequences:** [2026-10-01: opencode takes MCP tool names as permission keys](#2026-10-01-opencode-takes-mcp-tool-names-as-permission-keys-67) later found native keys.

## 2026-09-29: the opencode hook is a generated plugin (#56)

- **Status:** replaced by [2026-09-30: the opencode plugin is a template](#2026-09-30-the-opencode-plugin-is-a-template-81)
- **Context:** opencode runs hooks as JavaScript plugins.
- **Options:** None considered.
- **Choice and why:** Generate `~/.config/opencode/plugins/set-up-machine.js`. It runs the same Python script with `--harness opencode` and throws its output. A probe showed the thrown message reaches the model unwrapped, as the tool result. It spawns the script asynchronously with a 10-second limit and fails open, as the Claude Code wiring does.
- **Consequences:** A marker on the first line says the file is the skill's. A file of that name without it is kept, and the hook is reported not wired.

## 2026-09-29: opencode has no semantic guard (#56)

- **Status:** replaced by [2026-09-30: no auto-mode guard](#2026-09-30-no-auto-mode-guard)
- **Context:** Rows carried a `guard` for Claude Code's auto mode.
- **Options:** None considered.
- **Choice and why:** Name each row's `guard` as `none` for opencode.
- **Consequences:** None.

## 2026-09-29: one Cursor adapter covers the IDE and the CLI (#57)

- **Status:** accepted
- **Context:** The IDE and the CLI share the user rule folder and `~/.cursor/hooks.json`. Only the CLI has a permission file.
- **Options:** None considered.
- **Choice and why:** One adapter for both.
- **Consequences:** The plan names which half each gap belongs to.

## 2026-09-29: the shared file reaches Cursor as a generated copy (#57)

- **Status:** accepted
- **Context:** The IDE and the CLI read user rule files in `~/.cursor/rules/`. The CLI reads them only for a working folder inside the home folder, by walking up. An `.mdc` file applies to every chat only with `alwaysApply: true` frontmatter. `@file` is a context reference, not an include.
- **Options:**
  - A link or an import: neither works.
  - Account User Rules: they live on the account, out of reach.
- **Choice and why:** A generated copy in `~/.cursor/rules/global-instructions.mdc`, refreshed on every apply.
- **Consequences:** An edit to the shared file shows in the plan until the next apply. Whether CLI sessions get Account User Rules stays unconfirmed and no longer matters.

## 2026-09-29: the Cursor CLI's native entries are literal Shell(prefix) (#57)

- **Status:** accepted
- **Context:** The CLI's glob escapes everything but `*`, which matches anything, `/` included. A literal prefix matches the prefix and anything after a space, the meaning of Claude Code's ` *` rule.
- **Options:** None considered.
- **Choice and why:** Write literal `Shell(<prefix>)` entries in `~/.cursor/cli-config.json`. Rows with `arguments: "none"` become `Shell(x:)`, which matches only the bare command (probed).
- **Consequences:** Rows with `files` get no entry, since the CLI's Read rules do not bind shell commands.

## 2026-09-29: Claude Code's entries use Bash(prefix *) (#57)

- **Status:** accepted
- **Context:** The Cursor CLI unions `~/.claude/settings.json` into its lists, where a project cannot remove them. It matches the `:*` form only against the bare command, and the ` *` form against every use with something after it. Claude Code reads the two the same. This replaces the `Bash(<prefix>:*)` form from [2026-09-29: a row describes a command by its meaning](#2026-09-29-a-row-describes-a-command-by-its-meaning).
- **Options:** Keep `Bash(<prefix>:*)`: Cursor would miss every use with arguments.
- **Choice and why:** Switch to `Bash(<prefix> *)`. A probe with the CLI's own deny list empty showed the ` *` entries refusing `rm -rf x`, a force push and `gh repo delete owner/x`.
- **Consequences:** An old `:*` entry with a space no longer counts as covering. The ` *` entry is added beside it, and the old one is an extra.

## 2026-09-29: the Claude Code adapter adds an empty allow beside a deny (#57)

- **Status:** accepted
- **Context:** The Cursor CLI's schema needs both lists. Without one, it skips the whole file, silently.
- **Options:** None considered.
- **Choice and why:** Add an empty `allow` list beside `deny`.
- **Consequences:** None.

## 2026-09-29: the Cursor hook is wired on four events (#57)

- **Status:** accepted
- **Context:** Cursor's hard blocks are `beforeShellExecution`, `beforeMCPExecution`, `beforeReadFile` and `preToolUse`. Only `beforeMCPExecution` carries the server name. `preToolUse` calls a tool `MCP:<tool>`.
- **Options:** None considered.
- **Choice and why:** Wire `beforeShellExecution`, `beforeMCPExecution`, `beforeReadFile`, and `preToolUse` for `Write|Delete|Grep`. Each call reaches one of them, so no call is reported twice. MCP goes through `beforeMCPExecution`.
- **Consequences:** None.

## 2026-09-29: the Cursor hook always answers JSON (#57)

- **Status:** accepted
- **Context:** A probe showed the CLI gives the agent `user_message`. A hook `allow` overrides neither a native deny nor the allowlist prompt.
- **Options:** `failClosed`: it does not match the Claude Code hook's fail-open choice.
- **Choice and why:** Answer `{}` to let a call through, and put a refusal in both `user_message` and `agent_message`. The hook is not `failClosed`.
- **Consequences:** The gap says the IDE then has nothing underneath.

## 2026-09-29: Claude Code's hook run by Cursor refuses but does not report (#57)

- **Status:** accepted
- **Context:** Cursor runs the hooks in `~/.claude/settings.json` too, so one call could be reported twice.
- **Options:** None considered.
- **Choice and why:** The payload's `cursor_version` tells the Claude Code hook to leave the report to the hook wired for Cursor.
- **Consequences:** None.

## 2026-09-29: the Cursor CLI refuses .env.example natively (#57)

- **Status:** accepted
- **Context:** Cursor's globs have no classes, so an exception cannot be written.
- **Options:** Leave `.env.*` to the hook: `.env.local` would have only the hook.
- **Choice and why:** A plain `**/.env.*` that refuses too much is safer.
- **Consequences:** The hook and the IDE leave `.env.example` open. The plan names the gap.

## 2026-09-29: bare rows get no Claude Code entry (#57)

- **Status:** accepted
- **Context:** An exact `Bash(env)` refuses only `env` in Claude Code. The Cursor CLI reads `~/.claude/settings.json` and matches it as a prefix. It would refuse `env FOO=1 cmd`, `export FOO=1` and `set -e`, which the table allows. This replaces the #64 choice to write exact entries for bare rows.
- **Options:** Exact entries: Cursor reads them too broadly.
- **Choice and why:** Write no Claude Code entry for bare rows. `env`, `export` and `set` alone are left to the hook, and in part to the auto-mode guard, on Claude Code. They are named as a gap there.
- **Consequences:** `cli-config.json` keeps `Shell(x:)`, which matches only the bare command.

## 2026-09-29: Cursor has no memory (#57)

- **Status:** accepted
- **Context:** The skill turns memory off in each harness.
- **Options:** None considered.
- **Choice and why:** Cursor's plan shows `none`, from `memory.WITHOUT_MEMORY`.
- **Consequences:** None.

## 2026-09-29: every wired hook command fails open

- **Status:** accepted
- **Context:** The final branch review found that Claude Code, Codex and Cursor block a call on exit 2. `python3 <script>` returns 2 when the script is gone, so a moved or removed skill would block every tool call.
- **Options:** None considered.
- **Choice and why:** The command is `[ -f <script> ] && python3 <script> … || true`. Cursor's ends `|| echo '{}'`, since Cursor reads an empty answer as invalid JSON, which blocks. A deny is JSON on stdout with exit 0, so it passes through. The hook's own exit 1 on an unreadable table is now silent. opencode's plugin checks that the script exists before it starts it.
- **Consequences:** The native entries still hold when the hook is gone. The plan names a hook script outside `~/.agents/skills` or `~/.claude/skills`, such as a repo checkout, as a gap, once.

## 2026-09-29: arguments flags matches a program with only flags

- **Status:** accepted
- **Context:** `declare -x`, `typeset +x` and `export` with only flags list the variables that carry those flags.
- **Options:** None considered.
- **Choice and why:** Add `arguments: "flags"`. Bare `declare` and `typeset` join `env-dump`. A new row, `env-dump-listed`, refuses `declare`, `typeset` and `export` with only flags.
- **Consequences:** No harness's patterns can say "only flags" without refusing `declare -x NAME=value`. So the row has no native entries, and every adapter names the gap. `export -p` alone matches both this row and `env-dump-declared`. The overlap stays, since `-p` with a name (`declare -p TOKEN`) still needs the older row.

## 2026-09-29: the user's own skills repo is installed as a plan item

- **Status:** replaced by [2026-10-03: the workstation repo lists what every machine installs](#2026-10-03-the-workstation-repo-lists-what-every-machine-installs)
- **Context:** The spec asks for shared skills to be installed.
- **Options:** None considered.
- **Choice and why:** The plan reads the `skills-repo` row from the shared file. When the skills CLI's lock file (`~/.agents/.skill-lock.json`) records no skill from that source, the plan shows the `npx skills add` command as an `added` line, which apply runs.
- **Consequences:** No value, or `none`, gives a `none` line. A value that is not `<owner>/<repo>` is a gap. Nothing is guessed.

## 2026-09-29: the hook checks redirects and tee against the file rows

- **Status:** accepted
- **Context:** A redirect or `tee` reads or writes a file without a file tool.
- **Options:** None considered.
- **Choice and why:** A redirect's target is a read (`<`) or a write (`>`, `>>`, `&>`). `tee`'s operands are writes. Heredocs, here-strings and descriptor duplications (`>&2`) are not files. A write is checked against the read rows too, as for file tools.
- **Consequences:** None.

## 2026-09-29: operands takes alternative sequences

- **Status:** accepted
- **Context:** `chmod-recursive-777` has several spellings of one mode.
- **Options:** None considered.
- **Choice and why:** `operands` takes alternatives: `777`, `0777`, `a+rwx`, `a=rwx`, `ugo+rwx` and `ugo=rwx`. Codex gets one pattern with the alternatives. The other harnesses get one entry per spelling.
- **Consequences:** Other spellings of the same mode are the row's gap.

## 2026-09-29: a trial --home never starts a real harness

- **Status:** accepted
- **Context:** Claude Code's and Cursor's tool discovery read the real machine's config and login.
- **Options:** None considered.
- **Choice and why:** Under a `--home` other than the user's own, the plan skips discovery, names the gap and keeps the mail entries written before. `--tool-names` can supply the list.
- **Consequences:** A trial does not find new mail tools.

## 2026-09-29: searches are checked by path and glob

- **Status:** accepted
- **Context:** A search can read a protected file without naming its path.
- **Options:** Expand every glob: the hook does not expand a search over a folder.
- **Choice and why:** A `Grep` (Claude Code, Cursor) or `grep` (opencode's `include`) whose glob names a file row's files by name (`*.env`, `.env*`) is refused.
- **Consequences:** A glob that matches ordinary names too (`*`, `*.*`) is a search over the folder. Each adapter names it in its file-row gap.

## 2026-09-29: file paths fold case where program names do

- **Status:** accepted
- **Context:** macOS and Windows treat file names case-insensitively.
- **Options:** None considered.
- **Choice and why:** File paths fold case on those systems, as program names do.
- **Consequences:** `.ENV` meets `**/.env` there.

## 2026-09-30: the agent sets each harness up from its reference (#81)

- **Status:** accepted
- **Context:** The spec asked for one adapter per harness as a reference file. Harness formats change faster than a script frozen at one version can follow. This replaces the adapter modules, the reconcile script, the plan id and the manifest from the 2026-09-29 entries.
- **Options:** Keep the adapters and the plan/apply engine: they fall behind the harnesses.
- **Choice and why:** The agent sets up each harness from its reference. Each reference carries what only the code knew: native forms with worked examples, listing commands, hook payloads and answers, and Codex's trust hash. It tells the agent to check the harness's current docs first.
- **Consequences:** The 2026-09-29 entries stay as the record.

## 2026-09-30: three things stay code (#81)

- **Status:** accepted
- **Context:** Some parts cannot be left to an agent's reading of a reference.
- **Options:** None considered.
- **Choice and why:** The pre-tool hook, `rules.json` and `verify.py` stay code. Verify is a test, not a setup step. It feeds each row's samples to the hook, runs the plain commands through `codex execpolicy check`, and checks that every harness's hook is wired to a script that exists.
- **Consequences:** None.

## 2026-09-30: every row carries samples (#81)

- **Status:** accepted
- **Context:** Agents need worked examples, and verify needs data.
- **Options:** None considered.
- **Choice and why:** Each row carries `samples`, as `covers` and `leaves`. They are the rows' examples for agents, the data verify checks, and what set-up-project's audit matches a project entry against.
- **Consequences:** None.

## 2026-09-30: Codex's check reports and never fails (#81)

- **Status:** accepted
- **Context:** Some rows get no Codex rule by design: shell rows, bare rows and rows on files.
- **Options:** Fail on a difference: by-design rows would always fail.
- **Choice and why:** Codex's check only reports. A `differs` line is read against `references/codex.md`. A `stricter` line is a user rule the diff keeps.
- **Consequences:** None.

## 2026-09-30: no manifest

- **Status:** accepted
- **Context:** Without code to keep it, the manifest from [2026-09-29: a manifest records what the skill wrote](#2026-09-29-a-manifest-records-what-the-skill-wrote) cannot stay accurate. This replaces it.
- **Options:** None considered.
- **Choice and why:** "Never remove what it did not write" becomes a narrow list. The diff removes only memory files, a harness's own global file that becomes a link, and this skill's own wiring that points at an old script.
- **Consequences:** An entry that a dropped row left behind is `extra`, for the user to remove.

## 2026-09-30: backups stay where they were (#81)

- **Status:** accepted
- **Context:** The agent now writes the files.
- **Options:** None considered.
- **Choice and why:** The agent takes a backup in `~/.config/agents/backups/<time>/` before any write.
- **Consequences:** None.

## 2026-09-30: the agent writes Codex's trusted_hash (#81)

- **Status:** accepted
- **Context:** The plan no longer exists to write the trust entry. This replaces [2026-09-29: the plan writes Codex's hook trust entry](#2026-09-29-the-plan-writes-codexs-hook-trust-entry-55).
- **Options:** None considered.
- **Choice and why:** The agent writes `trusted_hash` as part of the approved diff. Approving the whole diff stands in for Codex's `/hooks` review, as the maintainer confirmed. `verify.py --codex-trust-hash` computes the hash, so the hashing lives in one place.
- **Consequences:** Verify checks the entry.

## 2026-09-30: the auto-mode guard is optional and stays off (#81)

- **Status:** replaced by [2026-09-30: no auto-mode guard](#2026-09-30-no-auto-mode-guard)
- **Context:** The guard's value was unproven. This replaces [2026-09-29: a row's guard goes into autoMode.hard_deny](#2026-09-29-a-rows-guard-goes-into-automodehard_deny-64).
- **Options:** None considered.
- **Choice and why:** Keep the guard off until the probes in #65 run. The references describe it, and the diff lists each guard as `none`.
- **Consequences:** The probes decide its future.

## 2026-09-30: the opencode plugin is a template (#81)

- **Status:** accepted
- **Context:** No script generates the plugin any more. This replaces [2026-09-29: the opencode hook is a generated plugin](#2026-09-29-the-opencode-hook-is-a-generated-plugin-56).
- **Options:** The agent writes JavaScript itself: less reliable.
- **Choice and why:** `references/opencode-plugin.js` is a template. The agent fills in the hook command and copies it.
- **Consequences:** None.

## 2026-09-30: hook.json is optional (#81)

- **Status:** accepted
- **Context:** The hook already defaults to `~/.local/state/agents/reports`. This replaces [2026-09-29: the hook's report folder is set in hook.json](#2026-09-29-the-hooks-report-folder-is-set-in-hookjson-54).
- **Options:** None considered.
- **Choice and why:** `~/.config/agents/hook.json` is needed only for another folder.
- **Consequences:** None.

## 2026-09-30: the Linux container runs verify and the unit tests (#81)

- **Status:** accepted
- **Context:** Without a plan/apply script, there is no setup to run in the container.
- **Options:** None considered.
- **Choice and why:** The container runs verify and the unit tests only.
- **Consequences:** The Codex session probes needed the script. They stay described in `references/codex.md`.

## 2026-09-30: the hook reads quoting in one pass (#82)

- **Status:** accepted
- **Context:** The review listed known bypasses. The hook's regexes could not tell quoted from unquoted text.
- **Options:** Keep the regexes.
- **Choice and why:** A scanner reads the quoting in one pass before tokenizing. It tracks single and double quotes, `$'…'`, escapes, comments, `$(…)`, backticks and `$(( ))`. So a `<<` counts as a heredoc only where the shell reads code. A substitution inside single quotes, or escaped, stays text.
- **Consequences:** It also reads the substitutions in an unquoted heredoc's body, a bypass the review did not list.

## 2026-09-30: more wrappers and shells (#82)

- **Status:** accepted
- **Context:** Several wrappers and shells could run a refused command past the hook.
- **Options:** None considered.
- **Choice and why:** Add the wrappers `busybox`, `watch`, `setsid`, `flock`, `parallel`, `script`, `chronic`, `unbuffer` and `arch`. Add the shells `fish`, `ash`, `mksh`, `csh` and `tcsh`. `watch` and `parallel` also have their words read as one shell string. `flock -c` and `script -c` have their option's string read. A pipe into a shell reads the words before it, joined and one by one.
- **Consequences:** None.

## 2026-09-30: the verdict names ask rows (#82)

- **Status:** accepted
- **Context:** Tests and verify could not check ask rows.
- **Options:** None considered.
- **Choice and why:** The verdict names ask rows too. The hook still says nothing for them, since the native ask entries do the asking.
- **Consequences:** None.

## 2026-09-30: deleting main covers master too (#82)

- **Status:** accepted
- **Context:** The branch name can sit anywhere after `push`.
- **Options:** None considered.
- **Choice and why:** Two rows cover the `--delete` form and the empty refspec form, through a new `any_operand` match key.
- **Consequences:** None.

## 2026-09-30: /proc/*/environ is a file row and a command row (#82)

- **Status:** accepted
- **Context:** `/proc/*/environ` holds a process's environment.
- **Options:** None considered.
- **Choice and why:** Cover it as a file row and as a command row.
- **Consequences:** File rows may now start with `/`.

## 2026-09-30: env templates and docs are readable (#82)

- **Status:** accepted
- **Context:** Some files with `.env` in the name are not env files.
- **Options:** None considered.
- **Choice and why:** `.env.sample`, `.env.template` and `.env*.md` are readable, beside `.env.example`. They are templates and docs about env files.
- **Consequences:** None.

## 2026-09-30: two hook gaps are named, not closed (#82)

- **Status:** accepted
- **Context:** Two bypasses have no reliable fix.
- **Options:** None considered.
- **Choice and why:** Name them as gaps. A glob the shell expands (`cat .env*`) reaches a `.env` file under a name the hook never sees. `ps e` and `ps eww` print environments through letters no rule can tell from ordinary `ps` options.
- **Consequences:** None.

## 2026-09-30: the global section is Environment defaults

- **Status:** accepted
- **Context:** The section was `## Defaults`. The skills called it "the Defaults table", "the global Defaults" and "a Defaults row", as if it were a named source of truth. The maintainer never meant a special term.
- **Options:** "Tools": it reads as an agent's tools.
- **Choice and why:** `## Environment defaults`, written in plain lowercase words.
- **Consequences:** A project's `AGENTS.md` uses the same heading for its own rows, and `/set-up-project` writes it.

## 2026-09-30: the role agent-to-start is now agent

- **Status:** accepted
- **Context:** The maintainer chose the `<agent>` placeholder in the effort skills.
- **Options:** None considered.
- **Choice and why:** Rename the role `agent-to-start` to `agent`, to match.
- **Consequences:** None.

## 2026-09-30: ~/.claude/CLAUDE.md is a symlink to the shared file (#89)

- **Status:** accepted
- **Context:** The maintainer chose this on the first live run. It replaces [2026-09-29: Claude Code reaches the shared file by an @ import](#2026-09-29-claude-code-reaches-the-shared-file-by-an--import).
- **Options:** The `@` import.
- **Choice and why:** A symlink. The shared `AGENTS.md` is the one source, and every harness that can reads it through a link. Claude Code follows the link, as Codex and opencode do.
- **Consequences:** An import-only file from the earlier form becomes the link.

## 2026-09-30: Claude Code's absolute file paths take // (#89)

- **Status:** accepted
- **Context:** Claude Code's permission rules read `/path` as relative to the settings file and `//path` as absolute. The reference had said `/` paths stay as they are.
- **Options:** None considered.
- **Choice and why:** Write absolute paths with `//`. The `proc-environ-read` row is `Read(//proc/**/environ)`.
- **Consequences:** None.

## 2026-09-30: no auto-mode guard

- **Status:** accepted
- **Context:** The probes on #65 ran seven environment and `.env` reads, with and without section 6.1's `hard_deny` rule. This replaces [2026-09-30: the auto-mode guard is optional and stays off](#2026-09-30-the-auto-mode-guard-is-optional-and-stays-off-81).
- **Options:** Keep the guard: its only extra catch was `env | grep`, which the hook already refuses as `env-dump`. A script that prints `.env` got through every time, and `cat .env` did too under the client-side classifier.
- **Choice and why:** Remove the `guard` field and Claude Code's auto-mode section. The guard would add a classifier call to every shell command and close no gap.
- **Consequences:** The skill writes no `autoMode` rules. Auto mode's built-in rules stay as Claude Code ships them.

## 2026-09-30: the generated block ends with an environment-variables paragraph

- **Status:** replaced by [2026-10-01: keep enforcement and remove its inventory from every session](#2026-10-01-keep-enforcement-and-remove-its-inventory-from-every-session)
- **Context:** The rows catch the common commands: `env`, `printenv`, `export -p`, reading or sourcing `.env`, and the file tools. Nothing pattern-based catches `echo $TOKEN`, an interpreter or a script.
- **Options:** None considered.
- **Choice and why:** The maintainer asked for one plain instruction that covers every route, so the block closes with it.
- **Consequences:** The only real prevention is keeping secrets out of reach: out of the shell environment, or refused by an OS-level sandbox. The maintainer's projects hold no secrets in the environment today.

## 2026-09-30: a command row can match the variables it expands (#97)

- **Status:** accepted
- **Context:** `env-print` had a gap: `echo $TOKEN` cannot be told from `echo $HOME` by text. A secret's name usually says what it is.
- **Options:** None considered.
- **Choice and why:** A new `variables` key holds case-insensitive globs over variable names. `env-print-secret` refuses `echo`, `printf` and `print` when an argument expands a name matching `*TOKEN*`, `*KEY*`, `*SECRET*`, `*PASSWORD*`, `*PASSWD*` or `*CREDENTIAL*`.
- **Consequences:** No harness's patterns can match a variable's name inside an argument. So there is no native entry anywhere, and each reference lists a gap the hook covers.

## 2026-09-30: the hook marks expansions before tokenising (#97)

- **Status:** accepted
- **Context:** Tokenising drops quotes, so `echo '$API_TOKEN'` and `echo $API_TOKEN` became the same word.
- **Options:** None considered.
- **Choice and why:** `mark_expansions` marks each `$` the shell would expand, before tokenising. Only rows with `variables` read the marked words, so every other row sees commands as before.
- **Consequences:** `${#NAME}` (a length) and passing a variable to another command (`curl -H "Bearer $TOKEN"`) stay allowed.

## 2026-09-30: find -delete is denied (#92)

- **Status:** accepted
- **Context:** `find-delete`'s rule line said "asks first", but nothing asked. `find` takes `-delete` after the path, so no harness's prefix entry catches it, and the hook leaves ask rows to the harness.
- **Options:** Keep it an ask row: nothing asks.
- **Choice and why:** Move `find-delete` from ask to deny. The maintainer asked for it to be blocked as far as possible. The hook now refuses it on every harness, behind wrappers, `bash -c` and `$(…)` too.
- **Consequences:** The instruction says to list with `find`, then move the files into `.scratch/`. No harness has a native entry for `find`'s options, and *Spellings* says so for every harness.

## 2026-10-01: a person's own parts come from their own repository (#113)

- **Status:** accepted
- **Context:** A new machine needed the person's Tool values and workflow typed again. The spec is #111.
- **Options:** None considered.
- **Choice and why:** The Environment defaults table's Tool column and the Personal workflow section are generated from the person's repository, the way the rules block is generated from the rule table. The roles' What it is and When none columns still come from the skill.
- **Consequences:** A new machine gets them by running the skill, and the repository can be private.

## 2026-10-01: the pointer is ~/.config/agents/source.md (#113)

- **Status:** replaced by [2026-10-09: the workstation repo is a parameter and a role](#2026-10-09-the-workstation-repo-is-a-parameter-and-a-role)
- **Context:** The skill must find the person's repository without naming it in public files.
- **Options:** None considered.
- **Choice and why:** `~/.config/agents/source.md` names the repository as `<owner>/<repo>` and its clone path, or `none`. It sits outside every repository, so it is private by being local. It works like `docs/agents/issue-tracker.md` does for a project. When it is missing, Inspect asks the user once and the diff writes it.
- **Consequences:** `none` is recorded so the next run does not ask. A machine with no repository keeps its hand-written Tool values and workflow lines. The skill finds the repository only through the pointer and names no parameter for it.

## 2026-10-01: the repository's files sit in an agents/ folder (#113)

- **Status:** replaced by [2026-10-11: setup/ replaces agents/](#2026-10-11-setup-replaces-agents-195)
- **Context:** The skill needs a known place in the person's repository.
- **Options:** None considered.
- **Choice and why:** Use an `agents/` folder, so the rest of the repository stays free. In `instructions.md`, only the Role and Tool columns are read.
- **Consequences:** Any other column, such as Why, and any text outside the two sections are notes that stay there. A role left out is `none`.

## 2026-10-01: agents/permissions.json has a place and no format yet (#113)

- **Status:** replaced by [2026-10-01: personal permissions use the rule table's format](#2026-10-01-personal-permissions-use-the-rule-tables-format-114)
- **Context:** Personal rows were planned but not designed.
- **Options:** None considered.
- **Choice and why:** Reserve `agents/permissions.json`. The next ticket, #114, fills it.
- **Consequences:** None.

## 2026-10-01: personal permissions use the rule table's format (#114)

- **Status:** accepted
- **Context:** #113 reserved `agents/permissions.json` with no format. The spec is #111.
- **Options:** None considered.
- **Choice and why:** The file keeps its name and takes the rule table's format, `{"version": 1, "rules": [...]}`. One loader, `rules.load(path, personal=True)`, checks both files, and a malformed personal row is refused the same way.
- **Consequences:** A personal row cannot reuse a table id, so a rule's id still names one row.

## 2026-10-01: a plain allow level for personal rows (#114)

- **Status:** accepted
- **Context:** A person who adds a tool needs it to run with no prompt and nothing to report.
- **Options:** Allow it in the table too: a generic rule should never loosen a harness.
- **Choice and why:** Add a plain `allow` level, for personal rows only. Every harness evaluates deny and ask over allow: Codex by the strictest decision, and opencode because allow entries are written first. `verify.py` fails an allow sample that a table row denies or asks for.
- **Consequences:** A personal allow cannot loosen a table row.

## 2026-10-01: the hook and verify load personal rows through the pointer (#114)

- **Status:** accepted
- **Context:** Personal rows must be enforced beside the table.
- **Options:** Fail open on the whole table when the personal file is malformed: the generic rules would drop.
- **Choice and why:** The hook and `verify.py` load personal rows through the pointer. A missing pointer or file means no personal rows. A malformed personal file makes the hook skip the personal rows and keep the table's.
- **Consequences:** `verify.py` reports a malformed file as `personal FAIL`.

## 2026-10-01: a personal row is written only where its tool exists (#114)

- **Status:** accepted
- **Context:** A personal row can name a tool that a machine or harness lacks.
- **Options:** None considered.
- **Choice and why:** Write a command row where its program is on `PATH`. Write an MCP-tool row in a harness that lists a tool it matches. Write a file row everywhere.
- **Consequences:** Elsewhere the row is `n/a`, with the missing tool named.

## 2026-10-01: the audit marks personal entries personal (#114)

- **Status:** accepted
- **Context:** Personal entries would otherwise show as `extra`.
- **Options:** None considered.
- **Choice and why:** Mark a personal row's entries `personal`, beside their usual mark, never `extra`. An entry that a removed personal row left behind is `extra`, like a dropped table row's.
- **Consequences:** A hand-written allow the person wants kept is proposed as a personal row in the clone, the way #113 carries hand-written Tool values.

## 2026-10-01: verify checks personal entries in Claude Code only (#114)

- **Status:** accepted
- **Context:** Claude Code is the one harness whose settings `verify.py` can read in full.
- **Options:** None considered.
- **Choice and why:** Check personal entries in Claude Code only. An entry belongs to a row when the row covers what the entry names.
- **Consequences:** An MCP-tool row with no entry is `n/a`, since `verify.py` cannot list a harness's tools. The other harnesses' entries are compared in the diff.

## 2026-10-01: personal rows get rule lines (#114)

- **Status:** replaced by [2026-10-01: keep enforcement and remove its inventory from every session](#2026-10-01-keep-enforcement-and-remove-its-inventory-from-every-session)
- **Context:** An agent should read the instructions of personal rows.
- **Options:** None considered.
- **Choice and why:** Personal deny, ask and allow-and-report rows get rule lines in the generated block, after the table's. An `allow` row gets none.
- **Consequences:** None.

## 2026-10-01: nothing is lost on the switch to the repository (#114)

- **Status:** accepted
- **Context:** The shared file can hold a value or line the repository lacks.
- **Options:** None considered.
- **Choice and why:** The diff adds the value or line to the clone's `instructions.md` first.
- **Consequences:** The report names the file for the user to commit, since the skill does not push someone's personal repository.

## 2026-10-01: verify checks the personal parts, and a missing pointer fails (#114)

- **Status:** accepted
- **Context:** The audit must show whether the shared file carries the repository's values.
- **Options:** None considered.
- **Choice and why:** A `personal` line is `ok` when the shared file carries the repository's values, and `none` when the pointer says none. It is `FAIL` when the pointer is missing or malformed, the clone or its file is missing, or a value or the workflow differs. A missing pointer fails because it is a gap the diff closes.
- **Consequences:** A set-up machine never shows a missing pointer. The test homes now carry a `none` pointer.

## 2026-10-01: the reference names no particular tool (#114)

- **Status:** accepted
- **Context:** The skills repo is public and general.
- **Options:** None considered.
- **Choice and why:** `references/personal-repository.md` and the tests describe the kinds of entries with placeholders.
- **Consequences:** None.

## 2026-10-01: Codex CLI preferences are declared in agents/codex.toml (#119)

- **Status:** accepted
- **Context:** Codex CLI preferences are personal, and the public repo must not hold them.
- **Options:** None considered.
- **Choice and why:** Declare them in private `agents/codex.toml`, found through the existing pointer. At first, allow only `sandbox_mode`, `approval_policy` and `approvals_reviewer`.
- **Consequences:** A setting with no declaration stays user-managed, so setup never invents a personal choice.

## 2026-10-01: Codex declarations are validated against the installed CLI (#119)

- **Status:** accepted
- **Context:** Official documentation and installed schemas can differ.
- **Options:** Ignore unsupported input, or assume the inspected version stays current.
- **Choice and why:** Validate against the installed CLI before applying. Reject unsupported source entries and report the support gap.
- **Consequences:** None.

## 2026-10-01: only declared and supported Codex defaults change (#119)

- **Status:** accepted
- **Context:** Codex's config holds much more than the declared defaults.
- **Options:** Migrate conflicting `default_permissions` configurations.
- **Choice and why:** Change only declared, supported defaults, through the existing diff and backup. Keep unrelated TOML, separate profiles, hooks, rules and stricter constraints. Keep conflicting `default_permissions` configurations and report the incompatibility.
- **Consequences:** None.

## 2026-10-01: the Codex config home is resolved once (#119)

- **Status:** accepted
- **Context:** A custom Codex home must cover instructions, config, rules, hooks and verification together.
- **Options:** None considered.
- **Choice and why:** Resolve the Codex config home once and use it everywhere. Fixture runs use an explicit synthetic home.
- **Consequences:** Fixture runs never inherit the live config home or authentication.

## 2026-10-01: persisted Codex defaults are audited apart from session settings (#119)

- **Status:** accepted
- **Context:** Profiles, trusted projects, CLI flags, cloud defaults and enforced requirements can change or constrain the result.
- **Options:** Treat a matching user file as proof of session behavior.
- **Choice and why:** Audit persisted defaults separately from effective session settings. Report observed overrides and unverified layers.
- **Consequences:** None.

## 2026-10-01: running Codex sessions are left alone (#119)

- **Status:** accepted
- **Context:** A changed default could affect sessions already running.
- **Options:** None considered.
- **Choice and why:** Leave existing sessions running. Changes take effect in later sessions. The skill explains `/permissions` where it is supported.
- **Consequences:** Auto-review sends eligible approvals to a reviewer. It keeps the sandbox boundaries and the possibility of refusal.

## 2026-10-01: keep enforcement and remove its inventory from every session

- **Status:** accepted
- **Context:** The shared file carried each row's summary, reason and alternative, and repeated explanations across command variants. This replaces the earlier per-row requirements for the global instructions, including [2026-10-01: personal rows get rule lines](#2026-10-01-personal-rows-get-rule-lines-114) and [2026-09-30: the generated block ends with an environment-variables paragraph](#2026-09-30-the-generated-block-ends-with-an-environment-variables-paragraph).
- **Options:** None considered.
- **Choice and why:** The shared file carries general guidance for a rejection, the common `rm -rf` fallback and a short secrets guardrail. The rule table, personal rows, hook messages and native permissions keep their detail.
- **Consequences:** Every session reads less.

## 2026-10-01: fallback examples come from observed failures

- **Status:** accepted
- **Context:** The shared file could list a fallback for every possible denial.
- **Options:** Pre-load every possible denial.
- **Choice and why:** Add a fallback example only when a real session is stuck after a rejection.
- **Consequences:** None.

## 2026-10-01: role fallbacks are shortened at their source

- **Status:** accepted
- **Context:** The session-host and worktree-tool rows carried long fallbacks.
- **Options:** None considered.
- **Choice and why:** Keep the action and remove the explanation, in the source rows.
- **Consequences:** None.

## 2026-10-01: the personal workflow is grouped by topic

- **Status:** accepted
- **Context:** The personal workflow section had a fixed intro and one flat list.
- **Options:** None considered.
- **Choice and why:** Use short rules under third-level headings, keeping the meaning in the personal source. Copy those headings into the shared file. Leave out empty categories and the old fixed intro.
- **Consequences:** None.

## 2026-10-01: approver user on an ask row (#67)

- **Status:** accepted
- **Context:** Some asks, such as a saved mail draft, must reach the user, not an automatic reviewer or a mode that answers for them.
- **Options:** None considered.
- **Choice and why:** An ask row can say `approver: "user"`. The hook refuses its calls where the payload shows no one will ask: Claude Code's `auto`, `dontAsk` and `bypassPermissions` modes, Codex under approval policy `never`, and every call under Cursor and opencode, which cannot promise a prompt.
- **Consequences:** Claude Code's docs say auto mode still asks for an ask rule, but no probe has shown it for an MCP tool. Auto mode stays refused until one does.

## 2026-10-01: Codex has native entries for MCP tools (#67)

- **Status:** accepted
- **Context:** The Codex note said MCP tools had no native entries. It was stale.
- **Options:** None considered.
- **Choice and why:** Use Codex's native entries: `disabled_tools` and per-tool `approval_mode` on `[mcp_servers.<id>]`, and per-tool `enabled` and `approval_mode` plus an `approvals_reviewer` on `[apps.<id>]`.
- **Consequences:** A plain MCP server has no reviewer of its own. So under a top-level `auto_review`, an `approver: "user"` row there is a gap.

### References

- Codex's configuration reference and `openai/codex` at `2685e3a`: the MCP and apps entries.

## 2026-10-01: opencode takes MCP tool names as permission keys (#67)

- **Status:** accepted
- **Context:** opencode names MCP tools `<server>_<tool>`.
- **Options:** None considered.
- **Choice and why:** Use the names as permission keys, with wildcards allowed. A row is native once a session lists the tools.
- **Consequences:** opencode's `--auto` mode answers every ask, which the plugin cannot see.

## 2026-10-01: secrets stay behind rules, with the gap accepted (#98)

- **Status:** accepted
- **Context:** The research in `docs/research/secrets-out-of-reach.md` showed what else could close the gap left by the rows.
- **Options:**
  - 1Password (`op run`): not worth paying for while no real secret sits on the machine.
  - Claude Code's OS sandbox: the only option that closes the gap, but it breaks git over SSH, `herdr`, `gh` and notifications unless each is excluded.
  - A Codex deny profile: not worth it for the same reason.
- **Choice and why:** Guard the obvious paths only. The rows, the hook and the shared secrets guardrail stay the whole defence on every harness.
- **Consequences:**
  - An interpreter (`python3 -c 'open(".env")'`), a glob the shell expands (`cat .e?v`) and another process's launch environment (`ps eww`, or any same-user process on macOS) get past the rows. Only the global instruction to never read, print or change secrets covers them. Rules cannot parse interpreter code reliably, so the gap is named, not chased.
  - Hygiene stays outside the rule table: keep tokens out of shell profiles, and keep a project's keys in its gitignored `.env`.
  - Reopen this when a real secret lives on the machine.

## 2026-10-01: two more secret file rows (#98)

- **Status:** accepted
- **Context:** Common token files were not covered.
- **Options:** Cover `*.key` and `id_*`: Keynote files share `*.key`, and `~/.ssh` already covers `id_*`.
- **Choice and why:** `home-credentials-read` covers the token files of git (`~/.netrc`, `~/.git-credentials`), `gh` (`~/.config/gh/hosts.yml`), npm (`~/.npmrc`), Docker (`~/.docker/config.json`) and `~/.kube/config`. `key-files-read` covers `*.pem`, `*.p12` and `*.pfx` anywhere.
- **Consequences:** The tools that own the token files still read them.

## 2026-10-03: the workstation repo lists what every machine installs

- **Status:** accepted
- **Context:** The skill installed only `<skills-repo>`. A skill from another source or a session host's plugin was a hand step in the user's notes, so machines drifted. This replaces [2026-09-29: the user's own skills repo is installed as a plan item](#2026-09-29-the-users-own-skills-repo-is-installed-as-a-plan-item).
- **Options:** None considered.
- **Choice and why:** `agents/installs.json` lists skills by source, with an optional list of names, and anything else as a `check` and `install` command pair. Commands keep the skill free of any one tool: it never learns what a plugin is.
- **Consequences:** None.

## 2026-10-03: target and os pick the machines

- **Status:** accepted
- **Context:** Some installs belong only on some machines.
- **Options:** None considered.
- **Choice and why:** `target` separates `local`, the machine the user sits at, from `remote`, the ones Inspect treats as remote. `os` separates macOS from Linux. A field left out matches every machine.
- **Consequences:** The common entry stays short.

## 2026-10-03: the installs file is the whole list

- **Status:** accepted
- **Context:** A machine could get something the user left out on purpose.
- **Options:** None considered.
- **Choice and why:** With the file, `<skills-repo>` is installed only when the file lists it. Without the file, the skill installs `<skills-repo>` as before.
- **Consequences:** A person with no file loses nothing.

## 2026-10-03: outdated means the hash differs

- **Status:** accepted
- **Context:** A source counted as present once any one of its skills was installed, and nothing was ever updated.
- **Options:** None considered.
- **Choice and why:** The lock's `skillFolderHash` is the git tree hash of the skill's folder, the same `sha` the GitHub trees API returns. A skill whose hash differs is outdated.
- **Consequences:** One call per source finds every skill behind its source.

## 2026-10-03: installs need no separate approval

- **Status:** accepted
- **Context:** Writing the installs file is already the user's approval.
- **Options:** None considered.
- **Choice and why:** A diff with only installs and updates from the file is written without asking.
- **Consequences:** None.

## 2026-10-03: personal repository becomes workstation repo

- **Status:** accepted
- **Context:** The maintainer found "personal repository" and "personal rows" vague.
- **Options:** None considered.
- **Choice and why:** Say "workstation repo" and "personal permissions". The reference file moved to `references/workstation-repo.md`.
- **Consequences:** Code names, such as `personal.py`, stay, since renaming them changes nothing a reader sees. Earlier entries keep the old words.

## 2026-10-03: a skill name clash is a gap

- **Status:** accepted
- **Context:** The lock holds one skill per name. When an entry would install a name already installed from another source, or two entries give the same name, `npx skills add` would silently replace one source's copy on every machine.
- **Options:** None considered.
- **Choice and why:** A clash is a `gap`, and nothing is installed for that name. The audit names both sources.
- **Consequences:** The user makes the choice.

## 2026-10-03: a clash with a built-in command is noted, not skipped

- **Status:** accepted
- **Context:** A skill's name can match a harness's built-in command, and one may hide the other.
- **Options:** Skip the skill: the user listed it on purpose.
- **Choice and why:** Note it as a `gap` and still install it.
- **Consequences:** None.

## 2026-10-03: an ignore list for deliberate leftovers

- **Status:** accepted
- **Context:** A machine can have skills the list leaves out on purpose, such as an experiment or a hand-made skill the lock does not track. They looked like drift.
- **Options:** None considered.
- **Choice and why:** `ignore` lists them. The audit marks them `ignored` instead of `extra`, and never installs or removes them.
- **Consequences:** A name that is both ignored and listed is a malformed file, since the two say opposite things.

## 2026-10-09: the shared file has a working agreement and a glossary

- **Status:** accepted
- **Context:** The user wants one cohesive global instructions file, ordered from general to specific.
- **Options:** None considered.
- **Choice and why:** Add two optional sections. The order is: working agreement, glossary, environment defaults with `### <Tool> glossary` subsections, the generated rules block, and the personal workflow. How the user works with agents comes first, then the words they share, then which tool fills each role.
- **Consequences:** None.

## 2026-10-09: harness-specific words go in tool glossaries

- **Status:** accepted
- **Context:** The shared glossary must hold in every harness and session host.
- **Options:** None considered.
- **Choice and why:** A `### <Tool> glossary` under the roles table says what a word is in one tool, such as a session in `herdr`.
- **Consequences:** When the user changes a tool, only its glossary changes, and the shared glossary stays harness-agnostic.

## 2026-10-09: the workstation repo is the source of the new sections

- **Status:** accepted
- **Context:** The new sections need a source, as the personal workflow has.
- **Options:** None considered.
- **Choice and why:** `agents/instructions.md` has the same sections in the same order. Each optional section is copied when it is there and left out when it is not.
- **Consequences:** Without a workstation repo, the user's sections in the shared file stay as they are.

## 2026-10-09: verify counts the new sections toward personal ok

- **Status:** accepted
- **Context:** The audit must cover the new sections.
- **Options:** None considered.
- **Choice and why:** A section that differs, is missing from the shared file, or is in the shared file without a source is `personal FAIL`.
- **Consequences:** None.

## 2026-10-09: the skill relies on the workstation repo's agents/ folder only

- **Status:** accepted
- **Context:** The workstation repo also holds documents for whoever maintains the setup, such as the user's principles or a full glossary.
- **Options:** None considered.
- **Choice and why:** The skill relies on the `agents/` folder and nothing else. The repo's own `AGENTS.md` names the other documents.
- **Consequences:** Their names and paths stay the user's. The shared file's glossary holds only the core words.

## 2026-10-09: the workstation repo is a parameter and a role

- **Status:** accepted
- **Context:** The skill found the workstation repo only through the pointer and named no parameter for it. Someone who installs the public skills cannot see the user's repository. This replaces [2026-10-01: the pointer is ~/.config/agents/source.md](#2026-10-01-the-pointer-is-configagentssourcemd-113).
- **Options:** None considered.
- **Choice and why:** `<workstation-repo>` and `<path-to-workstation-repo>` are parameters and roles. The skills name the repository as a parameter, say what it holds, work without one, and say how to start one.
- **Consequences:** The pointer stays, as the next entry says.

## 2026-10-09: the pointer fills the two roles' Tool column

- **Status:** accepted
- **Context:** The skill needs the pointer to find the repository before it generates anything.
- **Options:** None considered.
- **Choice and why:** The pointer stays the source and fills the two roles' Tool column. `agents/instructions.md` leaves the two rows out.
- **Consequences:** `verify.py` fails a shared file whose rows differ from the pointer or lack them. It also fails an `agents/instructions.md` row that differs from the pointer.

## 2026-10-09: this skill reads the workstation repo and maintain-environment owns it

- **Status:** accepted
- **Context:** Two skills described the workstation repo.
- **Options:** None considered.
- **Choice and why:** `references/workstation-repo.md` became `references/workstation.md`. It keeps the pointer, the `agents/` format, generation and the run without a repository. What the repository is for, its starting layout and how to start one moved to `/maintain-environment`'s `references/workstation.md`.
- **Consequences:** None.

## 2026-10-09: without a workstation repo, the skill works as before

- **Status:** accepted
- **Context:** Not everyone has a workstation repo.
- **Options:** None considered.
- **Choice and why:** The personal lines stay in the shared file.
- **Consequences:** The report says that `/maintain-environment` can start a workstation repo.

## 2026-10-10: the hook refuses every ask row under Cursor

- **Status:** accepted
- **Context:** Cursor has no ask list. Its CLI permissions have only `allow` and `deny`. Auto-review sends an unlisted command to a classifier that "is not a security boundary". A live test on Linux ran `git clean -f -n` without a prompt. Claude Code asks for an ask rule even in auto mode.
- **Options:** Refuse only the `approver: "user"` rows: Cursor would run the other ask rows without asking.
- **Choice and why:** Refuse every ask row under Cursor. A refusal is the nearest Cursor can come to asking, so the user runs the command.
- **Consequences:** Each of the four rows tells the agent to stop and give the user the exact command when no one will be asked, as the mail rows do.

### References

- [CLI permissions](https://cursor.com/docs/cli/reference/permissions) and [run modes](https://cursor.com/docs/agent/security/run-modes): Cursor has no ask list, and Auto-review is not a security boundary.
- [Claude Code permissions](https://code.claude.com/docs/en/permissions): Claude Code asks for an ask rule in auto mode.

## 2026-10-10: a no_native_ask flag for Cursor

- **Status:** accepted
- **Context:** The hook already treats Claude Code's `auto` mode as unattended for `approver: "user"` rows.
- **Options:** Mark the four rows `approver: "user"`: Claude Code's auto mode would refuse them too, where Claude Code asks today.
- **Choice and why:** A new `no_native_ask` flag. Only Cursor's reader sets it.
- **Consequences:** Claude Code, Codex and opencode keep their behavior.

## 2026-10-10: a personal instructions file per harness

- **Status:** replaced by [2026-10-11: setup/harnesses.json points at each harness's files](#2026-10-11-setupharnessesjson-points-at-each-harnesss-files-195)
- **Context:** Harnesses differ: Cursor has a sandbox and no ask list, and Claude Code has neither. A line about one harness in the shared file reaches every harness and confuses the others. The user wants these lines in the workstation repo.
- **Options:** None considered.
- **Choice and why:** `agents/harnesses/<harness>.md` holds one harness's lines. The skill holds only the mechanism, not the content.
- **Consequences:** `verify.py` compares each generated file with its source, as for the shared file, with a `harness` line per file.

## 2026-10-10: only the Instructions section is copied

- **Status:** accepted
- **Context:** A harness file can hold notes beside its instructions.
- **Options:** None considered.
- **Choice and why:** Copy only the `## Instructions` section. The rest of the file is notes, as in `agents/instructions.md`.
- **Consequences:** None.

## 2026-10-10: per-harness instructions start with Cursor

- **Status:** accepted
- **Context:** Cursor reads every `~/.cursor/rules/*.mdc` with `alwaysApply: true`. Claude Code, Codex and opencode read the shared file through a link, so each needs its own way in.
- **Options:** None considered.
- **Choice and why:** Support Cursor first, through a second generated rule file. It adds the lines without touching the shared file.
- **Consequences:** Until the others have a way in, a source for one of them is a `gap` line.

## 2026-10-10: Cursor gets entries for the Claude Code plugins it imports

- **Status:** accepted
- **Context:** Cursor's CLI imports Claude Code's plugins, with their skills and MCP servers. A plugin's server is `plugin-<plugin>-<server>` there, and `cursor-agent mcp list` cannot list it. The old listing step found nothing, so a row like a personal Exa allow left Cursor asking, or a headless run rejecting the call.
- **Options:** None considered.
- **Choice and why:** Claude Code's tool listing supplies the tools. The two names differ only in `_` and `-`, so each matched `mcp__plugin_<plugin>_<server>__<tool>` becomes `Mcp(plugin-<plugin>-<server>:<tool>)`. A test on Linux with `agent` 2026.10.01 ran Exa's search without a prompt with the entry, and the call asked without it.
- **Consequences:** Only the skills import is in Cursor's docs. The plugin import sits behind a switch Cursor controls, so the reference treats it as a fact to check, not a promise.

## 2026-10-10: Pi is a harness for instructions, skills, memory and declared defaults

- **Status:** accepted
- **Context:** Pi 1.1.0's bundled docs and its `dist/` source show how it reads instructions and skills. Pi reads the first of `AGENTS.override.md`, `AGENTS.md`, `AGENTS.MD`, `CLAUDE.md` and `CLAUDE.MD` in its agent folder, and it follows symlinks.
- **Options:** None considered.
- **Choice and why:** `<agent-dir>/AGENTS.md` is a relative symlink to the shared file, as for opencode. Pi finds skills in `~/.agents/skills` and removes duplicates by real path, so it needs no install of its own.
- **Consequences:** Pi has no memory feature, so there is nothing to turn off.

## 2026-10-10: Pi's agent folder is resolved once

- **Status:** accepted
- **Context:** `PI_CODING_AGENT_DIR` moves the folder, as `CODEX_HOME` moves Codex's.
- **Options:** None considered.
- **Choice and why:** Resolve the folder once. `verify.py` honors the variable on the real home without printing it. A fixture home ignores it unless `--pi-agent-dir` names a folder.
- **Consequences:** None.

## 2026-10-10: Pi's declared defaults are merged key by key

- **Status:** accepted
- **Context:** Pi writes runtime state into the same `settings.json`, such as `deviceId` and `lastChangelogVersion`.
- **Options:** Copy the whole file: it overwrites that state.
- **Choice and why:** `agents/pi.json` declares defaults. The skill merges only the declared keys, and `verify.py` compares only those keys and never prints their values.
- **Consequences:** Unlike `agents/codex.toml`, the file has no allowlist of keys, since Pi's settings are plain JSON with no parser to probe.

## 2026-10-10: Pi's enforcement waits for a design

- **Status:** replaced by [2026-10-10: an extension runs the hook on every Pi tool call](#2026-10-10-an-extension-runs-the-hook-on-every-pi-tool-call)
- **Context:** Pi has no permission system and asks for no approval (`docs/security.md`). An extension can block a tool call from a `tool_call` handler, but how it runs the hook was not decided.
- **Options:** None considered.
- **Choice and why:** The reference names permissions and the hook as one `gap`. `verify.py` prints `hook gap` for Pi, which does not fail the audit.
- **Consequences:** Pi has no guardrail until the design is done.

## 2026-10-10: a session host's Pi integration stays out of this skill

- **Status:** accepted
- **Context:** A session host's integration, such as `herdr integration install pi`, writes its own extension.
- **Options:** None considered.
- **Choice and why:** The workstation repo's installs list carries it, as it carries the integrations for the other harnesses.
- **Consequences:** None.

## 2026-10-10: an extension runs the hook on every Pi tool call

- **Status:** accepted
- **Context:** The maintainer asked for Pi's extensions used as Pi intends them, with parity to the Claude Code setup, and left the technical choices to the agents. This replaces [2026-10-10: Pi's enforcement waits for a design](#2026-10-10-pis-enforcement-waits-for-a-design).
- **Options:** None considered.
- **Choice and why:** `<agent-dir>/extensions/set-up-machine.ts` comes from `references/pi-extension.ts`, as opencode's plugin comes from its template. Its `tool_call` handler sends the call to `pre_tool_hook.py --harness pi`. A refusal becomes `{ block: true, reason }`, and Pi gives the agent the reason as the tool's result. Nested calls from `codemode` scripts reach the handler one by one, and a live run on Pi 1.1.0 refused a nested `rm -rf`.
- **Consequences:** Named gaps:
  - A handler after the hook can change `event.input`. In Pi 1.1.0, packages' and built-in extensions load after the global folder, and Pi offers no way to run last.
  - A package can start child sessions without extensions. `pi-subagents` 0.77.0 does this for foreground children.
  - `--no-extensions` skips the hook.
  - The user's `!` commands are not tool calls.

## 2026-10-10: the Pi extension asks with No as the first answer

- **Status:** accepted
- **Context:** Pi has no ask list, but an extension can show a dialog. Pi's `ctx.ui.confirm` is a `select` dialog with Yes first, so a stray Enter would allow the call.
- **Options:** `ctx.ui.confirm`: Enter allows the call.
- **Choice and why:** The hook answers `{"ask": …}`, and the extension calls `ctx.ui.select` with No first, so Enter and Escape both refuse. Without a UI, in print and JSON mode, the hook refuses every ask row. This uses `no_native_ask`, as for Cursor, and sets `unattended` only when `hasUI` is false.
- **Consequences:** A writer now takes `(denials, asks=())`. Only Pi's writer uses the ask hits, so the other harnesses answer as before.

## 2026-10-10: the Pi extension fails closed

- **Status:** accepted
- **Context:** The other harnesses fail open because their native rules stay underneath. Pi has none, so failing open would mean no guardrail at all. A first draft failed open, and the maintainer's review asked for this change.
- **Options:** Fail open, as the other harnesses do.
- **Choice and why:** A missing script, a failed start, a non-zero exit, an answer that is not a JSON object, or a 10-second timeout blocks the call. The reason tells the agent the guardrail is unavailable and the user should run `/set-up-machine`.
- **Consequences:** `pi --no-extensions` is the way out until then.

## 2026-10-10: the session host sees the Pi dialog

- **Status:** accepted
- **Context:** Pi reports `blocked` to the terminal on its own (OSC 7501). Herdr's Pi integration reported the pane as `working` while the dialog waited. The integration (version 9) listens for a `herdr:blocked` event on Pi's event bus.
- **Options:** Ring the terminal bell: a write to stdout could break the TUI or the RPC protocol.
- **Choice and why:** The extension emits `herdr:blocked` around the dialog, and a live run showed the pane as `blocked`. It adds a `ctx.ui.notify` warning too.
- **Consequences:** None.

## 2026-10-10: verify checks the Pi extension like opencode's plugin

- **Status:** accepted
- **Context:** Nothing else enforces the rule table in Pi.
- **Options:** None considered.
- **Choice and why:** No extension is `FAIL`. A foreign file at the same path is a `gap`, left alone.
- **Consequences:** None.

## 2026-10-10: plugins are a setup area with their own list

- **Status:** accepted
- **Context:** Plugins were plain `commands` entries. The skill could not tell a plugin from any other install, or which harness should have it. The user's setup describes every harness by five setup areas, and plugins are one of them.
- **Options:** None considered.
- **Choice and why:** A `plugins` list in `agents/installs.json`. Each entry names its kind, its source or server, and the harnesses that get it.
- **Consequences:** None.

## 2026-10-10: a plugin is a bundle or a standalone MCP server

- **Status:** accepted
- **Context:** The list needs kinds.
- **Options:** None considered.
- **Choice and why:** A bundle installs MCP servers, skills and hooks as one unit. A standalone MCP server is a plugin with only that server.
- **Consequences:** Skills stay their own area, through `skills`.

## 2026-10-10: each harness takes plugins its own documented way

- **Status:** accepted
- **Context:** Harnesses install plugins differently.
- **Options:** None considered.
- **Choice and why:** Each harness's reference has a Plugins section. Claude Code installs bundles. Cursor gets bundles only by importing Claude Code's, since its CLI has no install command, and it takes standalone servers in `~/.cursor/mcp.json`.
- **Consequences:** None.

## 2026-10-10: plugin gaps are named, not guessed

- **Status:** accepted
- **Context:** Some plugin setups cannot be checked safely or are not yet described.
- **Options:** Guess.
- **Choice and why:** `verify.py` prints a `gap` line for each: a standalone MCP server in Claude Code, since checking it means reading `~/.claude.json`, which can hold tokens; and any plugin in Codex, opencode and Pi until their references say how.
- **Consequences:** [2026-10-10: Pi takes plugins](#2026-10-10-pi-takes-plugins) and [2026-10-10: Codex plugins come from the installs list](#2026-10-10-codex-plugins-come-from-the-installs-list) later closed the Pi and Codex gaps.

## 2026-10-10: verify only reads plugin files

- **Status:** accepted
- **Context:** The plugin check must not change anything.
- **Options:** None considered.
- **Choice and why:** `verify.py` reads Claude Code's `installed_plugins.json` and `enabledPlugins`, the plugin folder's `mcp.json` for the server names Cursor shows, and `~/.cursor/mcp.json`.
- **Consequences:** An enabled bundle the list leaves out is `extra`, because Cursor imports it too.

## 2026-10-10: Pi takes plugins

- **Status:** accepted
- **Context:** The plugins setup area named Pi as a gap. Pi 1.1.0 documents both kinds.
- **Options:** None considered.
- **Choice and why:** Pi's reference has a real Plugins section, and `verify.py` checks Pi entries.
- **Consequences:** None.

## 2026-10-10: Pi's own word is extension

- **Status:** accepted
- **Context:** For Pi, every item the user writes or takes from others is an extension. The maintainer asked for this in review.
- **Options:** None considered.
- **Choice and why:** "Plugins" stays the name of the setup area. For Pi, the skill, `verify.py` and the tests say "extension".
- **Consequences:** Literal names keep their form: the `packages` key in `settings.json`, `pi install` and `pi list`.

## 2026-10-10: a Pi bundle is a Pi extension in packages

- **Status:** accepted
- **Context:** Pi delivers extensions through `packages` in `<agent-dir>/settings.json`.
- **Options:** None considered.
- **Choice and why:** The skill adds a missing source and replaces an entry for the same extension at another version. It keeps every other entry.
- **Consequences:** None.

## 2026-10-10: a Pi extension source fits only an entry for Pi alone

- **Status:** accepted
- **Context:** A Pi `source` is Pi's own form: `npm:`, `git:` or an `https://` git URL. Claude Code and Cursor need `<plugin>@<marketplace>`, and Pi cannot install that form.
- **Options:** A local path: it does not name the same extension on every machine.
- **Choice and why:** One entry cannot serve both, so the validator refuses each mix.
- **Consequences:** None.

## 2026-10-10: Pi extension identity follows Pi

- **Status:** accepted
- **Context:** Pi treats an npm source by its name, and a git source by its host and repository path without the ref.
- **Options:** None considered.
- **Choice and why:** `verify.py` uses the same identity. It prints `FAIL` for another version of a listed extension, and `extra` for a configured extension the list leaves out.
- **Consequences:** None.

## 2026-10-10: a changed git ref needs pi update

- **Status:** replaced by [2026-10-10: setup does not handle a pinned package](#2026-10-10-setup-does-not-handle-a-pinned-package)
- **Context:** At startup Pi installs only a missing extension, and reinstalls an npm one whose version does not match. It leaves an existing git checkout at its old ref. A live change from `@v0.1.0` to `@v0.2.0` stayed at `v0.1.0` until `pi update <source>` ran.
- **Options:** None considered.
- **Choice and why:** `verify.py` compares the checkout's `HEAD` with the ref, read-only through `git rev-parse`. It also reads `FETCH_HEAD`, since `pi update` fetches the ref and resets to it without a local tag. A checkout at another commit is a `FAIL` that names the `pi update` command.
- **Consequences:** None.

## 2026-10-10: standalone MCP servers for Pi go in mcp.json

- **Status:** accepted
- **Context:** Pi's built-in MCP client reads `<agent-dir>/mcp.json`.
- **Options:** None considered.
- **Choice and why:** Put standalone servers there. `verify.py` compares the entry as it does for Cursor.
- **Consequences:** `verify.py` prints a `gap` when `-builtin:mcp` turns that client off.

## 2026-10-10: setup does not handle a pinned package

- **Status:** accepted
- **Context:** The maintainer has no pinned-package use case. This replaces [2026-10-10: a changed git ref needs pi update](#2026-10-10-a-changed-git-ref-needs-pi-update).
- **Options:** None considered.
- **Choice and why:** Every source installs latest, and recorded versions are history only. The verifier does not detect a pin. It prints no policy gap for a fixed source, does not compare a git checkout with a declared ref, and does not advise `pi update` for a pin.
- **Consequences:** The plugin adapters keep this too: the Pi adapter does not compare a git checkout with a ref.

## 2026-10-10: one source for Pi extensions

- **Status:** accepted
- **Context:** `agents/pi.json` could also declare `packages`, as a Pi setting.
- **Options:** Two lists: they would disagree.
- **Choice and why:** A `packages` key in `agents/pi.json` is a `gap` that asks the user to move it into `plugins`. The skill neither compares nor writes it.
- **Consequences:** None.

## 2026-10-10: Codex plugins come from the installs list

- **Status:** accepted
- **Context:** The plugins setup area named Codex as a gap.
- **Options:** None considered.
- **Choice and why:** Install portable bundles through Codex's marketplace commands. Compare standalone MCP entries against the resolved config home.
- **Consequences:**
  - Synthetic-home tests cover policy drift, custom config homes, authentication status and preservation. A repeat proposal produces no changes.
  - A fresh skill audit found malformed approval values, scalar owned tables and quoted comment markers. Each has a fix with a regression test. Malformed existing tool lists are refused for guided review.
  - The team test exempts this setup skill. Personal plugin choices remain workstation declarations.

### References

- [Codex MCP configuration](https://learn.chatgpt.com/docs/extend/mcp) and [developer commands](https://learn.chatgpt.com/docs/developer-commands).

## 2026-10-10: Codex MCP policies are declared in codex_mcp

- **Status:** replaced by [2026-10-10: mcp_policy replaces codex_mcp](#2026-10-10-mcp_policy-replaces-codex_mcp)
- **Context:** Bundled MCP servers need per-tool policies.
- **Options:** None considered.
- **Choice and why:** Declare them in `codex_mcp`. Personal tool choices stay in the workstation. The delivery mechanism stays in this skill.
- **Consequences:** None.

## 2026-10-10: Codex TOML outside the skill's entries is kept

- **Status:** accepted
- **Context:** Codex's config holds the user's own settings.
- **Options:** None considered.
- **Choice and why:** Generate a pure proposal before applying the approved diff. Keep stricter tool lists. Refuse unfamiliar syntax.
- **Consequences:** None.

## 2026-10-10: Codex OAuth is checked through the CLI

- **Status:** accepted
- **Context:** Credential files must not be read.
- **Options:** Read the credential files.
- **Choice and why:** Check OAuth through the CLI and its actual status. Codex 0.162.1 reports authenticated OAuth as `o_auth`, and disabled servers report `unsupported`.
- **Consequences:** A missing sign-in is a gap. Servers that need authentication stay disabled until sign-in succeeds. The adapter reads configuration and OAuth metadata without calling an MCP tool.

## 2026-10-10: installation is not tool parity

- **Status:** accepted
- **Context:** A cached manifest proves an installed bundle. It does not prove supported components or live tool discovery.
- **Options:** Probe the live tools: that calls the service.
- **Choice and why:** Report installation and tool parity apart. Honor excluded tools without live probes. Keep exclusions independent of the approval reviewer, and check their configuration without calling the service.
- **Consequences:** None.

## 2026-10-10: mcp_policy replaces codex_mcp

- **Status:** accepted
- **Context:** Every harness needs per-tool MCP policies, not only Codex. This replaces [2026-10-10: Codex MCP policies are declared in codex_mcp](#2026-10-10-codex-mcp-policies-are-declared-in-codex_mcp).
- **Options:** None considered.
- **Choice and why:** One `mcp_policy` object on the installs entry serves every harness. Its fields are `enabled_tools`, `disabled_tools`, `approval_mode` and `require_oauth`.
- **Consequences:** None.

## 2026-10-10: permissions are the source for tool lists

- **Status:** accepted
- **Context:** Tool lists could live in `mcp_policy` or in the permissions.
- **Options:** None considered.
- **Choice and why:** The rule table and `agents/permissions.json` name the tools. Each adapter derives its harness's list from those rows.
- **Consequences:** A copy in `mcp_policy` is optional.

## 2026-10-10: one plugin module per harness

- **Status:** replaced by [2026-10-11: one harness setup per harness](#2026-10-11-one-harness-setup-per-harness)
- **Context:** Each harness that takes plugins needs its own logic.
- **Options:** None considered.
- **Choice and why:** Each harness exposes `validate`, `check` and `propose` when it takes plugins. Discovery loads them through a lookup table.
- **Consequences:** None.

## 2026-10-10: the skill owns the Codex procedure

- **Status:** accepted
- **Context:** The Codex plugin steps need one home.
- **Options:** None considered.
- **Choice and why:** `references/codex.md` gives numbered steps and a done check. The TOML and OAuth detail is a subsection at the end of that file.
- **Consequences:** None.

## 2026-10-11: setup/ replaces agents/ (#195)

- **Status:** accepted
- **Context:** The workstation repo moved each harness's files into that harness's own folder (#195). This replaces the `agents/` paths in the entries above, from [2026-10-01: the repository's files sit in an agents/ folder](#2026-10-01-the-repositorys-files-sit-in-an-agents-folder-113) on.
- **Options:** None considered.
- **Choice and why:** `setup/` is the one folder the skill relies on. It holds `instructions.md`, `permissions.json` and `installs.json` in full.
- **Consequences:** The hook's state folder and `~/.config/agents/` keep their names, since they are not workstation paths.

## 2026-10-11: setup/harnesses.json points at each harness's files (#195)

- **Status:** accepted
- **Context:** Cursor's instructions and the Codex and Pi configs now sit in their harness folders. This replaces [2026-10-10: a personal instructions file per harness](#2026-10-10-a-personal-instructions-file-per-harness).
- **Options:** None considered.
- **Choice and why:** An entry in `setup/harnesses.json` takes `instructions`, `config`, or both. Paths are relative to the repository's root.
- **Consequences:** A `config` for a harness without a config reader is a `gap`. Only Codex and Pi have one today.

## 2026-10-11: one module knows the workstation layout (#195)

- **Status:** replaced by [2026-10-12: one explicit list of harnesses](#2026-10-12-one-explicit-list-of-harnesses)
- **Context:** Many readers need workstation paths.
- **Options:** None considered.
- **Choice and why:** `scripts/setupmachine/layout.py` names the folder and the harnesses file. Every reader asks it for a path.
- **Consequences:** A later layout change is one edit.

## 2026-10-11: no fallback to agents/ (#195)

- **Status:** accepted
- **Context:** The skill and the workstation repo change together.
- **Options:** A fallback to the old layout.
- **Choice and why:** No fallback. The skill pull request merges first, and the workstation pull request merges right after it. Nobody runs `/set-up-machine` between the two merges.
- **Consequences:** No machine needs the old layout.

## 2026-10-11: the harnesses file is strict (#195)

- **Status:** accepted
- **Context:** A guessed path could write the wrong file.
- **Options:** None considered.
- **Choice and why:** The file needs `version` 1. An unknown key, an unknown harness, or a path outside the repository is a `FAIL` that names the problem. A path to a missing file is a `FAIL` that names the pointer, such as `harnesses.cursor.instructions`.
- **Consequences:** None.

## 2026-10-11: the generated header names the source path (#195)

- **Status:** accepted
- **Context:** A file generated from the old path must not look like someone else's file.
- **Options:** None considered.
- **Choice and why:** Cursor's `harness-instructions.mdc` names the path from the harnesses file. Any header that starts with the generated prefix counts as the skill's file.
- **Consequences:** A file from the old path differs and is rewritten, not left alone.

## 2026-10-11: one harness setup per harness

- **Status:** replaced by [2026-10-12: one explicit list of harnesses](#2026-10-12-one-explicit-list-of-harnesses)
- **Context:** The skill registered one harness in several lists: the verifier's wiring table, the hook's reader table, the plugin checker's adapter table, and the skill body's audit lines. Adding a harness meant editing all of them. This replaces [2026-09-29: each harness adds a reader and a writer to hook.HARNESSES](#2026-09-29-each-harness-adds-a-reader-and-a-writer-to-hookharnesses-54) and [2026-10-10: one plugin module per harness](#2026-10-10-one-plugin-module-per-harness).
- **Options:** None considered.
- **Choice and why:** A harness setup is the single registration for one harness. Its module holds the harness's audit, its hook translation and, when it takes plugins, its plugin adapter. The verifier, the hook and the plugin checker load every module in `scripts/setupmachine/harness_setups/`. A new harness is one new module, with no list of names to edit.
- **Consequences:**
  - Printed audit lines stay the same. A `FAIL` still fails the run, and a `gap` still leaves it passing.
  - The skill body states the run. Each harness reference states that harness's lines. Each rule-row field is described once, in `references/rule-table.md`.

## 2026-10-12: the agent writes the setup; scripts only enforce and check

- **Status:** accepted
- **Context:** About 200 lines of Python could write harness files (`propose`), but only the tests called them, and the maintainer wants the agent to do the writing.
- **Options:** Keep a script that writes the setup: it repeats what the references say and goes stale when a harness changes its format.
- **Choice and why:** The agent writes every harness file by following the harness references. Two scripts stay: the pre-tool hook, which enforces, and the verifier, which checks.
- **Consequences:** The file-writing code is gone. A harness format change touches its reference and its check only.

### References
- [Spec: Give each environment skill one job and a readable verifier (#213)](https://github.com/yahyabedirhan/skills/issues/213): the redesign these entries come from.

## 2026-10-12: the verifier prints one harness by setup-area table

- **Status:** accepted
- **Context:** The maintainer could not tell what `verify.py` checked. It printed about a dozen channels and thirteen status words, and it never checked skills or memory.
- **Options:** Keep the channel lines: they mix outcomes with mechanics, and only `FAIL` mattered.
- **Choice and why:** A `setup` line, a `rules` line, then one table: a row per harness, a column per setup area (instructions, guardrails, sandbox, plugins, skills). A cell is `ok`, `FAIL`, `gap` or `n/a`, the worst of its checks. Exit 1 on any `FAIL`.
- **Consequences:** set-up-project depends only on the exit code. Skills are now checked: each listed skill needs a `SKILL.md` in a folder the harness reads.

### References
- [Spec: Give each environment skill one job and a readable verifier (#213)](https://github.com/yahyabedirhan/skills/issues/213): the redesign these entries come from.

## 2026-10-12: one explicit list of harnesses

- **Status:** accepted
- **Context:** This replaces the harness setups found by folder discovery, and `layout.py`'s own list of harness labels. Discovery used attribute checks and `inspect.signature`, which the maintainer could not follow, and a second list existed anyway.
- **Options:** Folder discovery: it hides the registration and needed function inspection.
- **Choice and why:** `ALL` in `scripts/setupmachine/harnesses/__init__.py` names every harness. Each module has the same names: `ID`, `LABEL`, `present`, `read`, `write`, and one `check_<area>` per setup area.
- **Consequences:** Adding a harness is one module, one line in `ALL` and one reference.

### References
- [Spec: Give each environment skill one job and a readable verifier (#213)](https://github.com/yahyabedirhan/skills/issues/213): the redesign these entries come from.

## 2026-10-12: no unit tests in the repo

- **Status:** accepted
- **Context:** The repo held 255 unit tests, many on wording, plumbing or code only the tests called.
- **Options:** Keep the tests: they pinned details the maintainer did not want, and doubled the code to read.
- **Choice and why:** Delete `scripts/tests/`. A maintainer writes throwaway tests in `.scratch/` while changing a script. The rule samples, which the verifier runs through the hook on every machine, are the check that stays.
- **Consequences:** A refactor of the hook needs a throwaway comparison against the old behaviour, as this one had.

### References
- [Spec: Give each environment skill one job and a readable verifier (#213)](https://github.com/yahyabedirhan/skills/issues/213): the redesign these entries come from.

## 2026-10-12: the verifier needs no network and no harness CLI

- **Status:** accepted
- **Context:** The old verifier started Codex in a temp home to probe its config parser, ran `codex execpolicy` and `codex mcp list`, and printed a fixed freshness line.
- **Options:** Keep the probes: they never failed the run, and they made it slow and hard to read.
- **Choice and why:** The verifier reads installed files only. Upstream versions and sign-ins are the agent's checks in Inspect.
- **Consequences:** A Codex OAuth sign-in is not verified.

### References
- [Spec: Give each environment skill one job and a readable verifier (#213)](https://github.com/yahyabedirhan/skills/issues/213): the redesign these entries come from.

## 2026-10-12: Pi's declared settings sit in its sandbox column

- **Status:** accepted
- **Context:** Pi has no sandbox, and its declared settings (models, packages) set none of the five areas.
- **Options:** A sixth column: the setup areas are five, and the glossary defines them.
- **Choice and why:** Check them in the sandbox column, the column Pi has no other use for.
- **Consequences:** The column name fits Pi's settings loosely. Revisit when Pi gets a sandbox.

### References
- [Spec: Give each environment skill one job and a readable verifier (#213)](https://github.com/yahyabedirhan/skills/issues/213): the redesign these entries come from.

## 2026-10-12: plugin names are unique per harness

- **Status:** accepted
- **Context:** The workstation's installs list has two `exa` entries, a Claude Code bundle and a Pi server, and the old checker refused the file.
- **Options:** Unique names per file: it refuses a real setup.
- **Choice and why:** A name may repeat when the entries name different harnesses.
- **Consequences:** None open.

### References
- [Spec: Give each environment skill one job and a readable verifier (#213)](https://github.com/yahyabedirhan/skills/issues/213): the redesign these entries come from.

## 2026-10-12: Claude Code gets no Write(...) entries

- **Status:** accepted
- **Context:** Replaces "write rows also write Write(**/…) entries". In a live check, Claude Code 2.1.296 warned at startup for each `Write(...)` deny in `~/.claude/settings.json`: file permission checks match only `Edit(...)` rules.
- **Options:** Keep the `Write(**/…)` entries for the Cursor CLI: it already gets its own `Write(...)` entries in `cli-config.json`, and the warning shows in every session.
- **Choice and why:** Write rows become `Edit(...)` entries only. An existing `Write(...)` entry is this skill's own outdated wiring, so it is `removed`.
- **Consequences:** The startup warning goes away. The verifier counts a `Write(...)` entry in Claude Code's settings for no personal permission.

## 2026-10-12: opencode's reasoning variant is checked live

- **Status:** accepted
- **Context:** A declared opencode config set `reasoningEffort` `high`, but the TUI ran `medium`. The TUI restores a per-model variant from `~/.local/state/opencode/model.json` and submits it, which beats the config, even `agent.build.variant`.
- **Options:** Have the verifier read or write the TUI state file: it is opencode's runtime state, not config, and it changes whenever the user picks a variant.
- **Choice and why:** Declare `agent.build.variant` beside the model, and name the upstream bug as a gap. The live check reads the variant from the TUI status line. On a mismatch, the variant is switched once in the TUI (ctrl+t), which updates the remembered state.
- **Consequences:** The verifier checks only the config file. The gap closes when upstream fixes the bug.

### References
- [anomalyco/opencode#38363](https://github.com/anomalyco/opencode/issues/38363): the TUI's remembered variant beats the config.
- [anomalyco/opencode#13718](https://github.com/anomalyco/opencode/issues/13718): the same for `agent.build.variant`.
