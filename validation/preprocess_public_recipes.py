"""Translate curated publication facts into ImpregCalc request documents.

This validation-only adapter intentionally lives outside ``src/impregcalc``. It does
not teach the scientific core aliases, infer omitted loading conventions, or turn
unreported assays into measured commercial purities.
"""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path
from typing import Any


def load_record(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict) or not str(value.get("case_id", "")).startswith("IC-PUB-"):
        raise ValueError("A public-recipe fixture must have an IC-PUB-* case_id")
    return value


def build_requests(record: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Build one request, or explicit parallel requests for an ambiguous basis."""

    source = record["source_recipe"]
    targets = source["targets"]
    ambiguous = [target for target in targets if target.get("basis") is None]
    if ambiguous and (len(ambiguous) != 1 or len(targets) != 1):
        raise ValueError("Only a single explicitly enumerated ambiguous target is supported")
    bases = ambiguous[0]["basis_interpretations"] if ambiguous else [None]
    requests: dict[str, dict[str, Any]] = {}
    for interpreted_basis in bases:
        request_targets = []
        for target in targets:
            basis = target.get("basis") or interpreted_basis
            if basis is None:
                raise ValueError("Missing loading basis without an explicit interpretation")
            request_target: dict[str, Any] = {
                "name": target["name"],
                "kind": target["kind"],
                "basis": basis,
                "loading_percent": target["loading_percent"],
                "precursor": {
                    "formula": target["normalized_precursor_formula"],
                    "target_element": target["target_element"],
                },
            }
            if target.get("active_formula") is not None:
                request_target["active_formula"] = target["active_formula"]
            if target.get("purity_fraction") is not None:
                request_target["precursor"]["purity_fraction"] = target["purity_fraction"]
            request_targets.append(request_target)
        request: dict[str, Any] = {
            "support_name": source["support_name"],
            "support_mass_g": source["support_mass_g"],
            "method": source["method"],
            "pore_volume_ml_g": source["pore_volume_ml_g"],
            "targets": request_targets,
            "cycles": source["cycles"],
        }
        if source.get("solution_volume_ml") is not None:
            request["solution_volume_ml"] = source["solution_volume_ml"]
        scenario = str(interpreted_basis or "reported_basis")
        requests[scenario] = deepcopy(request)
    return requests


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture", type=Path)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    payload = build_requests(load_record(arguments.fixture))
    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if arguments.output is None:
        print(encoded, end="")
    else:
        arguments.output.write_text(encoded, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
