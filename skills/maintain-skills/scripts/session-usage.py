#!/usr/bin/env python3
"""Token usage of a Claude Code session transcript, split into phases.

usage: session-usage.py <transcript.jsonl> [--split HH:MM:SS ...]

Prints the user-message timestamps (to choose split points), then per phase:
model calls, output tokens, cache reads, cache writes, uncached input.
Times are the transcript's UTC timestamps.
"""
import json
import sys


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    path, splits = args[0], []
    if "--split" in args:
        splits = sorted(args[args.index("--split") + 1:])

    calls, seen = [], set()
    print("user messages:")
    for line in open(path):
        row = json.loads(line)
        msg = row.get("message") or {}
        ts = row.get("timestamp", "")
        if row.get("type") == "assistant" and msg.get("usage") and msg.get("id") not in seen:
            seen.add(msg["id"])
            calls.append((ts[11:19], msg["usage"]))
        if row.get("type") == "user":
            content = msg.get("content")
            text = content if isinstance(content, str) else next(
                (c.get("text", "") for c in content or [] if isinstance(c, dict) and c.get("type") == "text"), "")
            if text and not text.startswith("<"):
                print(f"  {ts[11:19]}  {text[:70]!r}")

    bounds = ["00:00:00", *splits, "99:99:99"]
    print("\nphase                calls   output   cache_read  cache_write  input")
    for start, end in zip(bounds, bounds[1:]):
        rows = [u for t, u in calls if start <= t < end]
        if not rows:
            continue
        total = lambda key: sum(u.get(key, 0) for u in rows)
        print(f"{start}-{end[:8]:8}  {len(rows):5}  {total('output_tokens'):7}  {total('cache_read_input_tokens'):11}"
              f"  {total('cache_creation_input_tokens'):11}  {total('input_tokens'):5}")


if __name__ == "__main__":
    main()
