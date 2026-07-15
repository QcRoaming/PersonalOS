from __future__ import annotations

import importlib.util
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))
SPEC = importlib.util.spec_from_file_location("personal_os", SCRIPT_DIR / "personal_os.py")
assert SPEC and SPEC.loader
personal_os = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = personal_os
SPEC.loader.exec_module(personal_os)


class PersonalOSTests(unittest.TestCase):
    def copy_store(self, destination: Path) -> Path:
        target = destination / "PersonalOS"
        shutil.copytree(
            ROOT,
            target,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".personal-os.lock"),
        )
        return target

    def test_continue_main_routes_to_declared_main_lane(self) -> None:
        lane, hits = personal_os.select_lane(ROOT, query="继续主线")
        self.assertIsNotNone(lane)
        self.assertEqual(lane.meta["id"], "research.kernel_aware_gemm")
        self.assertEqual(hits, ["main_lane"])

    def test_generated_views_are_deterministic_and_current(self) -> None:
        first = personal_os.generated_view_texts(ROOT)
        second = personal_os.generated_view_texts(ROOT)
        self.assertEqual(first, second)
        for name, content in first.items():
            self.assertEqual((ROOT / name).read_text(encoding="utf-8"), content)

    def test_checkpoint_bumps_one_lane_and_rebuilds_views(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self.copy_store(Path(temporary))
            lane, _ = personal_os.select_lane(root, lane_id="skills.mcp")
            assert lane
            version = int(lane.meta["version"])
            result = personal_os.cmd_checkpoint(
                root,
                "skills.mcp",
                "Checkpoint test",
                ["Run tests"],
                ["Push state"],
                ["Unit test passed"],
                ["repo@commit:path"],
                ["多机同步|applied|checkpoint test|second-device test"],
                version,
            )
            self.assertEqual(result, 0)
            updated, _ = personal_os.parse_frontmatter(lane.path)
            self.assertEqual(int(updated["version"]), version + 1)
            self.assertEqual(personal_os.cmd_check(root), 0)

    def test_install_is_idempotent_and_preserves_other_global_guidance(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            codex_home = home / ".codex"
            codex_home.mkdir()
            agents = codex_home / "AGENTS.md"
            agents.write_text("# Existing guidance\n", encoding="utf-8")
            with patch.dict(os.environ, {"CODEX_HOME": str(codex_home)}):
                self.assertEqual(personal_os.cmd_install(ROOT, home), 0)
                self.assertEqual(personal_os.cmd_install(ROOT, home), 0)
            content = agents.read_text(encoding="utf-8")
            self.assertIn("# Existing guidance", content)
            self.assertEqual(content.count(personal_os.MANAGED_BEGIN), 1)
            self.assertTrue(
                (home / ".agents/skills/personal-os/SKILL.md").is_file()
            )


if __name__ == "__main__":
    unittest.main()
