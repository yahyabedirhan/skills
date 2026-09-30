---
name: set-up-machine
description: Set up or audit a machine's coding-agent harnesses from one rule table - the shared global instructions every harness reads, the global rules (deny, ask, allow-and-report) each one enforces, the pre-tool hook, and memory kept off. Use for a new machine or VPS, to audit this machine's agent setup, or when another skill says to check the machine.
---

# Set up machine

Make every coding-agent harness on the machine (Claude Code, Codex, opencode, Cursor's IDE and CLI) match two sources: the **rule table**, [`rules.json`](rules.json), which holds each global rule once as what it covers; and the **shared global instructions file**, `~/.config/agents/AGENTS.md`, which every harness reads. Each harness also runs the **pre-tool hook**, `scripts/pre_tool_hook.py`, before every tool call, and keeps its memory off. Never remove or loosen an entry the table didn't produce: it's the user's. Harness formats change, so check the docs a harness reference links before writing; where they differ, follow the docs and name the difference in your report. Running the skill again is the **audit**: the same steps, ending with an empty diff.

## Parameters

- `<skills-repo>`: the user's own skills repo on GitHub, as `owner/repo`.

## Steps

1. **Inspect.** Find each harness on the machine, read its reference, then every file that reference names. Read the shared file too.
2. **Propose one diff** that brings each harness in line with the rule table, the shared file's shape, memory off, the hook wired, and the `<skills-repo>` skills installed. Give every harness found its own section, listing each gap its reference names and the hook's blind spots.
3. **Ask once** for one approval of the whole diff. A change after that needs a new approval.
4. **Back up** every file the diff changes or removes.
5. **Write** exactly the approved diff.
6. **Verify** with `scripts/verify.py`, then inspect again until the diff is empty. Report the backup folder, what's wired, the gaps, and the stricter and extra entries.

## References

- [references/machine-diff.md](references/machine-diff.md): read before step 2. The diff's labels, what may be removed, the shared skills install, the backup folder, writing, what verify must print, and trying a change on a copy of the home folder.
- [references/global-instructions.md](references/global-instructions.md): read whenever the shared file or a harness's own global file is in the diff. The shared file's shape, the Defaults roles, what counts as personal workflow, moving a harness's own file, and why memory stays off.
- [references/rule-table.md](references/rule-table.md): read to turn a row into native entries or to change the table. A row's fields, its `match` kinds, and the spellings a command row needs.
- [references/pre-tool-hook.md](references/pre-tool-hook.md): read when wiring the hook or changing the code. What it does per level, the script path and fail-open wiring, the blind spots every audit names, and the tests.
- One reference per harness, read for each harness found: [Claude Code](references/claude-code.md), [Codex](references/codex.md), [opencode](references/opencode.md), [Cursor](references/cursor.md). Each says how the harness is found, where it keeps each setting, a row's native form with worked examples, the hook's wiring, and its gaps.
