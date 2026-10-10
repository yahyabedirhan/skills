"""The plugins setup area: the `plugins` list in the workstation repo's agents/installs.json, checked
against each harness.

A plugin is a plugin bundle (MCP servers, skills and hooks installed as one unit, such as
`exa@claude-plugins-official`) or a standalone MCP server. Each entry names the harnesses that
should have it:

    {"name": "exa", "kind": "bundle", "source": "exa@claude-plugins-official",
     "harnesses": ["claude-code", "cursor"]}
    {"name": "docs", "kind": "mcp", "server": {"url": "https://..."}, "harnesses": ["cursor"]}
    {"name": "web", "kind": "bundle", "source": "npm:pi-web-access@0.38.0", "harnesses": ["pi"]}

What each harness can take (references/workstation.md, and each harness reference's Plugins section):

- Claude Code: bundles, installed with `claude plugin install`. Standalone MCP servers are a gap:
  checking them means reading ~/.claude.json, which can hold tokens.
- Cursor: bundles by importing Claude Code's enabled plugins, and standalone MCP servers in
  ~/.cursor/mcp.json.
- Pi: bundles as Pi extensions, which Pi delivers through its <agent-dir>/settings.json `packages`
  setting, and standalone MCP servers in <agent-dir>/mcp.json. A Pi bundle's `source` is a Pi
  extension source (`npm:...`, `git:...` or an https git URL), so its entry names only `pi`; Claude
  Code's `<plugin>@<marketplace>` can't reach Pi.
- Codex: local marketplace bundles and standalone MCP servers, with declared MCP tool policies.
- opencode: a gap for now.

`check` inspects files and read-only CLI metadata; the agent installs and writes, as SKILL.md says.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

from .personal import PersonalError, read_pointer
from . import codex_plugins

INSTALLS = Path("agents/installs.json")
KINDS = ("bundle", "mcp")
KEYS = {"name", "kind", "source", "marketplace", "server", "harnesses", "os", "codex_mcp"}
LABELS = {"claude-code": "Claude Code", "cursor": "Cursor", "codex": "Codex", "opencode": "opencode", "pi": "Pi"}
OSES = {"macos": "darwin", "linux": "linux"}
SOURCE = re.compile(r"^[A-Za-z0-9_.-]+@[A-Za-z0-9_.-]+$")
MARKETPLACE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
NPM_SPEC = re.compile(r"^(@?[^@]+(?:/[^@]+)?)(?:@(.+))?$")  # Pi's parseNpmSpec
NPM_NAME = re.compile(r"^(@[A-Za-z0-9_.~-]+/)?[A-Za-z0-9_.~-]+$")
PI_SERVER = re.compile(r"^[A-Za-z0-9_-]+$")
PI_SOURCE_FORMS = "npm:<name>[@<version>], git:<host>/<owner>/<repo>[@<ref>] or https://<host>/<owner>/<repo>[@<ref>]"


class PluginsError(ValueError):
    pass


def check(home: Path, pi_dir: Path | None = None, codex_home: Path | None = None, codex: str | None = None) -> list:
    """(status, text) lines for the plugins list; none when there is no list to check.

    pi_dir is Pi's agent folder, as verify.py resolves it; home/.pi/agent when not given."""
    try:
        pointer = read_pointer(home)
    except PersonalError:
        return []
    if not pointer.repository:
        return []
    path = pointer.clone / INSTALLS
    try:
        entries = load(path)
    except PluginsError as exc:
        return [("FAIL", str(exc))]
    if not entries:
        return []
    claude = _claude_plugins(home)
    pi = _Pi(pi_dir or home / ".pi/agent")
    codex_state = codex_plugins.Codex(codex_home or home / ".codex", codex)
    lines = []
    for entry in entries:
        name, kind = entry["name"], entry["kind"]
        tag = f"{name} ({kind})"
        oses = entry.get("os")
        if oses and not any(OSES[o] == _platform() for o in oses):
            lines.append(("n/a", f"{name}: for {', '.join(oses)} only"))
            continue
        for harness in entry["harnesses"]:
            label = LABELS[harness]
            if harness == "claude-code":
                lines.append(_claude_code(home, tag, entry, claude))
            elif harness == "cursor":
                lines.append(_cursor(home, tag, entry, claude))
            elif harness == "codex":
                lines.extend(codex_state.check(tag, entry))
            elif harness == "pi":
                lines.append(pi.check(tag, entry))
            else:
                lines.append(("gap", f"{label}: {tag} is listed, but set-up-machine can't deliver plugins to "
                                     f"{label} yet"))
    for source in sorted(s for s, on in claude.items() if on):
        if not any(e["kind"] == "bundle" and e["source"] == source for e in entries):
            lines.append(("extra", f"Claude Code: {source} is enabled but not in the plugins list; "
                                   "Cursor imports it too"))
    if pi.folder.is_dir() and pi.error is None:
        listed = {pi_identity(e["source"]) for e in entries if e["kind"] == "bundle" and "pi" in e["harnesses"]}
        for source in pi.extensions:
            if pi_identity(source) not in listed:
                lines.append(("extra", f"Pi: {source} is an extension in {pi.settings_path} but not in the "
                                       "plugins list"))
    return lines


