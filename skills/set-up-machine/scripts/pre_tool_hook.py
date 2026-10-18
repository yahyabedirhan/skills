#!/usr/bin/env python3
"""set-up-machine's pre-tool hook. A harness runs it before each tool call, with the call on stdin.

usage: `pre_tool_hook.py` [--harness claude-code|codex|cursor|grok-bot|opencode|pi] [--config FILE] [--rules FILE]

The steps:

1. Read the payload with the harness module's `read`, into one tool call.
2. Load the rule table (`rules.json`) and the personal permissions from the workstation repo.
3. Decide the call with hook.decide.
4. A denied call: print the harness's refusal, naming each refused part, its rule and instruction.
5. Otherwise, write a report line for each allow-and-report row it hits, and print the harness's
   answer, which leaves the call to the harness's own permissions (or, in Pi, asks the user).

It exits 1 when it can't read the call or the rule table. Each harness's wiring then lets the call
through to its native rules, except Pi's, which has none and refuses it (`references/pi/cli.md`).
Python 3.9+, standard library only.
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from setupmachine import hook, rules, workstation  # noqa: E402
from setupmachine.harnesses import BY_ID  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="set-up-machine's pre-tool hook: reads one tool call on stdin.")
    parser.add_argument("--harness", choices=sorted(BY_ID), default="claude-code")
    parser.add_argument("--config", type=Path, default=Path(hook.CONFIG_PATH).expanduser())
    parser.add_argument("--rules", type=Path, default=rules.DEFAULT_TABLE)
    args = parser.parse_args()
    harness = BY_ID[args.harness]
    try:
        payload = json.loads(sys.stdin.read() or "{}")
        call = harness.read(payload if isinstance(payload, dict) else {})
        table = rules.load(args.rules)
    except (ValueError, OSError) as exc:
        print(f"set-up-machine hook: {exc}", file=sys.stderr)
        return 1
    # A broken personal file leaves the rule table's rows in force; `verify.py` reports the file.
    try:
        table += workstation.personal_rows(Path.home(), table)
    except Exception as exc:
        print(f"set-up-machine hook: personal permissions skipped: {exc}", file=sys.stderr)
    try:
        verdict = hook.decide(call, table, Path.home())
    except (ValueError, OSError) as exc:
        print(f"set-up-machine hook: {exc}", file=sys.stderr)
        return 1
    if verdict.denials:
        sys.stdout.write(harness.write(verdict.denials))
        return 0
    if verdict.reports and call.report:
        try:
            folder = hook.report_dir(hook.load_config(args.config), args.config)
            hook.write_report(folder, call, verdict.reports, args.harness, datetime.now(timezone.utc))
        except (ValueError, OSError) as exc:
            print(f"set-up-machine hook: couldn't write the report: {exc}", file=sys.stderr)
            return 1
    sys.stdout.write(harness.write([], verdict.asks))
    return 0


if __name__ == "__main__":
    sys.exit(main())
