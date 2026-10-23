#!/usr/bin/env python3
"""Build the README diagrams as Graphite-profile HTML files with one inline SVG each.

Run from the repo root: python3 docs/diagrams/src/build.py
Then render each HTML file to a 2x PNG with docs/diagrams/src/render.sh.
"""
from html import escape
from pathlib import Path
import textwrap

OUT = Path(__file__).resolve().parent
W = 960
BX, BW = 40, 880          # box x and width
PAD = 20                  # inner padding
MONO_CH = 7.2             # IBM Plex Mono 12px advance
C = dict(paper="#131417", paper2="#222529", ink="#e4e6e9", muted="#8b9097", soft="#6b7078",
         accent="#ffffff", shade="#b9bec4", fold="#4f545b", line="rgba(255,255,255,0.16)")

def wrap(text, px):
    return textwrap.wrap(text, max(10, int(px / MONO_CH))) or [""]

def node(n, y):
    """Return (svg, height) for one node at top y."""
    focal = n.get("focal", False)
    name_c = C["paper"] if focal else C["ink"]
    note_c = C["fold"] if focal else C["muted"]
    sub_c = C["paper"] if focal else C["ink"]
    parts, cy = [], y + PAD
    tx = BX + PAD
    if n.get("tag"):
        parts.append(f'<text x="{tx}" y="{cy+12}" font-family="IBM Plex Mono" font-size="10" letter-spacing="1.6" fill="{note_c}">{escape(n["tag"])}</text>')
        tx += 110
    inner = BX + BW - PAD - tx
    parts.append(f'<text x="{tx}" y="{cy+13}" font-family="Inter Tight" font-weight="600" font-size="15" fill="{name_c}">{escape(n["name"])}</text>')
    cy += 18
    for line in wrap(n["note"], inner) if n.get("note") else []:
        cy += 18
        parts.append(f'<text x="{tx}" y="{cy}" font-family="IBM Plex Mono" font-size="12" fill="{note_c}">{escape(line)}</text>')
    rows = n.get("rows", [])
    if rows:
        lw = max(len(a) for a, _ in rows) * MONO_CH + 24
        multi = any(len(wrap(b, inner - lw)) > 1 for _, b in rows)
        cy += 10
        for k, (a, b) in enumerate(rows):
            blines = wrap(b, inner - lw)
            cy += 18 if k == 0 or not multi else 22
            parts.append(f'<text x="{tx}" y="{cy}" font-family="IBM Plex Mono" font-size="12" fill="{sub_c}">{escape(a)}</text>')
            for i, bl in enumerate(blines):
                if i:
                    cy += 16
                parts.append(f'<text x="{tx+lw:.0f}" y="{cy}" font-family="IBM Plex Mono" font-size="12" fill="{note_c}">{escape(bl)}</text>')
    chains = n.get("chains", [])
    labw = max((len(l) for l, _ in chains), default=0)
    for label, chain in chains:
        lw = (labw * MONO_CH + 12) if labw else 0
        for i, cl in enumerate(wrap(chain, inner - lw)):
            cy += 18 if i == 0 else 16
            if i == 0 and label:
                parts.append(f'<text x="{tx}" y="{cy}" font-family="IBM Plex Mono" font-size="12" fill="{note_c}">{escape(label)}</text>')
            parts.append(f'<text x="{tx+lw:.0f}" y="{cy}" font-family="IBM Plex Mono" font-size="12" fill="{sub_c}">{escape(cl)}</text>')
    h = int(cy - y + PAD - 2)
    h += (-h) % 4
    x0, y0, x1, y1 = BX + .5, y + .5, BX + BW - .5, y + h - .5
    if focal:
        d = 14
        box = (f'<path d="M{x0+2} {y0} H{x1-d} L{x1} {y0+d} V{y1-2} Q{x1} {y1} {x1-2} {y1} H{x0+2} Q{x0} {y1} {x0} {y1-2} V{y0+2} Q{x0} {y0} {x0+2} {y0} Z" fill="{C["accent"]}"/>'
               f'<path d="M{x1-d} {y0} V{y0+d} H{x1} Z" fill="{C["shade"]}"/>')
    else:
        box = f'<rect x="{x0}" y="{y0}" width="{BW-1}" height="{h-1}" rx="2" fill="{C["paper2"]}" stroke="{C["line"]}" stroke-width="1"/>'
    return box + "".join(parts), h

