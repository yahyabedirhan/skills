"""The shared global instructions file, and the manifest of what set-up-machine wrote.

Both live in one harness-neutral folder, `<home>/.config/agents/`, which every
adapter reaches: Claude Code by an `@` import, harnesses without imports by a
symlink to the file.
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from . import hook
from .plan import Change, FileWrite, Run, Section

# How a harness's program is looked up on PATH; tests replace it.
which = shutil.which


def trial_home(home: Path, os_home: Path):
    """Why plan won't start a harness to list its tools, when `home` isn't the user's own, else None.
    A harness started there would read the real machine's configuration and login."""
    if home.resolve() == os_home.resolve():
        return None
    return (f"plan doesn't start a harness under a --home other than your own ({home}), since it would read the real "
            "machine; pass --tool-names to match a list instead")


def harness_found(home: Path, os_home: Path, folder: Path, programs) -> bool:
    """Whether a harness is on this machine: its config folder exists, or, in the user's own
    home, one of its programs is on PATH. A fresh install that has never run has no folder yet
    (Codex, opencode and the Cursor CLI make theirs on first start); a trial `--home` goes by
    folders alone, since PATH describes the real machine."""
    return folder.is_dir() or (home.resolve() == os_home.resolve() and any(which(p) for p in programs))


BEGIN = "<!-- set-up-machine:rules start. Generated from set-up-machine's rule table: change the table, not these lines. -->"
END = "<!-- set-up-machine:rules end -->"

TITLE = "# Global agent instructions"
RULE_LINE = (
    "Only what describes this person's own workflow and explains a global rule. "
    "Anything a teammate would need goes in the project or a skill."
)

# The Defaults table: one row per role a skill may name. Values are the user's;
# set-up-machine only adds a missing row, with NO_DEFAULT as its value.
DEFAULTS_HEADING = "## Defaults"
DEFAULTS_INTRO = (
    "Skills name each role as a placeholder (`<session-host>`); this table gives its value. "
    "`none` means the skill's own fallback. A project's own Defaults table overrides a row for that project."
)
ROLES = ("session-host", "worktree-tool", "notification-method", "agent-to-start", "skills-repo", "path-to-skills-repo")
NO_DEFAULT = "none"

# The personal-workflow section: the user's, never rewritten.
WORKFLOW_HEADING = "## Personal workflow"
WORKFLOW_INTRO = "Rules for how this person works that pass the team test. Anything a project or a skill needs goes there instead."

BLOCK_INTRO = """## Global rules

Every harness on this machine enforces these as far as it can. A harness refuses the whole command when any part of it matches a rule, so run each risky step as its own command, and read a refusal as a refusal of that step only.
"""

LEVEL_LABEL = {"deny": "Denied", "ask": "Asks first", "allow-and-report": "Allowed and reported"}

MANIFEST_VERSION = 1


def folder(home: Path) -> Path:
    return home / ".config" / "agents"


def instructions_path(home: Path) -> Path:
    return folder(home) / "AGENTS.md"


def manifest_path(home: Path) -> Path:
    return folder(home) / "set-up-machine.json"


def hook_config_path(home: Path) -> Path:
    return folder(home) / "hook.json"


def backups_path(home: Path) -> Path:
    return folder(home) / "backups"


def read_text(path: Path):
    try:
        return path.read_text()
    except FileNotFoundError:
        return None


def rule_lines(rules: list) -> list:
    return [
        f"- **{LEVEL_LABEL[r.level]}:** {r.summary}. {r.reason} {'Instead: ' if r.level == 'deny' else ''}{r.instruction}"
        for r in rules
    ]


def render_block(rules: list) -> str:
    return "\n".join([BEGIN, BLOCK_INTRO, *rule_lines(rules), END])


def defaults_table() -> str:
    rows = [f"| {role} | {NO_DEFAULT} |" for role in ROLES]
    return "\n".join(["| Role | Default |", "|---|---|", *rows])


def new_file(block: str) -> str:
    return "\n\n".join([
        TITLE, RULE_LINE, DEFAULTS_HEADING, DEFAULTS_INTRO, defaults_table(), block, WORKFLOW_HEADING, WORKFLOW_INTRO,
    ]) + "\n"


def _role_row(line: str):
    """The role a Defaults table row names, or None for any other line."""
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    return cells[0].lower() if line.lstrip().startswith("|") and cells else None


