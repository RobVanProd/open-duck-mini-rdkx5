import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def test_v119_cpu_result_passes_without_training_rerun() -> None:
    value = json.loads(
        (
            ANALYSIS / "winner_v119_transition_cpu_result.json"
        ).read_text(encoding="utf-8")
    )
    assert value["status"] == (
        "PASS_WINNER_V119_TRANSITION_CPU_SMOKE_RECOVERED"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["recovery"]["classification"] == "reporting_only"
    assert value["recovery"]["training_rerun"] is False
    assert value["transition_contract"]["default_off_bit_exact"]
    assert value["transition_contract"]["analytic_max_abs_error"] == 0.0
    assert value["transition_contract"]["max_rate_excess_rad"] <= 1e-7
    assert value["training"]["checkpoint_steps"] == [0, 1024]
    assert value["training"]["onnx_steps"] == [0, 1024]
    assert len(value["training"]["policy_leaf_deltas"]) == 15
    assert all(
        delta > 0.0
        for delta in value["training"]["policy_leaf_deltas"].values()
    )
    assert len(value["deployed_onnx"]) == 2
    assert all(
        row["inference"]["pass"]
        and row["recovered_matches_existing"]
        for row in value["deployed_onnx"]
    )
    assert value["authority"]["hosted_preregistration_authorized"]
    assert value["authority"]["hosted_training_authorized"] is False
    assert value["authority"]["colab_authorized"] is False
