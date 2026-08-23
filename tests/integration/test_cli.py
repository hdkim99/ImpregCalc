from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.integration
def test_cli_calculate_without_gui_import(tmp_path: Path) -> None:
    output = tmp_path / "recipe.json"
    code = (
        "import sys; from impregcalc.cli import main; "
        f"status=main(['calculate','examples/co_ru_iwi.json','--output',{str(output)!r}]); "
        "assert 'tkinter' not in sys.modules; assert 'matplotlib' not in sys.modules; "
        "raise SystemExit(status)"
    )
    completed = subprocess.run(
        [sys.executable, "-c", code],
        cwd=Path.cwd(),
        env={**os.environ, "MPLBACKEND": ""},
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert output.is_file()


@pytest.mark.integration
def test_cli_rejects_invalid_request(tmp_path: Path) -> None:
    invalid = tmp_path / "invalid.json"
    invalid.write_text("{}", encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, "-m", "impregcalc.cli", "validate", str(invalid)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 2
    assert "error" in completed.stderr
