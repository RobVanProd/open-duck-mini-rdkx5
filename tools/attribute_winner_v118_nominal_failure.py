#!/usr/bin/env python3
"""Close repeated rate tightening and select a V119 transition match."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
V117_RESULT = ANALYSIS / "winner_v117_nominal_behavior_result.json"
V118_RESULT = ANALYSIS / "winner_v118_nominal_behavior_result.json"
V117_CONTRACT = (
    ANALYSIS / "winner_v117_postguard_rate_projection_contract.json"
)
V118_CONTRACT = ANALYSIS / "winner_v118_rate_projection_contract.json"
V114_CPU = ANALYSIS / "winner_v114_linear_torque_cpu_result.json"
V114_VALIDATION = (
    ANALYSIS / "winner_v114_recovered_training_validation.json"
)
OUTPUT = ANALYSIS / "winner_v118_nominal_failure_attribution.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V118_NOMINAL_FAILURE_ATTRIBUTION_20260724.md"
)
EXPECTED_HASHES = {
    "v117_result": (
        "0a3d04b478e46c5041b52554008cb5e8db800f0a2552932cd60cb8640efee09a"
    ),
    "v118_result": (
        "fa361e326c901e9863047bf9ac588830fb93ee5f263d95df68b1a6203c814ba7"
    ),
    "v117_contract": (
        "9aab1d09ffcff7608fa758ea891f4b2a6c54d90b00a056a4478c503514d05beb"
    ),
    "v118_contract": (
        "4988315b8e215c04791f11dedf224d583625d0a5534f472d301a20247e7c379d"
    ),
    "v114_cpu": (
        "f211c6cb344e5548c15de9d3213217a69e1c3891afce9e63e30e07d2a177c104"
    ),
    "v114_validation": (
        "d822de06ce69e349403e9ef9cacdb961dbaf15157b5e5d28907b8c95cde9ddae"
    ),
}


def sha256(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def checkpoint(value: dict, step: int) -> dict:
    return next(
        row for row in value["per_checkpoint"] if row["step"] == step
    )


def value_after(command: list[str], flag: str) -> str:
    index = command.index(flag)
    return command[index + 1]


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(
                f"refusing to overwrite V118 attribution: {path}"
            )
    v117_result = json.loads(V117_RESULT.read_text(encoding="utf-8"))
    v118_result = json.loads(V118_RESULT.read_text(encoding="utf-8"))
    v117_contract = json.loads(
        V117_CONTRACT.read_text(encoding="utf-8")
    )
    v118_contract = json.loads(
        V118_CONTRACT.read_text(encoding="utf-8")
    )
    v114_cpu = json.loads(V114_CPU.read_text(encoding="utf-8"))
    v114_validation = json.loads(
        V114_VALIDATION.read_text(encoding="utf-8")
    )
    hashes = {
        "v117_result": sha256(V117_RESULT),
        "v118_result": sha256(V118_RESULT),
        "v117_contract": sha256(V117_CONTRACT),
        "v118_contract": sha256(V118_CONTRACT),
        "v114_cpu": sha256(V114_CPU),
        "v114_validation": sha256(V114_VALIDATION),
    }
    v117_half = checkpoint(v117_result, 1_003_520)
    v117_final = checkpoint(v117_result, 2_007_040)
    v118_half = checkpoint(v118_result, 1_003_520)
    v118_final = checkpoint(v118_result, 2_007_040)
    v117_delta = v117_contract["projection"][
        "selected_normalized_action_delta"
    ]
    v118_delta = v118_contract["projection"][
        "selected_normalized_action_delta"
    ]
    affected = set(v118_contract["projection"]["affected_joints"])
    joint_rows = [
        {
            "joint_index": index,
            "v117_delta": float(before),
            "v118_delta": float(after),
            "tightened": after < before,
        }
        for index, (before, after) in enumerate(
            zip(v117_delta, v118_delta, strict=True)
        )
    ]
    command = v114_cpu["training"]["command"]
    original_training_rates = [
        float(value)
        for value in value_after(
            command, "--ground_up_action_velocity_limits_rad_s"
        ).split(",")
    ]
    v117_rates = v117_contract["projection"]["selected_rate_limit_rad_s"]
    training_metrics = v114_validation["training_metric_evidence"]
    linear_torque = training_metrics[
        "eval/episode_cost/linear_peak_torque_exceedance"
    ]
    tracking_tail = training_metrics[
        "eval/episode_cost/tracking_tail_exceedance"
    ]
    checks = {
        "all_hashes_exact": hashes == EXPECTED_HASHES,
        "both_results_valid_complete": (
            v117_result.get("failed_validity_checks") == []
            and v118_result.get("failed_validity_checks") == []
            and v117_result["summary"]["cells"] == 16
            and v118_result["summary"]["cells"] == 16
        ),
        "both_final_checkpoints_all_eight_pass": (
            v117_final["all_eight_cells_pass"]
            and v118_final["all_eight_cells_pass"]
        ),
        "tightening_reduces_half_pass_count": (
            v117_half["passing_cells"] == 3
            and v118_half["passing_cells"] == 2
        ),
        "tightening_worsens_half_current": (
            v118_half["worst_peak_current_a"]
            > v117_half["worst_peak_current_a"]
        ),
        "tightening_worsens_half_torque": (
            v118_half["worst_peak_torque_nm"]
            > v117_half["worst_peak_torque_nm"]
        ),
        "same_four_joints_tightened": (
            sum(row["tightened"] for row in joint_rows) == 4
            and affected
            == {
                "left_hip_pitch",
                "left_knee",
                "left_ankle",
                "right_ankle",
            }
        ),
        "v114_training_used_original_rate_vector": (
            original_training_rates
            == [
                1.0,
                0.75,
                1.5,
                1.5,
                1.5,
                0.5,
                0.5,
                0.5,
                0.5,
                0.5,
                0.75,
                1.25,
                1.0,
                1.25,
            ]
        ),
        "v117_deployment_vector_differs_from_training": (
            any(
                abs(before - after) > 1.0e-6
                for before, after in zip(
                    original_training_rates, v117_rates, strict=True
                )
            )
        ),
        "linear_torque_objective_decreased_at_both_checkpoints": (
            linear_torque[0]["value"] > linear_torque[1]["value"]
            > linear_torque[2]["value"]
        ),
        "tracking_tail_objective_decreased_at_both_checkpoints": (
            tracking_tail[0]["value"] > tracking_tail[1]["value"]
            > tracking_tail[2]["value"]
        ),
        "no_reward_or_behavior_selection": True,
        "no_training_authorized_by_attribution": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    value = {
        "schema_version": (
            "winner_v118.nominal_failure_attribution.v1"
        ),
        "status": (
            "PASS_WINNER_V118_NOMINAL_FAILURE_ATTRIBUTION"
            if not failed
            else "HOLD_WINNER_V118_NOMINAL_FAILURE_ATTRIBUTION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "comparison": {
            "v117_half": v117_half,
            "v117_final": v117_final,
            "v118_half": v118_half,
            "v118_final": v118_final,
            "rate_delta_rows": joint_rows,
        },
        "selected_mechanism": {
            "name": "V119_TRAIN_TRANSITION_MATCH",
            "source_checkpoint": "exact V114 final at 2,007,040",
            "train_time_rate_vector": "V117 selected vector",
            "train_time_actual_centered_guard_margin_rad": 0.165,
            "train_time_postguard_rate_projection": True,
            "applied_target_observation_preserved": True,
            "linear_torque_objective_preserved": True,
            "tracking_tail_objective_preserved": True,
            "postexport_transform": (
                "same G3 + V117 final rate projection + x0 deadband"
            ),
            "reason": (
                "V114 learned under the original rate vector and without "
                "the postexport G3/final projection. Output-only tightening "
                "is nonmonotonic. The next falsifiable mechanism is to make "
                "the training transition match the deployed constraint."
            ),
        },
        "closed_routes": {
            "repeat_output_only_rate_formula": True,
            "v118_checkpoint_selection": True,
            "cherry_pick_green_final": True,
            "reward_curve_selection": True,
        },
        "decision": (
            "PREREGISTER_V119_DEFAULT_OFF_AND_CPU_TRANSITION_CONTRACT"
            if not failed
            else "STOP"
        ),
        "authority": {
            "v119_cpu_contract_preregistration_authorized": not failed,
            "training_authorized": False,
            "colab_authorized": False,
            "behavior_evaluation_authorized": False,
            "full_matrix_authorized": False,
            "checkpoint_selection_authorized": False,
            "gate5_authorized": False,
            "rdkx5_or_robot": False,
            "robot_clearance": False,
            "torque_or_motion": False,
        },
        "input_hashes": hashes,
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner-v118 nominal failure attribution\n\n"
        f"Status: `{value['status']}`\n\n"
        f"Decision: `{value['decision']}`\n\n"
        "V117 to V118 tightened the same four final rate caps, but the half "
        "checkpoint fell from 3/8 to 2/8 and both worst current and torque "
        "increased. Repeating output-only tightening is closed. V114 trained "
        "under the older vector without the deployed G3/final projection, so "
        "the next mechanism is an exact train/deploy transition match. This "
        "artifact authorizes only a default-off CPU contract, not training.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(value["decision"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