def build(slug, title, desc, nodes):
    y, body, arrows = 76, [], []
    for i, n in enumerate(nodes):
        svg, h = node(n, y)
        body.append(svg)
        y += h
        if i < len(nodes) - 1:
            nxt = nodes[i + 1]
            if nxt.get("arrow_in"):
                gap = 36
                ax = BX + 60.5
                arrows.append(f'<line x1="{ax}" y1="{y}" x2="{ax}" y2="{y+gap-2}" stroke="{C["muted"]}" stroke-width="1.25" marker-end="url(#{slug}-arrow)"/>')
                if isinstance(nxt["arrow_in"], str):
                    arrows.append(f'<text x="{ax+14}" y="{y+gap/2+4}" font-family="Inter Tight" font-size="12" fill="{C["muted"]}">{escape(nxt["arrow_in"])}</text>')
                y += gap
            else:
                y += 12
    H = y + 40
    H += (-H) % 4
    rim = lambda a, b, i: (f'<linearGradient id="{slug}-rim{i}" x1="0" y1="0" x2="0" y2="1">'
                           f'<stop offset="0" stop-color="#fff" stop-opacity="{a}"/><stop offset="1" stop-color="#fff" stop-opacity="{b}"/></linearGradient>')
    svg = f'''<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="{slug}-title {slug}-desc">
<title id="{slug}-title">{escape(title)}</title>
<desc id="{slug}-desc">{escape(desc)}</desc>
<defs>
<linearGradient id="{slug}-tile" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#222529"/><stop offset="1" stop-color="#131417"/></linearGradient>
{rim(.32, .08, 1)}{rim(.14, .03, 2)}
<marker id="{slug}-arrow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{C["muted"]}"/></marker>
</defs>
<rect x="0" y="0" width="{W}" height="{H}" rx="12" fill="url(#{slug}-tile)"/>
<rect x="2.5" y="2.5" width="{W-5}" height="{H-5}" rx="10" fill="none" stroke="url(#{slug}-rim1)" stroke-width="1"/>
<rect x="10.5" y="10.5" width="{W-21}" height="{H-21}" rx="2" fill="none" stroke="url(#{slug}-rim2)" stroke-width="1"/>
<text x="{BX}" y="52" font-family="Space Grotesk" font-weight="600" font-size="20" letter-spacing="-0.2" fill="{C["ink"]}">{escape(title)}</text>
{"".join(arrows)}
{"".join(body)}
</svg>'''
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{escape(title)}</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@600&family=Inter+Tight:wght@400;600&family=IBM+Plex+Mono:wght@400&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
.diagram-container{{overflow-x:auto}}
svg{{display:block;min-width:{W}px}}
</style>
</head>
<body>
<div class="diagram-container">
{svg}
</div>
</body>
</html>
'''
    (OUT / f"{slug}.html").write_text(html)
    print(slug, W, H)

SH = "the session host, this session, or paste"
build("effort-workflow", "The effort workflow",
      "Five stages, from start to settle, with the skill that runs each stage and what it leaves.", [
    dict(tag="START", name="init-effort", note="worktree and branch (or a new repo), decided once",
         rows=[(SH, "starts the thinking session")]),
    dict(tag="THINKING", name="grilling, to-spec, to-tickets", note="leaves a spec, tickets and a handoff", arrow_in=True),
    dict(tag="HANDOVER", name="handover", note="ready, prompt, mechanism, started", arrow_in=True,
         rows=[("handoff", "writes the handoff in the repo"), (SH, "starts a fresh orchestrator")]),
    dict(tag="BUILD", name="orchestrate-with-handoff → orchestrate-effort", focal=True, arrow_in=True,
         rows=[("orchestrating", "the orchestrator's discipline"), ("implement", "each ticket, built by a sub-agent"),
               ("show-me", "shows the plan"), ("to-pr", "last step: opens the pull request")]),
    dict(tag="SETTLE", name="settle-effort", note="after you approve: merge, follow up, carry over", arrow_in=True,
         rows=[("settle-session", "leaves nothing hanging, frees what merged")]),
])
build("design-frameworks", "The design frameworks",
      "Four design skills, each with its subject and the order of stages it designs in.", [
    dict(name="low-level-design", note="code: modules, classes, files, folders",
         chains=[("", "requirements → entities and relationships → class design → implementation → extensibility")]),
    dict(name="system-design", note="systems: services, data stores, APIs, scale",
         chains=[("", "requirements → core entities → API → data flow → high-level design → deep dives")]),
    dict(name="cli-design", note="command-line interfaces: commands, flags, output, help",
         chains=[("", "requirements → command model → inputs → output and errors → help → implementation → evolution")]),
    dict(name="swift-performance", note="Swift apps: what runs, how often, at what volume",
         chains=[("build:", "workload → hot paths → budgets → work bounding → reuse → concurrency → measurement"),
                 ("diagnosis:", "symptom → reproduction → measurement → isolation → root cause → verification")]),
])
build("communication-style", "How the agent shows you its work",
      "Three show-me skills for explaining and reporting, and two skills for when you leave and come back.", [
    dict(name="show-me", note="explains the current topic",
         chains=[("", "pseudocode · call tree · file tree · diff block · one focused HTML page")]),
    dict(name="show-me-artifact", note="a report or decision set to read later, as a hosted page",
         chains=[("", "status first · progress · item tree · tables · decision cards → republished to the same URL")]),
    dict(name="show-me-diagram", note="one designed diagram, through diagram-design",
         chains=[("", "type picked to fit · profiles shipped with it · opened in a browser")]),
    dict(name="i-am-afk", note="you're away: work on alone, keep your part for the end"),
    dict(name="i-am-back", note="you're back: show-me what happened, what's done and what needs you"),
])
build("agent-setup", "Where a change to your agents goes",
      "Where a change belongs, what carries it, where skills come from and install, and the operations, audits and recap.", [
    dict(tag="WHERE", name="permission · global instruction · project AGENTS.md · skill · skill reference (no memory)"),
    dict(tag="CARRY", name="rerun set-up-machine or set-up-project where the change applies"),
    dict(tag="SOURCE", name="your skills repo, or someone else's", focal=True),
    dict(tag="INSTALLS", name="global (~/.agents/skills) or one project (.agents/skills)", arrow_in="npx skills add / update / remove"),
    dict(tag="OPERATIONS", name="install, update, move, remove, fork, publish"),
    dict(tag="AUDITS", name="which skills you use, a fresh prompt audit, a run's cost"),
    dict(tag="RECAP", name="/skill-recap", note="how a session used its skills → findings → /to-tickets"),
])
build("set-up-machine", "What set-up-machine writes",
      "Each global rule goes from rules.json through inspection, one approved diff and verification, into the shared files, every harness and the global skills; running it again is the audit.", [
    dict(name="rules.json", note="each global rule once: level, reason, instruction, samples"),
    dict(name="inspect + references", note="the agent reads each harness's files and its reference", arrow_in=True),
    dict(name="one diff, one approval", note="added, tightened, gaps, extra rules; each file backed up, then written", arrow_in=True, focal=True),
    dict(name="verify.py", note="the samples against the hook and Codex's checker; every hook wired", arrow_in=True),
    dict(name="Shared files", arrow_in=True, rows=[
        ("~/.config/agents/AGENTS.md", "the shared global instructions: working agreement, glossary, environment defaults, rule lines, personal workflow"),
        ("~/.config/agents/source.md", "the pointer to your workstation repo, where your environment defaults, workflow and personal permissions come from"),
        ("pre_tool_hook.py", "runs before every tool call; reads a command as the shell runs it")]),
    dict(name="Harnesses", rows=[
        ("Claude Code  ~/.claude/", "settings.json: deny and ask entries, the hook, auto memory off; CLAUDE.md imports the shared file"),
        ("Codex        ~/.codex/", "rules/set-up-machine.rules, hooks.json, AGENTS.md → shared file, memories off in config.toml"),
        ("opencode     ~/.config/opencode/", "opencode.json permissions, plugins/set-up-machine.js runs the hook, AGENTS.md → shared file"),
        ("Cursor       ~/.cursor/", "cli-config.json permissions, hooks.json, rules/global-instructions.mdc copies the shared file"),
        ("Pi           ~/.pi/agent/", "extensions/set-up-machine.ts runs the hook and asks for ask rows, AGENTS.md → shared file, declared settings.json defaults")]),
    dict(name="~/.agents/skills", note="your skills repo (the skills-repo environment default), installed globally"),
    dict(name="run again", note="the audit: a diff that changes nothing"),
])
build("set-up-project", "What set-up-project does",
      "set-up-project checks the machine first, then explores, asks and writes the project files after one approval; its audit flags project files that weaken a global rule.", [
    dict(name="verify.py", note="set-up-machine's check first; a machine that fails is set up before the project"),
    dict(name="explore, ask, one approval", note="tracker, triage labels, domain docs, optional environment defaults", arrow_in=True),
    dict(name="write", note="AGENTS.md, CLAUDE.md as @AGENTS.md, .gitignore, docs/agents/", arrow_in=True, focal=True),
    dict(name="audit", note="any project harness file that weakens a global rule"),
])
build("email", "How the email skill works",
      "Spark CLI reads mail, the Gmail connector acts on it, the skill says which tool does which job, and setup.md sets both up.", [
    dict(tag="READ", name="Spark CLI", note="for an email task you asked for: inbox by category, threads, pins, contacts"),
    dict(tag="ACT", name="Gmail connector", note="mark done (archive), labels, pins (stars), saved drafts on approval"),
    dict(tag="HOW", name="which tool for which job", note="what to do and when stays with you"),
    dict(tag="SETUP", name="setup.md", note="both tools, the deny and ask rules, and checks"),
])
build("wispr-flow-dictionary", "How wispr-flow-dictionary works",
      "It finds misheard terms, fixes them with words, rules or snippets behind a backup, and checks whether each fix held.", [
    dict(tag="FIND", name="terms, formatter swaps and counts", note="over any window (30m, 3h, 2d)"),
    dict(tag="FIX", name="a plain word first", note="a rule only when a mistake returns; snippets for text you repeat",
         chains=[("", "every write backs up first, can be undone, and can relaunch the app")]),
    dict(tag="CHECK", name="counts the misheard form", note="since its word was added, to see whether a fix held"),
])
