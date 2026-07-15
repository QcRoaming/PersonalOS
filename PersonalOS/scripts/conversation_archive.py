#!/usr/bin/env python3
"""Import exact conversation exports or provided transcripts into an isolated archive."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
INDEX_PATH = Path("archives/conversations/index.json")
VIEW_PATH = Path("ARCHIVES.md")
ARCHIVE_DIR = Path("archives/conversations/items")
MEDIA_DIR = Path("archives/conversations/media")
SURFACES = {
    "chatgpt_text",
    "chatgpt_voice",
    "codex_cli",
    "codex_ide",
    "other",
}
COVERAGE_LEVELS = {
    "exact_export",
    "provided_transcript",
    "visible_context_only",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(text)
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_name(value: str, fallback: str = "conversation") -> str:
    normalized = re.sub(r"[^\w.-]+", "-", value.strip(), flags=re.UNICODE).strip("-._")
    return normalized[:80] or fallback


def content_text(message: dict[str, Any]) -> str:
    content = message.get("content", {})
    if isinstance(content, str):
        return content
    if not isinstance(content, dict):
        return json.dumps(content, ensure_ascii=False)
    parts = content.get("parts", [])
    if not isinstance(parts, list):
        parts = [parts]
    rendered: list[str] = []
    for part in parts:
        if isinstance(part, str):
            rendered.append(part)
        elif isinstance(part, dict):
            if isinstance(part.get("text"), str):
                rendered.append(part["text"])
            elif isinstance(part.get("content"), str):
                rendered.append(part["content"])
            else:
                rendered.append(json.dumps(part, ensure_ascii=False, sort_keys=True))
        else:
            rendered.append(json.dumps(part, ensure_ascii=False))
    return "\n".join(rendered)


def chatgpt_active_messages(conversation: dict[str, Any]) -> list[dict[str, Any]]:
    mapping = conversation.get("mapping", {})
    if not isinstance(mapping, dict):
        return []
    current = conversation.get("current_node")
    node_ids: list[str] = []
    visited: set[str] = set()
    while current and current in mapping and current not in visited:
        visited.add(current)
        node_ids.append(current)
        current = mapping[current].get("parent")
    if node_ids:
        node_ids.reverse()
        messages = [mapping[node].get("message") for node in node_ids]
    else:
        messages = [node.get("message") for node in mapping.values()]
        messages.sort(
            key=lambda message: (
                message or {}
            ).get("create_time") or 0
        )
    return [message for message in messages if isinstance(message, dict)]


def trim_before_trigger(
    messages: list[dict[str, Any]], trigger: str
) -> tuple[list[dict[str, Any]], bool]:
    cutoff: int | None = None
    for index, message in enumerate(messages):
        role = (message.get("author") or {}).get("role")
        if role == "user" and content_text(message).strip() == trigger:
            cutoff = index
    if cutoff is None:
        return messages, False
    return messages[:cutoff], True


def normalize_chatgpt_conversation(
    conversation: dict[str, Any], trigger: str
) -> tuple[dict[str, Any], bool]:
    messages, matched = trim_before_trigger(chatgpt_active_messages(conversation), trigger)
    normalized = []
    for index, message in enumerate(messages):
        normalized.append(
            {
                "sequence": index,
                "role": (message.get("author") or {}).get("role", "unknown"),
                "author": message.get("author"),
                "created_at": message.get("create_time"),
                "updated_at": message.get("update_time"),
                "content_type": (message.get("content") or {}).get("content_type")
                if isinstance(message.get("content"), dict)
                else "text",
                "text": content_text(message),
                "source_message": message,
            }
        )
    payload = {
        "conversation_id": conversation.get("id") or conversation.get("conversation_id"),
        "title": conversation.get("title") or "Untitled conversation",
        "created_at": conversation.get("create_time"),
        "updated_at": conversation.get("update_time"),
        "messages": normalized,
    }
    return payload, matched


def load_chatgpt_export(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        conversations = data
    elif isinstance(data, dict) and isinstance(data.get("conversations"), list):
        conversations = data["conversations"]
    elif isinstance(data, dict) and "mapping" in data:
        conversations = [data]
    else:
        raise ValueError("JSON is not a recognized ChatGPT conversation export")
    return [item for item in conversations if isinstance(item, dict)]


def select_conversations(
    conversations: list[dict[str, Any]],
    conversation_id: str,
    title: str,
    latest: bool,
    import_all: bool,
) -> list[dict[str, Any]]:
    if import_all:
        return conversations
    selected = conversations
    if conversation_id:
        selected = [
            item
            for item in selected
            if str(item.get("id") or item.get("conversation_id") or "") == conversation_id
        ]
    if title:
        selected = [item for item in selected if str(item.get("title") or "") == title]
    if latest:
        return [
            max(
                selected,
                key=lambda item: item.get("update_time") or item.get("create_time") or 0,
            )
        ] if selected else []
    if not conversation_id and not title:
        if len(selected) == 1:
            return selected
        raise ValueError(
            "export contains multiple conversations; pass --conversation-id, --title, --latest, or --all"
        )
    if len(selected) > 1:
        raise ValueError("selection is ambiguous; use --conversation-id")
    return selected


def provided_transcript(path: Path, title: str) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = None
    if isinstance(data, dict) and isinstance(data.get("messages"), list):
        messages = data["messages"]
        conversation_id = data.get("id") or data.get("conversation_id")
        resolved_title = title or data.get("title") or path.stem
    else:
        messages = [{"sequence": 0, "role": "transcript", "text": raw}]
        conversation_id = None
        resolved_title = title or path.stem
    return {
        "conversation_id": conversation_id,
        "title": resolved_title,
        "created_at": None,
        "updated_at": None,
        "messages": messages,
        "raw_transcript": raw,
    }


def default_index() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "registry_id": "personal.conversation_archives",
        "entries": [],
    }


def load_index(root: Path) -> dict[str, Any]:
    path = root / INDEX_PATH
    if not path.is_file():
        return default_index()
    return json.loads(path.read_text(encoding="utf-8"))


def archive_media(
    root: Path, archive_id: str, audio_paths: list[Path]
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for source in audio_paths:
        source = source.expanduser().resolve()
        if not source.is_file():
            raise ValueError(f"audio file does not exist: {source}")
        digest = sha256_file(source)
        target_name = f"{digest[:12]}-{safe_name(source.name, 'audio')}"
        target = root / MEDIA_DIR / archive_id / target_name
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.is_file():
            shutil.copy2(source, target)
        records.append(
            {
                "path": target.relative_to(root).as_posix(),
                "sha256": digest,
                "size_bytes": source.stat().st_size,
                "source_name": source.name,
            }
        )
    return records


def build_archive(
    source_path: Path,
    payload: dict[str, Any],
    surface: str,
    coverage: str,
    trigger: str,
    trigger_matched: bool,
    lane: str,
    audio_records: list[dict[str, Any]],
) -> dict[str, Any]:
    payload_hash = sha256_bytes(canonical_bytes(payload))
    identity = payload.get("conversation_id") or payload.get("title") or source_path.name
    archive_id = sha256_bytes(f"{identity}:{payload_hash}".encode("utf-8"))[:20]
    return {
        "schema_version": SCHEMA_VERSION,
        "archive_id": archive_id,
        "imported_at": utc_now(),
        "lane": lane or None,
        "source": {
            "surface": surface,
            "coverage": coverage,
            "file_name": source_path.name,
            "file_sha256": sha256_file(source_path),
            "trigger": trigger,
            "trigger_matched": trigger_matched,
        },
        "voice": {
            "is_voice_conversation": surface == "chatgpt_voice",
            "transcript_archived": True,
            "raw_audio_archived": bool(audio_records),
            "audio_files": audio_records,
        },
        "payload": payload,
        "integrity": {
            "payload_sha256": payload_hash,
        },
    }


def render_view(index: dict[str, Any]) -> str:
    code = chr(96)
    entries = sorted(
        index.get("entries", []),
        key=lambda item: item.get("imported_at", ""),
        reverse=True,
    )
    lines = [
        "# Conversation Archives",
        "",
        "> Generated index. Raw archives are opt-in and isolated from PersonalOS Lane state.",
        "",
        f"- Archive count: {len(entries)}",
        f"- Last import: {entries[0].get('imported_at') if entries else 'never'}",
        "",
        "| Imported | Title | Surface | Coverage | Messages | Voice/audio | Lane | Archive |",
        "|---|---|---|---|---:|---|---|---|",
    ]
    for entry in entries:
        voice = "transcript"
        if entry.get("raw_audio_archived"):
            voice = "transcript + audio"
        elif not entry.get("is_voice_conversation"):
            voice = "—"
        lines.append(
            "| {imported} | {title} | {surface} | {coverage} | {count} | {voice} | {lane} | {code}{path}{code} |".format(
                imported=entry.get("imported_at", "unknown"),
                title=str(entry.get("title", "Untitled")).replace("|", "/"),
                surface=entry.get("surface", "unknown"),
                coverage=entry.get("coverage", "unknown"),
                count=entry.get("message_count", 0),
                voice=voice,
                lane=entry.get("lane") or "—",
                code=code,
                path=entry.get("path", "missing"),
            )
        )
    lines.extend(
        [
            "",
            "Coverage meanings:",
            "",
            "- exact_export: selected conversation imported from an account data export.",
            "- provided_transcript: exact bytes of a user-provided transcript were preserved.",
            "- visible_context_only: incomplete best-effort context; never call it a full backup.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def save_archive(root: Path, archive: dict[str, Any]) -> Path:
    archive_id = archive["archive_id"]
    title = archive["payload"].get("title") or "conversation"
    filename = f"{safe_name(title)}-{archive_id}.json"
    target = root / ARCHIVE_DIR / filename
    atomic_write(target, json.dumps(archive, ensure_ascii=False, indent=2) + "\n")
    index = load_index(root)
    entry = {
        "archive_id": archive_id,
        "imported_at": archive["imported_at"],
        "title": title,
        "conversation_id": archive["payload"].get("conversation_id"),
        "surface": archive["source"]["surface"],
        "coverage": archive["source"]["coverage"],
        "message_count": len(archive["payload"].get("messages", [])),
        "lane": archive.get("lane"),
        "is_voice_conversation": archive["voice"]["is_voice_conversation"],
        "raw_audio_archived": archive["voice"]["raw_audio_archived"],
        "payload_sha256": archive["integrity"]["payload_sha256"],
        "path": target.relative_to(root).as_posix(),
    }
    entries = [
        item for item in index.get("entries", []) if item.get("archive_id") != archive_id
    ]
    entries.append(entry)
    index["entries"] = sorted(entries, key=lambda item: item["archive_id"])
    index["updated_at"] = archive["imported_at"]
    atomic_write(root / INDEX_PATH, json.dumps(index, ensure_ascii=False, indent=2) + "\n")
    atomic_write(root / VIEW_PATH, render_view(index))
    return target


def validate_archive_files(root: Path) -> list[str]:
    errors: list[str] = []
    index_path = root / INDEX_PATH
    view_path = root / VIEW_PATH
    if not index_path.is_file():
        return [f"missing conversation archive index: {INDEX_PATH}"]
    try:
        index = load_index(root)
    except (OSError, json.JSONDecodeError) as error:
        return [f"cannot read conversation archive index: {error}"]
    if index.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"archive schema_version must be {SCHEMA_VERSION}")
    seen: set[str] = set()
    for entry in index.get("entries", []):
        archive_id = entry.get("archive_id", "")
        if not archive_id:
            errors.append("archive entry missing archive_id")
            continue
        if archive_id in seen:
            errors.append(f"duplicate archive_id: {archive_id}")
        seen.add(archive_id)
        path = root / entry.get("path", "")
        if not path.is_file():
            errors.append(f"missing archive file: {entry.get('path')}")
            continue
        try:
            archive = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"cannot read archive {path}: {error}")
            continue
        digest = sha256_bytes(canonical_bytes(archive.get("payload")))
        if digest != archive.get("integrity", {}).get("payload_sha256"):
            errors.append(f"payload hash mismatch: {entry.get('path')}")
        if digest != entry.get("payload_sha256"):
            errors.append(f"index hash mismatch: {entry.get('path')}")
        for media in archive.get("voice", {}).get("audio_files", []):
            media_path = root / media.get("path", "")
            if not media_path.is_file():
                errors.append(f"missing archived audio: {media.get('path')}")
            elif sha256_file(media_path) != media.get("sha256"):
                errors.append(f"audio hash mismatch: {media.get('path')}")
    if not view_path.is_file():
        errors.append(f"missing generated archive view: {VIEW_PATH}")
    elif view_path.read_text(encoding="utf-8") != render_view(index):
        errors.append(f"{VIEW_PATH} is stale; run conversation_archive.py view")
    return errors


def cmd_import(args: argparse.Namespace) -> int:
    root = args.root.expanduser().resolve()
    source = args.source.expanduser().resolve()
    if not source.is_file():
        print(f"ERROR: source file does not exist: {source}", file=sys.stderr)
        return 1
    if args.surface not in SURFACES:
        print(f"ERROR: invalid surface {args.surface}", file=sys.stderr)
        return 1
    try:
        audio_paths = [path.expanduser() for path in args.audio]
        if args.kind == "chatgpt-export":
            conversations = select_conversations(
                load_chatgpt_export(source),
                args.conversation_id,
                args.title,
                args.latest,
                args.all,
            )
            if not conversations:
                raise ValueError("no conversation matched the selection")
            imported: list[Path] = []
            for conversation in conversations:
                payload, matched = normalize_chatgpt_conversation(
                    conversation, args.before_trigger
                )
                provisional_id = sha256_bytes(canonical_bytes(payload))[:20]
                media = archive_media(root, provisional_id, audio_paths)
                archive = build_archive(
                    source,
                    payload,
                    args.surface,
                    "exact_export",
                    args.before_trigger,
                    matched,
                    args.lane,
                    media,
                )
                if media and provisional_id != archive["archive_id"]:
                    old = root / MEDIA_DIR / provisional_id
                    new = root / MEDIA_DIR / archive["archive_id"]
                    if old.is_dir() and not new.exists():
                        old.rename(new)
                        for record in archive["voice"]["audio_files"]:
                            record["path"] = record["path"].replace(
                                provisional_id, archive["archive_id"], 1
                            )
                imported.append(save_archive(root, archive))
        else:
            payload = provided_transcript(source, args.title)
            provisional_id = sha256_bytes(canonical_bytes(payload))[:20]
            media = archive_media(root, provisional_id, audio_paths)
            coverage = (
                "visible_context_only"
                if args.kind == "visible-context"
                else "provided_transcript"
            )
            archive = build_archive(
                source,
                payload,
                args.surface,
                coverage,
                args.before_trigger,
                False,
                args.lane,
                media,
            )
            if media and provisional_id != archive["archive_id"]:
                old = root / MEDIA_DIR / provisional_id
                new = root / MEDIA_DIR / archive["archive_id"]
                if old.is_dir() and not new.exists():
                    old.rename(new)
                    for record in archive["voice"]["audio_files"]:
                        record["path"] = record["path"].replace(
                            provisional_id, archive["archive_id"], 1
                        )
            imported = [save_archive(root, archive)]
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    for path in imported:
        print(f"archived {path}")
    print(f"updated {root / INDEX_PATH}")
    print(f"updated {root / VIEW_PATH}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    default_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    importer = subparsers.add_parser("import", help="import an exported conversation or transcript")
    importer.add_argument("--root", type=Path, default=default_root)
    importer.add_argument("--source", type=Path, required=True)
    importer.add_argument(
        "--kind",
        choices=("chatgpt-export", "transcript", "visible-context"),
        required=True,
    )
    importer.add_argument("--surface", choices=sorted(SURFACES), required=True)
    importer.add_argument("--conversation-id", default="")
    importer.add_argument("--title", default="")
    importer.add_argument("--latest", action="store_true")
    importer.add_argument("--all", action="store_true")
    importer.add_argument("--before-trigger", default="导入")
    importer.add_argument("--lane", default="")
    importer.add_argument("--audio", type=Path, action="append", default=[])
    check = subparsers.add_parser("check", help="validate archives, media hashes, and view")
    check.add_argument("--root", type=Path, default=default_root)
    view = subparsers.add_parser("view", help="rebuild the archive index view")
    view.add_argument("--root", type=Path, default=default_root)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = args.root.expanduser().resolve()
    if args.command == "import":
        return cmd_import(args)
    if args.command == "check":
        errors = validate_archive_files(root)
        for error in errors:
            print(f"ERROR: {error}")
        if errors:
            return 1
        index = load_index(root)
        print(f"OK: {len(index.get('entries', []))} conversation archives")
        return 0
    if args.command == "view":
        index = load_index(root)
        atomic_write(root / VIEW_PATH, render_view(index))
        print(f"updated {root / VIEW_PATH}")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
