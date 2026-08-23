"""Mass-conserving impregnation recipe calculations."""

from __future__ import annotations

from dataclasses import dataclass

from .errors import CompositionError
from .formula import ParsedFormula, parse_formula
from .models import (
    CyclePortion,
    LoadingBasis,
    LoadingKind,
    LoadingTarget,
    PrecursorRequirement,
    PreparationMethod,
    PromoterTarget,
    RecipeRequest,
    RecipeResult,
)


@dataclass(frozen=True, slots=True)
class _LinearMass:
    """Component mass represented as ``coefficient * final_mass + fixed_g``."""

    coefficient: float
    fixed_g: float

    def at(self, final_mass_g: float) -> float:
        return self.coefficient * final_mass_g + self.fixed_g


@dataclass(frozen=True, slots=True)
class _ResolvedTarget:
    target: LoadingTarget
    active: ParsedFormula
    precursor: ParsedFormula
    mass: _LinearMass


def _active_formula(target: LoadingTarget) -> str:
    if target.kind is LoadingKind.ELEMENTAL_METAL:
        if target.active_formula and target.active_formula != target.precursor.target_element:
            raise CompositionError("elemental_metal active_formula must equal the target element")
        return target.precursor.target_element
    if target.kind is LoadingKind.PRECURSOR:
        if target.active_formula and (
            parse_formula(target.active_formula).composition
            != parse_formula(target.precursor.formula).composition
        ):
            raise CompositionError(
                "A precursor loading may only use an active_formula equivalent to the precursor"
            )
        return target.precursor.formula
    assert target.active_formula is not None
    return target.active_formula


def _resolve_target(target: LoadingTarget, support_mass_g: float) -> _ResolvedTarget:
    active = parse_formula(_active_formula(target))
    precursor = parse_formula(target.precursor.formula)
    element = target.precursor.target_element
    if active.count(element) == 0:
        raise CompositionError(f"Active formula {active.normalized} contains no {element}")
    if precursor.count(element) == 0:
        raise CompositionError(f"Precursor formula {precursor.normalized} contains no {element}")
    fraction = target.loading_percent / 100.0
    mass = (
        _LinearMass(fraction, 0.0)
        if target.basis is LoadingBasis.FINAL_CATALYST
        else _LinearMass(0.0, fraction * support_mass_g)
    )
    return _ResolvedTarget(target, active, precursor, mass)


def _promoter_linear_mass(
    promoter: PromoterTarget, reference: _ResolvedTarget
) -> tuple[_LinearMass, ParsedFormula, ParsedFormula]:
    precursor = parse_formula(promoter.precursor.formula)
    if precursor.count(promoter.target_element) == 0:
        raise CompositionError(
            f"Promoter precursor {precursor.normalized} contains no {promoter.target_element}"
        )
    promoter_element = parse_formula(promoter.target_element)
    reference_element = reference.target.precursor.target_element
    reference_atoms_per_g = (
        reference.active.count(reference_element) / reference.active.molar_mass_g_mol
    )
    promoter_g_per_reference_g = (
        promoter.atomic_ratio_to_reference
        * reference_atoms_per_g
        * promoter_element.molar_mass_g_mol
    )
    return (
        _LinearMass(
            reference.mass.coefficient * promoter_g_per_reference_g,
            reference.mass.fixed_g * promoter_g_per_reference_g,
        ),
        promoter_element,
        precursor,
    )


def _precursor_yield_g_per_g(
    kind: LoadingKind,
    active: ParsedFormula,
    precursor: ParsedFormula,
    target_element: str,
) -> float:
    if kind is LoadingKind.PRECURSOR:
        return 1.0
    active_from_one_mole_precursor_g = (
        precursor.count(target_element) / active.count(target_element) * active.molar_mass_g_mol
    )
    return active_from_one_mole_precursor_g / precursor.molar_mass_g_mol


def _make_requirement(
    *,
    name: str,
    kind: LoadingKind,
    basis_description: str,
    active: ParsedFormula,
    precursor: ParsedFormula,
    target_element: str,
    purity: float,
    active_mass_g: float,
    volume_ml: float,
    fractions: tuple[float, ...],
    atomic_ratio_note: str | None = None,
) -> PrecursorRequirement:
    yield_fraction = _precursor_yield_g_per_g(kind, active, precursor, target_element)
    if not 0 < yield_fraction <= 1.0 + 1e-12:
        raise CompositionError("Computed precursor-to-active mass yield is outside (0, 1]")
    pure_precursor_g = active_mass_g / yield_fraction
    commercial_precursor_g = pure_precursor_g / purity
    precursor_mol = pure_precursor_g / precursor.molar_mass_g_mol
    element_fraction = (
        active.count(target_element)
        * parse_formula(target_element).molar_mass_g_mol
        / active.molar_mass_g_mol
    )
    cycles = tuple(
        CyclePortion(
            cycle=index,
            fraction=fraction,
            precursor_mass_g=commercial_precursor_g * fraction,
            solution_volume_ml=volume_ml * fraction,
        )
        for index, fraction in enumerate(fractions, start=1)
    )
    return PrecursorRequirement(
        name=name,
        kind=kind,
        basis_description=basis_description,
        active_formula=active.normalized,
        target_element=target_element,
        active_component_mass_g=active_mass_g,
        target_element_mass_g=active_mass_g * element_fraction,
        precursor_formula=precursor.normalized,
        precursor_molar_mass_g_mol=precursor.molar_mass_g_mol,
        precursor_purity_fraction=purity,
        pure_precursor_mass_g=pure_precursor_g,
        commercial_precursor_mass_g=commercial_precursor_g,
        precursor_amount_mol=precursor_mol,
        concentration_commercial_g_ml=commercial_precursor_g / volume_ml,
        concentration_pure_mol_l=precursor_mol / (volume_ml / 1000.0),
        cycle_portions=cycles,
        atomic_ratio_note=atomic_ratio_note,
    )


