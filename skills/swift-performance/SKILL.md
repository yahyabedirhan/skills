---
name: swift-performance
description: Keep a Swift app fast on macOS, in two modes. Build mode designs, implements or reviews a SwiftUI or AppKit view, list, model or data flow so it scales. Diagnosis mode finds the cause when an app is slow, laggy, janky, hot, or busy while idle.
---

# Swift performance

A cost is the amount of work, times how often it runs, times how long it waits. Most slowness in a Swift app is ordinary work on a hot path, the code that runs per frame or per input event. Examples are a whole list rebuilt on each hover, a model sorted on each render, or an animation that never stops. Build mode keeps such work out while the code is written. Diagnosis mode finds which one got in.

Write your own tools for each app: the fixture data, the scenario that drives the app, and the counters in its hot paths. They differ for every app, and a tool written for another app measures what that app needed. The two scripts in `scripts/` measure the main thread, which nearly every case needs.

## Choosing the mode

| The session | Mode |
|---|---|
| Designing, implementing or reviewing code | Build mode |
| A report of slowness, or a number that looks wrong | Diagnosis mode |
| The fix that a diagnosis found | Build mode, on the fix |

## Build mode

Run all seven steps for a new feature or screen. For a review or a small change, run steps 4 to 6 on the diff.

1. **Workload model.** Name how many items each view shows today, at ×10 and at ×100. Find the largest view: usually one that merges others, such as an "All" tab or a search across everything.
   - Done when every view that lists data has its three numbers.
2. **Hot path analysis.** Tag each piece of work by how often it runs: per frame, per input event, per action, per data change, or once. Input events are hovers, scroll steps and keystrokes. Actions are clicks and navigation.
   - Done when every computation in a view's body, a handler or an observer has its tag.
3. **Performance budgets.** Hold each tag to a budget. A frame at 120 Hz has 8 ms of main-thread time, shared by everything in the window. An action finishes within 100 ms. An open window that nobody touches uses about 0% CPU.
   - Done when the cost of each hot path at ×10 fits its budget, or is flagged.
4. **Work bounding.** Do only the work that the user can see.
   - Draw a collection that can grow lazily, with `LazyVStack`, `List` or `Table`. A `VStack` builds and lays out every item, the ones off screen too.
   - Run an animation, symbol effect, `TimelineView`, timer or poll only while its view is visible and something changes. A repeating effect redraws the whole window every frame, and the cost grows with the size of the view tree.
   - Keep the identity of a large subtree stable. A new `.id` throws the subtree away and builds it again.
5. **Reuse and invalidation.** Compute each result once, and redraw only what changed.
   - Compute derived data, such as filtered, sorted, grouped or merged collections, when its source data changes. Store it, and read the stored result in `body`.
   - Keep fast-changing state in the smallest view that needs it. Hover, selection, scroll position and countdowns are fast-changing. State at the root of a list, bound into every row, redraws every row on each change.
   - Build per-item extras when they are shown. Tooltip text, previews and detail strings are extras.
   - Read an item's geometry, preferences or scroll position on demand, or in a coordinate space that doesn't move. An observer on every item fires for every item on every layout pass.
   - Sort and compare keys or indices, not large value types, because each move copies the whole value.
6. **Concurrency and I/O.** Keep the main thread for drawing and input. Run network calls, disk access, parsing and child processes off it, and return their results to it in one update.
7. **Measurement.** Build fixture data at each volume from step 1. Measure each flagged hot path against its budget with `scripts/MainThreadMeter.swift`, or with `sample` and `scripts/sample-busy.py`.
   - Done when each flagged path has one number before the change and one after.

## Diagnosis mode

1. **Symptom.** Write down what is slow, where it is slow, how slow it is, and at what volume.
2. **Reproduction.** Make the slowness repeat on demand at the user's volume. Use a copy of the app or a prototype, with its own data, because a diagnosis changes things and the user's app and data must stay as they are.
   - Done when the slowness shows each time you run the case.
3. **Measurement.** Measure the main thread on the path that the user takes. Use `sample` and `scripts/sample-busy.py` on an app you can't rebuild, and `scripts/MainThreadMeter.swift` in one you can. Measure three states: idle, the slow interaction, and a comparison case that is fast.
   - Done when the slow case and the comparison case differ in a number.
4. **Isolation.** Switch parts off one at a time until the cost goes away. Parts are views, modifiers, observers and timers. A comparison case that stays fast at the same volume, such as a sibling screen, points at what differs.
5. **Root cause.** Name the mechanism, how often it runs, its file and line, and the build mode rule it breaks in step 4, 5 or 6.
   - Done when removing the cause removes the cost.
6. **Verification.** Apply the fix in a copy beside the unchanged baseline, and measure both in the same way.

## Measuring you can trust

- **Measure main-thread CPU share and stall length.** Total CPU and frames per second hide where the time goes. A stall is how late the main thread runs work that is waiting for it.
- **Measure idle too.** An open window that nobody touches should cost nothing, so a busy idle window is a finding of its own.
- **Count how often bodies and handlers run.** Frequency explains most costs: the same few milliseconds are harmless once per data change and too slow on every hover.
- **Check the state at the moment you measure.** Confirm that the window is open, the data is loaded, and nothing else is drawing.
- **Measure one process doing one thing.** Other windows, other copies and background work on the same main thread add to the reading.
- **Check that your tools don't cause the cost.** Automation, control commands, overlays and screenshot paths can change what the app draws. Confirm each finding on the path that a user takes.
- **Compare release builds with release builds.** Debug builds behave differently. A profiler can record nothing for a build it can't read, so keep `sample` as a fallback.
- **Repeat each case at least twice, and change one thing per run.** Single readings of the same idle case can differ by half.
- **Find causes by isolation when the profile has no app code in it.** Profilers show where time goes, not why. A stack with only framework code means that something keeps scheduling redraws.

## Reporting

Report a table of costs: each scenario at each volume, with its main-thread share, worst stall and slowest action. Then list each root cause with its file and line, how often it runs, and the build mode rule it breaks.

## Scripts

- `scripts/MainThreadMeter.swift`: a class to add to an app or a prototype that you can build. It reads the main thread's CPU share from the kernel, and times how late the main thread runs a block posted every 8 ms. It works on macOS and iOS.
- `scripts/sample-busy.py`: reads files written by `sample <pid> <seconds> -file <path>`, and prints the main thread's busy share. With `--frames <binary>` it also lists that binary's heaviest frames on the main thread. It measures a running app without a rebuild.
