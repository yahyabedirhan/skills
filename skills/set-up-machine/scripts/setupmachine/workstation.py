"""The workstation repo: the source of every personal part of a machine's setup.

The pointer, `~/.config/agents/source.md`, names `<workstation-repo>` and its clone, `<path-to-workstation-repo>`,
or says there is none. This module reads the repo's `setup/` folder through it:

- `setup/instructions.md`: the personal parts of the shared global instructions file;
- `setup/permissions.json`: personal permissions, rows in the rule table's format;
- `setup/installs.json`: the skills and plugins every machine gets;
- `setup/harnesses.json`: where each harness's own instructions and declared config are.

The steps: read the pointer, read each file that exists, and record a problem that names
the file for each one that is missing or malformed. The verifier prints those problems as
FAIL lines. The hook uses only `personal_rows`. `references/workstation.md` is the format.
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from . import rules as rule_table

POINTER = Path(".config/agents/source.md")
SHARED = Path(".config/agents/AGENTS.md")
DEFAULTS, AGREEMENT, GLOSSARY, WORKFLOW = (
    "## Environment defaults", "## Working agreement", "## Glossary", "## Personal workflow")
WORKFLOW_INTRO = ("Rules for how this person works that pass the team test. "
                  "Anything a project or a skill needs goes there instead.")
POINTER_ROLES = ("workstation-repo", "path-to-workstation-repo")
HARNESS_SECTION = "## Instructions"
OSES = {"macos": "darwin", "linux": "linux"}


@dataclass
class Setup:
    """What the workstation repo asks for, as one machine reads it."""
    repository: str = ""  # `<owner>/<repo>`, or "" when the pointer says none
    clone: Path | None = None
    clone_text: str = ""  # the clone path as the pointer writes it, such as `~/code/setup`
    problems: list = field(default_factory=list)  # one sentence per missing or malformed file
    rows: list = field(default_factory=list)  # personal permissions, as rule-table Rules
    installs: dict = field(default_factory=dict)  # `installs.json`, or {} without it
    # {harness: {"instructions" | "config": Path, "environments": {env: {"instructions" | "config": Path}}}}
    harness_files: dict = field(default_factory=dict)

    def plugins(self, harness: str) -> list:
        """The `installs.json` plugin entries for this harness that apply to this machine's OS."""
        here = "darwin" if sys.platform == "darwin" else "linux"
        return [e for e in self.installs.get("plugins", [])
                if harness in e["harnesses"] and (not e.get("os") or any(OSES.get(o) == here for o in e["os"]))]

    def file(self, harness: str, kind: str, env: str | None = None) -> Path | None:
        """The environment's own file when `harnesses.json` names one, else the harness's shared one."""
        entry = self.harness_files.get(harness, {})
        own = entry.get("environments", {}).get(env, {}).get(kind) if env else None
        return own or entry.get(kind)


def load(home: Path, table: list, harness_ids) -> Setup:
    """The pointer and every `setup/` file it leads to. Problems are recorded, never raised.
    `harness_ids` maps each harness id to the environments it has."""
    setup = Setup()
    try:
        setup.repository, setup.clone, setup.clone_text = read_pointer(home)
    except ValueError as exc:
        setup.problems.append(str(exc))
        return setup
    if not setup.repository:
        return setup
    folder = setup.clone / "setup"
    try:
        setup.rows = personal_rows(home, table)
    except ValueError as exc:
        setup.problems.append(str(exc))
    setup.installs = _installs(folder / "installs.json", set(harness_ids), setup.problems)
    setup.harness_files = _harness_files(setup.clone, dict(harness_ids), setup.problems)
    return setup


def read_pointer(home: Path) -> tuple:
    """(repository, clone path, clone text) from the pointer; ("", None, "") when it says none."""
    path = home / POINTER
    if not path.is_file():
        raise ValueError(f"no pointer at {path}: ask the user for their workstation repo, or none, and write it")
    text = path.read_text()
    repository = _field(text, "Repository")
    if repository is None:
        raise ValueError(f"{path} has no `- Repository:` line")
    if repository.lower() == "none":
        return "", None, ""
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError(f"{path}: the repository `{repository}` isn't `<owner>/<repo>`")
    clone = _field(text, "Clone") or ""
    if not clone.startswith(("~/", "/")):
        raise ValueError(f"{path} needs a `- Clone:` path starting with `~/` or `/`")
    return repository, Path(str(home) + clone[1:]) if clone.startswith("~/") else Path(clone), clone


