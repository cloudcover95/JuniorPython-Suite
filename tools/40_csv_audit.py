#!/usr/bin/env python3
"""CSV audit: report ragged rows, empty files, and non-UTF-8 CSVs under a root.

Read-only, stdlib only, no network. Usage: csv_audit.py [ROOT] [--json]
"""
import argparse
import csv
import json
import os
import sys


def audit_file(path):
    info = {"path": path, "rows": 0, "columns": 0, "ragged": 0, "issue": ""}
    try:
        with open(path, "r", encoding="utf-8", newline="") as fh:
            rows = list(csv.reader(fh))
    except UnicodeDecodeError:
        info["issue"] = "not-utf8"
        return info
    except (OSError, csv.Error) as exc:
        info["issue"] = "error: %s" % exc
        return info
    if not rows:
        info["issue"] = "empty"
        return info
    info["rows"] = len(rows)
    info["columns"] = len(rows[0])
    info["ragged"] = sum(1 for r in rows[1:] if len(r) != len(rows[0]))
    if info["ragged"]:
        info["issue"] = "ragged"
    return info


def main(argv=None):
    ap = argparse.ArgumentParser(description="Audit CSV files under a root (read-only).")
    ap.add_argument("root", nargs="?", default=".", help="directory to scan")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    args = ap.parse_args(argv)
    results = []
    for dp, dn, fn in os.walk(args.root):
        dn[:] = [d for d in dn if d != ".git"]
        for f in sorted(fn):
            if f.lower().endswith(".csv"):
                results.append(audit_file(os.path.join(dp, f)))
    bad = [r for r in results if r["issue"]]
    if args.json:
        print(json.dumps({"files": len(results), "flagged": bad}, indent=2))
    else:
        print("csv files: %d, flagged: %d" % (len(results), len(bad)))
        for r in bad:
            print("  %s: %s (rows=%d ragged=%d)" % (r["path"], r["issue"], r["rows"], r["ragged"]))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