def load(path: Path) -> list:
    """The `plugins` entries of an installs.json, checked; [] when the file or the list is absent."""
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError) as exc:
        raise PluginsError(f"{path} isn't valid JSON: {exc}") from None
    entries = data.get("plugins", []) if isinstance(data, dict) else None
    if not isinstance(entries, list):
        raise PluginsError(f"{path}: `plugins` must be a list")
    seen = set()
    pi_extensions = {}
    for i, entry in enumerate(entries):
        where = f"{path}: plugins[{i}]"
        if not isinstance(entry, dict):
            raise PluginsError(f"{where} must be an object")
        for key in entry:
            if key not in KEYS:
                raise PluginsError(f"{where}: unknown key {key!r}")
        name = entry.get("name")
        if not isinstance(name, str) or not name:
            raise PluginsError(f"{where}: name is required")
        if name in seen:
            raise PluginsError(f"{where}: name {name!r} is used twice")
        seen.add(name)
        kind = entry.get("kind")
        if kind not in KINDS:
            raise PluginsError(f"{where}: kind must be bundle or mcp")
        harnesses = entry.get("harnesses")
        if not isinstance(harnesses, list) or not harnesses:
            raise PluginsError(f"{where}: harnesses can't be empty")
        for h in harnesses:
            if h not in LABELS:
                raise PluginsError(f"{where}: unknown harness {h!r}")
        if kind == "bundle":
            if "server" in entry:
                raise PluginsError(f"{where}: a bundle takes no server")
            source = entry.get("source") if isinstance(entry.get("source"), str) else ""
            identity = pi_identity(source)
            if SOURCE.match(source) and "pi" in harnesses:
                raise PluginsError(f"{where}: Pi takes a bundle only by its Pi extension source; give Pi its own entry")
            if identity is not None and harnesses != ["pi"]:
                raise PluginsError(f"{where}: a Pi extension source fits only an entry whose only harness is pi; "
                                   "give the other harnesses their own entry")
            if harnesses == ["pi"]:
                # A Pi bundle is a Pi extension, named the way Pi's settings.json `packages` names it.
                if identity is None:
                    raise PluginsError(f"{where}: source must be a Pi extension source: {PI_SOURCE_FORMS}")
                if "marketplace" in entry:
                    raise PluginsError(f"{where}: a Pi extension takes no marketplace")
                if identity in pi_extensions:
                    raise PluginsError(f"{where}: names the same Pi extension as plugins[{pi_extensions[identity]}]")
                pi_extensions[identity] = i
            else:
                if not SOURCE.match(source):
                    raise PluginsError(f"{where}: source must be <plugin>@<marketplace>")
                market = entry.get("marketplace")
                if market is not None and (not isinstance(market, str) or not MARKETPLACE.match(market)):
                    raise PluginsError(f"{where}: marketplace must be <owner>/<repo>")
        else:
            server = entry.get("server")
            if not isinstance(server, dict) or not (isinstance(server.get("url"), str)
                                                    or isinstance(server.get("command"), str)):
                raise PluginsError(f"{where}: server needs url or command")
            if "source" in entry or "marketplace" in entry:
                raise PluginsError(f"{where}: an mcp entry takes server, not source or marketplace")
            if "pi" in harnesses and not PI_SERVER.match(name):
                raise PluginsError(f"{where}: Pi takes server names of letters, digits, _ and -")
        try:
            codex_plugins.validate(entry, where)
        except codex_plugins.PluginError as exc:
            raise PluginsError(str(exc)) from None
        oses = entry.get("os")
        if oses is not None and (not isinstance(oses, list) or any(o not in OSES for o in oses)):
            raise PluginsError(f"{where}: os takes macos and linux")
    return entries


