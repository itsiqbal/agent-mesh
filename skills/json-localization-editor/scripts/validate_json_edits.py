#!/usr/bin/env python3
"""Validate edited JSON localization files against an untouched snapshot.

Usage:
  validate_json_edits.py <original-file-or-dir> <edited-file-or-dir> [--show-changes]

Checks every edited file:
  ERROR  file doesn't parse, has duplicate keys, or is missing
  ERROR  keys added/removed, array length changed, value type changed
  ERROR  number / boolean / null changed
  ERROR  a string that looks technical (URL, slug, ID, path...) changed
  ERROR  placeholders, HTML tags, URLs or Markdown link targets not preserved
  ERROR  a non-empty string became empty
  WARN   key order changed, formatting (indent / trailing newline / BOM) changed
  WARN   value under a technical-sounding key changed (e.g. "type": "Download")
  WARN   leading/trailing whitespace changed, code spans changed
  WARN   short UI string grew a lot (may not fit its button/label)
Exit code 1 if any ERROR.
"""

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import (  # noqa: E402
    code_spans_in, iter_json_files, load_json, placeholders_in,
    tags_in, technical_reason, urls_in,
)


class Report:
    def __init__(self):
        self.errors, self.warns, self.changes = [], [], []

    def err(self, f, path, msg):
        self.errors.append(f"ERROR {f} {path}: {msg}")

    def warn(self, f, path, msg):
        self.warns.append(f"WARN  {f} {path}: {msg}")


def child_path(path, k):
    if isinstance(k, int):
        return f"{path}[{k}]"
    return f"{path}.{k}" if re.match(r"^[A-Za-z_$][\w$]*$", k) else f"{path}[{json.dumps(k, ensure_ascii=False)}]"


def diff_multiset(a, b):
    from collections import Counter
    ca, cb = Counter(a), Counter(b)
    missing = list((ca - cb).elements())
    added = list((cb - ca).elements())
    return missing, added


def compare_strings(rep, f, path, key, old, new):
    if old == new:
        return
    rep.changes.append((f, path, old, new))
    reason = technical_reason(key, old)
    if reason == "value":
        rep.err(f, path, f"technical-looking value changed: {old!r} -> {new!r}")
    elif reason == "key":
        rep.warn(f, path, f"value under technical-sounding key {key!r} changed ({old!r} -> {new!r}); confirm it is user-facing")
    if old.strip() and not new.strip():
        rep.err(f, path, "string became empty")

    strict_o, soft_o = placeholders_in(old)
    strict_n, soft_n = placeholders_in(new)
    missing, added = diff_multiset(strict_o, strict_n)
    if missing or added:
        rep.err(f, path, f"placeholders changed; missing={missing} added={added}")
    missing, added = diff_multiset(soft_o, soft_n)
    if missing or added:
        rep.warn(f, path, f"brace tokens changed inside ICU message (fine if these are translated branch bodies); missing={missing} added={added}")

    missing, added = diff_multiset(tags_in(old), tags_in(new))
    if missing or added:
        rep.err(f, path, f"HTML tags/attributes changed; missing={missing} added={added}")

    missing, added = diff_multiset(urls_in(old), urls_in(new))
    if missing or added:
        rep.err(f, path, f"URLs/link targets changed; missing={missing} added={added}")

    missing, added = diff_multiset(code_spans_in(old), code_spans_in(new))
    if missing or added:
        rep.warn(f, path, f"inline code spans changed; missing={missing} added={added}")

    if old[: len(old) - len(old.lstrip())] != new[: len(new) - len(new.lstrip())] or \
       old[len(old.rstrip()):] != new[len(new.rstrip()):]:
        rep.warn(f, path, "leading/trailing whitespace changed (matters if the string is concatenated)")

    if 0 < len(old) <= 30 and len(new) > max(len(old) * 1.6, len(old) + 12):
        rep.warn(f, path, f"short UI string grew from {len(old)} to {len(new)} chars; check it still fits")


