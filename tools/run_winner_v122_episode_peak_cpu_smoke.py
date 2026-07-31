#!/usr/bin/env python3
"""Run the preregistered V122 episode-peak CPU mechanics smoke."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""
os.environ["ROCR_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"

from flax.training import orbax_utils
import jax
import numpy as np
import onnx
from orbax import checkpoint as ocp


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from build_ground_up_actual_centered_guard_screen import (  # noqa: E402
    append_guard,
)
from build_ground_up_command_deadband_repair import (  # noqa: E402
    wrap as append_deadband,
)
from build_winner_v113_postexport_policies import (  # noqa: E402
    graph_io,
    initializers,
    sha256,
)
from build_winner_v117_postguard_rate_projection_policies import (  # noqa: E402
    append_projection,
    inference_contract,
)
from run_winner_v111_peak_torque_cpu_smoke import (  # noqa: E402
    sha256_directory,
    tree_errors,
)
from run_winner_v114_linear_torque_cpu_smoke import (  # noqa: E402
    scalar_events,
)


ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v122_episode_peak_cpu_preregistration.json"
V121_TRANSFORM = (
    ANALYSIS / "winner_v121_deployment_transform_contract.json"
)
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
RESULT = ANALYSIS / "winner_v122_episode_peak_cpu_result.json"
MARKDOWN = ANALYSIS / "WINNER_V122_EPISODE_PEAK_CPU_RESULT_20260724.md"
PREREG_SHA256 = (
    "3617e52dc26a3a6db317473162077ece264af8aef8e3afc276a1925d33cabc89"
)
VELOCITY_LIMITS = (
    "1.0,.75,1.4736209064722061,1.4300791546702385,"
    "1.3976470567286015,.5,.5,.5,.5,.5,.75,1.25,1.0,"
    "1.2215287424623966"
)
METRIC_TAG = "eval/episode_cost/episode_peak_torque_increment"


def deployed_onnx_contract(raw_path: Path, output_path: Path) -> dict:
    contract = json.loads(V121_TRANSFORM.read_text(encoding="utf-8"))
    transform = contract["transform"]
    selected_delta = np.asarray(
        transform["exact_train_normalized_action_delta"],
        dtype=np.float32,
    )
    home = np.asarray(transform["home_target_rad"], dtype=np.float32)
    actual_obs_indices = np.asarray(
        transform["measured_joint_offset_indices"], dtype=np.int64
    )
    pitch_indices = np.asarray(
        transform["pitch_chain_action_indices"], dtype=np.int64
    )
    command_index = int(transform["command_x_observation_index"])
    deadband = float(transform["zero_deadband_absolute_command_x"])
    action_scale = float(transform["action_scale_rad"])
    margin = float(transform["g3_margin_rad"])
    raw = onnx.load(raw_path)
    raw_initializers = initializers(raw)
    guarded = append_guard(
        raw,
        obs_indices=actual_obs_indices,
        pitch_indices=pitch_indices,
        home=home,
        action_scale=action_scale,
        margin=margin,
    )
    deadbanded = append_deadband(
        guarded,
        command_index=command_index,
        deadband=deadband,
    )
    deployed = append_projection(
        deadbanded,
        selected_delta=selected_delta,
        command_index=command_index,
        deadband=deadband,
    )
    onnx.checker.check_model(deployed)
    onnx.save(deployed, output_path)
    inference = inference_contract(
        raw_path,
        output_path,
        selected_delta=selected_delta,
        changed_indices=pitch_indices,
        command_index=command_index,
        deadband=deadband,
        home=home,
        pitch_indices=pitch_indices,
        actual_obs_indices=actual_obs_indices,
        action_scale=action_scale,
        guard_margin=margin,
    )
    deployed_initializers = initializers(deployed)
    return {
        "step": int(raw_path.stem.rsplit("_", 1)[1]),
        "raw_sha256": sha256(raw_path),
        "deployed_sha256": sha256(output_path),
        "raw_train_delta_exact": bool(
            "max_action_delta" in raw_initializers
            and np.array_equal(
                raw_initializers["max_action_delta"],
                selected_delta[None],
            )
        ),
        "final_projection_delta_exact": bool(
            np.array_equal(
                deployed_initializers["v117_max_action_delta"],
                selected_delta[None],
            )
        ),
        "graph_io": graph_io(deployed),
        "inference": inference,
        "initializers_finite": all(
            np.isfinite(onnx.numpy_helper.to_array(item)).all()
            for item in deployed.graph.initializer
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--source-checkpoint", type=Path, required=True)
    parser.add_argument("--cpu-template", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    args = parser.parse_args()
    playground = args.playground_root.resolve()
    source = args.source_checkpoint.resolve()
    cpu_template = args.cpu_template.resolve()
    work = args.work_root.resolve()
    if work.exists():
        raise FileExistsError(f"refusing to reuse V122 work root: {work}")
    if RESULT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite V122 CPU result")
    if sha256(PREREG) != PREREG_SHA256:
        raise ValueError("V122 preregistration changed")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V122_EPISODE_PEAK_CPU_SMOKE"
        or prereg.get("failed_checks") != []
        or prereg.get("authority", {}).get("cpu_smoke_authorized")
        is not True
        or sha256_directory(source)
        != prereg["source"]["checkpoint_directory_sha256"]
    ):
        raise ValueError("V122 CPU smoke is not authorized")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("V122 execution requires a clean worktree")

    work.mkdir(parents=True)
    output = work / "smoke"
    output.mkdir()
    log = work / "training.log"
    sys.path.insert(0, str(playground))
    from playground.open_duck_mini_v2.joystick import (  # noqa: E402
        default_config,
        ground_up_episode_peak_torque_increment_cost,
    )

    threshold = float(prereg["objective"]["threshold_nm"])
    dt = np.float32(0.02)
    force_sequence = np.zeros((6, 14), dtype=np.float32)
    force_sequence[1, 3] = np.float32(threshold + 0.05)
    force_sequence[2, 12] = np.float32(-(threshold + 0.02))
    force_sequence[3, 13] = np.float32(threshold + 0.20)
    force_sequence[4, 3] = np.float32(threshold + 0.10)
    force_sequence[5, 4] = np.float32(threshold + 0.25)
    disabled_costs = []
    disabled_states = []
    previous_disabled = jax.numpy.asarray(np.float32(0.125))
    for force in force_sequence:
        cost, next_state = ground_up_episode_peak_torque_increment_cost(
            jax.numpy.asarray(force),
            previous_disabled,
            threshold,
            float(dt),
            False,
        )
        disabled_costs.append(float(cost))
        disabled_states.append(float(next_state))
        previous_disabled = next_state
    enabled_costs = []
    enabled_states = []
    previous = jax.numpy.asarray(np.float32(0.0))
    for force in force_sequence:
        cost, next_state = ground_up_episode_peak_torque_increment_cost(
            jax.numpy.asarray(force),
            previous,
            threshold,
            float(dt),
            True,
        )
        enabled_costs.append(float(cost))
        enabled_states.append(float(next_state))
        previous = next_state
    analytic_peak = float(
        np.max(
            np.maximum(
                np.max(np.abs(force_sequence), axis=1) - threshold,
                0.0,
            )
        )
    )
    integrated_peak = float(
        np.sum(np.asarray(enabled_costs, dtype=np.float64))
        * float(dt)
    )
    config = default_config()
    default_scale = float(
        config.reward_config.scales.episode_peak_torque_increment
    )
    default_linear_scale = float(
        config.reward_config.scales.linear_peak_torque_exceedance
    )

    command = [
        sys.executable,
        "playground/open_duck_mini_v2/runner.py",
        "--task",
        "flat_terrain_backlash",
        "--env",
        "joystick",
        "--output_dir",
        str(output),
        "--num_timesteps",
        "1024",
        "--ppo_seed",
        "100",
        "--ppo_num_envs",
        "4",
        "--ppo_num_evals",
        "2",
        "--ppo_episode_length",
        "64",
        "--ppo_unroll_length",
        "8",
        "--ppo_batch_size",
        "4",
        "--ppo_num_minibatches",
        "1",
        "--ppo_num_updates_per_batch",
        "2",
        "--ppo_learning_rate",
        "0.0003",
        "--ppo_discounting",
        "0.97",
        "--ppo_entropy_cost",
        "0.005",
        "--policy_architecture",
        "reference_residual_recurrent_adapter",
        "--recurrent_hidden_size",
        "64",
        "--imitation_scale",
        "1.0",
        "--reference_feature_table_path",
        str(REFERENCE),
        "--nominal_reference_bootstrap",
        "--ground_up_hard_vector_command_support",
        "--ground_up_command_support_min_x",
        "0.074",
        "--ground_up_command_support_max_x",
        "0.080",
        "--ground_up_action_velocity_limits_rad_s",
        VELOCITY_LIMITS,
        "--ground_up_measured_actuator_bridge",
        "--ground_up_actuator_bridge_delay_ticks",
        "3,3,3,3,3,3,2,3,3,3,2,3,2,3",
        "--ground_up_actuator_bridge_tau_s",
        ".015,.015,.005,.010,.010,.120,.120,.120,.120,.020,"
        ".035,.010,.030,.005",
        "--ground_up_applied_target_observation",
        "--ground_up_tracking_tail_exceedance_scale",
        "-6572.254964031055",
        "--ground_up_tracking_tail_threshold_rad",
        "0.20",
        "--ground_up_peak_torque_exceedance_scale",
        "0",
        "--ground_up_linear_peak_torque_exceedance_scale",
        "0",
        "--ground_up_episode_peak_torque_increment_scale",
        str(prereg["objective"]["scale"]),
        "--reference_start_phase",
        "0",
        "--ground_up_signed_progress_objective",
        "--winner_v3_variable_configuration",
        "--winner_v3_deviation_scale",
        "1.0",
        "--winner_v119_train_transition_match",
        "--critic_observation",
        "privileged_state",
        "--restore_checkpoint_path",
        str(source),
    ]
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(playground)
    started = time.monotonic()
    completed = subprocess.run(
        command,
        cwd=playground,
        env=environment,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=1800,
        check=False,
    )
    elapsed = time.monotonic() - started
    log.write_text(completed.stdout, encoding="utf-8")
    if completed.returncode != 0:
        raise RuntimeError(
            f"V122 CPU runner failed rc={completed.returncode}; "
            f"tail={completed.stdout[-5000:]}"
        )

    checkpoints = sorted(path for path in output.iterdir() if path.is_dir())
    raw_graphs = sorted(output.glob("*.onnx"))
    checkpoint_steps = sorted(
        int(path.name.rsplit("_", 1)[1]) for path in checkpoints
    )
    onnx_steps = sorted(
        int(path.stem.rsplit("_", 1)[1]) for path in raw_graphs
    )
    if checkpoint_steps != [0, 1024] or onnx_steps != [0, 1024]:
        raise ValueError(
            f"unexpected V122 exports: {checkpoint_steps}, {onnx_steps}"
        )
    initial_checkpoint = next(
        path for path in checkpoints if path.name.endswith("_0")
    )
    final_checkpoint = next(
        path for path in checkpoints if path.name.endswith("_1024")
    )
    checkpointer = ocp.PyTreeCheckpointer()
    template = checkpointer.restore(str(cpu_template))
    source_restore_args = orbax_utils.restore_args_from_target(template)
    source_tree = checkpointer.restore(
        str(source), item=template, restore_args=source_restore_args
    )
    initial_restore_args = orbax_utils.restore_args_from_target(source_tree)
    initial_tree = checkpointer.restore(
        str(initial_checkpoint),
        item=source_tree,
        restore_args=initial_restore_args,
    )
    final_tree = checkpointer.restore(
        str(final_checkpoint),
        item=source_tree,
        restore_args=initial_restore_args,
    )
    initial_structure, initial_deltas = tree_errors(
        source_tree, initial_tree
    )
    trained_structure, trained_deltas = tree_errors(
        initial_tree, final_tree
    )
    policy_deltas = {
        name: value
        for name, value in trained_deltas.items()
        if name.startswith("1/params/")
    }
    all_finite = all(
        np.isfinite(np.asarray(leaf)).all()
        for leaf in jax.tree_util.tree_leaves(final_tree)
    )
    event_file = next(output.glob("events.out.tfevents*"))
    metric_rows = scalar_events(event_file, METRIC_TAG)
    deployed_rows = []
    for raw_path in raw_graphs:
        deployed_path = work / (
            f"v122_deployed_{raw_path.stem.rsplit('_', 1)[1]}.onnx"
        )
        deployed_rows.append(
            deployed_onnx_contract(raw_path, deployed_path)
        )
    expected_io = {
        "inputs": {
            "obs": [1, 115],
            "previous_action": [1, 14],
            "h_in": [1, 64],
        },
        "outputs": {
            "continuous_actions": [1, 14],
            "previous_action_out": [1, 14],
            "h_out": [1, 64],
        },
    }
    checks = {
        "cpu_only": jax.default_backend() == "cpu"
        and all(device.platform == "cpu" for device in jax.devices()),
        "default_off_scale_exact_zero": default_scale == 0.0,
        "existing_linear_scale_default_zero": default_linear_scale == 0.0,
        "disabled_cost_exact_zero": disabled_costs == [0.0] * 6,
        "disabled_state_bit_exact": disabled_states == [0.125] * 6,
        "enabled_state_monotonic": bool(
            np.all(np.diff(np.asarray(enabled_states)) >= 0.0)
        ),
        "enabled_initial_state_reset_zero": enabled_states[0] == 0.0,
        "episode_integral_equals_analytic_peak": (
            abs(integrated_peak - analytic_peak) <= 1.0e-7
        ),
        "exact_exports_0_and_1024": checkpoint_steps == [0, 1024]
        and onnx_steps == [0, 1024],
        "source_restore_structure_exact": initial_structure,
        "source_restore_parameters_bit_exact": max(
            initial_deltas.values(), default=0.0
        )
        == 0.0,
        "trained_structure_exact": trained_structure,
        "trained_tree_all_finite": bool(all_finite),
        "every_policy_leaf_updated": len(policy_deltas) == 15
        and all(value > 0.0 for value in policy_deltas.values()),
        "objective_metric_exact_steps": [
            row["step"] for row in metric_rows
        ]
        == [0, 1024],
        "objective_metric_finite_nonzero": bool(metric_rows)
        and all(
            math.isfinite(row["value"]) and row["value"] > 0.0
            for row in metric_rows
        ),
        "both_raw_train_deltas_exact": all(
            row["raw_train_delta_exact"] for row in deployed_rows
        ),
        "both_final_projection_deltas_exact": all(
            row["final_projection_delta_exact"] for row in deployed_rows
        ),
        "both_deployed_onnx_abis_exact": all(
            row["graph_io"] == expected_io for row in deployed_rows
        ),
        "both_deployed_onnx_contracts_pass": all(
            row["inference"]["pass"] for row in deployed_rows
        ),
        "both_deployed_initializers_finite": all(
            row["initializers_finite"] for row in deployed_rows
        ),
        "wall_seconds_at_most_1800": elapsed <= 1800.0,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    value = {
        "schema_version": "winner_v122.episode_peak_cpu_result.v1",
        "status": (
            "PASS_WINNER_V122_EPISODE_PEAK_CPU_SMOKE"
            if not failed
            else "HOLD_WINNER_V122_EPISODE_PEAK_CPU_SMOKE"
        ),
        "failed_checks": failed,
        "checks": checks,
        "analytic_objective": {
            "threshold_nm": threshold,
            "dt_s": float(dt),
            "disabled_costs": disabled_costs,
            "disabled_states": disabled_states,
            "enabled_costs": enabled_costs,
            "enabled_states": enabled_states,
            "analytic_episode_peak_excess_nm": analytic_peak,
            "integrated_increment_cost_nm": integrated_peak,
            "max_abs_error_nm": abs(integrated_peak - analytic_peak),
            "default_scale": default_scale,
            "default_linear_scale": default_linear_scale,
        },
        "training": {
            "command": command,
            "elapsed_seconds": elapsed,
            "checkpoint_steps": checkpoint_steps,
            "onnx_steps": onnx_steps,
            "initial_checkpoint_sha256": sha256_directory(
                initial_checkpoint
            ),
            "final_checkpoint_sha256": sha256_directory(final_checkpoint),
            "event_sha256": sha256(event_file),
            "log_sha256": sha256(log),
            "objective_metric": {
                "tag": METRIC_TAG,
                "events": metric_rows,
            },
            "policy_leaf_deltas": policy_deltas,
        },
        "deployed_onnx": deployed_rows,
        "input_hashes": {
            "preregistration": sha256(PREREG),
            "source_checkpoint": sha256_directory(source),
            "cpu_template": sha256_directory(cpu_template),
            "playground_manifest": sha256(
                playground / "WINNER_V122_COMPOSED_SOURCE_MANIFEST.json"
            ),
            "v121_transform": sha256(V121_TRANSFORM),
        },
        "execution": {
            "formal_behavior_cells": 0,
            "colab_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "hosted_preregistration_authorized": not failed,
            "hosted_training_authorized": False,
            "colab_authorized": False,
            "behavior_evaluation_authorized": False,
            "checkpoint_selection_authorized": False,
            "gate5_authorized": False,
            "robot_clearance": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner-v122 episode-peak CPU result\n\n"
        f"Status: `{value['status']}`\n\n"
        f"Failed checks: `{failed}`\n\n"
        "This is a CPU mechanics smoke only. It executes no formal behavior "
        "cells and grants no Colab, Gate 5, RDK-X5, or robot authority.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(RESULT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
