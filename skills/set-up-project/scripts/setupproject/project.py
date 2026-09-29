"""The project plan: the machine check, the project's files, and the audit, shown before anything is written."""
from __future__ import annotations

from pathlib import Path

from setupmachine import reconcile
from setupmachine.adapters import ADAPTERS
from setupmachine.plan import Plan, render as render_machine

from . import audit, scaffold

# The order kinds are listed in, and which fail the audit.
KINDS = ("added", "updated", "todo", "present", "weakens", "overlaps", "extra", "gap")


class PlanMismatch(RuntimeError):
    pass


def check_machine(home: Path, table: list, rules_path: Path, tool_names=None):
    """set-up-machine's plan for this home: its text when the machine differs, else None."""
    tools = None
    if tool_names:
        names = [l.strip() for l in Path(tool_names).read_text().splitlines() if l.strip()]
        tools = {adapter.NAME: names for adapter in ADAPTERS}
    plan = reconcile.build(home, table, Path.home(), tools, rules_path)
    return render_machine(plan) if plan.has_changes else None


def build(project: Path, home: Path, table: list) -> Plan:
    sections, writes = scaffold.plan(project)
    sections += audit.audit(project, home, table)
    return Plan(project, sections, writes)


def render(plan: Plan) -> str:
    out = [f"set-up-project plan for {plan.home}", "", "Machine  set-up-machine reports no changes", ""]
    for s in plan.sections:
        out.append(f"{s.title}  ({_shown(s.path, plan.home)})")
        present = sum(1 for c in s.changes if c.kind == "present")
        for kind in KINDS:
            if kind == "present":
                if present:
                    out.append(f"  present     {present} in place")
                continue
            out.extend(_line(c) for c in s.changes if c.kind == kind)
        if not s.changes:
            out.append("  nothing to audit")
        out.append("")
    todo = plan.count("todo")
    out.append(
        f"Summary: {plan.count('added')} added, {plan.count('updated')} updated, {todo} to do by hand; "
        f"audit: {plan.count('weakens')} weaken a global rule, {plan.count('overlaps')} overlap one, "
        f"{plan.count('gap')} gap(s)."
    )
    if plan.has_changes:
        out.append(f"Plan id: {plan.id}")
    elif not todo:
        out.append("No changes.")
    out.append("Audit: " + ("failed." if plan.count("weakens") else "passed."))
    return "\n".join(out) + "\n"


def _line(c) -> str:
    level = f"{c.level:<6}" if c.level else " " * 6
    rule = f"  [{c.rule}]" if c.rule else ""
    note = f"  ({c.note})" if c.note else ""
    return f"  {c.kind:<11} {level} {c.text}{rule}{note}"


def _shown(path: Path, project: Path) -> str:
    try:
        return str(path.relative_to(project)) or "."
    except ValueError:
        return str(path)


def apply(plan: Plan, approved_id: str) -> list:
    """Write every changed file of the approved plan. Returns the paths written."""
    if approved_id != plan.id:
        raise PlanMismatch(
            f"the project changed since plan {approved_id} (it's now {plan.id}); plan it again and approve the new diff")
    written = []
    for w in plan.writes:
        if not w.changed:
            continue
        target = w.path.resolve()  # through a symlink, so a linked file stays linked
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(w.new)
        written.append(w.path)
    return written
