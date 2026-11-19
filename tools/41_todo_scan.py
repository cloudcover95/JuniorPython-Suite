#!/usr/bin/env python3
"""Todo scanner: list TODO/FIXME/HACK/XXX markers in a source tree. Stdlib only, read-only."""
import argparse, json, os, re, sys

PAT = re.compile(r"\b(TODO|FIXME|HACK|XXX)\b[:\s-]*(.*)")
SKIP = {".git", "node_modules", "__pycache__", ".venv"}


def scan(root, exts, max_bytes):
    for dp, dns, fns in os.walk(root):
        dns[:] = sorted(d for d in dns if d not in SKIP)
        for fn in sorted(fns):
            if exts and os.path.splitext(fn)[1] not in exts:
                continue
            p = os.path.join(dp, fn)
            try:
                if os.path.getsize(p) > max_bytes:
                    continue
                with open(p, "r", encoding="utf-8", errors="ignore") as f:
                    for n, line in enumerate(f, 1):
                        m = PAT.search(line)
                        if m:
                            yield {"file": os.path.relpath(p, root), "line": n,
                                   "tag": m.group(1), "text": m.group(2).strip()[:120]}
            except OSError:
                continue


def main(argv=None):
    ap = argparse.ArgumentParser(description="List TODO/FIXME/HACK/XXX markers under a directory.")
    ap.add_argument("root", nargs="?", default=".", help="directory to scan")
    ap.add_argument("--ext", action="append", default=[], help="extension filter, e.g. .py (repeatable)")
    ap.add_argument("--max-bytes", type=int, default=1_000_000)
    ap.add_argument("--json", action="store_true", help="emit JSON")
    a = ap.parse_args(argv)
    hits = list(scan(a.root, set(a.ext), a.max_bytes))
    if a.json:
        print(json.dumps(hits, indent=2))
    else:
        for h in hits:
            print(f"{h['file']}:{h['line']}: {h['tag']} {h['text']}")
        print(f"total: {len(hits)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
