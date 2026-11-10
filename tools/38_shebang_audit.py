#!/usr/bin/env python3
"""Shebang audit: report scripts whose shebang and executable bit disagree.

Read-only, stdlib only. Walks a directory and flags files that have a
shebang but no exec bit, or an exec bit on a text file with no shebang.
"""
import argparse
import os
import stat
import sys

SKIP = {".git", "__pycache__", "node_modules"}


def audit(root):
    rows = []
    for d, dirs, files in os.walk(root):
        dirs[:] = sorted(x for x in dirs if x not in SKIP)
        for f in sorted(files):
            p = os.path.join(d, f)
            try:
                st = os.lstat(p)
                if not stat.S_ISREG(st.st_mode):
                    continue
                with open(p, "rb") as fh:
                    head = fh.read(256)
            except OSError:
                continue
            if b"\0" in head:
                continue
            shebang = head.startswith(b"#!")
            exe = bool(st.st_mode & 0o111)
            if shebang and not exe:
                rows.append(("shebang-not-exec", p))
            elif exe and not shebang:
                rows.append(("exec-no-shebang", p))
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description="Audit shebang vs exec-bit mismatches (read-only).")
    ap.add_argument("root", nargs="?", default=".", help="directory to scan")
    ap.add_argument("--selftest", action="store_true", help="run a built-in smoke test")
    a = ap.parse_args(argv)
    if a.selftest:
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            with open(os.path.join(t, "a.sh"), "w") as fh:
                fh.write("#!/bin/sh\necho hi\n")
            with open(os.path.join(t, "b.txt"), "w") as fh:
                fh.write("plain\n")
            os.chmod(os.path.join(t, "b.txt"), 0o755)
            kinds = sorted(k for k, _ in audit(t))
            assert kinds == ["exec-no-shebang", "shebang-not-exec"], kinds
        print("selftest ok")
        return 0
    rows = audit(a.root)
    for k, p in rows:
        print("%-17s %s" % (k, p))
    print("mismatches: %d" % len(rows))
    return 1 if rows else 0


if __name__ == "__main__":
    sys.exit(main())