def cursor_server_name(source: str, server: str) -> str:
    """The name Cursor gives an MCP server of a Claude Code plugin it imports."""
    return f"plugin-{source.split('@', 1)[0]}-{server}"


def pi_identity(source: str):
    """The extension a Pi extension source names, as Pi 1.1.0 identifies it, or None for another form.

    Pi treats two sources with one identity as the same extension: an npm source by its name, a git
    source by host and repository path without the ref (core/package-manager.js, getPackageIdentity).
    Local paths aren't taken, since one path doesn't name the same extension on every machine."""
    if source.startswith("npm:"):
        match = NPM_SPEC.match(source[4:].strip())
        return f"npm:{match.group(1)}" if match and NPM_NAME.match(match.group(1)) else None
    git = _git_source(source)
    return f"git:{git[0]}/{git[1]}" if git else None


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


class _Pi:
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
            source = item.get("source") if isinstance(item, dict) else item  # the object form filters resources
            if isinstance(source, str):
                self.extensions.append(source)
        builtins = settings.get("extensions", [])  # the setting that can turn off builtin:mcp
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
            stale = self._stale_checkout(source)
            if stale:
                return ("FAIL", f"Pi: {tag} {source} is an extension in {self.settings_path}, but its checkout at "
                                f"{stale[0]} isn't at {stale[1]}; run `pi update {source}`")
            return ("ok", f"Pi: {tag} {source} is an extension in {self.settings_path}")
        other = [p for p in self.extensions if pi_identity(p) == pi_identity(source)]
        if other:
            return ("FAIL", f"Pi: {tag} {self.settings_path} has {other[0]} instead of {source}")
        return ("FAIL", f"Pi: {tag} {source} isn't an extension in {self.settings_path}")

    def _stale_checkout(self, source: str):
        """(checkout, ref) when Pi's checkout of a pinned git extension is at another commit; else None.

        At startup Pi installs only a missing git extension and leaves an existing checkout where it is,
        so a changed ref needs `pi update <source>`, which fetches the ref and resets to FETCH_HEAD. An npm
        extension needs no check: Pi reinstalls one whose version doesn't match at startup."""
        git = _git_source(source)
        if not git or not git[2]:
            return None
        folder = self.folder / "git" / git[0] / git[1]
        head = _rev(folder, "HEAD")
        if not head:
            return None  # not installed yet, or unreadable: a new session installs a missing one
        ref = git[2]
        target = None
        try:
            for record in (folder / ".git/FETCH_HEAD").read_text().splitlines():
                sha, _, note = record.partition("\t")
                if f"'{ref}'" in note:
                    target = _rev(folder, f"{sha}^{{commit}}")
                    break
        except OSError:
            pass
        target = target or _rev(folder, f"{ref}^{{commit}}")
        return None if target == head else (folder, ref)

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


