---
name: 3d-model-design
description: Design, build, improve or assess a 3D model of a real or imagined thing through the 3D model delivery framework, as an experienced 3D artist would. Use when making a 3D model from reference images, from a reference 3D model, or from a low-detail model; when scoring how close a model is to its references; when preparing a model for WebGL or 3D Studio; or when the user asks how something in 3D works.
---

# 3D model design

Build a 3D model the way an experienced 3D artist builds one: understand the subject first, measure before judging, and construct the model **cumulatively**, part by part and pass by pass, so every step adds to the last instead of starting over.
Follow the **delivery framework** in every session, whether the model is new, improved or only assessed, so the user always finds the same things in the same places.
Speak with the words in [glossary.md](references/glossary.md) and use each word the same way every time, because a user who is new to 3D learns the craft from your consistent language.

The recurring failure is the **one-shot**: generating a whole model, scoring it, throwing it away and generating another.
One-shots never converge, because nothing learned in one survives into the next.
Build instead: each part keeps what earlier passes proved, and each pass changes one thing and measures it.

The second failure is **vibe judgement**: calling a model good because it looks good from the one angle you checked.
Every claim of quality rests on a number from the **scorecard**, and on **check views** the score never saw.

## Steps

1. **Restate the session's purpose in one line**, read from the request and its context, so a misreading costs one reply.
   - **Building a new model:** walk every stage of the framework.
   - **Improving an existing model,** such as a low-detail model to a detailed one: assess it first through References and Scorecard, then run Plan, Passes, Delivery and Journal on it.
   - **Assessing a model:** run References and Scorecard only, and report the score with its diagnosis.
   - **Answering a question about 3D:** answer from the glossary and the references, with a small example or a render where one helps.
2. **Agree the brief and the quality level** before anything is built (see Brief). Be honest about cost: a recognisable low-poly model takes an hour, and a model a person can mistake for the real thing takes days of passes.
3. **Choose the interaction mode** from the request:
   - **Interactive:** present each stage's product and wait for the user before the next stage.
   - **All in:** run the stages on your own. Report to the user only at each scored **checkpoint**, at a **plateau**, when blocked, and at the end.
   Both modes walk the same stages and keep the same records, so the method stays visible either way.
4. **Work through the delivery framework** below, stage by stage, reading a reference when its stage reaches it.
5. **Finish with the journal** and tell the user where the model, the checkpoints and the journal are.

## The delivery framework

```text
Brief → References → Scorecard → Plan → Blockout → Passes ⟲ → Delivery → Journal
                                          └── checkpoint after the blockout and after every pass
```

Each stage rests on the one before it: the references define what "right" means, the scorecard turns that into numbers, the plan splits the work so each part can be measured, and the passes raise the numbers one cause at a time.
Go back to an earlier stage when a later one exposes a gap, such as a pass that needs a view the references lack.
The four ways a model starts, from images, from a reference model, from a low-detail model or from another model, change only what References and Blockout do; [flows.md](references/flows.md) has each one.

### Brief

Write down, in a few lines, what the model is and what it is for:

- **Subject:** what it is, which version or year of it, and what is in and out of scope, such as "the stadium bowl as a spectator sees it, not the corridors behind the stands".
- **Quality level:** one of **blockout** (shape only), **game-ready** (recognisable, light, textured) or **hero** (detailed enough to pass for the real thing up close). The level decides how many passes the plan holds and when to stop.
- **Where it runs:** for WebGL and 3D Studio, the delivery budgets: triangles, draw calls, texture memory and file size. Detail and speed are separate concerns: build the detail, then deliver it fast with the techniques in [webgl-delivery.md](references/webgl-delivery.md).
- **Identity rules:** whether names, logos, crests or plates may appear. Ask when the subject carries any, because the answer changes the textures.
- **The quality benchmark:** a model or viewer of a similar subject at the quality the user wants, used for a side-by-side craft comparison, not for scoring.

### References

Collect just enough reference to know the subject from every side that matters: front, sides, back, top, the diagonals, and the inside when the inside is in scope.
Record each one in the **reference manifest** with its source, date, what it shows, and whether it is a **score view** or a **check view**.
Solve a **camera** for every reference you will compare against: its position, direction and focal length, so a render from that camera lands on the reference pixel for pixel.
Gather the facts a modeller needs, such as dimensions, counts and materials, each with its source, and mark what no source states as a gap.
[references-and-cameras.md](references/references-and-cameras.md) covers sources, capture and camera solving.

### Scorecard

Define the score before building, so every later pass is judged by the same ruler:

- **The views:** the score views, with their solved cameras, and at least two check views that the score never uses, because a model tuned only on score views overfits them.
- **The measures:** shape, materials and lines per view, each from 0 to 100, plus the overall score as their mean. [scoring.md](references/scoring.md) defines each measure and how to render a fair comparison.
- **The craft checklist:** the details a benchmark-quality model of this subject shows, each counted present or missing at every checkpoint.
- **The targets** per measure, set from the quality level, and the **plateau rule**: when the overall score rises less than 1 point across three scored passes, stop and diagnose before the next pass.

Score the references against themselves first. Each must score 100, or the measuring is broken.

### Plan

