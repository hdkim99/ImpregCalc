# macOS GUI support and diagnostics

## Supported and verified combinations

The declared support target for 0.1.x is macOS 15 or newer, Python 3.10–3.13,
Apple Silicon and Intel, using Tkinter/ttk. GitHub workflows target `macos-15`
(Apple Silicon) and `macos-15-intel` (Intel). Intel hosted availability is currently
announced by GitHub through August 2027.

Local smoke performed during 0.1.0 development:

- macOS 27.0;
- Apple Silicon (`arm64`);
- Python 3.14.7 in a clean virtual environment;
- Tk 9.0;
- window creation, calculation, Markdown export, close, and process exit.

Python 3.14 is an extra development smoke, not yet part of the package's declared
3.10–3.13 compatibility range.

## Clean installation

```bash
python3 -m venv /tmp/impregcalc-macos-smoke
/tmp/impregcalc-macos-smoke/bin/python -m pip install .
/tmp/impregcalc-macos-smoke/bin/python -c "import tkinter; print(tkinter.TkVersion)"
/tmp/impregcalc-macos-smoke/bin/python -m impregcalc.gui
```

Expected: one window opens; Calculate shows a cobalt recipe; Export writes a
non-empty file; closing the window returns the process normally.

Automated lifecycle command from a source checkout:

```bash
python tests/gui_widget_smoke.py /tmp/impregcalc-gui-smoke.md
test -s /tmp/impregcalc-gui-smoke.md
```

## If Tkinter is unavailable

Capture:

```bash
python --version
uname -m
sw_vers
python -c "import sys; print(sys.executable); import tkinter; print(tkinter.TkVersion)"
python -m pip list
python -m impregcalc.gui
```

Use a python.org or Homebrew Python distribution that includes compatible Tcl/Tk.
The Python extra `impregcalc[gui]` is intentionally empty because Tkinter is a Python
distribution component, not a PyPI dependency.

## Backend and Qt policy

ImpregCalc has no PyQt, PySide, Qt, or pyqtgraph dependency. The scientific core and
CLI never import Tkinter or matplotlib. Tkinter is imported only by the GUI adapter.
The optional figure exporter selects `Agg` before importing `matplotlib.pyplot`, so
CLI plot export does not probe a Qt or display backend.

