from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "conversation_archive.py"
SPEC = importlib.util.spec_from_file_location("conversation_archive_tested", SCRIPT)
assert SPEC and SPEC.loader
archive = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = archive
SPEC.loader.exec_module(archive)


def message(role: str, text: str, timestamp: float) -> dict:
    return {
        "author": {"role": role},
        "create_time": timestamp,
        "content": {"content_type": "text", "parts": [text]},
    }


def sample_conversation(identifier: str = "conversation-1") -> dict:
    return {
        "id": identifier,
        "title": "Archive test",
        "create_time": 1.0,
        "update_time": 4.0,
        "current_node": "trigger",
        "mapping": {
            "root": {
                "parent": None,
                "children": ["user"],
                "message": message("system", "system guidance", 1.0),
            },
            "user": {
                "parent": "root",
                "children": ["assistant"],
                "message": message("user", "hello", 2.0),
            },
            "assistant": {
                "parent": "user",
                "children": ["trigger"],
                "message": message("assistant", "hi", 3.0),
            },
            "trigger": {
                "parent": "assistant",
                "children": [],
                "message": message("user", "导入", 4.0),
            },
        },
    }


class ConversationArchiveTests(unittest.TestCase):
    def initialize_root(self, root: Path) -> None:
        index = archive.default_index()
        archive.atomic_write(
            root / archive.INDEX_PATH,
            json.dumps(index, ensure_ascii=False, indent=2) + "\n",
        )
        archive.atomic_write(root / archive.VIEW_PATH, archive.render_view(index))

    def importer_args(self, root: Path, source: Path, **overrides) -> argparse.Namespace:
        values = {
            "root": root,
            "source": source,
            "kind": "chatgpt-export",
            "surface": "chatgpt_text",
            "conversation_id": "conversation-1",
            "title": "",
            "latest": False,
            "all": False,
            "before_trigger": "导入",
            "lane": "research.kernel_aware_gemm",
            "audio": [],
        }
        values.update(overrides)
        return argparse.Namespace(**values)

    def test_chatgpt_export_excludes_trigger_and_preserves_source_messages(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.initialize_root(root)
            source = root / "conversations.json"
            source.write_text(
                json.dumps([sample_conversation()], ensure_ascii=False),
                encoding="utf-8",
            )
            self.assertEqual(archive.cmd_import(self.importer_args(root, source)), 0)
            index = archive.load_index(root)
            self.assertEqual(len(index["entries"]), 1)
            entry = index["entries"][0]
            self.assertEqual(entry["coverage"], "exact_export")
            self.assertEqual(entry["message_count"], 3)
            stored = json.loads((root / entry["path"]).read_text(encoding="utf-8"))
            self.assertTrue(stored["source"]["trigger_matched"])
            texts = [item["text"] for item in stored["payload"]["messages"]]
            self.assertEqual(texts, ["system guidance", "hello", "hi"])
            self.assertEqual(archive.validate_archive_files(root), [])

    def test_voice_transcript_can_include_explicit_audio_copy(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.initialize_root(root)
            source = root / "voice.md"
            source.write_text("user: hello\nassistant: hi\n", encoding="utf-8")
            audio = root / "voice.m4a"
            audio.write_bytes(b"fake-audio")
            args = self.importer_args(
                root,
                source,
                kind="transcript",
                surface="chatgpt_voice",
                conversation_id="",
                title="Voice window",
                audio=[audio],
            )
            self.assertEqual(archive.cmd_import(args), 0)
            entry = archive.load_index(root)["entries"][0]
            self.assertEqual(entry["coverage"], "provided_transcript")
            self.assertTrue(entry["raw_audio_archived"])
            self.assertEqual(archive.validate_archive_files(root), [])

    def test_visible_context_is_never_labeled_exact(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.initialize_root(root)
            source = root / "visible.md"
            source.write_text("best effort only\n", encoding="utf-8")
            args = self.importer_args(
                root,
                source,
                kind="visible-context",
                surface="chatgpt_text",
                conversation_id="",
                title="Visible context",
            )
            self.assertEqual(archive.cmd_import(args), 0)
            entry = archive.load_index(root)["entries"][0]
            self.assertEqual(entry["coverage"], "visible_context_only")

    def test_multi_conversation_export_requires_selection(self) -> None:
        conversations = [sample_conversation("one"), sample_conversation("two")]
        with self.assertRaises(ValueError):
            archive.select_conversations(conversations, "", "", False, False)


if __name__ == "__main__":
    unittest.main()
