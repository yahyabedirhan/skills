"""Pi's harness setup. It audits Pi, translates one hook payload, and adapts one plugin entry.

It copies Cursor's operations: `id`, `label`, `present`, `audit`, `read`, `write`, and, because Pi
takes plugins, `validate`, `check`, and `propose`. `audit` returns `(channel, status, text)` for
the hook extension, the instructions link, declared defaults, and broken skill links.
The printed words stay `hook`, `pi`, and `plugin`.

A bundle is a Pi extension in settings.json `packages`. A standalone server is an mcp.json entry.
This adapter does not compare a git checkout with a pinned ref. `declared_defaults` is how the
shared module knows this harness setup already audits a Pi config from the harnesses file.
"""
from __future__ import annotations

import copy
import json
import os
import re
import shlex
from pathlib import Path
from urllib.parse import urlsplit

from .. import layout, personal
from ..harnesses import policy
from ..harnesses.errors import PluginsError
from ..hook import ToolCall, _plain, _search, command_script, refusal

id = "pi"
label = "Pi"
DEFAULT_DIR = Path(".pi/agent")
EXTENSION_HEADER = "// set-up-machine: the pre-tool hook, as a Pi extension."
PLUGIN_KEYS = ("packages",)  # Pi extensions come from the plugins list, not the Pi config
# Pi's built-in tools that take a path: the input field holding it, and the access it means.
FILE_TOOLS = {
    "read": ("path", "read"),
    "edit": ("path", "write"),
    "write": ("path", "write"),
    "grep": ("path", "read"),
    "find": ("path", "read"),
    "ls": ("path", "read"),
}
# Pi's shell tools: the input field `command` holds the command.
SHELL_TOOLS = ("bash", "powershell")
# Without a UI (print and json mode, or a child session started without one) no one can answer.
UNATTENDED = "Pi without a UI"

SOURCE = re.compile(r"^[A-Za-z0-9_.-]+@[A-Za-z0-9_.-]+$")
NPM_SPEC = re.compile(r"^(@?[^@]+(?:/[^@]+)?)(?:@(.+))?$")  # Pi's parseNpmSpec
NPM_NAME = re.compile(r"^(@[A-Za-z0-9_.~-]+/)?[A-Za-z0-9_.~-]+$")
PI_SERVER = re.compile(r"^[A-Za-z0-9_-]+$")
PI_SOURCE_FORMS = "npm:<name>[@<version>], git:<host>/<owner>/<repo>[@<ref>] or https://<host>/<owner>/<repo>[@<ref>]"


class ConfigError(ValueError):
    pass


def present(home: Path) -> bool:
    """Whether Pi is set up on this machine: its agent folder exists.

    On the real home that folder may be `PI_CODING_AGENT_DIR`. A fixture home uses `~/.pi/agent`
    unless the verifier passes the folder it resolved.
    """
    return _agent_dir(home).is_dir()


def audit(home: Path, folder: Path | None = None) -> list:
    """`(channel, status, text)` for Pi's extension, link, defaults, and skill links.

    `folder` is the agent folder this run resolved (`--pi-agent-dir`, or `PI_CODING_AGENT_DIR`
    on the real home). Without it, this resolves the folder the same way.
    """
    folder = _agent_dir(home, folder)
    lines = [("hook", *_wiring(home, folder))]
    lines.extend(("pi", status, text) for status, text in _agent_lines(home, folder))
    return lines


def declared_defaults(home: Path, folder: Path | None = None) -> list:
    """`(status, text)` for keys the declared Pi config sets. The shared module uses this
    to see that a Pi config from the harnesses file is already audited."""
    return _defaults(home, _agent_dir(home, folder))


