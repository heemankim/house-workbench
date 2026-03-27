"""Shared pytest fixtures for workbench test harness."""

import pytest

from tests.helpers.workspace import WorkspaceFactory


@pytest.fixture
def workspace_factory(tmp_path):
    """Provide a WorkspaceFactory rooted at a temporary directory."""
    return WorkspaceFactory(tmp_path)


@pytest.fixture
def minimal_workspace(workspace_factory):
    """Create and return a minimal workspace path."""
    return workspace_factory.create_minimal()


@pytest.fixture
def workspace_after_start(workspace_factory):
    """Create and return a workspace in post-wb-start state (from static fixture)."""
    return workspace_factory.create_from_fixture("after-wb-start")


@pytest.fixture
def workspace_after_done(workspace_factory):
    """Create and return a workspace in post-wb-done state (from static fixture)."""
    return workspace_factory.create_from_fixture("after-wb-done")
