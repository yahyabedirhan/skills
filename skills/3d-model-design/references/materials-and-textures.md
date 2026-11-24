# Materials and textures

Materials make a correct shape read as a real thing.
Use PBR materials throughout, because Blender, glTF and three.js all speak base colour, roughness, metalness and normal the same way.

## Choosing how a surface gets its look

| Surface | Approach |
|---|---|
| Large plain areas, such as paint, concrete, grass or glass | A material with constant values or a tiling texture. |
| Repeated detail, such as seats, cladding panels or bricks | A tiling texture or a trim sheet shared by every module. |
| Unique detail in known places, such as lamps, signs, crests or markings | An atlas or decals, placed from the references. |
| Fine geometry that is too costly to model, such as grooves, vents or bolts | A normal map baked from a detailed model or drawn. |

Free CC0 textures and HDRIs from Poly Haven and ambientCG cover most generic surfaces, such as concrete, steel, grass and asphalt.

## Traced material maps

When a reference shows where each material is, such as an orthographic capture, trace the material layout rather than the pixels:

1. Sort each reference pixel into a material class with fixed colour rules.
2. Clean the class map: fill badges and other unwanted marks from their surroundings, remove speckles with a majority filter, and make it symmetric when the subject is.
3. Paint your own colour for each class into an atlas, with lines in a slightly different tone of the same class where the reference shows design lines, such as lamp internals or panel seams.
4. Give every face atlas UVs by projecting it onto the reference view it faces most directly.

This keeps the model's look your own while every detail lands where the reference has it.
Its limits: the detail is flat, so it reads best from a distance, and a face seen by two views can take only one view's colour.

## Values that read correctly

- Keep each material's rendered value inside its class, with margin, under the score light. Check it from the rendered values per class after each material pass.
- Real paint, plastic and glass reflect about 4 % at facing angles and much more at grazing angles. A dark material in a bright reflective environment turns grey at its edges.
- Real-world base colours are darker than they look: fresh snow is about 0.8, concrete about 0.35, asphalt about 0.05. Bright base colours make a model look like a toy.

## Atlases and texel density

- Pack the textures of parts that share a material into one atlas, so the parts can join into one mesh and one draw call.
- Keep texel density even across parts at the size the model is seen. Raise it only where the camera goes close, such as the seats near a viewing position.
- Leave a few pixels of padding around each region in an atlas, because texture filtering samples beyond the edges.

## Baking

Bake when the delivered model must look like a heavier one: normals from a detailed model onto a light one, or ambient occlusion into the base colour of static parts.
Bake in Blender with Cycles, then check the baked result under the delivery renderer, because a bake that looks right in Blender can show seams in three.js.
