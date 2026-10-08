#!/usr/bin/env python3
"""List the user-facing strings in JSON files, with their JSON paths.

Usage:
  extract_strings.py <file-or-dir> [more ...] [--all] [--json] [--max-len N]

By default, values that look technical (URLs, slugs, IDs, paths, colour codes,
placeholder-only strings, numbers) are skipped. --all includes every string.
--json prints machine-readable output. Invalid JSON files are reported, not skipped silently.
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import iter_json_files, load_json, walk, technical_reason  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--all", action="store_true", help="include strings that look technical")
    ap.add_argument("--json", action="store_true", help="output JSON")
    ap.add_argument("--max-len", type=int, default=0, help="truncate displayed values to N chars (text mode)")
    args = ap.parse_args()

    results = []
    errors = []
    total_files = 0
    try:
        files = list(iter_json_files(args.paths))
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
    for f in files:
        total_files += 1
        try:
            data, _ = load_json(f)
        except Exception as e:  # noqa: BLE001
            errors.append({"file": f, "error": str(e)})
            continue
        entries = []
        skipped = 0
        for path, key, value in walk(data):
            if not isinstance(value, str):
                continue
            reason = technical_reason(key, value)
            if reason and not args.all:
                skipped += 1
                continue
            entries.append({"path": path, "value": value, **({"technical": reason} if reason else {})})
        results.append({"file": f, "strings": entries, "skipped_technical": skipped})

    if args.json:
        json.dump({"files": results, "errors": errors}, sys.stdout, ensure_ascii=False, indent=2)
        print()
    else:
        n_strings = 0
        for r in results:
            print(f"=== {r['file']}  ({len(r['strings'])} strings, {r['skipped_technical']} technical skipped)")
            for e in r["strings"]:
                v = e["value"]
                if args.max_len and len(v) > args.max_len:
                    v = v[: args.max_len] + "…"
                tag = f"  [technical:{e['technical']}]" if "technical" in e else ""
                print(f"{e['path']}{tag}\n    {json.dumps(v, ensure_ascii=False)}")
            n_strings += len(r["strings"])
            print()
        for e in errors:
            print(f"!!! INVALID JSON: {e['file']}: {e['error']}")
        print(f"Files: {total_files}  Strings listed: {n_strings}  Invalid files: {len(errors)}")

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
