# Workstation repo

What this skill reads from the user's workstation repo, and the pointer that names the repository and its clone. The workstation repo holds the user's personal agent setup. `/maintain-environment` owns it: its `references/workstation.md` says what the repository is for, and how to start one or change what it holds.

The workstation repo is the source and the machine's files are output: every run rewrites the generated parts of the shared file, and a personal permission's entries in each harness's settings, from the repository.

**When the user has no workstation repo,** set up the machine without one. The personal parts of the shared file are then their own source, and this skill keeps them as they are. Say in the report that `/maintain-environment` can start a workstation repo.

## The pointer

`~/.config/agents/source.md` names `<workstation-repo>` and `<path-to-workstation-repo>` on this machine. This skill needs it to find the repository before it generates anything. It sits outside every repository, so it stays private by being local.

```markdown
# Workstation repo

Where this machine's personal agent setup comes from. Written by set-up-machine.

- Repository: `<workstation-repo>`
- Clone: `<path-to-workstation-repo>`
```

The clone path starts `~/` or `/`. A person with no workstation repo has `- Repository: none` and no `Clone:` line, so the next run doesn't ask again. The pointer's two values are the Tool column of the `workstation-repo` and `path-to-workstation-repo` rows in the shared file, written as the pointer writes them, or `none`.

- **When the pointer is missing:** ask the user once, in Inspect, for `<workstation-repo>` and `<path-to-workstation-repo>`, or whether they have none. The diff writes the pointer as an `added` line, the same as any other file.
- **When the pointer records none and the user names a workstation repo:** the diff rewrites the pointer with both values as an `updated` line.
- **When the clone path doesn't exist:** the diff clones the repository there, as an install command run before any file is written.

## The repository's layout

This skill reads only the `agents/` folder at the repository's root. The rest of the repository is the user's, as `/maintain-environment`'s `references/workstation.md` describes.

### `agents/instructions.md`

The values this skill writes into the shared file, and the person's notes on them:

```markdown
# Personal instructions

## Working agreement

- **<agreement-name>.** <agreement>

## Glossary

- **<term>**: <definition>

## Environment defaults

| Role | Tool | Why |
|---|---|---|
| `<role>` | `<tool>` | <reason> |

### <tool-name> glossary

- **<term>**: <tool-definition>

## Personal workflow

### <topic>

- <rule>
```

- **Working agreement:** how this person and their agents work together, optional, one agreement per line: `<agreement-name>` is a short label, `<agreement>` the agreement itself.
- **Glossary:** the words this person and their agents share, optional: `<term>` is the word, and its `<definition>` holds in any harness.
- **Copying:** Each is copied as it is into the shared file's section of the same name, up to the next `## ` heading. A section that is missing or empty is left out of the shared file.
- **Environment defaults:** one row per role the person fills, named as in the roles table in `global-instructions.md`. `<tool>` is a tool name or the exact command; `<reason>` is why this choice, kept here as a note. Only the Role and Tool columns are read; any other column, such as Why, is notes that stay in the repository. A role left out, or given `none`, is `none` in the shared file. Leave out `workstation-repo` and `path-to-workstation-repo`: the pointer fills them, and `verify.py` fails a row here that differs from it.
- **Tool glossaries:** optional `### <tool-name> glossary` subsections after the table, where `<tool-name>` is the tool's name; each `<tool-definition>` says what the term is in that tool. Everything from the first `### ` heading to the next `## ` heading is copied as it is after the shared file's table. Notes between the table and that heading stay in the repository.
- **Personal workflow:** concise rules for how this person works, each `<rule>` under a `### <topic>` heading, where `<topic>` names a group of rules. Everything under the heading, up to the next `## ` heading, is copied as it is into the shared file's Personal workflow section, including its `###` topic headings. Notes on when and how to use a tool the person added count as workflow lines.
- Any other text in the file is notes, and stays in the repository. Check every copied line against the team test in `global-instructions.md`.

### `agents/harnesses/<harness>.md`

Instructions for one harness only, for what differs between harnesses: a sandbox, a missing ask list, a tool only one harness has. `<harness>` is the harness's reference name: `claude-code`, `codex`, `cursor`, `opencode` or `pi`. Each file is optional.

```markdown
# <Harness> instructions

<notes>

## Instructions

- <instruction>
```

- **Copying:** everything under `## Instructions`, up to the next `## ` heading, is copied as it is into the harness's own instructions file. Other text is notes and stays in the repository. A file with no `## Instructions` section, or an empty one, is a `FAIL`.
- **Where it goes:** only Cursor has a file today, `~/.cursor/rules/harness-instructions.mdc` (cursor.md, *Global instructions*). Claude Code, Codex, opencode and Pi read the shared file through a link, so they have no place for it yet: a source for one of them is a `gap` line.
- Never put a rule every harness needs here; it belongs in `agents/instructions.md`. Check every line against the team test in `global-instructions.md`.

