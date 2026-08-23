from __future__ import annotations

import platform
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.macos
@pytest.mark.skipif(platform.system() != "Darwin", reason="requires a real macOS GUI session")
def test_real_macos_gui_lifecycle(tmp_path: Path) -> None:
    output = tmp_path / "macos-gui.md"
    completed = subprocess.run(
        [sys.executable, "tests/gui_widget_smoke.py", str(output)],
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert output.is_file()
