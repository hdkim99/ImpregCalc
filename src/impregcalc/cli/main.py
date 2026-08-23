"""ImpregCalc command-line interface."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from impregcalc import __version__
from impregcalc.application.service import calculate_recipe, load_request
from impregcalc.core.errors import ImpregCalcError
from impregcalc.core.formula import parse_formula
from impregcalc.io import format_markdown, write_result


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="impregcalc",
        description="Explicit supported-catalyst impregnation recipe arithmetic.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)
    calculate_parser = subparsers.add_parser("calculate", help="calculate and export a recipe")
    calculate_parser.add_argument("input", type=Path, help="JSON recipe request")
    calculate_parser.add_argument("--output", "-o", type=Path)
    calculate_parser.add_argument("--plot", type=Path, help="optional PNG/SVG/PDF summary")
    validate_parser = subparsers.add_parser("validate", help="validate and calculate a request")
    validate_parser.add_argument("input", type=Path)
    formula_parser = subparsers.add_parser("formula", help="inspect formula composition and mass")
    formula_parser.add_argument("formula")
    example_parser = subparsers.add_parser("example", help="print the bundled example request")
    example_parser.add_argument("--output", "-o", type=Path)
    return parser


def _example_path() -> Path:
    source = Path("examples/co_ru_iwi.json")
    if not source.is_file():
        raise FileNotFoundError("Run this command from the source checkout to access the example")
    return source


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "formula":
            formula = parse_formula(args.formula)
            print(
                json.dumps(
                    {
                        "formula": formula.normalized,
                        "composition": formula.composition,
                        "molar_mass_g_mol": formula.molar_mass_g_mol,
                    },
                    indent=2,
                )
            )
            return 0
        if args.command == "example":
            content = _example_path().read_text(encoding="utf-8")
            if args.output:
                args.output.write_text(content, encoding="utf-8")
            else:
                print(content, end="")
            return 0
        request = load_request(args.input)
        result = calculate_recipe(request)
        if args.command == "validate":
            print(
                f"VALID: mass closure residual = {result.mass_closure_residual_g:.3e} g; "
                f"{len(result.requirements)} precursor(s)"
            )
            return 0
        if args.output:
            write_result(result, args.output)
            print(f"Wrote {args.output}")
        else:
            print(format_markdown(result))
        if args.plot:
            from impregcalc.plotting import save_recipe_figure

            save_recipe_figure(result, args.plot)
            print(f"Wrote {args.plot}")
        return 0
    except (ImpregCalcError, OSError, RuntimeError, ValueError) as exc:
        print(f"impregcalc: error: {exc}", file=sys.stderr)
        return 2