`verify.py` prints a `harness` line per file: `ok` when the generated file matches its source, `FAIL` when it is missing or differs, or when a generated file outlived its source, `n/a` when the harness isn't set up, and `gap` for a harness with no place yet, or a file of the same name the skill didn't write.

### `agents/permissions.json`

The person's own permission rows, such as allowing a tool they added, or refusing a command only they want refused. It has the rule table's format, `{"version": 1, "rules": [<row>, …]}`, and each row the fields and `match` kinds of a rule-table row (SKILL.md, *Rule table*), with one more level:

- **`allow`:** the harness runs a call the row covers without a prompt, and the hook says nothing. On Codex the command also runs outside the sandbox, unreported, since Codex's only decision that skips the prompt is `allow` (`codex.md`). Only a personal permission takes it; the rule table refuses it, since a generic rule never loosens a harness. Its `instruction` says how to go ahead, and its `covers` samples are calls it must allow.
- **`deny`, `ask` and `allow-and-report`** work as in the rule table: the hook refuses a deny row's calls and reports an allow-and-report row's, and the harnesses' native entries ask.

The checks are the rule table's, through `scripts/setupmachine/rules.py`: a malformed row is refused, and so is an id the rule table already uses. A personal permission can't loosen a table row: an `allow` row whose sample a table row denies or asks for fails `verify.py`. No file means no personal permissions.

### `agents/codex.toml`

Keep explicitly chosen Codex CLI defaults in this private file. Use only the top-level keys `sandbox_mode`, `approval_policy` and `approvals_reviewer`; each is optional. A missing file or omitted key declares no preference, so leave that setting user-managed. Removing a declaration leaves its persisted value in place for the user to remove.

Validate the keys and values before proposing any write. Reject unknown keys, nested tables and unsupported values with an explicit gap; this file is an allowlist, not a copy of Codex's whole configuration. Keep credentials, model providers, project trust, profiles, hook state and runtime state in their existing homes. Existing memory and hook ownership remains with this skill's Codex adapter.

Read `codex.md` for installed-version support, preservation and override checks. Mark each declared preference `personal` in the diff. Keep chosen values and this repository's identity and clone path out of public reports, issues, pull requests and fixtures; use synthetic values there.

### `agents/pi.json`

Keep explicitly chosen Pi settings in this private file: a JSON object of top-level keys from Pi's settings reference, such as `defaultProvider`, `defaultModel`, `defaultThinkingLevel` and `enableInstallTelemetry`. Each key is optional. A missing file or omitted key declares no preference, so leave that setting user-managed. Removing a declaration leaves its persisted value in place for the user to remove.

```json
{
  "defaultThinkingLevel": "<level>",
  "enableInstallTelemetry": false
}
```

- Declare only preferences. Leave out runtime state Pi writes itself, such as `deviceId` and `lastChangelogVersion`, and keep credentials, trust decisions and sessions in Pi's own files.
- A file that isn't a JSON object is a `FAIL`, and nothing from it is written.
- Read `pi.md` for the merge into `<agent-dir>/settings.json`, the backup and activation. Mark each declared key `personal` in the diff. Keep chosen values out of public reports, issues, pull requests and fixtures.

`verify.py` prints a `pi` line per declared key: `same` when `settings.json` holds the declared value, `FAIL` when it's missing or differs, and `none` with no file. It never prints the values.

### `agents/installs.json`

What each machine installs beyond the harnesses' configuration: skills, and anything else that needs a command, such as a session host's plugin or integration. With the file, it is the whole list, including the user's own skills repo, so a machine gets nothing it leaves out. Without it, the skill installs `<skills-repo>`.

```json
{
  "skills": [
    { "source": "<skills-repo>" },
    { "source": "<owner>/<app-repo>", "skills": ["<skill>"] }
  ],
  "ignore": ["<skill>"],
  "commands": [
    {
      "name": "<plugin>",
      "target": ["remote"],
      "check": "<check-command>",
      "install": "<install-command>"
    }
  ]
}
```

- **`skills`:** each entry has a `source`, a GitHub `owner/repo`, and an optional `skills` array of skill names in it. Without `skills`, the entry means every skill in the source, including one added to it later.
- **`ignore`:** skill names a machine may have that the list leaves out on purpose, such as an experiment on one machine or a hand-made skill the lock doesn't track. Mark an installed skill on this list `ignored`, not `extra`, and never install, update or remove it, since it is the user's on that machine.
- **`commands`:** each entry has a `name`, a `check` (`<check-command>`) and an `install` (`<install-command>`). Run each as written, as a shell command in the home folder, never wrapped in `sh -c`, since the rule table's `shell-inline-command` row refuses that. Write `check` so it exits 0 only when the thing is installed and current, since the skill runs `install` whenever it fails.
- **`target` and `os`:** optional arrays on any entry. `target` takes `local`, the machine the user sits at, and `remote`, a machine Inspect treats as remote or headless. `os` takes `macos` and `linux`. An entry applies when both match this machine; a field left out matches every machine. An entry that doesn't apply is an `n/a` line naming the field.
- All three arrays are optional. Refuse the file, with a `gap` line and no installs from it, when it isn't valid JSON, an entry has an unknown key or misses a required one, or an `ignore` name is also one a `skills` entry installs, since a guessed entry could install the wrong thing.