def read(payload: dict) -> ToolCall:
    """What set-up-machine's Pi extension sends from `tool_call`: `toolName`, `input` (the
    tool's arguments), `cwd`, `sessionId` and `hasUI`. MCP tools keep their
    `mcp__<server>__<tool>` names. `codemode`'s script (`input.code`) isn't read: each tool
    call the script makes reaches the extension as its own `tool_call`."""
    tool = payload.get("toolName") if isinstance(payload.get("toolName"), str) else ""
    args = payload.get("input") if isinstance(payload.get("input"), dict) else {}
    command = args.get("command") if tool in SHELL_TOOLS else None
    files = []
    if tool in FILE_TOOLS:
        key, access = FILE_TOOLS[tool]
        if isinstance(args.get(key), str) and args[key]:
            files.append((args[key], access))
    searches = ()
    if tool == "grep":
        searches = _search(args, "path", "glob")
    elif tool == "find":
        searches = _search(args, "path", "pattern")
    return ToolCall(
        tool=tool,
        command=command if isinstance(command, str) else None,
        files=tuple(files),
        searches=searches,
        cwd=payload.get("cwd") if isinstance(payload.get("cwd"), str) else "",
        session=payload.get("sessionId") if isinstance(payload.get("sessionId"), str) else "",
        unattended="" if payload.get("hasUI") is True else UNATTENDED,
        no_native_ask=True,  # Pi has no permission system: the extension does the asking
    )


def write(denials: list, asks=()) -> str:
    """Always one JSON line: `{"block": <refusal>}`, `{"ask": <question>}`, or `{}`.
    The extension returns a block to Pi, which gives the agent the reason as the tool's result."""
    if denials:
        return json.dumps({"block": refusal(denials)}) + "\n"
    if asks:
        return json.dumps({"ask": _asking(list(asks))}) + "\n"
    return "{}\n"


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


def _agent_dir(home: Path, folder: Path | None = None) -> Path:
    """The agent folder: the one this run passed, else `PI_CODING_AGENT_DIR` on the real home,
    else `~/.pi/agent`."""
    if folder is not None:
        return folder.expanduser().resolve()
    custom = os.environ.get("PI_CODING_AGENT_DIR") if home == Path.home().resolve() else None
    chosen = Path(custom) if custom else home / DEFAULT_DIR
    return chosen.expanduser().resolve()


def _wiring(home: Path, folder: Path):
    if not folder.is_dir():
        return ("none", f"{label}: not set up here (no ~/{DEFAULT_DIR.as_posix()})")
    path = folder / "extensions" / "set-up-machine.ts"
    try:
        text = path.read_text()
    except OSError:
        return ("FAIL", f"Pi: no extension at {path}; Pi has no permission system, so nothing enforces the rule table")
    if not text.startswith(EXTENSION_HEADER):
        return ("gap", f"Pi: {path} wasn't written by set-up-machine; left alone, so the hook isn't wired (references/pi.md)")
    match = re.search(r"^const COMMAND = (\[.*\]);$", text, re.M)
    try:
        command = json.loads(match.group(1)) if match else []
    except ValueError:
        command = []
    script = command_script(shlex.join(command), id, home) if command else None
    if script is None:
        return ("FAIL", f"Pi: {path} doesn't run the pre-tool hook with --harness pi")
    if not script.is_file():
        return ("FAIL", f"Pi: {path} runs {script}, which doesn't exist")
    return ("wired", f"Pi: {path} -> {script}")


def _agent_lines(home: Path, folder: Path) -> list:
    """(status, text) lines for Pi; one `none` line when the agent folder doesn't exist."""
    if not folder.is_dir():
        return [("none", f"Pi: not set up here (no {folder})")]
    return _link(home, folder) + _skill_links(folder) + _defaults(home, folder)


def _link(home: Path, folder: Path) -> list:
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


def _skill_links(folder: Path) -> list:
    skills = folder / "skills"
    if not skills.is_dir():
        return []
    return [("extra", f"Pi: {entry} is a broken link; remove it")
            for entry in sorted(skills.iterdir()) if entry.is_symlink() and not entry.exists()]


def _load_declared(home: Path) -> tuple:
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
        path = layout.harness_file(pointer.clone, id, "config")
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


def _defaults(home: Path, folder: Path) -> list:
    try:
        declared, source = _load_declared(home)
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


def _asking(asks: list) -> str:
    """The question the Pi extension puts to the user for a call that hits ask rows."""
    lines = ["The global rule table asks you before this call runs. Allow it?"]
    for hit in asks:
        rule = hit.rule
        lines.append(f"- `{hit.part}`: ask rule {rule.id} ({_plain(rule.summary)}). {rule.reason} The agent's instruction: {rule.instruction}")
    return "\n".join(lines)


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
