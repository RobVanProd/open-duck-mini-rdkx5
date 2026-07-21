from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/analysis/winner_v20_joint_recurrent_support_cpu_v2_result.json"
IMPORTER = ROOT / "tools/import_winner_v20_joint_recurrent_support_cpu_v2_result.py"


def test_two_update_cpu_proof_passes_with_recurrent_opening() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V20_JOINT_RECURRENT_SUPPORT_CPU_CONTRACT"
    assert value["decision"] == (
        "AUTHORIZE_SEPARATE_JOINT_RECURRENT_100_UPDATE_PREREGISTRATION_ONLY"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    recurrent = {"obs_weight", "previous_action_weight", "hidden_weight", "hidden_bias"}
    updates = value["optimization"]["updates"]
    assert all(updates[0]["gradient_max_abs"][name] == 0.0 for name in recurrent)
    assert all(updates[1]["gradient_max_abs"][name] > 0.0 for name in recurrent)
    assert all(updates[1]["leaf_max_abs_delta"][name] > 0.0 for name in recurrent)
    assert [row["sampled_hidden_replay_max_abs_error"] for row in value["rollouts"]] == [
        2.980232238769531e-07,
        3.5762786865234375e-07,
    ]
    assert value["repository_attribution"]["github_run_id"] == 29853236226
    assert value["repository_attribution"]["github_artifact_id"] == 8504369891
    assert value["authority"]["robot_clearance"] is False


def test_v2_importer_has_no_execution_or_hardware_authority() -> None:
    source = IMPORTER.read_text(encoding="utf-8")
    assert "onnxruntime" not in source
    assert "import jax" not in source
    assert "--hardware-authorized" not in source
