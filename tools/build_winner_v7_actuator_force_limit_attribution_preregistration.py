#!/usr/bin/env python3
"""Freeze the read-only winner-v7 actuator-force failure attribution."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "winner_v7_actuator_force_limit_attribution_preregistration.json"
AUDIT_TOOL = ROOT / "tools" / "audit_winner_v7_actuator_force_limit_attribution.py"
SOURCE_RESULT = ANALYSIS / "winner_v7_full_behavior_revalidation_result.json"
CURRENT_CONTRACT = ANALYSIS / "winner_v3_current_gate_application_contract.json"
SOURCE_PREREG = ANALYSIS / "winner_v7_full_behavior_revalidation_preregistration.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def frozen_repo_file(path: Path) -> dict[str, str]:
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "sha256": sha256(path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-xml", type=Path, required=True)
    parser.add_argument("--scene-xml", type=Path, required=True)
    parser.add_argument("--source-result-commit", required=True)
    args = parser.parse_args()
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    source = json.loads(SOURCE_RESULT.read_text(encoding="utf-8"))
    if source["decision"] != "CLOSE_WINNER_V7_PROTECTED_BASE":
        raise ValueError("source winner-v7 result is not the frozen closed result")
    if source["checks"]["exactly_128_cells"] is not True:
        raise ValueError("source winner-v7 population is incomplete")
    payload = {
        "schema_version": "open_duck_mini.winner_v7_actuator_force_limit_attribution_preregistration.v1",
        "status": "FROZEN_WINNER_V7_ACTUATOR_FORCE_LIMIT_ATTRIBUTION",
        "causal_question": "Did the closed winner-v7 moving population fail the physical current/torque envelope because every moving trace saturated the simulator's uniformly inherited STS3215 force ceiling above the frozen manufacturer limit?",
        "source_result_commit": args.source_result_commit,
        "frozen_inputs": {
            "winner_v7_result": frozen_repo_file(SOURCE_RESULT),
            "current_gate_contract": frozen_repo_file(CURRENT_CONTRACT),
            "winner_v7_preregistration": frozen_repo_file(SOURCE_PREREG),
            "audit_tool_sha256": sha256(AUDIT_TOOL),
            "model_xml_filename": args.model_xml.name,
            "model_xml_sha256": sha256(args.model_xml),
            "scene_xml_filename": args.scene_xml.name,
            "scene_xml_sha256": sha256(args.scene_xml),
        },
        "analysis_contract": {
            "population": "all 128 trace identities and hashes embedded in the imported winner-v7 result",
            "expected_partition": {"moving": 96, "zero_command": 32},
            "joint_order": [
                "left_hip_yaw", "left_hip_roll", "left_hip_pitch", "left_knee", "left_ankle",
                "neck_pitch", "head_pitch", "head_yaw", "head_roll",
                "right_hip_yaw", "right_hip_roll", "right_hip_pitch", "right_knee", "right_ankle",
            ],
            "ceiling_tolerance_nm": 1e-6,
            "replay": [
                "verify every source trace hash, row count, finite value, and contiguous tick",
                "recompute per-joint peak torque and current from actuator_force_nm",
                "recompute the strict consecutive duration above 2 A",
                "apply both the 2.5 A peak-current and 1.91229675 N.m peak-torque gates",
                "parse the scene include, STS3215 inherited force range, actuator count, names, and class binding",
                "report peak joint/tick distributions and a seven-tick context around each trace peak",
            ],
            "no_statistics_or_thresholds_may_be_changed_after_freeze": True,
        },
        "selection_rule": {
            "all_checks_required": [
                "source_winner_v7_remains_closed",
                "source_population_complete",
                "source_behavior_expectations_preserved",
                "model_scene_binding_exact",
                "all_14_actuators_share_sts3215_force_range",
                "simulator_force_limit_exceeds_frozen_physical_limit",
                "all_moving_traces_fail_peak_current",
                "all_moving_traces_fail_peak_torque",
                "all_moving_trace_peaks_hit_model_force_ceiling",
                "all_moving_trace_peaks_are_head_roll",
                "all_zero_traces_pass_peak_current_and_torque",
                "no_trace_reaches_duration_trip",
                "source_runner_omitted_frozen_torque_gate",
            ],
            "pass_decision": "SELECT_DISTINCT_PHYSICAL_STS3215_FORCE_LIMIT_CONTRACT",
            "fail_decision": "CLOSE_PHYSICAL_FORCE_LIMIT_ATTRIBUTION_ROUTE",
            "selected_limit": "min(1.91229675 N.m manufacturer stall torque, 2.5 A * 0.784532 N.m/A)",
        },
        "interpretation_constraints": [
            "winner-v7 remains closed and is never retried or reclassified",
            "the source torque-gate omission is reported even though it cannot change the already-failed result",
            "a pass authorizes only a distinct zero-behavior default-off simulator contract",
            "no policy weights, observations, actions, rewards, gates, current conversion, or traces may change",
        ],
        "authority": {
            "read_only_cpu_analysis_only": True,
            "training_gpu_colab": False,
            "simulator_policy_behavior_run": False,
            "runtime_robot_rdkx5_torque_motion_gate5": False,
        },
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"WROTE={OUTPUT}")
    print(f"SHA256={sha256(OUTPUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