def ensure_shape(text: str):
    """Add what the file's shape lacks: the rule line, the Defaults section and its
    role rows, and the personal-workflow section. Adds only; returns (text, what was added)."""
    lines = text.split("\n")
    added = []
    if not any(l.strip() == RULE_LINE for l in lines):
        at = 1 if lines and lines[0].startswith("# ") else 0
        lines[at:at] = ([""] if at else []) + [RULE_LINE] + ([""] if not at else [])
        added.append("the rule line at the top")
    if not any(l.strip() == DEFAULTS_HEADING for l in lines):
        at = next((i for i, l in enumerate(lines) if l.strip() == BEGIN), None)
        section = [DEFAULTS_HEADING, "", DEFAULTS_INTRO, "", *defaults_table().split("\n"), ""]
        if at is None:
            lines = _trim_end(lines) + [""] + section
        else:
            lines[at:at] = section
        added.append("the Defaults table, every role `none`")
    else:
        start = next(i for i, l in enumerate(lines) if l.strip() == DEFAULTS_HEADING)
        end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("#") or lines[i].strip() == BEGIN), len(lines))
        rows = [i for i in range(start + 1, end) if _role_row(lines[i]) is not None]
        have = {_role_row(lines[i]) for i in rows}
        missing = [r for r in ROLES if r.lower() not in have]
        if missing:
            new_rows = [f"| {r} | {NO_DEFAULT} |" for r in missing]
            if rows:
                lines[rows[-1] + 1:rows[-1] + 1] = new_rows
            else:
                lines[start + 1:start + 1] = ["", "| Role | Default |", "|---|---|", *new_rows]
            added.extend(f"the Defaults row {r}, `none`" for r in missing)
    if not any(l.strip() == WORKFLOW_HEADING for l in lines):
        lines = _trim_end(lines) + ["", WORKFLOW_HEADING, "", WORKFLOW_INTRO, ""]
        added.append("the personal workflow section")
    return "\n".join(lines), added


def _trim_end(lines: list) -> list:
    while lines and not lines[-1].strip():
        lines = lines[:-1]
    return lines


def plan_instructions(home: Path, rules: list):
    """The shared file with its shape completed and its generated block brought up to date.
    Outside the block it only adds what the shape lacks; nothing there is rewritten."""
    path = instructions_path(home)
    old = read_text(path)
    block = render_block(rules)
    section = Section("Shared global instructions", path, show_diff=True)
    if old is None:
        return section, FileWrite(path, old, new_file(block))
    text, added = ensure_shape(old)
    for what in added:
        section.changes.append(Change("added", what, note="the file's shape; the rest of the file is kept"))
    if BEGIN in text:
        before, rest = text.split(BEGIN, 1)
        if END not in rest:
            raise ValueError(f"{path} has the rules start marker without its end marker; restore it by hand")
        new = before + block + rest.split(END, 1)[1]
    else:
        # No block yet: it goes before the personal workflow section.
        before, after = text.split(WORKFLOW_HEADING, 1)
        new = before.rstrip("\n") + "\n\n" + block + "\n\n" + WORKFLOW_HEADING + after
    if not new.endswith("\n"):
        new += "\n"
    return section, FileWrite(path, old, new)


# Where the skills CLI installs skills, relative to a home folder (maintain-environment's skill-operations).
SKILL_FOLDERS = (".agents/skills", ".claude/skills")


def plan_hook_config(home: Path, os_home: Path, script=None):
    """The pre-tool hook's configuration: created with the default report folder, then the user's.

    In another home than the user's own, the default report folder is inside
    that home, so a trial run never reports into the real one. A hook `script`
    outside a skills install folder is named: every harness's wiring points at
    it, and it goes when that folder does (the hook then fails open).
    """
    path = hook_config_path(home)
    old = read_text(path)
    section = Section("Pre-tool hook configuration", path, show_diff=True)
    if old is None:
        own = home.resolve() == os_home.resolve()
        default = hook.DEFAULT_REPORT_DIR if own else str(home / hook.DEFAULT_REPORT_DIR[2:])
        config = {"report_dir": default}
        new = json.dumps(config, indent=2) + "\n"
    else:
        try:
            config = json.loads(old)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path} isn't valid JSON ({exc}); fix it by hand, then run the plan again") from exc
        if not isinstance(config, dict):
            raise ValueError(f"{path} must hold a JSON object; fix it by hand, then run the plan again")
        new = old
    section.changes.append(Change("wired", f"the hook's reports go to {hook.report_dir(config, path)}"))
    if script is not None and not installed_skill(Path(script), home, os_home):
        section.changes.append(Change(
            "gap", f"the hook runs from {Path(script).parent.parent}, which isn't under a skills install folder "
                   f"({', '.join('~/' + f for f in SKILL_FOLDERS)}): if that folder moves or goes, every harness's "
                   "hook stops checking (it fails open) until the plan runs again from the installed skill"))
    return section, FileWrite(path, old, new)


