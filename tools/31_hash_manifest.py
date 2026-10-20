#!/usr/bin/env python3
"""Hash manifest: build and verify SHA-256 manifests for a directory tree.

Part of JuniorPython-Suite (JuniorCloud LLC). Stdlib only, offline, no network.
Read-only on the scanned tree: it only writes a manifest when --out is given.

Manifest format is one line per file, compatible with `sha256sum -c`:
    <64 hex digest>  <relative/posix/path>

Examples:
    python3 hash_manifest.py build ./project > project.sha256
    python3 hash_manifest.py build ./project --out project.sha256 --exclude .git
    python3 hash_manifest.py verify ./project project.sha256
    python3 hash_manifest.py verify ./project project.sha256 --json
"""
import argparse
import fnmatch
import hashlib
import json
import os
import sys

CHUNK = 1 << 20
DEFAULT_EXCLUDES = (".git", "__pycache__", ".DS_Store")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            block = fh.read(CHUNK)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def _excluded(name, patterns):
    return any(fnmatch.fnmatch(name, p) for p in patterns)


def walk_files(root, excludes):
    """Yield relative posix paths of regular files under root, sorted."""
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if not _excluded(d, excludes))
        for name in filenames:
            if _excluded(name, excludes):
                continue
            full = os.path.join(dirpath, name)
            if os.path.islink(full) or not os.path.isfile(full):
                continue
            rel = os.path.relpath(full, root).replace(os.sep, "/")
            out.append(rel)
    return sorted(out)


def build_manifest(root, excludes):
    entries = {}
    for rel in walk_files(root, excludes):
        try:
            entries[rel] = sha256_file(os.path.join(root, rel))
        except OSError as exc:
            print("warn: cannot read %s: %s" % (rel, exc), file=sys.stderr)
    return entries


def format_manifest(entries):
    return "".join("%s  %s\n" % (d, p) for p, d in sorted(entries.items()))


def parse_manifest(text):
    entries = {}
    for lineno, line in enumerate(text.splitlines(), 1):
        line = line.rstrip("\r")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        parts = line.split(None, 1)
        if len(parts) != 2 or len(parts[0]) != 64:
            raise ValueError("bad manifest line %d: %r" % (lineno, line))
        digest, path = parts
        entries[path.lstrip("*").strip()] = digest.lower()
    return entries


def compare(expected, actual):
    ok, changed, missing, extra = [], [], [], []
    for path, digest in sorted(expected.items()):
        if path not in actual:
            missing.append(path)
        elif actual[path] != digest:
            changed.append(path)
        else:
            ok.append(path)
    extra = sorted(p for p in actual if p not in expected)
    return {"ok": ok, "changed": changed, "missing": missing, "extra": extra}


def cmd_build(args):
    if not os.path.isdir(args.root):
        print("error: not a directory: %s" % args.root, file=sys.stderr)
        return 2
    entries = build_manifest(args.root, args.exclude)
    text = format_manifest(entries)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("wrote %d entries to %s" % (len(entries), args.out), file=sys.stderr)
    else:
        sys.stdout.write(text)
    return 0


def cmd_verify(args):
    if not os.path.isdir(args.root):
        print("error: not a directory: %s" % args.root, file=sys.stderr)
        return 2
    try:
        with open(args.manifest, "r", encoding="utf-8") as fh:
            expected = parse_manifest(fh.read())
    except (OSError, ValueError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    actual = build_manifest(args.root, args.exclude)
    out_path = os.path.abspath(args.manifest)
    actual = {p: d for p, d in actual.items()
              if os.path.abspath(os.path.join(args.root, p)) != out_path}
    result = compare(expected, actual)
    bad = bool(result["changed"] or result["missing"] or (args.strict and result["extra"]))
    if args.json:
        summary = {k: len(v) for k, v in result.items()}
        print(json.dumps({"summary": summary, "detail": result, "pass": not bad}, indent=2))
    else:
        for key in ("changed", "missing", "extra"):
            for path in result[key]:
                print("%-8s %s" % (key.upper(), path))
        print("ok=%d changed=%d missing=%d extra=%d -> %s" % (
            len(result["ok"]), len(result["changed"]), len(result["missing"]),
            len(result["extra"]), "FAIL" if bad else "PASS"))
    return 1 if bad else 0


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Build and verify SHA-256 manifests for a directory tree (stdlib, offline).")
    sub = p.add_subparsers(dest="cmd")
    b = sub.add_parser("build", help="hash every file under ROOT and print a manifest")
    b.add_argument("root")
    b.add_argument("--out", help="write manifest to this file instead of stdout")
    v = sub.add_parser("verify", help="compare ROOT against a manifest file")
    v.add_argument("root")
    v.add_argument("manifest")
    v.add_argument("--json", action="store_true", help="print a JSON report")
    v.add_argument("--strict", action="store_true", help="fail on extra files too")
    for sp in (b, v):
        sp.add_argument("--exclude", action="append", default=list(DEFAULT_EXCLUDES),
                        help="glob for file/dir names to skip (repeatable)")
    args = p.parse_args(argv)
    if args.cmd == "build":
        return cmd_build(args)
    if args.cmd == "verify":
        return cmd_verify(args)
    p.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
