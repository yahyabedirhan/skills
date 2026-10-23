# Decisions: set-up-project

This page records the decisions behind the [`set-up-project`](../../skills/set-up-project/SKILL.md) skill.
It is for maintaining the skill and is never installed.
Entries follow the shape in [index.md](index.md).
The spec is "Spec: every harness and project is set up and audited from the skills" (#49); the ticket is "set-up-project sets up and audits a project" (#60).

## 2026-09-29: a fork of setup-matt-pocock-skills

- **Status:** accepted
- **Context:** The skill needs a base for the tracker, label and domain setup.
- **Options:** None considered.
- **Choice and why:** Fork `setup-matt-pocock-skills` at `d80fa0f`, the last upstream commit that touches the skill's folder. Sections A to C, the `## Agent skills` block and the tracker, label and domain templates stay close to upstream, so a later upstream change diffs cleanly.
- **Consequences:**
  - The local tracker moves from `.scratch/` to `.efforts/<effort>/`, as the `to-spec` and `to-tickets` forks already do.
  - The GitHub template gains the effort-label and name-by-title lines that `init-effort`'s own copy carried. That copy is gone: `init-effort` now runs set-up-project for a new project.

## 2026-09-29: model-invoked, where upstream is user-invoked

- **Status:** accepted
- **Context:** `to-spec`, `to-tickets` and `init-effort` need to run the skill when no tracker is configured, and rollout issues ask an agent to run it on each project.
- **Options:** Stay user-invoked, as upstream: other skills couldn't load it.
- **Choice and why:** Make it model-invoked.
- **Consequences:** None.

## 2026-09-29: AGENTS.md is always the rules file, and CLAUDE.md holds @AGENTS.md

- **Status:** replaced by [2026-10-01: CLAUDE.md is the import line or a symlink to AGENTS.md](#2026-10-01-claudemd-is-the-import-line-or-a-symlink-to-agentsmd)
- **Context:** Upstream edits whichever of the two files exists. Codex, opencode and Cursor read `AGENTS.md`. Claude Code skips it when a `CLAUDE.md` exists.
- **Options:** Edit whichever file exists, as upstream: the harnesses would read different text.
- **Choice and why:** `AGENTS.md` is the rules file, and `CLAUDE.md` holds `@AGENTS.md`. The import line makes one text reach every harness.
- **Consequences:** A lone `CLAUDE.md` moves into `AGENTS.md`. A `CLAUDE.md` beside an existing `AGENTS.md` gets the import added, and its other lines are listed for the agent to move, since merging two files needs judgement.

## 2026-09-29: a script for the deterministic part, prompts for the rest

- **Status:** replaced by [2026-09-30: the agent does what set_up_project.py did](#2026-09-30-the-agent-does-what-set_up_projectpy-did)
- **Context:** Part of the setup is the same on every project.
- **Options:** None considered.
- **Choice and why:** `set_up_project.py plan|apply` checks the machine, writes `AGENTS.md`'s skeleton, `CLAUDE.md` and the `.gitignore` lines on one approval, and audits. Apply takes the plan id, as set-up-machine's does. The tracker, labels and docs stay upstream's explore-present-confirm flow, reported by the plan as `todo` until written.
- **Consequences:** "No changes." means the whole setup is in place.

## 2026-09-29: the machine check runs set-up-machine's own reconcile

- **Status:** replaced by [2026-09-30: the machine check is set-up-machine's verify.py](#2026-09-30-the-machine-check-is-set-up-machines-verifypy)
- **Context:** The project audit must judge rules the same way the machine does.
- **Options:** A second copy of what each rule covers: it would drift.
- **Choice and why:** The script imports `setupmachine` from `<skills>/set-up-machine/scripts` (`--machine-skill` overrides it). The audit reads the same `rules.json` and the same adapter expansions (`opencode.entries_for`, `effective`, `command_prefixes`) as the machine.
- **Consequences:** When the machine differs, the plan prints set-up-machine's plan and its apply command and exits 3. The agent takes one approval for it. set-up-project never applies the machine by itself.

## 2026-09-29: the audit judges each harness by how it merges project files

- **Status:** accepted
- **Context:** Each harness merges project files over global ones in its own way, as section 5 of each harness's research describes.
- **Options:** None considered.
- **Choice and why:** Judge each harness by its own merge:
  - opencode: the project config is merged over the global one exactly as opencode does. A key already there keeps its place, and a new key goes last. Each rule's samples are evaluated before and after; a looser result is `weakens`.
  - Cursor CLI: a project `deny` list that drops any global entry is `weakens`. An allow over an ask row is `weakens`, since there is no ask level. An allow over a deny row is `overlaps`.
  - Claude Code: permissions can't be loosened. An allow over a deny command row is `weakens` only when the user settings lack `classifyAllShell`, since auto mode's classifier would be skipped; else it is `overlaps`. The Cursor CLI reads the project's `.claude/settings.json` too, so an allow there over an ask row is `weakens`. `disableAllHooks`, `autoMemoryEnabled: true` and `disableAutoMode` are `weakens`.
  - Codex: rules can't be loosened. `[features] hooks = false` and `memories = true` are `weakens`.
- **Consequences:** The Claude Code case with the auto-mode guard off changed in [2026-09-30: with the auto-mode guard off, an allow over a deny row is overlaps](#2026-09-30-with-the-auto-mode-guard-off-an-allow-over-a-deny-row-is-overlaps).

## 2026-09-29: overlaps doesn't fail the audit, weakens does

- **Status:** accepted
- **Context:** A project allow that covers a rail's command is against allow-only. Where the rail still holds everywhere, it is a tidy-up, not a hole.
- **Options:** None considered.
- **Choice and why:** `weakens` fails the audit and `overlaps` doesn't. Exit code 2 marks a failed audit.
- **Consequences:** A script or a rollout issue can tell a failed audit from the exit code.

## 2026-09-29: the audit never edits a project's harness files

- **Status:** accepted
- **Context:** A project's harness files belong to the project.
- **Options:** None considered.
- **Choice and why:** The audit names each entry and the fix. The agent changes one only on the user's approval.
- **Consequences:** A project deny or ask is `extra`, kept, and a candidate for the rule table.

## 2026-09-29: a project may hold its own Defaults table

- **Status:** accepted
- **Context:** A project may require a tool for a role that differs from the global one.
- **Options:** None considered.
- **Choice and why:** A project's `## Defaults` table overrides the global rows it names, for that project. The template allows it.
- **Consequences:** Section D proposes a row only when the project itself requires a tool for a role.

## 2026-09-30: the agent does what set_up_project.py did

- **Status:** accepted
- **Context:** This replaces [2026-09-29: a script for the deterministic part, prompts for the rest](#2026-09-29-a-script-for-the-deterministic-part-prompts-for-the-rest) (#81).
- **Options:** None considered.
- **Choice and why:** Drop the script. `AGENTS.md`, `CLAUDE.md`'s single import and the `.gitignore` lines join the one draft the user approves. The audit is the agent reading each project harness file against `references/project-files.md`.
- **Consequences:** No script to maintain.

## 2026-09-30: the machine check is set-up-machine's verify.py

- **Status:** accepted
- **Context:** This replaces [2026-09-29: the machine check runs set-up-machine's own reconcile](#2026-09-29-the-machine-check-runs-set-up-machines-own-reconcile) (#81).
- **Options:** None considered.
- **Choice and why:** Run `verify.py`. It is fast and writes nothing. When a line fails, the agent runs set-up-machine first.
- **Consequences:** The full set-up-machine audit stays that skill's job.

## 2026-09-30: the audit matches project entries against samples.covers

- **Status:** accepted
- **Context:** Without the script, the audit no longer has the spellings the adapters generated (#81).
- **Options:** None considered.
- **Choice and why:** Match project entries against each row's `samples.covers`, the same samples verify checks.
- **Consequences:** None.

## 2026-09-30: the audit checks every harness's project files

- **Status:** accepted
- **Context:** A teammate may use a harness this machine doesn't have (#81).
- **Options:** Check only the harnesses set up on this machine: it misses a teammate's.
- **Choice and why:** Check every harness's project files, whether or not that harness is set up here.
- **Consequences:** None.

## 2026-09-30: with the auto-mode guard off, an allow over a deny row is overlaps

- **Status:** accepted
- **Context:** This changes the Claude Code case of [2026-09-29: the audit judges each harness by how it merges project files](#2026-09-29-the-audit-judges-each-harness-by-how-it-merges-project-files) (#81).
- **Options:** None considered.
- **Choice and why:** A project allow over a deny command row is `overlaps`. The user deny still wins, and there is no classifier to route around.
- **Consequences:** None.

## 2026-10-01: create the effort label before the first issue that uses it

- **Status:** accepted
- **Context:** The GitHub template told skills to pass `effort:<effort>` to `gh issue create`, and that command fails when the label is missing.
- **Options:** None considered.
- **Choice and why:** The publish section lists labels and runs `gh label create` only when that exact name is absent. `--limit 1000` is there because `gh label list` pages, and a short page can hide a label that already exists.
- **Consequences:** None.

## 2026-10-01: a machine check passes on exit code 0

- **Status:** accepted
- **Context:** `verify.py` prints `codex differs` for rows Codex can't express, and still exits 0 with `rules ok`. "If any line fails" sent agents to set up the machine on a healthy check.
- **Options:** None considered.
- **Choice and why:** A pass is the `rules` line saying `ok` and no `hook` line saying `FAIL`.
- **Consequences:** None.

## 2026-10-01: CLAUDE.md is the import line or a symlink to AGENTS.md

- **Status:** accepted
- **Context:** This replaces [2026-09-29: AGENTS.md is always the rules file, and CLAUDE.md holds @AGENTS.md](#2026-09-29-agentsmd-is-always-the-rules-file-and-claudemd-holds-agentsmd). The intro said `CLAUDE.md` holds only `@AGENTS.md`, while the write step already accepted a symlink.
- **Options:** None considered.
- **Choice and why:** Accept both forms. Both give Claude Code the same text, since it skips `AGENTS.md` when `CLAUDE.md` exists.
- **Consequences:** The intro, the draft and the `AGENTS.md` seed now say the same thing.

## 2026-10-12: the machine check depends only on the verifier's exit code

- **Status:** accepted
- **Context:** Step 1 explained Codex line names (`differs`, `same`, `stricter`, `skipped`), so it broke whenever set-up-machine's output changed.
- **Options:** None considered.
- **Choice and why:** A pass is exit code 0 from set-up-machine's verifier; otherwise run set-up-machine first.
- **Consequences:** set-up-machine can change what it prints without an edit here.

## 2026-10-23: each project's release lifecycle lives in its own docs/agents/releasing.md

- **Status:** accepted
- **Context:** Versions fell behind across a user's projects: one reached its registry with no tag and no GitHub release. The release steps lived outside each project, so its team couldn't see them.
- **Options:** None considered.
- **Choice and why:** Releases work the way issue tracking does. set-up-project writes `docs/agents/releasing.md` from a seed template, so each project's team sees how it releases. The parts every project of the user shares live once, in `setup/releasing.md` of the workstation repo the pointer names, and the skill starts each project's page from them. The audit reports a project that releases without a page, and a page that disagrees with the shared rules.
- **Consequences:**
  - A project gets its page on its next set-up-project run.
  - set-up-project reads the workstation repo for the first time, and only that one file. Without a pointer or the file, the seed template alone is the start.
  - settle-effort follows the page after merging a version bump.

### References
- [Spec: Give each environment skill one job and a readable verifier (#213)](https://github.com/yahyabedirhan/skills/issues/213): the redesign these entries come from.

## 2026-10-23: release pages stay short

- **Status:** accepted
- **Context:** The first release pages restated the shared release rules, and added commands, formatting details and plans for registries a project didn't use. The maintainer found them too comprehensive, and trimmed two of them by hand.
- **Options:** None considered.
- **Choice and why:** The maintainer decided that release pages stay short. The seed holds three sections: what a release ships, the release order in a line or two per step, and the roles. Everything the shared release rules already say stays there, and the page holds only what the project does.
- **Consequences:**
  - A new release page starts short. An existing long page stays until someone trims it, because the audit checks a page against the shared rules, not its length.
  - Without shared release rules, the seed's one-line version rule in step 1 is the only version rule a page gets.
