# References and cameras

A reference is only useful for scoring when you know the camera that took it.
Collect few references, solve each one's camera, and record both in the reference manifest.

## Sources

Go down this list, and stop when every side of the subject that is in scope is covered:

1. **Viewers you can drive:** Google Earth's 3D view and Google Maps' satellite and 3D views for buildings and places, Sketchfab and other web viewers for reference models. A drivable viewer gives any angle, a known up direction and often orthographic views.
2. **Official and architectural material:** the architect's and engineers' project pages, plans, sections and elevations. A drawing with a scale bar is the best source of dimensions.
3. **Open photo archives:** Wikimedia Commons categories, Mapillary street-level images, and sites that document the subject, such as stadium or vehicle databases.
4. **Social media and video:** recent photos and video frames, for the current state of a subject that changes, such as signage or seats.
5. **Web search** for facts: dimensions, counts, materials and dates, each with its source.

Capture public pages only, with the user's browser when a page needs it.
Use the newest references for a subject that changes, and record the date of each, because a model mixing two eras matches neither.

## Capture

- **Orthographic captures:** when a viewer offers an orthographic camera, capture front, side, rear and top with the same scale. Measure the scale in pixels per metre from a known length, and record it.
- **Fixed perspective cameras:** for diagonals and corners, set the viewer's camera numerically when it allows, such as through the URL or a script, so the capture is repeatable.
- **Plain conditions:** capture with the viewer's plain light, a plain background and its interface hidden, at a fixed window size, because every difference that is not the subject costs score points that no pass can earn back.
- **Video frames:** pick sharp frames, record the timestamp, and treat each frame as a photo.
- **Interior views:** for a subject whose inside is in scope, capture views from where a person stands, such as seats in a stadium or the driver's seat in a car.

## The reference manifest

Keep one file, such as `references/manifest.json`, with one entry per reference:

```json
{
  "id": "ge-ne-45",
  "file": "references/ge-ne-45.png",
  "source": "Google Earth 3D, https://earth.google.com/...",
  "captured": "2026-11-25",
  "shows": "north-east corner from 45 degrees above",
  "role": "score",
  "camera": { "kind": "perspective", "position": [0, 0, 0], "target": [0, 0, 0], "up": [0, 0, 1], "fov_deg": 35, "solved_by": "pnp, 8 points, 1.2 px error" }
}
```

`role` is `score`, `check` or `fact`: a fact reference gives a dimension or a detail but is never compared pixel by pixel.

## Solving a camera

Solve the camera of every score view and check view.

- **Orthographic captures:** the camera is the capture's direction, its scale in pixels per metre and the pixel of one known point. Check it by rendering a box of known size from it.
- **Photos with known points:** mark six or more points whose 3D positions you know, such as the corners of a pitch, the base and top of a tower, or the ends of a wall, and solve the pose and focal length with OpenCV's `solvePnP` and `calibrateCamera`, or with fSpy and its Blender importer from vanishing lines. A large known rectangle on the ground, such as a pitch or a car park, makes the solve strong.
- **Check the solve:** render the blockout from the solved camera and overlay its outline on the reference. An error over a few pixels at known points means a wrong point or a wrong dimension; fix it before scoring, because every later score inherits the error.
- **Iterate the solve with the model:** as the model improves, re-solve with more points read from it, since a better model gives better known points.

## Facts

Record each dimension, count and material with its source in the brief or a `facts.md` file.
When two sources disagree, record both and say which the model uses and why.
When no source states a fact, measure it from a solved reference and mark it measured, so a later reader knows how certain it is.
