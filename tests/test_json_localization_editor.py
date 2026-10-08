"""Localization helper tests use disposable JSON snapshots only."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "skills/json-localization-editor/scripts"


class LocalizationEditorTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.original = self.root / "original.json"
        self.edited = self.root / "edited.json"

    def run_helper(self, name, *args):
        return subprocess.run([sys.executable, str(SCRIPTS / name), *map(str, args)], text=True, capture_output=True)

    def write_pair(self, original, edited):
        self.original.write_text(json.dumps(original, ensure_ascii=False) + "\n")
        self.edited.write_text(json.dumps(edited, ensure_ascii=False) + "\n")

    def validate(self):
        return self.run_helper("validate_json_edits.py", self.original, self.edited, "--show-changes")

    def test_safe_string_edits_preserve_technical_and_markup_values(self):
        original = {
            "title": "Hello {{name}}, use <strong>Save</strong> or [help](https://example.com/help).",
            "details": "Read `user.name` and save %1$s to ${folder}.",
            "path": "/assets/image.png", "url": "https://example.com", "count": 3, "enabled": True,
            "items": ["First item", "Second item"], "missing": None,
        }
        edited = {**original, "title": "Bonjour {{name}}, utilisez <strong>Enregistrer</strong> ou [aide](https://example.com/help)."}
        self.write_pair(original, edited)
        result = self.validate()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Strings changed: 1", result.stdout)

    def test_structural_and_nonstring_changes_fail(self):
        original = {"title": "Hello friend", "items": ["First item"], "count": 3, "enabled": True}
        cases = [
            {k: v for k, v in original.items() if k != "title"},
            {**original, "items": []}, {**original, "title": 1},
            {**original, "count": 4}, {**original, "enabled": False},
        ]
        for edited in cases:
            with self.subTest(edited=edited):
                self.write_pair(original, edited)
                self.assertEqual(self.validate().returncode, 1)

    def test_placeholders_html_links_and_technical_paths_fail(self):
        cases = [
            ("Hello {{name}}", "Bonjour {{user}}"),
            ("Hello %1$s %1$s", "Bonjour %1$s"),
            ('Read <a href="/help">help</a>', 'Lire <a href="/other">aide</a>'),
            ("Read [help](https://example.com/help)", "Lire [aide](https://example.com/other)"),
            ("/assets/image.png", "/assets/other.png"),
        ]
        for old, new in cases:
            with self.subTest(old=old):
                self.write_pair({"text": old}, {"text": new})
                self.assertEqual(self.validate().returncode, 1)

    def test_invalid_json_and_duplicate_keys_fail(self):
        self.original.write_text('{"title":"Hello friend"}')
        for text in ('{"title":', '{"title":"Bonjour","title":"Salut"}'):
            with self.subTest(text=text):
                self.edited.write_text(text)
                self.assertEqual(self.validate().returncode, 1)
                self.assertEqual(self.run_helper("extract_strings.py", self.edited).returncode, 1)
        self.edited.write_text('{"title":"Bonjour ami"}')
        for text in ('{"title":', '{"title":"Hello","title":"Hi"}'):
            with self.subTest(original=text):
                self.original.write_text(text)
                self.assertEqual(self.validate().returncode, 1)

    def test_missing_empty_and_mismatched_inputs_fail(self):
        empty = self.root / "empty"
        empty.mkdir()
        missing = self.root / "missing"
        self.write_pair({"title": "Hello friend"}, {"title": "Bonjour ami"})
        for path in (empty, missing):
            with self.subTest(path=path):
                self.assertEqual(self.run_helper("extract_strings.py", path).returncode, 1)
                self.assertEqual(self.run_helper("validate_json_edits.py", path, empty).returncode, 1)
        self.assertEqual(self.run_helper("validate_json_edits.py", self.original, empty).returncode, 1)
        non_json = self.root / "config.yaml"
        non_json.write_text("title: Hello")
        self.assertEqual(self.run_helper("extract_strings.py", non_json).returncode, 1)

    def test_nonstandard_json_constants_fail_in_original_and_edited_files(self):
        valid = '{"title":"Hello friend","count":3}'
        for constant in ("NaN", "Infinity", "-Infinity"):
            invalid = '{"title":"Hello friend","count":' + constant + '}'
            with self.subTest(constant=constant):
                self.original.write_text(valid)
                self.edited.write_text(invalid)
                self.assertEqual(self.validate().returncode, 1)
                self.assertEqual(self.run_helper("extract_strings.py", self.edited).returncode, 1)
                self.original.write_text(invalid)
                self.edited.write_text(valid)
                self.assertEqual(self.validate().returncode, 1)
                self.assertEqual(self.run_helper("extract_strings.py", self.original).returncode, 1)

    def test_extraction_lists_visible_strings_and_skips_technical_values(self):
        self.original.write_text(json.dumps({"title": "Hello friend", "url": "https://example.com", "label": "Save"}))
        result = self.run_helper("extract_strings.py", self.original, "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        entries = json.loads(result.stdout)["files"][0]["strings"]
        self.assertEqual([entry["path"] for entry in entries], ["$.title", "$.label"])
        all_result = self.run_helper("extract_strings.py", self.original, "--all", "--json")
        self.assertEqual(len(json.loads(all_result.stdout)["files"][0]["strings"]), 3)


if __name__ == "__main__":
    unittest.main()
