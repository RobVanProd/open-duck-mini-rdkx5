import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t170_hosted_preregistration_contract() -> None:
    path = ANALYSIS / "t170_eight_stratum_head_hosted_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PREREGISTERED_T170_EIGHT_STRATUM_HEAD_HOSTED_CONTINUATION"
    )
    assert value["failed_checks"] == []
    assert value["training"]["body_configuration_strata"] == 8
    assert value["training"]["environments_per_stratum"] == 32
    assert value["training"]["actor_trainable_groups"] == [
        "negative_adapter_location"
    ]
    assert value["training"]["retry"] is False
    assert value["training"]["same_run_resume"] is False
    assert value["post_training"]["both_checkpoint_persistence_required"]


def test_t170_package_contract() -> None:
    path = ANALYSIS / "t170_eight_stratum_head_hosted_package_contract.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T170_EIGHT_STRATUM_HEAD_HOSTED_PACKAGE"
    assert value["failed_checks"] == []
    assert value["checks"]["eight_stratum_readback_frozen"]
    assert value["checks"]["credentials_absent"]
    assert value["checks"]["robot_access_material_absent"]
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["hosted_sessions_opened"] == 0
