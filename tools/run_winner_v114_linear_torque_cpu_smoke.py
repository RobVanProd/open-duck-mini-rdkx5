#!/usr/bin/env python3
"""Run the preregistered V114 linear-torque CPU mechanics smoke."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import struct
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
import onnxruntime as ort
from orbax import checkpoint as ocp
from tensorboardX.proto.event_pb2 import Event


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from run_winner_v111_peak_torque_cpu_smoke import (  # noqa: E402
    sha256,
    sha256_directory,
    tree_errors,
)


ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v114_linear_torque_cpu_preregistration.json"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
RESULT = ANALYSIS / "winner_v114_linear_torque_cpu_result.json"
MARKDOWN = ANALYSIS / "WINNER_V114_LINEAR_TORQUE_CPU_RESULT_20260724.md"
PREREG_SHA256 = (
    "2b1a25ac1f7b9728f728c366bae6ad071c4b71b6b92f07e90ed89c64360ae65a"
)
VELOCITY_LIMITS = (
    "1.0,.75,1.5,1.5,1.5,.5,.5,.5,.5,.5,.75,1.25,1.0,1.25"
)
LINEAR_SCALE = "-307.48131091308585"
METRIC_TAG = "eval/episode_cost/linear_peak_torque_exceedance"


def scalar_events(path: Path, tag: str) -> list[dict[str, float | int]]:
    rows: list[dict[str, float | int]] = []
    with path.open("rb") as stream:
        while True:
            length_bytes = stream.read(8)
            if not length_bytes:
                break
            if len(length_bytes) != 8:
                raise ValueError("truncated TensorBoard event length")
            length = struct.unpack("<Q", length_bytes)[0]
            stream.read(4)
            payload = stream.read(length)
            stream.read(4)
            event = Event()
            event.ParseFromString(payload)
            if not event.HasField("summary"):
                continue
            for value in event.summary.value:
                if value.tag == tag:
                    rows.append(
                        {
                            "step": int(event.step),
                            "value": float(value.simple_value),
                        }
                    )
    return rows


def onnx_contract(path: Path) -> dict[str, object]:
    model = onnx.load(path)
    inputs = {
        item.name: [
            dim.dim_value for dim in item.type.tensor_type.shape.dim
        ]
        for item in model.graph.input
    }
    outputs = {
        item.name: [
            dim.dim_value for dim in item.type.tensor_type.shape.dim
        ]
        for item in model.graph.output
    }
    expected_inputs = {
        "obs": [1, 115],
        "previous_action": [1, 14],
        "h_in": [1, 64],
    }
    expected_outputs = {
        "continuous_actions": [1, 14],
        "previous_action_out": [1, 14],
        "h_out": [1, 64],
    }
    session = ort.InferenceSession(
        path.read_bytes(), providers=["CPUExecutionProvider"]
    )
    previous = np.zeros((1, 14), dtype=np.float32)
    hidden = np.zeros((1, 64), dtype=np.float32)
    chain_finite = True
    for tick in range(256):
        obs = np.linspace(-0.2, 0.2, 115, dtype=np.float32)[None]
        obs += np.float32(tick * 1.0e-5)
        action, previous, hidden = session.run(
            ["continuous_actions", "previous_action_out", "h_out"],
            {"obs": obs, "previous_action": previous, "h_in": hidden},
        )
        chain_finite &= bool(
            np.isfinite(action).all()
            and np.isfinite(previous).all()
            and np.isfinite(hidden).all()
        )
    return {
        "abi_exact": inputs == expected_inputs and outputs == expected_outputs,
        "cpu_provider_exact": session.get_providers()
        == ["CPUExecutionProvider"],
        "chain_256_finite": chain_finite,
        "initializers_finite": all(
            np.isfinite(onnx.numpy_helper.to_array(item)).all()
            for item in model.graph.initializer
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
        raise FileExistsError(f"refusing to reuse V114 work root: {work}")
    if RESULT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite V114 CPU result")
    if sha256(PREREG) != PREREG_SHA256:
        raise ValueError("V114 preregistration changed")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V114_LINEAR_TORQUE_CPU_SMOKE"
        or prereg.get("failed_checks") != []
        or prereg.get("authority", {}).get("cpu_smoke_authorized")
        is not True
        or sha256_directory(source)
        != prereg["source"]["checkpoint_directory_sha256"]
    ):
        raise ValueError("V114 CPU smoke is not authorized")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("V114 execution requires a clean worktree")
    work.mkdir(parents=True)
    output = work / "smoke"
    output.mkdir()
    log = work / "training.log"

    sys.path.insert(0, str(playground))
    from playground.open_duck_mini_v2.joystick import (  # noqa: E402
        default_config,
        ground_up_linear_peak_torque_exceedance_cost,
    )

    threshold = float(prereg["objective"]["threshold_nm"])
    analytic_force = np.zeros(14, dtype=np.float32)
    analytic_force[3] = np.float32(threshold + 0.2)
    observed_cost = float(
        ground_up_linear_peak_torque_exceedance_cost(
            jax.numpy.asarray(analytic_force), threshold
        )
    )
    expected_cost = float(
        np.mean(np.maximum(np.abs(analytic_force) - threshold, 0.0))
    )
    config = default_config()
    default_linear = float(
        config.reward_config.scales.linear_peak_torque_exceedance
    )
    default_squared = float(
        config.reward_config.scales.peak_torque_exceedance
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
        ".015,.015,.005,.010,.010,.120,.120,.120,.120,.020,.035,.010,.030,.005",
        "--ground_up_applied_target_observation",
        "--ground_up_tracking_tail_exceedance_scale",
        "-6572.254964031055",
        "--ground_up_tracking_tail_threshold_rad",
        "0.20",
        "--ground_up_peak_torque_exceedance_scale",
        "0",
        "--ground_up_linear_peak_torque_exceedance_scale",
        LINEAR_SCALE,
        "--reference_start_phase",
        "0",
        "--ground_up_signed_progress_objective",
        "--winner_v3_variable_configuration",
        "--winner_v3_deviation_scale",
        "1.0",
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
            f"V114 CPU runner failed rc={completed.returncode}; "
            f"tail={completed.stdout[-4000:]}"
        )
    checkpoints = sorted(path for path in output.iterdir() if path.is_dir())
    graphs = sorted(output.glob("*.onnx"))
    checkpoint_steps = sorted(
        int(path.name.rsplit("_", 1)[1]) for path in checkpoints
    )
    onnx_steps = sorted(
        int(path.stem.rsplit("_", 1)[1]) for path in graphs
    )
    if checkpoint_steps != [0, 1024] or onnx_steps != [0, 1024]:
        raise ValueError(
            f"unexpected V114 exports: {checkpoint_steps}, {onnx_steps}"
        )
    initial_checkpoint = next(
        path for path in checkpoints if path.name.endswith("_0")
    )
    final_checkpoint = next(
        path for path in checkpoints if path.name.endswith("_1024")
    )
    final_onnx = next(path for path in graphs if path.stem.endswith("_1024"))
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
    graph_contract = onnx_contract(final_onnx)
    checks = {
        "cpu_only": jax.default_backend() == "cpu"
        and all(device.platform == "cpu" for device in jax.devices()),
        "analytic_linear_hinge_exact": (
            abs(observed_cost - expected_cost) <= 1.0e-8
        ),
        "default_off_linear_scale_exact_zero": default_linear == 0.0,
        "default_off_squared_scale_exact_zero": default_squared == 0.0,
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
        "onnx_abi_exact": bool(graph_contract["abi_exact"]),
        "onnx_cpu_provider_exact": bool(
            graph_contract["cpu_provider_exact"]
        ),
        "onnx_256_tick_chain_finite": bool(
            graph_contract["chain_256_finite"]
        ),
        "onnx_initializers_finite": bool(
            graph_contract["initializers_finite"]
        ),
        "wall_seconds_at_most_1800": elapsed <= 1800.0,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    result = {
        "schema_version": "winner_v114.linear_torque_cpu_result.v1",
        "status": (
            "PASS_WINNER_V114_LINEAR_TORQUE_CPU_SMOKE"
            if not failed
            else "HOLD_WINNER_V114_LINEAR_TORQUE_CPU_SMOKE"
        ),
        "failed_checks": failed,
        "checks": checks,
        "analytic_objective": {
            "observed": observed_cost,
            "expected": expected_cost,
            "max_abs_error": abs(observed_cost - expected_cost),
            "default_linear_scale": default_linear,
            "default_squared_scale": default_squared,
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
            "final_onnx_sha256": sha256(final_onnx),
            "event_sha256": sha256(event_file),
            "log_sha256": sha256(log),
            "objective_metric": {
                "tag": METRIC_TAG,
                "events": metric_rows,
            },
            "policy_leaf_deltas": policy_deltas,
        },
        "input_hashes": {
            "preregistration": sha256(PREREG),
            "source_checkpoint": sha256_directory(source),
            "cpu_template": sha256_directory(cpu_template),
            "composed_manifest": sha256(
                playground / "WINNER_V114_COMPOSED_SOURCE_MANIFEST.json"
            ),
        },
        "run_root": str(work),
        "authority": {
            "hosted_preregistration_authorized": not failed,
            "hosted_training_authorized": False,
            "behavior_evaluation_authorized": False,
            "checkpoint_selection_authorized": False,
            "gate5_authorized": False,
            "robot_clearance": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    RESULT.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner-v114 linear-torque CPU smoke result\n\n"
        f"Status: `{result['status']}`\n\n"
        f"Failed checks: `{failed}`\n\n"
        f"Wall time: `{elapsed}` s\n\n"
        f"Objective events: `{metric_rows}`\n\n"
        "A pass authorizes only a separate hosted-run preregistration. It "
        "does not authorize hosted training by itself, behavior selection, "
        "Gate 5, robot use, torque, or motion.\n",
        encoding="utf-8",
    )
    print(result["status"])
    print(f"result_sha256={sha256(RESULT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
