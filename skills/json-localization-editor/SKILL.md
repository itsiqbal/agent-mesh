---
name: json-localization-editor
description: Edit and localize user-facing strings in JSON locale, CMS, SEO, and FAQ files while preserving structure and technical values. Use for grammar fixes, translation polishing, or native-language JSON copy editing; excludes YAML and application configuration.
---

# JSON Localization Editor

You are acting as an expert translator, native-language editor and localization specialist. The input is one or more JSON files (or folders, possibly nested) containing AI-generated content that will be published. The goal is text that reads as if a fluent native speaker wrote it for this audience, with the JSON still working exactly as before in the application.

The deliverable is the corrected JSON files, edited in place with the same paths and filenames, plus a short report. If the user explicitly asks for review only, report proposed fixes without editing files. Do not write an explanation of the content itself unless asked.

## Step 1: Establish the brief

You need four things before editing:

- **Target language** (and variant: pt-BR vs pt-PT, es-ES vs es-MX, zh-Hans vs zh-Hant, en-GB vs en-US, ms-MY vs id-ID, and so on)
- **Target market / region**
- **Audience** (general consumers, business users, developers, travellers...)
- **Context** (what the product or site is, where the text appears)

Take them from the user's message, applicable project `AGENTS.md`, `CLAUDE.md`, or `GEMINI.md` guidance, or a style guide or glossary file in the repo. If the language is missing, infer it from the content and file names (`de.json`, `locales/fr-CA/`) and state what you inferred. Ask only if the language or variant is genuinely ambiguous, since a wrong variant means redoing every file. Also note the formality register the existing content uses (du/Sie, tu/vous, tú/usted, anda/awak, 您/你) and keep it unless the user says otherwise.

Look for an existing glossary, style guide or reference locale (often `en.json`) and use it. If a source-language file exists alongside the target files, compare against it to catch mistranslations and omissions.

## Step 2: Inventory and snapshot

1. List the JSON files in scope. Skip `node_modules`, build output, lockfiles, `package.json`, `tsconfig.json` and other config files unless the user explicitly includes them.
2. Snapshot the originals before touching anything, so the validator has something to compare against:
   ```bash
   TARGET_PATH="<absolute target file or directory path>"
   SNAP="$(mktemp -d)"
   ORIGINAL_PATH="$SNAP/$(basename "$TARGET_PATH")"
   cp -R "$TARGET_PATH" "$ORIGINAL_PATH"
   ```
   Confirm the copy succeeded before editing. Repeat for separate target paths as needed. If the files are in a clean git working tree you can instead validate against `git show HEAD:<file>`, but the snapshot is simpler and works everywhere.
3. Get an overview of the reviewable text:
   ```bash
   SKILL_DIR="<absolute directory containing this loaded SKILL.md>"
   python3 "$SKILL_DIR/scripts/extract_strings.py" "$TARGET_PATH"
   ```
   It prints each user-facing string with its JSON path and skips values that look technical (URLs, slugs, IDs, paths, colour codes, pure placeholders). Use `--all` to include everything, or `--json` for machine-readable output. Resolve `SKILL_DIR` from the loaded skill location; do not assume a global home directory or a particular tool installation.

## Step 3: Build a working glossary

Before editing, skim all files and decide on one rendering for recurring terms: UI verbs (upload, download, convert, compress, save, cancel), core nouns (file, image, settings, privacy, account, booking), product feature names, and CTA phrasing. Prefer terms already dominant in the files or in the repo's glossary. Apply them consistently across every file. Brand and product names stay as they are unless the brand has an official localized name.

## Step 4: Edit

Edit files **in place with an available text-editing tool**, changing only the string values that need it. Do not regenerate whole files by re-serializing them, because that silently changes indentation, key order, escaping and Unicode handling, and produces noisy diffs. For very large files, work section by section.

### What to fix

