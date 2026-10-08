#!/usr/bin/env python3
"""Shared helpers for the json-localization-editor scripts."""

import json
import os
import re

SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", ".nuxt", "out", "coverage", "__pycache__", ".venv", "venv"}
SKIP_FILES = {"package.json", "package-lock.json", "tsconfig.json", "jsconfig.json", "composer.json", "composer.lock", ".eslintrc.json", "manifest.json"}

# Keys whose values are almost always technical, not user-facing.
TECHNICAL_KEYS = {
    "id", "_id", "uuid", "key", "slug", "url", "href", "src", "path", "route", "link", "permalink", "canonical",
    "icon", "image", "img", "thumbnail", "logo", "type", "kind", "variant", "color", "colour", "class", "classname",
    "component", "template", "layout", "name_id", "code", "lang", "locale", "hreflang", "mime", "mimetype",
    "format", "extension", "ext", "email", "phone", "date", "datetime", "timestamp", "version", "hash", "target",
    "rel", "method", "action", "status", "category_id", "parent_id", "sort", "order", "width", "height",
}

URL_RE = re.compile(r"^(https?://|mailto:|tel:|www\.)\S*$", re.I)
PATH_RE = re.compile(r"^(/|\./|\.\./)[\w\-./#?=&%]*$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:[-_][a-z0-9]+)+$")
IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z0-9_]+)+$")  # dotted.key.paths
CONST_RE = re.compile(r"^[A-Z0-9_]{2,}$")
HEX_RE = re.compile(r"^#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
NUMLIKE_RE = re.compile(r"^[\d\s.,:%+\-/x×]*$")
FILE_RE = re.compile(r"^[\w\-.]+\.(png|jpe?g|gif|svg|webp|avif|ico|pdf|json|js|ts|css|html?|mp4|webm|mp3|woff2?)$", re.I)
EMAIL_RE = re.compile(r"^[\w.+\-]+@[\w\-]+\.[\w.\-]+$")
MIME_RE = re.compile(r"^[a-z]+/[a-z0-9.+\-]+$")
UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)

