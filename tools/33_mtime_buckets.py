#!/usr/bin/env python3
"""mtime_buckets: read-only file age report.

Walks a directory tree and groups files by modification age into buckets
(<1d, <7d, <30d, <365d, older). Optionally lists the N newest/oldest files.
Stdlib only, offline, never writes or deletes anything. No network.

JuniorCloud LLC - JuniorPython-Suite.
"""
import argparse
import json
import os
import sys
import time

BUCKETS = [("<1d", 86400), ("<7d", 7 * 86400), ("<30d", 30 * 86400),
           ("<365d", 365 * 86400), ("older", float("inf"))]
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv"}


def bucket_for(age):
    for name, limit in BUCKETS:
        if age < limit:
            return name
    return "older"


def scan(root, include_hidden=False, now=None):
    now = time.time() if now is None else now
    counts = {name: 0 for name, _ in BUCKETS}
    sizes = {name: 0 for name, _ in BUCKETS}
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS
                             and (include_hidden or not d.startswith(".")))
        for fn in filenames:
            if not include_hidden and fn.startswith("."):
                continue
            path = os.path.join(dirpath, fn)
            try:
                st = os.lstat(path)
            except OSError:
                continue
            age = max(0.0, now - st.st_mtime)
            b = bucket_for(age)
            counts[b] += 1
            sizes[b] += st.st_size
            files.append((st.st_mtime, os.path.relpath(path, root)))
    files.sort()
    return counts, sizes, files


def human(n):
    for unit in ("B", "K", "M", "G", "T"):
        if n < 1024:
            return "%d%s" % (n, unit) if unit == "B" else "%.1f%s" % (n, unit)
        n /= 1024.0
    return "%.1fP" % n


def main(argv=None):
    p = argparse.ArgumentParser(description="Read-only file age buckets for a directory tree (stdlib, offline).")
    p.add_argument("root", nargs="?", default=".", help="directory to scan (default: .)")
    p.add_argument("-n", "--top", type=int, default=5, help="show N newest and oldest files (default 5, 0 to hide)")
    p.add_argument("--hidden", action="store_true", help="include dotfiles and dot-directories")
    p.add_argument("--json", action="store_true", help="emit JSON instead of text")
    a = p.parse_args(argv)
    if not os.path.isdir(a.root):
        p.error("not a directory: %s" % a.root)
    counts, sizes, files = scan(a.root, a.hidden)
    top = max(0, a.top)
    fmt = lambda t: time.strftime("%Y-%m-%d %H:%M", time.localtime(t))
    newest = [(fmt(t), f) for t, f in reversed(files[-top:])] if top else []
    oldest = [(fmt(t), f) for t, f in files[:top]] if top else []
    if a.json:
        print(json.dumps({"root": os.path.abspath(a.root), "total": len(files),
                          "buckets": {k: {"files": counts[k], "bytes": sizes[k]} for k in counts},
                          "newest": newest, "oldest": oldest}, indent=2))
        return 0
    print("root: %s  files: %d" % (os.path.abspath(a.root), len(files)))
    for name, _ in BUCKETS:
        print("  %-6s %7d files  %9s" % (name, counts[name], human(sizes[name])))
    if top:
        print("newest:")
        for t, f in newest:
            print("  %s  %s" % (t, f))
        print("oldest:")
        for t, f in oldest:
            print("  %s  %s" % (t, f))
    return 0


if __name__ == "__main__":
    sys.exit(main())