def personal_rows(home: Path, table: list) -> list:
    """The personal permissions from `setup/permissions.json`; [] without a pointer, repo or file.

    A malformed row, or an id the rule table already uses, raises RuleTableError.
    """
    try:
        repository, clone, _ = read_pointer(home)
    except ValueError:
        return []
    path = clone / "setup/permissions.json" if repository else None
    if path is None or not path.is_file():
        return []
    rows = rule_table.load(path, personal=True)
    taken = {r.id for r in table}
    for row in rows:
        if row.id in taken:
            raise rule_table.RuleTableError(f"{path}: the id {row.id!r} is already a row of the rule table")
    return rows


# --- the shared global instructions file ------------------------------------------------


def shared_file_problems(setup: Setup, home: Path) -> list:
    """How the shared file differs from what `setup/instructions.md` generates; [] when it matches.

    Compared: the Tool column of the Environment defaults table (with the two roles the
    pointer fills), the tool glossaries after it, and the Working agreement, Glossary and
    Personal workflow sections.
    """
    source, shared = setup.clone / "setup/instructions.md", home / SHARED
    try:
        want_text, have_text = source.read_text(), shared.read_text()
    except OSError as exc:
        return [f"can't read {exc.filename}"]
    want, have = tools_table(want_text), tools_table(have_text)
    if want is None:
        return [f"{source} has no `{DEFAULTS}` table with Role and Tool columns"]
    if have is None:
        return [f"{shared} has no `{DEFAULTS}` table with Role and Tool columns"]
    problems = []
    from_pointer = dict(zip(POINTER_ROLES, (setup.repository, setup.clone_text)))
    for role, value in from_pointer.items():
        if want.get(role, "none") not in ("none", value):
            problems.append(f"`{role}` is in {source}, but the pointer fills it: leave it out")
    want = {**{r: v for r, v in want.items() if v != "none"}, **from_pointer}
    for role in sorted(set(want) | set(have)):
        if have.get(role) != want.get(role, "none"):
            problems.append(f"`{role}` is `{have.get(role)}` in {shared}, `{want.get(role, 'none')}` from {source}")
    for name in (AGREEMENT, GLOSSARY, WORKFLOW, "tool glossaries"):
        mine, theirs = _part(want_text, name), _part(have_text, name)
        if name == WORKFLOW and theirs and theirs.startswith(WORKFLOW_INTRO):
            theirs = theirs[len(WORKFLOW_INTRO):].strip()
        if mine != theirs:
            problems.append(f"`{name}` in {shared} differs from {source}")
    return problems


def section(text: str, heading: str):
    """The text under a `## ` heading, up to the next `## ` heading or generated block; None without one."""
    lines = text.split("\n")
    starts = [i for i, line in enumerate(lines) if line.strip() == heading]
    if not starts:
        return None
    body = []
    for line in lines[starts[0] + 1:]:
        if line.startswith("## ") or line.startswith("<!-- set-up-machine:"):
            break
        body.append(line)
    return "\n".join(body).strip()


def tools_table(text: str):
    """{role: Tool value} from the Environment defaults table, or None without one."""
    rows = [_cells(line) for line in (section(text, DEFAULTS) or "").split("\n") if line.strip().startswith("|")]
    header = [_plain(c).lower() for c in rows[0]] if rows else []
    if "role" not in header or "tool" not in header:
        return None
    role_at, tool_at = header.index("role"), header.index("tool")
    return {_plain(row[role_at]): _plain(row[tool_at]) or "none" for row in rows[1:]
            if len(row) > max(role_at, tool_at) and not all(set(c.strip()) <= set("-: ") for c in row)}


def _part(text: str, name: str):
    """One optional part of the instructions: a section, or the tool glossaries; None when absent or empty."""
    if name != "tool glossaries":
        return section(text, name) or None
    lines = (section(text, DEFAULTS) or "").split("\n")
    start = next((i for i, line in enumerate(lines) if line.startswith("### ")), None)
    return "\n".join(lines[start:]).strip() or None if start is not None else None


def _cells(line: str) -> list:
    """A table row's cells; a `|` inside backticks, or escaped, belongs to its cell."""
    cells, cell, code, i, line = [], "", False, 0, line.strip()
    while i < len(line):
        if line.startswith("\\|", i):
            cell, i = cell + "|", i + 2
            continue
        code ^= line[i] == "`"
        if line[i] == "|" and not code:
            cells.append(cell)
            cell = ""
        else:
            cell += line[i]
        i += 1
    return (cells + [cell])[1:-1]


