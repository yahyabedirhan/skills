"""Read-only Codex preference audit and a pure proposal seam for fixture verification.

Only agents/codex.toml is a preference source. Proposals never write config or
inspect profiles, project settings, managed requirements, authentication or state.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

from . import personal

try:
    import tomllib
except ImportError:
    tomllib = None

SOURCE = Path("agents/codex.toml")
VALUES = {
    "sandbox_mode": ("read-only", "workspace-write", "danger-full-access"),
    "approval_policy": ("on-request", "never"),
    "approvals_reviewer": ("user", "auto_review"),
}


class ConfigError(ValueError):
    pass


def parse(text: str) -> dict:
    if tomllib is None:
        raise ConfigError("TOML audit requires Python 3.11+; existing rule and hook checks remain available")
    try:
        return tomllib.loads(text)
    except ValueError:
        # Parser diagnostics can quote an unrelated value. Do not echo config contents.
        raise ConfigError("invalid TOML; fix the configuration before proposing changes") from None


def validate(preferences: dict) -> dict:
    if set(preferences) - set(VALUES):
        raise ConfigError("unsupported preference key or table; source allows only sandbox_mode, approval_policy and approvals_reviewer")
    for key, value in preferences.items():
        if not isinstance(value, str) or value not in VALUES[key]:
            raise ConfigError(f"unsupported {key} value; supported source values: {', '.join(VALUES[key])}; granular and deprecated policies require guided review")
    return preferences


def load(home: Path) -> dict:
    try:
        pointer = personal.read_pointer(home)
    except personal.PersonalError:
        return {}  # personal.check reports missing or malformed pointers
    if not pointer.repository:
        return {}
    path = pointer.clone / SOURCE
    if not path.exists():
        return {}
    try:
        return validate(parse(path.read_text()))
    except (OSError, UnicodeError):
        raise ConfigError("cannot read agents/codex.toml as UTF-8 text") from None


def conflict(config: dict, preferences: dict) -> str | None:
    if "profiles" in config:
        return "legacy inline profiles require guided review; preserve them rather than guessing their constraints"
    if "default_permissions" in config and "sandbox_mode" in preferences:
        return "default_permissions conflicts with sandbox_mode; preserve it and resolve permissions through guided review"
    if "default_permissions" in config and ("sandbox_mode" in config or "sandbox_workspace_write" in config):
        return "default_permissions coexists with legacy sandbox configuration; preserve it and resolve the conflict"
    current, wanted = config.get("sandbox_mode"), preferences.get("sandbox_mode")
    if current in VALUES["sandbox_mode"] and wanted in VALUES["sandbox_mode"]:
        if VALUES["sandbox_mode"].index(current) < VALUES["sandbox_mode"].index(wanted):
            return "existing sandbox_mode is stricter; preserve it and review the declared preference"
    if "approval_policy" in preferences and isinstance(config.get("approval_policy"), dict):
        return "existing granular approval_policy requires guided review; preserve its constraints"
    return None


def propose(text: str, preferences: dict) -> str:
    """Return a root-key-only proposal, preserving all unowned text byte for byte.

    An unfamiliar assignment form is a guided edit, never a lossy TOML rewrite.
    This seam exercises the inspect/diff/apply outcome in synthetic homes only.
    """
    validate(preferences)
    config = parse(text)
    problem = conflict(config, preferences)
    if problem:
        raise ConfigError(problem)
    changed = {key: value for key, value in preferences.items() if config.get(key) != value}
    if not changed:
        return text
    lines = text.splitlines(keepends=True)
    # Multiline strings can contain apparent table headings/assignments. Leave
    # this uncommon form to the guided diff rather than guessing their spans.
    if '"""' in text or "'''" in text:
        raise ConfigError("multiline TOML strings require a guided root-key edit; preserve unrelated text")
    boundary = next((i for i, line in enumerate(lines) if line.lstrip().startswith("[")), len(lines))
    newline = "\r\n" if "\r\n" in text else "\n"
    additions = []
    for key, value in changed.items():
        matches = [(i, re.fullmatch(rf'(\s*{key}\s*=\s*)("[^"\r\n]*"|\'[^\'\r\n]*\')(\s*(?:#[^\r\n]*)?)(\r?\n)?', line))
                   for i, line in enumerate(lines[:boundary])]
        matches = [(i, match) for i, match in matches if match]
        if key in config:
            if len(matches) != 1:
                raise ConfigError(f"existing {key} assignment requires a guided edit; preserve its syntax")
            i, match = matches[0]
            lines[i] = match[1] + json.dumps(value) + match[3] + (match[4] or "")
        else:
            additions.append(f"{key} = {json.dumps(value)}{newline}")
    if additions:
        if boundary and not lines[boundary - 1].endswith(("\n", "\r")):
            additions.insert(0, newline)
        lines[boundary:boundary] = additions
    proposal = "".join(lines)
    result = parse(proposal)
    if result != {**config, **preferences}:
        raise ConfigError("proposal could not preserve the parsed configuration; use a guided edit")
    return proposal


