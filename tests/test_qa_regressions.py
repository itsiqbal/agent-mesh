"""Observable installer safety checks using isolated homes only."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SafetyRegressionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name).resolve() / "home with spaces"
        self.home.mkdir()
        self.codex = self.home / "custom codex"
        self.environment = dict(os.environ, HOME=str(self.home), CODEX_HOME=str(self.codex))

    def run_script(self, script, *arguments):
        return subprocess.run(["bash", str(ROOT / script), *arguments], env=self.environment,
                              capture_output=True, text=True, timeout=30)

    def snapshot(self):
        return {str(p.relative_to(self.home)): p.read_bytes()
                for p in self.home.rglob("*") if p.is_file()}

    def test_all_targets_preflight_before_any_mutation(self):
        collision = self.home / ".agents/skills/rest-api-design/SKILL.md"
        collision.parent.mkdir(parents=True)
        collision.write_text("user-owned skill")
        before = self.snapshot()
        result = self.run_script("install.sh", "--only", "claude,antigravity,opencode,codex")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("collision", result.stderr.lower())
        self.assertEqual(self.snapshot(), before)

    def test_uninstall_preserves_user_additions_inside_owned_skill(self):
        installed = self.run_script("install.sh", "--only", "codex")
        self.assertEqual(installed.returncode, 0, installed.stderr)
        extra = self.home / ".agents/skills/rest-api-design/user-notes.md"
        extra.write_text("keep my notes")
        result = self.run_script("uninstall.sh", "--only", "codex")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(extra.read_text(), "keep my notes")
        self.assertFalse((extra.parent / "SKILL.md").exists())

    def test_duplicate_rules_markers_abort_without_mutation(self):
        self.codex.mkdir()
        rules = self.codex / "AGENTS.md"
        rules.write_text("user rule\n<!-- BEGIN ai-agent-kit -->\n<!-- BEGIN ai-agent-kit -->\n")
        before = self.snapshot()
        result = self.run_script("install.sh", "--only", "codex")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("markers", result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_dry_runs_leave_home_byte_identical(self):
        before = self.snapshot()
        for script in ("install.sh", "uninstall.sh"):
            result = self.run_script(script, "--only", "codex", "--dry-run")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(self.snapshot(), before)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_overlapping_selected_roots_abort_before_mutation(self):
        self.environment["CODEX_HOME"] = str(self.home / ".claude")
        before = self.snapshot()
        result = self.run_script("install.sh", "--only", "claude,codex")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.snapshot(), before)

    def test_inline_rules_markers_abort_preserving_surrounding_text(self):
        self.codex.mkdir()
        rules = self.codex / "AGENTS.md"
        rules.write_text("<!-- BEGIN ai-agent-kit -->user text\n<!-- END ai-agent-kit -->\n")
        before = self.snapshot()
        result = self.run_script("install.sh", "--only", "codex")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.snapshot(), before)

    def test_default_codex_home_and_existing_config_preserved(self):
        self.environment.pop("CODEX_HOME")
        default = self.home / ".codex"
        default.mkdir()
        config = default / "config.toml"
        original = b'# my configuration\nmodel = "user-selected"\n'
        config.write_bytes(original)
        result = self.run_script("install.sh", "--only", "codex")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(list((default / "agents").glob("*.toml"))), 14)
        expected_skills = {path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md")}
        expected_skills.update(path.parent.name for path in (ROOT / "workflows").glob("*/BODY.md"))
        installed_skills = {path.parent.name for path in (self.home / ".agents/skills").glob("*/SKILL.md")}
        self.assertEqual(installed_skills, expected_skills)
        self.assertEqual(config.read_bytes(), original)
        result = self.run_script("uninstall.sh", "--only", "codex")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(config.read_bytes(), original)