def _field(text: str, name: str):
    match = re.search(rf"^\s*[-*]\s*{name}:\s*(.*?)\s*$", text, re.M)
    return _plain(match.group(1)) if match else None


def _plain(cell: str) -> str:
    cell = cell.strip()
    return cell[1:-1].strip() if len(cell) >= 2 and cell[0] == cell[-1] == "`" else cell


# --- `installs.json` and `harnesses.json` ---------------------------------------------------


def _json(path: Path, problems: list):
    """The JSON object in a file, {} when the file is absent, None (and a problem) when it's malformed."""
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        problems.append(f"{path} isn't valid JSON")
        return None
    if not isinstance(data, dict):
        problems.append(f"{path} must be a JSON object")
        return None
    return data


def _installs(path: Path, harness_ids: set, problems: list) -> dict:
    """`installs.json`, with each plugin entry checked for the fields the verifier reads."""
    data = _json(path, problems)
    if not data:
        return {}
    seen = set()
    for i, entry in enumerate(data.get("plugins", [])):
        where = f"{path}: plugins[{i}]"
        harnesses = entry.get("harnesses") if isinstance(entry, dict) else None
        if not isinstance(harnesses, list) or not harnesses or not set(harnesses) <= harness_ids:
            problems.append(f"{where} needs `harnesses`, a list from {', '.join(sorted(harness_ids))}")
            return {}
        kind_ok = (entry.get("kind") == "bundle" and isinstance(entry.get("source"), str)
                   or entry.get("kind") == "mcp" and isinstance(entry.get("server"), dict))
        if not isinstance(entry.get("name"), str) or not kind_ok:
            problems.append(f"{where} needs a `name`, and a `source` (bundle) or a `server` (mcp)")
            return {}
        for harness in harnesses:  # the same name may serve different harnesses, each once
            if (entry["name"], harness) in seen:
                problems.append(f"{where}: {harness} gets the name {entry['name']!r} twice")
            seen.add((entry["name"], harness))
    for i, entry in enumerate(data.get("skills", [])):
        if not isinstance(entry, dict) or not isinstance(entry.get("source"), str):
            problems.append(f"{path}: skills[{i}] needs a `source`, `<owner>/<repo>`")
            return {}
    return data


def _harness_files(clone: Path, harness_ids: dict, problems: list) -> dict:
    """{harness: {kind: path, "environments": {env: {kind: path}}}} from `harnesses.json`. A harness's
    `environments` key holds what only one of its environments has; each path must be a file inside the repo."""
    path = clone / "setup/harnesses.json"
    data = _json(path, problems)
    if not data:
        return {}
    if data.get("version") != 1 or not isinstance(data.get("harnesses", {}), dict):
        problems.append(f"{path} needs \"version\": 1 and a `harnesses` object")
        return {}
    files = {}
    kinds = {"instructions", "config"}
    for harness, entry in data.get("harnesses", {}).items():
        if harness not in harness_ids or not isinstance(entry, dict) or not set(entry) <= kinds | {"environments"}:
            problems.append(f"{path}: `harnesses.{harness}` must be a known harness with instructions, config, "
                            "environments or some of them")
            continue
        found = files.setdefault(harness, {})
        found.update(_kind_files(clone, path, f"harnesses.{harness}", {k: v for k, v in entry.items() if k in kinds},
                                 problems))
        envs = entry.get("environments", {})
        known = harness_ids[harness]
        if not isinstance(envs, dict):
            problems.append(f"{path}: `harnesses.{harness}.environments` must be an object")
            continue
        for env, own in envs.items():
            if env not in known or not isinstance(own, dict) or not own or not set(own) <= kinds:
                problems.append(f"{path}: `harnesses.{harness}.environments.{env}` must be one of "
                                f"{', '.join(sorted(known)) or 'none'}, with instructions, config or both")
                continue
            found.setdefault("environments", {})[env] = _kind_files(
                clone, path, f"harnesses.{harness}.environments.{env}", own, problems)
    return files


def _kind_files(clone: Path, path: Path, where: str, entry: dict, problems: list) -> dict:
    files = {}
    for kind, value in entry.items():
        target = clone / str(value)
        if not target.resolve().is_relative_to(clone.resolve()) or not target.is_file():
            problems.append(f"{path}: `{where}.{kind}` is `{value}`, which isn't a file in the repo")
            continue
        files[kind] = target
    return files
