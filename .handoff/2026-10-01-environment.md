# Handoff: personal setup in a personal repository, found through a pointer

- **Worktree:** this one, `~/.treehouse/skills-22e236/2/skills` (treehouse lease `environment`), on branch `environment/personal-repository`, cut from `origin/main`.
- **Spec:** #111 "Spec: personal setup lives in a person's own repository, found through a pointer". Label `effort:environment`.
- **Tickets, in order:**
  1. #113 "set-up-machine reads a personal repository through a pointer, for instructions". Not blocked.
  2. #114 "Personal permissions from the personal repository, with a plain allow level". Blocked by #113.
  3. #115 "maintain-environment sends personal changes to the personal repository". Blocked by #113.
  4. #116 "Audit the skills repo for personal setup and move it out". Blocked by #113.
- **Replaces** #104 (closed), which asked for a home for personal allows.
- **The other side:** the maintainer's own personal repository is private, and its issue is tracked there by another agent. That agent waits on #113's and #114's reference to fill the files. Don't edit that repository from here.
- **Reaching the session that handed over:** it stops after the handover. Decide open questions yourself and list them in the pull request's *Things to be aware of*.

## Settled with the maintainer

- The generic safety rules stay in `rules.json`. Only personal preferences move: which tool fills each role, personal workflow lines, and tools the person added along with when to use them.
- The pointer is `~/.config/agents/source.md`. set-up-machine asks the user for it when it's missing and writes it.
- The personal repository is the source and the machine's files are output. A personal change goes there, then set-up-machine runs again.
- This repo is public and general. The reference and every skill text describe the kinds of entries at a high level, and **name no particular tool or example**.
- Testing goes through `verify.py --home <copy>` and the hook's tests (`scripts/tests/`).

## Suggested skills

`orchestrate-effort`, `orchestrating`, `set-up-machine`, `maintain-environment`, `tdd`, `writing-for-agents`, `to-pr`. Read `docs/decisions/skill-writing.md` before changing a skill.
