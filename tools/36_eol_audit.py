#!/usr/bin/env python3
"""Read-only text hygiene audit: line endings, BOMs, trailing whitespace, final newline.

Walks a folder (or checks single files) and reports, per text file, whether it uses
LF, CRLF, CR or mixed line endings, starts with a UTF-8 BOM, has trailing
whitespace, or is missing a final newline. Binary files are skipped.

Stdlib only. Offline. Never modifies any file. Opens no sockets.
JuniorCloud LLC. cloudcover95.
"""
import argparse
import json
import os
import sys

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".mypy_cache"}
BOM = b"\xef\xbb\xbf"


def is_binary(data):
    return b"\x00" in data[:8192]


def audit_bytes(data):
    crlf = data.count(b"\r\n")
    cr = data.count(b"\r") - crlf
    lf = data.count(b"\n") - crlf
    kinds = [k for k, n in (("LF", lf), ("CRLF", crlf), ("CR", cr)) if n]
    eol = "none" if not kinds else (kinds[0] if len(kinds) == 1 else "mixed")
    trailing = 0
    for line in data.replace(b"\r\n", b"\n").replace(b"\r", b"\n").split(b"\n"):
        if line.endswith((b" ", b"\t")):
            trailing += 1
    return {
        "eol": eol,
        "lf": lf,
        "crlf": crlf,
        "cr": cr,
        "bom": data.startswith(BOM),
        "trailing_ws_lines": trailing,
        "final_newline": (not data) or data.endswith((b"\n", b"\r")),
    }


def iter_files(paths, max_bytes):
    for p in paths:
        if os.path.isfile(p):
            yield p
            continue
        for root, dirs, files in os.walk(p):
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
            for name in sorted(files):
                fp = os.path.join(root, name)
                try:
                    if os.path.islink(fp) or os.path.getsize(fp) > max_bytes:
                        continue
                except OSError:
                    continue
                yield fp


def issues_of(r, expect):
    out = []
    if r["eol"] == "mixed":
        out.append("mixed-eol")
    elif expect and r["eol"] not in ("none", expect):
        out.append("eol-" + r["eol"].lower())
    if r["bom"]:
        out.append("bom")
    if r["trailing_ws_lines"]:
        out.append("trailing-ws")
    if not r["final_newline"]:
        out.append("no-final-newline")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("paths", nargs="*", default=["."], help="files or folders (default .)")
    ap.add_argument("--expect", choices=["LF", "CRLF"], default="LF",
                    help="expected line ending (default LF)")
    ap.add_argument("--max-bytes", type=int, default=5_000_000,
                    help="skip files larger than this (default 5000000)")
    ap.add_argument("--all", action="store_true", help="list clean files too")
    ap.add_argument("--json", action="store_true", help="JSON output")
    a = ap.parse_args(argv)

    rows, scanned, binary = [], 0, 0
    for fp in iter_files(a.paths, a.max_bytes):
        try:
            with open(fp, "rb") as fh:
                data = fh.read()
        except OSError:
            continue
        if is_binary(data):
            binary += 1
            continue
        scanned += 1
        r = audit_bytes(data)
        r["path"] = fp
        r["issues"] = issues_of(r, a.expect)
        if r["issues"] or a.all:
            rows.append(r)

    flagged = sum(1 for r in rows if r["issues"])
    if a.json:
        print(json.dumps({"scanned": scanned, "binary_skipped": binary,
                          "flagged": flagged, "files": rows}, indent=2))
    else:
        for r in rows:
            print("%-6s %s  %s" % (r["eol"], r["path"], ",".join(r["issues"]) or "ok"))
        print("scanned=%d binary_skipped=%d flagged=%d" % (scanned, binary, flagged))
    return 1 if flagged else 0


if __name__ == "__main__":
    sys.exit(main())
