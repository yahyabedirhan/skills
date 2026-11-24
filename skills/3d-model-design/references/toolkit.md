# Toolkit

Every tool here is free.
Install what a project needs and record what you installed in the project's README, so the user knows what is on their machine.
Ask before using a paid service; none is a default.

## Building and rendering

- **Blender, headless:** `blender -b --factory-startup --python build.py -- <args>` runs a build script without a window. Keep each script deterministic, so the same inputs give the same model. Blender 4 and later name the Principled BSDF inputs `Coat Weight`, `Emission Color` and `Specular IOR Level`.
- **Cycles:** use it for score renders, because its light paths can be controlled exactly: a world that lights diffuse rays evenly and shows glossy rays a dim colour, set with the Light Path node. Use the GPU, such as Metal on a Mac; the first render compiles kernels for several minutes.
- **EEVEE:** fast previews and turntables. It ignores some light-path tricks, so it is not the score renderer.
- **blender-mcp** (`ahujasid/blender-mcp`): a Blender add-on and MCP server that let an agent run Python in a live Blender window and look at the viewport. Useful for interactive sessions and visual checks; the headless scripts stay the source of truth.
- **ffmpeg:** turntable videos and GIFs from rendered frames.

## Measuring and image work

- **Python with numpy, scipy, scikit-image, pillow and opencv-python:** masks, class maps, edges, scores, diagnosis maps and image composites. Keep it in a project virtual environment, made with `uv`, and run scripts with `python -I`.
- **OpenCV calibration:** `solvePnP` and `calibrateCamera` solve a reference photo's camera from known points.
- **fSpy** with its Blender importer: solves a camera from vanishing lines in a photo of a building.
- **SAM 2** and **DINOv2**, run locally: part masks for photos whose colours vary, and a semantic similarity tiebreak.

## Capturing references

- **Playwright:** drives web viewers headless with fixed window sizes and scripted cameras, for repeatable captures.
- **The user's Chrome,** through Claude in Chrome: pages that need the user's session or a real browser, such as Google Earth's 3D view. Hide the interface and fix the window size before capturing.
- **Web search and fetch:** facts and image sources.

## Delivering

- **Blender's glTF exporter:** GLB with JPEG or WebP textures.
- **three.js:** the runtime. Load a GLB with `GLTFLoader`, instance modules with `InstancedMesh`, switch detail with `LOD`.
- **3D Studio,** through `studio3d` and `/3d-studio`: components, versions, variants, checks, shots, performance measures and the user's app.

## Generating

- **TRELLIS and Hunyuan3D,** run locally where the machine allows: a rough starting mesh from images, for organic one-off objects only.
