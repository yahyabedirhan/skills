"""Pi plugin adapter: validate, check and propose. It never writes.

A bundle is a Pi extension in settings.json `packages`. A standalone server is an
mcp.json entry. This adapter does not compare a git checkout with a pinned ref.
"""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

from . import policy
from .errors import PluginsError

SOURCE = re.compile(r"^[A-Za-z0-9_.-]+@[A-Za-z0-9_.-]+$")
NPM_SPEC = re.compile(r"^(@?[^@]+(?:/[^@]+)?)(?:@(.+))?$")  # Pi's parseNpmSpec
NPM_NAME = re.compile(r"^(@[A-Za-z0-9_.~-]+/)?[A-Za-z0-9_.~-]+$")
PI_SERVER = re.compile(r"^[A-Za-z0-9_-]+$")
PI_SOURCE_FORMS = "npm:<name>[@<version>], git:<host>/<owner>/<repo>[@<ref>] or https://<host>/<owner>/<repo>[@<ref>]"


def validate(entry: dict, where: str, seen: dict | None = None, index: int = 0):
    """Pi's source and server rules. `seen` maps an extension identity to the earlier index."""
    policy.validate(entry, where)
    seen = {} if seen is None else seen
    harnesses = entry["harnesses"]
    if entry["kind"] == "bundle":
        source = entry.get("source") if isinstance(entry.get("source"), str) else ""
        ident = identity(source)
        if SOURCE.match(source) and "pi" in harnesses:
            raise PluginsError(f"{where}: Pi takes a bundle only by its Pi extension source; give Pi its own entry")
        if ident is not None and harnesses != ["pi"]:
            raise PluginsError(f"{where}: a Pi extension source fits only an entry whose only harness is pi; "
                               "give the other harnesses their own entry")
        if harnesses == ["pi"]:
            if ident is None:
                raise PluginsError(f"{where}: source must be a Pi extension source: {PI_SOURCE_FORMS}")
            if "marketplace" in entry:
                raise PluginsError(f"{where}: a Pi extension takes no marketplace")
            if ident in seen:
                raise PluginsError(f"{where}: names the same Pi extension as plugins[{seen[ident]}]")
            seen[ident] = index
        return
    if "pi" in harnesses and not PI_SERVER.match(entry["name"]):
        raise PluginsError(f"{where}: Pi takes server names of letters, digits, _ and -")


def identity(source: str):
    """The extension a Pi extension source names, as Pi 1.1.0 identifies it, or None for another form.

    Pi treats two sources with one identity as the same extension: an npm source by its name, a git
    source by host and repository path without the ref (core/package-manager.js, getPackageIdentity).
    Local paths aren't taken, since one path doesn't name the same extension on every machine."""
    if not isinstance(source, str):
        return None
    if source.startswith("npm:"):
        match = NPM_SPEC.match(source[4:].strip())
        return f"npm:{match.group(1)}" if match and NPM_NAME.match(match.group(1)) else None
    git = _git_source(source)
    return f"git:{git[0]}/{git[1]}" if git else None


def check(ctx, tag: str, entry: dict) -> list:
    return [State(ctx.pi_dir).check(tag, entry)]


def propose(settings: dict, mcp: dict, entry: dict, rules=()) -> tuple:
    """(settings, mcp.json) with this entry merged. Other keys stay. It never writes."""
    validate(entry, "plugin")
    settings = copy.deepcopy(settings or {})
    mcp = copy.deepcopy(mcp or {})
    if entry["kind"] == "bundle":
        packages = settings.setdefault("packages", [])
        if not isinstance(packages, list):
            raise PluginsError("packages must be a list; preserve it for guided review")
        source = entry["source"]
        ident = identity(source)
        replaced = False
        for i, item in enumerate(packages):
            current = item.get("source") if isinstance(item, dict) else item
            if current == source or identity(current) == ident:
                if isinstance(item, dict):
                    item = dict(item)
                    item["source"] = source
                    packages[i] = item
                else:
                    packages[i] = source
                replaced = True
                break
        if not replaced:
            packages.append(source)
        return settings, mcp
    servers = mcp.setdefault("mcpServers", {})
    if not isinstance(servers, dict):
        raise PluginsError("mcpServers must be an object; preserve it for guided review")
    servers[entry["name"]] = dict(entry["server"])
    return settings, mcp


