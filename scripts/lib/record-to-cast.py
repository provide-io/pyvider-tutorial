#!/usr/bin/env python3
"""
Record a command's terminal output as an asciinema v2 .cast file.

Uses Python's pty module to allocate a real PTY so terminal escape sequences,
colors, and cursor movement are captured correctly — no asciinema binary required.

Usage:
    python3 ci/record-to-cast.py OUTPUT.cast COMMAND [ARGS...]

Example:
    python3 ci/record-to-cast.py conformance.cast soup stir --recursive
"""
import fcntl
import json
import os
import pty
import re
import struct
import subprocess
import sys
import termios
import time

# Strip only the sequences that cause the player to flash — specifically the
# alternate screen buffer switch and full-screen clears. Leave everything else
# (colors, erase-line, cursor movement) intact so the output renders correctly.
_STRIP_RE = re.compile(
    r"\x1b\["
    r"(?:"
    r"\?(?:1049|1047|47)[hl]"   # alternate screen buffer enter/exit (the flash cause)
    r"|\?25[lh]"                 # cursor hide/show
    r"|[23]J"                    # erase entire screen / clear scrollback
    r")"
)

# Scrub absolute paths and structlog debug lines from output.
_HOME_RE = re.compile(r"/Users/\w+/[^\s'\")\]]+")
_LOG_LINE_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z\s+[^\r\n]*\r?\n")


def _scrub(text: str) -> str:
    text = _STRIP_RE.sub("", text)
    text = _LOG_LINE_RE.sub("", text)
    text = _HOME_RE.sub(lambda m: "…/" + m.group(0).rsplit("/", 1)[-1], text)
    return text


def main() -> None:
    if len(sys.argv) < 3:
        print(
            f"Usage: {sys.argv[0]} [--split-lines] [--pause-end=N] [--title=TEXT] "
            "OUTPUT.cast COMMAND [ARGS...]",
            file=sys.stderr,
        )
        sys.exit(1)

    args = sys.argv[1:]
    split_lines = False
    pause_end = 0.0
    # Every cast this produced was stamped "pyvider conformance suite",
    # including the five tutorial parts, none of which is the conformance
    # suite. The player shows it, so it is worth passing in.
    title = "pyvider"

    while args and args[0].startswith("--"):
        if args[0] == "--split-lines":
            split_lines = True
            args = args[1:]
        elif args[0].startswith("--pause-end"):
            if "=" in args[0]:
                pause_end = float(args[0].split("=", 1)[1])
            else:
                pause_end = float(args[1])
                args = args[1:]
            args = args[1:]
        elif args[0].startswith("--title"):
            if "=" in args[0]:
                title = args[0].split("=", 1)[1]
            else:
                title = args[1]
                args = args[1:]
            args = args[1:]
        else:
            break

    output_path = args[0]
    command = args[1:]

    events: list = []
    start_time = time.time()

    cols, rows = 120, 40
    master_fd, slave_fd = pty.openpty()

    # Set the PTY size so the child process renders at the target dimensions.
    winsize = struct.pack("HHHH", rows, cols, 0, 0)
    fcntl.ioctl(slave_fd, termios.TIOCSWINSZ, winsize)

    proc = subprocess.Popen(
        command,
        stdout=slave_fd,
        stderr=slave_fd,
        stdin=subprocess.DEVNULL,
        close_fds=True,
    )
    os.close(slave_fd)

    last_ts = 0.0

    while True:
        try:
            chunk = os.read(master_fd, 4096)
        except OSError:
            break
        if not chunk:
            break
        elapsed = round(time.time() - start_time, 6)
        text = _scrub(chunk.decode("utf-8", errors="replace"))
        if text:
            if split_lines:
                # Split on newlines so each line is a separate event — gives
                # the player a streaming feel for linear command output.
                # Don't use for TUI apps (Rich live tables) where cursor
                # movement sequences must stay in their original chunks.
                base_ts = max(elapsed, last_ts + 0.05)
                lines = text.split("\n")
                for i, line in enumerate(lines):
                    fragment = line + ("\n" if i < len(lines) - 1 else "")
                    if fragment:
                        line_ts = round(base_ts + i * 0.05, 6)
                        events.append([line_ts, "o", fragment])
                        last_ts = line_ts
            else:
                events.append([elapsed, "o", text])
                last_ts = elapsed
        sys.stdout.buffer.write(chunk)
        sys.stdout.flush()

    proc.wait()
    exit_code = proc.returncode
    os.close(master_fd)

    # Append a hold frame so the final output stays visible before looping.
    if pause_end > 0 and events:
        final_ts = events[-1][0]
        events.append([round(final_ts + pause_end, 6), "o", ""])

    header = {
        "version": 2,
        "width": cols,
        "height": rows,
        "timestamp": int(start_time),
        "title": title,
        "env": {"TERM": "xterm-256color", "SHELL": "/bin/bash"},
    }

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(header) + "\n")
        for event in events:
            f.write(json.dumps(event) + "\n")

    print(
        f"\n✅ Cast written to {output_path} ({len(events)} events, {time.time() - start_time:.1f}s)",
        file=sys.stderr,
    )

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
