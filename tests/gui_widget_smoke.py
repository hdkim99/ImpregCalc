"""Executable end-to-end GUI wiring smoke used by CI and local macOS validation."""

from __future__ import annotations

import sys

from impregcalc.core.models import LoadingBasis, LoadingKind
from impregcalc.gui.app import create_app


def main(output: str) -> int:
    root, app = create_app()
    # IC-PUB-002 is inside the deliberately compact single-target GUI scope:
    # 3 wt% elemental Fe relative to gamma-Al2O3 support, nitrate nonahydrate,
    # and a reported support pore volume of 0.47 mL/g. The publication did not
    # report a support batch mass or precursor assay, so this smoke uses a
    # scale-independent 1.000 g support and validates the pure equivalent.
    values = {
        "support_name": "gamma-Al2O3 (IC-PUB-002; pure-equivalent audit)",
        "support_mass": "1.0",
        "pore_volume": "0.47",
        "target_name": "iron (publication assay unreported; 100% pure equivalent)",
        "loading": "3.0",
        "kind": LoadingKind.ELEMENTAL_METAL.value,
        "basis": LoadingBasis.SUPPORT_RELATIVE.value,
        "element": "Fe",
        "active_formula": "Fe",
        "precursor": "Fe(NO3)3·9H2O",
        "purity_percent": "100",
        "cycles": "1",
    }
    for key, value in values.items():
        app.values[key].set(value)
    root.update_idletasks()
    result = app.calculate_current()
    assert abs(result.requirements[0].pure_precursor_mass_g - 0.21702497985495567) < 1e-12
    assert result.nominal_pore_volume_ml == 0.47
    assert "Required commercial precursor" in app.output.get("1.0", "end")
    destination = app.export_to(output)
    assert destination.is_file() and destination.stat().st_size > 0
    root.update_idletasks()
    root.destroy()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
