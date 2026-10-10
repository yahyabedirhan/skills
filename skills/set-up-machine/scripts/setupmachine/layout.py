"""The workstation repo's layout: the one place that names its folder and its harnesses file.

set-up-machine reads only `setup/` in the workstation repo. The folder holds the global
sources in full (`instructions.md`, `permissions.json`, `installs.json`) and an optional
harnesses file, `harnesses.json`, that points at each harness's own files, wherever they sit
in the repo:

    {"version": 1,
     "harnesses": {"cursor": {"instructions": "harnesses/cursor/instructions.md"},
                   "codex": {"config": "harnesses/codex-cli/config/config.toml"}}}

Paths are relative to the repo's root. A harness with nothing to point at has no entry, and
without the file no harness has instructions or a config of its own. Every reader asks this
module for a path; none names the folder or the file itself. references/workstation.md is the
layout for agents.
"""
from __future__ import annotations

import json
from pathlib import Path

FOLDER = Path("setup")
INSTRUCTIONS = FOLDER / "instructions.md"
PERMISSIONS = FOLDER / "permissions.json"
INSTALLS = FOLDER / "installs.json"
HARNESSES = FOLDER / "harnesses.json"
HARNESS_LABELS = {"claude-code": "Claude Code", "cursor": "Cursor", "codex": "Codex", "opencode": "opencode", "pi": "Pi"}
HARNESS_NAMES = tuple(sorted(HARNESS_LABELS))
KINDS = ("instructions", "config")
KEYS = ("version", "harnesses")


class LayoutError(ValueError):
    pass


def instructions(clone: Path) -> Path:
    return clone / INSTRUCTIONS


def permissions(clone: Path) -> Path:
    return clone / PERMISSIONS


def installs(clone: Path) -> Path:
    return clone / INSTALLS


def harness_file(clone: Path, harness: str, kind: str) -> Path | None:
    """The file `harnesses.json` points at for one harness, or None when it points at none.

    A malformed harnesses file, or a pointer to a file that doesn't exist, raises LayoutError.
    """
    path = harness_files(clone).get(harness, {}).get(kind)
    if path is not None and not path.is_file():
        problem = "which isn't a file" if path.exists() else "which doesn't exist"
        raise LayoutError(f"{clone / HARNESSES}: `harnesses.{harness}.{kind}` points at {path}, "
                          f"{problem}; fix the path or add the file")
    return path


def harness_files(clone: Path) -> dict:
    """{harness: {kind: absolute path}} from `harnesses.json`, checked; {} without the file.

    The paths are not checked for existence here; harness_file does that for the one it returns.
    """
    path = clone / HARNESSES
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
    except (OSError, UnicodeError, ValueError):
        raise LayoutError(f"{path} isn't valid JSON") from None
    if not isinstance(data, dict):
        raise LayoutError(f"{path} must be a JSON object with `version` and `harnesses`")
    for key in data:
        if key not in KEYS:
            raise LayoutError(f"{path}: unknown key {key!r}; it takes {', '.join(KEYS)}")
    if "version" not in data:
        raise LayoutError(f"{path} has no `version`; add \"version\": 1")
    if type(data["version"]) is not int or data["version"] != 1:
        raise LayoutError(f"{path}: unsupported version {data['version']!r}; it takes 1")
    harnesses = data.get("harnesses", {})
    if not isinstance(harnesses, dict):
        raise LayoutError(f"{path}: `harnesses` must be an object of harness names")
    root = clone.resolve()
    files = {}
    for harness, entry in harnesses.items():
        if harness not in HARNESS_NAMES:
            raise LayoutError(f"{path}: unknown harness {harness!r}; it takes {', '.join(HARNESS_NAMES)}")
        if not isinstance(entry, dict) or not entry:
            raise LayoutError(f"{path}: `harnesses.{harness}` must be an object with instructions, config or both")
        files[harness] = {}
        for kind, value in entry.items():
            where = f"`harnesses.{harness}.{kind}`"
            if kind not in KINDS:
                raise LayoutError(f"{path}: unknown key {where}; a harness takes {', '.join(KINDS)}")
            if not isinstance(value, str) or not value.strip():
                raise LayoutError(f"{path}: {where} must be a path relative to the repo's root")
            target = clone / value
            # resolve() follows `..` and links, so a path that leaves the clone either way is refused.
            if not target.resolve().is_relative_to(root):
                raise LayoutError(f"{path}: {where} is `{value}`, outside the repo; "
                                  "give a path relative to the repo's root")
            files[harness][kind] = target
    return files
