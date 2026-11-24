# WebGL delivery

Detail and speed are separate concerns: build the model at full detail, then deliver it so a browser draws it fast.
Measure the delivered file against the brief's budgets, and render the score views from it again, because export steps can lose detail.

## Budgets

Rough figures for one model on a modern laptop in WebGL, to adjust in the brief:

| Kind of model | Triangles | Draw calls | Texture memory |
|---|---|---|---|
| A prop or vehicle in a scene | 20k–100k | under 20 | under 32 MB |
| A hero building viewed alone | 0.5M–3M with instancing | under 200 | under 256 MB |

Count instanced triangles separately: a million seats from one instanced module cost one draw call but still cost vertex work.

## Making it light

- **Decimate** where the detail is invisible, and compare the silhouette before and after.
- **Join by material:** merge every part that shares a material into one mesh, because each material on each mesh costs a draw call.
- **Instance** modules: three.js `InstancedMesh` in code, or the `EXT_mesh_gpu_instancing` glTF extension in a GLB. Check that the exporter and the loader in use support it before relying on it.
- **Compress textures:** JPEG or WebP for colour, and halve any texture whose texels are larger than the pixels it covers on screen.
- **Levels of detail:** a lighter mesh for far views, chosen by screen size with three.js `LOD`.
- **Progressive quality:** draw a light version while the camera moves and the full one when it stops, or lower the pixel ratio during motion. This keeps orbiting smooth without lowering the model's detail.

## Exporting a GLB from Blender

- glTF is Y-up: the exporter turns Blender's Z-up scene, so turn it back in the loader when the target is Z-up.
- Every node a modifier or a material needs must be exportable: the exporter keeps image textures linked to the Principled BSDF, and drops procedural nodes and mix nodes, so bake those to images first.
- Hidden objects still count in bounds in many tools; remove an optional part from the scene instead of hiding it.
- Check the exported file's contents: the primitives per material, the vertex and triangle counts, and the image sizes and formats.

## 3D Studio

Deliver into 3D Studio with `/3d-studio`: one component per part and one for the whole model, a version per delivered take, variants for looks or levels of detail.
A sealed version copies the library files it imports, including GLB files, so keep heavy files few and reuse them across versions.
Check every variant, measure it with `perf`, shoot it, and seal it; show the user with `app show`.
