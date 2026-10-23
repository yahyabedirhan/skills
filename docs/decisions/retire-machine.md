# Decisions: retire-machine

This page records the decisions behind the [`retire-machine`](../../skills/retire-machine/SKILL.md) skill.
It is for maintaining the skill and is never installed.
Entries follow the shape in [index.md](index.md).

## 2026-10-09: a skill of its own, not a mode of /set-up-machine

- **Status:** accepted
- **Context:** Retiring a machine could be a mode of `/set-up-machine`.
- **Options:** A mode of `/set-up-machine`: setup and its audit run often and change only settings, while retirement runs once per machine and ends in a step that can't be undone.
- **Choice and why:** A separate skill. Keeping them apart keeps the audit safe to rerun.
- **Consequences:** None.

## 2026-10-09: the user deletes the machine at the provider

- **Status:** accepted
- **Context:** Deletion can't be undone, and the provider's console is outside every harness.
- **Options:** None considered.
- **Choice and why:** The agent hands over the link and the order: snapshot if wanted, then delete, never only stop.
- **Consequences:** The last step is always the user's.

## 2026-10-09: take stock before changing anything

- **Status:** accepted
- **Context:** Retiring a VPS found a public web service that had run for seven weeks, and an untracked file in a repository cloned into the home folder. Neither was in the machine's own checklist.
- **Options:** None considered.
- **Choice and why:** Take stock before any change, and read panes without typing into them.
- **Consequences:** Retirement takes longer, and finds what a checklist misses.

## 2026-10-09: the session host's saved machine goes last

- **Status:** accepted
- **Context:** The saved machine is the agent's route to the machine.
- **Options:** Remove it earlier: the remaining steps then need SSH, which needs the user's approval.
- **Choice and why:** Remove it last.
- **Consequences:** None.

## 2026-10-09: revoking GitHub keys is the user's command

- **Status:** accepted
- **Context:** The rule table's `gh-access-keys` row refuses `gh ssh-key` to agents.
- **Options:** Try another route: that bypasses the rule.
- **Choice and why:** The skill gives the user the commands.
- **Consequences:** The user runs the key revocation.

## 2026-10-09: the workstation repo is found, not assumed

- **Status:** accepted
- **Context:** The skill records the retirement where the user keeps notes on the machine.
- **Options:** None considered.
- **Choice and why:** Read the repo through the pointer `~/.config/agents/source.md`, as `/set-up-machine` and `/maintain-environment` do, and ask once when the pointer records none. Name no file in that repo.
- **Consequences:** A repo with another layout works too.
