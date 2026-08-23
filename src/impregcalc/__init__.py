"""ImpregCalc public API.

Importing this package never imports Tkinter, matplotlib, or another GUI backend.
"""

from .application.service import calculate_recipe, load_request
from .core.calculator import calculate
from .core.formula import parse_formula
from .core.models import (
    LoadingBasis,
    LoadingKind,
    LoadingTarget,
    PrecursorSpec,
    PreparationMethod,
    PromoterTarget,
    RecipeRequest,
    RecipeResult,
)

__all__ = [
    "LoadingBasis",
    "LoadingKind",
    "LoadingTarget",
    "PrecursorSpec",
    "PreparationMethod",
    "PromoterTarget",
    "RecipeRequest",
    "RecipeResult",
    "calculate",
    "calculate_recipe",
    "load_request",
    "parse_formula",
]

__version__ = "0.1.0"
