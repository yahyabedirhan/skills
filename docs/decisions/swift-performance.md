# Decisions: swift-performance

The decisions behind the `swift-performance` skill. This file is for maintaining the skill and is never installed. Read it before changing the skill. Entries follow the shape in [index.md](index.md).

## Maintaining

The skill is a distilled record of one diagnosis. The app was a SwiftUI menu bar app. Its tabs layout became slow as its projects grew. A lesson goes into the skill only when it holds for nearly every macOS Swift app. Keep the features, numbers and tools of one app out of the skill. When a new diagnosis teaches a general lesson, add it as a short rule in its section. Then record the session it came from in a new entry here.

## 2026-10-13: one skill with a build mode and a diagnosis mode

- **Status:** accepted
- **Context:** The maintainer wanted agents to avoid obvious performance mistakes by default. The maintainer also wanted a method to follow when an app is slow.
- **Options:**
  - A design framework only: agents would have no method when someone reports slowness.
  - Two skills: the two modes share one set of rules, so two skills would repeat them.
- **Choice and why:** One skill with two modes. Steps 4 to 6 of build mode hold the rules. A diagnosis ends with the rule that the code breaks. Its fix then goes through build mode.
- **Consequences:** The description has two triggers. One is writing or reviewing Swift UI code. The other is a report of slowness.

## 2026-10-13: the steps are general and the rules are for Swift

- **Status:** accepted
- **Context:** A first draft named its steps after rendering. Those names fit a UI app, but not a service or a data pipeline.
- **Options:** A skill for every platform, with one reference per platform. The maintainer asked for Swift on macOS only.
- **Choice and why:** The seven steps name general causes: work bounding, reuse and invalidation, and concurrency and I/O. The rules in each step are for SwiftUI and AppKit.
- **Consequences:** A later skill for web or backend work can reuse the steps with its own rules.

## 2026-10-13: two scripts, and agents write the other tools

- **Status:** accepted
- **Context:** The diagnosis made six tools: fixture data, counters, a main-thread meter, a `sample` reader, a stress script and a model benchmark.
- **Options:**
  - Keep all six: the fixtures, scenarios, counters and benchmarks are specific to one app. A fixed script also makes agents measure what it measures, not what the app needs.
  - Keep none: nearly every case needs the meter and the reader. Both are easy to get wrong. The meter's timer crashes under Swift 6 isolation when it is made in the wrong place. `sample` labels the main thread in two ways.
- **Choice and why:** Keep `MainThreadMeter.swift` and `sample-busy.py`, because most cases need them. The skill tells agents to write each other tool for the app.
- **Consequences:** The skill has no `references/` folder. Every rule fits in `SKILL.md`.

## 2026-10-13: lessons kept only in their general form

- **Status:** accepted
- **Context:** The diagnosis also found causes specific to one app. Examples are a banner that kept the panel redrawing while an agent controlled the app, and the sizing of a menu bar window.
- **Options:** Keep them as examples: they would teach one app's features as rules.
- **Choice and why:** Keep each lesson only in its general form:
  - The banner from agent control became "check that your tools don't cause the cost".
  - Several windows in one prototype process became "measure one process doing one thing".
  - An Instruments template that recorded nothing became "keep `sample` as a fallback".
- **Consequences:** The skill names no app, no measured number and no project tool.

## 2026-10-13: no pointers from other skills yet

- **Status:** accepted
- **Context:** `/low-level-design`, `/implement` and `/code-review` could point at build mode.
- **Options:** Add the pointers now: each adds a line to a skill that every kind of project uses, before anyone has used this skill.
- **Choice and why:** Let the description trigger the skill on Swift UI work for now.
- **Consequences:** Decide again after agents use the skill. Add the pointers if agents that write SwiftUI don't load it.
