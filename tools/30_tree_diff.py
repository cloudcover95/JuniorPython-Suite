#!/usr/bin/env python3
"""tree_diff: compare two directory trees, read-only.

JuniorPython-Suite tool. JuniorCloud LLC. Stdlib only.
Reports files that were added, removed, or changed between a LEFT and a
RIGHT directory. Changes are detected by size first, then SHA-256.
Never writes, moves, or deletes anything. No network. No server.
Guards: mint false, socket false, layer_one false, fetch false.
"""
import argparse
import hashlib
import json
import os
import sys

CHUNK = 1 << 16


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            block = fh.read(CHUNK)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def walk(root, skip_hidden):
    found = {}
    for dirpath, dirnames, filenames in os.walk(root):
        if skip_hidden:
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        dirnames.sort()
        for name in sorted(filenames):
            if skip_hidden and name.startswith("."):
                continue
            full = os.path.join(dirpath, name)
            if os.path.islink(full) or not os.path.isfile(full):
                continue
            rel = os.path.relpath(full, root).replace(os.sep, "/")
            try:
                found[rel] = os.path.getsize(full)
            except OSError:
                continue
    return found


def diff_trees(left, right, skip_hidden=True, quick=False):
    a = walk(left, skip_hidden)
    b = walk(right, skip_hidden)
    added = sorted(set(b) - set(a))
    removed = sorted(set(a) - set(b))
    changed = []
    same = 0
    for rel in sorted(set(a) & set(b)):
        if a[rel] != b[rel]:
            changed.append(rel)
        elif quick:
            same += 1
        else:
            try:
                if sha256_of(os.path.join(left, rel)) != sha256_of(os.path.join(right, rel)):
                    changed.append(rel)
                else:
                    same += 1
            except OSError:
                changed.append(rel)
    return {"left": left, "right": right, "added": added, "removed": removed,
            "changed": changed, "unchanged": same}


def build_parser():
    p = argparse.ArgumentParser(
        prog="tree_diff",
        description="Compare two directory trees (read-only): added, removed, changed files.")
    p.add_argument("left", help="baseline directory")
    p.add_argument("right", help="directory to compare against the baseline")
    p.add_argument("--all", action="store_true", help="include hidden files and folders")
    p.add_argument("--quick", action="store_true", help="compare by size only, skip hashing")
    p.add_argument("--json", action="store_true", help="print the result as JSON")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    for d in (args.left, args.right):
        if not os.path.isdir(d):
            print("not a directory: %s" % d, file=sys.stderr)
            return 2
    res = diff_trees(args.left, args.right, skip_hidden=not args.all, quick=args.quick)
    if args.json:
        print(json.dumps(res, indent=2))
    else:
        for tag, key in (("+", "added"), ("-", "removed"), ("~", "changed")):
            for rel in res[key]:
                print("%s %s" % (tag, rel))
        print("added %d, removed %d, changed %d, unchanged %d" % (
            len(res["added"]), len(res["removed"]), len(res["changed"]), res["unchanged"]))
    return 1 if (res["added"] or res["removed"] or res["changed"]) else 0


if __name__ == "__main__":
    sys.exit(main())
