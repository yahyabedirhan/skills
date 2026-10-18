"""Claude Code cloud sessions: one Anthropic-managed VM per session, a fresh clone of the repo, and the repo's own CLAUDE.md and `.claude/settings.json` (references/claude-code/cloud.md).

Nothing in `~/.claude/` on the user's machine reaches the VM. The repo's SessionStart hook only installs the skills and tools; the agent then applies the setup itself, as the repo's cloud section tells it, and the repo's PreToolUse hook runs the pre-tool hook with `--harness claude-code`.

When `~/.local/share/agents/environment-setup.json` exists, the cloud environment's setup script, which `<workstation-repo>` renders, set the session up instead: it wrote the user-level files before Claude Code launched, and the checks read those files (references/claude-code/cloud.md, *Environment setup*).
"""
from __future__ import annotations

import os
from pathlib import Path

from . import FOLDER, HARNESS_INSTRUCTIONS, read, write  # noqa: F401
from ...checks import (Cell, any_wired_problem, as_list, cell, dig, harness_instructions_problem, link_problem, na,
                       read_json, skill_problems)
from ...workstation import HARNESS_SECTION, section

ID, LABEL = "claude-code", "Claude Code"
ENV = "cloud"
# The section of the repo's CLAUDE.md, or the AGENTS.md it reads, that the agent follows at start.
CLOUD_SECTION = "## Claude Code cloud specific instructions"
PROJECT_SETTINGS = Path(".claude/settings.json")
# Left by a cloud environment's setup script once it set the session up (references/claude-code/cloud.md).
ENVIRONMENT_MARKER = Path(".local/share/agents/environment-setup.json")
CLOUD_RULES = FOLDER / "rules/cloud-instructions.md"


def present(home: Path) -> bool:
    """A cloud VM sets CLAUDE_CODE_REMOTE=true, and a machine never does. A `--home` fixture on the VM is still the cloud, the same way a CLI on PATH is seen from the real machine."""
    return os.environ.get("CLAUDE_CODE_REMOTE") == "true"


# --- the checks ----------------------------------------------------------------------------


def environment_setup(home: Path) -> bool:
    """Whether a cloud environment's setup script set this session up."""
    return (home / ENVIRONMENT_MARKER).is_file()


def check_instructions(ctx) -> Cell:
    """The repo installs on SessionStart, its instructions carry the cloud section, which points at the cloud instructions file, and the agent's own setup linked CLAUDE.md, turned memory off and wrote Claude Code's own instructions."""
    if environment_setup(ctx.home):
        return _environment_instructions(ctx)
    if ctx.setup.clone is None:
        return Cell("gap", ["no workstation clone: can't see the repo's CLAUDE.md or .claude/settings.json"])
    declared = ctx.setup.file(ID, "instructions", ENV)
    problems = []
    settings_path = ctx.setup.clone / PROJECT_SETTINGS
    if not _commands(read_json(settings_path) or {}, "SessionStart"):
        problems.append(("FAIL" if declared else "gap", f"{ctx.show(settings_path)} has no SessionStart hook to install"))
    if declared is None:
        problems.append(("gap", "setup/harnesses.json names no instructions for Claude Code's cloud environment"))
        return cell(problems)
    if not section(declared.read_text(), HARNESS_SECTION):
        problems.append(("FAIL", f"{ctx.show(declared)} has no `{HARNESS_SECTION}` section"))
    relative = declared.relative_to(ctx.setup.clone).as_posix()
    body = _cloud_section(ctx.setup.clone)
    if not body:
        problems.append(("FAIL", f"the repo's CLAUDE.md has no `{CLOUD_SECTION}` section; the agent reads it at start"))
    elif relative not in body:
        problems.append(("FAIL", f"the repo's `{CLOUD_SECTION}` section doesn't point at {relative}"))
    problems.append(link_problem(ctx, ctx.home / FOLDER / "CLAUDE.md"))
    if (read_json(ctx.home / FOLDER / "settings.json") or {}).get("autoMemoryEnabled") is not False:
        problems.append(("FAIL", "autoMemoryEnabled isn't false in ~/.claude/settings.json"))
    problems.append(harness_instructions_problem(ctx, ID, ctx.home / HARNESS_INSTRUCTIONS))
    return cell([p for p in problems if p])


