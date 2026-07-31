#!/usr/bin/env python3
"""Preregister the zero-credit predictive-torque S0-S2 falsification sequence."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v124_predictive_torque_s0_s2_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "WINNER_V124_PREDICTIVE_TORQUE_S0_S2_PREREGISTRATION_20260724.md"
)

INPUTS = {
    "v121_result": ANALYSIS / "winner_v121_nominal_behavior_result.json",
    "v123_result": ANALYSIS / "winner_v123_nominal_behavior_result.json",
    "v123_attribution": (
        ANALYSIS / "winner_v123_episode_peak_failure_attribution.json"
    ),
    "v121_diagnosis": ANALYSIS / "winner_v121_peak_objective_diagnosis.json",
    "v121_transform": (
        ANALYSIS / "winner_v121_deployment_transform_contract.json"
    ),
    "plant_preregistration": (
        ANALYSIS
        / "winner_v3_variable_configuration_replacement_preregistration.json"
    ),
    "v122_hosted_preregistration": (
        ANALYSIS / "winner_v122_hosted_preregistration.json"
    ),
    "episode_peak_patch": (
        ROOT / "patches/winner_v122_episode_peak_torque_increment.patch"
    ),
    "closed_loop_evaluator": ROOT / "tools/closed_loop_sim_eval.py",
    "bridge_model": ROOT / "tools/actuator_bridge_model.py",
}

EXPECTED_HASHES = {
    "v121_result": (
        "8bdefb90032facb4a3f3f7c833e608d2b35dac958ac0fcc2bbbd393ddcbb6047"
    ),
    "v123_result": (
        "015fc6b85c5b3e3742f97c1e082987bc82c65da774e74d22b9a9e3c32907baa0"
    ),
    "v123_attribution": (
        "cdbade24b74472445eddd19bc2cac083b8ac263f275dd97b85f39dd6b87a9070"
    ),
    "v121_diagnosis": (
        "1c84a48c3f4eff354108240b4084d6546d1232cccd6bf67d715d9c1518b0e26a"
    ),
    "v121_transform": (
        "4bd5eab5343cd8401db1789773fa3cc345727d903cb31222e0ea9870f0e9e640"
    ),
    "plant_preregistration": (
        "c8f986ceb24863f33c1fc99170548d2e255cb6a26737d3f74762f8dcd4485a24"
    ),
    "v122_hosted_preregistration": (
        "fbbd796fdbf30d0e634ea712ceadd2946af035037bf6481f4ef3e1d0caed8c8e"
    ),
    "episode_peak_patch": (
        "afa07528fa832b0e64e220587936b3c699ee893f026d1caa822674b3850f6c8e"
    ),
    "closed_loop_evaluator": (
        "66f2969d3acb324d21694771b8579a20662b9068b84020cb708667f99fa70504"
    ),
    "bridge_model": (
        "82184df17195cf7241a70e806741a0fdb4e49904fd12b4ee8fe7a38617602472"
    ),
}

EXPECTED_EXTERNAL_HASHES = {
    "joystick": (
        "86fb379195f75a87da08623e5f8d9a1ab3f747c47d2cb8b5cc2fb3bd2db6e8d6"
    ),
    "base": (
        "0e90b98b113c2e5ff4abd34b64482e3f1b3d365ef95481d1838f8b855de99988"
    ),
    "scene": (
        "33af97247d6a876cf47c9e37185cb71bd09f6793bc0f62d90cbe2a91caa3ba63"
    ),
    "robot_xml": (
        "11e922dc9524716e9f54b2fd8be54133fa65efbc61de96ddc846d991de1c9d38"
    ),
    "runtime_sts3215": (
        "a52b5a1551dce7940aadbd1b6446b91a796d279875d77ee247e4ef1cd43b4aa8"
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def trace_inventory(run_root: Path) -> list[dict[str, Any]]:
    traces = sorted((run_root / "traces").glob("*.jsonl"))
    cells = {
        path.stem: read_json(path)
        for path in sorted((run_root / "cells").glob("*.json"))
    }
    inventory: list[dict[str, Any]] = []
    for path in traces:
        rows = 0
        first_tick = None
        last_tick = None
        required_fields = True
        with path.open(encoding="utf-8") as stream:
            for line in stream:
                if not line.strip():
                    continue
                row = json.loads(line)
                tick = int(row["tick"])
                first_tick = tick if first_tick is None else first_tick
                last_tick = tick
                rows += 1
                required_fields = required_fields and all(
                    key in row
                    for key in (
                        "sent_target_rad",
                        "applied_target_rad",
                        "actual_position_pre_rad",
                        "actual_position_rad",
                        "actuator_force_nm",
                        "obs_state",
                        "qpos",
                        "qvel",
                        "reward",
                        "reward_terms",
                    )
                )
        cell = cells.get(path.stem)
        inventory.append(
            {
                "filename": path.name,
                "sha256": sha256(path),
                "rows": rows,
                "first_tick": first_tick,
                "last_tick": last_tick,
                "required_fields": required_fields,
                "cell_trace_hash_exact": (
                    cell is not None
                    and cell.get("trace", {}).get("sha256") == sha256(path)
                ),
            }
        )
    return inventory


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--v121-run-root", type=Path, required=True)
    parser.add_argument("--v123-run-root", type=Path, required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite preregistration: {path}")

    input_hashes = {name: sha256(path) for name, path in INPUTS.items()}
    values = {name: read_json(path) for name, path in INPUTS.items() if path.suffix == ".json"}

    playground = args.playground_root.resolve()
    external_paths = {
        "joystick": playground / "playground/open_duck_mini_v2/joystick.py",
        "base": playground / "playground/open_duck_mini_v2/base.py",
        "scene": (
            playground
            / "playground/open_duck_mini_v2/xmls/scene_flat_terrain_backlash.xml"
        ),
        "robot_xml": (
            playground
            / "playground/open_duck_mini_v2/xmls/open_duck_mini_v2_backlash.xml"
        ),
        "runtime_sts3215": (
            args.runtime_root.resolve() / "src/open_duck_x5/bus/sts3215.py"
        ),
    }
    external_hashes = {
        name: sha256(path) for name, path in external_paths.items()
    }
    v121_traces = trace_inventory(args.v121_run_root.resolve())
    v123_traces = trace_inventory(args.v123_run_root.resolve())

    v121 = values["v121_result"]
    v123 = values["v123_result"]
    attribution = values["v123_attribution"]
    transform = values["v121_transform"]["transform"]
    checks = {
        "all_repository_input_hashes_exact": input_hashes == EXPECTED_HASHES,
        "all_external_source_hashes_exact": (
            external_hashes == EXPECTED_EXTERNAL_HASHES
        ),
        "v121_result_valid_and_11_of_16": (
            v121.get("status")
            == "PASS_WINNER_V121_NOMINAL_BEHAVIOR_VALID_RESULT"
            and v121.get("summary", {}).get("passing_cells") == 11
            and v121.get("summary", {}).get(
                "persistent_both_checkpoint_pass"
            )
            is False
        ),
        "v123_result_valid_and_4_of_16": (
            v123.get("status")
            == "PASS_WINNER_V123_NOMINAL_BEHAVIOR_VALID_RESULT"
            and v123.get("summary", {}).get("passing_cells") == 4
            and v123.get("summary", {}).get(
                "persistent_both_checkpoint_pass"
            )
            is False
        ),
        "frozen_failure_population_exact": (
            attribution.get("failed_checks") == []
            and attribution.get("comparison", {})
            .get("v121", {})
            .get("trace", {})
            .get("torque_exceed_events")
            == 15
            and attribution.get("comparison", {})
            .get("v123", {})
            .get("trace", {})
            .get("torque_exceed_events")
            == 184
        ),
        "v121_trace_inventory_exact": (
            len(v121_traces) == 16
            and all(
                row["rows"] == 600
                and row["first_tick"] == 0
                and row["last_tick"] == 599
                and row["required_fields"]
                and row["cell_trace_hash_exact"]
                for row in v121_traces
            )
        ),
        "v123_trace_inventory_exact": (
            len(v123_traces) == 16
            and all(
                row["rows"] == 600
                and row["first_tick"] == 0
                and row["last_tick"] == 599
                and row["required_fields"]
                and row["cell_trace_hash_exact"]
                for row in v123_traces
            )
        ),
        "v121_transform_contract_exact": (
            transform.get("observation_dim") == 115
            and transform.get("action_dim") == 14
            and transform.get("action_scale_rad") == 0.25
            and transform.get("g3_margin_rad") == 0.165
            and transform.get("apply_identically_to_both_checkpoints") is True
            and transform.get("final_state_feedback")
            == "final_bounded_action"
            and len(transform.get("exact_train_target_delta_rad", [])) == 14
        ),
        "analysis_is_zero_credit_and_read_only": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)

    position_quantum = 2.0 * math.pi / 4096.0
    velocity_quantum = 2.0 * math.pi / 4095.0
    value = {
        "schema_version": "winner_v124.predictive_torque_s0_s2_preregistration.v1",
        "status": (
            "PREREGISTERED_WINNER_V124_PREDICTIVE_TORQUE_S0_S2"
            if not failed
            else "HOLD_WINNER_V124_PREDICTIVE_TORQUE_S0_S2_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": input_hashes,
        "external_source_hashes": external_hashes,
        "external_source_paths": {
            name: str(path) for name, path in external_paths.items()
        },
        "trace_inputs": {
            "v121_run_root": str(args.v121_run_root.resolve()),
            "v121_manifest_sha256": canonical_sha256(v121_traces),
            "v121": v121_traces,
            "v123_run_root": str(args.v123_run_root.resolve()),
            "v123_manifest_sha256": canonical_sha256(v123_traces),
            "v123": v123_traces,
        },
        "pre_run_ruling": {
            "uniform_wrapper_satisfies_both_checkpoint_rule": True,
            "reason": (
                "One mechanism-selected deterministic transform must be applied "
                "unchanged to both independently frozen V121 checkpoints, and "
                "each checkpoint must still pass all eight cells. This is not "
                "checkpoint selection and cannot be revised after S3 results."
            ),
            "s3_pass_rule": (
                "both uniformly wrapped checkpoints independently pass all "
                "eight frozen nominal cells"
            ),
            "one_checkpoint_only": "reject persistence; no cherry-picking",
        },
        "exact_source_hypotheses": {
            "bridge": {
                "first_current_command_effect_tick": "decision_tick + delay_ticks",
                "home_relative_gain": True,
                "lag_alpha": "1-exp(-control_dt_s/tau_s)",
                "post_lag_velocity_clip": True,
                "mapping": "piecewise_affine_monotone_per_joint",
            },
            "torque": {
                "kp_nm_per_rad": 17.11,
                "kv_nm_s_per_rad": 0.0,
                "forcerange_nm": [-3.23, 3.23],
                "force_state_position": (
                    "qpos_post - sim_dt_s*qvel_post at the final "
                    "semi-implicit Euler substep"
                ),
            },
            "current": {
                "nm_per_a": 0.784532,
                "mapping": "abs(actuator_force_nm)/0.784532",
                "peak_torque_limit_nm": 1.91229675,
                "peak_current_limit_a": 2.5,
                "strict_overcurrent_threshold_a": 2.0,
                "strict_overcurrent_equivalent_torque_nm": 2.0 * 0.784532,
                "peak_current_equivalent_torque_nm": 2.5 * 0.784532,
            },
        },
        "s0_model_closure": {
            "bridge_trace_max_abs_error_rad_max": 6.0e-8,
            "torque_trace_max_abs_error_nm_max": 5.0e-6,
            "reported_current_max_abs_error_a_max": 1.0e-12,
            "requirements": [
                "extract constants and ordering from the frozen composed source",
                "replay every V121 and V123 bridge target from sent-target history",
                "reconstruct every logged actuator force from qpos/qvel and ctrl",
                "reconstruct every reported current peak from actuator force",
            ],
            "failure_rule": "any failed source or trace closure stops before S1",
        },
        "s1_event_autopsy": {
            "event_definition": "abs(actuator_force_nm) > 1.91229675",
            "last_controlling_decision_tick": "event_tick-delay_ticks",
            "committed_definition": "last_controlling_decision_tick < 0",
            "local_preventability": (
                "Using the exact piecewise bridge transition and the realized "
                "source-aligned force-state q at the event tick, the intersection "
                "of [-1,1], the frozen G3 target interval, the frozen final-action "
                "rate interval, and both P30/P31-34 torque-safe target intervals "
                "is nonempty at the last controlling decision."
            ),
            "v121_requirement": "all 15 events locally preventable and none committed",
            "v123_requirement": "at least 95 percent of 184 events locally preventable",
            "prediction_error": (
                "qhat=q_pre+horizon_s*qdot_pre; horizon_s="
                "(delay_ticks+1)*control_dt_s-sim_dt_s"
            ),
            "s1b": {
                "direct_credit_definition": (
                    "an element event directly sets the per-episode global "
                    "running maximum; all other element events receive zero "
                    "episode-peak increment credit by source construction"
                ),
                "counterfactual_reward": (
                    "clip((base_scaled_sum-307.48131091308585*"
                    "increment_rate)*0.02,0,10000)"
                ),
                "report": [
                    "directly credited versus zero-direct-credit event counts",
                    "max-setting tick count",
                    "intended un-clipped episode price",
                    "realized clipped reward price",
                    "fraction of intended price removed by clipping",
                ],
                "gate": (
                    "source identity and reconstruction must be exact; event "
                    "fractions are reported without a post-hoc threshold"
                ),
            },
            "failure_rule": (
                "any committed or nonpreventable V121 event, or less than 95 "
                "percent locally preventable V123 events, stops before S2/S3"
            ),
        },
        "s2_feasibility": {
            "population": (
                "all ticks with a complete prediction horizon in the six moving "
                "V121-half cells; x=0 remains on the frozen exact deadband bypass"
            ),
            "prediction_reserve_by_joint_rad": (
                "max(p99.9 absolute source-aligned q prediction error across "
                "the passing population and both fit delays, maximum V121-event "
                "precursor prediction error) + measurement_and_goal_floor"
            ),
            "measurement_and_goal_floor": {
                "position_half_lsb_rad": position_quantum / 2.0,
                "velocity_half_lsb_rad_s": velocity_quantum / 2.0,
                "goal_full_lsb_rad": position_quantum,
                "formula": (
                    "position_half_lsb + horizon_s*velocity_half_lsb + "
                    "goal_full_lsb"
                ),
            },
            "torque_reserve_by_joint_nm": "17.11*prediction_reserve_by_joint_rad",
            "robustness": (
                "derive one target interval per joint and fit using the exact "
                "piecewise bridge; intersect P30 and P31-34 intervals"
            ),
            "supreme_constraints": [
                "normalized action remains in [-1,1]",
                "frozen G3 actual-position-centered margin remains 0.165 rad",
                "frozen exact trained final-action rate delta remains unchanged",
            ],
            "hard_requirements": [
                "positive torque-safe half-width for every joint",
                "zero empty robust-box and supreme-constraint intersections",
                "existing >2 A dwell remains at most 99 consecutive ticks",
            ],
            "diagnostics_not_selection": [
                "fraction of original targets requiring projection",
                "p95 and maximum projected target correction",
                "per-joint applied-error occupancy",
                "per-joint >1.569064 N.m dwell occupancy",
            ],
            "failure_rule": "any hard requirement failure stops before S3",
        },
        "decision_after_s2": {
            "all_s0_s2_requirements_pass": (
                "authorize only a separately preregistered zero-credit S3 "
                "uniform wrapper behavior screen"
            ),
            "any_requirement_fails": (
                "close the predictive-box formulation without Colab or rollout"
            ),
            "s3_goes_16_of_16": (
                "no hosted run; preregister the full frozen robustness matrix"
            ),
            "s3_fixes_torque_but_costs_gait": (
                "a train-through S4 CPU contract may be designed; Colab remains "
                "unauthorized until that separate contract passes"
            ),
        },
        "execution_now": {
            "training_steps": 0,
            "behavior_rollouts": 0,
            "colab_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "s0_s2_read_only_analysis_authorized": not failed,
            "s3_behavior_screen_authorized": False,
            "s4_cpu_contract_authorized": False,
            "hosted_training_authorized": False,
            "checkpoint_selection_authorized": False,
            "gate5_authorized": False,
            "rdkx5_or_robot": False,
            "robot_clearance": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner-v124 predictive-torque S0-S2 preregistration\n\n"
        f"Status: `{value['status']}`\n\n"
        "This freezes a read-only source/trace falsification sequence for an "
        "exact predictive applied-torque box. The exact bridge is "
        "piecewise-affine because it includes delay, home-relative gain, lag, "
        "and a post-lag velocity clip.\n\n"
        "Before any result is known, the repository rules that applying one "
        "unchanged deterministic wrapper to both independently judged V121 "
        "checkpoints satisfies the two-checkpoint protocol. Both must still "
        "pass all eight cells; one checkpoint is never sufficient.\n\n"
        "No behavior rollout, training, Colab, RDK-X5, robot, torque, motion, "
        "or Gate 5 action is authorized by this artifact.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