Check each entry that applies, then put what's missing in the diff:

- **A skill:** `~/.agents/.skill-lock.json` records each installed skill with its `source`, `skillPath` and `skillFolderHash`, the git tree hash of the skill's folder when it was installed. Read the source's tree in one call, `gh api "repos/<owner>/<repo>/git/trees/HEAD?recursive=1"`; a skill is a folder holding a `SKILL.md`, and its entry's `sha` is the folder's current hash.
  - `added` when a skill the entry names, or any skill in a whole-source entry, has no lock entry from that source. Install it with `npx --yes skills add <owner>/<repo> -g -a codex -y`, adding `-s <skill>` for each named skill, and `-a claude-code` only when `~/.claude/skills` isn't a link to `~/.agents/skills`, since the CLI would link the folder into itself.
  - `updated` when the lock's `skillFolderHash` differs from the folder's `sha` in the tree. Update it with `npx --yes skills update <skill> -g -y`.
  - `present` when the hashes match.
  - When the tree call fails, such as with no `gh` login, name it as a `gap` line and check presence only.
  - **When a skill's name is already installed from another source,** a lock entry with that name and a different `source`, **or two entries in the file both provide it:** mark it `gap`, name both sources, and install nothing for that name. The lock holds one skill per name, so `npx skills add` would silently replace the other source's copy on every machine. The user resolves it by dropping one source, or by naming skills so the two no longer overlap.
  - **When a listed skill's name matches a harness's built-in slash command:** add a `gap` line naming the harness and the command, and still install it. One of the two may hide the other in that harness, which the user should know about, but the skill is theirs to keep.
  - `extra` for an installed skill in the lock that no entry provides and `ignore` doesn't name: kept, for the user to add to the file, add to `ignore` or remove.
- **A command:** `present` when `check` exits 0; otherwise `added`, and Write runs `install`, then `check` again. A `check` that still fails after `install` is a failed install: report it.

Never put a secret in the file: it is a repository, and the commands run as written. A command that needs a credential reads it from where the tool already keeps it.

## Writing the shared file from it

With a workstation repo, the shared file's personal parts are generated from `agents/instructions.md`: the Working agreement, the Glossary, the Tool column of the Environment defaults table except the two rows the pointer fills, the tool glossaries after it, and the Personal workflow section. Each sits in the order `global-instructions.md` gives. The rules block follows `global-instructions.md`'s compact template. The roles' What it is and When none columns still come from this skill's roles table.

- **When the shared file holds a Tool value, or a line of another personal part, that the workstation repo lacks:** add it to the clone's `agents/instructions.md` in the same diff, before the shared file is rewritten, so nothing is lost. In the report, name the file for the user to commit and push in their own repository.
- **When `agents/instructions.md` doesn't exist yet:** the diff creates it from the shared file's current values in the shape above.

`verify.py` checks the result: a `personal` line is `ok` when the shared file carries the repository's values and sections, `none` when the pointer says there is no repository, and `FAIL` when the pointer is missing, a section differs, a `workstation-repo` or `path-to-workstation-repo` row is missing or differs from the pointer, or the shared file has an optional section the repository lacks or lacks one it has.

## Writing the personal permissions

Turn each personal permission into each harness's entries the way that harness's reference turns a rule-table row, written beside the table's entries in the same files. Mark every entry a personal permission produced `personal` in the diff, so the user tells it from the table's and never reads it as `extra`.

- **Only where its tool exists:** a command row applies where one of its programs is on `PATH`; an MCP-tool row in a harness that lists a tool it matches, by the listing that harness's reference gives; a file row in every harness. Elsewhere it's an `n/a` line naming the missing tool, and nothing is written there, since an entry for a tool the harness lacks only adds noise.
- **Rejection guidance:** keep personal permissions' details in the permission file and harness entries. The hook supplies their reasons and alternatives; do not append them to the shared file's compact rules block. Notes on when to use a tool belong in the personal workflow.
- **When the machine holds an `extra` entry that is the person's own choice,** such as an allow for a tool they added by hand: propose it as a personal permission in the clone's `agents/permissions.json` in the same diff, so the next machine gets it too, and name the file in the report for the user to commit there.
- **When a personal permission is removed:** the entries it left behind are `extra`, for the user to remove.

`verify.py` runs each personal permission's samples through the hook with the table's, fails a malformed file, and checks Claude Code's settings: `personal present` names a row's entries, `personal n/a` says which tool Claude Code lacks, `personal gap` is a row with no native entry there, and `personal FAIL` an entry missing. The other harnesses' entries are compared in the diff.
