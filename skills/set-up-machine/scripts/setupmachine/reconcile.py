"""Reconcile: what the skill wants against what's on the machine, then apply it."""
from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

from . import shared
from .adapters import ADAPTERS
from .plan import Plan


class PlanMismatch(RuntimeError):
    pass


def build(home: Path, rules: list, os_home: Path) -> Plan:
    manifest = shared.load_manifest(home)
    manifest_old = shared.read_text(shared.manifest_path(home))
    sections, writes = [], []

    section, write = shared.plan_instructions(home, rules)
    sections.append(section)
    writes.append(write)

    owned_after = {}
    for adapter in ADAPTERS:
        a_sections, a_writes, owned = adapter.plan(
            home, rules, manifest["harnesses"].get(adapter.NAME, {}), shared.instructions_path(home), os_home
        )
        sections.extend(a_sections)
        writes.extend(a_writes)
        if owned:
            owned_after[adapter.NAME] = owned

    plan = Plan(home, sections, writes)
    if plan.has_changes or owned_after != manifest["harnesses"]:
        writes.append(shared.manifest_write(home, manifest_old, owned_after))
    return plan


def apply(plan: Plan, approved_id: str) -> Path:
    """Write every changed file, after backing up the ones that exist. Returns the backup folder."""
    if approved_id != plan.id:
        raise PlanMismatch(
            f"the machine changed since plan {approved_id} (it's now {plan.id}); run the plan again and approve the new diff"
        )
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_dir = shared.backups_path(plan.home) / stamp
    for w in plan.writes:
        if not w.changed:
            continue
        if w.old is not None:
            target = backup_dir / w.path.relative_to(plan.home)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(w.path, target)
        # Write through a symlink to its target, so a linked file stays linked.
        target = w.path.resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_name(target.name + ".set-up-machine.tmp")
        tmp.write_text(w.new)
        if w.old is not None:
            shutil.copymode(target, tmp)
        tmp.replace(target)
    return backup_dir