def compare(rep, f, path, key, old, new):
    if type(old) is not type(new) and not (isinstance(old, (int, float)) and isinstance(new, (int, float)) and not isinstance(old, bool) and not isinstance(new, bool)):
        rep.err(f, path, f"type changed: {type(old).__name__} -> {type(new).__name__}")
        return
    if isinstance(old, dict):
        ok, nk = list(old.keys()), list(new.keys())
        for k in ok:
            if k not in new:
                rep.err(f, child_path(path, k), "key removed")
        for k in nk:
            if k not in old:
                rep.err(f, child_path(path, k), "key added")
        common_o = [k for k in ok if k in new]
        common_n = [k for k in nk if k in old]
        if common_o != common_n:
            rep.warn(f, path, "key order changed")
        for k in common_o:
            compare(rep, f, child_path(path, k), k, old[k], new[k])
    elif isinstance(old, list):
        if len(old) != len(new):
            rep.err(f, path, f"array length changed: {len(old)} -> {len(new)}")
        for i, (a, b) in enumerate(zip(old, new)):
            compare(rep, f, child_path(path, i), key, a, b)
    elif isinstance(old, str):
        compare_strings(rep, f, path, key, old, new)
    else:
        if old != new:
            rep.err(f, path, f"non-string value changed: {old!r} -> {new!r}")


def indent_style(raw):
    text = raw.decode("utf-8-sig", errors="replace")
    m = re.search(r"\n([ \t]+)\S", text)
    return m.group(1) if m else ""


def pair_files(orig, edited):
    if not os.path.exists(orig) or not os.path.exists(edited):
        raise ValueError("Original and edited paths must both exist")
    if os.path.isfile(orig) != os.path.isfile(edited):
        raise ValueError("Original and edited paths must both be files or both be directories")
    if os.path.isfile(orig) and os.path.isfile(edited):
        list(iter_json_files([orig, edited]))
        return [(orig, edited, os.path.basename(edited))], [], []
    o_files = {os.path.relpath(p, orig): p for p in iter_json_files([orig])}
    e_files = {os.path.relpath(p, edited): p for p in iter_json_files([edited])}
    pairs = [(o_files[r], e_files[r], r) for r in sorted(o_files) if r in e_files]
    missing = sorted(set(o_files) - set(e_files))
    extra = sorted(set(e_files) - set(o_files))
    return pairs, missing, extra


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("original")
    ap.add_argument("edited")
    ap.add_argument("--show-changes", action="store_true", help="print every changed string (old -> new)")
    args = ap.parse_args()

    rep = Report()
    try:
        pairs, missing, extra = pair_files(args.original, args.edited)
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
    for r in missing:
        rep.err(r, "", "file missing from edited output")
    for r in extra:
        rep.warn(r, "", "new file in edited output that is not in the original")

    changed_files = 0
    for o_path, e_path, rel in pairs:
        try:
            old, old_raw = load_json(o_path)
        except Exception as e:  # noqa: BLE001
            rep.err(rel, "", f"original snapshot is not valid JSON: {e}")
            continue
        try:
            new, new_raw = load_json(e_path)
        except Exception as e:  # noqa: BLE001
            rep.err(rel, "", f"edited file is not valid JSON: {e}")
            continue

        before = len(rep.changes)
        compare(rep, rel, "$", None, old, new)
        if len(rep.changes) > before:
            changed_files += 1

        if old_raw.startswith(b"\xef\xbb\xbf") != new_raw.startswith(b"\xef\xbb\xbf"):
            rep.warn(rel, "", "UTF-8 BOM added or removed")
        if old_raw.endswith(b"\n") and not new_raw.endswith(b"\n"):
            rep.warn(rel, "", "trailing newline removed")
        if indent_style(old_raw) != indent_style(new_raw):
            rep.warn(rel, "", "indentation style changed (file was probably re-serialized; prefer in-place edits)")
        if (b"\\u" in old_raw) != (b"\\u" in new_raw) and old_raw.count(b"\\u") > 3:
            rep.warn(rel, "", "unicode escaping style changed (\\uXXXX vs literal characters)")

    if args.show_changes:
        for f, path, o, n in rep.changes:
            print(f"--- {f} {path}\n  - {json.dumps(o, ensure_ascii=False)}\n  + {json.dumps(n, ensure_ascii=False)}")
        print()

    for line in rep.errors + rep.warns:
        print(line)
    print(f"\nFiles compared: {len(pairs)}  Files changed: {changed_files}  Strings changed: {len(rep.changes)}  "
          f"Errors: {len(rep.errors)}  Warnings: {len(rep.warns)}")
    sys.exit(1 if rep.errors else 0)


if __name__ == "__main__":
    main()
