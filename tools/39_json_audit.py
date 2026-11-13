#!/usr/bin/env python3
"""JSON audit: report .json files that fail to parse or have duplicate keys.

Read-only, stdlib only. Walks a directory, parses each .json file and
prints problems with file and reason. Exit 1 if any problem is found.
"""
import argparse
import json
import os
import sys

SKIP = {".git", "__pycache__", "node_modules"}


def _pairs(pairs):
    seen = set()
    for k, _ in pairs:
        if k in seen:
            raise ValueError("duplicate key: %r" % k)
        seen.add(k)
    return dict(pairs)


def audit(root):
    bad = []
    total = 0
    for d, dirs, files in os.walk(root):
        dirs[:] = sorted(x for x in dirs if x not in SKIP)
        for f in sorted(files):
            if not f.endswith(".json"):
                continue
            p = os.path.join(d, f)
            total += 1
            try:
                with open(p, "r", encoding="utf-8") as fh:
                    json.load(fh, object_pairs_hook=_pairs)
            except (ValueError, UnicodeDecodeError) as e:
                bad.append((p, str(e)))
            except OSError as e:
                bad.append((p, "unreadable: %s" % e))
    return total, bad


def main(argv=None):
    ap = argparse.ArgumentParser(description="Report invalid or duplicate-key JSON files (read-only).")
    ap.add_argument("root", nargs="?", default=".", help="directory to scan")
    a = ap.parse_args(argv)
    if not os.path.isdir(a.root):
        print("not a directory: %s" % a.root, file=sys.stderr)
        return 2
    total, bad = audit(a.root)
    for p, why in bad:
        print("%s: %s" % (os.path.relpath(p, a.root), why))
    print("checked=%d problems=%d" % (total, len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
