# Personal repository

Where a person's own setup lives, and the pointer that finds it.

A person keeps their personal setup in a repository of their own, which can be private: which tool fills each role, their personal workflow lines, and their personal permissions. That repository is the source and the machine's files are output, so make a personal change there and run this skill again; never edit the generated parts of the shared file by hand, since the next run rewrites them. A machine with no personal repository works as before: the user's Tool values and workflow lines stay where they are in the shared file.

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

The person's own permission rows, such as allowing a tool they added. This is its place only: its format isn't settled yet, so leave the file alone and write no entries from it.

## Writing the shared file from it

With a personal repository, the Tool column of the shared file's Environment defaults table and its Personal workflow section are generated from `agents/instructions.md`, the way the rules block is generated from the rule table. The roles' What it is and When none columns still come from this skill's roles table.

- **When the shared file holds a Tool value or workflow line the personal repository lacks:** add it to the clone's `agents/instructions.md` in the same diff, before the shared file is rewritten, so nothing is lost. In the report, name the file for the user to commit and push in their own repository.
- **When `agents/instructions.md` doesn't exist yet:** the diff creates it from the shared file's current values in the shape above.

`verify.py` checks the result: a `personal` line is `ok` when the shared file carries the repository's values, `none` when the pointer says there is no repository, and `FAIL` when the pointer is missing or anything differs.
