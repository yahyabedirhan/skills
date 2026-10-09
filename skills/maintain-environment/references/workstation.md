# Workstation repo

What the user's workstation repo holds, and how to start one and change it. `/set-up-machine` reads the repository to set up each machine. Its `references/workstation.md` gives the pointer that finds the clone and the exact format of every `agents/` file.

## What it is for

The workstation repo is the one source of everything personal about how the user's agents run:

- their working agreement and glossary;
- which tool fills each role;
- their personal workflow;
- their personal permissions;
- what every machine installs.

It is the user's own repository, usually private, because it holds the personal detail that the public skills repo and the user's projects leave out. `/set-up-machine` generates each machine's shared global instructions file and harness settings from it, so a change made once in the repository reaches every machine. Without one, each machine's shared file holds the personal lines itself, and a personal permission has no home.

## Its starting layout

```text
README.md                 what the repository is, for the user
AGENTS.md                 for whoever maintains the setup: the documents to read first
agents/instructions.md    ## Working agreement, ## Glossary, ## Environment defaults
                          (the roles table, then ### <Tool> glossary subsections), ## Personal workflow
agents/permissions.json   {"version": 1, "rules": []}
agents/installs.json      every machine's installs, starting with <skills-repo>
docs/principles.md        optional: the user's principles and a mental model of their setup
docs/decisions/           optional: one file per topic, each a list of dated entries
GLOSSARY.md               optional: the full glossary
```

- **`agents/`** is what `/set-up-machine` reads, and the only part a skill relies on. Write each file in the format `/set-up-machine`'s `references/workstation.md` gives. Start `agents/installs.json` as `{"skills": [{"source": "<skills-repo>"}]}`, since the file is the whole list a machine installs.
- **`AGENTS.md`** names each other document, such as the principles and the full glossary, and says when to read it. This skill reads it before a change that improves the workflow or environment. The other documents' names and paths are therefore the user's to choose.
- **`GLOSSARY.md`** holds every term. `agents/instructions.md` keeps only the core words every session needs, since `/set-up-machine` copies them into every harness's context.
- **`docs/decisions/`** keeps the reason behind each choice, so the generated files hold only rules. An entry may record a question the user hasn't decided yet.

## Starting one

Start a workstation repo when the user asks for one. Offer to start one when a change needs it, such as a personal permission.

1. Ask the user for `<workstation-repo>` and `<path-to-workstation-repo>`. Create the repository as private, since it holds personal detail, and clone it there.
2. Write the starting layout, leaving out `agents/instructions.md`. Write the optional documents only when the user has content for them.
3. Have the user commit and push the starting layout, or commit and push it when they ask.
4. Run `/set-up-machine` on this machine with the two values. It writes the pointer, replacing one that records none, and creates `agents/instructions.md` from the shared file's current personal parts. It also proposes the machine's own personal permission entries for `agents/permissions.json`.
5. Have the user commit and push the files `/set-up-machine` added, then run `/set-up-machine` on each other machine with the same two values.

## Changing it

Make each personal change in the clone at `<path-to-workstation-repo>`:

- a working agreement, glossary, environment default or personal workflow line: `agents/instructions.md`. Leave out the `workstation-repo` and `path-to-workstation-repo` rows: the pointer fills them, so change either value by running `/set-up-machine`, which rewrites the pointer;
- a personal permission: `agents/permissions.json`;
- a skill or a command every machine installs: `agents/installs.json`;
- the reason behind a choice: a decision record, or the Why column of the Environment defaults table in `agents/instructions.md`.

Leave the shared file's generated parts and the harness settings to `/set-up-machine`, since its next run rewrites them. The user commits and pushes the change. Each machine then pulls it into its clone and runs `/set-up-machine`.
