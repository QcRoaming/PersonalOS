from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "experiment_registry.py"
SPEC = importlib.util.spec_from_file_location("experiment_registry", SCRIPT)
assert SPEC and SPEC.loader
registry = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(registry)


def minimal_registry() -> dict:
    return {
        "schema_version": 1,
        "registry_id": "personal.experiments",
        "workspace_root_hint": "/workspace",
        "generated_view": "EXPERIMENTS.md",
        "entries": [
            {
                "id": "test.experiment",
                "title": "Test Experiment",
                "chapter": "test",
                "category": "historical_experiment",
                "status": "archived",
                "paths": [{"role": "root", "path": "experiments/test"}],
                "artifact_index": "experiments/test/index.md",
                "evidence_files": ["experiments/test/result.json"],
                "reproduce_command": "python3 run.py",
                "claim_boundary": "Test-only evidence.",
                "automation": {"auto_refresh": True, "producer": "experiments/test/run.py"},
            }
        ],
    }


class ExperimentRegistryTests(unittest.TestCase):
    def test_rejects_duplicate_ids_and_unsafe_paths(self) -> None:
        data = minimal_registry()
        duplicate = json.loads(json.dumps(data["entries"][0]))
        duplicate["paths"][0]["path"] = "../outside"
        data["entries"].append(duplicate)
        errors = registry.validate_registry_data(data)
        self.assertTrue(any("duplicate experiment id" in error for error in errors))
        self.assertTrue(any("safe POSIX relative path" in error for error in errors))

    def test_refresh_records_metadata_hashes_and_success(self) -> None:
        with tempfile.TemporaryDirectory() as root_text, tempfile.TemporaryDirectory() as workspace_text:
            root = Path(root_text)
            workspace = Path(workspace_text)
            (root / "registries").mkdir()
            (workspace / "experiments/test").mkdir(parents=True)
            (workspace / "experiments/test/index.md").write_text("index\n", encoding="utf-8")
            (workspace / "experiments/test/result.json").write_text('{"ok": true}\n', encoding="utf-8")
            (workspace / "experiments/test/__pycache__").mkdir()
            (workspace / "experiments/test/__pycache__/run.pyc").write_bytes(b"cache")
            (root / "registries/experiments.json").write_text(
                json.dumps(minimal_registry()), encoding="utf-8"
            )

            data = registry.refresh_registry(root, workspace, "test.experiment")
            observed = data["entries"][0]["observed"]
            self.assertTrue(observed["all_paths_exist"])
            self.assertEqual(observed["file_count"], 2)
            self.assertGreater(observed["size_bytes"], 0)
            self.assertEqual(len(observed["tree_fingerprint_sha256"]), 64)
            self.assertEqual(len(observed["tracked_files"]["experiments/test/result.json"]["sha256"]), 64)
            self.assertIsNotNone(observed["last_successful_run_utc"])
            self.assertEqual(registry.validate_registry_files(root), [])

    def test_refresh_preserves_last_success_for_other_entries(self) -> None:
        with tempfile.TemporaryDirectory() as root_text, tempfile.TemporaryDirectory() as workspace_text:
            root = Path(root_text)
            workspace = Path(workspace_text)
            (root / "registries").mkdir()
            (workspace / "experiments/test").mkdir(parents=True)
            for name in ("index.md", "result.json"):
                (workspace / "experiments/test" / name).write_text(name, encoding="utf-8")
            data = minimal_registry()
            data["entries"][0]["observed"] = {"last_successful_run_utc": "2026-01-01T00:00:00Z"}
            (root / "registries/experiments.json").write_text(json.dumps(data), encoding="utf-8")

            refreshed = registry.refresh_registry(root, workspace, None)
            self.assertEqual(
                refreshed["entries"][0]["observed"]["last_successful_run_utc"],
                "2026-01-01T00:00:00Z",
            )

    def test_missing_scope_is_visible_but_not_a_schema_error(self) -> None:
        with tempfile.TemporaryDirectory() as root_text, tempfile.TemporaryDirectory() as workspace_text:
            root = Path(root_text)
            workspace = Path(workspace_text)
            (root / "registries").mkdir()
            (root / "registries/experiments.json").write_text(
                json.dumps(minimal_registry()), encoding="utf-8"
            )

            data = registry.refresh_registry(root, workspace, None)
            observed = data["entries"][0]["observed"]
            self.assertFalse(observed["all_paths_exist"])
            self.assertEqual(observed["file_count"], 0)
            self.assertEqual(registry.validate_registry_files(root), [])

    def test_multiple_completed_ids_are_supported(self) -> None:
        with tempfile.TemporaryDirectory() as root_text, tempfile.TemporaryDirectory() as workspace_text:
            root = Path(root_text)
            workspace = Path(workspace_text)
            (root / "registries").mkdir()
            data = minimal_registry()
            second = json.loads(json.dumps(data["entries"][0]))
            second["id"] = "test.second"
            second["paths"] = [{"role": "root", "path": "experiments/second"}]
            second["artifact_index"] = "experiments/second/index.md"
            second["evidence_files"] = []
            data["entries"].append(second)
            for name in ("test", "second"):
                path = workspace / "experiments" / name
                path.mkdir(parents=True)
                (path / "index.md").write_text("index", encoding="utf-8")
            (root / "registries/experiments.json").write_text(json.dumps(data), encoding="utf-8")

            refreshed = registry.refresh_registry(
                root, workspace, ["test.experiment", "test.second"]
            )
            self.assertTrue(
                all(item["observed"]["last_successful_run_utc"] for item in refreshed["entries"])
            )

    def test_refresh_syncs_paper_use_from_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as root_text, tempfile.TemporaryDirectory() as workspace_text:
            root = Path(root_text)
            workspace = Path(workspace_text)
            (root / "registries").mkdir()
            (workspace / "experiments/test").mkdir(parents=True)
            (workspace / "experiments/test/index.md").write_text("index\n", encoding="utf-8")
            selection_path = workspace / "experiments/paper_selection.json"
            selection_path.write_text(
                json.dumps({
                    "entries": [{
                        "id": "test.experiment",
                        "tier": "primary_main_text",
                        "body_eligible": True,
                        "recommended_sections": ["Chapter test"],
                        "decision": "Use as test evidence.",
                        "usable_claims": ["The synchronization works."],
                    }]
                }),
                encoding="utf-8",
            )
            data = minimal_registry()
            data["paper_selection_source"] = "experiments/paper_selection.json"
            (root / "registries/experiments.json").write_text(json.dumps(data), encoding="utf-8")

            refreshed = registry.refresh_registry(root, workspace, None)
            paper_use = refreshed["entries"][0]["paper_use"]
            self.assertEqual(paper_use["tier"], "primary_main_text")
            self.assertTrue(paper_use["body_eligible"])
            self.assertEqual(registry.validate_registry_files(root), [])


if __name__ == "__main__":
    unittest.main()
