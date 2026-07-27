import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_t30_is_one_exact_unwrapped_cell() -> None:
    payload = load("t30_t28_margin_causality_preregistration.json")
    assert payload["status"] == "PREREGISTERED_T30_T28_MARGIN_CAUSAL_AB"
    assert payload["failed_checks"] == []
    assert payload["cell"] == {
        "condition": {
            "condition_index": 3,
            "id": "JOINT_FRICTIONLOSS_LO",
            "override": {"joint_frictionloss_scale": 0.9},
        },
        "checkpoint_id": "T23_SUPPORT_FINAL",
        "fit_id": "p30",
        "command_x_m_s": 0.077,
        "seed": 167931544,
        "duration_s": 12.0,
    }
    assert payload["unwrapped_policy"]["checkpoint_id"] == "T23_SUPPORT_FINAL"
    assert payload["fit"]["fit_id"] == "p30"
    assert payload["wrapped_failure"]["samples"] == 332
    assert payload["wrapped_failure"]["first_intervention_tick"] == 52
    assert payload["wrapped_failure"]["intervention_count"] == 5
    assert payload["authority"]["execute_one_unwrapped_cpu_cell"]
    assert not payload["authority"]["training"]
    assert not payload["authority"]["gate5"]
    assert not payload["authority"]["rdkx5_or_robot"]


def test_t30_mixed_outcome_closes_posthoc_t28() -> None:
    raw = load("t30_t28_margin_causality_result.json")
    payload = load("t30_t28_margin_causality_reconciliation.json")
    assert raw["source_cell"]["behavior"]["samples"] == 600
    assert not raw["source_cell"]["cell_green"]
    assert raw["wrapped_cell"]["samples"] == 332
    assert raw["causal_comparison"]["pre_intervention_exact"]
    assert payload["status"] == "PASS_T30_MIXED_OUTCOME_RECONCILIATION"
    assert payload["decision"] == "CLOSE_T28_POSTHOC_MARGIN_TRANSFORM"
    assert payload["failed_checks"] == []
    assert payload["facts"]["unwrapped_samples"] == 600
    assert payload["facts"]["wrapped_samples"] == 332
    assert payload["authority"]["posthoc_t28_candidate_closed"]
    assert payload["authority"]["mechanism_contract_review"]
    assert not payload["authority"]["training"]
    assert not payload["authority"]["gate5"]
