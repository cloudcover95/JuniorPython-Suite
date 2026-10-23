#!/usr/bin/env python3
"""Line census: count files, lines, blank lines and comment lines by extension.

Read-only, offline, stdlib only. No network, no sockets, no writes
unless --json-out is given. JuniorCloud LLC. Additive tool.

Examples:
  python3 line_census.py .
  python3 line_census.py ~/code --ext .py .md --top 10
  python3 line_census.py . --json-out census.json
"""
import argparse
import json
import os
import sys

COMMENT_PREFIX = {
    ".py": "#", ".sh": "#", ".rb": "#", ".yml": "#", ".yaml": "#", ".toml": "#",
    ".js": "//", ".ts": "//", ".c": "//", ".h": "//", ".cpp": "//", ".rs": "//",
    ".go": "//", ".java": "//", ".swift": "//", ".sol": "//",
}
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".mypy_cache"}


def is_binary(path, probe=1024):
    try:
        with open(path, "rb") as fh:
            return b"\0" in fh.read(probe)
    except OSError:
        return True


def census(root, exts=None, max_bytes=5_000_000):
    stats = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for name in sorted(filenames):
            path = os.path.join(dirpath, name)
            ext = os.path.splitext(name)[1].lower() or "(none)"
            if exts and ext not in exts:
                continue
            try:
                if os.path.islink(path) or os.path.getsize(path) > max_bytes:
                    continue
            except OSError:
                continue
            if is_binary(path):
                continue
            row = stats.setdefault(ext, {"files": 0, "lines": 0, "blank": 0, "comment": 0})
            row["files"] += 1
            prefix = COMMENT_PREFIX.get(ext)
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as fh:
                    for line in fh:
                        row["lines"] += 1
                        s = line.strip()
                        if not s:
                            row["blank"] += 1
                        elif prefix and s.startswith(prefix):
                            row["comment"] += 1
            except OSError:
                continue
    return stats


def render(stats, top=None):
    rows = sorted(stats.items(), key=lambda kv: kv[1]["lines"], reverse=True)
    if top:
        rows = rows[:top]
    out = ["%-10s %7s %9s %8s %8s %8s" % ("ext", "files", "lines", "blank", "comment", "code")]
    tot = {"files": 0, "lines": 0, "blank": 0, "comment": 0}
    for ext, r in rows:
        code = r["lines"] - r["blank"] - r["comment"]
        out.append("%-10s %7d %9d %8d %8d %8d" % (ext, r["files"], r["lines"], r["blank"], r["comment"], code))
        for k in tot:
            tot[k] += r[k]
    code = tot["lines"] - tot["blank"] - tot["comment"]
    out.append("%-10s %7d %9d %8d %8d %8d" % ("TOTAL", tot["files"], tot["lines"], tot["blank"], tot["comment"], code))
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Count lines by file extension (read-only, stdlib).")
    ap.add_argument("root", nargs="?", default=".", help="directory to scan (default .)")
    ap.add_argument("--ext", nargs="*", help="only these extensions, e.g. .py .md")
    ap.add_argument("--top", type=int, help="show only the N largest extensions")
    ap.add_argument("--json-out", help="also write the raw counts to this JSON file")
    args = ap.parse_args(argv)
    if not os.path.isdir(args.root):
        print("not a directory: %s" % args.root, file=sys.stderr)
        return 2
    exts = {e.lower() if e.startswith(".") else "." + e.lower() for e in args.ext} if args.ext else None
    stats = census(args.root, exts)
    print(render(stats, args.top))
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump(stats, fh, indent=2, sort_keys=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
