#!/usr/bin/env python3
"""Set up and audit this machine's agent harnesses from set-up-machine's rule table.

usage:
  set_up_machine.py plan  [--home DIR] [--rules FILE] [--tool-names FILE]
  set_up_machine.py apply --plan-id ID [--home DIR] [--rules FILE] [--tool-names FILE]

plan   shows, per harness, what applying would add, tighten or remove, the rules
       already in place, the gaps the harness can't express, and every extra
       rule found. It writes nothing. A plan with nothing to do ends "No changes."
apply  writes exactly the plan with that id, after backing up each file it
       changes under <home>/.config/agents/backups/. If anything changed since
       the plan, it refuses and writes nothing.

Mail-tool rules match the MCP tool names each harness exposes, which plan asks
the harness for (Claude Code: a `claude -p` session stopped once it lists its
tools). --tool-names FILE gives them instead, one per line.

--home defaults to $HOME. Point it at a copy to try the skill without touching
the real machine. Python 3.9+, standard library only.
"""
from __future__ import annotations

import argparse
import shlex
import sys
from pathlib import Path

from setupmachine import reconcile, rules
from setupmachine.adapters import ADAPTERS
from setupmachine.plan import Run, render


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("plan", "apply"))
    parser.add_argument("--home", type=Path, default=Path.home(), help="the home folder to set up (default: $HOME)")
    parser.add_argument("--rules", type=Path, default=rules.DEFAULT_TABLE, help="the rule table (default: the skill's rules.json)")
    parser.add_argument("--plan-id", help="apply only: the id printed by the plan that was approved")
    parser.add_argument("--tool-names", type=Path, help="MCP tool names, one per line, instead of asking each harness")
    args = parser.parse_args(argv)

    home = args.home.expanduser().resolve()
    if not home.is_dir():
        parser.error(f"--home {home} isn't a folder")
    try:
        table = rules.load(args.rules)
        tools = None
        if args.tool_names:
            names = [l.strip() for l in args.tool_names.read_text().splitlines() if l.strip()]
            tools = {adapter.NAME: names for adapter in ADAPTERS}
        plan = reconcile.build(home, table, Path.home(), tools, args.rules.resolve())
    except (rules.RuleTableError, ValueError, OSError) as exc:
        print(f"set-up-machine: {exc}", file=sys.stderr)
        return 1

    if args.command == "plan":
        sys.stdout.write(render(plan))
        if plan.has_changes:
            print(f"To apply after approval: {_apply_command(args, home, plan.id)}")
        return 0

    if not args.plan_id:
        parser.error("apply needs --plan-id from an approved plan")
    if not plan.has_changes:
        print("No changes.")
        return 0
    try:
        backup = reconcile.apply(plan, args.plan_id)
    except (reconcile.PlanMismatch, reconcile.RunFailed) as exc:
        print(f"set-up-machine: {exc}", file=sys.stderr)
        return 1
    for w in plan.writes:
        if isinstance(w, Run):
            print(f"ran {' '.join(w.argv)}")
        elif w.changed:
            print(f"{'linked' if w.link_to is not None else 'wrote'} {w.path}")
    if backup.exists():
        print(f"backups of the previous files: {backup}")
    print("Run the plan again: it should report no changes.")
    return 0


def _apply_command(args, home: Path, plan_id: str) -> str:
    parts = ["python3", str(Path(__file__).resolve()), "apply", "--plan-id", plan_id]
    if home != Path.home().resolve():
        parts += ["--home", str(home)]
    if args.rules.resolve() != rules.DEFAULT_TABLE:
        parts += ["--rules", str(args.rules.resolve())]
    if args.tool_names:
        parts += ["--tool-names", str(args.tool_names.resolve())]
    return shlex.join(parts)


if __name__ == "__main__":
    sys.exit(main())
