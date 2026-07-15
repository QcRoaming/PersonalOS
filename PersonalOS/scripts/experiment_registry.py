#!/usr/bin/env python3
"""Refresh and validate the PersonalOS experiment registry."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any


SCHEMA_VERSION = 1
REGISTRY_RELATIVE_PATH = Path("registries/experiments.json")
VIEW_RELATIVE_PATH = Path("EXPERIMENTS.md")
ALLOWED_CATEGORIES = {
    "historical_experiment",
    "paper_reproduction_material",
    "thesis_evidence",
}
ALLOWED_STATUSES = {
    "archived",
    "complete_method_evidence",
    "complete_pending_human_signoff",
    "reference_extraction_only",
}
ALLOWED_PAPER_TIERS = {
    "primary_main_text",
    "supporting_main_text",
    "appendix_only",
    "reference_only",
}
IGNORED_FILE_PARTS = {".git", "__pycache__"}
IGNORED_FILE_SUFFIXES = {".pyc", ".pyo"}
REQUIRED_ENTRY_FIELDS = {
    "id",
    "title",
    "chapter",
    "category",
    "status",
    "paths",
    "claim_boundary",
    "automation",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def timestamp_utc(timestamp: float) -> str:
    return (
        datetime.fromtimestamp(timestamp, timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def is_safe_relative_path(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts and value == path.as_posix()


def load_registry(root: Path) -> dict[str, Any]:
    path = root / REGISTRY_RELATIVE_PATH
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def validate_registry_data(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["registry root must be a JSON object"]
    if data.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if data.get("registry_id") != "personal.experiments":
        errors.append("registry_id must be personal.experiments")
    if data.get("generated_view") != VIEW_RELATIVE_PATH.as_posix():
        errors.append(f"generated_view must be {VIEW_RELATIVE_PATH.as_posix()}")
    paper_source = data.get("paper_selection_source")
    if paper_source is not None and not is_safe_relative_path(paper_source):
        errors.append("paper_selection_source must be a safe POSIX relative path")
    entries = data.get("entries")
    if not isinstance(entries, list) or not entries:
        errors.append("entries must be a non-empty list")
        return errors

    seen: set[str] = set()
    for index, entry in enumerate(entries):
        prefix = f"entries[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix} must be an object")
            continue
        missing = sorted(REQUIRED_ENTRY_FIELDS - set(entry))
        if missing:
            errors.append(f"{prefix} missing fields: {', '.join(missing)}")
        entry_id = entry.get("id")
        if not isinstance(entry_id, str) or not entry_id:
            errors.append(f"{prefix}.id must be a non-empty string")
        elif entry_id in seen:
            errors.append(f"duplicate experiment id: {entry_id}")
        else:
            seen.add(entry_id)
        if entry.get("category") not in ALLOWED_CATEGORIES:
            errors.append(f"{prefix}.category is not supported")
        if entry.get("status") not in ALLOWED_STATUSES:
            errors.append(f"{prefix}.status is not supported")

        paths = entry.get("paths")
        if not isinstance(paths, list) or not paths:
            errors.append(f"{prefix}.paths must be a non-empty list")
        else:
            for path_index, scope in enumerate(paths):
                scope_prefix = f"{prefix}.paths[{path_index}]"
                if not isinstance(scope, dict):
                    errors.append(f"{scope_prefix} must be an object")
                    continue
                if not isinstance(scope.get("role"), str) or not scope.get("role"):
                    errors.append(f"{scope_prefix}.role must be a non-empty string")
                if not is_safe_relative_path(scope.get("path")):
                    errors.append(f"{scope_prefix}.path must be a safe POSIX relative path")

        artifact_index = entry.get("artifact_index")
        if artifact_index is not None and not is_safe_relative_path(artifact_index):
            errors.append(f"{prefix}.artifact_index must be null or a safe relative path")
        evidence_files = entry.get("evidence_files", [])
        if not isinstance(evidence_files, list):
            errors.append(f"{prefix}.evidence_files must be a list")
        else:
            for evidence in evidence_files:
                if not is_safe_relative_path(evidence):
                    errors.append(f"{prefix}.evidence_files contains an unsafe path")
        reproduce = entry.get("reproduce_command")
        if reproduce is not None and not isinstance(reproduce, str):
            errors.append(f"{prefix}.reproduce_command must be null or a string")
        automation = entry.get("automation")
        if not isinstance(automation, dict):
            errors.append(f"{prefix}.automation must be an object")
        else:
            if not isinstance(automation.get("auto_refresh"), bool):
                errors.append(f"{prefix}.automation.auto_refresh must be a boolean")
            producer = automation.get("producer")
            if producer is not None and not is_safe_relative_path(producer):
                errors.append(f"{prefix}.automation.producer must be null or a safe relative path")
        paper_use = entry.get("paper_use")
        if paper_use is not None:
            if not isinstance(paper_use, dict):
                errors.append(f"{prefix}.paper_use must be an object")
            else:
                if paper_use.get("tier") not in ALLOWED_PAPER_TIERS:
                    errors.append(f"{prefix}.paper_use.tier is not supported")
                if not isinstance(paper_use.get("body_eligible"), bool):
                    errors.append(f"{prefix}.paper_use.body_eligible must be a boolean")
                for field in ("recommended_sections", "usable_claims"):
                    value = paper_use.get(field)
                    if not isinstance(value, list) or not all(
                        isinstance(item, str) and item for item in value
                    ):
                        errors.append(f"{prefix}.paper_use.{field} must be a non-empty string list")
                if not isinstance(paper_use.get("decision"), str) or not paper_use.get("decision"):
                    errors.append(f"{prefix}.paper_use.decision must be a non-empty string")

    if [entry.get("id") for entry in entries if isinstance(entry, dict)] != sorted(seen):
        errors.append("entries must be sorted by id")
    return errors


def sync_paper_use(data: dict[str, Any], workspace_root: Path) -> None:
    relative = data.get("paper_selection_source")
    if not relative:
        return
    source = resolve_workspace_path(workspace_root, relative)
    with source.open(encoding="utf-8") as stream:
        selection = json.load(stream)
    selected_entries = selection.get("entries")
    if not isinstance(selected_entries, list):
        raise ValueError("paper evidence selection entries must be a list")
    selected = {entry.get("id"): entry for entry in selected_entries if isinstance(entry, dict)}
    registry_ids = {entry["id"] for entry in data["entries"]}
    selected_ids = set(selected)
    if selected_ids != registry_ids:
        missing = sorted(registry_ids - selected_ids)
        extra = sorted(selected_ids - registry_ids)
        raise ValueError(
            "paper evidence selection ids differ from registry; "
            f"missing={missing}, extra={extra}"
        )
    for entry in data["entries"]:
        source_entry = selected[entry["id"]]
        entry["paper_use"] = {
            "tier": source_entry.get("tier"),
            "body_eligible": source_entry.get("body_eligible"),
            "recommended_sections": source_entry.get("recommended_sections"),
            "decision": source_entry.get("decision"),
            "usable_claims": source_entry.get("usable_claims"),
        }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_workspace_path(workspace_root: Path, relative: str) -> Path:
    workspace = workspace_root.resolve()
    candidate = (workspace / relative).resolve(strict=False)
    if candidate != workspace and workspace not in candidate.parents:
        raise ValueError(f"path escapes workspace root: {relative}")
    return candidate


def collect_observed(entry: dict[str, Any], workspace_root: Path, refreshed_at: str) -> dict[str, Any]:
    path_status: list[dict[str, Any]] = []
    files: dict[str, Path] = {}
    latest_mtime: float | None = None
    for scope in entry["paths"]:
        relative = scope["path"]
        path = resolve_workspace_path(workspace_root, relative)
        exists = path.exists()
        path_status.append({"role": scope["role"], "path": relative, "exists": exists})
        if not exists:
            continue
        candidates = [path] if path.is_file() else path.rglob("*")
        for candidate in candidates:
            if (
                candidate.is_symlink()
                or not candidate.is_file()
                or IGNORED_FILE_PARTS.intersection(candidate.parts)
                or candidate.suffix in IGNORED_FILE_SUFFIXES
            ):
                continue
            resolved = candidate.resolve()
            if workspace_root.resolve() not in resolved.parents and resolved != workspace_root.resolve():
                continue
            relative_file = resolved.relative_to(workspace_root.resolve()).as_posix()
            files[relative_file] = resolved

    fingerprint = hashlib.sha256()
    size_bytes = 0
    for relative, path in sorted(files.items()):
        stat = path.stat()
        size_bytes += stat.st_size
        latest_mtime = max(latest_mtime or stat.st_mtime, stat.st_mtime)
        fingerprint.update(f"{relative}\t{stat.st_size}\t{stat.st_mtime_ns}\n".encode())

    tracked: dict[str, dict[str, Any]] = {}
    tracked_paths = [entry.get("artifact_index"), *entry.get("evidence_files", [])]
    for relative in sorted({item for item in tracked_paths if item}):
        path = resolve_workspace_path(workspace_root, relative)
        if path.is_file() and not path.is_symlink():
            stat = path.stat()
            tracked[relative] = {
                "exists": True,
                "size_bytes": stat.st_size,
                "modified_at_utc": timestamp_utc(stat.st_mtime),
                "sha256": sha256_file(path),
            }
        else:
            tracked[relative] = {"exists": False}

    previous = entry.get("observed", {})
    return {
        "refreshed_at_utc": refreshed_at,
        "all_paths_exist": all(item["exists"] for item in path_status),
        "path_status": path_status,
        "file_count": len(files),
        "size_bytes": size_bytes,
        "last_modified_utc": timestamp_utc(latest_mtime) if latest_mtime is not None else None,
        "tree_fingerprint_sha256": fingerprint.hexdigest(),
        "tracked_files": tracked,
        "last_successful_run_utc": previous.get("last_successful_run_utc"),
    }


def human_size(size: int) -> str:
    value = float(size)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if value < 1024 or unit == "TiB":
            return f"{value:.0f} {unit}" if unit == "B" else f"{value:.1f} {unit}"
        value /= 1024
    raise AssertionError("unreachable")


def markdown_cell(value: Any) -> str:
    return str(value).replace("|", "/").replace("\n", " ")


def render_markdown(data: dict[str, Any]) -> str:
    entries = data["entries"]
    available = sum(bool(entry.get("observed", {}).get("all_paths_exist")) for entry in entries)
    auto = sum(bool(entry.get("automation", {}).get("auto_refresh")) for entry in entries)
    body_eligible = sum(
        bool(entry.get("paper_use", {}).get("body_eligible")) for entry in entries
    )
    lines = [
        "# Experiment Registry",
        "",
        "> Generated from `registries/experiments.json`; do not edit this file directly.",
        "",
        "## Storage Boundary",
        "",
        "PersonalOS stores experiment metadata, evidence pointers, hashes, and run state only. Raw data and build outputs remain in the workspace named by `workspace_root_hint`.",
        "",
        f"- Workspace root hint: `{data.get('workspace_root_hint', 'unknown')}`",
        f"- Last refreshed: `{data.get('last_refreshed_at_utc', 'never')}`",
        f"- Registered experiments: {len(entries)}",
        f"- Fully available paths: {available}/{len(entries)}",
        f"- Runner-maintained entries: {auto}/{len(entries)}",
        f"- Main-text eligible entries: {body_eligible}/{len(entries)}",
        "",
        "## Overview",
        "",
        "| ID | Chapter | Category | Status | Paper use | Paths | Files | Size | Last successful run |",
        "|---|---|---|---|---|---|---:|---:|---|",
    ]
    for entry in entries:
        observed = entry.get("observed", {})
        availability = "available" if observed.get("all_paths_exist") else "partial/missing"
        lines.append(
            "| `{id}` | {chapter} | {category} | {status} | {paper_use} | {availability} | {files} | {size} | {last_run} |".format(
                id=markdown_cell(entry["id"]),
                chapter=markdown_cell(entry["chapter"]),
                category=markdown_cell(entry["category"]),
                status=markdown_cell(entry["status"]),
                paper_use=markdown_cell(entry.get("paper_use", {}).get("tier", "unclassified")),
                availability=availability,
                files=observed.get("file_count", 0),
                size=human_size(observed.get("size_bytes", 0)),
                last_run=observed.get("last_successful_run_utc") or "not recorded",
            )
        )

    lines.extend(["", "## Entries", ""])
    for entry in entries:
        observed = entry.get("observed", {})
        lines.extend(
            [
                f"### {entry['title']} (`{entry['id']}`)",
                "",
                f"- Chapter/scope: {entry['chapter']}",
                f"- Category: `{entry['category']}`",
                f"- Status: `{entry['status']}`",
                f"- Paper use: `{entry.get('paper_use', {}).get('tier', 'unclassified')}`; main-text eligible: `{str(bool(entry.get('paper_use', {}).get('body_eligible'))).lower()}`",
                "- Recommended sections: " + (
                    "; ".join(entry.get("paper_use", {}).get("recommended_sections", [])) or "none"
                ),
                f"- Writing decision: {entry.get('paper_use', {}).get('decision', 'not classified')}",
                "- Paths: " + "; ".join(
                    f"{item['role']}=`{item['path']}`" for item in entry["paths"]
                ),
                f"- Artifact index: `{entry['artifact_index']}`" if entry.get("artifact_index") else "- Artifact index: none",
                "- Evidence: " + (
                    ", ".join(f"`{path}`" for path in entry.get("evidence_files", [])) or "none"
                ),
                f"- Reproduction: `{entry['reproduce_command']}`" if entry.get("reproduce_command") else "- Reproduction: no standalone command registered",
                "- Registry maintenance: " + (
                    f"automatic after `{entry['automation'].get('producer')}` succeeds"
                    if entry["automation"].get("auto_refresh")
                    else "manual refresh"
                ),
                f"- Claim boundary: {entry['claim_boundary']}",
                f"- Observed: {observed.get('file_count', 0)} files, {human_size(observed.get('size_bytes', 0))}, tree fingerprint `{observed.get('tree_fingerprint_sha256', 'not refreshed')}`",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(text)
        os.chmod(temporary, 0o644)
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def validate_registry_files(root: Path) -> list[str]:
    registry_path = root / REGISTRY_RELATIVE_PATH
    view_path = root / VIEW_RELATIVE_PATH
    if not registry_path.is_file():
        return [f"missing experiment registry: {REGISTRY_RELATIVE_PATH}"]
    try:
        data = load_registry(root)
    except (OSError, json.JSONDecodeError) as error:
        return [f"cannot read experiment registry: {error}"]
    errors = validate_registry_data(data)
    if not view_path.is_file():
        errors.append(f"missing generated experiment view: {VIEW_RELATIVE_PATH}")
    elif not errors and view_path.read_text(encoding="utf-8") != render_markdown(data):
        errors.append(f"{VIEW_RELATIVE_PATH} is stale; run experiment_registry.py refresh")
    return errors


def refresh_registry(
    root: Path, workspace_root: Path, completed_ids: str | list[str] | None
) -> dict[str, Any]:
    data = load_registry(root)
    errors = validate_registry_data(data)
    if errors:
        raise ValueError("invalid registry:\n- " + "\n- ".join(errors))
    sync_paper_use(data, workspace_root)
    errors = validate_registry_data(data)
    if errors:
        raise ValueError("invalid paper-use metadata:\n- " + "\n- ".join(errors))
    ids = {entry["id"] for entry in data["entries"]}
    completed = {completed_ids} if isinstance(completed_ids, str) else set(completed_ids or [])
    unknown = sorted(completed - ids)
    if unknown:
        raise ValueError(f"unknown completed experiment id(s): {', '.join(unknown)}")

    refreshed_at = utc_now()
    for entry in data["entries"]:
        observed = collect_observed(entry, workspace_root, refreshed_at)
        if entry["id"] in completed:
            observed["last_successful_run_utc"] = refreshed_at
        entry["observed"] = observed
    data["entries"].sort(key=lambda entry: entry["id"])
    data["workspace_root_hint"] = str(workspace_root.resolve())
    data["last_refreshed_at_utc"] = refreshed_at

    atomic_write(
        root / REGISTRY_RELATIVE_PATH,
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
    )
    atomic_write(root / VIEW_RELATIVE_PATH, render_markdown(data))
    return data


def build_parser() -> argparse.ArgumentParser:
    default_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    refresh = subparsers.add_parser("refresh", help="refresh observed metadata and Markdown view")
    refresh.add_argument("--root", type=Path, default=default_root)
    refresh.add_argument(
        "--workspace-root",
        type=Path,
        default=Path(os.environ.get("BUDDY_MLIR_ROOT", "/buddy-mlir")),
    )
    refresh.add_argument("--completed-id", action="append", default=[])
    check = subparsers.add_parser("check", help="validate schema and generated view")
    check.add_argument("--root", type=Path, default=default_root)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = args.root.expanduser().resolve()
    if args.command == "check":
        errors = validate_registry_files(root)
        for error in errors:
            print(f"ERROR: {error}")
        if errors:
            return 1
        data = load_registry(root)
        print(f"OK: {len(data['entries'])} registered experiments; generated view is current")
        return 0
    if args.command == "refresh":
        try:
            data = refresh_registry(root, args.workspace_root.expanduser(), args.completed_id)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            print(f"ERROR: {error}", file=sys.stderr)
            return 1
        available = sum(entry["observed"]["all_paths_exist"] for entry in data["entries"])
        print(f"updated {root / REGISTRY_RELATIVE_PATH}")
        print(f"updated {root / VIEW_RELATIVE_PATH}")
        print(f"registered={len(data['entries'])} fully_available={available}")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
