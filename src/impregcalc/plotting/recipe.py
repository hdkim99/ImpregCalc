"""Recipe summary visualization."""

from __future__ import annotations

from pathlib import Path

from impregcalc.core.models import RecipeResult


def save_recipe_figure(result: RecipeResult, path: str | Path) -> Path:
    """Save a result-derived PNG, SVG, or PDF without requiring a GUI backend."""

    try:
        import matplotlib
    except ImportError as exc:
        raise RuntimeError(
            'Plot export requires the optional dependency: pip install "impregcalc[plot]"'
        ) from exc
    matplotlib.use("Agg", force=True)
    from matplotlib import pyplot as plt

    destination = Path(path)
    if destination.suffix.lower() not in {".png", ".svg", ".pdf"}:
        raise ValueError("Figure suffix must be .png, .svg, or .pdf")
    labels = [row.precursor_formula for row in result.requirements]
    masses = [row.commercial_precursor_mass_g for row in result.requirements]
    figure, axes = plt.subplots(1, 2, figsize=(12.8, 6.4), constrained_layout=True)
    axes[0].barh(labels, masses, color="#287271")
    axes[0].set_xlabel("Commercial precursor to weigh / g")
    axes[0].set_title("Impregnation recipe")
    axes[0].grid(axis="x", alpha=0.25)
    axes[1].axis("off")
    text = (
        f"{result.request.support_name}\n"
        f"Support: {result.request.support_mass_g:.4g} g\n"
        f"Solution: {result.selected_solution_volume_ml:.4g} mL\n"
        f"Cycles: {result.request.cycles}\n\n"
        "Recipe arithmetic only\n"
        "Solubility and morphology are not predicted"
    )
    axes[1].text(0.05, 0.75, text, va="top", fontsize=15, linespacing=1.5)
    figure.suptitle("ImpregCalc — explicit loading basis and precursor stoichiometry", fontsize=17)
    destination.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(destination, dpi=100)
    plt.close(figure)
    return destination
