#!/usr/bin/env python3
"""Record the pre-outcome Winner-v20 two-stage authority correction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v20_two_stage_authority_correction.json"
MARKDOWN = ANALYSIS / "WINNER_V20_TWO_STAGE_AUTHORITY_CORRECTION_20260721.md"
V6_INTERFACE = ANALYSIS / "winner_v6_dynamic_calibration_interface_preregistration.json"
V12_DESIGN = ANALYSIS / "winner_v12_calibrator_training_preregistration.json"
V20_TRAINING = ANALYSIS / "winner_v20_joint_recurrent_support_training_preregistration.json"
SOURCES = {
    "builder": Path("tools/build_winner_v20_two_stage_authority_correction.py"),
    "tests": Path("tests/test_winner_v20_two_stage_authority_correction.py"),
    "v6_interface": Path(
        "outputs/analysis/winner_v6_dynamic_calibration_interface_preregistration.json"
    ),
    "v12_design": Path(
        "outputs/analysis/winner_v12_calibrator_training_preregistration.json"
    ),
    "v20_training": Path(
        "outputs/analysis/winner_v20_joint_recurrent_support_training_preregistration.json"
    ),
    "v20_gate_builder": Path(
        "tools/build_winner_v20_joint_recurrent_support_gate_preregistration.py"
    ),
    "v20_gate_runner": Path("tools/run_winner_v20_joint_recurrent_support_gate.py"),
    "v20_gate_importer": Path(
        "tools/import_winner_v20_joint_recurrent_support_gate_result.py"
    ),
    "network_interface": Path("patches/winner_v6_dynamic_calibration_networks.py"),
}


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def main() -> int:
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("Winner-v20 authority correction already exists")
    v6 = json.loads(V6_INTERFACE.read_text(encoding="utf-8"))
    v12 = json.loads(V12_DESIGN.read_text(encoding="utf-8"))
    v20 = json.loads(V20_TRAINING.read_text(encoding="utf-8"))
    training_order = v6["after_runtime_review_only"]["training_order"]
    if training_order != [
        "train only the calibrator/response encoder on support and self-supervised next-response prediction",
        "freeze it and require a complete unseen support gate under both actuator fits",
        "only after support passes, train one response-conditioned locomotion continuation",
        "evaluate both persistent checkpoints on the unchanged full behavior/current matrix",
    ]:
        raise ValueError("reviewed two-stage training order changed")
    two_stage = v12["two_stage_training"]
    if (
        v12.get("contract_id")
        != "winner-v12-two-stage-automatic-calibrator-r64-fixed-p30"
        or v12["frozen_interface"].get("calibration_ticks") != 250
        or v12["automatic_only"].get("runtime_context_source")
        != "final successful calibrator h_out[1,64]"
        or two_stage.get("locomotion_training") is not False
        or v20["authority"].get("pass_authorizes_only")
        != "a separate unchanged 124-cell support/context gate preregistration"
    ):
        raise ValueError("Winner-v20 calibrator-stage boundary changed")
    sources = {
        name: {
            "path": str(path).replace("\\", "/"),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    payload = {
        "schema_version": "winner_v20.two_stage_authority_correction.v1",
        "status": "PASS_WINNER_V20_TWO_STAGE_AUTHORITY_CORRECTED_PRE_OUTCOME",
        "decision": "CALIBRATOR_GATE_CANNOT_SELECT_A_DEPLOYMENT_POLICY",
        "causal_correction": {
            "incorrect_interpretation": (
                "a passing Winner-v20 calibrator support gate could directly authorize "
                "deployment-checkpoint selection"
            ),
            "correct_interpretation": (
                "Winner-v20 emits calibration_actions and a 64-value response state; "
                "it is the first stage of a two-stage policy and is not a walking policy"
            ),
            "correct_next_authority_if_support_passes": (
                "one separate response-conditioned locomotion-training preregistration"
            ),
        },
        "frozen_sequence": [
            "train and independently import the Winner-v20 calibrator artifact",
            "require both calibrator checkpoints to pass the unchanged support gate",
            "freeze the successful calibrator and its exact context-handoff semantics",
            "preregister and train exactly one response-conditioned locomotion continuation",
            "require both locomotion checkpoints to pass the unchanged full behavior/current matrix",
            "apply the preregistered behavior tie-breaker to select exactly one walking ONNX",
        ],
        "execution": {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_training_steps": 0,
            "behavior_cells": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "deployment_checkpoint_selected": False,
            "calibrator_is_deployable_walking_policy": False,
            "no_manual_mass_com_inertia_measurements": True,
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# Winner-v20 two-stage authority correction",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Calibrator is a deployable walking policy: `false`",
                "- Robot clearance: `false`",
                "- Robot / RDK access: `0`",
                "",
                "A passing Winner-v20 support gate may authorize only a separately",
                "preregistered response-conditioned locomotion-training stage.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
