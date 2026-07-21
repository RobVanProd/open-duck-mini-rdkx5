#!/usr/bin/env python3
"""Freeze one restored-snapshot Winner-v15 pitch-margin CPU update."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v15_pitch_margin_cpu_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V15_PITCH_MARGIN_CPU_CONTRACT_20260721.md"
ATTRIBUTION = ANALYSIS / "winner_v15_pitch_margin_objective_attribution.json"
STAGE1_RESULT = ANALYSIS / "winner_v13_normalized_response_stage1_v2_result.json"
SOURCES = {
    "builder": Path("tools/build_winner_v15_pitch_margin_cpu_contract.py"),
    "runner": Path("tools/run_winner_v15_pitch_margin_cpu_contract.py"),
    "environment_builder": Path("tools/prepare_winner_v15_cpu_environment.py"),
    "objective": Path("patches/winner_v15_pitch_margin_support.py"),
    "tests": Path("tests/test_winner_v15_pitch_margin_cpu_contract.py"),
    "objective_tests": Path("tests/test_winner_v15_pitch_margin_support.py"),
    "workflow": Path(".github/workflows/winner-v15-pitch-margin-cpu-contract.yml"),
    "objective_attribution": Path(
        "outputs/analysis/winner_v15_pitch_margin_objective_attribution.json"
    ),
    "winner_v14_result": Path(
        "outputs/analysis/winner_v14_support_action_diagnostic_result.json"
    ),
    "stage1_result": Path(
        "outputs/analysis/winner_v13_normalized_response_stage1_v2_result.json"
    ),
    "v12_training_primitives": Path("patches/winner_v12_calibrator_training.py"),
    "deployable_network": Path("patches/winner_v12_decomposed_backend_networks.py"),
    "cpu_smoke": Path("tools/run_winner_v12_calibrator_cpu_smoke.py"),
    "full_training_runner": Path("tools/run_winner_v12_full_calibrator_training.py"),
    "full_training_preregistration": Path(
        "outputs/analysis/winner_v12_full_calibrator_training_preregistration.json"
    ),
    "calibrator_design": Path(
        "outputs/analysis/winner_v12_calibrator_training_preregistration.json"
    ),
    "variable_configuration_domain": Path(
        "outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"
    ),
    "runtime_observer": Path(
        "artifacts/runtime_handoff/rdkx5_native_20260719/observer/winner_v2_contract.py"
    ),
    "canonical_p30_fit": Path(
        "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"
    ),
}


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite pitch-margin CPU contract: {path}")
    attribution = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    stage1 = json.loads(STAGE1_RESULT.read_text(encoding="utf-8"))
    final_snapshot = stage1.get("snapshot_manifest", [{}])[-1]
    if (
        attribution.get("status")
        != "PASS_WINNER_V15_PITCH_MARGIN_OBJECTIVE_ATTRIBUTION"
        or attribution.get("decision")
        != "PREREGISTER_ONE_SIDED_NEGATIVE_PITCH_MARGIN_CPU_CONTRACT"
        or attribution.get("execution_now", {}).get("optimizer_updates") != 0
        or stage1.get("status") != "PASS_WINNER_V13_NORMALIZED_RESPONSE_STAGE1"
        or stage1.get("failed_checks") != []
        or final_snapshot.get("sha256")
        != "8c1392c738eddfb098e61c1a6ae2f863eda883e1eba6ac546aef695da6f163af"
        or final_snapshot.get("bytes") != 189027
    ):
        raise ValueError("Winner-v15 CPU contract source evidence changed")
    sources = {
        name: {
            "path": str(path).replace("\\", "/"),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    payload = {
        "schema_version": "winner_v15.pitch_margin_cpu_contract.v1",
        "status": "FROZEN_WINNER_V15_PITCH_MARGIN_CPU_CONTRACT",
        "decision": "AUTHORIZE_ONE_RESTORED_PITCH_MARGIN_STAGE2_UPDATE_ONLY",
        "source_artifact": {
            "github_run_id": 29822834921,
            "github_run_attempt": 1,
            "github_run_head_sha": "0b1dac9ea47a93861f72fa5dd393134f36d6db02",
            "github_artifact_id": 8492593761,
            "github_artifact_name": "winner-v13-normalized-response-stage1-v2-29822834921",
            "artifact_zip_sha256": "b3ff19186ef39e8a72f9e43095d373840fb0b1562a2f7bed83a74c9f10cf6680",
            "snapshot_member": (
                "winner-v13-normalized-response-stage1-v2-work/snapshots/"
                "snapshot_stage1_update_100.npz"
            ),
            "snapshot_sha256": final_snapshot["sha256"],
            "snapshot_bytes": final_snapshot["bytes"],
        },
        "single_change": {
            "default_off": "bit-exact reviewed flat alive reward",
            "enabled_valid_transition_reward": (
                "1 - square(clip(max(0, -next_pitch_rad) / 0.35, 0, 1))"
            ),
            "failure_transition_reward": 0.0,
            "settled_terminal_bonus": 250.0,
            "all_observation_action_graph_dynamics_population_seed_and_mask_semantics": "unchanged",
            "trainable_scale": None,
        },
        "frozen_cpu_proof": {
            "stage2_optimizer_updates": 1,
            "population": "exact 40 training configurations x 2 hidden plants",
            "ticks": 250,
            "rollout_update_index": 0,
            "training_root_seed": 120120,
            "stage2_learning_rate": 0.0001,
            "requirements": [
                "default-off batch, episodes, observations, returns, and advantages bit-exact to reviewed rollout",
                "enabled path changes only reward-derived returns and advantages",
                "reward and penalty match the frozen analytic formula bit-exactly",
                "PPO masks and raw-to-bounded action path remain exact",
                "all Stage-2 gradients and leaves nonzero/changed",
                "all Stage-1 encoder/auxiliary leaves bit-exact frozen",
                "atomic Stage-2 snapshot readback",
                "115/14/64 ONNX ABI and chain <=1e-7",
            ],
        },
        "pass_rule": (
            "Every check passes. A pass authorizes only a separate 100-update "
            "pitch-margin support-training preregistration."
        ),
        "execution_now": {
            "stage2_optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "support_training_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "a separate pitch-margin support-training preregistration",
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
    }
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v15 pitch-margin CPU contract",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Source Stage-1 snapshot: `8c1392c7…6f163af`",
                "- Stage-2 updates: `1`",
                "- Formal support / locomotion / robot: `0 / 0 / 0`",
                "",
                "This contract proves the one-sided negative-pitch reward is the only",
                "enabled transition change, is bounded without a tunable coefficient,",
                "and can update the support head while leaving Stage-1 and ONNX ABI exact.",
                "A pass authorizes only a separate training preregistration.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
