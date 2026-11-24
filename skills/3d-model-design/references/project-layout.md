# Project layout

Each model is its own project: one git repository, one folder, one 3D Studio project.
A fixed layout lets the user find any reference, checkpoint or score without asking.

## Where a project lives

Put a project at `~/Developer/3d-models/<project>/`, named for its subject in lowercase with hyphens, such as `besiktas-stadium`.
Make it a git repository with a private GitHub remote named `3d-<project>`, and track large binaries, such as `.blend`, `.glb`, video and high-resolution images, with Git LFS.
Open it in 3D Studio with `studio3d project open . --slug <project> --title "<Subject>"`, so it appears as a project of its own.

## Folders

```text
<project>/
├── AGENTS.md            # what this project builds, its rules and how to rebuild it
├── README.md            # the brief, the current score, and how to run the pipeline
├── brief.md             # the brief: subject, scope, quality level, budgets, identity rules, benchmark
├── facts.md             # dimensions, counts and materials, each with its source
├── references/          # captures and photos, and manifest.json with each one's camera
├── scorecard/           # the score views, the measure code, targets and the self-test
├── build/               # Blender and Python scripts that build each part and the assembly
├── parts/               # per-part notes, when a part needs more than its script says
├── checkpoints/
│   └── 003-roof-ring/   # one folder per checkpoint, numbered in order
│       ├── score.json
│       ├── side-by-side/   # model beside reference at every score view and check view
│       ├── diagnosis/      # silhouette overlays, class confusion, edge maps
│       ├── turntable.gif
│       └── notes.md        # what changed, why, the score change, what is next
├── delivery/            # exported GLB files and textures
├── sections/            # 3D Studio sections, components and versions
├── lib/                 # 3D Studio library code that loads the delivered files
├── journal/
│   └── index.html       # the build story, with its images beside it
└── .scratch/            # ignored: renders and intermediate files
```

Number checkpoints with three digits and a short name for the pass, such as `000-blockout`, `001-stands-rake`, so they sort in order and say what they hold.
Write `checkpoints/index.md` with one line per checkpoint: its number, its pass, its overall score and its change.

## Git

Commit after every checkpoint, with the score in the message, so the history is the build log.
Commit references only when their sources allow it, and the remote is private.
Keep renders that a script can regenerate in `.scratch/`, and commit only the images a checkpoint shows.
