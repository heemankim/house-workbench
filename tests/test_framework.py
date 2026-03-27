"""Tests for the test framework itself — frontmatter parsing, validation, and workspace factory."""

import os
from pathlib import Path

import pytest

from tests.helpers.frontmatter import (
    SUBTASK_STATUSES,
    SUBTASK_TYPES,
    TASK_TYPES,
    parse_frontmatter,
    validate_fields,
    validate_skill_frontmatter,
    validate_subtask_frontmatter,
    validate_task_frontmatter,
    write_frontmatter,
)
from tests.helpers.workspace import WorkspaceFactory


# ──────────────────────────────────────────────
# parse_frontmatter
# ──────────────────────────────────────────────


class TestParseFrontmatter:
    def test_valid_frontmatter(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("---\ntype: code\ncreated: '2026-01-15'\n---\n\n# Hello\n")
        data, body = parse_frontmatter(f)
        assert data["type"] == "code"
        assert data["created"] == "2026-01-15"
        assert "# Hello" in body

    def test_empty_frontmatter(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("---\n---\n\nBody text\n")
        data, body = parse_frontmatter(f)
        assert data == {}
        assert "Body text" in body

    def test_no_frontmatter_raises(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("# Just a heading\n")
        with pytest.raises(ValueError, match="No frontmatter"):
            parse_frontmatter(f)

    def test_malformed_frontmatter_raises(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("---\ntype: code\n")
        with pytest.raises(ValueError, match="Malformed frontmatter"):
            parse_frontmatter(f)

    def test_frontmatter_with_list_values(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("---\ndepends:\n- 1\n- 2\ntags: [a, b]\n---\n\n")
        data, _ = parse_frontmatter(f)
        assert data["depends"] == [1, 2]
        assert data["tags"] == ["a", "b"]


# ──────────────────────────────────────────────
# validate_fields
# ──────────────────────────────────────────────


class TestValidateFields:
    def test_all_required_present(self):
        data = {"type": "code", "created": "2026-01-15"}
        assert validate_fields(data, ["type", "created"]) == []

    def test_missing_required(self):
        data = {"type": "code"}
        violations = validate_fields(data, ["type", "created"])
        assert len(violations) == 1
        assert "created" in violations[0]

    def test_enum_valid(self):
        data = {"status": "pending"}
        assert validate_fields(data, ["status"], enums={"status": SUBTASK_STATUSES}) == []

    def test_enum_invalid(self):
        data = {"status": "invalid"}
        violations = validate_fields(data, ["status"], enums={"status": SUBTASK_STATUSES})
        assert len(violations) == 1
        assert "invalid" in violations[0]


# ──────────────────────────────────────────────
# validate_task_frontmatter
# ──────────────────────────────────────────────


class TestValidateTaskFrontmatter:
    def test_valid_task(self):
        data = {"type": "code", "created": "2026-01-15"}
        assert validate_task_frontmatter(data) == []

    def test_invalid_type(self):
        data = {"type": "invalid", "created": "2026-01-15"}
        violations = validate_task_frontmatter(data)
        assert any("type" in v for v in violations)

    def test_missing_created(self):
        data = {"type": "code"}
        violations = validate_task_frontmatter(data)
        assert any("created" in v for v in violations)


# ──────────────────────────────────────────────
# validate_subtask_frontmatter
# ──────────────────────────────────────────────


class TestValidateSubtaskFrontmatter:
    def test_valid_code_subtask(self):
        data = {
            "type": "subtask",
            "status": "pending",
            "subtask_type": "code",
            "depends": [],
            "repo": "workbench",
            "branch": "feature/test",
            "created": "2026-01-15",
        }
        assert validate_subtask_frontmatter(data) == []

    def test_valid_research_subtask(self):
        data = {
            "type": "subtask",
            "status": "pending",
            "subtask_type": "research",
            "depends": [],
            "repo": "",
            "branch": "",
            "created": "2026-01-15",
        }
        assert validate_subtask_frontmatter(data) == []

    def test_code_missing_repo(self):
        data = {
            "type": "subtask",
            "status": "pending",
            "subtask_type": "code",
            "depends": [],
            "repo": "",
            "branch": "feature/test",
            "created": "2026-01-15",
        }
        violations = validate_subtask_frontmatter(data)
        assert any("repo" in v for v in violations)

    def test_invalid_status(self):
        data = {
            "type": "subtask",
            "status": "running",
            "subtask_type": "code",
            "depends": [],
            "repo": "workbench",
            "branch": "feature/test",
            "created": "2026-01-15",
        }
        violations = validate_subtask_frontmatter(data)
        assert any("status" in v for v in violations)

    def test_wrong_type_field(self):
        data = {
            "type": "task",
            "status": "pending",
            "subtask_type": "code",
            "depends": [],
            "repo": "workbench",
            "branch": "feature/test",
            "created": "2026-01-15",
        }
        violations = validate_subtask_frontmatter(data)
        assert any("subtask" in v for v in violations)


# ──────────────────────────────────────────────
# validate_skill_frontmatter
# ──────────────────────────────────────────────


class TestValidateSkillFrontmatter:
    def test_valid_skill(self):
        data = {
            "name": "wb-start",
            "description": "Start a task",
            "metadata": {"version": "2.1.0"},
        }
        assert validate_skill_frontmatter(data) == []

    def test_missing_metadata_version(self):
        data = {
            "name": "wb-start",
            "description": "Start a task",
            "metadata": {},
        }
        violations = validate_skill_frontmatter(data)
        assert any("version" in v for v in violations)

    def test_no_metadata_at_all(self):
        data = {"name": "wb-start", "description": "Start a task"}
        violations = validate_skill_frontmatter(data)
        assert any("version" in v for v in violations)


# ──────────────────────────────────────────────
# write_frontmatter
# ──────────────────────────────────────────────


class TestWriteFrontmatter:
    def test_roundtrip(self, tmp_path):
        f = tmp_path / "test.md"
        data = {"type": "code", "created": "2026-01-15"}
        write_frontmatter(f, data, body="# Hello\n")

        parsed_data, parsed_body = parse_frontmatter(f)
        assert parsed_data["type"] == "code"
        assert "# Hello" in parsed_body

    def test_creates_parent_dirs(self, tmp_path):
        f = tmp_path / "deep" / "nested" / "test.md"
        write_frontmatter(f, {"type": "code"})
        assert f.exists()


# ──────────────────────────────────────────────
# WorkspaceFactory.create_minimal
# ──────────────────────────────────────────────


class TestCreateMinimal:
    def test_config_exists(self, minimal_workspace):
        assert (minimal_workspace / "config.json").exists()

    def test_vault_para_structure(self, minimal_workspace):
        vault = minimal_workspace / "obsidian"
        for d in ["0-Inbox", "1-Projects", "3-Resources", "4-Archives"]:
            assert (vault / d).is_dir(), f"Missing PARA directory: {d}"

    def test_data_tasks_exists(self, minimal_workspace):
        assert (minimal_workspace / "data" / "tasks").is_dir()


# ──────────────────────────────────────────────
# WorkspaceFactory.create_from_fixture
# ──────────────────────────────────────────────


class TestCreateFromFixture:
    def test_after_wb_start_has_vault_task(self, workspace_after_start):
        task_md = workspace_after_start / "obsidian" / "1-Projects" / "sample-task" / "TASK.md"
        assert task_md.exists()
        data, body = parse_frontmatter(task_md)
        assert data["type"] == "code"
        assert "01. first-step" in body

    def test_after_wb_start_has_data_pointer(self, workspace_after_start):
        pointer = workspace_after_start / "data" / "tasks" / "sample-task" / "TASK.md"
        assert pointer.exists()
        data, _ = parse_frontmatter(pointer)
        assert "vaultPath" in data

    def test_after_wb_start_subtask_pending(self, workspace_after_start):
        st = workspace_after_start / "obsidian" / "1-Projects" / "sample-task" / "subtasks" / "01-first-step" / "SUBTASK.md"
        data, _ = parse_frontmatter(st)
        assert data["status"] == "pending"

    def test_after_wb_done_subtask_completed(self, workspace_after_done):
        st = workspace_after_done / "obsidian" / "1-Projects" / "sample-task" / "subtasks" / "01-first-step" / "SUBTASK.md"
        data, _ = parse_frontmatter(st)
        assert data["status"] == "done"
        assert "completed" in data

    def test_after_wb_done_checklist_marked(self, workspace_after_done):
        task_md = workspace_after_done / "obsidian" / "1-Projects" / "sample-task" / "TASK.md"
        _, body = parse_frontmatter(task_md)
        assert "[x]" in body
        assert "01. first-step" in body

    def test_fixture_not_found_raises(self, workspace_factory):
        with pytest.raises(FileNotFoundError):
            workspace_factory.create_from_fixture("nonexistent")


# ──────────────────────────────────────────────
# WorkspaceFactory.create_after_wb_start (programmatic)
# ──────────────────────────────────────────────


class TestCreateAfterWbStart:
    @pytest.fixture
    def ws(self, workspace_factory):
        return workspace_factory.create_after_wb_start(
            "my-task",
            [
                {"name": "setup", "subtask_type": "research"},
                {"name": "implement", "subtask_type": "code", "repo": "myrepo", "branch": "feature/my-task/implement", "depends": [1]},
            ],
            today="2026-03-20",
        )

    def test_vault_task_md(self, ws):
        task_md = ws / "obsidian" / "1-Projects" / "my-task" / "TASK.md"
        assert task_md.exists()
        data, body = parse_frontmatter(task_md)
        assert data["type"] == "code"
        assert data["created"] == "2026-03-20"
        assert "01. setup" in body
        assert "02. implement" in body

    def test_vault_subtask_md(self, ws):
        st = ws / "obsidian" / "1-Projects" / "my-task" / "subtasks" / "01-setup" / "SUBTASK.md"
        assert st.exists()
        data, _ = parse_frontmatter(st)
        assert data["status"] == "pending"
        assert data["subtask_type"] == "research"

    def test_vault_subtask_depends(self, ws):
        st = ws / "obsidian" / "1-Projects" / "my-task" / "subtasks" / "02-implement" / "SUBTASK.md"
        data, _ = parse_frontmatter(st)
        assert data["depends"] == [1]
        assert data["repo"] == "myrepo"

    def test_data_tasks_pointer(self, ws):
        pointer = ws / "data" / "tasks" / "my-task" / "TASK.md"
        assert pointer.exists()
        data, _ = parse_frontmatter(pointer)
        assert data["vaultPath"] == "1-Projects/my-task"

    def test_data_tasks_claude_md(self, ws):
        assert (ws / "data" / "tasks" / "my-task" / "CLAUDE.md").exists()

    def test_data_subtask_mirrors(self, ws):
        for slug in ["01-setup", "02-implement"]:
            st = ws / "data" / "tasks" / "my-task" / "subtasks" / slug / "SUBTASK.md"
            assert st.exists()

    def test_history_dir(self, ws):
        assert (ws / "data" / "tasks" / "my-task" / "history").is_dir()

    def test_claude_symlink(self, ws):
        link = ws / "data" / "tasks" / "my-task" / ".claude"
        assert os.path.islink(str(link))
