#!/usr/bin/env python3
"""Duplicate file finder (stdlib only, CLI).

Groups files by size, then by SHA-256, and reports duplicate sets.
Read-only: never deletes or modifies files.
"""
import argparse
import hashlib
import json
import os
import sys
from collections import defaultdict


def sha256_of(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def find_duplicates(roots, min_size=1, skip_hidden=True):
    by_size = defaultdict(list)
    for root in roots:
        for dirpath, dirnames, filenames in os.walk(root):
            if skip_hidden:
                dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            for name in filenames:
                if skip_hidden and name.startswith("."):
                    continue
                p = os.path.join(dirpath, name)
                if os.path.islink(p) or not os.path.isfile(p):
                    continue
                try:
                    size = os.path.getsize(p)
                except OSError:
                    continue
                if size >= min_size:
                    by_size[size].append(p)
    groups = []
    for size, paths in by_size.items():
        if len(paths) < 2:
            continue
        by_hash = defaultdict(list)
        for p in paths:
            try:
                by_hash[sha256_of(p)].append(p)
            except OSError:
                continue
        for digest, same in by_hash.items():
            if len(same) > 1:
                groups.append({"sha256": digest, "size": size, "files": sorted(same)})
    groups.sort(key=lambda g: g["size"] * (len(g["files"]) - 1), reverse=True)
    return groups


def main():
    ap = argparse.ArgumentParser(description="Find duplicate files by content (SHA-256). Read-only.")
    ap.add_argument("paths", nargs="*", default=["."], help="Directories to scan (default: .)")
    ap.add_argument("--min-size", type=int, default=1, help="Ignore files smaller than N bytes (default 1)")
    ap.add_argument("--include-hidden", action="store_true", help="Include dotfiles and dot-directories")
    ap.add_argument("--json", action="store_true", help="Output JSON")
    args = ap.parse_args()

    groups = find_duplicates(args.paths, args.min_size, not args.include_hidden)
    wasted = sum(g["size"] * (len(g["files"]) - 1) for g in groups)
    if args.json:
        json.dump({"groups": groups, "wasted_bytes": wasted}, sys.stdout, indent=2)
        print()
    else:
        for g in groups:
            print(f"[{g['size']} B x{len(g['files'])}] {g['sha256'][:12]}")
            for f in g["files"]:
                print(f"    {f}")
        print(f"{len(groups)} duplicate group(s), {wasted} reclaimable bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
