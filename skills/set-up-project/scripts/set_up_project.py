#!/usr/bin/env python3
"""Set up and audit a project for coding agents, after checking the machine.

usage:
  set_up_project.py plan  [--project DIR] [--home DIR] [--rules FILE] [--tool-names FILE] [--machine-skill DIR]
  set_up_project.py apply --plan-id ID [--project DIR] [--home DIR] [--rules FILE] [--machine-skill DIR]

plan   checks the machine first with set-up-machine's plan. If the machine
       differs, it prints that plan and the command to apply it, and stops
       (exit 3): approve it, apply it, and plan the project again. Otherwise it
       shows what it would write in the project (AGENTS.md, CLAUDE.md as
       `@AGENTS.md`, the .gitignore lines), what's left to write by hand (todo),
       and the audit of each harness's project files against the global rule
       table. It writes nothing. Nothing to write or do ends "No changes.".
apply  writes exactly the project plan with that id, and refuses if the
       project changed since.

Exit codes: 0 done; 1 an error; 2 the audit found a project file that weakens a
global rule; 3 the machine differs from set-up-machine's table.

--home defaults to $HOME: point it at a copy to try a machine change safely.
--rules and --tool-names are set-up-machine's, passed through. Python 3.9+,
standard library only.
"""
from __future__ import annotations

import argparse
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from setupproject import DEFAULT_MACHINE_SKILL, use_machine_skill  # noqa: E402

MACHINE_DIFFERS = 3
AUDIT_FAILED = 2


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("plan", "apply"))
    parser.add_argument("--project", type=Path, default=Path.cwd(), help="the project folder (default: here)")
    parser.add_argument("--home", type=Path, default=Path.home(), help="the machine's home folder (default: $HOME)")
    parser.add_argument("--rules", type=Path, help="set-up-machine's rule table (default: its rules.json)")
    parser.add_argument("--tool-names", type=Path, help="MCP tool names, one per line, for set-up-machine's plan")
    parser.add_argument("--machine-skill", type=Path, default=DEFAULT_MACHINE_SKILL,
                        help="the set-up-machine skill folder (default: beside this skill)")
    parser.add_argument("--plan-id", help="apply only: the id printed by the plan that was approved")
    args = parser.parse_args(argv)

    try:
        scripts = use_machine_skill(args.machine_skill)
    except ImportError as exc:
        print(f"set-up-project: {exc}", file=sys.stderr)
        return 1
    from setupmachine import rules  # noqa: E402  (found through use_machine_skill)
    from setupproject import project  # noqa: E402

    home = args.home.expanduser().resolve()
    target = args.project.expanduser().resolve()
    rules_path = (args.rules or rules.DEFAULT_TABLE).resolve()
    for name, folder in (("--home", home), ("--project", target)):
        if not folder.is_dir():
            parser.error(f"{name} {folder} isn't a folder")
    try:
        table = rules.load(rules_path)
    except (rules.RuleTableError, OSError) as exc:
        print(f"set-up-project: {exc}", file=sys.stderr)
        return 1

    if args.command == "apply":
        if not args.plan_id:
            parser.error("apply needs --plan-id from an approved plan")
        try:
            plan = project.build(target, home, table)
            written = project.apply(plan, args.plan_id)
        except (project.PlanMismatch, ValueError, OSError) as exc:
            print(f"set-up-project: {exc}", file=sys.stderr)
            return 1
        for path in written:
            print(f"wrote {path}")
        print("Plan the project again: it should report no changes.")
        return 0

    try:
        machine = project.check_machine(home, table, rules_path, args.tool_names)
    except (rules.RuleTableError, ValueError, OSError) as exc:
        print(f"set-up-project: set-up-machine's plan failed: {exc}", file=sys.stderr)
        return 1
    if machine is not None:
        sys.stdout.write(machine)
        command = _machine_apply(scripts, home, rules_path, rules.DEFAULT_TABLE, args.tool_names, machine)
        print()
        print("The machine differs from set-up-machine's table, so set it up first: show the plan above, "
              "ask for one approval, then run")
        print(f"  {command}")
        print("and plan the project again.")
        return MACHINE_DIFFERS

    try:
        plan = project.build(target, home, table)
    except (ValueError, OSError) as exc:
        print(f"set-up-project: {exc}", file=sys.stderr)
        return 1
    sys.stdout.write(project.render(plan))
    if plan.has_changes:
        print(f"To apply after approval: {_project_apply(args, target, home, rules_path, rules.DEFAULT_TABLE, plan.id)}")
    return AUDIT_FAILED if plan.count("weakens") else 0


def _plan_id(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("Plan id: "):
            return line[len("Plan id: "):].strip()
    return "<id>"


def _machine_apply(scripts: Path, home: Path, rules_path: Path, default_rules: Path, tool_names, text: str) -> str:
    parts = ["python3", str(scripts / "set_up_machine.py"), "apply", "--plan-id", _plan_id(text)]
    if home != Path.home().resolve():
        parts += ["--home", str(home)]
    if rules_path != default_rules.resolve():
        parts += ["--rules", str(rules_path)]
    if tool_names:
        parts += ["--tool-names", str(Path(tool_names).resolve())]
    return shlex.join(parts)


def _project_apply(args, target: Path, home: Path, rules_path: Path, default_rules: Path, plan_id: str) -> str:
    parts = ["python3", str(Path(__file__).resolve()), "apply", "--plan-id", plan_id, "--project", str(target)]
    if home != Path.home().resolve():
        parts += ["--home", str(home)]
    if rules_path != default_rules.resolve():
        parts += ["--rules", str(rules_path)]
    if args.machine_skill.resolve() != DEFAULT_MACHINE_SKILL.resolve():
        parts += ["--machine-skill", str(args.machine_skill.resolve())]
    return shlex.join(parts)


if __name__ == "__main__":
    sys.exit(main())
