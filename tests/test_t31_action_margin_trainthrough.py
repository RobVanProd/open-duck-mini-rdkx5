import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_t31_is_exactly_one_cpu_update_from_t23_half() -> None:
    payload = load(
        "t31_action_margin_trainthrough_cpu_preregistration.json"
    )
    assert (
        payload["status"]
        == "PREREGISTERED_T31_ACTION_MARGIN_TRAINTHROUGH_CPU_SMOKE"
    )
    assert payload["failed_checks"] == []
    assert payload["selection_evidence"]["half_margin_green_cells"] == 24
    assert payload["selection_evidence"]["posthoc_wrapper_closed"]
    assert payload["selection_evidence"]["reward_changes"] == 0
    assert not payload["selection_evidence"]["new_scalar_search"]
    assert payload["cpu_smoke"]["simulator_steps"] == 1024
    assert payload["cpu_smoke"]["exports"] == [0, 1024]
    assert payload["cpu_smoke"]["restore"] == (
        "T23_SUPPORT_HALF step 1003520"
    )


def test_t31_authority_is_cpu_only() -> None:
    payload = load(
        "t31_action_margin_trainthrough_cpu_preregistration.json"
    )
    assert payload["transition"]["default_off"]
    assert payload["transition"]["requires"] == (
        "--winner_t19_support_trainthrough"
    )
    assert payload["authority"]["execute_1024_cpu_steps"]
    assert not payload["authority"]["hosted_training"]
    assert not payload["authority"]["behavior_evaluation"]
    assert not payload["authority"]["gate5"]
    assert not payload["authority"]["rdkx5_or_robot"]
    assert not payload["authority"]["torque_or_motion"]


def test_t31_all_frozen_receipts_have_explicit_kind() -> None:
    payload = load(
        "t31_action_margin_trainthrough_cpu_preregistration.json"
    )
    receipts = [*payload["sources"].values(), *payload["assets"].values()]
    assert receipts
    assert all(item["kind"] in {"file", "directory"} for item in receipts)
