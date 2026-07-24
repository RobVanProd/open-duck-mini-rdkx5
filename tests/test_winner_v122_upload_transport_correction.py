import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_v122_transport_correction_preserves_exact_package() -> None:
    value = load("winner_v122_upload_transport_correction.json")
    assert value["status"] == (
        "PASS_WINNER_V122_UPLOAD_TRANSPORT_CORRECTION"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert len(value["chunks"]) == 4
    assert value["reconstruction"] == value["package"] | {"ordered": True}
    prior = value["prior_prelaunch_attempt"]
    assert prior["full_package_upload_attempts"] == 2
    assert prior["executor_started"] is False
    assert prior["optimizer_steps"] == 0
    assert prior["formal_behavior_cells"] == 0
    assert prior["session_stopped"] is True
    assert value["decision"] == (
        "AUTHORIZE_ONE_V122B_CHUNKED_TRANSPORT_LAUNCH"
    )
    assert value["authority"]["training_retry"] is False
    assert value["authority"]["one_chunked_transport_training_launch"] is True


def test_v122b_launch_keeps_training_payload_and_reconstructs() -> None:
    value = load("winner_v122b_chunked_colab_launch_contract.json")
    assert value["status"] == (
        "PASS_WINNER_V122B_CHUNKED_COLAB_LAUNCH_CONTRACT"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert len(value["chunks"]) == 4
    assert value["session"]["training_session_count"] == 1
    assert value["session"]["prior_prelaunch_transport_session_count"] == 1
    assert value["recovery"][
        "reconstruct_and_verify_package_before_launch"
    ] is True
    assert value["recovery"]["training_retry"] is False
    assert value["recovery"]["training_resume"] is False
    assert value["authority"]["one_exact_chunked_cli_launch"] is True
    assert value["authority"]["additional_training_attempt"] is False
    assert value["authority"]["gate5"] is False
