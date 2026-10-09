# Decisions: retire-machine

The decisions behind the `retire-machine` skill. This file is for maintaining it and is never installed. Add an entry for each new decision: the date, what was decided, and why.

## 2026-10-09: the first version

- **A skill of its own, not a mode of `/set-up-machine`.** Setup and its audit run often and change only settings; retirement runs once per machine and ends in a step that can't be undone. Keeping them apart keeps the audit safe to rerun.
- **The user deletes the machine at the provider.** Deletion can't be undone, and the provider's console is outside every harness. The agent hands over the link and the order: snapshot if wanted, then delete, never only stop.
- **Take stock before changing anything, and read panes without typing into them.** Retiring the Hetzner server found a public web service that had run for seven weeks and an untracked file in a repository cloned into the home folder. Neither was in the machine's own checklist.
- **The session host's saved machine goes last.** It is the agent's route to the machine; removing it earlier leaves the remaining steps to SSH, which needs the user's approval.
- **Revoking GitHub keys is the user's command.** The rule table's `gh-access-keys` row refuses `gh ssh-key` to agents, so the skill gives the user the commands instead of trying another route.
- **The workstation repo is found, not assumed.** The skill reads it through the pointer `~/.config/agents/source.md`, as `/set-up-machine` and `/maintain-environment` do, and asks once when the pointer records none. It names no file in that repo, so a repo with another layout works too.
