import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def test_v118_closes_tightening_and_selects_transition_match() -> None:
    value = json.loads(
        (
            ANALYSIS / "winner_v118_nominal_failure_attribution.json"
        ).read_text(encoding="utf-8")
    )
    assert value["status"] == (
        "PASS_WINNER_V118_NOMINAL_FAILURE_ATTRIBUTION"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["decision"] == (
        "PREREGISTER_V119_DEFAULT_OFF_AND_CPU_TRANSITION_CONTRACT"
    )
    assert value["closed_routes"][
        "repeat_output_only_rate_formula"
    ]
    assert value["closed_routes"]["v118_checkpoint_selection"]
    assert value["selected_mechanism"]["name"] == (
        "V119_TRAIN_TRANSITION_MATCH"
    )
    assert value["selected_mechanism"][
        "train_time_actual_centered_guard_margin_rad"
    ] == 0.165
    assert value["selected_mechanism"][
        "train_time_postguard_rate_projection"
    ]
    assert value["selected_mechanism"][
        "applied_target_observation_preserved"
    ]
    assert value["authority"][
        "v119_cpu_contract_preregistration_authorized"
    ]
    assert value["authority"]["training_authorized"] is False
    assert value["authority"]["colab_authorized"] is False
