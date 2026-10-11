"""Read-only audit of Pi's agent folder: the instructions link, declared defaults and skill links.

The agent folder is PI_CODING_AGENT_DIR, else ~/.pi/agent; verify.py resolves it. The
workstation repo, found through the pointer, can point at a Pi config from its harnesses file
(layout.py). That config declares Pi settings keys; only those keys are compared with
<agent-dir>/settings.json, and their values are never printed. A `packages` key
there is a gap: Pi extensions belong in the plugins list (plugins.py). auth.json, trust.json and
sessions are never read. references/pi.md is the layout.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from . import layout, personal

DEFAULT_DIR = Path(".pi/agent")
PLUGIN_KEYS = ("packages",)  # Pi extensions come from the plugins list in the installs file, not the Pi config


class ConfigError(ValueError):
    pass


def load(home: Path) -> tuple:
    """(the declared Pi settings, the source's path relative to the repo), or ({}, None) with no source.

    No source when there is no workstation repo or the layout points at no Pi config.
    """
    try:
        pointer = personal.read_pointer(home)
    except personal.PersonalError:
        return {}, None  # personal.check reports a missing or malformed pointer
    if not pointer.repository:
        return {}, None
    try:
        path = layout.harness_file(pointer.clone, "pi", "config")
    except layout.LayoutError as exc:
        raise ConfigError(str(exc)) from None
    if path is None:
        return {}, None
    try:
        data = json.loads(path.read_text())
    except (OSError, UnicodeError, ValueError):
        raise ConfigError(f"{path} isn't valid JSON") from None
    if not isinstance(data, dict):
        raise ConfigError(f"{path} must be a JSON object of Pi settings keys")
    return data, path.relative_to(pointer.clone).as_posix()


def audit(home: Path, folder: Path) -> list:
    """(status, text) lines for Pi; one `none` line when the agent folder doesn't exist."""
    if not folder.is_dir():
        return [("none", f"Pi: not set up here (no {folder})")]
    return instructions(home, folder) + skill_links(folder) + defaults(home, folder)


def instructions(home: Path, folder: Path) -> list:
    shared = home / personal.SHARED
    link = folder / "AGENTS.md"
    out = []
    override = folder / "AGENTS.override.md"
    if override.exists():
        out.append(("gap", f"Pi: {override} exists, and Pi reads it instead of the shared file"))
    if link.is_symlink() and not link.exists():
        out.append(("FAIL", f"Pi: {link} is a broken link; link it to the shared file: {os.path.relpath(shared, folder)}"))
    elif link.is_symlink() and link.resolve() == shared.resolve():
        out.append(("ok", f"Pi: {link} -> {shared}"))
    elif link.exists():
        out.append(("gap", f"Pi: {link} isn't a link to the shared file; Pi reads it instead until its lines "
                           "move into the shared file"))
    else:
        out.append(("FAIL", f"Pi: no {link}; link it to the shared file: {os.path.relpath(shared, folder)}"))
    return out


def skill_links(folder: Path) -> list:
    skills = folder / "skills"
    if not skills.is_dir():
        return []
    return [("extra", f"Pi: {entry} is a broken link; remove it")
            for entry in sorted(skills.iterdir()) if entry.is_symlink() and not entry.exists()]


def defaults(home: Path, folder: Path) -> list:
    try:
        declared, source = load(home)
    except ConfigError as exc:
        return [("FAIL", str(exc))]
    if source is None:
        return [("none", f"Pi: no declared defaults ({layout.HARNESSES} in the workstation repo points at no Pi config)")]
    if not declared:
        return [("none", f"Pi: no declared defaults ({source} declares no keys)")]
    path = folder / "settings.json"
    try:
        settings = json.loads(path.read_text()) if path.exists() else {}  # read_text follows a symlink
    except (OSError, UnicodeError, ValueError):
        return [("FAIL", f"Pi: {path} isn't valid JSON")]
    if not isinstance(settings, dict):
        return [("FAIL", f"Pi: {path} isn't a JSON object")]
    out = []
    for key, value in declared.items():
        if key in PLUGIN_KEYS:
            out.append(("gap", f"Pi: {source} declares {key}; Pi extensions belong in the plugins list, so move "
                               f"each one into `plugins` in {layout.INSTALLS} (references/pi.md, Plugins)"))
        elif key in settings and type(settings[key]) is type(value) and settings[key] == value:
            out.append(("same", f"Pi: {key} in {path} matches {source}"))
        else:
            out.append(("FAIL", f"Pi: {key} in {path} is missing or differs from {source}"))
    return out
