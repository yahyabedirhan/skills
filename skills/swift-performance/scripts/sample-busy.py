#!/usr/bin/env python3
"""Main-thread busy share from macOS `sample` output.

Usage:
  sample <pid> <seconds> -mayDie -file <path>       # record, once per state
  sample-busy.py <path> [<path> ...]                # busy share of each file
  sample-busy.py <path> --frames <binary> [--top N] # and the heaviest frames
                                                    # of <binary> on the main thread

Busy is every main-thread sample not waiting in the run loop for its next
event (`__CFRunLoopServiceMachPort`), so it fits apps with a run loop.
`--frames` counts each frame once per stack it appears in, at its largest
count, so callers and callees both show and the top is the hottest path.
"""
import argparse
import re
import sys

# `sample` labels the main thread in more than one way.
MAIN = re.compile(r"^\s+(\d+) Thread_\d+(\s+DispatchQueue_1: com\.apple\.main-thread|: Main Thread)")
THREAD = re.compile(r"^\s+\d+ Thread_\d+")
WAIT = re.compile(r"(\d+) __CFRunLoopServiceMachPort")
FRAME = re.compile(r"^[\s+!:|]*(\d+) (.+?)\s+\(in ([^)]+)\)")


def main_thread(lines):
    for start, line in enumerate(lines):
        match = MAIN.match(line)
        if match:
            end = start + 1
            while end < len(lines) and lines[end].strip() and not THREAD.match(lines[end]):
                end += 1
            return int(match.group(1)), lines[start:end]
    return None, []


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="+")
    parser.add_argument("--frames", metavar="BINARY", help="list the heaviest frames of this binary, such as the app's executable name")
    parser.add_argument("--top", type=int, default=20)
    args = parser.parse_args()

    for path in args.files:
        with open(path) as handle:
            lines = handle.read().split("\n")
        total, block = main_thread(lines)
        if total is None:
            print(f"{path}: no main thread found (did the process exit while sampling?)")
            continue
        waiting = sum(int(m.group(1)) for line in block for m in [WAIT.search(line)] if m)
        busy = total - waiting
        print(f"{path}: main thread busy {busy * 100 / total:.0f}% ({busy} of {total} samples)")
        if args.frames:
            heaviest = {}
            for line in block:
                match = FRAME.match(line)
                if match and match.group(3) == args.frames:
                    symbol = re.sub(r" \+ \d+.*$", "", match.group(2))
                    heaviest[symbol] = max(heaviest.get(symbol, 0), int(match.group(1)))
            for symbol, count in sorted(heaviest.items(), key=lambda item: -item[1])[: args.top]:
                print(f"  {count:6}  {symbol}")


if __name__ == "__main__":
    sys.exit(main())
