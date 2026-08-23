"""Executable end-to-end GUI wiring smoke used by CI and local macOS validation."""

from __future__ import annotations

import sys

from impregcalc.gui.app import create_app


def main(output: str) -> int:
    root, app = create_app()
    root.update_idletasks()
    result = app.calculate_current()
    assert result.requirements[0].commercial_precursor_mass_g > 0
    assert "Required commercial precursor" in app.output.get("1.0", "end")
    destination = app.export_to(output)
    assert destination.is_file() and destination.stat().st_size > 0
    root.update_idletasks()
    root.destroy()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
