"""Request decoding and calculation orchestration."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from impregcalc.core.calculator import calculate
from impregcalc.core.errors import CompositionError
from impregcalc.core.models import (
    LoadingBasis,
    LoadingKind,
    LoadingTarget,
    PrecursorSpec,
    PreparationMethod,
    PromoterTarget,
    RecipeRequest,
    RecipeResult,
)


def _mapping(value: object, context: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise CompositionError(f"{context} must be a JSON object")
    return value


def _precursor(data: Mapping[str, Any]) -> PrecursorSpec:
    return PrecursorSpec(
        formula=str(data["formula"]),
        target_element=str(data["target_element"]),
        purity_fraction=float(data.get("purity_fraction", 1.0)),
    )


def request_from_dict(data: Mapping[str, Any]) -> RecipeRequest:
    """Decode the documented JSON schema into a validated request."""

    try:
        targets = tuple(
            LoadingTarget(
                name=str(target_data["name"]),
                kind=LoadingKind(str(target_data["kind"])),
                basis=LoadingBasis(str(target_data["basis"])),
                loading_percent=float(target_data["loading_percent"]),
                active_formula=(
                    str(target_data["active_formula"])
                    if target_data.get("active_formula") is not None
                    else None
                ),
                precursor=_precursor(_mapping(target_data["precursor"], "target precursor")),
            )
            for item in data["targets"]
            for target_data in [_mapping(item, "target")]
        )
        promoters = tuple(
            PromoterTarget(
                name=str(promoter_data["name"]),
                target_element=str(promoter_data["target_element"]),
                reference_target=str(promoter_data["reference_target"]),
                atomic_ratio_to_reference=float(promoter_data["atomic_ratio_to_reference"]),
                precursor=_precursor(_mapping(promoter_data["precursor"], "promoter precursor")),
            )
            for item in data.get("promoters", [])
            for promoter_data in [_mapping(item, "promoter")]
        )
        fractions_raw = data.get("cycle_fractions")
        fractions = (
            tuple(float(item) for item in fractions_raw) if fractions_raw is not None else None
        )
        return RecipeRequest(
            support_name=str(data["support_name"]),
            support_mass_g=float(data["support_mass_g"]),
            method=PreparationMethod(str(data["method"])),
            targets=targets,
            pore_volume_ml_g=(
                float(data["pore_volume_ml_g"])
                if data.get("pore_volume_ml_g") is not None
                else None
            ),
            solution_volume_ml=(
                float(data["solution_volume_ml"])
                if data.get("solution_volume_ml") is not None
                else None
            ),
            promoters=promoters,
            cycles=int(data.get("cycles", 1)),
            cycle_fractions=fractions,
        )
    except (KeyError, TypeError, ValueError) as exc:
        if isinstance(exc, CompositionError):
            raise
        raise CompositionError(f"Invalid recipe document: {exc}") from exc


def load_request(path: str | Path) -> RecipeRequest:
    """Load and validate a UTF-8 JSON recipe request."""

    with Path(path).open(encoding="utf-8") as stream:
        payload = json.load(stream)
    return request_from_dict(_mapping(payload, "recipe document"))


def calculate_recipe(request: RecipeRequest | Mapping[str, Any] | str | Path) -> RecipeResult:
    """Calculate from an API model, JSON-like mapping, or JSON file path."""

    if isinstance(request, RecipeRequest):
        decoded = request
    elif isinstance(request, (str, Path)):
        decoded = load_request(request)
    else:
        decoded = request_from_dict(request)
    return calculate(decoded)
