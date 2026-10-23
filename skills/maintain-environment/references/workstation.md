# Workstation repo

What a workstation repo is for, and how to start one. Once it exists, its own `DESIGN.md` is the guide for changing it, and `/set-up-machine`'s `references/workstation.md` defines the format of each `setup/` file.

## Purpose

The workstation repo is the one source of everything personal about how the user's agents run:

- their working agreement and glossary;
- which tool fills each role;
- their personal workflow;
- their personal permissions;
- what every machine installs;
- the release rules every one of their projects shares, when they have them.

`<workstation-repo>` is the user's own repository, usually private, because it holds the personal detail that the public skills repo and the user's projects leave out. `/set-up-machine` reads its `setup/` folder on each machine, so a change made once reaches every machine. Without one, each machine's shared global instructions file holds the personal lines itself, and a personal permission has no home.

## Starting layout

```text
README.md                 what the repository is, for the user
AGENTS.md                 for whoever maintains the setup: the documents to read first
DESIGN.md                 where things are in the repository, and the shape of each kind of file
setup/instructions.md     written by /set-up-machine from the shared file's personal parts
setup/permissions.json    {"version": 1, "rules": []}
setup/installs.json       {"skills": [{"source": "<skills-repo>"}]}
```

- **`setup/`** is what `/set-up-machine` reads, and the only part a skill relies on. `/set-up-project` also reads `setup/releasing.md` when it exists.
- **`AGENTS.md`** names each other document, such as the user's principles or a full glossary, and says when to read it. The names and paths of those documents are the user's to choose.
- **`DESIGN.md`** starts short: the layout above, and that a new file copies the shape of its siblings. It grows as the user adds kinds of files.

## Creation

Start a workstation repo when the user asks for one. Offer to start one when a change needs it, such as a personal permission.

1. Ask the user for `<workstation-repo>` and `<path-to-workstation-repo>`. Create the repository as private, since it holds personal detail, and clone it there.
2. Write the starting layout, leaving out `setup/instructions.md`.
3. Have the user commit and push it, or commit and push it when they ask.
4. Run `/set-up-machine` on this machine with the two values. It writes the pointer and creates `setup/instructions.md` from the shared file's current personal parts. It also proposes the machine's personal permission entries for `setup/permissions.json`.
5. Have the user commit and push the files `/set-up-machine` added, then run `/set-up-machine` on each other machine with the same two values.
