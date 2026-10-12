# Profiles

The diagram-design profiles this skill ships. A profile is a saved set of choices, one per layer below, applied on top of diagram-design's style guide. A layer a profile leaves out keeps the upstream default.

| Profile | File | Use it for |
|---|---|---|
| Cursor Dark (default) | [cursor-dark.md](cursor-dark.md) | any diagram, read in a dark editor |
| Navy Blue | [navy-blue.md](navy-blue.md) | a calm dark diagram for slides or a README |
| Shipyard Green | [shipyard-green.md](shipyard-green.md) | anything about Shipyard or my agent work, in its icon's olive green |
| Parchment | [parchment.md](parchment.md) | a story or a process, on warm paper |

## The shape of a profile

Every profile has these sections, in this order, from what the diagram is to how it looks. Name things by their upstream names in diagram-design's `SKILL.md` and `references/style-guide.md`, and don't restate upstream rules.

```markdown
# Profile: <name>

<one line: the look, and when to use it>

## Diagram types
Upstream visual types this profile suits, by name (Flowchart, Layer stack, ...).

## Diagram style
Upstream variants it uses: Minimal light, Minimal dark or Full editorial, plus Sketchy when wanted.

## Look
Only what differs from upstream: density, stroke width, corner radius, spacing, emphasis.

## Palette
| Role | Value |   # upstream semantic roles: paper, paper-2, ink, muted, soft, rule, accent, accent-tint, link

## Typography
| Role | Family | Weight |   # title, node-name, sublabel (mono), callout (notes)
Google Fonts families, so the font link can load them.
```

To add a profile, copy this shape and add a row to the table above.

## How to check a profile

Render the same upstream examples, `assets/example-flowchart.html` and `assets/example-layers.html`, with each profile's palette and fonts swapped in, and screenshot them in a headless browser. Compare them side by side: the fonts load, every label reads against its ground, and the accent marks only the focal nodes.
