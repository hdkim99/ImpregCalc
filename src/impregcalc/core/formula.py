"""Chemical formula parsing with explicit hydrate-dot support.

Atomic masses are conventional abridged values based on the IUPAC 2021 table.
For elements whose standard atomic weight is an interval, the conventional value
commonly printed in abridged periodic tables is used. Isotopically enriched
materials are outside the scope of this module.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .errors import FormulaError

# g mol-1. Source and rounding policy are documented in docs/scientific-basis.md.
ATOMIC_WEIGHTS: dict[str, float] = {
    "H": 1.008,
    "He": 4.002602,
    "Li": 6.94,
    "Be": 9.0121831,
    "B": 10.81,
    "C": 12.011,
    "N": 14.007,
    "O": 15.999,
    "F": 18.998403162,
    "Ne": 20.1797,
    "Na": 22.98976928,
    "Mg": 24.305,
    "Al": 26.9815384,
    "Si": 28.085,
    "P": 30.973761998,
    "S": 32.06,
    "Cl": 35.45,
    "Ar": 39.95,
    "K": 39.0983,
    "Ca": 40.078,
    "Sc": 44.955907,
    "Ti": 47.867,
    "V": 50.9415,
    "Cr": 51.9961,
    "Mn": 54.938043,
    "Fe": 55.845,
    "Co": 58.933194,
    "Ni": 58.6934,
    "Cu": 63.546,
    "Zn": 65.38,
    "Ga": 69.723,
    "Ge": 72.630,
    "As": 74.921595,
    "Se": 78.971,
    "Br": 79.904,
    "Kr": 83.798,
    "Rb": 85.4678,
    "Sr": 87.62,
    "Y": 88.905838,
    "Zr": 91.224,
    "Nb": 92.90637,
    "Mo": 95.95,
    "Ru": 101.07,
    "Rh": 102.90549,
    "Pd": 106.42,
    "Ag": 107.8682,
    "Cd": 112.414,
    "In": 114.818,
    "Sn": 118.710,
    "Sb": 121.760,
    "Te": 127.60,
    "I": 126.90447,
    "Xe": 131.293,
    "Cs": 132.90545196,
    "Ba": 137.327,
    "La": 138.90547,
    "Ce": 140.116,
    "Pr": 140.90766,
    "Nd": 144.242,
    "Sm": 150.36,
    "Eu": 151.964,
    "Gd": 157.25,
    "Tb": 158.925354,
    "Dy": 162.500,
    "Ho": 164.930329,
    "Er": 167.259,
    "Tm": 168.934219,
    "Yb": 173.045,
    "Lu": 174.9668,
    "Hf": 178.486,
    "Ta": 180.94788,
    "W": 183.84,
    "Re": 186.207,
    "Os": 190.23,
    "Ir": 192.217,
    "Pt": 195.084,
    "Au": 196.966570,
    "Hg": 200.592,
    "Tl": 204.38,
    "Pb": 207.2,
    "Bi": 208.98040,
}

_TOKEN = re.compile(r"[A-Z][a-z]?|\d+|[()\[\]]")
_OPEN_TO_CLOSE = {"(": ")", "[": "]"}


@dataclass(frozen=True, slots=True)
class ParsedFormula:
    """A parsed neutral formula and its elemental composition."""

    original: str
    normalized: str
    composition: dict[str, int]
    molar_mass_g_mol: float

    def count(self, element: str) -> int:
        """Return atoms of *element* per formula unit."""

        return self.composition.get(element, 0)


def _merge(target: dict[str, int], source: dict[str, int], multiplier: int = 1) -> None:
    for symbol, count in source.items():
        target[symbol] = target.get(symbol, 0) + count * multiplier


def _parse_tokens(
    tokens: list[str], position: int, closing: str | None
) -> tuple[dict[str, int], int]:
    composition: dict[str, int] = {}
    while position < len(tokens):
        token = tokens[position]
        if token in {")", "]"}:
            if closing != token:
                raise FormulaError(f"Unexpected closing delimiter {token!r}")
            return composition, position + 1
        if token in _OPEN_TO_CLOSE:
            subgroup, position = _parse_tokens(tokens, position + 1, _OPEN_TO_CLOSE[token])
            multiplier = 1
            if position < len(tokens) and tokens[position].isdigit():
                multiplier = int(tokens[position])
                position += 1
            if multiplier <= 0:
                raise FormulaError("Formula subscripts must be positive integers")
            _merge(composition, subgroup, multiplier)
            continue
        if token.isdigit():
            raise FormulaError(f"Unexpected coefficient or subscript {token!r}")
        if token not in ATOMIC_WEIGHTS:
            raise FormulaError(f"Unsupported or unknown element symbol: {token}")
        position += 1
        multiplier = 1
        if position < len(tokens) and tokens[position].isdigit():
            multiplier = int(tokens[position])
            position += 1
        if multiplier <= 0:
            raise FormulaError("Formula subscripts must be positive integers")
        composition[token] = composition.get(token, 0) + multiplier
    if closing is not None:
        raise FormulaError(f"Missing closing delimiter {closing!r}")
    return composition, position


def _parse_segment(segment: str) -> dict[str, int]:
    coefficient = 1
    match = re.match(r"^(\d+)(?=[A-Z(\[])", segment)
    if match:
        coefficient = int(match.group(1))
        segment = segment[match.end() :]
    if not segment:
        raise FormulaError("Empty hydrate segment")
    tokens = _TOKEN.findall(segment)
    if "".join(tokens) != segment:
        raise FormulaError(
            f"Unsupported formula syntax in {segment!r}; charges and fractional subscripts "
            "are not accepted"
        )
    composition, position = _parse_tokens(tokens, 0, None)
    if position != len(tokens):
        raise FormulaError(f"Could not parse complete formula segment {segment!r}")
    return {symbol: count * coefficient for symbol, count in composition.items()}


def parse_formula(formula: str) -> ParsedFormula:
    """Parse a chemical formula, including ``Co(NO3)2·6H2O``-style hydrates.

    Both the Unicode middle dot and an ASCII full stop are accepted as hydrate
    separators. Charges, isotope labels, fractional stoichiometry, and adducts
    written with ``+`` are intentionally rejected instead of guessed.
    """

    normalized = formula.strip().replace(" ", "").replace("∙", "·").replace("•", "·")
    if not normalized:
        raise FormulaError("Chemical formula must not be empty")
    segments = re.split(r"[·.]", normalized)
    if any(not segment for segment in segments):
        raise FormulaError("Hydrate separator must have a formula on both sides")
    composition: dict[str, int] = {}
    for segment in segments:
        _merge(composition, _parse_segment(segment))
    mass = sum(ATOMIC_WEIGHTS[symbol] * count for symbol, count in composition.items())
    canonical = "·".join(segments)
    return ParsedFormula(formula, canonical, composition, mass)
