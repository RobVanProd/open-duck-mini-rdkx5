from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t212_contract_source() -> None:
    builder = (
        ROOT
        / "tools/build_t212_t210_postexport_composition_preregistration.py"
    ).read_text(encoding="utf-8")
    runner = (
        ROOT / "tools/run_t212_t210_postexport_composition.py"
    ).read_text(encoding="utf-8")
    assert "PASS_T211B_COST_INIT_BACKEND_RECOVERY" in builder
    assert "T164_COMPOSED_FINAL_FOR_ALL_THREE_T210_EXPORTS" in builder
    assert "output_sensitivity_is_diagnostic_only" in builder
    assert "t172.transform" in runner
    assert "all_graphs_change_only_nominal_pair" in runner
    assert "all_inactive_routes_bit_exact" in runner
    assert "all_x0_outputs_bit_exact" in runner
    assert "behavior_cells" in runner


def test_t212_result_when_present() -> None:
    path = ANALYSIS / "t212_t210_postexport_composition_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T212_T210_POSTEXPORT_COMPOSITION"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert (
        value["decision"]
        == "EARN_T213_T210_NOMINAL_BEHAVIOR_MATRIX_"
        "PREREGISTRATION_ONLY"
    )
    assert value["execution"]["behavior_cells"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["authority"]["behavior_matrix"] is False
    assert value["authority"]["gate5"] is False
