#!/usr/bin/env python3
"""e19_notification_qa.py — Record a manual cloud-to-phone notification test.

This utility records observations; it does NOT send notifications, access cloud
sessions, or independently verify delivery. Trigger the notification through the
actual cloud product and observe the physical phone.

Example:
    python e19_notification_qa.py \
        --session-id SESSION_ID \
        --device "iPhone / iOS VERSION" \
        --app-version VERSION \
        --observer tester \
        --triggered-at 2026-09-30T10:00:00Z \
        --observed-until 2026-09-30T10:05:00Z \
        --received-at 2026-09-30T10:00:12Z \
        --trigger-evidence "qa/session-completion.png" \
        --notification-evidence "qa/phone-notification.png" \
        --output e19-result.json

Evidence references should identify the tested session without containing tokens,
private notification contents, or other sensitive information. A missing
notification means only that delivery was not observed during the recorded window.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence


def parse_timestamp(value: str) -> datetime:
    """Parse an ISO 8601 timestamp with an explicit timezone and normalize to UTC."""
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "Use an ISO 8601 timestamp, such as 2026-09-30T10:00:00Z."
        ) from exc
    if parsed.utcoffset() is None:
        raise argparse.ArgumentTypeError("Timestamp must include a timezone.")
    return parsed.astimezone(timezone.utc)


def nonempty(value: str) -> str:
    """Reject empty identifiers and evidence references."""
    value = value.strip()
    if not value:
        raise argparse.ArgumentTypeError("Value must not be empty.")
    return value


def positive_integer(value: str) -> int:
    """Validate the explicitly chosen observation window."""
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Expected a positive integer.") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError("Expected a positive integer.")
    return parsed


def classify_observation(
    triggered_at: datetime,
    observed_until: datetime,
    received_at: datetime | None,
    window_seconds: int,
) -> dict[str, Any]:
    """Classify manually supplied observations, not provider delivery guarantees."""
    timestamps = [triggered_at, observed_until]
    if received_at is not None:
        timestamps.append(received_at)
    if any(timestamp.utcoffset() is None for timestamp in timestamps):
        raise ValueError("All timestamps must be timezone-aware.")
    if window_seconds <= 0:
        raise ValueError("Observation window must be positive.")
    if observed_until < triggered_at:
        raise ValueError("Observation cannot end before the trigger.")
    if received_at is not None and not triggered_at <= received_at <= observed_until:
        raise ValueError("Receipt must fall between trigger and observation end.")

    elapsed = (observed_until - triggered_at).total_seconds()
    latency = (
        (received_at - triggered_at).total_seconds()
        if received_at is not None
        else None
    )

    if latency is not None:
        outcome = (
            "received_within_window"
            if latency <= window_seconds
            else "received_after_window"
        )
    elif elapsed >= window_seconds:
        outcome = "not_observed_within_window"
    else:
        outcome = "inconclusive_short_observation"

    return {
        "outcome": outcome,
        "observation_seconds": elapsed,
        "reported_latency_seconds": latency,
        "independently_verified": False,
    }


def write_report(path: Path, report: dict[str, Any]) -> None:
    """Write a new report without overwriting existing evidence.

    On POSIX systems, the new file is owner-readable and owner-writable only.
    Parent directories must already exist. Partial files are removed on failure.
    """
    payload = json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        stream = os.fdopen(fd, "w", encoding="utf-8")
    except BaseException:
        os.close(fd)
        path.unlink(missing_ok=True)
        raise

    try:
        with stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def main(argv: Sequence[str] | None = None) -> int:
    """Validate observations and persist a structured E19 evidence record."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session-id", required=True, type=nonempty)
    parser.add_argument("--device", required=True, type=nonempty)
    parser.add_argument("--app-version", required=True, type=nonempty)
    parser.add_argument("--observer", required=True, type=nonempty)
    parser.add_argument("--trigger-evidence", required=True, type=nonempty)
    parser.add_argument("--notification-evidence", type=nonempty)
    parser.add_argument("--triggered-at", required=True, type=parse_timestamp)
    parser.add_argument("--observed-until", required=True, type=parse_timestamp)
    parser.add_argument("--received-at", type=parse_timestamp)
    parser.add_argument("--window-seconds", required=True, type=positive_integer,
                        help="QA observation threshold, not a product delivery SLA.")
    parser.add_argument("--notes", default="",
                        help="Record permissions, app state, network, and Focus/DND.")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)

    if (args.received_at is None) != (args.notification_evidence is None):
        parser.error("--received-at and --notification-evidence must be used together.")

    try:
        result = classify_observation(
            args.triggered_at,
            args.observed_until,
            args.received_at,
            args.window_seconds,
        )
    except ValueError as exc:
        parser.error(str(exc))

    report = {
        "schema_version": 1,
        "experiment": "E19",
        "source": "manual_phone_observation",
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "session_id": args.session_id,
        "device": args.device,
        "app_version": args.app_version,
        "observer": args.observer,
        "triggered_at": args.triggered_at.isoformat(),
        "observed_until": args.observed_until.isoformat(),
        "received_at": args.received_at.isoformat() if args.received_at else None,
        "window_seconds": args.window_seconds,
        "trigger_evidence": args.trigger_evidence,
        "notification_evidence": args.notification_evidence,
        "notes": args.notes,
        **result,
    }
    try:
        write_report(args.output, report)
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Could not write report: {exc}\n")

    print(f"{result['outcome']}: {args.output}")
    return 0  # Success means evidence was recorded, not that delivery succeeded.


if __name__ == "__main__":
    raise SystemExit(main())