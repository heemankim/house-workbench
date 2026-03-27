"""E2E scenario tests verifying structural output of wb-start / wb-done skills.

These tests validate the *structure* of skill output (file existence, frontmatter
schema, state consistency) — not AI-generated content.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests.helpers.frontmatter import (
    parse_frontmatter,
    validate_subtask_frontmatter,
    validate_task_frontmatter,
    write_frontmatter,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _vault_task_dir(ws: Path, task_name: str = "sample-task") -> Path:
    return ws / "obsidian" / "1-Projects" / task_name


def _data_task_dir(ws: Path, task_name: str = "sample-task") -> Path:
    return ws / "data" / "tasks" / task_name


def _parse_checklist(body: str) -> list[dict]:
    """Parse checklist lines from TASK.md body.

    Returns list of dicts: {checked: bool, num: str, name: str, link: str}
    """
    pattern = re.compile(
        r"^- \[(?P<check>[ x])\] (?P<num>\d+)\. (?P<name>[^ ]+) -> \[\[(?P<link>[^\]]+)\]\]"
    )
    items = []
    for line in body.splitlines():
        m = pattern.match(line.strip())
        if m:
            items.append({
                "checked": m.group("check") == "x",
                "num": m.group("num"),
                "name": m.group("name"),
                "link": m.group("link"),
            })
    return items


def _list_subtask_dirs(task_dir: Path) -> list[Path]:
    """Return sorted list of subtask directories under task_dir/subtasks/."""
    subtasks_dir = task_dir / "subtasks"
    if not subtasks_dir.exists():
        return []
    return sorted(d for d in subtasks_dir.iterdir() if d.is_dir())


# ===========================================================================
# 1. wb-start scenario
# ===========================================================================

class TestWbStartScenario:
    """Verify workspace structure after wb-start has run."""

    def test_vault_task_md_exists(self, workspace_after_start):
        ws = workspace_after_start
        task_md = _vault_task_dir(ws) / "TASK.md"
        assert task_md.exists(), "vault TASK.md must exist after wb-start"

    def test_vault_task_frontmatter_valid(self, workspace_after_start):
        ws = workspace_after_start
        fm, _ = parse_frontmatter(_vault_task_dir(ws) / "TASK.md")
        violations = validate_task_frontmatter(fm)
        assert violations == [], f"vault TASK.md frontmatter violations: {violations}"

    def test_vault_task_frontmatter_fields(self, workspace_after_start):
        ws = workspace_after_start
        fm, _ = parse_frontmatter(_vault_task_dir(ws) / "TASK.md")
        assert "type" in fm
        assert "created" in fm

    def test_vault_task_checklist_format(self, workspace_after_start):
        ws = workspace_after_start
        _, body = parse_frontmatter(_vault_task_dir(ws) / "TASK.md")
        items = _parse_checklist(body)
        assert len(items) == 2, f"Expected 2 checklist items, got {len(items)}"
        # All unchecked after start
        for item in items:
            assert not item["checked"], f"Subtask {item['num']} should be unchecked after start"

    def test_vault_task_checklist_links(self, workspace_after_start):
        ws = workspace_after_start
        _, body = parse_frontmatter(_vault_task_dir(ws) / "TASK.md")
        items = _parse_checklist(body)
        for item in items:
            link_target = _vault_task_dir(ws) / item["link"] / "SUBTASK.md"
            assert link_target.exists(), f"Checklist link target missing: {item['link']}"

    def test_vault_subtask_frontmatter_valid(self, workspace_after_start):
        ws = workspace_after_start
        for sub_dir in _list_subtask_dirs(_vault_task_dir(ws)):
            sub_md = sub_dir / "SUBTASK.md"
            assert sub_md.exists(), f"SUBTASK.md missing in {sub_dir.name}"
            fm, _ = parse_frontmatter(sub_md)
            violations = validate_subtask_frontmatter(fm)
            assert violations == [], f"{sub_dir.name} violations: {violations}"

    def test_vault_subtasks_all_pending(self, workspace_after_start):
        ws = workspace_after_start
        for sub_dir in _list_subtask_dirs(_vault_task_dir(ws)):
            fm, _ = parse_frontmatter(sub_dir / "SUBTASK.md")
            assert fm["status"] == "pending", f"{sub_dir.name} should be pending"

    def test_data_task_pointer_exists(self, workspace_after_start):
        ws = workspace_after_start
        task_md = _data_task_dir(ws) / "TASK.md"
        assert task_md.exists(), "data/tasks TASK.md pointer must exist"
        fm, _ = parse_frontmatter(task_md)
        assert "vaultPath" in fm, "data TASK.md must have vaultPath"

    def test_data_claude_md_exists(self, workspace_after_start):
        ws = workspace_after_start
        claude_md = _data_task_dir(ws) / "CLAUDE.md"
        assert claude_md.exists(), "data/tasks CLAUDE.md must exist"

    def test_data_subtask_dirs_mirror_vault(self, workspace_after_start):
        ws = workspace_after_start
        vault_subs = _list_subtask_dirs(_vault_task_dir(ws))
        data_subs = _list_subtask_dirs(_data_task_dir(ws))
        vault_names = {d.name for d in vault_subs}
        data_names = {d.name for d in data_subs}
        assert vault_names == data_names, (
            f"data/tasks subtask dirs must mirror vault: {data_names} != {vault_names}"
        )


# ===========================================================================
# 2. wb-done scenario
# ===========================================================================

class TestWbDoneScenario:
    """Verify workspace structure after wb-done has completed subtask 01."""

    def test_completed_subtask_status_done(self, workspace_after_done):
        ws = workspace_after_done
        fm, _ = parse_frontmatter(
            _vault_task_dir(ws) / "subtasks" / "01-first-step" / "SUBTASK.md"
        )
        assert fm["status"] == "done"

    def test_completed_subtask_has_completed_field(self, workspace_after_done):
        ws = workspace_after_done
        fm, _ = parse_frontmatter(
            _vault_task_dir(ws) / "subtasks" / "01-first-step" / "SUBTASK.md"
        )
        assert "completed" in fm, "Done subtask must have 'completed' date field"

    def test_task_checklist_marked(self, workspace_after_done):
        ws = workspace_after_done
        _, body = parse_frontmatter(_vault_task_dir(ws) / "TASK.md")
        items = _parse_checklist(body)
        assert len(items) == 2
        assert items[0]["checked"], "Subtask 01 should be checked in TASK.md"
        assert not items[1]["checked"], "Subtask 02 should remain unchecked"

    def test_remaining_subtask_still_pending(self, workspace_after_done):
        ws = workspace_after_done
        fm, _ = parse_frontmatter(
            _vault_task_dir(ws) / "subtasks" / "02-second-step" / "SUBTASK.md"
        )
        assert fm["status"] == "pending"

    def test_vault_data_consistency_for_done_subtask(self, workspace_after_done):
        ws = workspace_after_done
        vault_fm, _ = parse_frontmatter(
            _vault_task_dir(ws) / "subtasks" / "01-first-step" / "SUBTASK.md"
        )
        data_fm, _ = parse_frontmatter(
            _data_task_dir(ws) / "subtasks" / "01-first-step" / "SUBTASK.md"
        )
        assert vault_fm["status"] == data_fm["status"] == "done"
        assert "completed" in data_fm, "data SUBTASK.md must also have 'completed' field"

    def test_vault_data_consistency_for_pending_subtask(self, workspace_after_done):
        ws = workspace_after_done
        vault_fm, _ = parse_frontmatter(
            _vault_task_dir(ws) / "subtasks" / "02-second-step" / "SUBTASK.md"
        )
        data_fm, _ = parse_frontmatter(
            _data_task_dir(ws) / "subtasks" / "02-second-step" / "SUBTASK.md"
        )
        assert vault_fm["status"] == data_fm["status"] == "pending"


# ===========================================================================
# 3. State transition tests
# ===========================================================================

class TestStateTransitions:
    """Programmatic state transition tests using WorkspaceFactory."""

    @pytest.fixture
    def ws_three_subtasks(self, workspace_factory):
        """Create a workspace with 3 subtasks: research, code, doc."""
        subtasks = [
            {
                "name": "research",
                "subtask_type": "research",
                "repo": "",
                "branch": "",
                "depends": [],
            },
            {
                "name": "code",
                "subtask_type": "code",
                "repo": "workbench",
                "branch": "feature/test/code",
                "depends": [1],
            },
            {
                "name": "doc",
                "subtask_type": "doc",
                "repo": "",
                "branch": "",
                "depends": [1, 2],
            },
        ]
        return workspace_factory.create_after_wb_start(
            "transition-task", subtasks, today="2026-01-20"
        )

    def test_all_start_pending(self, ws_three_subtasks):
        ws = ws_three_subtasks
        vault_dir = _vault_task_dir(ws, "transition-task")
        for sub_dir in _list_subtask_dirs(vault_dir):
            fm, _ = parse_frontmatter(sub_dir / "SUBTASK.md")
            assert fm["status"] == "pending", f"{sub_dir.name} should start as pending"

    def test_three_subtasks_created(self, ws_three_subtasks):
        ws = ws_three_subtasks
        vault_dir = _vault_task_dir(ws, "transition-task")
        subs = _list_subtask_dirs(vault_dir)
        assert len(subs) == 3

    def test_checklist_has_three_items(self, ws_three_subtasks):
        ws = ws_three_subtasks
        vault_dir = _vault_task_dir(ws, "transition-task")
        _, body = parse_frontmatter(vault_dir / "TASK.md")
        items = _parse_checklist(body)
        assert len(items) == 3

    def test_modify_subtask_to_done_updates_frontmatter(self, ws_three_subtasks):
        """Simulate wb-done on subtask 01 by updating frontmatter directly."""
        ws = ws_three_subtasks
        vault_sub = _vault_task_dir(ws, "transition-task") / "subtasks" / "01-research" / "SUBTASK.md"
        fm, body = parse_frontmatter(vault_sub)

        # Transition to done
        fm["status"] = "done"
        fm["completed"] = "2026-01-21"
        write_frontmatter(vault_sub, fm, body=body)

        # Re-read and verify
        fm2, _ = parse_frontmatter(vault_sub)
        assert fm2["status"] == "done"
        assert fm2["completed"] == "2026-01-21"

    def test_checklist_consistency_after_manual_done(self, ws_three_subtasks):
        """After marking subtask 01 done, update checklist and verify consistency."""
        ws = ws_three_subtasks
        vault_dir = _vault_task_dir(ws, "transition-task")
        task_md = vault_dir / "TASK.md"

        # Update subtask 01 to done
        vault_sub = vault_dir / "subtasks" / "01-research" / "SUBTASK.md"
        fm, body = parse_frontmatter(vault_sub)
        fm["status"] = "done"
        fm["completed"] = "2026-01-21"
        write_frontmatter(vault_sub, fm, body=body)

        # Update TASK.md checklist (simulate what wb-done does)
        task_fm, task_body = parse_frontmatter(task_md)
        updated_body = task_body.replace(
            "- [ ] 01. research",
            "- [x] 01. research",
        )
        write_frontmatter(task_md, task_fm, body=updated_body)

        # Verify checklist now shows 01 as done
        _, new_body = parse_frontmatter(task_md)
        items = _parse_checklist(new_body)
        assert items[0]["checked"], "Subtask 01 should be checked after done"
        assert not items[1]["checked"], "Subtask 02 should remain unchecked"
        assert not items[2]["checked"], "Subtask 03 should remain unchecked"

    def test_depends_field_for_subtask_03(self, ws_three_subtasks):
        """Subtask 03 (doc) depends on [1, 2] — verify the depends field."""
        ws = ws_three_subtasks
        vault_sub = _vault_task_dir(ws, "transition-task") / "subtasks" / "03-doc" / "SUBTASK.md"
        fm, _ = parse_frontmatter(vault_sub)
        assert fm["depends"] == [1, 2], f"Expected depends=[1,2], got {fm['depends']}"

    def test_depends_field_for_subtask_02(self, ws_three_subtasks):
        """Subtask 02 (code) depends on [1]."""
        ws = ws_three_subtasks
        vault_sub = _vault_task_dir(ws, "transition-task") / "subtasks" / "02-code" / "SUBTASK.md"
        fm, _ = parse_frontmatter(vault_sub)
        assert fm["depends"] == [1]

    def test_subtask_types_correct(self, ws_three_subtasks):
        ws = ws_three_subtasks
        vault_dir = _vault_task_dir(ws, "transition-task")
        expected = {"01-research": "research", "02-code": "code", "03-doc": "doc"}
        for sub_dir in _list_subtask_dirs(vault_dir):
            fm, _ = parse_frontmatter(sub_dir / "SUBTASK.md")
            assert fm["subtask_type"] == expected[sub_dir.name], (
                f"{sub_dir.name}: expected {expected[sub_dir.name]}, got {fm['subtask_type']}"
            )


# ===========================================================================
# 4. Vault-first consistency
# ===========================================================================

class TestVaultFirstConsistency:
    """Verify vault-first principle: every vault subtask has a data mirror and vice versa."""

    def test_every_vault_subtask_has_data_mirror(self, workspace_after_start):
        ws = workspace_after_start
        vault_subs = _list_subtask_dirs(_vault_task_dir(ws))
        for vault_sub in vault_subs:
            data_sub = _data_task_dir(ws) / "subtasks" / vault_sub.name / "SUBTASK.md"
            assert data_sub.exists(), (
                f"Vault subtask {vault_sub.name} has no data mirror at {data_sub}"
            )

    def test_every_data_subtask_has_vault_source(self, workspace_after_start):
        ws = workspace_after_start
        data_subs = _list_subtask_dirs(_data_task_dir(ws))
        for data_sub in data_subs:
            vault_sub = _vault_task_dir(ws) / "subtasks" / data_sub.name / "SUBTASK.md"
            assert vault_sub.exists(), (
                f"Data subtask {data_sub.name} has no vault source at {vault_sub}"
            )

    def test_status_matches_between_vault_and_data(self, workspace_after_start):
        ws = workspace_after_start
        for sub_dir in _list_subtask_dirs(_vault_task_dir(ws)):
            vault_fm, _ = parse_frontmatter(sub_dir / "SUBTASK.md")
            data_fm, _ = parse_frontmatter(
                _data_task_dir(ws) / "subtasks" / sub_dir.name / "SUBTASK.md"
            )
            assert vault_fm["status"] == data_fm["status"], (
                f"{sub_dir.name}: vault status={vault_fm['status']} != data status={data_fm['status']}"
            )

    def test_checklist_count_matches_subtask_dirs(self, workspace_after_start):
        ws = workspace_after_start
        _, body = parse_frontmatter(_vault_task_dir(ws) / "TASK.md")
        items = _parse_checklist(body)
        vault_subs = _list_subtask_dirs(_vault_task_dir(ws))
        assert len(items) == len(vault_subs), (
            f"Checklist has {len(items)} items but {len(vault_subs)} subtask dirs exist"
        )

    def test_vault_data_consistency_after_done(self, workspace_after_done):
        """In after-wb-done fixture, vault and data statuses must still match."""
        ws = workspace_after_done
        for sub_dir in _list_subtask_dirs(_vault_task_dir(ws)):
            vault_fm, _ = parse_frontmatter(sub_dir / "SUBTASK.md")
            data_fm, _ = parse_frontmatter(
                _data_task_dir(ws) / "subtasks" / sub_dir.name / "SUBTASK.md"
            )
            assert vault_fm["status"] == data_fm["status"], (
                f"{sub_dir.name}: vault={vault_fm['status']} != data={data_fm['status']}"
            )

    def test_programmatic_workspace_consistency(self, workspace_factory):
        """Programmatically created workspace also satisfies vault-first consistency."""
        subtasks = [
            {"name": "alpha", "subtask_type": "research", "depends": []},
            {"name": "beta", "subtask_type": "code", "repo": "test", "branch": "feat/beta", "depends": [1]},
        ]
        ws = workspace_factory.create_after_wb_start("consistency-check", subtasks)
        vault_dir = _vault_task_dir(ws, "consistency-check")
        data_dir = _data_task_dir(ws, "consistency-check")

        vault_subs = _list_subtask_dirs(vault_dir)
        data_subs = _list_subtask_dirs(data_dir)

        assert {d.name for d in vault_subs} == {d.name for d in data_subs}

        for sub_dir in vault_subs:
            vault_fm, _ = parse_frontmatter(sub_dir / "SUBTASK.md")
            data_fm, _ = parse_frontmatter(
                data_dir / "subtasks" / sub_dir.name / "SUBTASK.md"
            )
            assert vault_fm["status"] == data_fm["status"]
