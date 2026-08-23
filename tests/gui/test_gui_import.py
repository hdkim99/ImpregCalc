from __future__ import annotations

import importlib
import sys

import pytest


@pytest.mark.gui
def test_core_import_does_not_load_gui_or_plotting() -> None:
    for name in ["impregcalc", "tkinter", "matplotlib", "matplotlib.pyplot"]:
        sys.modules.pop(name, None)
    importlib.import_module("impregcalc")
    assert "tkinter" not in sys.modules
    assert "matplotlib" not in sys.modules


@pytest.mark.gui
def test_gui_module_import() -> None:
    module = importlib.import_module("impregcalc.gui")
    assert callable(module.main)
