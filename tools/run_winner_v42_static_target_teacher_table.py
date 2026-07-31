#!/usr/bin/env python3
"""Build one frozen CPU-only static-target teacher table over 15 failures."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any, Mapping

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
PATCHES = ROOT / "patches"
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(PATCHES))

import run_winner_v25_directional_support_control_diagnostic as v25  # noqa: E402
import run_winner_v34_prefix_right_pitch_hard_intervention as v34  # noqa: E402
import run_winner_v41_static_equilibrium_target_feasibility as v41  # noqa: E402
import run_winner_v41_v2_static_equilibrium_target_feasibility as v41_v2  # noqa: E402


PREREGISTRATION = ANALYSIS / "winner_v42_static_target_teacher_table_preregistration.json"
V33_RESULT = ANALYSIS / "winner_v33_prefix_right_pitch_anchor_support_gate_result.json"
V41_RESULT = ANALYSIS / "winner_v41_v2_static_equilibrium_target_feasibility_result.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
CALIBRATOR_DESIGN = ANALYSIS / "winner_v12_calibrator_training_preregistration.json"

CONFIGURATION_IDS = (
    "COM_X_NEG",
    "COM_CORNER_00",
    "COM_CORNER_01",
    "COM_CORNER_02",
    "COM_CORNER_03",
    "OPTIONAL_AGGREGATE_HEAVY_AFT",
    "DISCOVERY_02",
    "DISCOVERY_03",
    "DISCOVERY_06",
    "DISCOVERY_09",
    "DISCOVERY_10",
    "HELDOUT_04",
    "HELDOUT_07",
    "HELDOUT_09",
    "HELDOUT_15",
)
PLANTS = ("P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH")
TARGETS_PER_CONFIGURATION = 729
EXPECTED_CANDIDATE_PLANT_CELLS = len(CONFIGURATION_IDS) * TARGETS_PER_CONFIGURATION * 2
TICKS = 250


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate_preregistration(value: Mapping[str, Any]) -> None:
    if (
        value.get("status") != "PREREGISTERED_WINNER_V42_STATIC_TARGET_TEACHER_TABLE"
        or value.get("decision") != "AUTHORIZE_ONE_CPU_ONLY_15_CONFIGURATION_TEACHER_TABLE"
    ):
        raise ValueError("Winner-v42 is not preregistered")
    expected = {
        "configuration_ids": list(CONFIGURATION_IDS),
        "actuator_plants": list(PLANTS),
        "grid_values": list(v41.GRID_VALUES),
        "targets_per_configuration": TARGETS_PER_CONFIGURATION,
        "maximum_candidate_plant_cells": EXPECTED_CANDIDATE_PLANT_CELLS,
        "duration_ticks": TICKS,
        "selection": "unchanged Winner-v41 deterministic shared-target key",
        "target_semantics": "one selected time-invariant target per configuration",
    }
    screen = value.get("screen", {})
    if any(screen.get(name) != expected_value for name, expected_value in expected.items()):
        raise ValueError("Winner-v42 screen constants changed")
    if value.get("execution_now") != {
        "configuration_tables": 0,
        "static_target_candidates": 0,
        "candidate_plant_cells": 0,
        "selected_target_replay_cells": 0,
        "optimizer_updates": 0,
        "locomotion_training_steps": 0,
        "robot_or_rdk_access": 0,
    }:
        raise ValueError("Winner-v42 execution authority changed")
    if value.get("pass_rule") != {
        "exact_15_configuration_tables": True,
        "exact_729_targets_per_configuration": True,
        "exact_21870_candidate_plant_cells": True,
        "all_candidate_actions_graph_bounded": True,
        "all_selected_target_replays_exact": True,
        "every_configuration_has_a_shared_two_plant_support_target": True,
        "closest_result_selection": False,
    }:
        raise ValueError("Winner-v42 pass rule changed")
    if value.get("authority") != {
        "robot_clearance": False,
        "training_authorized": False,
        "runtime_static_target_or_action_wrapper_authorized": False,
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "pass_authorizes_only": (
            "one separately frozen static-target teacher ABI CPU contract"
        ),
    }:
        raise ValueError("Winner-v42 authority changed")
    v41_result = json.loads(V41_RESULT.read_text(encoding="utf-8"))
    if value.get("source_results") != {
        "winner_v33_result_lf_sha256": lf_sha256(V33_RESULT),
        "winner_v33_support_failure_counts": {"half": 25, "final": 30},
        "winner_v33_failure_configuration_ids": sorted(CONFIGURATION_IDS),
        "winner_v41_result_lf_sha256": lf_sha256(V41_RESULT),
        "winner_v41_repository_attribution": v41_result["repository_attribution"],
    }:
        raise ValueError("Winner-v42 source-result attribution changed")
    sources = value.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v42 sources are absent")
    for name, item in sources.items():
        if item.get("hash_mode") != "lf" or lf_sha256(ROOT / item["path"]) != item.get("sha256"):
            raise ValueError(f"Winner-v42 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v42 source manifest changed")


def compact_plant_result(value: Mapping[str, Any]) -> dict[str, Any]:
    terminal = value["terminal"]
    episode = value["episode"]
    return {
        "plant": value["plant"],
        "support_pass": value["support_pass"],
        "terminal_tick": None if terminal is None else terminal["tick"],
        "valid_ticks": episode["valid_ticks"],
        "minimum_base_z_m": episode["minimum_base_z_m"],
        "maximum_abs_tilt_rad": episode["maximum_abs_tilt_rad"],
        "maximum_final_window_gyro_xy_norm_rad_s": (
            episode["maximum_final_window_gyro_xy_norm_rad_s"]
        ),
        "maximum_current_a": episode["maximum_current_a"],
        "maximum_torque_nm": episode["maximum_torque_nm"],
        "all_actions_bounded": value["all_actions_bounded"],
        "raw_target_sha256": value["raw_target_sha256"],
        "action_trace_sha256": value["action_trace_sha256"],
        "action_hash_chain_sha256": value["action_hash_chain_sha256"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--static-target-teacher-table-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.static_target_teacher_table_authorized:
        raise PermissionError(
            "Winner-v42 requires --offline-cpu-only "
            "--static-target-teacher-table-authorized"
        )
    if args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v42 result")

    import jax
    import mujoco

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v42 requires CPU-only JAX")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
    v41_result = json.loads(V41_RESULT.read_text(encoding="utf-8"))
    if (
        v41_result.get("schema_version")
        != "winner_v41.static_equilibrium_target_feasibility_result.v2"
        or v41_result.get("status")
        != "PASS_WINNER_V41_STATIC_EQUILIBRIUM_TARGET_FEASIBILITY"
        or v41_result.get("decision") != "AUTHORIZE_STATIC_TARGET_TEACHER_CONTRACT_ONLY"
        or v41_result.get("summary", {}).get("shared_support_pass_count") != 100
        or v41_result.get("summary", {}).get("selected_coordinates")
        != [-0.25, -0.25, 0.25]
        or v41_result.get("authority", {}).get("pass_authorizes_only")
        != "one separately frozen static-target teacher contract"
    ):
        raise ValueError("Winner-v41 does not authorize the teacher table")
    v33 = json.loads(V33_RESULT.read_text(encoding="utf-8"))
    if (
        v33.get("status") != "HOLD_WINNER_V33_PREFIX_RIGHT_PITCH_ANCHOR_SUPPORT_GATE"
        or v33.get("decision") != "DO_NOT_TRAIN_RESPONSE_CONDITIONED_LOCOMOTION"
    ):
        raise ValueError("Winner-v33 failure source changed")
    if tuple(v34.CONFIGURATION_IDS) != CONFIGURATION_IDS:
        raise ValueError("Winner-v42 failure configuration set changed")

    smoke, reviewed_gate, _, _, _, _ = v34.configure_reviewed_modules()
    if tuple(smoke.PLANTS) != PLANTS:
        raise ValueError("Winner-v42 actuator plants changed")
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v42 canonical P30 fit changed")
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v42 Playground commit changed")
    smoke.validate_playground_tree(args.playground_root)
    scene = args.playground_root / smoke.SCENE_RELATIVE
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    calibrator_design = json.loads(CALIBRATOR_DESIGN.read_text(encoding="utf-8"))
    configurations = v25.exact_configurations(
        json.loads(DOMAIN.read_text(encoding="utf-8"))
    )
    grid = v41.candidate_coordinates()
    if len(grid) != TARGETS_PER_CONFIGURATION:
        raise ValueError("Winner-v42 inherited target grid changed")
    v41.v38.expand_mirrored_blocks = v41_v2.expand_static_target

    configuration_results: list[dict[str, Any]] = []
    total_candidate_cells = 0
    all_actions_bounded = True
    all_replays_exact = True
    for configuration_id in CONFIGURATION_IDS:
        configuration = configurations[configuration_id]
        episodes: dict[str, Any] = {}
        initial_snapshots: dict[str, Mapping[str, Any]] = {}
        for plant in PLANTS:
            episode = smoke.Episode(
                mujoco, scene, configuration, plant, calibrator_design,
                observer_type, args.canonical_fit,
            )
            if episode.initial_contacts != (1, 1):
                raise ValueError("Winner-v42 cell does not start with both feet loaded")
            episodes[plant] = episode
            initial_snapshots[plant] = v25.capture_episode(mujoco, episode)

        candidates: list[dict[str, Any]] = []
        compact_candidates: list[dict[str, Any]] = []
        for candidate_index, coordinates in enumerate(grid):
            plant_results = [
                v41.evaluate_target(
                    mujoco=mujoco, smoke=smoke, reviewed_gate=reviewed_gate,
                    episode=episodes[plant], initial_snapshot=initial_snapshots[plant],
                    coordinates=coordinates, include_trace=False,
                )
                for plant in PLANTS
            ]
            total_candidate_cells += len(plant_results)
            all_actions_bounded &= all(
                item["all_actions_bounded"] for item in plant_results
            )
            row = {
                "candidate_index": candidate_index,
                "coordinates": coordinates.astype(float).tolist(),
                "coordinates_sha256": smoke.array_sha256(coordinates),
                "plant_results": plant_results,
                "shared_support_pass": all(
                    item["support_pass"] for item in plant_results
                ),
            }
            candidates.append(row)
            compact_candidates.append(
                {
                    "candidate_index": candidate_index,
                    "coordinates_sha256": row["coordinates_sha256"],
                    "shared_support_pass": row["shared_support_pass"],
                    "plant_results": [
                        compact_plant_result(item) for item in plant_results
                    ],
                }
            )

        passing = [row for row in candidates if row["shared_support_pass"]]
        selected = max(passing if passing else candidates, key=v41.candidate_key)
        selected_coordinates = np.asarray(selected["coordinates"], dtype=np.float32)
        replay_results = [
            v41.evaluate_target(
                mujoco=mujoco, smoke=smoke, reviewed_gate=reviewed_gate,
                episode=episodes[plant], initial_snapshot=initial_snapshots[plant],
                coordinates=selected_coordinates, include_trace=True,
            )
            for plant in PLANTS
        ]
        replay_exact = all(
            {name: replay[name] for name in original} == original
            for original, replay in zip(selected["plant_results"], replay_results)
        )
        all_replays_exact &= replay_exact
        configuration_results.append(
            {
                "configuration_id": configuration_id,
                "configuration_sha256": smoke.canonical_sha256(configuration),
                "candidate_receipts": compact_candidates,
                "shared_support_pass_count": len(passing),
                "per_plant_support_pass_counts": {
                    plant: sum(
                        row["plant_results"][plant_index]["support_pass"]
                        for row in candidates
                    )
                    for plant_index, plant in enumerate(PLANTS)
                },
                "selected_kind": (
                    "shared_support_pass" if passing
                    else "diagnostic_best_not_promoted"
                ),
                "selected_candidate_index": selected["candidate_index"],
                "selected_coordinates": selected["coordinates"],
                "selected_coordinates_sha256": selected["coordinates_sha256"],
                "selected_replay_exact": replay_exact,
                "selected_replay_results": replay_results,
            }
        )

    validity_checks = {
        "exact_15_configuration_tables": len(configuration_results) == 15,
        "exact_729_targets_per_configuration": all(
            len(row["candidate_receipts"]) == TARGETS_PER_CONFIGURATION
            for row in configuration_results
        ),
        "exact_21870_candidate_plant_cells": (
            total_candidate_cells == EXPECTED_CANDIDATE_PLANT_CELLS
        ),
        "all_candidate_actions_graph_bounded": bool(all_actions_bounded),
        "all_selected_target_replays_exact": bool(all_replays_exact),
    }
    efficacy_checks = {
        "every_configuration_has_a_shared_two_plant_support_target": all(
            row["shared_support_pass_count"] > 0 for row in configuration_results
        ),
    }
    checks = {**validity_checks, **efficacy_checks}
    valid = all(validity_checks.values())
    passed = valid and all(efficacy_checks.values())
    if not valid:
        status = "INVALID_WINNER_V42_STATIC_TARGET_TEACHER_TABLE"
        classification = "INVALID_STATIC_TARGET_TEACHER_TABLE"
        decision = "DO_NOT_SELECT_NEXT_POLICY_MECHANISM"
    elif passed:
        status = "PASS_WINNER_V42_STATIC_TARGET_TEACHER_TABLE"
        classification = "FULL_FAILURE_SET_STATIC_TARGET_TEACHER_TABLE_EXISTS"
        decision = "AUTHORIZE_STATIC_TARGET_TEACHER_ABI_CPU_CONTRACT_ONLY"
    else:
        status = "HOLD_WINNER_V42_STATIC_TARGET_TEACHER_TABLE"
        classification = "STATIC_TARGET_TEACHER_TABLE_INCOMPLETE"
        decision = "CLOSE_STATIC_TARGET_TEACHER_TABLE_ROUTE"
    result = {
        "schema_version": "winner_v42.static_target_teacher_table_result.v1",
        "status": status,
        "classification": classification,
        "decision": decision,
        "checks": checks,
        "failed_checks": sorted(name for name, value in checks.items() if not value),
        "screen": {
            "configuration_ids": list(CONFIGURATION_IDS),
            "actuator_plants": list(PLANTS),
            "grid_values": list(v41.GRID_VALUES),
            "targets_per_configuration": TARGETS_PER_CONFIGURATION,
            "maximum_candidate_plant_cells": EXPECTED_CANDIDATE_PLANT_CELLS,
            "duration_ticks": TICKS,
            "selection": "unchanged Winner-v41 deterministic shared-target key",
            "target_semantics": "one selected time-invariant target per configuration",
        },
        "configuration_results": configuration_results,
        "teacher_table": {
            row["configuration_id"]: {
                "candidate_index": row["selected_candidate_index"],
                "coordinates": row["selected_coordinates"],
                "coordinates_sha256": row["selected_coordinates_sha256"],
                "shared_support_pass": row["shared_support_pass_count"] > 0,
            }
            for row in configuration_results
        },
        "summary": {
            "configuration_pass_count": sum(
                row["shared_support_pass_count"] > 0 for row in configuration_results
            ),
            "configuration_hold_ids": [
                row["configuration_id"] for row in configuration_results
                if row["shared_support_pass_count"] == 0
            ],
            "shared_target_counts": {
                row["configuration_id"]: row["shared_support_pass_count"]
                for row in configuration_results
            },
            "selected_coordinates": {
                row["configuration_id"]: row["selected_coordinates"]
                for row in configuration_results
            },
        },
        "execution": {
            "configuration_tables": len(configuration_results),
            "static_target_candidates": len(configuration_results) * TARGETS_PER_CONFIGURATION,
            "candidate_plant_cells": total_candidate_cells,
            "selected_target_replay_cells": len(configuration_results) * 2,
            "optimizer_updates": 0,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": {
            "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
            "winner_v33_result_lf_sha256": lf_sha256(V33_RESULT),
            "winner_v41_result_lf_sha256": lf_sha256(V41_RESULT),
            "runner_lf_sha256": lf_sha256(Path(__file__)),
        },
        "authority": {
            "robot_clearance": False,
            "training_authorized": False,
            "runtime_static_target_or_action_wrapper_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "one separately frozen static-target teacher ABI CPU contract",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(status)
    print(f"CONFIGURATION_PASSES={result['summary']['configuration_pass_count']}/15")
    print(f"CONFIGURATION_HOLDS={result['summary']['configuration_hold_ids']}")
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
