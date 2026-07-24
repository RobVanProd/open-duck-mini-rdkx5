#!/usr/bin/env python3
"""Run the preregistered V119 transition-match CPU mechanics smoke."""

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
PREREG = ANALYSIS / "winner_v119_transition_cpu_preregistration.json"
RESULT = ANALYSIS / "winner_v119_transition_cpu_result.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V119_TRANSITION_CPU_RESULT_20260724.md"
)
PREREG_SHA256 = (
    "55f44915f750d29846df9aa0a5b6afaac3e12097e86ec4b26f7a637ffd1a2bee"
)
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
VELOCITY_LIMITS = (
    "1.0,.75,1.4736209064722061,1.4300791546702385,"
    "1.3976470567286015,.5,.5,.5,.5,.5,.75,1.25,1.0,"
    "1.2215287424623966"
)
METRIC_TAG = "eval/episode_cost/linear_peak_torque_exceedance"


def deployed_onnx_contract(
    raw_path: Path,
    output_path: Path,
    *,
    prereg: dict,
) -> dict:
    transition = prereg["transition"]
    selected_delta = np.asarray(
        transition["selected_normalized_action_delta"], dtype=np.float32
    )
    raw_model = onnx.load(raw_path)
    guard_prereg = json.loads(
        (
            ANALYSIS
            / "ground_up_actual_centered_guard_screen_preregistration.json"
        ).read_text(encoding="utf-8")
    )
    deadband_prereg = json.loads(
        (
            ANALYSIS
            / "ground_up_command_deadband_repair_preregistration.json"
        ).read_text(encoding="utf-8")
    )
    guard = guard_prereg["guard_contract"]
    guarded = append_guard(
        raw_model,
        obs_indices=np.asarray(
            guard["measured_joint_offset_indices"], dtype=np.int64
        ),
        pitch_indices=np.asarray(
            guard["pitch_chain_action_indices"], dtype=np.int64
        ),
        home=np.asarray(guard["home_target_rad"], dtype=np.float32),
        action_scale=float(guard["action_scale_rad"]),
        margin=float(transition["actual_centered_guard_margin_rad"]),
    )
    command_index = int(
        deadband_prereg["transform"]["command_x_observation_index"]
    )
    deadband = float(
        deadband_prereg["transform"][
            "zero_deadband_absolute_command_x"
        ]
    )
    deadbanded = append_deadband(
        guarded, command_index=command_index, deadband=deadband
    )
    deployed = append_projection(
        deadbanded,
        selected_delta=selected_delta,
        command_index=command_index,
        deadband=deadband,
    )
    onnx.checker.check_model(deployed)
    onnx.save(deployed, output_path)
    changed_indices = np.asarray(
        [2, 3, 4, 13], dtype=np.int64
    )
    inference = inference_contract(
        raw_path,
        output_path,
        selected_delta=selected_delta,
        changed_indices=changed_indices,
        command_index=command_index,
        deadband=deadband,
        home=np.asarray(guard["home_target_rad"], dtype=np.float32),
        pitch_indices=np.asarray(
            guard["pitch_chain_action_indices"], dtype=np.int64
        ),
        actual_obs_indices=np.asarray(
            guard["measured_joint_offset_indices"], dtype=np.int64
        ),
        action_scale=float(guard["action_scale_rad"]),
        guard_margin=float(
            transition["actual_centered_guard_margin_rad"]
        ),
    )
    return {
        "raw_sha256": sha256(raw_path),
        "deployed_sha256": sha256(output_path),
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
        raise FileExistsError(f"refusing to reuse V119 work root: {work}")
    if RESULT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite V119 CPU result")
    if sha256(PREREG) != PREREG_SHA256:
        raise ValueError("V119 preregistration changed")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V119_TRANSITION_CPU_SMOKE"
        or prereg.get("failed_checks") != []
        or prereg.get("authority", {}).get("cpu_smoke_authorized")
        is not True
        or sha256_directory(source)
        != prereg["source"]["checkpoint_directory_sha256"]
    ):
        raise ValueError("V119 CPU smoke is not authorized")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("V119 execution requires a clean worktree")

    work.mkdir(parents=True)
    output = work / "smoke"
    output.mkdir()
    log = work / "training.log"
    sys.path.insert(0, str(playground))
    from playground.open_duck_mini_v2.joystick import (  # noqa: E402
        WINNER_V119_GUARD_MARGIN_RAD,
        WINNER_V119_PITCH_MASK,
        WINNER_V119_RATE_LIMITS_RAD_S,
        default_config,
        winner_v119_transition_match,
    )

    rng = np.random.default_rng(20260724)
    proposed = rng.uniform(-1.0, 1.0, (128, 14)).astype(np.float32)
    previous = rng.uniform(-0.5, 0.5, (128, 14)).astype(np.float32)
    actual = rng.uniform(-0.5, 0.5, (128, 14)).astype(np.float32)
    rates = np.asarray(WINNER_V119_RATE_LIMITS_RAD_S, dtype=np.float32)
    disabled = np.asarray(
        winner_v119_transition_match(
            jax.numpy.asarray(proposed),
            jax.numpy.asarray(previous),
            jax.numpy.asarray(actual),
            jax.numpy.asarray(rates),
            0.02,
            False,
        )
    )
    enabled = np.asarray(
        winner_v119_transition_match(
            jax.numpy.asarray(proposed),
            jax.numpy.asarray(previous),
            jax.numpy.asarray(actual),
            jax.numpy.asarray(rates),
            0.02,
            True,
        )
    )
    margin = np.float32(WINNER_V119_GUARD_MARGIN_RAD)
    mask = np.asarray(WINNER_V119_PITCH_MASK, dtype=np.bool_)
    guarded = np.clip(proposed, actual - margin, actual + margin)
    guarded = np.where(mask[None], guarded, proposed)
    expected = np.clip(
        guarded,
        previous - rates[None] * np.float32(0.02),
        previous + rates[None] * np.float32(0.02),
    )
    analytic_error = float(np.max(np.abs(enabled - expected)))
    max_rate_excess = float(
        np.max(
            np.abs(enabled - previous)
            - rates[None] * np.float32(0.02)
        )
    )
    config = default_config()
    expected_rates = np.asarray(
        prereg["transition"]["rate_limits_rad_s"], dtype=np.float32
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
        "-307.48131091308585",
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
            f"V119 CPU runner failed rc={completed.returncode}; "
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
            f"unexpected V119 exports: {checkpoint_steps}, {onnx_steps}"
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
        step = int(raw_path.stem.rsplit("_", 1)[1])
        deployed_path = work / f"v119_deployed_{step}.onnx"
        row = deployed_onnx_contract(
            raw_path, deployed_path, prereg=prereg
        )
        row["step"] = step
        deployed_rows.append(row)
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
        "default_off_config_exact_false": (
            config.winner_v119_train_transition_match is False
        ),
        "default_off_transition_bit_exact": np.array_equal(
            disabled, proposed
        ),
        "enabled_transition_matches_analytic": analytic_error <= 1.0e-7,
        "enabled_final_rate_bound_exact": max_rate_excess <= 1.0e-7,
        "v117_rate_vector_float32_exact": np.array_equal(
            rates, expected_rates
        ),
        "guard_margin_exact": float(margin) == np.float32(0.165),
        "exact_exports_0_and_1024": checkpoint_steps == [0, 1024]
        and onnx_steps == [0, 1024],
        "source_restore_structure_exact": initial_structure,
        "source_restore_parameters_bit_exact": max(
            initial_deltas.values(), default=0.0
        )
        == 0.0,
        "trained_structure_exact": trained_structure,
        "trained_tree_all_finite": bool(all_finite),
        "every_policy_leaf_updated": bool(policy_deltas)
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
        "schema_version": "winner_v119.transition_cpu_result.v1",
        "status": (
            "PASS_WINNER_V119_TRANSITION_CPU_SMOKE"
            if not failed
            else "HOLD_WINNER_V119_TRANSITION_CPU_SMOKE"
        ),
        "failed_checks": failed,
        "checks": checks,
        "transition_contract": {
            "analytic_max_abs_error": analytic_error,
            "max_rate_excess_rad": max_rate_excess,
            "default_off_bit_exact": np.array_equal(disabled, proposed),
            "rate_limits_float32": rates.tolist(),
            "guard_margin_rad": float(margin),
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
            "playground_manifest": sha256(
                playground / "WINNER_V119_COMPOSED_SOURCE_MANIFEST.json"
            ),
        },
        "authority": {
            "hosted_preregistration_authorized": not failed,
            "hosted_training_authorized": False,
            "colab_authorized": False,
            "behavior_evaluation_authorized": False,
            "checkpoint_selection_authorized": False,
            "gate5_authorized": False,
            "rdkx5_or_robot": False,
            "robot_clearance": False,
            "torque_or_motion": False,
        },
    }
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner-v119 transition CPU result\n\n"
        f"Status: `{value['status']}`\n\n"
        "The default-off transition, enabled analytic hierarchy, exact "
        "V114-final restore, finite 1,024-step update, all actor leaves, and "
        "both stateful postexport ONNX chains are checked on CPU. A pass "
        "authorizes only a separate hosted preregistration; it does not "
        "authorize Colab execution, behavior, Gate 5, or robot work.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(RESULT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
