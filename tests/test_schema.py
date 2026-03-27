"""Layer 1: Frontmatter schema validation tests.

Validates SKILL.md, agent MD, and plugin structure files against their schemas.
These tests run against the ACTUAL plugin files (not fixtures).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from tests.helpers.frontmatter import parse_frontmatter, validate_skill_frontmatter

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PLUGIN_ROOT = Path.home() / ".claude/plugins/cache/workbench-local/workbench/2.1.0"
SKILLS_DIR = PLUGIN_ROOT / "skills"
AGENTS_DIR = PLUGIN_ROOT / "agents"

KEBAB_CASE_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
VALID_AGENT_MODELS = {"opus", "sonnet", "haiku"}
VALID_AGENT_TYPES = {"agent", "subagent"}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _plugin_available() -> bool:
    return PLUGIN_ROOT.is_dir()


def _discover_skills() -> list[Path]:
    """Return all SKILL.md paths under the plugin skills/ directory."""
    if not SKILLS_DIR.is_dir():
        return []
    return sorted(SKILLS_DIR.glob("*/SKILL.md"))


def _discover_agents() -> list[Path]:
    """Return all .md files under the plugin agents/ directory."""
    if not AGENTS_DIR.is_dir():
        return []
    return sorted(AGENTS_DIR.glob("*.md"))


def _parse_agent_frontmatter(file_path: Path) -> dict:
    """Parse frontmatter from agent files.

    Agent files may have a heading line before the ``---`` fence, so the
    standard ``parse_frontmatter`` helper (which expects ``---`` at line 0)
    cannot be used directly.

    Some agent files contain YAML values with special characters (e.g. ``?``
    in unquoted flow-sequence items) that strict ``yaml.safe_load`` rejects.
    We pre-process the raw YAML to quote such values before parsing.
    """
    text = file_path.read_text(encoding="utf-8")
    # Find first --- delimiter (may not be at position 0)
    first = text.find("---")
    if first == -1:
        raise ValueError(f"No frontmatter delimiter in {file_path}")
    second = text.find("---", first + 3)
    if second == -1:
        raise ValueError(f"Malformed frontmatter in {file_path}")
    fm_raw = text[first + 3 : second].strip()
    if not fm_raw:
        return {}

    # Pre-process: quote items inside flow sequences that contain special chars
    # e.g.  triggers: [맞아?, foo] -> triggers: ["맞아?", foo]
    def _quote_flow_items(line: str) -> str:
        m = re.match(r"^(\s*\w+:\s*)\[(.+)\]\s*$", line)
        if not m:
            return line
        prefix, items_str = m.group(1), m.group(2)
        items = [i.strip() for i in items_str.split(",")]
        quoted = []
        for item in items:
            if item and not item.startswith('"') and re.search(r"[?:{}[\]|>@`]", item):
                quoted.append(f'"{item}"')
            else:
                quoted.append(item)
        return f"{prefix}[{', '.join(quoted)}]"

    fm_fixed = "\n".join(_quote_flow_items(line) for line in fm_raw.splitlines())
    data = yaml.safe_load(fm_fixed)
    return data if data else {}


# ---------------------------------------------------------------------------
# Parametrize ids
# ---------------------------------------------------------------------------

_skill_paths = _discover_skills()
_skill_ids = [p.parent.name for p in _skill_paths]

_agent_paths = _discover_agents()
_agent_ids = [p.stem for p in _agent_paths]

# ---------------------------------------------------------------------------
# Module-level skip
# ---------------------------------------------------------------------------

pytestmark = pytest.mark.skipif(
    not _plugin_available(),
    reason=f"Plugin directory not found: {PLUGIN_ROOT}",
)

# ===========================================================================
# 1. SKILL.md schema validation
# ===========================================================================


class TestSkillSchema:
    """Validate frontmatter schema for every SKILL.md in the plugin."""

    @pytest.mark.parametrize("skill_path", _skill_paths, ids=_skill_ids)
    def test_required_fields(self, skill_path: Path):
        """Each SKILL.md must pass validate_skill_frontmatter (name, description, metadata.version)."""
        data, _ = parse_frontmatter(skill_path)
        violations = validate_skill_frontmatter(data)
        assert violations == [], f"Schema violations in {skill_path.parent.name}: {violations}"

    @pytest.mark.parametrize("skill_path", _skill_paths, ids=_skill_ids)
    def test_name_is_kebab_case(self, skill_path: Path):
        """The ``name`` field must be kebab-case."""
        data, _ = parse_frontmatter(skill_path)
        name = data.get("name", "")
        assert KEBAB_CASE_RE.match(name), (
            f"Skill name {name!r} in {skill_path.parent.name} is not kebab-case"
        )

    @pytest.mark.parametrize("skill_path", _skill_paths, ids=_skill_ids)
    def test_name_matches_directory(self, skill_path: Path):
        """The ``name`` field should match the containing directory name."""
        data, _ = parse_frontmatter(skill_path)
        assert data.get("name") == skill_path.parent.name, (
            f"name={data.get('name')!r} does not match directory {skill_path.parent.name!r}"
        )


# ===========================================================================
# 2. Agent MD schema validation
# ===========================================================================


class TestAgentSchema:
    """Validate frontmatter schema for every agent .md in the plugin."""

    @pytest.mark.parametrize("agent_path", _agent_paths, ids=_agent_ids)
    def test_required_fields(self, agent_path: Path):
        """Each agent file must have ``model`` and ``type`` in frontmatter."""
        data = _parse_agent_frontmatter(agent_path)
        missing = [f for f in ("model", "type") if f not in data]
        assert missing == [], f"Missing fields in {agent_path.stem}: {missing}"

    @pytest.mark.parametrize("agent_path", _agent_paths, ids=_agent_ids)
    def test_model_is_valid(self, agent_path: Path):
        """The ``model`` must be one of {opus, sonnet, haiku}."""
        data = _parse_agent_frontmatter(agent_path)
        model = data.get("model")
        assert model in VALID_AGENT_MODELS, (
            f"Agent {agent_path.stem} has invalid model={model!r}, expected one of {VALID_AGENT_MODELS}"
        )

    @pytest.mark.parametrize("agent_path", _agent_paths, ids=_agent_ids)
    def test_type_is_valid(self, agent_path: Path):
        """The ``type`` must be one of {agent, subagent}."""
        data = _parse_agent_frontmatter(agent_path)
        agent_type = data.get("type")
        assert agent_type in VALID_AGENT_TYPES, (
            f"Agent {agent_path.stem} has invalid type={agent_type!r}, expected one of {VALID_AGENT_TYPES}"
        )


# ===========================================================================
# 3. Cross-reference validation
# ===========================================================================


class TestCrossReferences:
    """Verify that skills referencing agents or other skills point to real files."""

    @staticmethod
    def _skills_with_agent_refs() -> list[tuple[str, str]]:
        """Return (skill_name, agent_stem) pairs for skills that reference agents."""
        pairs = []
        for skill_path in _skill_paths:
            data, _ = parse_frontmatter(skill_path)
            agents_map = (data.get("metadata") or {}).get("agents")
            if isinstance(agents_map, dict):
                for _role, ref in agents_map.items():
                    # refs look like "workbench:checker" -- extract the agent stem
                    stem = ref.split(":")[-1] if ":" in str(ref) else str(ref)
                    pairs.append((skill_path.parent.name, stem))
        return pairs

    @staticmethod
    def _skills_with_skill_refs() -> list[tuple[str, str]]:
        """Return (skill_name, referenced_skill) pairs."""
        pairs = []
        for skill_path in _skill_paths:
            data, _ = parse_frontmatter(skill_path)
            skill_refs = (data.get("metadata") or {}).get("skills")
            if isinstance(skill_refs, list):
                for ref in skill_refs:
                    pairs.append((skill_path.parent.name, str(ref)))
        return pairs

    @pytest.mark.parametrize(
        "skill_name,agent_stem",
        _skills_with_agent_refs.__func__(),
        ids=[f"{s}->{a}" for s, a in _skills_with_agent_refs.__func__()],
    )
    def test_referenced_agent_exists(self, skill_name: str, agent_stem: str):
        """An agent referenced in metadata.agents must have a corresponding .md file."""
        agent_file = AGENTS_DIR / f"{agent_stem}.md"
        assert agent_file.is_file(), (
            f"Skill {skill_name!r} references agent {agent_stem!r} but {agent_file} does not exist"
        )

    @pytest.mark.parametrize(
        "skill_name,ref_skill",
        _skills_with_skill_refs.__func__(),
        ids=[f"{s}->{r}" for s, r in _skills_with_skill_refs.__func__()],
    )
    def test_referenced_skill_exists(self, skill_name: str, ref_skill: str):
        """A skill referenced in metadata.skills must have a corresponding directory with SKILL.md."""
        skill_file = SKILLS_DIR / ref_skill / "SKILL.md"
        assert skill_file.is_file(), (
            f"Skill {skill_name!r} references skill {ref_skill!r} but {skill_file} does not exist"
        )


# ===========================================================================
# 4. Plugin structure validation
# ===========================================================================


class TestPluginStructure:
    """Verify the plugin root has the expected directory layout."""

    def test_required_directories_exist(self):
        """Plugin root must contain skills/, agents/, and CLAUDE.md."""
        assert SKILLS_DIR.is_dir(), f"Missing {SKILLS_DIR}"
        assert AGENTS_DIR.is_dir(), f"Missing {AGENTS_DIR}"
        assert (PLUGIN_ROOT / "CLAUDE.md").is_file(), f"Missing {PLUGIN_ROOT / 'CLAUDE.md'}"

    @pytest.mark.parametrize(
        "skill_dir",
        [d for d in sorted(SKILLS_DIR.iterdir()) if d.is_dir()] if SKILLS_DIR.is_dir() else [],
        ids=[d.name for d in sorted(SKILLS_DIR.iterdir()) if d.is_dir()] if SKILLS_DIR.is_dir() else [],
    )
    def test_each_skill_directory_has_skill_md(self, skill_dir: Path):
        """Every subdirectory under skills/ must contain a SKILL.md file."""
        assert (skill_dir / "SKILL.md").is_file(), (
            f"Skill directory {skill_dir.name!r} is missing SKILL.md"
        )