def support(preferences: dict, codex: str | None) -> list:
    """Probe the installed parser in a synthetic home, with negative controls.

    features list loads configuration without a model call or authenticated state.
    A successful candidate alone is insufficient: some versions ignore unknown keys.
    """
    if not codex:
        return [("gap", "installed CLI preference support unverified; Codex parser probe was skipped")]
    try:
        with tempfile.TemporaryDirectory(prefix="codex-config-support-") as tmp:
            folder = Path(tmp) / "codex"
            folder.mkdir()
            path = folder / "config.toml"
            def probe(values):
                path.write_text("".join(f"{key} = {json.dumps(value)}\n" for key, value in values.items()))
                return subprocess.run([codex, "features", "list"], cwd=tmp,
                                      env={"HOME": tmp, "CODEX_HOME": str(folder), "PATH": os.defpath},
                                      capture_output=True, text=True, timeout=15)
            for key in preferences:
                negative = probe({key: "set-up-machine-invalid-value"})
                # Require a parsing error naming our sentinel, not a random
                # executable/network failure, to establish recognition.
                recognized = ("failed to load bootstrap configuration" in negative.stderr
                              and "unknown variant `set-up-machine-invalid-value`" in negative.stderr
                              and f"in `{key}`" in negative.stderr)
                if negative.returncode == 0 or not recognized:
                    return [("gap", f"installed CLI recognition of {key} could not be established; do not apply it")]
            if probe(preferences).returncode != 0:
                return [("FAIL", "installed CLI rejected the declared preference combination; preserve configuration")]
            return [("supported", "installed CLI parser recognizes and accepts the declared preference keys and values")]
    except (OSError, subprocess.SubprocessError):
        return [("gap", "installed CLI parser probe failed or timed out; preserve configuration until guided validation")]


def audit(home: Path, folder: Path, codex: str | None = None) -> list:
    try:
        preferences = load(home)
        if not preferences:
            return [("none", "no declared Codex preferences; omitted keys remain user-managed")]
        path = folder / "config.toml"
        config = parse(path.read_text()) if path.exists() else {}
        problem = conflict(config, preferences)
        out = support(preferences, codex)
        if problem:
            out.append(("gap", problem))
        for key, value in preferences.items():
            status = "same" if config.get(key) == value else "FAIL"
            out.append((status, f"persisted {key} {'matches the declared source' if status == 'same' else 'is missing or differs from the declared source'}"))
        if "profile" in config:
            out.append(("gap", "top-level profile is unsupported by current official documentation; preserve it for guided review"))
        if any(folder.glob("*.config.toml")):
            out.append(("override", "separate profile files may override persisted defaults when selected; their contents and selection are unverified"))
        if "profiles" in config:
            out.append(("gap", "legacy inline profiles are unsupported by the inspected CLI; preserve them for guided review"))
        if "projects" in config:
            out.append(("override", "project configuration or trust may override defaults; effective project settings are unverified"))
        out.append(("gap", "managed requirements, CLI/cloud overrides and existing sessions are unverified by this persisted audit; validate through guided setup"))
        return out
    except (ConfigError, OSError, UnicodeError) as exc:
        message = str(exc) if isinstance(exc, ConfigError) else "cannot read Codex config.toml as UTF-8 text"
        return [("gap" if tomllib is None else "FAIL", message)]