def extras(ctx, entries: list) -> list:
    """`extra` lines for extensions configured in Pi that the plugins list leaves out."""
    state = State(ctx.pi_dir)
    if not state.folder.is_dir() or state.error is not None:
        return []
    listed = {identity(e["source"]) for e in entries if e["kind"] == "bundle" and "pi" in e["harnesses"]}
    lines = []
    for source in state.extensions:
        if identity(source) not in listed:
            lines.append(("extra", f"Pi: {source} is an extension in {state.settings_path} but not in the plugins list"))
    return lines


class State:
    """Pi's agent folder: the extensions in its settings.json `packages` and the servers in its mcp.json."""

    def __init__(self, folder: Path):
        self.folder = folder
        self.settings_path = folder / "settings.json"
        self.error = None
        self.extensions, self.builtins = [], []
        try:
            settings = json.loads(self.settings_path.read_text()) if self.settings_path.exists() else {}
        except (OSError, UnicodeError, ValueError):
            self.error = f"{self.settings_path} isn't valid JSON"
            return
        if not isinstance(settings, dict) or not isinstance(settings.get("packages", []), list):
            self.error = f"{self.settings_path} has no list in packages"
            return
        for item in settings.get("packages", []):
            source = item.get("source") if isinstance(item, dict) else item
            if isinstance(source, str):
                self.extensions.append(source)
        builtins = settings.get("extensions", [])
        self.builtins = builtins if isinstance(builtins, list) else []

    def check(self, tag: str, entry: dict):
        if not self.folder.is_dir():
            return ("n/a", f"Pi: {tag} isn't checked; Pi is not set up here")
        if entry["kind"] == "bundle":
            return self._extension(tag, entry["source"])
        return self._server(tag, entry)

    def _extension(self, tag: str, source: str):
        if self.error:
            return ("FAIL", f"Pi: {tag} can't be checked; {self.error}")
        if source in self.extensions:
            return ("ok", f"Pi: {tag} {source} is an extension in {self.settings_path}; "
                          "declaration matches, installed code and latest release are unverified")
        other = [item for item in self.extensions if identity(item) == identity(source)]
        if other:
            return ("FAIL", f"Pi: {tag} {self.settings_path} has {other[0]} instead of {source}")
        return ("FAIL", f"Pi: {tag} {source} isn't an extension in {self.settings_path}")

    def _server(self, tag: str, entry: dict):
        path = self.folder / "mcp.json"
        try:
            servers = json.loads(path.read_text()).get("mcpServers", {}) if path.is_file() else {}
        except (OSError, UnicodeError, ValueError, AttributeError):
            return ("FAIL", f"Pi: {tag} can't be checked; {path} isn't valid JSON")
        if not isinstance(servers, dict) or entry["name"] not in servers:
            return ("FAIL", f"Pi: {tag} has no entry in {path}")
        if servers[entry["name"]] != entry["server"]:
            return ("FAIL", f"Pi: {tag} entry in {path} differs from installs.json")
        if "-builtin:mcp" in self.builtins:
            return ("gap", f"Pi: {tag} is in {path}, but -builtin:mcp in {self.settings_path} turns off Pi's "
                           "built-in MCP, which reads that file")
        return ("ok", f"Pi: {tag} is in {path}")


def _git_source(source: str):
    """(host, repository path, ref or None) of a Pi git source, or None for another form."""
    if source.startswith("git:"):
        url = source[4:].strip()
    elif source.startswith("https://"):
        url = source
    else:
        return None
    if "://" in url:
        parts = urlsplit(url)
        host, path = parts.hostname or "", parts.path
    elif url.startswith("git@") and ":" in url:
        host, path = url[4:].split(":", 1)
    else:
        host, _, path = url.partition("/")
    path, _, ref = path.lstrip("/").partition("@")
    path = path[:-4] if path.endswith(".git") else path
    segments = path.split("/")
    if not host or "." not in host or len(segments) < 2 or not all(segments) or ".." in segments:
        return None
    return host.lower(), path, ref or None