def _rev(folder: Path, name: str):
    """The commit a name resolves to in a git checkout, read-only; None when it doesn't resolve."""
    if not (folder / ".git").exists():
        return None
    try:
        done = subprocess.run(["git", "-C", str(folder), "rev-parse", "--verify", "--quiet", name],
                              capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return done.stdout.strip() or None if done.returncode == 0 else None


def _claude_code(home: Path, tag: str, entry: dict, claude: dict):
    if not (home / ".claude").is_dir():
        return ("n/a", f"Claude Code: {tag} isn't checked; Claude Code is not set up here")
    if entry["kind"] == "mcp":
        return ("gap", f"Claude Code: {tag} is listed, but set-up-machine can't check a standalone MCP server "
                       "there yet; use a bundle")
    source = entry["source"]
    if source not in claude:
        return ("FAIL", f"Claude Code: {tag} {source} isn't installed")
    if not claude[source]:
        return ("FAIL", f"Claude Code: {tag} {source} isn't enabled in ~/.claude/settings.json")
    return ("ok", f"Claude Code: {tag} {source} is installed and enabled")


def _cursor(home: Path, tag: str, entry: dict, claude: dict):
    folder = home / ".cursor"
    if not folder.is_dir():
        return ("n/a", f"Cursor: {tag} isn't checked; Cursor is not set up here")
    if entry["kind"] == "bundle":
        source = entry["source"]
        if not claude.get(source):
            return ("FAIL", f"Cursor: {tag} needs {source} installed and enabled in Claude Code, since Cursor "
                            "imports bundles only from Claude Code")
        names = [cursor_server_name(source, s) for s in _bundle_servers(home, source)]
        how = f"as {', '.join(names)}" if names else "(skills only; no MCP server)"
        return ("ok", f"Cursor: {tag} is imported from Claude Code {how}")
    path = folder / "mcp.json"
    try:
        servers = json.loads(path.read_text()).get("mcpServers", {}) if path.is_file() else {}
    except (OSError, ValueError, AttributeError):
        return ("FAIL", f"Cursor: {tag} can't be checked; {path} isn't valid JSON")
    if entry["name"] not in servers:
        return ("FAIL", f"Cursor: {tag} has no entry in {path}")
    if servers[entry["name"]] != entry["server"]:
        return ("FAIL", f"Cursor: {tag} entry in {path} differs from installs.json")
    return ("ok", f"Cursor: {tag} is in {path}")


def _claude_plugins(home: Path) -> dict:
    """Each plugin Claude Code installed, as `<plugin>@<marketplace>` -> whether it is enabled."""
    try:
        installed = json.loads((home / ".claude/plugins/installed_plugins.json").read_text()).get("plugins", {})
    except (OSError, ValueError, AttributeError):
        installed = {}
    try:
        enabled = json.loads((home / ".claude/settings.json").read_text()).get("enabledPlugins", {})
    except (OSError, ValueError, AttributeError):
        enabled = {}
    return {source: enabled.get(source) is True for source in installed}


def _bundle_servers(home: Path, source: str) -> list:
    """The MCP server names a Claude Code plugin declares, from its install folder's mcp.json or .mcp.json."""
    try:
        records = json.loads((home / ".claude/plugins/installed_plugins.json").read_text())["plugins"][source]
        folder = Path(records[0]["installPath"])
    except (OSError, ValueError, KeyError, IndexError, TypeError):
        return []
    for name in (".mcp.json", "mcp.json"):
        try:
            data = json.loads((folder / name).read_text())
        except (OSError, ValueError):
            continue
        servers = data.get("mcpServers", data) if isinstance(data, dict) else {}
        return sorted(k for k, v in servers.items() if isinstance(v, dict))
    return []


def _platform() -> str:
    return "darwin" if sys.platform == "darwin" else "linux" if sys.platform.startswith("linux") else sys.platform
