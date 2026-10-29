#!/usr/bin/env python3
"""Empty finder: list zero-byte files and empty directories under a path.

Read-only, offline, stdlib only. Never deletes or modifies anything.
JuniorCloud LLC. Additive tool for JuniorPython-Suite.
"""
import argparse
import json
import os
import sys


def scan(root, include_hidden=False):
    """Return (empty_files, empty_dirs) as sorted relative paths."""
    empty_files, empty_dirs = [], []
    root = os.path.abspath(root)
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        if not include_hidden:
            rel_parts = os.path.relpath(dirpath, root).split(os.sep)
            if any(p.startswith(".") and p not in (".",) for p in rel_parts):
                continue
        visible = [f for f in filenames if include_hidden or not f.startswith(".")]
        for name in visible:
            full = os.path.join(dirpath, name)
            try:
                if os.path.isfile(full) and not os.path.islink(full) and os.path.getsize(full) == 0:
                    empty_files.append(os.path.relpath(full, root))
            except OSError:
                continue
        try:
            if dirpath != root and not os.listdir(dirpath):
                empty_dirs.append(os.path.relpath(dirpath, root))
        except OSError:
            continue
    return sorted(empty_files), sorted(empty_dirs)


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="List zero-byte files and empty directories (read-only, offline).")
    ap.add_argument("path", nargs="?", default=".", help="root folder to scan (default: .)")
    ap.add_argument("--hidden", action="store_true", help="include dotfiles and dot folders")
    ap.add_argument("--json", action="store_true", help="print JSON instead of text")
    args = ap.parse_args(argv)
    if not os.path.isdir(args.path):
        print(f"not a directory: {args.path}", file=sys.stderr)
        return 2
    files, dirs = scan(args.path, args.hidden)
    if args.json:
        print(json.dumps({"root": os.path.abspath(args.path), "empty_files": files,
                          "empty_dirs": dirs}, indent=2))
    else:
        for f in files:
            print(f"file  {f}")
        for d in dirs:
            print(f"dir   {d}")
        print(f"total: {len(files)} empty files, {len(dirs)} empty dirs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
