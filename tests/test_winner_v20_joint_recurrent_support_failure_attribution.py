from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v20_joint_recurrent_support_failure_attribution.py"
RESULT = ROOT / "outputs/analysis/winner_v20_joint_recurrent_support_failure_attribution.json"


def load():
    spec = importlib.util.spec_from_file_location("winner_v20_failure_attribution", BUILDER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_failure_attribution_is_rederived_from_imported_evidence() -> None:
    module = load()
    expected = module.build_payload()
    actual = json.loads(RESULT.read_text(encoding="utf-8"))
    assert actual == expected
    assert actual["status"] == "PASS_WINNER_V20_SUPPORT_FAILURE_ATTRIBUTION"
    assert actual["decision"] == (
        "AUTHORIZE_PREDICTOR_PRESERVING_JOINT_OBJECTIVE_CPU_CONTRACT_ONLY"
    )


def test_support_failures_are_exclusively_tilt_and_persist() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    half, final = value["support_gate"]["checkpoints"]
    assert (half["failing_support_cells"], final["failing_support_cells"]) == (16, 20)
    assert half["terminal_failed_check_counts"] == {"roll_pitch": 16}
    assert final["terminal_failed_check_counts"] == {"roll_pitch": 20}
    assert value["findings"]["current_torque_contact_base_and_determinism_not_causal"]


def test_predictor_preservation_is_selected_without_authorizing_training() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["findings"][
        "frozen_auxiliary_head_with_changed_recurrent_representation_is_incompatible"
    ]
    assert not value["findings"]["flat_transport_equation_selected"]
    assert value["authority"]["optimizer_updates_authorized_now"] == 0
    assert not value["authority"]["locomotion_training_authorized"]
    assert not value["authority"]["robot_clearance"]
