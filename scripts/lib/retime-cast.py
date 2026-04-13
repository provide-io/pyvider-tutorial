#!/usr/bin/env python3
"""
Retime an asciinema v2 .cast file to a target duration.

Terminal recordings can be too short (burst output) or too long (slow tests)
for a good website demo. This script proportionally scales all timestamps to
fit a target duration while preserving relative timing.

Usage:
    python3 ci/retime-cast.py INPUT.cast OUTPUT.cast [TARGET_SECONDS]

TARGET_SECONDS defaults to 15.
"""
import json
import sys


def retime(input_path: str, output_path: str, target_duration: float) -> None:
    with open(input_path, encoding="utf-8") as f:
        header = json.loads(f.readline())
        events = [json.loads(line) for line in f]

    if not events:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(header) + "\n")
        return

    original_duration = events[-1][0] - events[0][0]
    if original_duration <= 0:
        scale = 1.0
    else:
        scale = target_duration / original_duration

    first_ts = events[0][0]
    # Small lead-in so it doesn't start at t=0
    offset = 0.5

    new_events: list = []
    for event in events:
        new_ts = round(offset + (event[0] - first_ts) * scale, 3)
        new_events.append([new_ts, event[1], event[2]])

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(header) + "\n")
        for event in new_events:
            f.write(json.dumps(event) + "\n")

    final_duration = new_events[-1][0]
    print(
        f"Retimed {len(events)} events: "
        f"{original_duration:.1f}s → {final_duration:.1f}s "
        f"(scale {scale:.2f}x)",
        file=sys.stderr,
    )


def main() -> None:
    if len(sys.argv) < 3:
        print(
            f"Usage: {sys.argv[0]} INPUT.cast OUTPUT.cast [TARGET_SECONDS]",
            file=sys.stderr,
        )
        sys.exit(1)
    target = float(sys.argv[3]) if len(sys.argv) > 3 else 15.0
    retime(sys.argv[1], sys.argv[2], target)


if __name__ == "__main__":
    main()
