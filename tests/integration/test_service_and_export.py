from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from impregcalc.application.service import calculate_recipe, load_request
from impregcalc.io import format_markdown, write_result

EXAMPLE = Path("examples/co_ru_iwi.json")


@pytest.mark.integration
def test_example_loads_and_calculates() -> None:
    result = calculate_recipe(EXAMPLE)
    assert len(result.requirements) == 2
    assert abs(result.mass_closure_residual_g) < 1e-12
    assert result.requirements[0].precursor_formula == "Co(NO3)2·6H2O"


@pytest.mark.integration
def test_json_round_trip_has_units_and_definitions(tmp_path: Path) -> None:
    result = calculate_recipe(load_request(EXAMPLE))
    output = write_result(result, tmp_path / "recipe.json")
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "1.0"
    assert "selected_solution_volume_ml" in payload
    assert payload["requirements"][0]["basis"].startswith("15 wt% elemental_metal")
    assert payload["warnings"]


@pytest.mark.integration
def test_markdown_is_laboratory_readable(tmp_path: Path) -> None:
    result = calculate_recipe(EXAMPLE)
    text = format_markdown(result)
    assert "Required commercial precursor to weigh" in text
    assert "Pore volume" in text
    assert "Solubility" in text or "solubility" in text
    assert "Co(NO3)2·6H2O" in text
    assert write_result(result, tmp_path / "recipe.md").is_file()


@pytest.mark.integration
def test_csv_export(tmp_path: Path) -> None:
    output = write_result(calculate_recipe(EXAMPLE), tmp_path / "recipe.csv")
    with output.open(encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 2
    assert float(rows[0]["commercial_precursor_mass_g"]) > 0


@pytest.mark.integration
def test_xlsx_export_contains_recipe_cycles_and_notes(tmp_path: Path) -> None:
    openpyxl = pytest.importorskip("openpyxl")
    output = write_result(calculate_recipe(EXAMPLE), tmp_path / "recipe.xlsx")
    workbook = openpyxl.load_workbook(output, read_only=True)
    assert workbook.sheetnames == [
        "Recipe",
        "Components",
        "Cycles",
        "Assumptions and warnings",
    ]
