import pytest

from impregcalc.core.errors import FormulaError
from impregcalc.core.formula import parse_formula


@pytest.mark.scientific
@pytest.mark.parametrize(
    ("formula", "element", "count", "expected_mass"),
    [
        ("Co(NO3)2·6H2O", "H", 12, 291.031),
        ("Ni(NO3)2·6H2O", "Ni", 1, 290.791),
        ("Fe(NO3)3·9H2O", "O", 18, 403.992),
        ("Cu(NO3)2·3H2O", "Cu", 1, 241.599),
    ],
)
def test_hydrated_precursors(formula: str, element: str, count: int, expected_mass: float) -> None:
    parsed = parse_formula(formula)
    assert parsed.count(element) == count
    assert parsed.molar_mass_g_mol == pytest.approx(expected_mass, abs=0.002)


def test_ascii_hydrate_dot_and_nested_groups() -> None:
    parsed = parse_formula("Al2(SO4)3.18H2O")
    assert parsed.composition == {"Al": 2, "S": 3, "O": 30, "H": 36}


@pytest.mark.parametrize("formula", ["", "Co(NO3)2+6H2O", "Co2+", "XxO", "Co(NO3"])
def test_unsupported_or_invalid_formula_fails_explicitly(formula: str) -> None:
    with pytest.raises(FormulaError):
        parse_formula(formula)


def test_zero_subscript_is_rejected() -> None:
    with pytest.raises(FormulaError, match="positive"):
        parse_formula("Co0O")
