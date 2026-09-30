#!/usr/bin/env python3
"""Audit the skills for the team test: default tools and Defaults mentions.

usage: default_tools.py [--skills DIR] [--global FILE] [--tool NAME ...]

Two lists, both tolerated, never blocking (always exits 0):

- skill lines that name a default tool outside that tool's how-to skill. The
  tools are the --tool names, else the ones the Defaults table in the global
  file names for the tool roles (session-host, worktree-tool,
  notification-method). A skill folder whose name contains the tool's name is
  its how-to skill and is skipped, and so is a line that names that skill
  (routing to it: "use the handover-to-herdr skill").
- skill lines that mention "Defaults table" or "global instructions" outside a
  SKILL.md's `## Parameters` section, where a placeholder belongs instead. The
  skills that own the environment's instruction files are exempt.

Reads the Markdown and YAML an agent loads.
"""
import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

TOOL_ROLES = ("session-host", "worktree-tool", "notification-method")
MENTIONS = ("Defaults table", "global instructions")
# These skills describe the global instructions file and the layers themselves.
MENTION_EXEMPT = ("set-up-machine", "set-up-project", "maintain-environment")
PARAMETERS = "## Parameters"
GLOBAL_FILE = Path.home() / ".config" / "agents" / "AGENTS.md"
SKILLS_DIR = Path(__file__).resolve().parents[2]
READ = {".md", ".yaml", ".yml"}


@dataclass(frozen=True)
class Hit:
    skill: str
    path: str
    line: int
    tool: str  # the tool or the phrase matched
    text: str


def tools_from_defaults(text: str) -> list:
    """The tool each tool-role row names: the value's first word, lowercased."""
    tools = []
    for line in text.splitlines():
        cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
        if len(cells) < 2 or cells[0].lower() not in TOOL_ROLES:
            continue
        word = re.match(r"[\w.-]+", cells[1].replace("`", ""))
        if word and word.group().lower() != "none":
            tools.append(word.group().lower())
    return tools


def _files(skills: Path):
    """(skill, relative path, lines) for each file an agent loads inside a skill folder."""
    for path in sorted(p for p in skills.rglob("*") if p.is_file() and p.suffix in READ):
        rel = path.relative_to(skills)
        if len(rel.parts) >= 2:
            yield rel.parts[0], rel, path.read_text(errors="replace").splitlines()


def scan(skills: Path, tools: list) -> list:
    """Lines naming a tool outside its how-to skill, unless the line names that skill: routing to it."""
    folders = sorted(p.name for p in skills.iterdir() if p.is_dir())
    how_to = {t: [f for f in folders if t in f.lower()] for t in tools}
    hits = []
    for skill, rel, lines in _files(skills):
        named = [t for t in tools if t not in skill.lower()]
        for n, text in enumerate(lines, 1):
            for tool in named:
                if not re.search(rf"\b{re.escape(tool)}\b", text, re.IGNORECASE):
                    continue
                if any(re.search(rf"\b{re.escape(f)}\b", text) for f in how_to[tool]):
                    continue
                hits.append(Hit(skill, rel.as_posix(), n, tool, text.strip()))
    return hits


def scan_mentions(skills: Path) -> list:
    hits = []
    for skill, rel, lines in _files(skills):
        if skill in MENTION_EXEMPT:
            continue
        in_parameters = False
        for n, text in enumerate(lines, 1):
            if text.startswith("#"):
                in_parameters = rel.name == "SKILL.md" and text.strip() == PARAMETERS
            if in_parameters:
                continue
            for phrase in MENTIONS:
                if phrase.lower() in text.lower():
                    hits.append(Hit(skill, rel.as_posix(), n, phrase, text.strip()))
    return hits


def plural(n: int, word: str) -> str:
    return f"{n} {word}{'' if n == 1 else 's'}"


def report(title: str, hits: list) -> None:
    print(title)
    for hit in hits:
        text = hit.text if len(hit.text) <= 100 else hit.text[:97] + "..."
        print(f"  {hit.path}:{hit.line} {hit.tool}: {text}")
    skills = len({h.skill for h in hits})
    print(f"{plural(len(hits), 'line')} in {plural(skills, 'skill')}. Tolerated, not blocking.")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--skills", type=Path, default=SKILLS_DIR)
    ap.add_argument("--global", dest="global_file", type=Path, default=GLOBAL_FILE)
    ap.add_argument("--tool", action="append", default=[])
    args = ap.parse_args(argv)

    tools = [t.lower() for t in args.tool]
    if not tools and args.global_file.is_file():
        tools = tools_from_defaults(args.global_file.read_text())
    if tools:
        report(f"Skills naming a default tool ({', '.join(tools)}) outside its how-to skill:", scan(args.skills, tools))
    elif not args.global_file.is_file():
        print(f"No default tool named: {args.global_file} doesn't exist. Pass --global FILE or --tool NAME.")
    else:
        print(f"No default tool named: {args.global_file} has no tool in its Defaults table. Pass --tool NAME.")
    print()
    report("Skills mentioning the Defaults table or global instructions outside `## Parameters`:",
           scan_mentions(args.skills))
    return 0


if __name__ == "__main__":
    sys.exit(main())
