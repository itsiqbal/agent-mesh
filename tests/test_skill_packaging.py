"""Packaging excludes local interpreter artifacts without dropping source helpers."""
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('kit_installer', ROOT/'scripts/codex_install.py')
INSTALLER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INSTALLER)


class SkillPackagingTests(unittest.TestCase):
    def test_all_targets_copy_helpers_and_exclude_generated_artifacts(self):
        with tempfile.TemporaryDirectory(prefix='kit packaging ') as temporary:
            root = Path(temporary).resolve()
            kit, stage, home = root/'kit', root/'stage', root/'home'
            skill = kit/'skills/json-localization-editor'
            shutil.copytree(ROOT/'skills/json-localization-editor', skill)
            artifacts = [skill/'.DS_Store', skill/'scripts/helper.pyc',
                         skill/'scripts/helper.pyo',
                         skill/'scripts/__pycache__/helper.cpython-312.pyc',
                         skill/'scripts/__pycache__/extra.txt']
            for artifact in artifacts:
                artifact.parent.mkdir(parents=True, exist_ok=True)
                artifact.write_bytes(b'local artifact')
            (stage/'agents').mkdir(parents=True)
            (stage/'workflows').mkdir()
            for tool in sorted(INSTALLER.TOOLS):
                with self.subTest(tool=tool), patch.object(INSTALLER, 'KIT', kit):
                    _, _, destinations = INSTALLER.locations(tool, home, home/'.codex')
                    planned = INSTALLER.files(tool, stage, destinations)
                    for target, content in planned.items():
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(content)
                    skill_destinations = destinations[1:3] if tool == 'antigravity' else destinations[1:2]
                    for destination in skill_destinations:
                        installed = destination/'json-localization-editor'
                        self.assertTrue((installed/'SKILL.md').is_file())
                        for helper in ['_common.py', 'extract_strings.py', 'validate_json_edits.py']:
                            self.assertEqual((installed/'scripts'/helper).read_bytes(), (skill/'scripts'/helper).read_bytes())
                        for artifact in artifacts:
                            self.assertFalse((installed/artifact.relative_to(skill)).exists())


if __name__ == '__main__':
    unittest.main()
