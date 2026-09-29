"""Harness memory: every memory feature stays off and no memory file stays behind.

Adapters for harnesses with a memory feature turn it off in their own settings
and call `remove_files` for the folders the feature writes. `report_without_memory`
names the harnesses that have no memory feature, until each gets an adapter of
its own that says so itself. See references/global-instructions.md for why.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from .plan import Change, FileWrite, Section

# Harnesses without a memory feature (docs/research/harness-capabilities.md, "Memory").
WITHOUT_MEMORY = {}  # every covered harness now says so in its own adapter


def fingerprint(path: Path) -> str:
    """Stands in for a file's text in the plan, so a memory file that changes after the plan is caught."""
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def remove_files(home: Path, folders: list, section: Section) -> list:
    """A deletion per file under the given memory folders, each shown in the plan.

    Apply copies each file into the backup folder before deleting it.
    """
    writes = []
    for folder in folders:
        for path in sorted(p for p in folder.rglob("*") if p.is_file()):
            section.changes.append(Change("removed", _shown(path, home), note="memory file; kept in the backup"))
            writes.append(FileWrite(path, fingerprint(path), None))
    return writes


def report_without_memory(home: Path) -> list:
    sections = []
    for label, (folder, text) in WITHOUT_MEMORY.items():
        section = Section(f"{label}: memory", home / folder)
        section.changes.append(Change("none", text))
        sections.append(section)
    return sections


def _shown(path: Path, home: Path) -> str:
    try:
        return "<home>/" + str(path.relative_to(home))
    except ValueError:
        return str(path)
