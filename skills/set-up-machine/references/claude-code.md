# Claude Code adapter

What set-up-machine writes for Claude Code, and why. The code is `scripts/setupmachine/adapters/claude_code.py`. Sources: the Claude Code docs on [permissions](https://code.claude.com/docs/en/permissions), [memory](https://code.claude.com/docs/en/memory) and [settings](https://code.claude.com/docs/en/settings).

## Global instructions

- Claude Code reads `~/.claude/CLAUDE.md` in every session. It has no global `AGENTS.md`.
- The adapter adds one line to that file: `@~/.config/agents/AGENTS.md`, importing the shared file. Imports in user-scope files load without an approval dialog. The rest of `CLAUDE.md` is left as it is.
- Against a `--home` other than the user's own, the line holds the absolute path instead, since `~` would name the real home.

## Permissions

- **File:** `~/.claude/settings.json`, key `permissions` with the lists `deny`, `ask` and `allow`. Everything else in the file is kept as it is.
- **Levels:** `deny` rows go to `deny`, `ask` rows to `ask`. `allow-and-report` has no native level; it needs the pre-tool hook.
- **Evaluation:** deny, then ask, then allow; the first match wins. So tightening adds the stricter entry and leaves the looser one in place: it no longer takes effect, and it isn't the skill's to remove.
- **Matching:** `Bash(<prefix>:*)` matches the command text as written, not its parsed arguments. The adapter writes one entry per spelling the rule table expands to: `rm -rf`, `rm -fr`, `rm -R -f`, `rm --recursive --force`, `/bin/rm -rf`, and the rest.
- **Compound commands:** deny and ask rules apply to each part of `a && b`, `a; b`, pipes and subshells, and past wrappers such as `timeout`, `nice` and `nohup`.
- **Projects can't loosen it:** a user-level deny holds against any project `allow`.

## Gaps

Text matching lets these through, so the plan lists them as gaps for each rule:

- more flags in the same token (`rm -rfv`), and flags after the operands (`rm x -rf`);
- the command inside a quoted `bash -c`, `sh -c` or `zsh -c` string.

## What the agent sees

A refused command returns `Permission to use Bash with command <command> has been denied.` It names the command, not the rule, so the instruction reaches the agent through the shared file's rule line, loaded at the start of every session.

## Checking it

Two checks, run after an apply:

- **The deny holds:** in a throwaway folder, `claude -p "Run exactly: rm -rf x" --allowedTools Bash` leaves `x` in place and reports the command denied. Allowing `Bash` proves the deny rule refused it, not the lack of an allow.
- **The instruction is loaded:** `claude -p "Without tools: quote your rule about rm -rf and the file it came from."` quotes the rule line from `~/.config/agents/AGENTS.md`.
