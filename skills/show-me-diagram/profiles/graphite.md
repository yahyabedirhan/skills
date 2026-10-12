# Profile: Graphite

The look of the Swift Lab, Shipyard and skills logos: folded white paper on a dark granite tile. Use it for anything shown beside those apps, or for a crafted dark diagram on a website.

## Diagram types

Any upstream type. It suits Flowchart, Swimlane, Layer stack and Loop best, where the folded focal nodes lead the eye along a path.

## Diagram style

Minimal dark.

## Look

Only the focal elements fold, so the folds stay a signal, like the accent they replace.

- **Ground:** fill the page with the tile's vertical gradient, `#222529` at the top to `#131417` at the bottom, with no dot grid.
- **Frame:** draw a double rim around the diagram area, as the logos do. The outer rim is 1px white at 32% opacity at the top, fading to 8% at the bottom. The inner rim sits 8px inside it, at 14% fading to 3%. Corner radius 10.
- **Nodes:** crisp paper, with corner radius 2 and type tags at radius 0. Fill ordinary nodes with `paper-2` and a 1px `rule` outline.
- **Focal nodes:** fold them. Fill the node with `accent` (white), and set its name and sublabel in `paper`. Cut the top-right corner as a 14px dog-ear: a right triangle in `shade`, with the cut edge at 45°.
- **Focal arrows:** end them with a folded arrowhead: a triangle split along its axis, the left half in `shade` and the right half in `accent`, as in the Swift Lab icon.
- **Callouts:** upright, not italic.

## Palette

The logos' greys, with one cool blue for links. `shade` is the folded face of the paper, used only in the folds.

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

## Typography

Geometric and engineered, like the folds: no serif.

| Role | Family | Weight |
|---|---|---|
| `title` | Space Grotesk | 600, tracking -0.01em |
| `node-name` | Inter Tight | 600 |
| `sublabel` | IBM Plex Mono | 400 |
| `callout` | Inter Tight, not italic | 400 |

Use IBM Plex Mono for all technical text.
