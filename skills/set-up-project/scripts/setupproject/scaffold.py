"""The project's own files that set-up-project writes or checks.

- `AGENTS.md` is the one rules file; `CLAUDE.md` holds only `@AGENTS.md`, since
  Claude Code skips a project's `AGENTS.md` when a `CLAUDE.md` exists.
- `.gitignore` carries the folder standard's two ignored paths.
- The agent-written parts (the `## Agent skills` block, `docs/agents/`) are only
  checked: SKILL.md's steps write them from the templates.
"""
from __future__ import annotations

from pathlib import Path

from setupmachine.plan import Change, FileWrite, Section

IMPORT = "@AGENTS.md"
AGENTS_TITLE = "# Agent instructions"
AGENT_SKILLS = "## Agent skills"
GITIGNORE_LINES = (".scratch/", ".claude/worktrees/")
DOCS = ("docs/agents/issue-tracker.md", "docs/agents/domain.md")


def _read(path: Path):
    try:
        return path.read_text()
    except (FileNotFoundError, NotADirectoryError):
        return None


def plan(project: Path):
    """(sections, writes). Changes of kind `todo` are left to the agent's steps."""
    instructions = Section("Project instructions", project / "AGENTS.md")
    writes = _plan_instructions(project, instructions)
    ignore = Section("Folder standard", project / ".gitignore")
    gitignore = _plan_gitignore(project, ignore)
    if gitignore is not None:
        writes.append(gitignore)
    for rel in DOCS:
        if not (project / rel).is_file():
            instructions.changes.append(Change("todo", rel, note="missing: write it from the skill's template"))
    return [instructions, ignore], writes


def _plan_instructions(project: Path, section: Section) -> list:
    agents_path, claude_path = project / "AGENTS.md", project / "CLAUDE.md"
    agents, claude = _read(agents_path), _read(claude_path)

    # CLAUDE.md as a link to AGENTS.md is the same text: nothing to do.
    if claude_path.is_symlink() and claude_path.resolve() == agents_path.resolve() and agents is not None:
        section.changes.append(Change("present", "CLAUDE.md links to AGENTS.md"))
        _check_agent_skills(agents, section)
        return []

    claude_lines = [] if claude is None else claude.splitlines()
    others = [l for l in claude_lines if l.strip() and l.strip() != IMPORT]
    writes = []

    if agents is None:
        if others:
            new_agents = "\n".join(l for l in claude_lines if l.strip() != IMPORT).strip("\n") + "\n"
            section.changes.append(Change("added", "AGENTS.md", note="CLAUDE.md's lines move here"))
            section.changes.append(Change("updated", "CLAUDE.md", note=f"now only `{IMPORT}`"))
            writes.append(FileWrite(agents_path, None, new_agents))
            writes.append(FileWrite(claude_path, claude, IMPORT + "\n"))
            _check_agent_skills(new_agents, section)
            return writes
        new_agents = AGENTS_TITLE + "\n"
        section.changes.append(Change("added", "AGENTS.md", note="the one rules file every harness reads"))
        writes.append(FileWrite(agents_path, None, new_agents))
        agents = new_agents

    if claude is None:
        section.changes.append(Change("added", "CLAUDE.md", note=f"`{IMPORT}`, so Claude Code reads AGENTS.md"))
        writes.append(FileWrite(claude_path, None, IMPORT + "\n"))
    elif not any(l.strip() == IMPORT for l in claude_lines):
        section.changes.append(Change("updated", "CLAUDE.md", note=f"`{IMPORT}` added as its first line"))
        writes.append(FileWrite(claude_path, claude, IMPORT + "\n" + ("\n" if claude.strip() else "") + claude))
    else:
        section.changes.append(Change("present", "CLAUDE.md imports AGENTS.md"))
    for line in others:
        section.changes.append(Change(
            "todo", f"CLAUDE.md: {line.strip()[:80]}",
            note="move into AGENTS.md (Codex, opencode and Cursor read that file), then delete it here"))
    _check_agent_skills(agents, section)
    return writes


def _check_agent_skills(agents_text: str, section: Section) -> None:
    if not any(l.strip() == AGENT_SKILLS for l in agents_text.splitlines()):
        section.changes.append(Change("todo", f"AGENTS.md: {AGENT_SKILLS}", note="missing: write the block (step 4)"))
    else:
        section.changes.append(Change("present", f"AGENTS.md has {AGENT_SKILLS}"))


def _normal(line: str) -> str:
    line = line.strip()
    return line.lstrip("/").rstrip("/") if line and not line.startswith("#") else ""


def _plan_gitignore(project: Path, section: Section):
    path = project / ".gitignore"
    old = _read(path)
    have = {_normal(l) for l in (old or "").splitlines()}
    missing = [l for l in GITIGNORE_LINES if _normal(l) not in have]
    for line in GITIGNORE_LINES:
        section.changes.append(Change("added" if line in missing else "present", line))
    if not missing:
        return None
    base = old or ""
    if base and not base.endswith("\n"):
        base += "\n"
    return FileWrite(path, old, base + "".join(l + "\n" for l in missing))