def calculate(request: RecipeRequest) -> RecipeResult:
    """Calculate a supported-catalyst impregnation recipe.

    The function performs recipe arithmetic only. It assumes quantitative retention
    of the named target component and does not predict solubility, deposition,
    drying redistribution, calcination yield, morphology, dispersion, or activity.
    """

    resolved = {
        target.name: _resolve_target(target, request.support_mass_g) for target in request.targets
    }
    promoter_data: list[tuple[PromoterTarget, _LinearMass, ParsedFormula, ParsedFormula]] = []
    for promoter in request.promoters:
        try:
            reference = resolved[promoter.reference_target]
        except KeyError as exc:
            raise CompositionError(
                f"Promoter {promoter.name!r} refers to unknown target {promoter.reference_target!r}"
            ) from exc
        mass, active, precursor = _promoter_linear_mass(promoter, reference)
        promoter_data.append((promoter, mass, active, precursor))

    all_masses = [item.mass for item in resolved.values()] + [item[1] for item in promoter_data]
    coefficient = sum(item.coefficient for item in all_masses)
    fixed_g = sum(item.fixed_g for item in all_masses)
    if coefficient >= 1.0 - 1e-12:
        raise CompositionError(
            "Final-catalyst-basis loadings (including derived promoter mass) leave no "
            "positive support fraction"
        )
    final_mass_g = (request.support_mass_g + fixed_g) / (1.0 - coefficient)

    nominal_volume_ml = (
        request.support_mass_g * request.pore_volume_ml_g
        if request.pore_volume_ml_g is not None
        else None
    )
    if request.solution_volume_ml is not None:
        selected_volume_ml = request.solution_volume_ml
    elif nominal_volume_ml is not None:
        selected_volume_ml = nominal_volume_ml
    else:  # guarded by RecipeRequest validation
        raise CompositionError("A positive solution volume is required")

    fractions = request.cycle_fractions or tuple(
        1.0 / request.cycles for _ in range(request.cycles)
    )
    requirements: list[PrecursorRequirement] = []
    for item in resolved.values():
        target = item.target
        basis = (
            f"{target.loading_percent:g} wt% {target.kind.value} on final-catalyst basis"
            if target.basis is LoadingBasis.FINAL_CATALYST
            else f"{target.loading_percent:g} wt% {target.kind.value} relative to support mass"
        )
        requirements.append(
            _make_requirement(
                name=target.name,
                kind=target.kind,
                basis_description=basis,
                active=item.active,
                precursor=item.precursor,
                target_element=target.precursor.target_element,
                purity=target.precursor.purity_fraction,
                active_mass_g=item.mass.at(final_mass_g),
                volume_ml=selected_volume_ml,
                fractions=fractions,
            )
        )
    for promoter, mass, active, precursor in promoter_data:
        requirements.append(
            _make_requirement(
                name=promoter.name,
                kind=LoadingKind.ELEMENTAL_METAL,
                basis_description=(
                    f"elemental atomic ratio {promoter.target_element}:"
                    f"{resolved[promoter.reference_target].target.precursor.target_element} = "
                    f"{promoter.atomic_ratio_to_reference:g}:1"
                ),
                active=active,
                precursor=precursor,
                target_element=promoter.target_element,
                purity=promoter.precursor.purity_fraction,
                active_mass_g=mass.at(final_mass_g),
                volume_ml=selected_volume_ml,
                fractions=fractions,
                atomic_ratio_note=(
                    f"Derived from {promoter.reference_target!r}; promoter is counted in the "
                    "final formulated mass."
                ),
            )
        )

    total_active_g = sum(row.active_component_mass_g for row in requirements)
    closure = final_mass_g - request.support_mass_g - total_active_g
    warnings = [
        "No precursor-solubility database is applied; verify solution feasibility experimentally.",
        "The calculation does not predict deposition, drying redistribution, calcination loss, "
        "dispersion, morphology, or catalytic performance.",
        "Multi-cycle output is an arithmetic split, not a claim of equivalent catalyst structure.",
    ]
    if request.method is PreparationMethod.INCIPIENT_WETNESS:
        warnings.append(
            "Pore-volume times support-mass is a nominal planning volume, not a universal wetting "
            "truth; support pretreatment, solvent, and measurement method can change it."
        )
        if request.solution_volume_ml is not None and nominal_volume_ml is not None:
            warnings.append(
                "An explicit solution volume overrides the nominal pore-volume product."
            )
    assumptions = (
        "Loading arithmetic assumes quantitative retention/conversion of the named target "
        "component.",
        "Final-catalyst basis means component mass divided by support plus all named retained "
        "components in this model.",
        "Support-relative basis means component mass divided by the initial dry support mass.",
        "Purity correction treats the non-assay fraction as non-target material and does not add "
        "it to the final catalyst mass balance.",
    )
    return RecipeResult(
        request=request,
        final_formulated_mass_g=final_mass_g,
        total_active_component_mass_g=total_active_g,
        nominal_pore_volume_ml=nominal_volume_ml,
        selected_solution_volume_ml=selected_volume_ml,
        requirements=tuple(requirements),
        mass_closure_residual_g=closure,
        warnings=tuple(warnings),
        assumptions=assumptions,
    )
