"""Generator acceptance tests; all writes use isolated temporary repositories."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("build_kit", ROOT / "scripts/build_kit.py")
BUILD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD)


class GeneratorTests(unittest.TestCase):
    def test_all_agents_and_workflows_are_valid_and_deterministic(self):
        outputs = BUILD.render(ROOT)
        self.assertEqual(outputs, BUILD.render(ROOT))
        agents = {p: value for p, value in outputs.items() if p.suffix == ".toml"}
        self.assertEqual(len(agents), 14)
        for relative, value in agents.items():
            agent = tomllib.loads(value)
            source = ROOT / relative.parent
            metadata = json.loads((source / "metadata.json").read_text())
            self.assertEqual(agent["name"], source.name)
            self.assertEqual(agent["description"], (source / "DESCRIPTION.txt").read_text().strip())
            self.assertIn(BUILD.codex_text((source / "PROMPT.md").read_text(), [p.parent.name for p in (ROOT / "workflows").glob("*/BODY.md")]), agent["developer_instructions"])
            self.assertNotIn("model", agent)
            self.assertEqual(agent.get("sandbox_mode") == "read-only", metadata["read_only"])
            for skill in metadata["skills"]:
                self.assertTrue((ROOT / "skills" / skill / "SKILL.md").is_file())
                self.assertIn(f"`{skill}`", agent["developer_instructions"])
        skills = {p: value for p, value in outputs.items() if p.name == "SKILL.md"}
        self.assertEqual(len(skills), 6)
        for path, value in skills.items():
            name = path.parts[1]
            self.assertIn(f"# ${name}", value)
            self.assertIn("allow_implicit_invocation: false", outputs[path.parent / "agents/openai.yaml"])
        for path, value in outputs.items():
            self.assertEqual((ROOT / path).read_text(), value, str(path))

    def test_toml_roundtrips_quotes_backslashes_unicode_and_multiline(self):
        samples = ['a "quoted" value', r"C:\path\file", "first\nsecond\tline", "中文", "control \b\f\r", "triple \"\"\""]
        for value in samples:
            self.assertEqual(tomllib.loads("value = " + BUILD.quoted(value))["value"], value)

    def test_legacy_templates_follow_shared_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(ROOT / "agents", root / "agents")
            shutil.copytree(ROOT / "workflows", root / "workflows")
            prompt = root / "agents/architect/PROMPT.md"
            prompt.write_text(prompt.read_text() + "\nAdditional shared instruction.\n")
            outputs = BUILD.render(root)
            for tool in ("claude-code", "opencode", "antigravity"):
                self.assertIn("Additional shared instruction.", outputs[Path(f"agents/architect/{tool}.md")])
            self.assertIn("Additional shared instruction.", tomllib.loads(outputs[Path("agents/architect/codex.toml")])["developer_instructions"])

    def test_staging_and_check_report_drift_without_writing(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "source"
            root.mkdir()
            shutil.copytree(ROOT / "agents", root / "agents")
            shutil.copytree(ROOT / "workflows", root / "workflows")
            command = [sys.executable, str(ROOT / "scripts/build_kit.py"), "--root", str(root)]
            self.assertEqual(subprocess.run(command + ["--check"], capture_output=True).returncode, 0)
            target = root / "agents/architect/codex.toml"
            target.write_text("user change\n")
            checked = subprocess.run(command + ["--check"], capture_output=True, text=True)
            self.assertEqual(checked.returncode, 1)
            self.assertIn("agents/architect/codex.toml", checked.stderr)
            self.assertEqual(target.read_text(), "user change\n")
            staging = Path(temporary) / "staging"
            self.assertEqual(subprocess.run(command + ["--output-dir", str(staging)], capture_output=True).returncode, 0)
            self.assertEqual((staging / "agents/architect/codex.toml").read_text(), BUILD.render(root)[Path("agents/architect/codex.toml")])
            self.assertEqual(target.read_text(), "user change\n")


if __name__ == "__main__":
    unittest.main()
