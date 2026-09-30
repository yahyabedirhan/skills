---
name: handover-to-herdr
description: Start a new agent session in its own Herdr tab, send it its starting prompt and confirm it's working; also free a closing effort's own worktree from a Herdr tab outside it. Use when a handover, a new effort or an effort's close runs through Herdr, or when another skill says to.
argument-hint: "Worktree path, topic, role, and the starting prompt"
---

# Handover To Herdr

Open a new agent session in a Herdr tab and send it its starting prompt. The calling skill, `/handover` or `/init-effort`, has already written the handoff and the prompt and decides what the new session does. It hands over four inputs: the worktree path; the topic, which is the effort's name or what the work is; the new session's role, such as `Orchestrator`, `Thinking` or another one-word role; and the starting prompt.

Run this skill from inside a Herdr pane or from outside one, such as a desktop-app session. `/herdr` requires `HERDR_ENV=1`, which only says this session runs in a pane, so check that `herdr status` reaches a server instead. Target explicit IDs read from Herdr's JSON, pass `--no-focus` wherever a command takes it, and never use `--current`, so that no command lands on the pane the maintainer is using.

## Parameters

- `<agent-to-start>`: the command that starts a new agent session, e.g. `claude` or `codex`, with its flags.

## Steps

1. Check that `herdr status` reaches a server.
   - **If it doesn't:** say so and hand back to the calling skill, which then works as if there were no session host.
2. Open a tab in the workspace whose checkout is the worktree, or open the worktree as a new workspace from the repository's own workspace. Read `session-start-commands.md` for the commands of this and the next three steps.
3. Label the tab `<harness> · <role> · <topic>`, so the maintainer can tell what runs in it.
4. Start `<agent-to-start>` in the tab's root pane as an agent named `<topic>-<role>` in lowercase.
   - **When a startup screen blocks it,** such as the harness asking whether to trust the folder: show the screen to the maintainer and let them decide.
5. Send the starting prompt exactly as the calling skill wrote it, and confirm the new agent is working.
6. If this session runs in a Herdr tab, put `[settled] ` at the start of that tab's label once this session's own work is done. The marker tells the maintainer nothing more will happen in the tab, which stays only so its history can be read.
7. Give the calling skill the workspace and tab where the new agent runs, so it can tell the maintainer.

When `/close-effort` calls this skill, read `close-effort-commands.md` instead of the steps above.

## References

- [session-start-commands.md](session-start-commands.md): the Herdr commands for opening, labelling and starting a session and sending its prompt, with their pitfalls.
- [close-effort-commands.md](close-effort-commands.md): the Herdr commands a close needs: finding the agents still working, and freeing the closing session's own worktree from outside it.