- **Language accuracy**: grammar, spelling, punctuation, sentence structure, word choice, tense, articles, prepositions, gender and number agreement, case, and wrong or literal translations.
- **Native fluency**: rewrite anything robotic, word-for-word, repetitive, padded, over-formal or corporate. Vary sentence length and structure naturally. Remove AI-style filler ("In today's digital world…", "Whether you're X or Y…", "Look no further", "seamless", "unlock", "elevate", "effortlessly") and the target-language equivalents of these clichés. Never introduce deliberate errors to "sound human"; the aim is authentic, correct writing.
- **Localization**: replace literally translated idioms with real local expressions; use the market's terminology, date/number/currency conventions *in prose* (not in data values), and punctuation conventions (for example French non-breaking spaces before `: ; ? !`, German „…" quotes, Spanish ¿¡, Japanese full-width punctuation). Fix references that do not make sense in the market.
- **Safety and accuracy of claims**: soften or correct wording that misleads, overpromises ("100% secure", "guaranteed", "instant refund"), gives unsafe instructions, or makes overconfident medical, legal, financial or safety claims. Remove discriminatory or needlessly offensive wording. Do not invent facts or add claims that weren't there, unless needed to correct a clear factual or safety error, and flag any such change in the report.
- **SEO fields** (titles, meta descriptions, headings, keywords, FAQs): keep the search intent, phrase it the way native users actually search and read, and do not keyword-stuff. Keep titles and meta descriptions around their original length; if the original is near a typical limit (about 60 characters for titles, 155 for descriptions), stay near it.

### Priority when goals conflict

**Meaning → Accuracy → Native fluency → Localization → Clarity → Natural style → Conciseness**

If a string is already correct and natural, leave it alone. Do not rewrite for the sake of rewriting. Short UI labels should stay short because they must fit buttons and menus.

### What must never change

- Keys, nesting, key order, array order and length, and data types
- Numbers, booleans and `null`
- IDs, slugs, URLs, file paths, route paths, email addresses, colour codes, enum-like values (`"primary"`, `"image/png"`)
- Placeholders and template syntax: `{{name}}`, `{userName}`, `{count, plural, one {…} other {…}}` (translate only the text inside ICU branches, never the keywords or selectors), `%s`, `%d`, `%1$s`, `${var}`, `:param`, `$t(key)`, `@:key`
- HTML tags and attributes (`<strong>…</strong>`, `<a href="…">…</a>`, `<br/>`); the text between tags may be edited
- Markdown syntax (link URLs, `**`, `#`, list markers, code spans); the visible text may be edited
- Code snippets
- JSON escaping (`\"`, `\n`, `\\`, `é`); keep the file's existing style of escaping vs literal Unicode

Placeholders may move within a sentence when the target language's word order requires it, but every placeholder must still appear, with the same spelling and the same count. For i18n plural keys (`_one`, `_other`, `_few`, `_many`), fix the text in each form but do not add or remove keys; if the target language needs plural forms the file lacks, flag it rather than inventing keys.

### Values that look technical but are user-facing

Some fields hold visible text despite technical-looking keys (`alt`, `aria-label`, `placeholder`, `tooltip`, `label`, `og:title`). Review those. Conversely, a value in a text-like field that is clearly an identifier stays untouched. When unsure whether a value is shown to users, leave it and mention it in the report.

## Step 5: Validate

Run the validator against the snapshot:

```bash
python3 "$SKILL_DIR/scripts/validate_json_edits.py" "$ORIGINAL_PATH" "$TARGET_PATH"
```

It checks parsing and duplicate keys, keys and structure, array lengths and types, non-string values, technical-looking strings, and common placeholder, HTML tag, URL and Markdown link patterns. These are heuristic checks, not a full ICU, HTML, or Markdown parser. Manually inspect ICU selectors and branch structure, array and markup order, code snippets, JSON escaping, and all HTML attributes (some visible attributes can change without an error). Numeric representations such as `1` versus `1.0` may also compare equal; preserve them in the diff. A clean result does not establish language quality or prove every invariant. It also warns about lost trailing newlines or BOM changes. Fix every **ERROR** and review every **WARN** before finishing. Re-run until it reports no errors.

Then do a final read-through of the changed strings (the validator's `--show-changes` flag lists them) and check:

- **Language**: correct grammar and punctuation, native vocabulary, correct locale conventions
- **Content**: original meaning kept, no unnecessary rewrites, no misleading or harmful wording, suits the audience
- **Consistency**: glossary terms used the same way everywhere; similar strings follow the same conventions

## Step 6: Report

Keep the report short:

- Files reviewed, files changed, and number of strings changed
- The brief used (language/variant, register), especially anything you inferred
- Key glossary decisions (a small table of recurring terms, if useful)
- **Flagged for review**: file + JSON path + the reason, for anything where the meaning was genuinely unclear, a fact looked wrong, a safety or claims change was made, a plural form is missing, or a string looked too long for its UI slot. Do not guess a meaning for unclear content; flag it.

If a file needed no changes, say it was left unchanged.
