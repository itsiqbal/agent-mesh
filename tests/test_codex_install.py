"""Installer integration tests isolate every destination in disposable homes."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='kit home ')
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name).resolve()
        self.env = {**os.environ, 'HOME':str(self.home), 'CODEX_HOME':str(self.home/'custom codex')}
        self.codex = Path(self.env['CODEX_HOME'])

    def run_script(self, operation='install', *options, success=True):
        result = subprocess.run(['bash',str(ROOT/f'{operation}.sh'),'--only','codex',*options],env=self.env,text=True,capture_output=True)
        self.assertEqual(result.returncode == 0,success,result.stdout+result.stderr)
        return result

    def snapshot(self):
        return {str(p.relative_to(self.home)):p.read_bytes() for p in self.home.rglob('*') if p.is_file()}

    def test_repeat_and_uninstall_preserve_unrelated_content(self):
        self.codex.mkdir()
        rules = self.codex/'AGENTS.md'
        rules.write_text('My rules\n')
        self.run_script()
        before = self.snapshot()
        self.run_script()
        self.assertEqual(before,self.snapshot())
        (self.home/'.agents/skills/rest-api-design/user-note.txt').write_text('Keep me')
        self.run_script('uninstall')
        self.assertEqual(rules.read_text(),'My rules\n')
        self.assertEqual((self.home/'.agents/skills/rest-api-design/user-note.txt').read_text(),'Keep me')
        self.assertFalse((self.codex/'.ai-agent-kit-manifest.json').exists())

    def test_rules_without_final_newline_preserved(self):
        self.codex.mkdir()
        rules = self.codex/'AGENTS.md'
        rules.write_bytes(b'Original rules without newline')
        self.run_script()
        self.run_script('uninstall')
        self.assertEqual(rules.read_bytes(),b'Original rules without newline')

    def test_dry_run_has_no_mutations(self):
        self.run_script('install','--dry-run')
        self.assertEqual(self.snapshot(),{})
        self.run_script()
        before = self.snapshot()
        self.run_script('uninstall','--dry-run')
        self.assertEqual(self.snapshot(),before)

    def test_collision_preflight(self):
        destination = self.home/'.agents/skills/rest-api-design/SKILL.md'
        destination.parent.mkdir(parents=True)
        destination.write_text('Personal skill')
        before = self.snapshot()
        self.run_script(success=False)
        self.assertEqual(self.snapshot(),before)

    def test_modified_owned_file_and_rules(self):
        self.run_script()
        agent = self.codex/'agents/architect.toml'
        agent.write_text('My edited agent')
        rules = self.codex/'AGENTS.md'
        rules.write_text(rules.read_text().replace('Global Engineering Rules','Edited Engineering Rules'))
        before = self.snapshot()
        self.run_script(success=False)
        self.assertEqual(self.snapshot(),before)
        self.run_script('uninstall')
        self.assertEqual(agent.read_text(),'My edited agent')
        self.assertIn('Edited Engineering Rules',rules.read_text())
        manifest = json.loads((self.codex/'.ai-agent-kit-manifest.json').read_text())
        self.assertEqual(list(manifest['files']),[str(agent)])

    def test_symlink_rejected(self):
        actual = self.home/'actual'
        actual.mkdir()
        self.codex.symlink_to(actual,target_is_directory=True)
        self.run_script(success=False)
        self.assertEqual(list(actual.iterdir()),[])

    def test_invalid_manifest_traversal_and_markers(self):
        self.codex.mkdir()
        manifest = self.codex/'.ai-agent-kit-manifest.json'
        manifest.write_text(json.dumps({'version':1,'files':{str(self.codex/'agents/../outside'):'0'*64},'rules_hash':None}))
        self.run_script(success=False)
        manifest.unlink()
        (self.codex/'AGENTS.md').write_text('<!-- BEGIN ai-agent-kit -->\nmissing end')
        before = self.snapshot()
        self.run_script(success=False)
        self.assertEqual(before,self.snapshot())

    def test_invalid_targets(self):
        for options in [('--only',''),('--only','unknown'),('--only',)]:
            self.run_script('install',*options,success=False)
        self.assertEqual(self.snapshot(),{})

    def test_legacy_combined_and_default_targets(self):
        result = subprocess.run(['bash',str(ROOT/'install.sh')],env=self.env,text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)
        for relative in ['.claude/agents/architect.md','.gemini/config/agents/architect.md','.config/opencode/agents/architect.md']:
            self.assertTrue((self.home/relative).is_file())
        self.assertFalse(self.codex.exists())
        self.run_script('install','--only','codex,claude')
        self.assertTrue((self.codex/'agents/architect.toml').exists())

    def test_stale_owned_artifact_cleaned(self):
        self.run_script()
        stale = self.codex/'agents/old-role.toml'
        stale.write_text('Old role')
        manifest = self.codex/'.ai-agent-kit-manifest.json'
        value = json.loads(manifest.read_text())
        import hashlib
        value['files'][str(stale)] = hashlib.sha256(stale.read_bytes()).hexdigest()
        manifest.write_text(json.dumps(value))
        self.run_script()
        self.assertFalse(stale.exists())


if __name__ == '__main__':
    unittest.main()
