# Scoring

The score says how close the model is to its references, from views whose cameras are solved, as numbers from 0 to 100.
It exists so that every pass is judged by the same ruler and progress is measured, not felt.

## The views

- **Score views:** the solved references the score compares against. Cover the subject's main sides, the top, and the diagonals and corners, because a model can match the sides and still be wrong at the corners. For a subject with an inside in scope, add interior views.
- **Check views:** at least two solved references the score never uses, such as a low diagonal and a close-up. Score them at every checkpoint but never tune on them; when a pass raises the score views and lowers a check view, the pass overfits.
- **Weights:** weight every view equally unless the brief says one matters more, such as the drone view of a stadium.

## The comparison render

Render the model from each solved camera at the reference's pixel size, so the two images align pixel for pixel.
Render under light like the reference's: a viewer capture under even, unshadowed light with dark reflections; a daylight photo under a sun at the photo's direction.
A fair render matters more than any measure, because a lighting difference moves every surface across the class thresholds below.
Keep the score render separate from the realistic render the user sees in check views and the journal.

## The measures

For each view, compute three measures:

- **Shape:** the intersection over union of the two silhouettes. It is robust across styles and lighting, and it is the first measure to raise.
- **Materials:** sort every pixel inside both silhouettes into material classes, such as paint, glass, dark plastic, metal and light, by fixed colour rules applied to both images. The measure is the mean intersection over union of the classes present in the reference. For photos whose colours vary with light, use a part segmentation instead, such as SAM 2 masks for roof, stands, facade and ground, and compare part by part.
- **Lines:** the edges of both images, such as Canny edges inside the silhouettes, and the F-score of edges that agree within a few pixels. It rewards panel lines, window frames and part outlines in the right places.

The view's score is the mean of the three; the overall score is the mean over views.
A semantic similarity, such as the cosine of DINOv2 features, can break ties between two passes with near-equal scores, but it is never the gate, because it rewards looking similar in kind, not being right.

Score each reference against itself once: every measure must return 100. Anything less means the classifier or the mask is broken.

## Diagnosis maps

After every score, write the images that show where points were lost, because they find the next pass in minutes:

- **Silhouette overlay:** reference-only pixels in one colour, model-only pixels in another.
- **Class confusion:** a table of reference class against model class, and a map of each class's misses and extras.
- **Edge map:** reference edges the model misses, and model edges the reference lacks.
- **Rendered values per class:** the model's median luminance and saturation inside each reference class, which shows a material sitting on the wrong side of a class threshold.

## The ceiling

At a plateau, compute what the current approach can reach at best: score the approach's ideal input, such as the traced material maps or a perfect silhouette, against the reference.
Where the ceiling is low, the approach itself limits the score; change the technique or accept the limit and tell the user.
Where the ceiling is high but the score is low, the rendering or the geometry loses the points; the diagnosis maps show where.

## The craft checklist

The score measures closeness; the craft checklist measures detail.
Study the quality benchmark and list the details it shows for its subject, translated to yours: for a stadium, individual seats, aisle stairs, railings, roof structure, floodlights, screens, pitch markings and facade columns.
At each checkpoint, count each detail present or missing, and put the benchmark and the model side by side in the same kind of view.
Report the checklist as present out of listed, beside the score.

## Targets and stopping

Set targets from the quality level in the brief. A hero model, for example, aims for shape 95 or more and overall 80 or more on its score views.
Stop raising the score when every target is met, or at a plateau after diagnosis shows the remaining loss is structural.
Report honestly: the score, the ceiling, the check views and the craft checklist together, with the limits named.
