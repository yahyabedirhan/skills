# Glossary

These are the words this skill uses, each defined once.
Use them the same way every time, and explain one to the user the first time it matters, because a consistent vocabulary is how a newcomer learns the craft.

## Geometry

**Mesh**: the surface of a model, made of vertices joined into polygons. Renderers draw it as **triangles**, so budgets count triangles.

**Topology**: how the polygons of a mesh connect. Clean topology follows the form, such as rings of quads around a wheel arch; messy topology, such as from a voxel remesh, renders fine but is hard to edit by hand.

**Normal**: the direction a surface faces at a point. Smooth shading blends normals across polygons; flat shading shows each polygon as a facet. Wrong normals show as dark patches or ripples in reflections.

**Silhouette**: the outline of a model against the background from one view. It is the most robust thing to compare with a reference.

**Blockout**: the first version of a model, every part in its simplest form at the right size and place, with no detail.

**Part**: a piece of a model that can be built, scored and versioned on its own, such as a roof or a wheel.

**Module**: a part that repeats, such as a seat, a column or a window, built once and placed many times.

**Instancing**: drawing many copies of one module from one mesh and a list of positions, which costs one draw call instead of one per copy.

**Loft**: a surface swept through a series of cross-sections, such as a car body built from its section at each station along its length.

**Visual hull**: the largest volume consistent with a set of silhouettes: every point that projects inside the outline in every view.

**Boolean**: cutting or joining one mesh with another, such as subtracting a cylinder to cut a wheel arch.

**Modifier**: a non-destructive operation in Blender, such as subdivision, mirror, array, bevel, decimate or smooth, applied when the model is exported.

**Retopology**: rebuilding a messy mesh as a clean one over the same shape.

**Decimation**: reducing the triangle count of a mesh while keeping its shape.

## Surface

**Material**: how a surface responds to light. This skill uses **PBR** (physically based rendering) materials with base colour, roughness, metalness and normal.

**Base colour**: the colour of a surface without lighting, also called albedo.

**Roughness**: how blurred a surface's reflections are, from 0 (mirror) to 1 (chalk).

**Metalness**: whether a surface reflects like a metal (1) or a dielectric such as paint or plastic (0).

**UV map**: the 2D coordinates that place a texture on a 3D surface. **Projection UVs** come from projecting the surface onto an image from a camera.

**Texture**: an image used by a material, such as a base colour, roughness or normal texture.

**Atlas**: one texture that holds the textures of many parts, so they share one material and one draw call.

**Texel density**: texture pixels per metre of surface. Even texel density keeps detail consistent across a model.

**Decal**: a small texture placed on top of a surface, such as a sign, a number or a crest.

**Trim sheet**: a texture of strips (edges, panels, rails) that many parts reuse by mapping their UVs onto a strip.

**Baking**: rendering detail from a high-poly model or a lighting setup into a texture for a low-poly model, such as a normal map or ambient occlusion.

**Ambient occlusion**: the darkening of creases and corners that ambient light reaches less.

**Material class**: one of the few kinds of surface the scorer tells apart, such as paint, glass, dark plastic, metal and light.

## Light and rendering

**Render**: an image of the model made by a renderer. Blender has **Cycles**, a path tracer, and **EEVEE**, a real-time engine. three.js renders in the browser with WebGL.

**HDRI**: a panoramic image used as the environment light and reflection.

**Orthographic view**: a view without perspective, where size does not shrink with distance. Blueprint views of front, side and top are orthographic.

**Perspective view**: a view like a camera's, set by a **focal length** or field of view.

**Camera solve**: recovering a reference photo's camera position, direction and focal length, so a render from that camera matches the photo.

## Delivery

**GLB**: the binary form of glTF, the standard file for 3D on the web, holding meshes, materials and textures in one file.

**Draw call**: one request from the renderer to the GPU. Fewer draw calls render faster; each material on each mesh costs at least one.

**Level of detail (LOD)**: lighter versions of a model shown when it is small on screen or while the camera moves.

**Budget**: the limits the delivered model must meet: triangles, draw calls, texture memory, file size and frame time.

## Method

**Reference**: an image, model or viewer capture that shows the real subject. A **score view** is a reference the score compares against; a **check view** is one the score never uses, kept to catch overfitting.

**Reference manifest**: the list of references, each with its source, date, content, role and solved camera.

**Scorecard**: the views, measures, targets and plateau rule that define how close the model is.

**Pass**: one change for one named cause, followed by a full score.

**Checkpoint**: the saved record after the blockout and after each pass: the score, the images and one paragraph.

**Diagnosis map**: an image that shows where a measure loses points, such as the pixels where the model's class differs from the reference's.

**Ceiling**: the best score a measure can reach with the current approach, found by scoring the approach's own ideal input, such as the traced material maps, against the reference.

**Plateau**: three scored passes that together raise the overall score by less than 1 point.

**Craft checklist**: the details a benchmark-quality model of the subject shows, each counted present or missing.

**Journal**: the HTML page that tells how the model was built.
