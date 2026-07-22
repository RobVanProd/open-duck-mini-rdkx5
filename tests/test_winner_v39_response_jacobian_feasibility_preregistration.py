from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "outputs/analysis/winner_v39_response_jacobian_feasibility_preregistration.json"


def test_preregistration_is_exact_when_present() -> None:
    if not PREREG.exists():
        return
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_WINNER_V39_RESPONSE_JACOBIAN_FEASIBILITY"
    assert value["decision"] == "AUTHORIZE_ONE_CPU_ONLY_RESPONSE_JACOBIAN_COM_X_NEG_SCREEN"
    screen = value["screen"]
    assert screen == {
        "configuration_ids": ["COM_X_NEG"],
        "actuator_plants": ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"],
        "controlled_action_indices": [2, 3, 4, 11, 12, 13],
        "response_dimensions": ["base_pitch_rad", "body_pitch_rate_rad_s"],
        "control_dimensions": ["hip_pitch_magnitude", "knee", "ankle"],
        "duration_ticks": 250,
        "response_horizon_ticks": 8,
        "finite_difference_scale": "minimum paired graph action delta per mirrored axis",
        "solver": "numpy.linalg.lstsq(rcond=None), minimum-norm correction",
        "correction_bound": "one finite-difference step per mirrored axis",
        "expected_cells": 2,
        "constraints": (
            "Every response rollout and selected action uses the exact graph action "
            "boundary and unchanged P30 or P31/34 actuator bridge."
        ),
    }
    assert value["pass_rule"] == {
        "both_plants_pass_full_250_tick_support_gate": True,
        "all_response_jacobians_full_row_rank": True,
        "all_selected_actions_graph_bounded": True,
        "all_cells_use_nonzero_control": True,
        "closest_result_selection": False,
    }
    assert value["execution_now"] == {
        "response_jacobian_cells": 0,
        "optimizer_updates": 0,
        "locomotion_training_steps": 0,
        "robot_or_rdk_access": 0,
    }


def test_source_manifest_is_exact_when_present() -> None:
    if not PREREG.exists():
        return
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    for item in value["sources"].values():
        observed = hashlib.sha256(
            (ROOT / item["path"]).read_bytes().replace(b"\r\n", b"\n")
        ).hexdigest()
        assert item["hash_mode"] == "lf"
        assert observed == item["sha256"]
    canonical = hashlib.sha256(
        json.dumps(value["sources"], sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    assert canonical == value["source_manifest_sha256"]
