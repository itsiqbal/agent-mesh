"""Independent locale editing and installed helper QA; isolated fixtures only."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/json-localization-editor"


class LocalizationQATests(unittest.TestCase):
    def test_en_us_edit_retains_application_contract(self):
        # Raw product copy, no expected-edit hints embedded in the fixture.
        raw = '''{
  "welcome": "Hello {{name}}, your files is ready.",
  "help": "For helps, read [our guide](https://example.com/help).",
  "notice": "<strong>Careful</strong>: this action remove {count} files.",
  "steps": ["Choose the file you wants.", "Upload your file."],
  "route": "/uploads/new",
  "slug": "upload-file",
  "theme": "#123456",
  "mime": "image/png",
  "limit": 12,
  "enabled": true,
  "next": null
}
'''
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            snapshot, edited = directory / "original.json", directory / "en-US.json"
            snapshot.write_text(raw)
            edited.write_text(raw)
            extracted = subprocess.run([sys.executable, str(SKILL / "scripts/extract_strings.py"),
                                        str(edited), "--json"], capture_output=True, text=True, timeout=10)
            self.assertEqual(extracted.returncode, 0, extracted.stderr)
            entries = json.loads(extracted.stdout)["files"][0]["strings"]
            self.assertEqual({entry["path"] for entry in entries},
                             {"$.welcome", "$.help", "$.notice", "$.steps[0]", "$.steps[1]"})
            polished = raw.replace("your files is ready.", "your files are ready.")
            polished = polished.replace("For helps, read", "For help, read")
            polished = polished.replace("this action remove", "this action removes")
            polished = polished.replace("you wants.", "you want.")
            edited.write_text(polished)
            result = subprocess.run([sys.executable, str(SKILL / "scripts/validate_json_edits.py"),
                                     str(snapshot), str(edited), "--show-changes"],
                                    capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Strings changed: 4", result.stdout)
            self.assertIn("Errors: 0  Warnings: 0", result.stdout)
            old, new = json.loads(raw), json.loads(polished)
            self.assertEqual(list(old), list(new))
            for key in ("route", "slug", "theme", "mime", "limit", "enabled", "next"):
                self.assertEqual(old[key], new[key])
                self.assertIs(type(old[key]), type(new[key]))
            self.assertEqual(snapshot.read_text(), raw)

    def test_each_target_installs_executable_helpers(self):
        for target, relative in (("claude", ".claude/skills"),
                                 ("antigravity", ".gemini/antigravity/skills"),
                                 ("opencode", ".config/opencode/skills"),
                                 ("codex", ".agents/skills")):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as temporary:
                home = Path(temporary).resolve() / "home"
                home.mkdir()
                environment = dict(os.environ, HOME=str(home), CODEX_HOME=str(home / "codex home"))
                install = subprocess.run(["bash", str(ROOT / "install.sh"), "--only", target],
                                         env=environment, capture_output=True, text=True, timeout=30)
                self.assertEqual(install.returncode, 0, install.stderr)
                installed = home / relative / SKILL.name
                self.assertEqual({str(p.relative_to(installed)) for p in installed.rglob("*") if p.is_file()},
                                 {"SKILL.md", "scripts/_common.py", "scripts/extract_strings.py",
                                  "scripts/validate_json_edits.py"})
                locale = home / "en-US.json"
                locale.write_text('{"message":"Upload your file."}\n')
                for helper, args in (("extract_strings.py", [str(locale), "--json"]),
                                     ("validate_json_edits.py", [str(locale), str(locale)])):
                    result = subprocess.run([sys.executable, str(installed / "scripts" / helper), *args],
                                            capture_output=True, text=True, timeout=10)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