def installed_skill(script: Path, home: Path, os_home: Path) -> bool:
    """Whether a skill's file sits in a skills install folder of either home, links resolved."""
    folders = {(h / f).resolve() for h in (home, os_home) for f in SKILL_FOLDERS}
    resolved = script.resolve()
    return any(folder in resolved.parents for folder in folders)


# --- shared skills ------------------------------------------------------------------

SKILLS_REPO_ROLE = "skills-repo"
_REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def default_value(text: str, role: str):
    """A role's value in the Defaults table, or None when the row is missing or `none`."""
    for line in text.split("\n"):
        if _role_row(line) == role:
            cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
            value = cells[1] if len(cells) > 1 else ""
            return None if not value or value.lower() == NO_DEFAULT else value
    return None


def skills_lock_path(home: Path) -> Path:
    """Where the skills CLI records each global install and its source."""
    return home / ".agents" / ".skill-lock.json"


def installed_sources(home: Path) -> set:
    """The sources (`<owner>/<repo>`, lower case) the skills CLI installed global skills from."""
    try:
        data = json.loads(skills_lock_path(home).read_text())
    except (OSError, json.JSONDecodeError):
        return set()
    skills = data.get("skills") if isinstance(data, dict) else None
    return {s["source"].lower() for s in (skills or {}).values()
            if isinstance(s, dict) and isinstance(s.get("source"), str)}


def skills_add_argv(home: Path, source: str, *options) -> list:
    """`npx skills add` for a global install, with maintain-environment's agent flags: `-a codex`,
    plus `-a claude-code` unless `~/.claude/skills` links to `~/.agents/skills`."""
    argv = ["npx", "--yes", "skills", "add", source, *options, "-g", "-a", "codex"]
    claude_skills = home / ".claude" / "skills"
    if not (claude_skills.is_symlink() and claude_skills.resolve() == (home / ".agents" / "skills").resolve()):
        argv += ["-a", "claude-code"]
    return argv + ["-y"]


def plan_shared_skills(home: Path):
    """The user's own skills repo (the `skills-repo` Defaults row), installed globally: a Run the plan
    shows, then `present` once the skills CLI records a skill from it. No row, no install."""
    path = instructions_path(home)
    section = Section("Shared skills", home / ".agents" / "skills")
    repo = default_value(read_text(path) or "", SKILLS_REPO_ROLE)
    if repo is None:
        section.changes.append(Change(
            "none", f"no `{SKILLS_REPO_ROLE}` value in the Defaults table, so no shared skills to install; "
                    f"set it to `<owner>/<repo>` in {path.name} and run the plan again"))
        return section, []
    if not _REPO.match(repo):
        section.changes.append(Change(
            "gap", f"the `{SKILLS_REPO_ROLE}` value `{repo}` isn't `<owner>/<repo>`, so nothing is installed; "
                   "fix the row and run the plan again"))
        return section, []
    if repo.lower() in installed_sources(home):
        section.changes.append(Change("present", f"shared skills from {repo}", note="installed globally"))
        return section, []
    argv = skills_add_argv(home, repo)
    section.changes.append(Change("added", f"shared skills from {repo}", note=f"apply runs `{' '.join(argv)}`"))
    return section, [Run(skills_lock_path(home), argv, {"HOME": str(home)})]


def load_manifest(home: Path) -> dict:
    text = read_text(manifest_path(home))
    if text is None:
        return {"version": MANIFEST_VERSION, "harnesses": {}}
    data = json.loads(text)
    if data.get("version") != MANIFEST_VERSION:
        raise ValueError(f"{manifest_path(home)}: unsupported manifest version {data.get('version')!r}")
    data.setdefault("harnesses", {})
    return data


def manifest_write(home: Path, old_manifest_text, harnesses: dict) -> FileWrite:
    data = {
        "version": MANIFEST_VERSION,
        "about": "Entries set-up-machine wrote into each harness's files. It removes or loosens only these; anything else there is someone else's.",
        "harnesses": harnesses,
    }
    return FileWrite(manifest_path(home), old_manifest_text, json.dumps(data, indent=2) + "\n")
