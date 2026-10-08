"""Optional local discovery smoke; never starts a model or reads real credentials."""
import json
import os
from pathlib import Path
import shutil
import select
import subprocess
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
CODEX = shutil.which("codex")


@unittest.skipUnless(CODEX, "Codex CLI unavailable; local discovery smoke skipped")
class CodexDiscoveryTests(unittest.TestCase):
    def test_global_rules_and_skill_discovery(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary).resolve()
            home = directory / "home"
            home.mkdir()
            codex_home = home / "custom codex"
            environment = dict(os.environ, HOME=str(home), CODEX_HOME=str(codex_home))
            installed = subprocess.run(["bash", str(ROOT / "install.sh"), "--only", "codex"],
                                       env=environment, capture_output=True, text=True, timeout=30)
            self.assertEqual(installed.returncode, 0, installed.stderr)
            result = subprocess.run([CODEX, "debug", "prompt-input", "Local discovery smoke"],
                                    env=environment, cwd=directory, capture_output=True,
                                    text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            context = "\n".join(part.get("text", "") for item in json.loads(result.stdout)
                                for part in item.get("content", []))
            self.assertIn("Global Engineering Rules", context)
            self.assertIn("rest-api-design", context)
            self.assertNotIn("- new-feature:", context)
            server = subprocess.Popen([CODEX, "app-server", "--stdio"], env=environment,
                                      cwd=directory, stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            try:
                server.stdin.write(json.dumps({"id": 1, "method": "initialize", "params": {
                    "clientInfo": {"name": "agent-mesh-qa", "version": "1"},
                    "capabilities": {"experimentalApi": True}}}) + "\n")
                server.stdin.flush()
                self.read_response(server, 1)
                server.stdin.write(json.dumps({"method": "initialized"}) + "\n")
                server.stdin.write(json.dumps({"id": 2, "method": "skills/list", "params": {
                    "cwds": [str(directory)]}}) + "\n")
                server.stdin.flush()
                response = self.read_response(server, 2)
                catalog = {skill["name"]: skill for skill in response["result"]["data"][0]["skills"]}
                for workflow in (ROOT / "workflows").iterdir():
                    self.assertTrue(catalog[workflow.name]["enabled"])
                    self.assertEqual(Path(catalog[workflow.name]["path"]),
                                     home / ".agents/skills" / workflow.name / "SKILL.md")
            finally:
                server.terminate()
                server.communicate(timeout=5)

    def read_response(self, server, identifier):
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            if select.select([server.stdout], [], [], 0.5)[0]:
                line = server.stdout.readline()
                self.assertTrue(line, "App server closed before responding")
                response = json.loads(line)
                if response.get("id") == identifier:
                    self.assertNotIn("error", response)
                    return response
        self.fail("Local app-server response timed out")