# Placeholders / template syntax that must survive edits verbatim.
PLACEHOLDER_PATTERNS = [
    re.compile(r"\{\{\{?\s*[^{}]+?\s*\}?\}\}"),              # {{name}} / {{{html}}}
    re.compile(r"\$\{[^{}]+\}"),                            # ${var}
    re.compile(r"%(?:\d+\$)?[-+0#]*\d*(?:\.\d+)?[sdifuxX@]"),  # printf: %s %d %1$s %.2f %@
    re.compile(r"%\([A-Za-z_]\w*\)[sd]"),                   # python %(name)s
    re.compile(r"\$t\([^)]*\)"),                            # i18next nesting $t(key)
    re.compile(r"@:[\w.\-]+"),                              # vue-i18n linked @:key
    re.compile(r"(?:(?<=\s)|^):[a-zA-Z_]\w*\b"),          # laravel :param
    re.compile(r"\[\[\s*[^\[\]]+\s*\]\]"),                  # [[var]]
]
# ICU / single-brace placeholders: {name}, {count, plural, ...} -> capture the argument name + type
ICU_ARG_RE = re.compile(r"(?<![{$])\{\s*([A-Za-z_][\w.\-]*)\s*(?:,\s*(plural|select|selectordinal|number|date|time)\b)?")
HTML_TAG_RE = re.compile(r"</?[A-Za-z][\w\-]*(?:\s+[^<>]*?)?/?>")
MD_LINK_TARGET_RE = re.compile(r"\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
INLINE_URL_RE = re.compile(r"(?:https?://|mailto:|www\.)[^\s\"'<>)\]]+", re.I)
CODE_SPAN_RE = re.compile(r"`[^`]+`")


def iter_json_files(paths):
    """Yield JSON file paths from files or directories (recursive)."""
    for p in paths:
        if not os.path.exists(p):
            raise ValueError(f"Input path does not exist: {p}")
        if os.path.isfile(p):
            if not str(p).lower().endswith(".json"):
                raise ValueError(f"Expected a JSON file: {p}")
            yield p
            continue
        if not os.path.isdir(p):
            raise ValueError(f"Expected a JSON file or directory: {p}")
        found = False
        for root, dirs, files in os.walk(p):
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
            for f in sorted(files):
                if f.lower().endswith(".json") and f not in SKIP_FILES:
                    found = True
                    yield os.path.join(root, f)
        if not found:
            raise ValueError(f"No reviewable JSON files in directory: {p}")


class DuplicateKeyError(ValueError):
    pass


def _no_dupes(pairs):
    obj = {}
    for k, v in pairs:
        if k in obj:
            raise DuplicateKeyError(f"duplicate key {k!r}")
        obj[k] = v
    return obj


def _reject_constant(value):
    raise ValueError(f"Nonstandard JSON constant: {value}")


def load_json(path, check_dupes=True):
    with open(path, "rb") as fh:
        raw = fh.read()
    text = raw.decode("utf-8-sig")
    if check_dupes:
        return json.loads(text, object_pairs_hook=_no_dupes, parse_constant=_reject_constant), raw
    return json.loads(text, parse_constant=_reject_constant), raw


def walk(node, path="$"):
    """Yield (json_path, key, value) for every leaf."""
    if isinstance(node, dict):
        for k, v in node.items():
            child = f"{path}.{k}" if re.match(r"^[A-Za-z_$][\w$]*$", k) else f"{path}[{json.dumps(k, ensure_ascii=False)}]"
            if isinstance(v, (dict, list)):
                yield from walk(v, child)
            else:
                yield child, k, v
    elif isinstance(node, list):
        for i, v in enumerate(node):
            child = f"{path}[{i}]"
            if isinstance(v, (dict, list)):
                yield from walk(v, child)
            else:
                # inherit parent key for arrays of strings (e.g. "keywords": [...])
                parent_key = re.sub(r"\[\d+\]$", "", path).split(".")[-1]
                yield child, parent_key, v
    else:
        yield path, None, node


def only_placeholders(s):
    stripped = s
    for pat in PLACEHOLDER_PATTERNS:
        stripped = pat.sub("", stripped)
    stripped = ICU_SIMPLE_RE.sub("", stripped)
    stripped = HTML_TAG_RE.sub("", stripped)
    return stripped.strip(" \t\n.,:;-–—|/()[]") == ""


ICU_SIMPLE_RE = re.compile(r"\{\s*[A-Za-z_][\w.\-]*\s*\}")


def technical_reason(key, value):
    """Why a string value looks non-user-facing: "value" (its content looks like an
    identifier/URL/path/etc.), "key" (only its key name suggests so), or None."""
    if not isinstance(value, str):
        return "value"
    s = value.strip()
    if s == "":
        return "value"
    for rx in (URL_RE, PATH_RE, SLUG_RE, IDENT_RE, CONST_RE, HEX_RE, FILE_RE, EMAIL_RE, MIME_RE, UUID_RE):
        if rx.match(s):
            return "value"
    if NUMLIKE_RE.match(s) or only_placeholders(s):
        return "value"
    raw_key = key or ""
    k = raw_key.lower().replace("-", "_")
    key_says_technical = (
        k in TECHNICAL_KEYS
        or k.endswith(("_id", "_url", "_href", "_slug", "_path", "_key", "_icon", "_src", "_color", "_type"))
        or raw_key.endswith(("Id", "Url", "Href", "Slug", "Path"))
    )
    if key_says_technical and " " not in s:
        return "key"
    return None


def is_technical(key, value):
    return technical_reason(key, value) is not None


COMPLEX_ICU_RE = re.compile(r"\{\s*[A-Za-z_][\w.\-]*\s*,\s*(plural|select|selectordinal)\b")


def placeholders_in(s):
    """Return (strict, soft) sorted token lists.

    strict: tokens that must survive verbatim (a mismatch is an error).
    soft:   simple {word} tokens inside strings that also contain ICU plural/select
            blocks, where {word} may be a translatable branch body like {he}; a
            mismatch there is only a warning.
    """
    strict = []
    for pat in PLACEHOLDER_PATTERNS:
        strict.extend(m.group(0) for m in pat.finditer(s))
    has_complex = bool(COMPLEX_ICU_RE.search(s))
    soft = []
    for m in ICU_ARG_RE.finditer(s):
        name, kind = m.group(1), m.group(2)
        if kind:
            strict.append("{" + name + "," + kind + "}")
        elif has_complex:
            soft.append("{" + name + "}")
        else:
            strict.append("{" + name + "}")
    return sorted(strict), sorted(soft)


def normalize_tag(tag):
    # compare tags by name + attributes (attribute text like alt/title may be translated, so keep only href/src/class/id etc.)
    m = re.match(r"</?\s*([A-Za-z][\w\-]*)", tag)
    name = m.group(1).lower() if m else tag
    closing = tag.startswith("</")
    keep = []
    for am in re.finditer(r"([\w\-:]+)\s*=\s*(\"[^\"]*\"|'[^']*'|\S+)", tag):
        attr = am.group(1).lower()
        if attr in {"alt", "title", "aria-label", "placeholder"}:
            keep.append(attr)  # value may be localized
        else:
            keep.append(f"{attr}={am.group(2)}")
    return ("/" if closing else "") + name + ("[" + ",".join(sorted(keep)) + "]" if keep else "")


def tags_in(s):
    return sorted(normalize_tag(t) for t in HTML_TAG_RE.findall(s))


def urls_in(s):
    urls = INLINE_URL_RE.findall(s) + MD_LINK_TARGET_RE.findall(s)
    return sorted({u.rstrip(".,;:!?") for u in urls})


def code_spans_in(s):
    return sorted(CODE_SPAN_RE.findall(s))
