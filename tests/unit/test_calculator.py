import pytest

from impregcalc.core.calculator import calculate
from impregcalc.core.errors import CompositionError
from impregcalc.core.formula import ATOMIC_WEIGHTS, parse_formula
from impregcalc.core.models import (
    LoadingBasis,
    LoadingKind,
    LoadingTarget,
    PrecursorSpec,
    PreparationMethod,
    PromoterTarget,
    RecipeRequest,
)


def target(
    *,
    name: str = "cobalt",
    kind: LoadingKind = LoadingKind.ELEMENTAL_METAL,
    basis: LoadingBasis = LoadingBasis.FINAL_CATALYST,
    loading: float = 15.0,
    active: str | None = "Co",
    precursor: str = "Co(NO3)2·6H2O",
    element: str = "Co",
    purity: float = 1.0,
) -> LoadingTarget:
    return LoadingTarget(
        name=name,
        kind=kind,
        basis=basis,
        loading_percent=loading,
        active_formula=active,
        precursor=PrecursorSpec(precursor, element, purity),
    )


def request(*targets: LoadingTarget, **kwargs: object) -> RecipeRequest:
    return RecipeRequest(
        support_name="Al2O3",
        support_mass_g=float(kwargs.get("support_mass_g", 8.0)),
        method=PreparationMethod.INCIPIENT_WETNESS,
        pore_volume_ml_g=0.72,
        targets=targets or (target(),),
        cycles=int(kwargs.get("cycles", 1)),
        cycle_fractions=kwargs.get("cycle_fractions"),  # type: ignore[arg-type]
        promoters=kwargs.get("promoters", ()),  # type: ignore[arg-type]
    )


@pytest.mark.scientific
def test_elemental_final_basis_hand_calculation() -> None:
    result = calculate(request(target(loading=15.0)))
    expected_final = 8.0 / 0.85
    expected_co = 0.15 * expected_final
    expected_precursor = (
        expected_co * parse_formula("Co(NO3)2·6H2O").molar_mass_g_mol / ATOMIC_WEIGHTS["Co"]
    )
    row = result.requirements[0]
    assert result.final_formulated_mass_g == pytest.approx(expected_final)
    assert row.active_component_mass_g == pytest.approx(expected_co)
    assert row.commercial_precursor_mass_g == pytest.approx(expected_precursor)
    assert result.mass_closure_residual_g == pytest.approx(0.0, abs=1e-12)


@pytest.mark.scientific
def test_support_relative_loading_is_not_final_basis() -> None:
    result = calculate(request(target(basis=LoadingBasis.SUPPORT_RELATIVE, loading=15.0)))
    assert result.requirements[0].active_component_mass_g == pytest.approx(1.2)
    assert result.final_formulated_mass_g == pytest.approx(9.2)
    assert pytest.approx(13.043478) == 100 * 1.2 / 9.2


@pytest.mark.scientific
def test_oxide_loading_uses_oxide_stoichiometry() -> None:
    item = target(kind=LoadingKind.METAL_OXIDE, active="Co3O4", loading=15.0)
    result = calculate(request(item))
    row = result.requirements[0]
    expected_oxide = 0.15 * (8.0 / 0.85)
    expected_moles_oxide = expected_oxide / parse_formula("Co3O4").molar_mass_g_mol
    expected_precursor_moles = 3 * expected_moles_oxide
    assert row.active_component_mass_g == pytest.approx(expected_oxide)
    assert row.precursor_amount_mol == pytest.approx(expected_precursor_moles)
    assert row.target_element_mass_g < row.active_component_mass_g


@pytest.mark.scientific
def test_precursor_loading_is_distinct_from_elemental_loading() -> None:
    item = target(kind=LoadingKind.PRECURSOR, active=None, loading=10.0)
    result = calculate(request(item))
    row = result.requirements[0]
    assert row.active_formula == "Co(NO3)2·6H2O"
    assert row.pure_precursor_mass_g == pytest.approx(8.0 / 0.9 * 0.1)
    assert row.target_element_mass_g < row.active_component_mass_g


