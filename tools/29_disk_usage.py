#!/usr/bin/env python3
"""Disk usage analyzer: report the largest directories and files under a path."""
import argparse
import heapq
import os
import sys


def human(n):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{n:.1f}{unit}" if unit != "B" else f"{n}B"
        n /= 1024


def scan(root, include_hidden):
    dir_sizes, files = {}, []
    root = os.path.abspath(root)
    for dirpath, dirnames, filenames in os.walk(root, topdown=False, onerror=lambda e: None):
        rel = os.path.relpath(dirpath, root)
        if not include_hidden:
            if any(part.startswith(".") for part in rel.split(os.sep) if part != "."):
                continue
            dirnames = [d for d in dirnames if not d.startswith(".")]
            filenames = [f for f in filenames if not f.startswith(".")]
        total = 0
        for name in filenames:
            p = os.path.join(dirpath, name)
            try:
                if os.path.islink(p):
                    continue
                size = os.path.getsize(p)
            except OSError:
                continue
            total += size
            files.append((size, p))
        for d in dirnames:
            total += dir_sizes.get(os.path.join(dirpath, d), 0)
        dir_sizes[dirpath] = total
    return root, dir_sizes, files


def main():
    ap = argparse.ArgumentParser(description="Show the largest directories and files under a path.")
    ap.add_argument("path", nargs="?", default=".", help="root directory (default: .)")
    ap.add_argument("-n", "--top", type=int, default=10, help="entries to show per section")
    ap.add_argument("-d", "--max-depth", type=int, default=None, help="only list directories up to this depth")
    ap.add_argument("-a", "--all", action="store_true", help="include hidden files/directories")
    args = ap.parse_args()
    if not os.path.isdir(args.path):
        print(f"error: not a directory: {args.path}", file=sys.stderr)
        return 1
    root, dir_sizes, files = scan(args.path, args.all)
    print(f"Total: {human(dir_sizes.get(root, 0))}  ({len(files)} files)  {root}\n")
    dirs = [(s, p) for p, s in dir_sizes.items() if p != root and (
        args.max_depth is None or os.path.relpath(p, root).count(os.sep) < args.max_depth)]
    print(f"Top {args.top} directories:")
    for s, p in heapq.nlargest(args.top, dirs):
        print(f"  {human(s):>10}  {os.path.relpath(p, root)}")
    print(f"\nTop {args.top} files:")
    for s, p in heapq.nlargest(args.top, files):
        print(f"  {human(s):>10}  {os.path.relpath(p, root)}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
