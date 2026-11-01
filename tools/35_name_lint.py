#!/usr/bin/env python3
"""Read-only filename linter.

Walks a folder and flags names that tend to break scripts or cross-platform
syncs: spaces, non-ASCII characters, characters reserved on Windows, very long
names, trailing dots or spaces, and names that collide when case is ignored.
Nothing is renamed or written. Stdlib only, offline, no network.
"""
import argparse
import json
import os
import sys

RESERVED_CHARS = set('<>:"\\|?*')
RESERVED_NAMES = {"CON", "PRN", "AUX", "NUL"} | {f"COM{i}" for i in range(1, 10)} | {f"LPT{i}" for i in range(1, 10)}
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv"}


def issues_for(name, max_len):
    found = []
    if " " in name:
        found.append("space")
    if any(ord(c) > 127 for c in name):
        found.append("non-ascii")
    if any(c in RESERVED_CHARS or ord(c) < 32 for c in name):
        found.append("reserved-char")
    if name.split(".")[0].upper() in RESERVED_NAMES:
        found.append("reserved-name")
    if len(name) > max_len:
        found.append("too-long")
    if name.endswith((".", " ")):
        found.append("trailing-dot-or-space")
    return found


def scan(root, max_len, include_hidden):
    results = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and (include_hidden or not d.startswith(".")))
        names = [n for n in dirnames + sorted(filenames) if include_hidden or not n.startswith(".")]
        seen = {}
        for n in names:
            seen.setdefault(n.lower(), []).append(n)
        for n in names:
            found = issues_for(n, max_len)
            if len(seen[n.lower()]) > 1:
                found.append("case-collision")
            if found:
                results.append({"path": os.path.relpath(os.path.join(dirpath, n), root), "issues": found})
    return results


def main(argv=None):
    p = argparse.ArgumentParser(description="Read-only filename linter (stdlib, offline).")
    p.add_argument("root", nargs="?", default=".", help="folder to scan (default: .)")
    p.add_argument("--max-len", type=int, default=120, help="flag names longer than this (default: 120)")
    p.add_argument("--hidden", action="store_true", help="include dotfiles and dot-folders")
    p.add_argument("--json", action="store_true", help="print JSON instead of text")
    a = p.parse_args(argv)
    if not os.path.isdir(a.root):
        print(f"not a folder: {a.root}", file=sys.stderr)
        return 2
    res = scan(a.root, a.max_len, a.hidden)
    if a.json:
        print(json.dumps({"root": os.path.abspath(a.root), "flagged": len(res), "items": res}, indent=2))
    else:
        for r in res:
            print(f"{r['path']}: {', '.join(r['issues'])}")
        print(f"{len(res)} flagged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
