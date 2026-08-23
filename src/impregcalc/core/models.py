"""Typed data models and explicit scientific conventions."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .errors import CompositionError


class LoadingKind(str, Enum):
    """Quantity named by the reported loading percentage."""

    ELEMENTAL_METAL = "elemental_metal"
    METAL_OXIDE = "metal_oxide"
    PRECURSOR = "precursor"


class LoadingBasis(str, Enum):
    """Denominator convention for a loading percentage."""

    FINAL_CATALYST = "final_catalyst"
    SUPPORT_RELATIVE = "support_relative"


class PreparationMethod(str, Enum):
    """Supported impregnation modes implemented by the recipe arithmetic."""

    INCIPIENT_WETNESS = "incipient_wetness"
    WET_IMPREGNATION = "wet_impregnation"


@dataclass(frozen=True, slots=True)
class PrecursorSpec:
    formula: str
    target_element: str
    purity_fraction: float = 1.0

    def __post_init__(self) -> None:
        if not self.formula.strip():
            raise CompositionError("Precursor formula must not be empty")
        if not self.target_element.strip():
            raise CompositionError("Precursor target element must not be empty")
        if not 0 < self.purity_fraction <= 1:
            raise CompositionError("Precursor purity_fraction must be in (0, 1]")


@dataclass(frozen=True, slots=True)
class LoadingTarget:
    name: str
    kind: LoadingKind
    basis: LoadingBasis
    loading_percent: float
    precursor: PrecursorSpec
    active_formula: str | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise CompositionError("Target name must not be empty")
        if self.loading_percent <= 0:
            raise CompositionError("Target loading_percent must be greater than zero")
        if self.loading_percent >= 100 and self.basis is LoadingBasis.FINAL_CATALYST:
            raise CompositionError("A final-catalyst loading must be below 100 wt%")
        if self.kind is LoadingKind.METAL_OXIDE and not self.active_formula:
            raise CompositionError("metal_oxide loading requires active_formula")


@dataclass(frozen=True, slots=True)
class PromoterTarget:
    """An elemental promoter specified by an atomic ratio to a loading target."""

    name: str
    target_element: str
    reference_target: str
    atomic_ratio_to_reference: float
    precursor: PrecursorSpec

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.reference_target.strip():
            raise CompositionError("Promoter name and reference_target must not be empty")
        if self.atomic_ratio_to_reference <= 0:
            raise CompositionError("Promoter atomic ratio must be greater than zero")
        if self.target_element != self.precursor.target_element:
            raise CompositionError(
                "Promoter target element must match its precursor target element"
            )


@dataclass(frozen=True, slots=True)
class RecipeRequest:
    support_name: str
    support_mass_g: float
    method: PreparationMethod
    targets: tuple[LoadingTarget, ...]
    pore_volume_ml_g: float | None = None
    solution_volume_ml: float | None = None
    promoters: tuple[PromoterTarget, ...] = ()
    cycles: int = 1
    cycle_fractions: tuple[float, ...] | None = None

    def __post_init__(self) -> None:
        if not self.support_name.strip():
            raise CompositionError("Support name must not be empty")
        if self.support_mass_g <= 0:
            raise CompositionError("support_mass_g must be greater than zero")
        if not self.targets:
            raise CompositionError("At least one loading target is required")
        names = [target.name for target in self.targets]
        if len(names) != len(set(names)):
            raise CompositionError("Loading target names must be unique")
        promoter_names = [promoter.name for promoter in self.promoters]
        if set(names) & set(promoter_names) or len(promoter_names) != len(set(promoter_names)):
            raise CompositionError("All loading and promoter names must be unique")
        if self.pore_volume_ml_g is not None and self.pore_volume_ml_g <= 0:
            raise CompositionError("pore_volume_ml_g must be greater than zero when supplied")
        if self.solution_volume_ml is not None and self.solution_volume_ml <= 0:
            raise CompositionError("solution_volume_ml must be greater than zero when supplied")
        if self.method is PreparationMethod.INCIPIENT_WETNESS and self.pore_volume_ml_g is None:
            raise CompositionError("Incipient-wetness mode requires pore_volume_ml_g")
        if self.method is PreparationMethod.WET_IMPREGNATION and self.solution_volume_ml is None:
            raise CompositionError("Wet-impregnation mode requires an explicit solution_volume_ml")
        if self.cycles < 1:
            raise CompositionError("cycles must be at least one")
        if self.cycle_fractions is not None:
            if len(self.cycle_fractions) != self.cycles:
                raise CompositionError("cycle_fractions length must equal cycles")
            if any(fraction <= 0 for fraction in self.cycle_fractions):
                raise CompositionError("Every cycle fraction must be greater than zero")
            if abs(sum(self.cycle_fractions) - 1.0) > 1e-9:
                raise CompositionError("cycle_fractions must sum to one")


@dataclass(frozen=True, slots=True)
class CyclePortion:
    cycle: int
    fraction: float
    precursor_mass_g: float
    solution_volume_ml: float


@dataclass(frozen=True, slots=True)
class PrecursorRequirement:
    name: str
    kind: LoadingKind
    basis_description: str
    active_formula: str
    target_element: str
    active_component_mass_g: float
    target_element_mass_g: float
    precursor_formula: str
    precursor_molar_mass_g_mol: float
    precursor_purity_fraction: float
    pure_precursor_mass_g: float
    commercial_precursor_mass_g: float
    precursor_amount_mol: float
    concentration_commercial_g_ml: float
    concentration_pure_mol_l: float
    cycle_portions: tuple[CyclePortion, ...]
    atomic_ratio_note: str | None = None


@dataclass(frozen=True, slots=True)
class RecipeResult:
    request: RecipeRequest
    final_formulated_mass_g: float
    total_active_component_mass_g: float
    nominal_pore_volume_ml: float | None
    selected_solution_volume_ml: float
    requirements: tuple[PrecursorRequirement, ...]
    mass_closure_residual_g: float
    warnings: tuple[str, ...] = field(default_factory=tuple)
    assumptions: tuple[str, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation with units in every key."""

        return {
            "schema_version": "1.0",
            "support": {
                "name": self.request.support_name,
                "mass_g": self.request.support_mass_g,
                "pore_volume_ml_g": self.request.pore_volume_ml_g,
            },
            "method": self.request.method.value,
            "cycles": self.request.cycles,
            "final_formulated_mass_g": self.final_formulated_mass_g,
            "total_active_component_mass_g": self.total_active_component_mass_g,
            "nominal_pore_volume_ml": self.nominal_pore_volume_ml,
            "selected_solution_volume_ml": self.selected_solution_volume_ml,
            "mass_closure_residual_g": self.mass_closure_residual_g,
            "requirements": [
                {
                    "name": row.name,
                    "kind": row.kind.value,
                    "basis": row.basis_description,
                    "active_formula": row.active_formula,
                    "target_element": row.target_element,
                    "active_component_mass_g": row.active_component_mass_g,
                    "target_element_mass_g": row.target_element_mass_g,
                    "precursor_formula": row.precursor_formula,
                    "precursor_molar_mass_g_mol": row.precursor_molar_mass_g_mol,
                    "precursor_purity_fraction": row.precursor_purity_fraction,
                    "pure_precursor_mass_g": row.pure_precursor_mass_g,
                    "commercial_precursor_mass_g": row.commercial_precursor_mass_g,
                    "precursor_amount_mol": row.precursor_amount_mol,
                    "concentration_commercial_g_ml": row.concentration_commercial_g_ml,
                    "concentration_pure_mol_l": row.concentration_pure_mol_l,
                    "atomic_ratio_note": row.atomic_ratio_note,
                    "cycles": [
                        {
                            "cycle": cycle.cycle,
                            "fraction": cycle.fraction,
                            "precursor_mass_g": cycle.precursor_mass_g,
                            "shared_solution_volume_ml": cycle.solution_volume_ml,
                        }
                        for cycle in row.cycle_portions
                    ],
                }
                for row in self.requirements
            ],
            "assumptions": list(self.assumptions),
            "warnings": list(self.warnings),
        }
