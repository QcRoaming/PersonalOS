#!/usr/bin/env python3
"""Validate, route, and summarize a lightweight PersonalOS directory."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from experiment_registry import validate_registry_files


REQUIRED_ROOT_FILES = ("PERSONAL.md", "ROUTES.md", "AGENTS.md")
REQUIRED_META = ("id", "role", "priority", "status", "version", "keywords")


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
        f"- Last generated: {date.today().isoformat()}",
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("check", "dashboard"):
        item = sub.add_parser(command)
        item.add_argument("root", type=Path)
    route = sub.add_parser("route")
    route.add_argument("root", type=Path)
    route.add_argument("query")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = args.root.expanduser().resolve()
    if args.command == "check":
        return cmd_check(root)
    if args.command == "route":
        return cmd_route(root, args.query)
    if args.command == "dashboard":
        return cmd_dashboard(root)
    return 2


if __name__ == "__main__":
    sys.exit(main())
