"""Domain-specific exceptions."""


class ImpregCalcError(ValueError):
    """Base class for an invalid scientific input or unsupported convention."""


class FormulaError(ImpregCalcError):
    """Raised when a chemical formula is outside the documented grammar."""


class CompositionError(ImpregCalcError):
    """Raised when target loadings cannot define a physical mass balance."""
