"""Workspace fixture factory for workbench test harness."""

from __future__ import annotations

import json
import os
import shutil
from datetime import date
from pathlib import Path

from .frontmatter import write_frontmatter

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


class WorkspaceFactory:
    """Creates isolated test workspaces under a given base directory (typically tmp_path)."""

    def __init__(self, base_dir: Path):
        self.base = base_dir

    def create_minimal(self) -> Path:
        """Create a minimal workspace with config.json and empty PARA vault."""
        ws = self.base / "workspace"
        ws.mkdir(exist_ok=True)

        # config.json
        config = {
            "name": "test-workspace",
            "vault": "obsidian",
            "defaults": {"baseBranch": "main", "branchPrefix": "feature/"},
        }
        (ws / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")

        # PARA vault stub
        for d in ["0-Inbox", "1-Projects", "3-Resources", "4-Archives"]:
            (ws / "obsidian" / d).mkdir(parents=True, exist_ok=True)

        # data/tasks stub
        (ws / "data" / "tasks").mkdir(parents=True, exist_ok=True)

        return ws

    def create_from_fixture(self, fixture_name: str) -> Path:
        """Copy a static fixture into a fresh workspace directory."""
        src = FIXTURES_DIR / fixture_name
        if not src.exists():
            raise FileNotFoundError(f"Fixture not found: {src}")
        ws = self.base / fixture_name
        shutil.copytree(src, ws, symlinks=True)
        return ws

    def create_after_wb_start(
        self,
        task_name: str,
        subtasks: list[dict],
        *,
        task_type: str = "code",
        today: str | None = None,
    ) -> Path:
        """Programmatically create a workspace that looks like wb-start just ran.

        Args:
            task_name: e.g. "sample-task"
            subtasks: list of dicts with keys: name, subtask_type, repo, branch, depends
            task_type: "code" or "ops"
            today: override date string (YYYY-MM-DD)
        """
        today = today or date.today().isoformat()
        ws = self.create_minimal()

        # --- Vault side (SSoT) ---
        vault_task_dir = ws / "obsidian" / "1-Projects" / task_name
        vault_subtasks_dir = vault_task_dir / "subtasks"

        # vault TASK.md
        checklist_lines = []
        for i, st in enumerate(subtasks, 1):
            num = f"{i:02d}"
            slug = f"{num}-{st['name']}"
            checklist_lines.append(f"- [ ] {num}. {st['name']} -> [[subtasks/{slug}]]")

        write_frontmatter(
            vault_task_dir / "TASK.md",
            {"type": task_type, "created": today},
            body=f"# {task_name}\n\n## 서브태스크\n" + "\n".join(checklist_lines) + "\n",
        )

        # vault SUBTASK.md files
        for i, st in enumerate(subtasks, 1):
            num = f"{i:02d}"
            slug = f"{num}-{st['name']}"
            fm = {
                "type": "subtask",
                "status": "pending",
                "subtask_type": st.get("subtask_type", "code"),
                "depends": st.get("depends", []),
                "repo": st.get("repo", ""),
                "branch": st.get("branch", ""),
                "created": today,
            }
            body = (
                f"# {num}. {st['name']}\n\n"
                "## 목표\n\n"
                "## 분석\n> wb-next 시 subtask-analyzer가 채웁니다.\n\n"
                "## 작업 체크리스트\n> wb-next 시 자동으로 생성됩니다.\n\n"
                "## 의사결정\n\n"
                f"## 히스토리\n- [{today}] 생성\n"
            )
            write_frontmatter(vault_subtasks_dir / slug / "SUBTASK.md", fm, body=body)

        # --- data/tasks side (pointer) ---
        data_task_dir = ws / "data" / "tasks" / task_name
        write_frontmatter(
            data_task_dir / "TASK.md",
            {"type": task_type, "vaultPath": f"1-Projects/{task_name}"},
        )

        # data/tasks CLAUDE.md stub
        (data_task_dir / "CLAUDE.md").write_text(
            f"# Task: {task_name}\ntype: {task_type}\n",
            encoding="utf-8",
        )

        # data/tasks subtask mirrors
        for i, st in enumerate(subtasks, 1):
            num = f"{i:02d}"
            slug = f"{num}-{st['name']}"
            sub_dir = data_task_dir / "subtasks" / slug
            fm = {
                "type": "subtask",
                "status": "pending",
                "subtask_type": st.get("subtask_type", "code"),
                "depends": st.get("depends", []),
                "repo": st.get("repo", ""),
                "branch": st.get("branch", ""),
                "created": today,
            }
            write_frontmatter(sub_dir / "SUBTASK.md", fm)

        # history directory
        (data_task_dir / "history").mkdir(parents=True, exist_ok=True)

        # .claude symlink (dangling in test env, but islink() still works)
        claude_link = data_task_dir / ".claude"
        if not claude_link.exists() and not os.path.islink(str(claude_link)):
            os.symlink("../../../.claude", str(claude_link))

        return ws

    def add_task(self, ws: Path, task_name: str, task_type: str, subtasks: list[dict]) -> Path:
        """Add a task to an existing workspace. Returns the vault task directory."""
        today = date.today().isoformat()
        vault_task_dir = ws / "obsidian" / "1-Projects" / task_name

        checklist_lines = []
        for i, st in enumerate(subtasks, 1):
            num = f"{i:02d}"
            slug = f"{num}-{st['name']}"
            checklist_lines.append(f"- [ ] {num}. {st['name']} -> [[subtasks/{slug}]]")

        write_frontmatter(
            vault_task_dir / "TASK.md",
            {"type": task_type, "created": today},
            body=f"# {task_name}\n\n## 서브태스크\n" + "\n".join(checklist_lines) + "\n",
        )

        for i, st in enumerate(subtasks, 1):
            self.add_subtask(vault_task_dir, i, st["name"], **{
                k: v for k, v in st.items() if k != "name"
            })

        return vault_task_dir

    def add_subtask(
        self,
        task_dir: Path,
        num: int,
        name: str,
        *,
        subtask_type: str = "code",
        depends: list[int] | None = None,
        repo: str = "",
        branch: str = "",
        status: str = "pending",
    ) -> Path:
        """Create a single SUBTASK.md in the given task directory."""
        today = date.today().isoformat()
        slug = f"{num:02d}-{name}"
        fm = {
            "type": "subtask",
            "status": status,
            "subtask_type": subtask_type,
            "depends": depends or [],
            "repo": repo,
            "branch": branch,
            "created": today,
        }
        sub_path = task_dir / "subtasks" / slug / "SUBTASK.md"
        write_frontmatter(sub_path, fm)
        return sub_path
