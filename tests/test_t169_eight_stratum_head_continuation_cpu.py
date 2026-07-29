import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t169_preregistration_contract() -> None:
    path = (
        ANALYSIS
        / "t169_eight_stratum_head_continuation_cpu_preregistration.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PREREGISTERED_T169_EIGHT_STRATUM_HEAD_CONTINUATION_CPU_CONTRACT"
    )
    assert value["failed_checks"] == []
    assert value["training"]["timesteps"] == 1024
    assert value["training"]["num_envs"] == 8
    assert value["training"]["environments_per_stratum"] == 1
    assert value["mechanism"]["trainable_actor_groups"] == [
        "negative_adapter_location"
    ]
    assert len(value["mechanism"]["endpoint_names"]) == 8
    assert value["authority"]["hosted_training"] is False


def test_t169_result_contract() -> None:
    path = (
        ANALYSIS / "t169_eight_stratum_head_continuation_cpu_result.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    if value["failed_checks"]:
        assert (
            value["status"]
            == "HOLD_T169_EIGHT_STRATUM_HEAD_CONTINUATION_CPU_CONTRACT"
        )
        return
    assert (
        value["status"]
        == "PASS_T169_EIGHT_STRATUM_HEAD_CONTINUATION_CPU_CONTRACT"
    )
    assert (
        value["decision"]
        == "EARN_T170_EIGHT_STRATUM_HEAD_HOSTED_CONTINUATION_"
        "PREREGISTRATION_ONLY"
    )
    assert value["endpoint_contract"]["counts"] == {
        name: 1 for name in value["endpoint_contract"]["names"]
    }
    tree = value["tree_contract"]
    assert len(tree["nominal_expert_actor_leaf_deltas"]) == 2
    assert all(
        delta > 0
        for delta in tree["nominal_expert_actor_leaf_deltas"].values()
    )
    assert all(
        delta == 0
        for delta in tree["protected_mature_actor_leaf_deltas"].values()
    )
    assert all(
        delta == 0 for delta in tree["normalizer_leaf_deltas"].values()
    )
    assert value["execution"]["optimizer_steps"] == 1024
    assert value["execution"]["formal_behavior_cells"] == 0
    assert value["execution"]["hosted_compute_units"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
