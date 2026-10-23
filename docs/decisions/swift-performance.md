# Decisions: swift-performance

This page records the decisions behind the [`swift-performance`](../../skills/swift-performance/SKILL.md) skill.
It is for maintaining the skill and is never installed.
Entries follow the shape in [index.md](index.md).

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

## 2026-10-13: the first audit

- **Status:** accepted
- **Context:** A fresh sub-agent ran the prompt audit on the new skill. It also checked the rules against current Swift, and ran both scripts.
- **Options:** None considered.
- **Choice and why:** All 15 findings were applied:
  - Three facts were wrong. A repeating effect keeps the window rendering, but it doesn't run every body again. An observer on each item fires on each scroll step, not on each layout pass. Copying values in a sort was a micro-optimisation, so the rule went.
  - Two facts were missing. The frame budget is 16 ms at 60 Hz too. Swift 6.2 code with approachable concurrency needs `@concurrent` to leave the main actor.
  - The meter's 8 ms ping wakes the main thread. The skill now says to measure idle with `sample`.
  - The description now leads with its triggers, not with the two modes.
  - Repeated rules, a no-op sentence and a restated "done when" line were removed. A number from one session became a general reason.
  - The rule from the first draft stays: the frame cost grows with the size of the view tree. The diagnosis measured it. The same pulse cost 97% of the main thread in an eager list and 8% in a lazy one.
- **Consequences:** `SKILL.md` went from 75 to 72 lines. Most changes made a line shorter. `/diagnosing-bugs` and `/write-swift` also trigger on slowness. Check which skill loads in the first sessions.

## 2026-10-13: pruned for readability

- **Status:** accepted
- **Context:** The maintainer found the audited skill too crowded.
- **Options:** None considered.
- **Choice and why:** Keep every rule, and remove the words around it:
  - The mode table became one sentence in the opening paragraph.
  - Examples that a rule already implies were removed.
  - Four "done when" lines that restated their steps were removed.
  - The rule "find causes by isolation" moved into diagnosis step 4.
  - "Measure one process" merged into "confirm the state while you measure".
  - Reporting became one line under diagnosis mode.
- **Consequences:** The body went from about 1,250 words to about 650.

## 2026-10-13: the meter runs on macOS 13 and later

- **Status:** accepted
- **Context:** The first app to use the meter targets macOS 14. `Mutex` needs macOS 15, so the meter didn't compile there.
- **Options:** Keep `Mutex`: many apps still support macOS 14.
- **Choice and why:** Use `OSAllocatedUnfairLock`, which has the same `withLock` shape and works from macOS 13.
- **Consequences:** The meter compiles in a macOS 14 app, as the shipyard diagnosis showed.
