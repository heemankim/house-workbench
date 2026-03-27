"""Frontmatter parsing and validation utilities for workbench test harness."""

from __future__ import annotations

from pathlib import Path

import yaml


# --- Schema constants (from vault-conventions) ---

SUBTASK_STATUSES = {"pending", "in_progress", "done", "blocked", "skipped", "cancelled"}
SUBTASK_TYPES = {"code", "ops", "wait", "doc", "research"}
TASK_TYPES = {"code", "ops"}


def parse_frontmatter(file_path: Path) -> tuple[dict, str]:
    """Parse YAML frontmatter from a markdown file.

    Returns (frontmatter_dict, body_text).
    Raises ValueError if the file has no valid frontmatter.
    """
    text = file_path.read_text(encoding="utf-8")

    if not text.startswith("---"):
        raise ValueError(f"No frontmatter found in {file_path}")

    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"Malformed frontmatter in {file_path}")

    fm_raw = parts[1].strip()
    body = parts[2].lstrip("\n")

    data = yaml.safe_load(fm_raw) if fm_raw else {}
    if data is None:
        data = {}

    return data, body


def validate_fields(data: dict, required: list[str], *, enums: dict[str, set] | None = None) -> list[str]:
    """Validate required fields exist and enum values match.

    Returns a list of violation messages (empty = valid).
    """
    violations: list[str] = []

    for field in required:
        if field not in data:
            violations.append(f"missing required field: {field}")

    if enums:
        for field, allowed in enums.items():
            if field in data and data[field] not in allowed:
                violations.append(f"{field}={data[field]!r} not in {allowed}")

    return violations


def validate_task_frontmatter(data: dict) -> list[str]:
    """Validate TASK.md frontmatter against vault-conventions schema."""
    violations = validate_fields(
        data,
        required=["type", "created"],
        enums={"type": TASK_TYPES},
    )
    return violations


def validate_subtask_frontmatter(data: dict) -> list[str]:
    """Validate SUBTASK.md frontmatter against vault-conventions schema."""
    violations = validate_fields(
        data,
        required=["type", "status", "subtask_type", "depends", "created"],
        enums={
            "status": SUBTASK_STATUSES,
            "subtask_type": SUBTASK_TYPES,
        },
    )

    if data.get("type") != "subtask":
        violations.append(f"type must be 'subtask', got {data.get('type')!r}")

    # code type requires non-empty repo and branch
    if data.get("subtask_type") == "code":
        if not data.get("repo"):
            violations.append("code subtask requires non-empty 'repo'")
        if not data.get("branch"):
            violations.append("code subtask requires non-empty 'branch'")

    return violations


def validate_skill_frontmatter(data: dict) -> list[str]:
    """Validate SKILL.md frontmatter."""
    violations = validate_fields(data, required=["name", "description"])

    metadata = data.get("metadata", {})
    if not isinstance(metadata, dict) or "version" not in metadata:
        violations.append("missing metadata.version")

    return violations


def write_frontmatter(file_path: Path, data: dict, body: str = "") -> None:
    """Write a markdown file with YAML frontmatter."""
    fm_str = yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False).rstrip("\n")
    content = f"---\n{fm_str}\n---\n\n{body}" if body else f"---\n{fm_str}\n---\n"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
