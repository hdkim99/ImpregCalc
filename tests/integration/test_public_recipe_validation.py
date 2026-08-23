from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from impregcalc.application.service import calculate_recipe

ROOT = Path(__file__).parents[2]
FIXTURES = ROOT / "validation/fixtures"
PREPROCESSOR = ROOT / "validation/preprocess_public_recipes.py"


def _preprocess(case_id: str) -> dict[str, dict[str, Any]]:
    completed = subprocess.run(
        [sys.executable, str(PREPROCESSOR), str(FIXTURES / f"{case_id}.json")],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert isinstance(payload, dict)
    return payload


@pytest.mark.scientific
@pytest.mark.integration
def test_ic_pub_002_support_relative_iron_nonahydrate() -> None:
    request = _preprocess("IC-PUB-002")["reported_basis"]
    result = calculate_recipe(request)
    iron = result.requirements[0]

    # Independent hand arithmetic: 0.03 g Fe and
    # 0.03 * M[Fe(NO3)3.9H2O] / M[Fe].
    assert iron.active_component_mass_g == pytest.approx(0.03, abs=1e-14)
    assert iron.precursor_molar_mass_g_mol == pytest.approx(403.992, abs=1e-9)
    assert iron.pure_precursor_mass_g == pytest.approx(0.21702497985495567, rel=1e-12)
    assert result.nominal_pore_volume_ml == pytest.approx(0.47, abs=1e-14)
    assert iron.precursor_formula == "Fe(NO3)3·9H2O"


@pytest.mark.scientific
@pytest.mark.integration
def test_ic_pub_003_final_basis_niobia_keeps_nominal_and_icp_separate() -> None:
    fixture = json.loads((FIXTURES / "IC-PUB-003.json").read_text(encoding="utf-8"))
    request = _preprocess("IC-PUB-003")["reported_basis"]
    result = calculate_recipe(request)
    niobia = result.requirements[0]

    # Controlled 10 wt% means m_Nb2O5/(0.5 + m_Nb2O5) = 0.10.
    assert result.final_formulated_mass_g == pytest.approx(0.5 / 0.9, rel=1e-12)
    assert niobia.active_component_mass_g == pytest.approx(0.5 / 9.0, rel=1e-12)
    assert niobia.pure_precursor_mass_g == pytest.approx(0.11292889531525474, rel=1e-12)
    assert result.nominal_pore_volume_ml == pytest.approx(0.5 * 0.63, abs=1e-14)
    assert fixture["reported_observations"] == {
        "controlled_nb2o5_loading_percent": 10.0,
        "icp_aes_real_nb2o5_loading_percent": 4.7,
    }
    assert request["targets"][0]["loading_percent"] == 10.0


@pytest.mark.scientific
@pytest.mark.integration
def test_ic_pub_004_coupled_cobalt_platinum_final_basis() -> None:
    request = _preprocess("IC-PUB-004")["reported_basis"]
    result = calculate_recipe(request)
    rows = {row.name: row for row in result.requirements}

    # Coupled denominator: support/(1 - 0.10 - 0.0005).
    expected_final = 1.0 / 0.8995
    assert result.final_formulated_mass_g == pytest.approx(expected_final, rel=1e-12)
    assert rows["cobalt"].active_component_mass_g == pytest.approx(expected_final * 0.10, rel=1e-12)
    assert rows["platinum"].active_component_mass_g == pytest.approx(
        expected_final * 0.0005, rel=1e-12
    )
    assert rows["cobalt"].pure_precursor_mass_g == pytest.approx(0.5490076476746413, rel=1e-12)
    assert rows["platinum"].pure_precursor_mass_g == pytest.approx(0.0011033174301484463, rel=1e-12)
    assert rows["cobalt"].cycle_portions[0].solution_volume_ml == pytest.approx(0.477)
    assert rows["platinum"].cycle_portions[0].solution_volume_ml == pytest.approx(0.477)
    assert abs(result.mass_closure_residual_g) < 1e-12


@pytest.mark.scientific
@pytest.mark.integration
def test_ic_pub_001_preserves_loading_ambiguity_and_volume_discrepancy() -> None:
    requests = _preprocess("IC-PUB-001")
    assert set(requests) == {"final_catalyst", "support_relative"}
    final_result = calculate_recipe(requests["final_catalyst"])
    support_result = calculate_recipe(requests["support_relative"])
    final_mass = final_result.requirements[0].pure_precursor_mass_g
    support_mass = support_result.requirements[0].pure_precursor_mass_g

    assert final_mass == pytest.approx(0.02891516176612963, rel=1e-12)
    assert support_mass == pytest.approx(0.02862601014846833, rel=1e-12)
    assert support_mass < 0.03 and final_mass < 0.03
    assert final_result.selected_solution_volume_ml == pytest.approx(5.0)
    assert final_result.nominal_pore_volume_ml == pytest.approx(1.16)
    assert any("overrides" in warning for warning in final_result.warnings)

    # Forward audit of the reported 0.030 g using C10H14O4Pd (304.638 g/mol).
    reported_pd_g = 0.03 * 106.42 / 304.638
    assert reported_pd_g / 1.0 * 100 == pytest.approx(1.0479979516672249)
    assert reported_pd_g / (1.0 + reported_pd_g) * 100 == pytest.approx(1.0371288624327797)


@pytest.mark.integration
def test_public_source_manifest_and_failure_register_are_complete() -> None:
    manifest = json.loads(
        (ROOT / "validation/public-data-sources.json").read_text(encoding="utf-8")
    )
    failures = json.loads((ROOT / "validation/failure-register.json").read_text(encoding="utf-8"))
    sources = {entry["case_id"]: entry for entry in manifest["sources"]}
    decisions = {entry["case_id"]: entry for entry in failures["entries"]}
    assert set(sources) == {f"IC-PUB-{index:03d}" for index in range(1, 7)}
    assert set(decisions) == set(sources)
    for source in sources.values():
        assert source["doi"].startswith("10.")
        assert len(source["sha256"]) == 64
        assert source["file_size_bytes"] > 0
        assert source["license"]
