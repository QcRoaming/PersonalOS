#!/usr/bin/env python3
"""Validate, route, and summarize a lightweight PersonalOS directory."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path

from experiment_registry import validate_registry_files


REQUIRED_ROOT_FILES = ("PERSONAL.md", "ROUTES.md", "AGENTS.md")
REQUIRED_META = ("id", "role", "priority", "status", "version", "keywords")
GENERATED_VIEWS = ("DASHBOARD.md", "HANDOFF.md", "KNOWLEDGE.md")
KNOWLEDGE_STATES = ("unknown", "exposed", "understood", "applied", "verified", "stale")
MANAGED_BEGIN = "<!-- PERSONAL_OS:BEGIN -->"
MANAGED_END = "<!-- PERSONAL_OS:END -->"


@dataclass
class Lane:
    path: Path
    meta: dict[str, str]
    text: str


def parse_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return {}, text
    meta: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip()
    return meta, "\n".join(lines[end + 1 :]).lstrip()


def load_lanes(root: Path) -> list[Lane]:
    lanes: list[Lane] = []
    for path in sorted((root / "lanes").glob("*.md")):
        meta, body = parse_frontmatter(path)
        lanes.append(Lane(path=path, meta=meta, text=body))
    return lanes


def section(text: str, name: str, limit: int = 3) -> list[str]:
    pattern = re.compile(rf"^#\s+{re.escape(name)}\s*$", re.MULTILINE | re.IGNORECASE)
    match = pattern.search(text)
    if not match:
        return []
    tail = text[match.end() :]
    next_heading = re.search(r"^#\s+", tail, re.MULTILINE)
    if next_heading:
        tail = tail[: next_heading.start()]
    items: list[str] = []
    for raw in tail.splitlines():
        line = raw.strip()
        if not line:
            continue
        line = re.sub(r"^[-*]\s+", "", line)
        line = re.sub(r"^\d+\.\s+", "", line)
        if line.startswith("|") or line.startswith("#"):
            continue
        items.append(line)
        if len(items) >= limit:
            break
    return items


def priority_value(value: str) -> int:
    match = re.fullmatch(r"P(\d+)", value.strip(), re.IGNORECASE)
    return int(match.group(1)) if match else 99


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


def markdown_cell(value: str) -> str:
    return str(value).replace("|", "/").replace("\n", " ").strip()


def section_body(text: str, name: str) -> str:
    pattern = re.compile(rf"^#\s+{re.escape(name)}\s*$", re.MULTILINE | re.IGNORECASE)
    match = pattern.search(text)
    if not match:
        return ""
    tail = text[match.end() :]
    next_heading = re.search(r"^#\s+", tail, re.MULTILINE)
    if next_heading:
        tail = tail[: next_heading.start()]
    return tail.strip()


def replace_section(text: str, name: str, body: str) -> str:
    replacement = f"# {name}\n\n{body.strip()}\n"
    pattern = re.compile(
        rf"^#\s+{re.escape(name)}\s*$.*?(?=^#\s+|\Z)",
        re.MULTILINE | re.IGNORECASE | re.DOTALL,
    )
    if pattern.search(text):
        return pattern.sub(replacement + "\n", text, count=1).rstrip() + "\n"
    return text.rstrip() + "\n\n" + replacement


def update_frontmatter(text: str, updates: dict[str, str]) -> str:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("file has no YAML frontmatter")
    try:
        end = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
    except StopIteration as error:
        raise ValueError("frontmatter is not closed") from error
    remaining = dict(updates)
    for index in range(1, end):
        if ":" not in lines[index]:
            continue
        key = lines[index].split(":", 1)[0].strip()
        if key in remaining:
            lines[index] = f"{key}: {remaining.pop(key)}"
    for key, value in remaining.items():
        lines.insert(end, f"{key}: {value}")
        end += 1
    return "\n".join(lines).rstrip() + "\n"


def select_lane(root: Path, query: str = "", lane_id: str = "") -> tuple[Lane | None, list[str]]:
    lanes = load_lanes(root)
    routes_meta, _ = parse_frontmatter(root / "ROUTES.md")
    if lane_id:
        lane = next((item for item in lanes if item.meta.get("id") == lane_id), None)
        return lane, [lane_id] if lane else []
    normalized = query.casefold()
    if "主线" in query or "main lane" in normalized or "mainline" in normalized:
        main_id = routes_meta.get("main_lane", "")
        return next((item for item in lanes if item.meta.get("id") == main_id), None), ["main_lane"]
    ranked: list[tuple[int, int, Lane, list[str]]] = []
    for lane in lanes:
        hits: list[str] = []
        score = 0
        current_id = lane.meta.get("id", "")
        title = lane.meta.get("title", "")
        if current_id.casefold() in normalized or (title and title.casefold() in normalized):
            score += 20
            hits.append(current_id)
        for keyword in lane.meta.get("keywords", "").split("|"):
            keyword = keyword.strip()
            if keyword and keyword.casefold() in normalized:
                score += max(2, min(8, len(keyword) // 2))
                hits.append(keyword)
        if score:
            ranked.append(
                (score, -priority_value(lane.meta.get("priority", "P99")), lane, hits)
            )
    ranked.sort(key=lambda item: (item[0], item[1]), reverse=True)
    if ranked:
        return ranked[0][2], ranked[0][3]
    if not query:
        main_id = routes_meta.get("main_lane", "")
        return next((item for item in lanes if item.meta.get("id") == main_id), None), []
    return None, []


def knowledge_rows(lane: Lane) -> list[list[str]]:
    body = section_body(lane.text, "Knowledge State")
    rows: list[list[str]] = []
    for raw in body.splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 4 or cells[0].casefold() == "topic" or set(cells[0]) == {"-"}:
            continue
        rows.append(cells[:4])
    return rows


def latest_experiment(root: Path) -> tuple[str, str, str] | None:
    path = root / "registries" / "experiments.json"
    if not path.is_file():
        return None
    try:
        entries = json.loads(path.read_text(encoding="utf-8")).get("entries", [])
    except (OSError, json.JSONDecodeError):
        return None
    ranked: list[tuple[str, str, str]] = []
    for entry in entries:
        observed = entry.get("observed", {})
        completed = observed.get("last_successful_run_utc")
        if completed:
            ranked.append((completed, entry.get("id", "unknown"), entry.get("status", "unknown")))
    return max(ranked) if ranked else None


def state_watermark(root: Path) -> str:
    values = [
        lane.meta.get("last_activity_at", lane.meta.get("updated_at", ""))
        for lane in load_lanes(root)
    ]
    registry = root / "registries" / "experiments.json"
    if registry.is_file():
        try:
            values.append(
                json.loads(registry.read_text(encoding="utf-8")).get(
                    "last_refreshed_at_utc", ""
                )
            )
        except (OSError, json.JSONDecodeError):
            pass
    return max((value for value in values if value), default="unknown")


def cmd_check(root: Path) -> int:
    errors: list[str] = []
    warnings: list[str] = []
    for name in REQUIRED_ROOT_FILES:
        if not (root / name).is_file():
            errors.append(f"missing root file: {name}")
    if not (root / "lanes").is_dir():
        errors.append("missing directory: lanes")
    lanes = load_lanes(root) if (root / "lanes").is_dir() else []
    seen: set[str] = set()
    main_count = 0
    versions: dict[str, int] = {}
    for lane in lanes:
        for key in REQUIRED_META:
            if not lane.meta.get(key):
                errors.append(f"{lane.path.name}: missing frontmatter field {key}")
        lane_id = lane.meta.get("id", lane.path.stem)
        if lane_id in seen:
            errors.append(f"duplicate lane id: {lane_id}")
        seen.add(lane_id)
        if lane.meta.get("role") == "main" and lane.meta.get("status") == "active":
            main_count += 1
        try:
            versions[lane_id] = int(lane.meta.get("version", ""))
        except ValueError:
            errors.append(f"{lane.path.name}: version must be an integer")
        line_count = len(lane.path.read_text(encoding="utf-8").splitlines())
        if line_count > 300:
            warnings.append(f"{lane.path.name}: {line_count} lines; compact the lane")
    if main_count != 1:
        errors.append(f"expected exactly one active main lane, found {main_count}")
    errors.extend(f"experiment registry: {item}" for item in validate_registry_files(root))
    if not errors:
        for name, expected in generated_view_texts(root).items():
            path = root / name
            if not path.is_file():
                errors.append(f"missing generated view: {name}")
            elif path.read_text(encoding="utf-8") != expected:
                errors.append(f"{name} is stale; run personal_os.py views")
    pending_dir = root / "pending"
    if pending_dir.is_dir():
        for delta in pending_dir.glob("*.delta.md"):
            meta, _ = parse_frontmatter(delta)
            lane_id = meta.get("lane", "")
            try:
                base_version = int(meta.get("base_version", ""))
            except ValueError:
                errors.append(f"{delta.name}: invalid base_version")
                continue
            if lane_id not in versions:
                errors.append(f"{delta.name}: unknown lane {lane_id}")
            elif base_version != versions[lane_id]:
                warnings.append(
                    f"{delta.name}: base version {base_version}, current {versions[lane_id]}"
                )
    for item in warnings:
        print(f"WARNING: {item}")
    for item in errors:
        print(f"ERROR: {item}")
    if errors:
        return 1
    print(f"OK: {len(lanes)} lanes, one active main lane, no structural errors")
    return 0


def cmd_route(root: Path, query: str) -> int:
    normalized = query.casefold()
    ranked: list[tuple[int, int, Lane, list[str]]] = []
    for lane in load_lanes(root):
        hits: list[str] = []
        score = 0
        lane_id = lane.meta.get("id", "")
        title = lane.meta.get("title", "")
        if lane_id.casefold() in normalized or (title and title.casefold() in normalized):
            score += 20
            hits.append(lane_id)
        for keyword in lane.meta.get("keywords", "").split("|"):
            keyword = keyword.strip()
            if keyword and keyword.casefold() in normalized:
                score += max(2, min(8, len(keyword) // 2))
                hits.append(keyword)
        if score:
            ranked.append((score, -priority_value(lane.meta.get("priority", "P99")), lane, hits))
    ranked.sort(key=lambda item: (item[0], item[1]), reverse=True)
    if not ranked:
        print("adhoc")
        return 0
    best = ranked[0]
    print(best[2].meta.get("id", best[2].path.stem))
    print(f"file={best[2].path.relative_to(root)}")
    print(f"score={best[0]}")
    print(f"matched={','.join(best[3])}")
    if len(ranked) > 1 and ranked[1][0] == best[0]:
        print(f"warning=tie with {ranked[1][2].meta.get('id')}")
    return 0


def cmd_dashboard(root: Path) -> int:
    routes_meta, _ = parse_frontmatter(root / "ROUTES.md")
    lanes = load_lanes(root)
    lines = [
        "# PersonalOS Dashboard",
        "",
        "> Generated view. Do not edit facts here; edit the owning lane and regenerate.",
        "",
        "## Global",
        "",
        f"- Main lane: `{routes_meta.get('main_lane', 'unknown')}`",
        f"- State watermark: {state_watermark(root)}",
        f"- Canonical store: `{routes_meta.get('canonical_store', 'unknown')}`",
        f"- Remote repository: `{routes_meta.get('git_repository', 'pending')}`",
        "",
        "## Lane Overview",
        "",
        "| Lane | Role | Priority | Status | Current checkpoint |",
        "|---|---|---:|---|---|",
    ]
    for lane in sorted(
        lanes,
        key=lambda item: (
            priority_value(item.meta.get("priority", "P99")),
            item.meta.get("id", ""),
        ),
    ):
        checkpoint = section(lane.text, "Current Checkpoint", 1)
        if not checkpoint:
            checkpoint = section(lane.text, "Current Chapter", 1)
        current = checkpoint[0] if checkpoint else "—"
        lines.append(
            "| `{id}` | {role} | {priority} | {status} | {current} |".format(
                id=lane.meta.get("id", lane.path.stem),
                role=lane.meta.get("role", "unknown"),
                priority=lane.meta.get("priority", "P?"),
                status=lane.meta.get("status", "unknown"),
                current=current.replace("|", "/"),
            )
        )
    registry_path = root / "registries" / "experiments.json"
    lines.extend(["", "## Experiment Registry", ""])
    if registry_path.is_file():
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        experiments = registry.get("entries", [])
        available = sum(
            bool(item.get("observed", {}).get("all_paths_exist")) for item in experiments
        )
        automatic = sum(
            bool(item.get("automation", {}).get("auto_refresh")) for item in experiments
        )
        body_eligible = sum(
            bool(item.get("paper_use", {}).get("body_eligible")) for item in experiments
        )
        lines.extend(
            [
                "- Human-readable index: `EXPERIMENTS.md`",
                f"- Registered experiments: {len(experiments)}",
                f"- Fully available paths: {available}/{len(experiments)}",
                f"- Runner-maintained entries: {automatic}/{len(experiments)}",
                f"- Main-text eligible entries: {body_eligible}/{len(experiments)}",
                f"- Last refreshed: `{registry.get('last_refreshed_at_utc', 'never')}`",
            ]
        )
    else:
        lines.append("- Registry not found.")
    main = next(
        (lane for lane in lanes if lane.meta.get("id") == routes_meta.get("main_lane")),
        None,
    )
    lines.extend(["", "## Main-line Next Actions", ""])
    if main:
        next_items = section(main.text, "Next", 5)
        lines.extend(f"{index}. {item}" for index, item in enumerate(next_items, 1))
    else:
        lines.append("- Main lane not found.")
    blockers: list[str] = []
    for lane in lanes:
        if lane.meta.get("status") == "active":
            blockers.extend(
                f"{lane.meta.get('id')}: {item}"
                for item in section(lane.text, "Current Blockers", 1)
            )
    lines.extend(["", "## Active Blockers", ""])
    lines.extend(f"- {item}" for item in blockers[:6])
    (root / "DASHBOARD.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"updated {root / 'DASHBOARD.md'}")
    return 0


def render_dashboard(root: Path) -> str:
    routes_meta, _ = parse_frontmatter(root / "ROUTES.md")
    lanes = load_lanes(root)
    code = chr(96)
    lines = [
        "# PersonalOS Dashboard",
        "",
        "> Generated view. Do not edit facts here; edit the owning lane and regenerate.",
        "",
        "## Global",
        "",
        f"- Main lane: {code}{routes_meta.get('main_lane', 'unknown')}{code}",
        f"- State watermark: {state_watermark(root)}",
        f"- Canonical store: {code}{routes_meta.get('canonical_store', 'unknown')}{code}",
        f"- Remote repository: {code}{routes_meta.get('git_repository', 'pending')}{code}",
        "",
        "## Lane Overview",
        "",
        "| Lane | Role | Priority | Status | Last activity | Current checkpoint |",
        "|---|---|---:|---|---|---|",
    ]
    for lane in sorted(
        lanes,
        key=lambda item: (
            priority_value(item.meta.get("priority", "P99")),
            item.meta.get("id", ""),
        ),
    ):
        checkpoint = section(lane.text, "Current Checkpoint", 1)
        if not checkpoint:
            checkpoint = section(lane.text, "Current Chapter", 1)
        current = checkpoint[0] if checkpoint else "—"
        lines.append(
            "| {code}{id}{code} | {role} | {priority} | {status} | {activity} | {current} |".format(
                code=code,
                id=lane.meta.get("id", lane.path.stem),
                role=lane.meta.get("role", "unknown"),
                priority=lane.meta.get("priority", "P?"),
                status=lane.meta.get("status", "unknown"),
                activity=lane.meta.get("last_activity_at", lane.meta.get("updated_at", "unknown")),
                current=markdown_cell(current),
            )
        )
    registry_path = root / "registries" / "experiments.json"
    lines.extend(["", "## Experiment Registry", ""])
    if registry_path.is_file():
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        experiments = registry.get("entries", [])
        available = sum(
            bool(item.get("observed", {}).get("all_paths_exist")) for item in experiments
        )
        automatic = sum(
            bool(item.get("automation", {}).get("auto_refresh")) for item in experiments
        )
        body_eligible = sum(
            bool(item.get("paper_use", {}).get("body_eligible")) for item in experiments
        )
        lines.extend(
            [
                f"- Human-readable index: {code}EXPERIMENTS.md{code}",
                f"- Registered experiments: {len(experiments)}",
                f"- Fully available paths: {available}/{len(experiments)}",
                f"- Runner-maintained entries: {automatic}/{len(experiments)}",
                f"- Main-text eligible entries: {body_eligible}/{len(experiments)}",
                f"- Last refreshed: {code}{registry.get('last_refreshed_at_utc', 'never')}{code}",
            ]
        )
    else:
        lines.append("- Registry not found.")
    main = next(
        (lane for lane in lanes if lane.meta.get("id") == routes_meta.get("main_lane")),
        None,
    )
    lines.extend(["", "## Main-line Next Actions", ""])
    if main:
        next_items = section(main.text, "Next", 5)
        lines.extend(f"{index}. {item}" for index, item in enumerate(next_items, 1))
    else:
        lines.append("- Main lane not found.")
    blockers: list[str] = []
    for lane in lanes:
        if lane.meta.get("status") == "active":
            blockers.extend(
                f"{lane.meta.get('id')}: {item}"
                for item in section(lane.text, "Current Blockers", 1)
            )
    lines.extend(["", "## Active Blockers", ""])
    lines.extend(f"- {item}" for item in blockers[:6])
    return "\n".join(lines).rstrip() + "\n"


def render_handoff(root: Path) -> str:
    routes_meta, _ = parse_frontmatter(root / "ROUTES.md")
    code = chr(96)
    lanes = sorted(
        load_lanes(root),
        key=lambda lane: (
            lane.meta.get("last_activity_at", lane.meta.get("updated_at", "")),
            -priority_value(lane.meta.get("priority", "P99")),
        ),
        reverse=True,
    )
    lines = [
        "# PersonalOS Handoff",
        "",
        "> Generated recovery packet. The owning lane files remain authoritative.",
        "",
        "## Resume Anchor",
        "",
        f"- Canonical repository: {code}{routes_meta.get('git_repository', 'unknown')}{code}",
        f"- Repository subdirectory: {code}{routes_meta.get('repository_subdir', '.')}{code}",
        f"- Main lane: {code}{routes_meta.get('main_lane', 'unknown')}{code}",
        f"- State watermark: {state_watermark(root)}",
    ]
    recent = latest_experiment(root)
    if recent:
        lines.extend(
            [
                f"- Latest successful registered experiment: {code}{recent[1]}{code}",
                f"- Experiment completed at: {code}{recent[0]}{code}",
            ]
        )
    lines.extend(
        [
            "",
            "## Recent Lane State",
            "",
            "| Lane | Last activity | Checkpoint | Doing | Next |",
            "|---|---|---|---|---|",
        ]
    )
    for lane in lanes:
        checkpoint = section(lane.text, "Current Checkpoint", 1)
        if not checkpoint:
            checkpoint = section(lane.text, "Current Chapter", 1)
        doing = section(lane.text, "Doing", 1)
        next_items = section(lane.text, "Next", 1)
        lines.append(
            "| {code}{id}{code} | {activity} | {checkpoint} | {doing} | {next_item} |".format(
                code=code,
                id=lane.meta.get("id", lane.path.stem),
                activity=lane.meta.get("last_activity_at", lane.meta.get("updated_at", "unknown")),
                checkpoint=markdown_cell(checkpoint[0] if checkpoint else "—"),
                doing=markdown_cell(doing[0] if doing else "—"),
                next_item=markdown_cell(next_items[0] if next_items else "—"),
            )
        )
    lines.extend(
        [
            "",
            "## Recovery Rule",
            "",
            "1. Read PERSONAL.md and ROUTES.md.",
            "2. Select exactly one lane; read only that lane and declared dependency sections.",
            "3. Treat the newest remote commit as canonical; do not infer current state from chat memory.",
            "4. Read KNOWLEDGE.md only for an explicit cross-domain learning review.",
            "5. Read EXPERIMENTS.md or its registry entry only when experiment evidence is relevant.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def render_knowledge(root: Path) -> str:
    code = chr(96)
    lines = [
        "# PersonalOS Knowledge Index",
        "",
        "> Generated cross-domain index. Knowledge facts remain owned by their lane files.",
        "",
        "| Lane | Topic | State | Evidence | Next evidence |",
        "|---|---|---|---|---|",
    ]
    for lane in sorted(
        load_lanes(root),
        key=lambda item: (
            priority_value(item.meta.get("priority", "P99")),
            item.meta.get("id", ""),
        ),
    ):
        for topic, state, evidence, next_evidence in knowledge_rows(lane):
            lines.append(
                "| {code}{lane_id}{code} | {topic} | {state} | {evidence} | {next_evidence} |".format(
                    code=code,
                    lane_id=lane.meta.get("id", lane.path.stem),
                    topic=markdown_cell(topic),
                    state=markdown_cell(state),
                    evidence=markdown_cell(evidence),
                    next_evidence=markdown_cell(next_evidence),
                )
            )
    lines.extend(
        [
            "",
            "Knowledge stages: unknown → exposed → understood → applied → verified. "
            "Use stale when older evidence must be revalidated.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def generated_view_texts(root: Path) -> dict[str, str]:
    return {
        "DASHBOARD.md": render_dashboard(root),
        "HANDOFF.md": render_handoff(root),
        "KNOWLEDGE.md": render_knowledge(root),
    }


def cmd_views(root: Path) -> int:
    for name, content in generated_view_texts(root).items():
        atomic_write(root / name, content)
        print(f"updated {root / name}")
    return 0


def cmd_dashboard(root: Path) -> int:
    return cmd_views(root)


def update_knowledge(body: str, specifications: list[str]) -> str:
    rows: list[list[str]] = []
    for raw in body.splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) >= 4 and cells[0].casefold() != "topic" and set(cells[0]) != {"-"}:
            rows.append(cells[:4])
    by_topic = {row[0].casefold(): row for row in rows}
    for specification in specifications:
        cells = [cell.strip() for cell in specification.split("|")]
        if len(cells) != 4:
            raise ValueError(
                "knowledge must use topic|state|evidence|next-evidence"
            )
        topic, state, evidence, next_evidence = cells
        if state not in KNOWLEDGE_STATES:
            raise ValueError(f"invalid knowledge state: {state}")
        replacement = [topic, state, evidence, next_evidence]
        previous = by_topic.get(topic.casefold())
        if previous:
            rows[rows.index(previous)] = replacement
        else:
            rows.append(replacement)
        by_topic[topic.casefold()] = replacement
    lines = [
        "| Topic | State | Evidence | Next evidence |",
        "|---|---|---|---|",
    ]
    lines.extend("| " + " | ".join(markdown_cell(cell) for cell in row) + " |" for row in rows)
    return "\n".join(lines)


def cmd_checkpoint(
    root: Path,
    lane_id: str,
    summary: str,
    doing: list[str],
    next_items: list[str],
    evidence: list[str],
    artifacts: list[str],
    knowledge: list[str],
    base_version: int | None,
) -> int:
    lane, _ = select_lane(root, lane_id=lane_id)
    if not lane:
        print(f"ERROR: unknown lane {lane_id}", file=sys.stderr)
        return 1
    lock = root / ".personal-os.lock"
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        print(
            f"ERROR: another PersonalOS writer holds {lock}; retry after it finishes",
            file=sys.stderr,
        )
        return 1
    original = lane.path.read_text(encoding="utf-8")
    try:
        current_version = int(lane.meta.get("version", "0"))
        if base_version is not None and base_version != current_version:
            print(
                f"ERROR: base version {base_version}, current version {current_version}; "
                "pull and merge before retrying",
                file=sys.stderr,
            )
            return 1
        updated = replace_section(original, "Current Checkpoint", summary)
        if doing:
            updated = replace_section(
                updated, "Doing", "\n".join(f"- {item}" for item in doing)
            )
        if next_items:
            updated = replace_section(
                updated,
                "Next",
                "\n".join(f"{index}. {item}" for index, item in enumerate(next_items, 1)),
            )
        new_evidence = [f"{utc_now()} — {item}" for item in evidence]
        new_evidence.extend(f"{utc_now()} — artifact: {item}" for item in artifacts)
        if new_evidence:
            previous = section(updated, "Recent Evidence", 8)
            merged = (new_evidence + previous)[:10]
            updated = replace_section(
                updated,
                "Recent Evidence",
                "\n".join(f"- {item}" for item in merged),
            )
        if knowledge:
            updated = replace_section(
                updated,
                "Knowledge State",
                update_knowledge(section_body(updated, "Knowledge State"), knowledge),
            )
        updated = update_frontmatter(
            updated,
            {
                "version": str(current_version + 1),
                "updated_at": date.today().isoformat(),
                "last_activity_at": utc_now(),
            },
        )
        atomic_write(lane.path, updated)
        cmd_views(root)
        result = cmd_check(root)
        if result:
            atomic_write(lane.path, original)
            cmd_views(root)
            print("ERROR: checkpoint rolled back after validation failure", file=sys.stderr)
            return result
        print(f"checkpointed {lane_id}: version {current_version + 1}")
        return 0
    finally:
        os.close(descriptor)
        lock.unlink(missing_ok=True)


def cmd_start(root: Path, query: str, lane_id: str, pull: bool) -> int:
    if pull and cmd_sync(root, "pull", ""):
        return 1
    lane, hits = select_lane(root, query=query, lane_id=lane_id)
    if not lane:
        print("adhoc")
        return 0
    checkpoint = section(lane.text, "Current Checkpoint", 1)
    if not checkpoint:
        checkpoint = section(lane.text, "Current Chapter", 1)
    print("# Session Brief")
    print(f"lane={lane.meta.get('id', lane.path.stem)}")
    print(f"file={lane.path.relative_to(root)}")
    print(f"version={lane.meta.get('version', 'unknown')}")
    print(f"last_activity={lane.meta.get('last_activity_at', lane.meta.get('updated_at', 'unknown'))}")
    if hits:
        print(f"matched={','.join(hits)}")
    print("\n## Current checkpoint")
    print(checkpoint[0] if checkpoint else "—")
    for heading in ("Doing", "Next", "Current Blockers"):
        print(f"\n## {heading}")
        items = section(lane.text, heading, 5)
        print("\n".join(f"- {item}" for item in items) if items else "—")
    print("\nRead PERSONAL.md and ROUTES.md, then only the selected lane and declared dependencies.")
    return 0


def run_git(repo: Path, arguments: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *arguments],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def git_top(root: Path) -> Path:
    result = run_git(root, ["rev-parse", "--show-toplevel"])
    return Path(result.stdout.strip()).resolve()


def cmd_sync(root: Path, mode: str, message: str) -> int:
    try:
        repo = git_top(root)
    except (subprocess.CalledProcessError, FileNotFoundError) as error:
        print(f"ERROR: PersonalOS is not inside a Git checkout: {error}", file=sys.stderr)
        return 1
    routes_meta, _ = parse_frontmatter(root / "ROUTES.md")
    expected = routes_meta.get("git_repository", "")
    try:
        remote = run_git(repo, ["remote", "get-url", "origin"]).stdout.strip()
    except subprocess.CalledProcessError:
        print("ERROR: Git remote 'origin' is not configured", file=sys.stderr)
        return 1
    if expected and expected.casefold() not in remote.casefold():
        print(
            f"ERROR: origin {remote} does not match canonical repository {expected}",
            file=sys.stderr,
        )
        return 1
    try:
        if mode == "pull":
            dirty = run_git(repo, ["status", "--porcelain"]).stdout.strip()
            if dirty:
                print(
                    "ERROR: worktree is not clean; checkpoint or commit local changes before pull",
                    file=sys.stderr,
                )
                return 1
            result = run_git(repo, ["pull", "--ff-only"])
            print(result.stdout.strip() or "already up to date")
            return cmd_check(root)

        cmd_views(root)
        if cmd_check(root):
            return 1
        relative_root = root.relative_to(repo).as_posix() or "."
        staged = run_git(repo, ["diff", "--cached", "--name-only"]).stdout.splitlines()
        outside = [
            path
            for path in staged
            if relative_root != "."
            and path != relative_root
            and not path.startswith(relative_root + "/")
        ]
        if outside:
            print(
                "ERROR: unrelated staged files exist: " + ", ".join(outside),
                file=sys.stderr,
            )
            return 1
        run_git(repo, ["add", "--", relative_root])
        if run_git(repo, ["diff", "--cached", "--quiet"], check=False).returncode == 0:
            print("nothing to push")
            return 0
        commit_message = message or f"Sync PersonalOS checkpoint {date.today().isoformat()}"
        run_git(repo, ["commit", "-m", commit_message])
        branch = run_git(repo, ["branch", "--show-current"]).stdout.strip()
        if not branch:
            print("ERROR: detached HEAD; switch to a branch before sync", file=sys.stderr)
            return 1
        pull_result = run_git(repo, ["pull", "--rebase", "origin", branch], check=False)
        if pull_result.returncode:
            print(pull_result.stdout + pull_result.stderr, file=sys.stderr)
            print("ERROR: rebase failed; resolve conflicts without force-pushing", file=sys.stderr)
            return 1
        push_result = run_git(repo, ["push", "-u", "origin", branch])
        print(push_result.stdout.strip() or push_result.stderr.strip())
        return 0
    except subprocess.CalledProcessError as error:
        print((error.stdout or "") + (error.stderr or ""), file=sys.stderr)
        return error.returncode or 1


def cmd_doctor(root: Path) -> int:
    result = cmd_check(root)
    print(f"root={root}")
    print(f"env_root={os.environ.get('PERSONAL_OS_ROOT', 'not set')}")
    pointer = Path.home() / ".personal-os-root"
    print(f"pointer={pointer.read_text(encoding='utf-8').strip() if pointer.is_file() else 'not installed'}")
    try:
        repo = git_top(root)
        print(f"git_root={repo}")
        print(f"branch={run_git(repo, ['branch', '--show-current']).stdout.strip() or 'detached'}")
        print(f"origin={run_git(repo, ['remote', 'get-url', 'origin']).stdout.strip()}")
        print(f"worktree={'clean' if not run_git(repo, ['status', '--porcelain']).stdout.strip() else 'dirty'}")
        print(f"head={run_git(repo, ['rev-parse', '--short', 'HEAD']).stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("git=unavailable")
        result = 1
    return result


def managed_agents_block(root: Path) -> str:
    return "\n".join(
        [
            MANAGED_BEGIN,
            "# PersonalOS global continuity",
            "",
            f"- Canonical local root: {root}",
            "- At the start of continuity work, read HANDOFF.md, PERSONAL.md, and ROUTES.md.",
            "- Route to exactly one lane and read only its declared dependencies.",
            "- Before local work, run personal_os.py start with --pull when the worktree is clean.",
            "- After a durable task, experiment, decision, blocker, or knowledge-stage change,",
            "  create a checkpoint and run personal_os.py sync --push.",
            "- Do not rely on chat memory when the canonical Git state is available.",
            MANAGED_END,
        ]
    )


def cmd_install(root: Path, home: Path) -> int:
    pointer = home / ".personal-os-root"
    atomic_write(pointer, str(root) + "\n")
    codex_home = Path(os.environ.get("CODEX_HOME", home / ".codex"))
    agents = codex_home / "AGENTS.md"
    existing = agents.read_text(encoding="utf-8") if agents.is_file() else ""
    block = managed_agents_block(root)
    pattern = re.compile(
        re.escape(MANAGED_BEGIN) + r".*?" + re.escape(MANAGED_END),
        re.DOTALL,
    )
    if pattern.search(existing):
        content = pattern.sub(block, existing)
    else:
        content = existing.rstrip() + ("\n\n" if existing.strip() else "") + block + "\n"
    atomic_write(agents, content.rstrip() + "\n")
    skill_source = root / "skill" / "personal-os" / "SKILL.md"
    skill_target = home / ".agents" / "skills" / "personal-os" / "SKILL.md"
    if not skill_source.is_file():
        print(f"ERROR: missing portable skill source: {skill_source}", file=sys.stderr)
        return 1
    skill_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(skill_source, skill_target)
    print(f"installed root pointer: {pointer}")
    print(f"installed global guidance: {agents}")
    print(f"installed global skill: {skill_target}")
    print("Restart Codex CLI or the IDE extension so it rebuilds the instruction chain.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("check", "dashboard", "views", "doctor"):
        item = sub.add_parser(command)
        item.add_argument("root", type=Path)
    route = sub.add_parser("route")
    route.add_argument("root", type=Path)
    route.add_argument("query")
    start = sub.add_parser("start", help="print the minimal context packet for one lane")
    start.add_argument("root", type=Path)
    start.add_argument("--query", default="")
    start.add_argument("--lane", default="")
    start.add_argument("--pull", action="store_true")
    checkpoint = sub.add_parser(
        "checkpoint", help="persist one compact semantic state change"
    )
    checkpoint.add_argument("root", type=Path)
    checkpoint.add_argument("--lane", required=True)
    checkpoint.add_argument("--summary", required=True)
    checkpoint.add_argument("--doing", action="append", default=[])
    checkpoint.add_argument("--next", action="append", default=[])
    checkpoint.add_argument("--evidence", action="append", default=[])
    checkpoint.add_argument("--artifact", action="append", default=[])
    checkpoint.add_argument(
        "--knowledge",
        action="append",
        default=[],
        metavar="TOPIC|STATE|EVIDENCE|NEXT",
    )
    checkpoint.add_argument("--base-version", type=int)
    sync = sub.add_parser("sync", help="pull or commit/rebase/push the canonical store")
    sync.add_argument("root", type=Path)
    sync_mode = sync.add_mutually_exclusive_group(required=True)
    sync_mode.add_argument("--pull", dest="mode", action="store_const", const="pull")
    sync_mode.add_argument("--push", dest="mode", action="store_const", const="push")
    sync.add_argument("--message", default="")
    install = sub.add_parser("install", help="install global Codex discovery pointers")
    install.add_argument("root", type=Path)
    install.add_argument("--home", type=Path, default=Path.home())
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = args.root.expanduser().resolve()
    if args.command == "check":
        return cmd_check(root)
    if args.command == "route":
        return cmd_route(root, args.query)
    if args.command in {"dashboard", "views"}:
        return cmd_dashboard(root)
    if args.command == "start":
        return cmd_start(root, args.query, args.lane, args.pull)
    if args.command == "checkpoint":
        try:
            return cmd_checkpoint(
                root,
                args.lane,
                args.summary,
                args.doing,
                args.next,
                args.evidence,
                args.artifact,
                args.knowledge,
                args.base_version,
            )
        except ValueError as error:
            print(f"ERROR: {error}", file=sys.stderr)
            return 1
    if args.command == "sync":
        return cmd_sync(root, args.mode, args.message)
    if args.command == "doctor":
        return cmd_doctor(root)
    if args.command == "install":
        return cmd_install(root, args.home.expanduser().resolve())
    return 2


if __name__ == "__main__":
    sys.exit(main())
