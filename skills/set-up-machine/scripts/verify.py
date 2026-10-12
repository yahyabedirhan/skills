#!/usr/bin/env python3
"""set-up-machine's verifier: did every harness on this machine get what the workstation repo's setup/ asks for?

usage: verify.py [--home DIR] [--rules FILE]
       verify.py --codex-trust-hash COMMAND

It reads the machine and writes nothing. The steps:

1. Load the rule table and the workstation repo's setup/ files, through the pointer
   (~/.config/agents/source.md).
2. Print two global lines:
   - setup: the pointer and setup/ files are readable, and the shared global instructions
     file (~/.config/agents/AGENTS.md) carries what setup/instructions.md generates;
   - rules: every sample of every rule-table row and personal permission gets its row's
     answer from the hook's decision.
3. Print one table: a row per harness found (its folder exists, or its CLI is on PATH; a --home
   copy counts only its folders), a column per setup area (instructions,
   guardrails, sandbox, plugins, skills), each cell ok, FAIL, gap or n/a.
4. Print one detail line per FAIL and gap cell.
5. Exit 1 when any line or cell is FAIL.

--codex-trust-hash prints the trusted_hash Codex needs in config.toml for a hook running
COMMAND (references/codex.md). Python 3.9+, standard library only.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from setupmachine import checks, hook, rules, workstation  # noqa: E402
from setupmachine.harnesses import ALL, codex, pi  # noqa: E402

AREAS = ("instructions", "guardrails", "sandbox", "plugins", "skills")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check every harness against the workstation repo's setup/.")
    parser.add_argument("--home", type=Path, default=Path.home(), help="the home folder to check (default: $HOME)")
    parser.add_argument("--rules", type=Path, default=rules.DEFAULT_TABLE)
    parser.add_argument("--codex-trust-hash", metavar="COMMAND", help="print Codex's trusted_hash for this hook command")
    args = parser.parse_args()
    if args.codex_trust_hash is not None:
        print(codex.trust_hash(args.codex_trust_hash))
        return 0
    home = args.home.expanduser().resolve()
    try:
        table = rules.load(args.rules)
    except rules.RuleTableError as exc:
        print(f"rules  FAIL  {exc}")
        return 1
    setup = workstation.load(home, table, [h.ID for h in ALL])
    ctx = checks.Context(home, setup, table + setup.rows, codex.config_home(home), pi.agent_dir(home))

    failed = global_line("setup", *setup_line(ctx), home)
    failed |= global_line("rules", *rules_line(ctx, len(table)), home)
    rows = [(h.LABEL, [getattr(h, f"check_{area}")(ctx) for area in AREAS]) for h in ALL if h.present(home)]
    print_table(rows)
    return 1 if failed or any(c.status == "FAIL" for _, cells in rows for c in cells) else 0


def setup_line(ctx) -> tuple:
    """(status, text): the pointer and setup/ files, and the shared file against setup/instructions.md."""
    setup = ctx.setup
    if setup.problems:
        return "FAIL", "; ".join(setup.problems)
    if not setup.repository:
        return "n/a", "the pointer says there is no workstation repo, so the shared file is its own source"
    problems = workstation.shared_file_problems(setup, ctx.home)
    if problems:
        return "FAIL", "; ".join(problems)
    return "ok", f"{setup.repository}: the shared file matches setup/instructions.md"


def rules_line(ctx, table_size: int) -> tuple:
    """(status, text): each sample through hook.decide gets its row's answer."""
    wrong, count = [], 0
    for row in ctx.rows:
        for sample in row.covers:
            count += 1
            verdict = decide(row, sample, ctx)
            got = _answer(verdict, row)
            if got != row.level:
                wrong.append(f"{row.id}: `{sample}` got {got}, expected {row.level}")
        for sample in row.leaves:
            count += 1
            if _holds(decide(row, sample, ctx), row):
                wrong.append(f"{row.id}: `{sample}` should pass, but the row catches it")
    personal = len(ctx.rows) - table_size
    text = f"{table_size} rows" + (f" and {personal} personal permissions" if personal else "") + f", {count} samples"
    return ("FAIL", f"{text}; " + "; ".join(wrong)) if wrong else ("ok", text)


def decide(row, sample: str, ctx):
    """The hook's verdict on one sample, as the call a row of its kind would see."""
    cwd = str(ctx.home / "project")
    if row.kind == "file":
        call = hook.ToolCall(tool="Read" if row.access == "read" else "Write", files=((sample, row.access),), cwd=cwd)
    elif row.kind == "mcp-tool":
        call = hook.ToolCall(tool=sample, cwd=cwd)
    else:
        call = hook.ToolCall(tool="Bash", command=sample, cwd=cwd)
    return hook.decide(call, ctx.rows, ctx.home)


def _holds(verdict, row) -> bool:
    return any(hit.rule.id == row.id for hit in verdict.denials + verdict.asks + verdict.reports + verdict.allows)


def _answer(verdict, row) -> str:
    """The row's level when the verdict holds it. An allow row also needs no other row to ask or deny."""
    if not _holds(verdict, row):
        return "no match"
    return verdict.answer if row.level == "allow" else row.level


def global_line(name: str, status: str, text: str, home: Path) -> bool:
    print(f"{name:<6} {status:<5} {text.replace(str(home) + '/', '~/')}")
    return status == "FAIL"


def print_table(rows: list):
    if not rows:
        print("\nNo harness is set up on this machine.")
        return
    width = max(len("harness"), *(len(label) for label, _ in rows)) + 2
    print("\n" + "harness".ljust(width) + "".join(area.ljust(14) for area in AREAS).rstrip())
    for label, cells in rows:
        print(label.ljust(width) + "".join(c.status.ljust(14) for c in cells).rstrip())
    details = [f"{c.status:<4}  {label} {area}: {'; '.join(c.details)}" for label, cells in rows
               for area, c in zip(AREAS, cells) if c.status in ("FAIL", "gap")]
    print("\n" + "\n".join(details) if details else "", end="\n" if details else "")


if __name__ == "__main__":
    sys.exit(main())