Split the model into **parts**: pieces that one person could build alone and that the score can see separately, such as the roof, the facade columns and the stands of a stadium.
For each part, write the technique that builds it, the references that show it, and the measure that proves it.
Find the repetition, such as seats, columns and windows, and plan it as one **module** placed many times, because repetition built by hand drifts and costs memory.
Order the passes from large to small: shape before materials, materials before details.
[construction.md](references/construction.md) has the techniques and when each fits.

### Blockout

Build every part in its simplest form at the right size and place, and score it.
The blockout proves the cameras, the scale and the scoring pipeline end to end before any detail exists.
A blockout whose shape score is far from the target means the proportions or the cameras are wrong. Fix that now, because every detail added on a wrong blockout is rework.

### Passes

Raise the score one **pass** at a time.
A pass names its one cause, such as "the roof edge is 2 m too low in the side view", changes only what that cause needs, rebuilds, and scores every view.

- **Before each pass:** read the **diagnosis maps** from the last score, find the largest loss, and name its cause.
- **After each pass:** keep the change only if the overall score rose and no check view got worse; otherwise revert it and record why.
- **Every few passes:** render the check views and the benchmark side by side, because the score can rise while the model gets worse where no score view looks.
- **At a plateau:** stop and diagnose. Compute the **ceiling** of each measure, find which loss is structural and which is fixable, and either change the technique or report to the user that the measure has reached what this approach can give.
- [materials-and-textures.md](references/materials-and-textures.md) covers material passes.

### Checkpoints

After the blockout and after every pass, save a checkpoint, so the user can follow the work in the file system without asking:

- the score table and its change since the last checkpoint;
- side-by-side images of the model and the reference at every score view, and the check views;
- a turntable GIF or video for the larger milestones;
- one paragraph: what the pass changed, why, and what is next.

[project-layout.md](references/project-layout.md) fixes where checkpoints live and how they are named.
In all-in mode, send the user a short report with the score table and two or three images at each scored checkpoint.

### Delivery

Prepare the model for where it runs: decimate where detail is invisible, join parts by material, instance the modules, compress textures and add **levels of detail**.
Measure triangles, draw calls, texture memory, file size and frame time against the brief's budgets, and render the score views again from the delivered file to prove nothing was lost.
For 3D Studio, make the parts and the whole model into components and versions, and check, shoot and seal them with `/3d-studio`.
[webgl-delivery.md](references/webgl-delivery.md) has the techniques.

### Journal

Write one HTML page that tells how the model was built: the brief, the references, the scorecard, the plan, each checkpoint with its images and score, the final score against the targets, the benchmark comparison, and the honest limits.
The journal is the user's record of the method, so write it for someone who was not there.

## Lessons

Each lesson came from a real build; the reason beside it is what makes it general.

- **Trace classes, not pixels.** Tracing a reference's pixels copies its texture, its lighting and its logos. Sort the reference into material classes and paint your own colours, so the model owns its look.
- **Render the comparison under the reference's light.** Reflections and occlusion move dark and light materials across class thresholds. Match the reference viewer's light in the score render, and keep a realistic render for the check views.
- **Keep every colour away from a class threshold.** A silver of luminance 202 scored as "light" until it was moved to 186; a tail lamp red scored as paint. Check each material's rendered value against the classifier.
- **One surface, one colour.** A face that two views both see can take only one view's texture, so the geometry has to agree with every view. When two views disagree about the same pixels, fix the shape, not the texture.
- **A detached part drops out of a largest-blob mask.** When a part such as a mirror floats free of the body, the silhouette mask loses it. Root parts into what they attach to.
- **Scripts that filter by name hit innocent objects.** A render script that deleted every `Plane` also deleted the number plates. Name every object for what it is.
- **Smoothing trades score for realism.** The surface that scored best rippled in reflections. Judge surface quality in a perspective check view with a reflective environment.
- **Read the confusion before the next pass.** Per-class confusion and edge maps showed in minutes what guessing missed for hours.
- **Know the ceiling.** Scoring the traced maps against the reference showed which losses no geometry could fix, which ended a plateau honestly.
- **Keep the loop tight.** A full rebuild, render and score in about two minutes allows dozens of passes. The first GPU render compiles its kernels for minutes, so time the second one.

## References

- [glossary.md](references/glossary.md): the 3D words this skill uses, each defined once.
- [flows.md](references/flows.md): the four ways a model starts, and what each changes in References and Blockout.
- [references-and-cameras.md](references/references-and-cameras.md): finding and capturing references, the manifest, and solving each reference's camera.
- [scoring.md](references/scoring.md): the measures, the fair comparison render, diagnosis maps, the ceiling, the craft checklist and the plateau rule.
- [construction.md](references/construction.md): the techniques that build parts, and when each fits.
- [materials-and-textures.md](references/materials-and-textures.md): PBR materials, atlases, traced material maps, decals and baking.
- [webgl-delivery.md](references/webgl-delivery.md): GLB export, budgets, instancing, levels of detail and progressive quality.
- [toolkit.md](references/toolkit.md): the free tools, what each is for and how to drive it.
- [project-layout.md](references/project-layout.md): the folder of a model project, its checkpoints, its journal and its 3D Studio project.