def check_guardrails(ctx) -> Cell:
    """A match-all PreToolUse group runs the installed pre_tool_hook.py: in ~/.claude/settings.json when the environment set the session up before launch, else in the repo's settings, since the agent's own ~/.claude/settings.json comes too late."""
    if environment_setup(ctx.home):
        path = ctx.home / FOLDER / "settings.json"
    elif ctx.setup.clone is None:
        return Cell("gap", ["no workstation clone: can't see .claude/settings.json"])
    else:
        path = ctx.setup.clone / PROJECT_SETTINGS
    settings = read_json(path)
    if settings is None:
        return Cell("FAIL", [f"no {ctx.show(path)}, or it isn't valid JSON"])
    commands = [h.get("command") for g in as_list(dig(settings, "hooks", "PreToolUse"))
                if isinstance(g, dict) and g.get("matcher") in ("*", "", None)
                for h in as_list(g.get("hooks")) if isinstance(h, dict)]
    problems = [any_wired_problem(ctx, path, commands, ID)]
    if settings.get("disableAllHooks") is True:
        problems.append(("FAIL", f"{ctx.show(path)} sets disableAllHooks, so the hook never runs"))
    problems.append(("gap", "personal permissions have no native entries here, so the hook alone refuses them"))
    return cell([p for p in problems if p])


def check_sandbox(ctx) -> Cell:
    return Cell("gap", ["the network level is set on the cloud environment; nothing on the VM shows it"])


def check_plugins(ctx) -> Cell:
    if not ctx.setup.plugins(ID):
        return na("installs.json lists no plugin for Claude Code")
    return Cell("gap", ["a cloud session installs no plugin bundle, from user or repo settings; "
                        "claude.ai connectors come from the account and nothing on the VM lists them"])


def check_skills(ctx) -> Cell:
    """Each listed skill is in ~/.claude/skills or the repo's .claude/skills."""
    folders = [ctx.home / FOLDER / "skills"]
    if ctx.setup.clone is not None:
        folders.append(ctx.setup.clone / FOLDER / "skills")
    return cell(skill_problems(ctx, folders))


def check_config(ctx) -> Cell:
    """The model and the network level are picked on claude.ai, so a cloud config has no file to land in. The harness's shared config describes ~/.claude/settings.json on a machine, so it doesn't count here."""
    own = ctx.setup.harness_files.get(ID, {}).get("environments", {}).get(ENV, {}).get("config")
    if own is None:
        return na("the model is picked when the session starts; no file on the VM holds it")
    return Cell("gap", [f"{ctx.show(own)}: a cloud session has no settings file for its keys"])


def _environment_instructions(ctx) -> Cell:
    """The environment's setup script linked CLAUDE.md, turned memory off and wrote Claude Code's own rules and the cloud rules, each matching its source."""
    problems = [link_problem(ctx, ctx.home / FOLDER / "CLAUDE.md")]
    if (read_json(ctx.home / FOLDER / "settings.json") or {}).get("autoMemoryEnabled") is not False:
        problems.append(("FAIL", "autoMemoryEnabled isn't false in ~/.claude/settings.json"))
    problems.append(harness_instructions_problem(ctx, ID, ctx.home / HARNESS_INSTRUCTIONS))
    problems.append(harness_instructions_problem(ctx, ID, ctx.home / CLOUD_RULES, env=ENV))
    return cell([p for p in problems if p])


def _commands(settings: dict, event: str) -> list:
    return [h.get("command") for g in as_list(dig(settings, "hooks", event)) if isinstance(g, dict)
            for h in as_list(g.get("hooks")) if isinstance(h, dict) and isinstance(h.get("command"), str)]


def _cloud_section(clone: Path):
    """The cloud section of the repo's CLAUDE.md, or of the AGENTS.md it links to or imports."""
    claude = clone / "CLAUDE.md"
    texts = [claude.read_text()] if claude.is_file() else []
    agents = clone / "AGENTS.md"
    if agents.is_file() and (claude.is_symlink() or any("@AGENTS.md" in t for t in texts)):
        texts.append(agents.read_text())
    return next((body for body in (section(t, CLOUD_SECTION) for t in texts) if body), None)
