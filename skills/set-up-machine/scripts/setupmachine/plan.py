"""The plan: what reconcile would change, shown as a diff before anything is written."""
from __future__ import annotations

import difflib
import hashlib
from dataclasses import dataclass, field
from pathlib import Path

# Kinds that change a file, then kinds that are only reported.
CHANGE_KINDS = ("added", "tightened", "removed")
REPORT_KINDS = ("present", "wired", "stricter", "found", "gap", "none", "extra")


@dataclass
class Change:
    kind: str  # one of CHANGE_KINDS or REPORT_KINDS
    text: str
    level: str = ""
    rule: str = ""
    note: str = ""


@dataclass
class Section:
    title: str
    path: Path
    changes: list = field(default_factory=list)
    show_diff: bool = False  # print the file's unified diff instead of change lines


@dataclass
class FileWrite:
    path: Path
    old: object  # str, or None when the file doesn't exist yet
    new: object  # str, or None to delete the file (apply keeps it in the backup)

    @property
    def changed(self) -> bool:
        return self.old != self.new


@dataclass
class Plan:
    home: Path
    sections: list
    writes: list

    @property
    def has_changes(self) -> bool:
        return any(w.changed for w in self.writes)

    @property
    def id(self) -> str:
        """Fingerprint of every write, so apply runs exactly the plan that was approved."""
        h = hashlib.sha256()
        for w in sorted(self.writes, key=lambda w: str(w.path)):
            if w.changed:
                for part in (str(w.path), "\0", w.old if w.old is not None else "\1", "\0",
                             w.new if w.new is not None else "\1", "\0"):
                    h.update(part.encode())
        return h.hexdigest()[:12]

    def count(self, kind: str) -> int:
        return sum(1 for s in self.sections for c in s.changes if c.kind == kind)


def render(plan: Plan) -> str:
    out = [f"set-up-machine plan for {plan.home}", ""]
    writes = {w.path: w for w in plan.writes}
    for s in plan.sections:
        out.append(f"{s.title}  ({_shown(s.path, plan.home)})")
        if s.show_diff:
            w = writes.get(s.path)
            if w is not None and w.changed:
                out.append("  " + ("created" if w.old is None else "updated") + ":")
                out.extend("    " + line for line in _diff(w))
        present = sum(1 for c in s.changes if c.kind == "present")
        for kind in CHANGE_KINDS:
            out.extend(_line(c) for c in s.changes if c.kind == kind)
        if present:
            out.append(f"  present     {present} entr{'y' if present == 1 else 'ies'} already in place")
        for kind in ("wired", "stricter", "found", "gap", "none", "extra"):
            out.extend(_line(c) for c in s.changes if c.kind == kind)
        if not s.changes and not (s.show_diff and writes.get(s.path) and writes[s.path].changed):
            out.append("  up to date")
        out.append("")
    out.append(
        f"Summary: {plan.count('added')} added, {plan.count('tightened')} tightened, "
        f"{plan.count('removed')} removed; {plan.count('extra')} extra rules kept; "
        f"{plan.count('gap')} gap(s)."
    )
    out.append(f"Plan id: {plan.id}" if plan.has_changes else "No changes.")
    return "\n".join(out).rstrip() + "\n"


def _line(c: Change) -> str:
    level = f"{c.level:<6}" if c.level else " " * 6
    rule = f"  [{c.rule}]" if c.rule else ""
    note = f"  ({c.note})" if c.note else ""
    return f"  {c.kind:<11} {level} {c.text}{rule}{note}"


def _shown(path: Path, home: Path) -> str:
    """A path inside the home, written relative to it (the plan's header names the home)."""
    try:
        return "<home>/" + str(path.relative_to(home))
    except ValueError:
        return str(path)


def _diff(w: FileWrite) -> list:
    old = [] if w.old is None else w.old.splitlines()
    new = [] if w.new is None else w.new.splitlines()
    return [
        line
        for line in difflib.unified_diff(old, new, lineterm="", n=1)
        if not line.startswith(("---", "+++"))
    ]
