# Construction

Build each part with the technique that fits its form, in code, so a rebuild is one command and a pass changes a parameter rather than a hand edit.
Blender's Python API, run headless, is the default builder, because a script records every step and can be re-run after any change upstream.

## Techniques

| Technique | Fits | How |
|---|---|---|
| Profile and extrude | walls, facades, stands, roofs in plan | Draw the footprint or the section as a curve from measured points, extrude it, and bevel its edges. |
| Lathe | wheels, columns, domes, bowls | Revolve a measured profile around an axis. |
| Loft from silhouettes | smooth bodies, hulls, fuselages | Take the section shape from the front view, scale it per station by the top-view width and the side-view height, and build the surface through the stations. |
| Visual hull | small attached parts, such as mirrors and brackets | Keep the volume inside the outline in every view, then smooth it. |
| Modules and arrays | seats, columns, windows, railings, steps | Build one module, then place it by a rule: an array along a curve, a grid on a surface, or a list of measured positions. |
| Booleans | openings, arches, cut-outs | Subtract a simple solid. Apply booleans before smoothing, and check the result for stray faces. |
| Subdivision and bevel | hard surfaces with soft edges | Model a coarse cage and let subdivision round it; bevel the edges that catch light. |
| Generated mesh | organic one-off forms | Generate a rough mesh locally, retopologise it, and treat it as a blockout. |

## Parts and assembly

- Give each part its own script or function, its own origin and its own name, so a part can be rebuilt, scored and versioned alone.
- Assemble the whole model from the parts in one assembly script, by placement only, so a part's change never needs a change to the assembly.
- Keep the shared measurements, such as the pitch size, the roof ring radius or the wheelbase, in one facts file that every part reads, because a measurement written twice drifts.
- Name every object for what it is. Scripts that select by name, such as a render that removes a ground plane, will hit any object with a generic name.

## Repetition

Find the rule behind a repeated element before placing it: equal spacing, a count around a ring, rows that follow a rake angle.
Measure the rule from the references, such as the number of columns between two known points, and check it against an overlay.
Build the module at full detail once, because a single module can carry detail that would be unaffordable as unique geometry.

## Surfaces

- A voxel remesh gives a clean closed surface from a messy volume, but leaves faint terraces. Smooth it, then check reflections in a perspective view with an HDRI.
- Smoothing rounds corners and can shrink silhouettes; compare the shape score before and after.
- A crease that defines the form, such as a beltline or a roof edge, should be geometry, not only texture, because light reveals it.
