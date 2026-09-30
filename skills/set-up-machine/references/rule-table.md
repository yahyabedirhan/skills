# Rule table

How to change the rule table, `rules.json`, and the pre-tool hook that reads it. A row's fields, its `match` kinds and its spellings are in `SKILL.md`.

## Changing a row

Edit a row, or add one with its samples, then run `python3 <this skill>/scripts/verify.py --no-codex` until `rules ok`, and the unit tests below. The change reaches a machine when `/set-up-machine` runs there again. When the hook would read a row differently from what the row means, change the hook first, writing its test first in `scripts/tests/test_hook.py`.

## Changing the hook's code

Run the tests with `python3 -m unittest discover -s <this skill>/scripts/tests`. `scripts/tests/linux/run.sh <repo> <output folder>` runs them and `verify.py` in a fresh Linux container.

## Adding a harness

Write one reference with the same headings as [Claude Code's](claude-code.md), and add its wiring check to `HARNESSES` in `scripts/verify.py`.
