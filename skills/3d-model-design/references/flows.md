# Flows

A model starts from one of four inputs.
The input changes only what the References and Blockout stages do; Scorecard, Plan, Passes, Delivery and Journal run the same way for all four.

## From images

The input is photos or screenshots of the real subject, with no 3D model.

- **References:** collect views around the subject, including at least one near-top view for the plan shape and, for a building, a map or satellite view for the footprint. Solve a camera for each score view from geometry you know, such as a rectangle of known size. Gather dimensions from sources, because a camera solve needs one known length to set the scale.
- **Blockout:** build from the plan footprint upward. Extrude the footprint, cut the profile from a side or elevation view, and place the main parts at their measured heights. For a symmetric subject, build one half and mirror it.
- **What to watch:** photos differ in lighting, season and lens. Prefer score views from the same day and light, and mark the rest as check views.

## From a reference 3D model

The input is a 3D model of the subject that can be viewed but not used, such as a model in a web viewer that is not downloadable or not licensed for reuse.

- **References:** capture the viewer from fixed cameras. Orthographic front, side, rear and top views give blueprints with a known scale; perspective diagonals give check views. Record each camera exactly, so a render can match it pixel for pixel. Capture with the viewer's own plain light and background, and turn off its interface, logos and shadows where it allows.
- **Blockout:** trace the silhouettes into a volume, such as a loft or a visual hull, and place the parts the views show.
- **What to watch:** the reference model has its own mistakes. Where it disagrees with photos of the real subject, the photos win, and the scorecard should say which views come from which source.

## From a low-detail model to a detailed one

The input is your own or a downloaded low-detail model, and the goal is a detailed, realistic one.

- **References:** the low-detail model is not the reference; the real subject is. Collect references as in the first two flows, and score the low-detail model as the baseline.
- **Blockout:** the low-detail model is the blockout when its scale and proportions score well. Fix its proportions first if they do not.
- **What to watch:** the low-detail model's topology rarely carries detail well. Plan which parts to keep and which to rebuild, part by part.

## From one model to another

The input is a usable 3D model, and the goal is a different model: a restyle, a conversion, a variant or a different level of detail.

- **References:** the target look, such as a style benchmark or a photo of the variant. When the goal is a lighter version, the source model is itself the reference, and the score compares the two from the same cameras.
- **Blockout:** the source model.
- **What to watch:** licences. Use a source model only when its licence allows it, and record the licence in the reference manifest.

## Generated starting meshes

Image-to-3D generators, such as TRELLIS and Hunyuan3D, which can run locally, make a rough mesh from one or a few images.
Use one only as a blockout for an organic or one-off object, never for architecture or anything with exact repetition, because generators lose scale, symmetry and repeated structure.
Score a generated mesh like any blockout before building on it.
