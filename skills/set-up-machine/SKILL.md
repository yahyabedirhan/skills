---
name: set-up-machine
description: Set up or audit a machine's coding-agent harnesses from one rule table and the user's workstation repo - the shared global instructions every harness reads, the global rules (deny, ask, allow-and-report) each one enforces, the pre-tool hook, memory kept off, each harness's declared config such as its default model, the plugins each harness gets, and the skills and tools the workstation repo lists to install. Use for a new machine or VPS, to audit this machine's agent setup, or when another skill says to check the machine.
---

# Set up machine

Set up every selected harness (Claude Code, Codex, opencode, Cursor's CLI, desktop app and cloud agents, Pi, Grok Bot) from its sources. Install or update each selected tool to the latest available version. Running the skill again is the **audit**: check configuration and freshness, then propose any required updates.

## Sources

- **Rule table**, [`rules.json`](rules.json).
- **Workstation repo**, `<workstation-repo>`, found through the **pointer**, `~/.config/agents/source.md`, which names the repository and its clone. Each of these files is optional:
  - `setup/instructions.md`: the working agreement, the glossaries, which tool fills each role, and the personal workflow;
  - `setup/permissions.json`: the **personal permissions**, rows each harness carries beside the rule table's;
  - `setup/installs.json`: the skills, plugins and commands every machine gets;
  - `setup/harnesses.json`: where each harness's instructions and declared config are. Every harness can have a declared config, such as its default model.

## Outputs

- **Shared global instructions file**, `~/.config/agents/AGENTS.md`, which every harness reads; its personal parts come from `setup/instructions.md`.
- **Harness instructions**, for a harness whose `instructions` file `setup/harnesses.json` names: today Cursor's `~/.cursor/rules/harness-instructions.mdc` (references/workstation.md).
- Each harness's permission entries, from the rule table and the personal permissions.
- The **pre-tool hook**, `scripts/pre_tool_hook.py`, run before every tool call.
- The **pointer**, when it is missing or records none.
- Each harness's **declared config**, from the `config` file `setup/harnesses.json` names for it: only the keys that file sets are merged into the harness's own config file (references/workstation.md, *A declared config*), and every other key stays the user's.
- The skills and commands `setup/installs.json` lists for this machine, and its **plugins** in each harness it names: the plugins setup area, a plugin bundle or a standalone MCP server per entry.
- Memory off in every harness.

## Rules for every run

- Reproduce installation choices, configuration and steps, not a snapshot of software versions. Use the latest stable release, or the latest default branch for repository-distributed code. Apply this to harnesses, skills, plugins, packages and command-line tools.
- Record installed versions and source commits as audit evidence, not future installation targets. Keep historical citations and dependency lockfiles separate from machine setup choices.
- Check the current upstream source before calling an installation up to date. A matching declaration or an existing executable proves presence only. Report unavailable freshness checks as `gap`.
- Keep every entry the rule table didn't produce, as it is: it's the user's.
- Harness formats change: check the docs a harness reference links before writing. Where they differ, follow the docs and name the difference in your report.

## Parameters

- `<skills-repo>`: the user's own skills repo on GitHub, as `owner/repo`. Installed only when the workstation repo has no `setup/installs.json`.
- `<workstation-repo>`: the user's own repo for their personal agent setup, usually private, as `owner/repo`.
- `<path-to-workstation-repo>`: where that repo is cloned, e.g. `~/code/agent-setup`.
- `<session-host>`: where agent sessions run, such as `herdr`. The live check starts a session of each harness there.

## Steps

1. **Inspect.** Find each selected harness and tool, compare its installed version with the latest source, and read its current documentation. Preserve its installation channel. Read each harness reference, then the non-secret configuration fields it needs. Leave credentials, authentication stores and runtime state unread. Read the shared file and the pointer too, and when the pointer names a workstation repo, read `references/workstation.md` and the repository's `setup/instructions.md`, `setup/permissions.json`, `setup/installs.json` and `setup/harnesses.json` in `<path-to-workstation-repo>`, then each file `setup/harnesses.json` points at. Inspect each harness's optional `config` as its reference directs. For Codex, use one resolved config home throughout setup and verification; for Pi, one resolved agent folder.
   - **When the pointer is missing:** read `references/workstation.md`, then ask the user once for `<workstation-repo>` and `<path-to-workstation-repo>`, or whether they have none. The diff writes the pointer, recording "none" too, so the next run doesn't ask.
   - **When the pointer records no workstation repo:** set up the machine as `references/workstation.md` says for a run without one, or, when the user names one now, as it says for rewriting the pointer.
   - **When the machine is remote or headless, such as a VPS:** read `references/remote-machine.md` first.
   - **When the harness is Grok Bot:** its instructions go into memory, not files. Follow references/grok-bot/desktop.md, *Instructions*, for apply, reconcile and audit.
   - **When trying a change without touching the real machine:** run the steps against a copy of the home folder in the project's `.scratch/`, and check it with `verify.py --home <copy>`. Start no harness there, since it would read the real login.
2. **Propose one diff** that brings each harness in line with the rule table, the shared file's shape and personal parts, the pointer, memory off, the hook wired, each harness's declared config, and the installs: every skill and command `setup/installs.json` lists for this machine, each selected installation up to date. Include harness upgrades and plugin updates, not only missing installs. Give every harness found its own section, listing each gap its reference names and the hook's blind spots. Read `references/global-instructions.md` whenever a global instructions file is in the diff.

   Work out what each harness should hold, from `rules.json`, the personal permissions, the shared file's shape and the harness's reference, and compare it with what the machine holds. Write the whole diff: per harness and file, the exact entries or a unified diff, each line marked:

   - `added`, `tightened` (a stricter entry added where it wins), `removed`, `updated` (an installed harness, skill, plugin or tool behind its latest source);
   - `present`, `wired` (the hook), `found` (the MCP tools a row matched);
   - `stricter` (the machine is stricter than the table: kept), `extra` (neither the table's nor a personal permission's: kept), `ignored` (an installed skill `setup/installs.json` leaves out on purpose: kept, never installed or removed), `gap` (what the harness can't express), `none` (no such feature);
   - `personal` beside the mark of every entry a personal permission produced (`added, personal`; `present, personal`), so the user can tell those entries from the table's and never reads them as `extra`;
   - `n/a` (not applicable) for a personal permission whose tool this harness lacks, with why: nothing is written for it there.

   Use `removed` only for memory files, a harness's own global file whose every line is already in the shared file (it becomes a link), and this skill's own wiring that points at an old script. An entry a dropped row, the table's or a personal one, left behind is `extra`, for the user to remove.
   - **When the workstation repo has `setup/installs.json`:** the diff holds a line per entry that applies to this machine, and an `n/a` line, with why, per entry that doesn't. The file is the whole list: install nothing it leaves out. `references/workstation.md` gives the format, the checks and the commands.
   - **Without the file, with a `<skills-repo>` value:** the diff installs that repo's skills globally: `npx --yes skills add <owner>/<repo> -g -a codex -a claude-code -y`, leaving out `-a claude-code` when `~/.claude/skills` is a link to `~/.agents/skills`. Compare the installed skill hashes with the source's latest default branch, as `references/workstation.md` describes. Presence in the lock file alone does not prove freshness. With no value, it's a `none` line.
3. **Ask once** for one approval of the whole diff. A change after that needs a new approval.
   - **When the diff holds only `added` and `updated` installs from `setup/installs.json`:** write it without asking, since the user approved that list by writing it.
4. **Back up** every file the diff changes or removes. Before writing any file, copy each one into `~/.config/agents/backups/<UTC time as YYYYmmddTHHMMSSZ>/`, at its path relative to the home folder (`.claude/settings.json`). Copy a symlink as a link.
5. **Write** exactly the approved diff. Run any install command first, such as a skill the diff installs. If one fails, stop subsequent writes and report what changed before the failure. Check configuration and guardrail compatibility after upgrades; report failures rather than making an old snapshot the desired state. In JSON and TOML files, change only the keys the diff names and keep the rest. Write through a symlink to its target.
6. **Verify** with `python3 <skill-folder>/scripts/verify.py`, where `<skill-folder>` is this skill's installed folder. It needs Python 3.9+ and the standard library only, and it writes nothing. The run passes when [What verify must show](#what-verify-must-show) holds. Then inspect again until the diff changes nothing: no pending `added`, `updated`, `tightened` or `removed` line. Report the backup folder, what's wired, the gaps, and the stricter and extra entries.

   The verifier checks persisted configuration, not upstream releases. Complete the freshness checks from Inspect before you report that every installation is the latest.

7. **Live check** each harness, as [references/live-check.md](references/live-check.md) says. Start a real session of each harness in `<session-host>`, with its default model, give each the same probe in a throwaway folder, and read the disk and the screen. The verifier proves the files; the live check proves each harness acts on them. Fix each `FAIL` through steps 2 to 6, then check that harness again. The run is done when the verifier and the live check both pass.
   - **When `<session-host>` can't start a session of a harness:** name that harness's live check as a `gap`.

## What verify must show

Two global lines, then one table, then one detail line per `FAIL` and `gap` cell:

```text
setup  ok    <owner>/<repo>: the shared file matches setup/instructions.md
rules  ok    38 rows and 2 personal permissions, 197 samples

harness      instructions  guardrails    sandbox       plugins       skills        config
Claude Code  ok            ok            n/a           ok            ok            ok
Cursor       FAIL          ok            ok            ok            ok            ok

FAIL  Cursor instructions: ~/.cursor/rules/global-instructions.mdc is stale; generate it again
```

- **`setup`:** the pointer and every `setup/` file are readable, and the shared file carries what `setup/instructions.md` generates. `n/a` when the pointer says there is no workstation repo.
- **`rules`:** every sample of every rule-table row and personal permission gets its row's answer from the hook.
- **A row per harness present.** Each cell is `ok`, `FAIL`, `gap` (the harness can't do it, or the check can't see it) or `n/a` (the area doesn't apply). The columns:
  - `instructions`: the harness reads the shared file, its own instructions from `setup/harnesses.json` when named, and memory is off;
  - `guardrails`: the hook is wired to an installed script, and each personal permission has its native entry where the harness has native rules;
  - `sandbox`: the harness's sandbox and approval settings: Cursor's run mode, and the sandbox and approval keys of the declared Codex config;
  - `plugins`: each `setup/installs.json` plugin for this harness is installed and enabled;
  - `skills`: each skill `setup/installs.json` lists is in a folder this harness reads skills from;
  - `config`: each key the harness's declared config sets has the same value in the harness's config file; `n/a` without a declared config. It isn't a setup area: a default model is none of the five.

The run passes when no line or cell is `FAIL`; the verifier then exits 0. Report each `gap` line. Each harness reference's *Checking it* section says what its row checks.

## Rule table

`rules.json` holds each global rule once, by meaning, not in any harness's form. Each field of a row, each `match` kind, and the spellings are in [references/rule-table.md](references/rule-table.md). Each harness reference turns a row into that harness's entries. The hook and `verify.py` read the same rows through `scripts/setupmachine/rules.py`, which refuses a malformed row. A workstation repo's `setup/permissions.json` holds personal permissions in the same format, which every harness, the hook and `verify.py` take beside the table's (`references/workstation.md`).

## Pre-tool hook

`scripts/pre_tool_hook.py` (Python 3.9+, standard library only) is the hook every harness runs before each tool call. It reads `rules.json`, and the personal permissions through the pointer, and checks the call:

- **deny** rows: it reads a command the way the shell runs it, and checks file tools, redirects and MCP tools too. It refuses the call, naming each refused part with its rule's reason and instruction.
- **allow-and-report** rows: it writes one JSON line per call to `<report-folder>/<date>.jsonl`, readable by the user alone; the harness's permissions decide.
- **ask** rows: the harness's native ask entries do the asking. A row with `approver: "user"` is refused instead where the call shows that no one will ask the user: Claude Code in `auto`, `dontAsk` or `bypassPermissions` mode, Codex with approval policy `never`, and every call under Cursor and opencode, which can't promise a prompt (their references say why). Cursor has no ask list at all, so there the hook refuses every ask row, `approver` or not. Pi has no ask list either, but its extension can ask: with a UI, the hook names the ask rows and the extension asks the user in Pi's dialog; without one, the hook refuses every ask row (references/pi/cli.md).
- **allow** rows: it says nothing; the harness's native allow entries let the call run without a prompt.

A malformed personal file leaves the table's rows in force: the hook skips the personal permissions and `verify.py` reports the file.

### Wiring

Each harness reference shows its wiring with `<script>` in place of the script's path. Replace it with the absolute path of `scripts/pre_tool_hook.py` in the installed skill (under `~/.agents/skills` or `~/.claude/skills`), never in a checkout or worktree, which can be deleted. If there is no installed copy, name the gap. `verify.py` fails wiring whose script is elsewhere.

The wiring fails open (`[ -f <script> ] && … || true`, or the form a harness reference gives): if the script is gone, each call goes on under the native entries. Without it, `python3` would exit 2 on the missing script, which blocks every call. Pi is the exception: it has no native entries underneath, so its extension fails closed and refuses each call the hook can't check (references/pi/cli.md).

`<report-folder>` is `~/.local/state/agents/reports`, or `report_dir` in `~/.config/agents/hook.json`.

### What it can't see

Name these once in every audit:

- a command inside a script file or another interpreter (`python -c`);
- a command built from variables (`$cmd -rf x`);
- an alias or function defined elsewhere;
- an abbreviated long option (`--recur`);
- a force push by refspec (`git push origin +main`);
- a glob the shell expands (`cat .env*`);
- an automatic reviewer, such as Codex's `auto_review`, answering an `approver: "user"` row, since the call's payload doesn't show the reviewer;
- each row's own `gap`.

## References

- [references/global-instructions.md](references/global-instructions.md): the shared file's shape, the roles table, the working agreement and glossaries, what counts as personal workflow, moving a harness's own file, and why memory stays off.
- [references/rule-table.md](references/rule-table.md): a row's fields, its `match` kinds, and the spellings a harness needs.
- [references/workstation.md](references/workstation.md): what this skill reads from the workstation repo: the pointer, the `setup/` files, the files `setup/harnesses.json` points at, and their format, generating the shared file's personal parts and the personal permissions from them, the installs list, and the run without one.
- [references/live-check.md](references/live-check.md): starting a real session of each harness, the probe, and reading what it did.
- [references/remote-machine.md](references/remote-machine.md): running agents on any remote or headless machine: signing in without a browser, per-machine settings, keeping sessions alive, and containing a misled agent.
  - [references/new-remote-machine.md](references/new-remote-machine.md): for a brand-new machine, first: the base it needs, done with the user as root, from key access, the dedicated user, keys-only SSH, the firewall, updates, swap and the docker group to the session host's integration, git credentials, `PATH` over SSH and a headless browser.
- One folder per harness, `references/<harness>/`, with one page per environment, `<env>.md`, read for each environment found. A harness with more than one environment also has an `index.md` for what its environments share. Each page has the same headings: Found, Instructions, Guardrails, Sandbox, Plugins, Skills, Config, Hook wiring, Gaps, Checking it, and leaves out what the shared page already covers. Which harnesses and environments there are, and the rule for the split, are the workstation repo's, in its `harnesses/index.md`. Claude Code and Codex are still one page each, `references/<harness>.md`, until they move to this layout.
  - [references/claude-code.md](references/claude-code.md): Claude Code.
  - [references/codex.md](references/codex.md): Codex. Its *Codex MCP* section holds the TOML and OAuth detail.
  - [references/cursor/](references/cursor/index.md): Cursor. What the CLI and the desktop app share, then [cli.md](references/cursor/cli.md), [desktop.md](references/cursor/desktop.md) and [cloud.md](references/cursor/cloud.md), a cloud agent found on its VM.
  - [references/opencode/cli.md](references/opencode/cli.md): opencode.
  - [references/pi/cli.md](references/pi/cli.md): Pi, whose only enforcement is the hook's extension.
  - [references/grok-bot/desktop.md](references/grok-bot/desktop.md): Grok Bot, whose instructions live in memory and whose permissions, connectors, secrets and routines live in the app.

## Scripts

- [scripts/pre_tool_hook.py](scripts/pre_tool_hook.py): the pre-tool hook every harness calls before each tool call.
- [scripts/verify.py](scripts/verify.py): the check above. It writes nothing. `--home <folder>` checks a copy of a home folder, where a harness is found by its folder only, not by a CLI on `PATH`. `--grok-bot-rules` prints the rule table and personal permissions as Grok Bot's Auto-review rules (references/grok-bot/desktop.md). `--harness <harness> [--env <env>]` keeps one harness's rows, or one environment's, such as `--harness cursor --env cloud`. `--codex-trust-hash '<command>'` prints the `trusted_hash` Codex needs for a hook command (references/codex.md).
- `scripts/setupmachine/`: the modules both scripts use. `harnesses/__init__.py` lists every environment in `ALL`. A harness is a package, `harnesses/<harness>/`, with one module per environment and the shared code in its `__init__.py`; Claude Code and Codex are still one module each.
- [references/opencode/opencode-plugin.js](references/opencode/opencode-plugin.js): the opencode plugin that calls the hook.
- [references/pi/pi-extension.ts](references/pi/pi-extension.ts): the Pi extension that calls the hook and asks the user for ask rows.
