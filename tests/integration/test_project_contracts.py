from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[2]


@pytest.mark.integration
def test_dgx_workflow_excludes_untrusted_fork_code() -> None:
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "runs-on: [self-hosted, Linux, ARM64, dgx-spark]" in workflow
    assert "github.actor == github.repository_owner" in workflow
    assert "github.event.pull_request.head.repo.full_name == github.repository" in workflow
    assert "pull_request_target" not in workflow
    assert "workflow_run" not in workflow
    assert "issue_comment" not in workflow
    assert "contents: read" in workflow


@pytest.mark.integration
def test_actions_are_pinned_and_publish_uses_oidc() -> None:
    workflows = list((ROOT / ".github/workflows").glob("*.yml"))
    action_uses = re.compile(r"^\s*uses:\s*[^#\s]+@([^\s#]+)", re.MULTILINE)
    for path in workflows:
        text = path.read_text(encoding="utf-8")
        for revision in action_uses.findall(text):
            assert re.fullmatch(r"[0-9a-f]{40}", revision), (path, revision)
    publish = (ROOT / ".github/workflows/publish.yml").read_text(encoding="utf-8")
    assert "id-token: write" in publish
    assert "environment:" in publish and "name: pypi" in publish


@pytest.mark.integration
def test_macos_matrix_covers_arm_and_intel_real_gui_workflow() -> None:
    workflow = (ROOT / ".github/workflows/macos.yml").read_text(encoding="utf-8")
    assert "label: macos-15" in workflow
    assert "label: macos-15-intel" in workflow
    assert "tests/gui_widget_smoke.py" in workflow
    assert "MPLBACKEND: Agg" in workflow


@pytest.mark.integration
def test_scientific_core_has_no_gui_or_plot_backend_import() -> None:
    core_text = "\n".join(
        path.read_text(encoding="utf-8") for path in (ROOT / "src/impregcalc/core").glob("*.py")
    )
    for forbidden in ("tkinter", "matplotlib", "PyQt", "PySide"):
        assert forbidden not in core_text
