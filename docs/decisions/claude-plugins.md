# Decisions: Claude Code plugins

This page records how the skills in this repo are published as Claude Code plugins, from `.claude-plugin/marketplace.json`.
This file is for maintaining the marketplace and is never installed.
The marketplace was created for the Wispr Flow dictionary skill, its first plugin, and the decision to publish it as a plugin sits in that skill's decisions: `wispr-flow-dictionary.md` > '2026-09-28: also a Claude Code plugin, from a marketplace in this repo'.
Entries follow the shape in [index.md](index.md).

The entries below come from [#34](https://github.com/yahyabedirhan/skills/issues/34).
They were checked against Claude Code 2.1.286 and its docs: the [plugins reference](https://code.claude.com/docs/en/plugins-reference), the [marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference), [host a marketplace](https://code.claude.com/docs/en/plugins/host-marketplace) and [skills](https://code.claude.com/docs/en/skills).

## 2026-10-01: one plugin per skill, or one per family when skills name each other

- **Status:** accepted
- **Context:** The marketplace needs a rule for how skills are grouped into plugins.
- **Options:**
  - One plugin per skill everywhere: the effort workflow's skills hand off to each other by name, so their pointers would dangle.
  - Put a skill in more than one plugin: a skill in two installed plugins loads twice.
- **Choice and why:** One plugin per skill, unless the skills name each other; then one plugin per family. The effort workflow ships as one plugin, `effort-workflow`. `show-me`, `low-level-design`, `system-design`, `email` and `wispr-flow-dictionary` stand alone, so each is its own plugin and a user takes only what they want. A skill is in one plugin only.
- **Consequences:** A new skill that names another skill joins that skill's family plugin.

## 2026-10-01: a family plugin is rooted at skills/ and lists its folders

- **Status:** accepted
- **Context:** A family plugin must load only its own skills.
- **Options:** A source of `./`: a `skills` key adds to the default `skills/` scan instead of replacing it, so it would load every skill in the repo. This was tested with `--plugin-dir`.
- **Choice and why:** The entry has `"source": "./skills"` and a `skills` array of `./<skill>` paths. The default scan then looks for `skills/skills/`, which doesn't exist, and only the listed folders load.
- **Consequences:** A single-skill plugin keeps the `wispr-flow-dictionary` shape: `source` is the skill's folder.

## 2026-10-01: effort-workflow depends on show-me

- **Status:** accepted
- **Context:** `/orchestrate-effort` uses `show-me` to show the plan. The family also uses `grilling`, `prototype`, `tdd` and `code-review` from mattpocock/skills.
- **Options:** None considered.
- **Choice and why:** A `dependencies` entry installs `show-me` with the family. The mattpocock/skills companions aren't plugins from a marketplace this one trusts, so the README keeps naming them.
- **Consequences:** Users install the mattpocock/skills companions themselves.

## 2026-10-01: agent setup is not a plugin

- **Status:** accepted
- **Context:** `/set-up-machine` and the skills that name it could also ship as a plugin.
- **Options:** A plugin: it lives in a cache folder that changes with each update, so the hook's wired path would break. A Claude Code plugin also can't install skills for several harnesses with `npx skills`, which is what the family exists for.
- **Choice and why:** Keep agent setup out of the marketplace. `/set-up-machine` wires the pre-tool hook to the absolute path of its installed copy, under `~/.agents/skills` or `~/.claude/skills`. `/maintain-environment`, `/set-up-project` and `/skill-recap` stay with it, since they name `/set-up-machine`.
- **Consequences:** These skills install only with `npx skills`.

## 2026-10-01: handover prompts keep bare skill names

- **Status:** accepted
- **Context:** A plugin skill's full name is `/<plugin>:<skill>`, and the skills name each other without a prefix.
- **Options:** Add the plugin prefix to every skill name in the text: not needed.
- **Choice and why:** Keep the bare names. Claude Code also runs a plugin skill by its bare name when no other skill has that name. A test with a user-invoked plugin skill showed this: `/zqa-one some/path.md` ran it with the argument. So `/orchestrate-with-handoff <handoff>` starts the plugin's skill. The model sees the prefixed names in its skill list and matches them to the bare names in the text.
- **Consequences:** A name clash with another skill would break the bare name.

## 2026-10-01: installing a skill both ways stays a README warning

- **Status:** accepted
- **Context:** A plugin skill and the same skill installed with `npx skills` both load. The bare name runs the `npx skills` copy, so plugin updates to it go unseen.
- **Options:** Detect or block the double install: Claude Code has no way for a plugin to do either.
- **Choice and why:** The README tells the user to pick one way and how to remove the other.
- **Consequences:** The maintainer installs with `npx skills`. The plugins are for other Claude Code users.

## 2026-10-01: plugin names are the skill's name or the family's name

- **Status:** accepted
- **Context:** A plugin name is what users type in `/plugin install` and what `enabledPlugins` stores, so a rename breaks installs.
- **Options:** None considered.
- **Choice and why:** A plugin is named after its skill, or after its family in kebab case.
- **Consequences:** The marketplace's `renames` map, from Claude Code 2.1.193, can carry users to a new name or record a removed plugin as `null`. Use it if a name must change, rather than treat names as fixed.

## 2026-10-01: no version on any plugin

- **Status:** accepted
- **Context:** A plugin may set a `version`.
- **Options:** None considered.
- **Choice and why:** Set no `version`, as for `wispr-flow-dictionary`. Each push to the default branch reaches users as a new commit.
- **Consequences:** Every push to the default branch is a release.

## 2026-10-01: validate without installing

- **Status:** accepted
- **Context:** The marketplace needs a check before it ships.
- **Options:** None considered.
- **Choice and why:** Run `claude plugin validate --strict .` and load a scratch copy of `skills/` with `--plugin-dir`. Nothing is installed.
- **Consequences:** An install from GitHub, end to end, is left to a QA issue.
