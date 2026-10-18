# Profile: Graphite

The look of the Shipyard and skills logos: folded white paper on a dark granite tile. Use it for anything shown beside those apps, or for a crafted dark diagram on a website.

## Diagram types

Any upstream type. It suits Flowchart, Swimlane, Layer stack and Loop best, where the folded focal nodes lead the eye along a path.

## Diagram style

Minimal dark.

## Look

Only the focal elements fold, so the folds stay a signal, like the accent they replace.

- **Ground:** make the diagram the tile. Fill the diagram area with the tile's vertical gradient, `#222529` at the top to `#131417` at the bottom, with no dot grid, and keep the page around it flat `paper`. A gradient on the whole page shows a seam at the diagram's edge.
- **Label masks:** fill them with the same gradient, in `userSpaceOnUse` coordinates, so each mask matches the ground behind it. A flat fill shows as a dark patch.
- **Frame:** draw a double rim inside the tile's edge, as the logos do. The outer rim is 1px white at 32% opacity at the top, fading to 8% at the bottom. The inner rim sits 8px inside it, at 14% fading to 3%. Keep the corners concentric: radius 12 for the tile, 10 for the outer rim and 2 for the inner rim.
- **Nodes:** crisp paper. Give step nodes corner radius 2 and type tags radius 0. Keep the upstream pill for start and end nodes, since the shape tells them apart. Fill ordinary nodes with `paper-2` and outline them in `line`. The fill matches the top of the tile, so the outline carries the edge.
- **Focal nodes:** fold them. Fill the node with `accent` (white), with no outline. Set its name and sublabel in `paper`, and its secondary text, such as a description or a phase label, in `fold-muted`. Cut the top-right corner as a 14px dog-ear: a right triangle in `shade`, with the cut edge at 45°.
- **Focal arrows:** end them with a folded arrowhead, at least 14 × 12: a triangle split along its axis, one half in `shade` and the other in `accent`, as in the logos. A smaller head hides the split.
- **Callouts:** upright, not italic.

## Palette

The logos' greys, with one cool blue for links. Graphite adds three roles that upstream has none for. `shade` is the folded face of the paper, used only in the folds. `fold-muted` is secondary text on a folded node. `line` is a node outline, stronger than the `rule` hairlines.

| Role | Value |
|---|---|
| `paper` | `#131417` |
| `paper-2` | `#222529` |
| `ink` | `#e4e6e9` |
| `muted` | `#8b9097` |
| `soft` | `#6b7078` |
| `rule` | `rgba(255,255,255,0.10)` |
| `accent` | `#ffffff` |
| `accent-tint` | `rgba(255,255,255,0.06)` |
| `link` | `#9db3c8` |
| `shade` | `#b9bec4` |
| `fold-muted` | `#4f545b` |
| `line` | `rgba(255,255,255,0.16)` |

## Typography

Geometric and engineered, like the folds: no serif.

| Role | Family | Weight |
|---|---|---|
| `title` | Space Grotesk | 600, tracking -0.01em |
| `node-name` | Inter Tight | 600 |
| `sublabel` | IBM Plex Mono | 400 |
| `callout` | Inter Tight, not italic | 400 |

Use IBM Plex Mono for all technical text.
