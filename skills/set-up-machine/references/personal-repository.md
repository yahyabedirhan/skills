# Personal repository

Where a person's own setup lives, and the pointer that finds it.

A person keeps their personal setup in a repository of their own, which can be private: which tool fills each role, their personal workflow lines, and their personal permissions. That repository is the source and the machine's files are output, so make a personal change there and run this skill again; never edit the generated parts of the shared file, or a personal row's entries in a harness's settings, by hand, since the next run rewrites them. A machine with no personal repository works as before: the user's Tool values and workflow lines stay where they are in the shared file.

## The pointer

`~/.config/agents/source.md` names the personal repository and where it is cloned on this machine. It sits outside every repository, so it stays private by being local.

```markdown
# Personal repository

Where this machine's personal agent setup comes from. Written by set-up-machine.

- Repository: `<owner>/<repo>`
- Clone: `<path to the clone>`
```

The clone path starts `~/` or `/`. A person with no personal repository has `- Repository: none` and no `Clone:` line, so the next run doesn't ask again.

- **When the pointer is missing:** ask the user once, in Inspect, which repository holds their personal setup and where it is cloned, or whether they have none. The diff writes the pointer as an `added` line, the same as any other file.
- **When the clone path doesn't exist:** the diff clones the repository there, as an install command run before any file is written.

## The repository's layout

Both files sit in an `agents/` folder at the repository's root, so the rest of the repository stays free for whatever else the person keeps there.

### `agents/instructions.md`

The values this skill writes into the shared file, and the person's notes on them:

```markdown
# Personal instructions

## Environment defaults

| Role | Tool | Why |
|---|---|---|
| `<role>` | `<tool name or exact command>` | <why this choice, kept here> |

## Personal workflow

- <one rule for how this person works>
```

- **Environment defaults:** one row per role the person fills, named as in the roles table in `global-instructions.md`. Only the Role and Tool columns are read; any other column, such as Why, is notes that stay in the repository. A role left out, or given `none`, is `none` in the shared file.
- **Personal workflow:** everything under the heading, up to the next `## ` heading, is copied as it is into the shared file's Personal workflow section, below its fixed intro line. Notes on when and how to use a tool the person added count as workflow lines. A line still has to pass the team test that `global-instructions.md` describes.
- Any other text in the file is notes, and stays in the repository.

### `agents/permissions.json`

The person's own permission rows, such as allowing a tool they added, or refusing a command only they want refused. It has the rule table's format, `{"version": 1, "rules": [<row>, …]}`, and each row the fields and `match` kinds of a rule-table row (SKILL.md, *Rule table*), with one more level:

- **`allow`:** the harness runs a call the row covers without a prompt, and the hook says nothing. On Codex the command also runs outside the sandbox, unreported, since Codex's only decision that skips the prompt is `allow` (`codex.md`). Only a personal row takes it; the rule table refuses it, since a generic rule never loosens a harness. Its `instruction` says how to go ahead, and its `covers` samples are calls it must allow.
- **`deny`, `ask` and `allow-and-report`** work as in the rule table: the hook refuses a deny row's calls and reports an allow-and-report row's, and the harnesses' native entries ask.

The checks are the rule table's, through `scripts/setupmachine/rules.py`: a malformed row is refused, and so is an id the rule table already uses. A personal row can't loosen a table row: an `allow` row whose sample a table row denies or asks for fails `verify.py`. No file means no personal rows.

## Writing the shared file from it

With a personal repository, the Tool column of the shared file's Environment defaults table and its Personal workflow section are generated from `agents/instructions.md`, the way the rules block is generated from the rule table. The roles' What it is and When none columns still come from this skill's roles table.

- **When the shared file holds a Tool value or workflow line the personal repository lacks:** add it to the clone's `agents/instructions.md` in the same diff, before the shared file is rewritten, so nothing is lost. In the report, name the file for the user to commit and push in their own repository.
- **When `agents/instructions.md` doesn't exist yet:** the diff creates it from the shared file's current values in the shape above.

`verify.py` checks the result: a `personal` line is `ok` when the shared file carries the repository's values, `none` when the pointer says there is no repository, and `FAIL` when the pointer is missing or anything differs.

## Writing the personal rows

Turn each personal row into each harness's entries the way that harness's reference turns a rule-table row, written beside the table's entries in the same files. Mark every entry a personal row produced `personal` in the diff, so the user tells it from the table's and never reads it as `extra`.

- **Only where its tool exists:** a command row applies where one of its programs is on `PATH`; an MCP-tool row in a harness that lists a tool it matches, by the listing that harness's reference gives; a file row in every harness. Elsewhere it's an `n/a` line naming the missing tool, and nothing is written there, since an entry for a tool the harness lacks only adds noise.
- **Rule lines:** a personal `deny`, `ask` or `allow-and-report` row gets its line in the shared file's generated block, after the table's and in the same form, so the agent reads its instruction. An `allow` row gets none: it asks nothing of the agent, and notes on when to use the tool belong in the personal workflow.
- **When the machine holds an `extra` entry that is the person's own choice,** such as an allow for a tool they added by hand: propose it as a personal row in the clone's `agents/permissions.json` in the same diff, so the next machine gets it too, and name the file in the report for the user to commit there.
- **When a personal row is removed:** the entries it left behind are `extra`, for the user to remove.

`verify.py` runs each personal row's samples through the hook with the table's, fails a malformed file, and checks Claude Code's settings: `personal present` names a row's entries, `personal n/a` says which tool Claude Code lacks, `personal gap` is a row with no native entry there, and `personal FAIL` an entry missing. The other harnesses' entries are compared in the diff.
