#!/usr/bin/env python3
"""Read-only symlink audit: broken links, absolute targets, links escaping the root, loops.

Walks a folder without following symlinks and reports every symbolic link it finds,
with its raw target, whether the target exists, whether the target is absolute,
whether the resolved target lands outside the scanned root, and whether resolving
it loops. Useful before archiving, syncing or publishing a tree.

Stdlib only. Offline. Never modifies any file. Opens no sockets.
mint false. socket false. layer_one false. fetch false. ue5_launch false.
JuniorCloud LLC. cloudcover95.
"""
import argparse
import json
import os
import sys

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".mypy_cache"}


def inspect_link(path, root_real):
    target = os.readlink(path)
    info = {
        "path": path,
        "target": target,
        "absolute": os.path.isabs(target),
        "exists": False,
        "escapes_root": False,
        "loop": False,
    }
    try:
        resolved = os.path.realpath(path, strict=True)
        info["exists"] = True
    except (OSError, RuntimeError) as exc:
        if isinstance(exc, RuntimeError) or getattr(exc, "errno", None) == 40:
            info["loop"] = True
        resolved = os.path.realpath(path)
    info["resolved"] = resolved
    try:
        info["escapes_root"] = os.path.commonpath([root_real, resolved]) != root_real
    except ValueError:
        info["escapes_root"] = True
    flags = []
    if info["loop"]:
        flags.append("loop")
    elif not info["exists"]:
        flags.append("broken")
    if info["absolute"]:
        flags.append("absolute")
    if info["escapes_root"]:
        flags.append("escapes")
    info["flags"] = flags
    return info


def walk(root, skip):
    root_real = os.path.realpath(root)
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        keep = []
        for d in sorted(dirnames):
            full = os.path.join(dirpath, d)
            if os.path.islink(full):
                yield inspect_link(full, root_real)
            elif d not in skip:
                keep.append(d)
        dirnames[:] = keep
        for f in sorted(filenames):
            full = os.path.join(dirpath, f)
            if os.path.islink(full):
                yield inspect_link(full, root_real)


def main(argv=None):
    p = argparse.ArgumentParser(description="Read-only symlink audit (broken, absolute, escaping, loops).")
    p.add_argument("root", nargs="?", default=".", help="folder to scan (default: .)")
    p.add_argument("--json", action="store_true", help="emit JSON instead of text")
    p.add_argument("--problems", action="store_true", help="only list links with at least one flag")
    p.add_argument("--include-skipped", action="store_true", help="also descend into .git, node_modules, venvs")
    p.add_argument("--strict", action="store_true", help="exit 1 if any broken or looping link is found")
    a = p.parse_args(argv)
    if not os.path.isdir(a.root):
        print(f"not a folder: {a.root}", file=sys.stderr)
        return 2
    skip = set() if a.include_skipped else SKIP_DIRS
    links = list(walk(a.root, skip))
    shown = [l for l in links if l["flags"]] if a.problems else links
    summary = {
        "root": os.path.realpath(a.root),
        "links": len(links),
        "broken": sum(1 for l in links if "broken" in l["flags"]),
        "loops": sum(1 for l in links if "loop" in l["flags"]),
        "absolute": sum(1 for l in links if l["absolute"]),
        "escapes_root": sum(1 for l in links if l["escapes_root"]),
    }
    if a.json:
        print(json.dumps({"summary": summary, "links": shown}, indent=2))
    else:
        for l in shown:
            tag = ",".join(l["flags"]) or "ok"
            print(f"[{tag}] {l['path']} -> {l['target']}")
        print(f"links={summary['links']} broken={summary['broken']} loops={summary['loops']} "
              f"absolute={summary['absolute']} escapes_root={summary['escapes_root']}")
    if a.strict and (summary["broken"] or summary["loops"]):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
