"""A compact, fully wired Tkinter workflow for a single loading target."""

from __future__ import annotations

import platform
import sys
from pathlib import Path

from impregcalc.application.service import calculate_recipe
from impregcalc.core.models import (
    LoadingBasis,
    LoadingKind,
    LoadingTarget,
    PrecursorSpec,
    PreparationMethod,
    RecipeRequest,
    RecipeResult,
)
from impregcalc.io import format_markdown, write_result

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
except ImportError as exc:  # pragma: no cover - depends on external Python distribution
    raise RuntimeError(
        "ImpregCalc GUI could not import Tkinter. "
        f"Python={platform.python_version()}, OS={platform.platform()}. "
        'Install the package with `pip install "impregcalc[gui]"` and use a Python '
        "distribution that includes Tcl/Tk, then run `python -m impregcalc.gui`. "
        "The GUI extra records installation intent but cannot add Tcl/Tk to Python itself."
    ) from exc


class RecipeApp:
    """One-root Tk application whose controls call the public calculation service."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("ImpregCalc 0.1.0")
        self.root.minsize(850, 620)
        self._last_result: RecipeResult | None = None
        self.values: dict[str, tk.StringVar] = {
            "support_name": tk.StringVar(value="gamma-Al2O3"),
            "support_mass": tk.StringVar(value="8.0"),
            "pore_volume": tk.StringVar(value="0.72"),
            "target_name": tk.StringVar(value="cobalt"),
            "loading": tk.StringVar(value="15"),
            "kind": tk.StringVar(value=LoadingKind.ELEMENTAL_METAL.value),
            "basis": tk.StringVar(value=LoadingBasis.FINAL_CATALYST.value),
            "element": tk.StringVar(value="Co"),
            "active_formula": tk.StringVar(value="Co"),
            "precursor": tk.StringVar(value="Co(NO3)2·6H2O"),
            "purity_percent": tk.StringVar(value="98"),
            "cycles": tk.StringVar(value="1"),
        }
        self._build()

    def _build(self) -> None:
        frame = ttk.Frame(self.root, padding=12)
        frame.pack(fill="both", expand=True)
        inputs = ttk.LabelFrame(frame, text="Explicit recipe inputs", padding=10)
        inputs.pack(fill="x")
        fields = [
            ("Support", "support_name"),
            ("Dry support mass / g", "support_mass"),
            ("Pore volume / mL g⁻¹", "pore_volume"),
            ("Target name", "target_name"),
            ("Loading / wt%", "loading"),
            ("Target element", "element"),
            ("Retained component formula", "active_formula"),
            ("Precursor formula", "precursor"),
            ("Precursor purity / %", "purity_percent"),
            ("Arithmetic cycles", "cycles"),
        ]
        for index, (label, key) in enumerate(fields):
            row, column = divmod(index, 2)
            offset = column * 2
            ttk.Label(inputs, text=label).grid(row=row, column=offset, sticky="w", padx=4, pady=4)
            ttk.Entry(inputs, textvariable=self.values[key], width=28).grid(
                row=row, column=offset + 1, sticky="ew", padx=4, pady=4
            )
        row = len(fields) // 2 + len(fields) % 2
        ttk.Label(inputs, text="Loading quantity").grid(
            row=row, column=0, sticky="w", padx=4, pady=4
        )
        ttk.Combobox(
            inputs,
            textvariable=self.values["kind"],
            values=[item.value for item in LoadingKind],
            state="readonly",
            width=25,
        ).grid(row=row, column=1, sticky="ew", padx=4, pady=4)
        ttk.Label(inputs, text="Loading denominator").grid(
            row=row, column=2, sticky="w", padx=4, pady=4
        )
        ttk.Combobox(
            inputs,
            textvariable=self.values["basis"],
            values=[item.value for item in LoadingBasis],
            state="readonly",
            width=25,
        ).grid(row=row, column=3, sticky="ew", padx=4, pady=4)
        inputs.columnconfigure(1, weight=1)
        inputs.columnconfigure(3, weight=1)

        actions = ttk.Frame(frame, padding=(0, 10))
        actions.pack(fill="x")
        ttk.Button(actions, text="Calculate", command=self._calculate_clicked).pack(side="left")
        ttk.Button(actions, text="Export…", command=self._export_clicked).pack(side="left", padx=8)
        ttk.Label(
            actions,
            text="IWI volume is nominal; solubility and catalyst morphology are not predicted.",
        ).pack(side="right")
        self.output = tk.Text(frame, wrap="word", height=25, font=("TkFixedFont", 11))
        self.output.pack(fill="both", expand=True)

    def request_from_widgets(self) -> RecipeRequest:
        kind = LoadingKind(self.values["kind"].get())
        active = self.values["active_formula"].get().strip()
        return RecipeRequest(
            support_name=self.values["support_name"].get(),
            support_mass_g=float(self.values["support_mass"].get()),
            pore_volume_ml_g=float(self.values["pore_volume"].get()),
            method=PreparationMethod.INCIPIENT_WETNESS,
            cycles=int(self.values["cycles"].get()),
            targets=(
                LoadingTarget(
                    name=self.values["target_name"].get(),
                    kind=kind,
                    basis=LoadingBasis(self.values["basis"].get()),
                    loading_percent=float(self.values["loading"].get()),
                    active_formula=active or None,
                    precursor=PrecursorSpec(
                        formula=self.values["precursor"].get(),
                        target_element=self.values["element"].get(),
                        purity_fraction=float(self.values["purity_percent"].get()) / 100.0,
                    ),
                ),
            ),
        )

    def calculate_current(self) -> RecipeResult:
        result = calculate_recipe(self.request_from_widgets())
        self._last_result = result
        self.output.delete("1.0", "end")
        self.output.insert("1.0", format_markdown(result))
        return result

    def export_to(self, path: str | Path) -> Path:
        result = self._last_result or self.calculate_current()
        return write_result(result, path)

    def _calculate_clicked(self) -> None:
        try:
            self.calculate_current()
        except (ValueError, RuntimeError) as exc:
            messagebox.showerror("ImpregCalc input error", str(exc), parent=self.root)

    def _export_clicked(self) -> None:
        path = filedialog.asksaveasfilename(
            parent=self.root,
            defaultextension=".md",
            filetypes=[
                ("Markdown", "*.md"),
                ("JSON", "*.json"),
                ("CSV", "*.csv"),
                ("Excel", "*.xlsx"),
            ],
        )
        if not path:
            return
        try:
            self.export_to(path)
        except (ValueError, RuntimeError, OSError) as exc:
            messagebox.showerror("ImpregCalc export error", str(exc), parent=self.root)


def create_app(root: tk.Tk | None = None) -> tuple[tk.Tk, RecipeApp]:
    """Create exactly one root when one is not injected by a test or host."""

    actual_root = root if root is not None else tk.Tk()
    return actual_root, RecipeApp(actual_root)


def main() -> int:
    try:
        root, _app = create_app()
    except tk.TclError as exc:
        print(
            "ImpregCalc GUI could not create a Tk window. "
            f"Python={platform.python_version()}, OS={platform.platform()}. "
            "On macOS, use a supported python.org or Homebrew Python with Tcl/Tk. "
            f"Details: {exc}",
            file=sys.stderr,
        )
        return 2
    root.mainloop()
    return 0