def test_purity_adjusts_weighed_mass_only() -> None:
    pure = calculate(request(target(purity=1.0))).requirements[0]
    impure = calculate(request(target(purity=0.98))).requirements[0]
    assert impure.pure_precursor_mass_g == pytest.approx(pure.pure_precursor_mass_g)
    assert impure.commercial_precursor_mass_g == pytest.approx(
        pure.commercial_precursor_mass_g / 0.98
    )


@pytest.mark.scientific
def test_coimpregnation_coupled_final_mass() -> None:
    cobalt = target(loading=15.0)
    ruthenium = target(
        name="ruthenium",
        loading=0.2,
        active="Ru",
        precursor="RuCl3",
        element="Ru",
    )
    result = calculate(request(cobalt, ruthenium))
    assert result.final_formulated_mass_g == pytest.approx(8.0 / (1 - 0.15 - 0.002))
    first_fraction = result.requirements[0].active_component_mass_g / result.final_formulated_mass_g
    second_fraction = (
        result.requirements[1].active_component_mass_g / result.final_formulated_mass_g
    )
    assert first_fraction == pytest.approx(0.15)
    assert second_fraction == pytest.approx(0.002)


@pytest.mark.scientific
def test_promoter_atomic_ratio_is_reproduced() -> None:
    promoter = PromoterTarget(
        name="Ru promoter",
        target_element="Ru",
        reference_target="cobalt",
        atomic_ratio_to_reference=0.01,
        precursor=PrecursorSpec("RuCl3", "Ru", 0.99),
    )
    result = calculate(request(target(), promoters=(promoter,)))
    co, ru = result.requirements
    co_moles = co.target_element_mass_g / ATOMIC_WEIGHTS["Co"]
    ru_moles = ru.target_element_mass_g / ATOMIC_WEIGHTS["Ru"]
    assert ru_moles / co_moles == pytest.approx(0.01)
    assert result.mass_closure_residual_g == pytest.approx(0.0, abs=1e-12)


def test_iwi_volume_is_nominal_pore_volume_product() -> None:
    result = calculate(request(target()))
    assert result.nominal_pore_volume_ml == pytest.approx(5.76)
    assert result.selected_solution_volume_ml == pytest.approx(5.76)
    assert any("nominal" in item.lower() for item in result.warnings)


def test_wet_impregnation_uses_explicit_solution_volume() -> None:
    recipe = RecipeRequest(
        support_name="SiO2",
        support_mass_g=10,
        method=PreparationMethod.WET_IMPREGNATION,
        solution_volume_ml=50,
        targets=(target(basis=LoadingBasis.SUPPORT_RELATIVE),),
    )
    result = calculate(recipe)
    assert result.nominal_pore_volume_ml is None
    assert result.selected_solution_volume_ml == 50


def test_equal_multicycle_is_arithmetic_split() -> None:
    result = calculate(request(target(), cycles=3))
    portions = result.requirements[0].cycle_portions
    assert sum(item.precursor_mass_g for item in portions) == pytest.approx(
        result.requirements[0].commercial_precursor_mass_g
    )
    assert [item.fraction for item in portions] == pytest.approx([1 / 3, 1 / 3, 1 / 3])
    assert any("arithmetic split" in item for item in result.warnings)


def test_custom_cycle_fractions() -> None:
    result = calculate(request(target(), cycles=2, cycle_fractions=(0.4, 0.6)))
    assert [item.fraction for item in result.requirements[0].cycle_portions] == [0.4, 0.6]


@pytest.mark.parametrize("loading", [0, -1])
def test_zero_and_negative_loadings_rejected(loading: float) -> None:
    with pytest.raises(CompositionError):
        target(loading=loading)


def test_impossible_final_composition_rejected() -> None:
    one = target(name="one", loading=60)
    two = target(name="two", loading=40, active="Ni", precursor="Ni(NO3)2·6H2O", element="Ni")
    with pytest.raises(CompositionError, match="support fraction"):
        calculate(request(one, two))


def test_missing_promoter_reference_rejected() -> None:
    promoter = PromoterTarget(
        name="Ru",
        target_element="Ru",
        reference_target="missing",
        atomic_ratio_to_reference=0.01,
        precursor=PrecursorSpec("RuCl3", "Ru"),
    )
    with pytest.raises(CompositionError, match="unknown target"):
        calculate(request(target(), promoters=(promoter,)))
