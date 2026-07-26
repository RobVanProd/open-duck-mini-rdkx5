#!/usr/bin/env python3
"""Run T20's preregistered support train-through one-update CPU contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""
os.environ["ROCR_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"

from flax.training import orbax_utils
import jax
import numpy as np
from orbax import checkpoint as ocp


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs" / "analysis"
sys.path.insert(0, str(TOOLS))

from build_t8_state_coherent_handoff_assets import (  # noqa: E402
    add_context_input,
    parity_contract,
)
from run_winner_v111_peak_torque_cpu_smoke import (  # noqa: E402
    sha256_directory,
    tree_errors,
)
from run_winner_v114_linear_torque_cpu_smoke import (  # noqa: E402
    scalar_events,
)
from t18_rate_coherent_support_onnx import (  # noqa: E402
    verify_wrapper,
    wrap_rate_coherent_support,
)


PREREGISTRATION = (
    ANALYSIS / "t20_support_trainthrough_one_update_preregistration.json"
)
RESULT = ANALYSIS / "t20_support_trainthrough_one_update_result.json"
MARKDOWN = (
    ANALYSIS / "T20_SUPPORT_TRAINTHROUGH_ONE_UPDATE_RESULT_20260726.md"
)
VELOCITY_LIMITS = (
    "1.0,.75,1.5,1.5,1.5,.5,.5,.5,.5,.5,.75,1.25,1.0,1.25"
)
EXPECTED_RAW_INPUTS = {
    "obs": [1, 115],
    "previous_action": [1, 14],
    "h_in": [1, 64],
}
EXPECTED_CONTEXT_INPUTS = {
    **EXPECTED_RAW_INPUTS,
    "calibration_context": [1, 64],
}
EXPECTED_OUTPUTS = {
    "continuous_actions": [1, 14],
    "previous_action_out": [1, 14],
    "h_out": [1, 64],
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


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def directory_receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "sha256": sha256_directory(path),
    }


def verify_receipt(value: dict[str, Any], label: str) -> None:
    path = Path(value["path"])
    kind = value["kind"]
    if kind == "file":
        valid = (
            path.is_file()
            and path.stat().st_size == value["bytes"]
            and sha256(path) == value["sha256"]
        )
    elif kind == "directory":
        valid = path.is_dir() and sha256_directory(path) == value["sha256"]
    else:
        raise ValueError(f"unknown T20 receipt kind: {kind}")
    if not valid:
        raise RuntimeError(f"T20 frozen receipt changed: {label}")


def validate_preregistration(value: dict[str, Any]) -> None:
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        value.get("status")
        != "PREREGISTERED_T20_SUPPORT_TRAINTHROUGH_ONE_UPDATE"
        or canonical_sha256(basis)
        != value.get("preregistered_contract_sha256")
    ):
        raise RuntimeError("T20 preregistration identity changed")
    for name, item in value["sources"].items():
        verify_receipt(item, name)
    for name, item in value["assets"].items():
        verify_receipt(item, name)


def training_command(
    *,
    python: Path,
    output: Path,
    reference: Path,
    restore: Path,
) -> list[str]:
    return [
        str(python),
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
        str(reference),
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
        "--winner_t19_support_trainthrough",
        "--critic_observation",
        "privileged_state",
        "--restore_checkpoint_path",
        str(restore),
    ]


def remap_checkpoint(
    source: Path,
    template: Path,
    output: Path,
) -> tuple[Any, dict[str, Any]]:
    checkpointer = ocp.PyTreeCheckpointer()
    template_tree = checkpointer.restore(str(template))
    source_tree = checkpointer.restore(
        str(source),
        item=template_tree,
        restore_args=orbax_utils.restore_args_from_target(template_tree),
    )
    checkpointer.save(
        str(output),
        source_tree,
        save_args=orbax_utils.save_args_from_target(source_tree),
    )
    restored = checkpointer.restore(
        str(output),
        item=source_tree,
        restore_args=orbax_utils.restore_args_from_target(source_tree),
    )
    structure, deltas = tree_errors(source_tree, restored)
    return source_tree, {
        "source": directory_receipt(source),
        "template": directory_receipt(template),
        "remapped": directory_receipt(output),
        "structure_exact": structure,
        "maximum_abs_error": max(deltas.values(), default=0.0),
        "all_leaves_exact": all(value == 0.0 for value in deltas.values()),
    }


def graph_io(path: Path) -> dict[str, Any]:
    import onnxruntime as ort

    session = ort.InferenceSession(
        str(path), providers=["CPUExecutionProvider"]
    )
    return {
        "inputs": {item.name: list(item.shape) for item in session.get_inputs()},
        "outputs": {
            item.name: list(item.shape) for item in session.get_outputs()
        },
        "providers": session.get_providers(),
    }


def deployment_graph(
    raw: Path,
    output_root: Path,
) -> dict[str, Any]:
    output_root.mkdir(parents=True)
    context = output_root / "context_abi.onnx"
    wrapped = output_root / "rate_coherent_support.onnx"
    add_context_input(raw, context)
    context_parity = parity_contract(raw, context)
    wrapper = wrap_rate_coherent_support(context, wrapped)
    verification = verify_wrapper(context, wrapped)
    return {
        "raw": receipt(raw),
        "raw_io": graph_io(raw),
        "context_abi": receipt(context),
        "context_io": graph_io(context),
        "context_parity": context_parity,
        "wrapped": receipt(wrapped),
        "wrapped_io": graph_io(wrapped),
        "wrapper": wrapper,
        "verification": verification,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-root", required=True, type=Path)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise SystemExit("T20 formal CPU contract requires --execute")
    for path in (RESULT, MARKDOWN, args.work_root):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T20 path: {path}")
    prereg = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(prereg)
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T20 execution requires a clean worktree")

    work = args.work_root.resolve()
    work.mkdir(parents=True)
    smoke = work / "smoke"
    smoke.mkdir()
    source = Path(prereg["assets"]["source_checkpoint"]["path"])
    template = Path(prereg["assets"]["cpu_topology_template"]["path"])
    reference = Path(prereg["sources"]["reference"]["path"])
    playground = Path(prereg["playground"]["path"])
    remapped = work / "cpu_source_checkpoint"
    source_tree, remap = remap_checkpoint(source, template, remapped)

    command = training_command(
        python=Path(sys.executable),
        output=smoke,
        reference=reference,
        restore=remapped,
    )
    environment = dict(os.environ)
    environment.update(
        {
            "PYTHONPATH": str(playground),
            "CUDA_VISIBLE_DEVICES": "",
            "HIP_VISIBLE_DEVICES": "",
            "ROCR_VISIBLE_DEVICES": "",
            "JAX_PLATFORMS": "cpu",
            "JAX_PLATFORM_NAME": "cpu",
            "XLA_PYTHON_CLIENT_PREALLOCATE": "false",
            "JAX_COMPILATION_CACHE_DIR": str(
                Path(
                    "D:/CodexArtifacts/open-duck-policy/"
                    "jax_compilation_cache"
                )
            ),
        }
    )
    started = time.monotonic()
    completed = subprocess.run(
        command,
        cwd=playground,
        env=environment,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=1800,
    )
    elapsed = time.monotonic() - started
    log = work / "training.log"
    log.write_text(
        completed.stdout,
        encoding="utf-8",
        newline="\n",
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"T20 CPU runner failed rc={completed.returncode}\n"
            f"{completed.stdout[-12000:]}"
        )

    checkpoints = sorted(path for path in smoke.iterdir() if path.is_dir())
    raw_graphs = sorted(smoke.glob("*.onnx"))
    checkpoint_steps = sorted(
        int(path.name.rsplit("_", 1)[1]) for path in checkpoints
    )
    onnx_steps = sorted(
        int(path.stem.rsplit("_", 1)[1]) for path in raw_graphs
    )
    if checkpoint_steps != [0, 1024] or onnx_steps != [0, 1024]:
        raise RuntimeError(
            f"T20 export steps changed: {checkpoint_steps}, {onnx_steps}"
        )
    initial_checkpoint = next(
        path for path in checkpoints if path.name.endswith("_0")
    )
    final_checkpoint = next(
        path for path in checkpoints if path.name.endswith("_1024")
    )
    initial_raw = next(
        path for path in raw_graphs if path.stem.endswith("_0")
    )
    final_raw = next(
        path for path in raw_graphs if path.stem.endswith("_1024")
    )
    checkpointer = ocp.PyTreeCheckpointer()
    restore_args = orbax_utils.restore_args_from_target(source_tree)
    initial_tree = checkpointer.restore(
        str(initial_checkpoint),
        item=source_tree,
        restore_args=restore_args,
    )
    final_tree = checkpointer.restore(
        str(final_checkpoint),
        item=source_tree,
        restore_args=restore_args,
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
    critic_deltas = {
        name: value
        for name, value in trained_deltas.items()
        if name.startswith("2/params/")
    }
    final_finite = all(
        np.isfinite(np.asarray(leaf)).all()
        for leaf in jax.tree_util.tree_leaves(final_tree)
    )
    deployments = {
        "0": deployment_graph(initial_raw, work / "deployment" / "0"),
        "1024": deployment_graph(
            final_raw, work / "deployment" / "1024"
        ),
    }
    event_file = next(smoke.glob("events.out.tfevents*"))
    reward_events = scalar_events(event_file, "eval/episode_reward")
    expected_raw_io = {
        "inputs": EXPECTED_RAW_INPUTS,
        "outputs": EXPECTED_OUTPUTS,
    }
    expected_context_io = {
        "inputs": EXPECTED_CONTEXT_INPUTS,
        "outputs": EXPECTED_OUTPUTS,
    }
    frozen_source = prereg["assets"]["source_v121_half_onnx"]["sha256"]
    frozen_context = prereg["assets"][
        "frozen_t18_context_abi_onnx"
    ]["sha256"]
    frozen_wrapped = prereg["assets"]["frozen_t18_wrapped_onnx"]["sha256"]
    initial_deployment = deployments["0"]
    all_context_parity = all(
        row["context_parity"]["all_outputs_bit_exact"]
        and all(
            value == 0.0
            for value in row["context_parity"]["maximum_abs_errors"].values()
        )
        for row in deployments.values()
    )
    all_wrapper_contracts = all(
        row["verification"]["maximum_action_error"] == 0.0
        and row["verification"]["maximum_previous_action_error"] == 0.0
        and row["verification"]["maximum_hidden_error"] == 0.0
        and row["verification"]["maximum_normalized_rate_excess"]
        <= 32.0 * float(np.finfo(np.float32).eps)
        and row["verification"][
            "previous_action_out_equals_action_bit_exact"
        ]
        and row["verification"]["x0_output_equals_support_action_bit_exact"]
        and row["verification"]["output_bounds_exact"]
        for row in deployments.values()
    )
    checks = {
        "cpu_only": (
            jax.default_backend() == "cpu"
            and all(device.platform == "cpu" for device in jax.devices())
        ),
        "cpu_topology_remap_structure_exact": remap["structure_exact"],
        "cpu_topology_remap_leaf_exact": (
            remap["all_leaves_exact"]
            and remap["maximum_abs_error"] == 0.0
        ),
        "exact_exports_0_and_1024": (
            checkpoint_steps == [0, 1024]
            and onnx_steps == [0, 1024]
        ),
        "source_restore_structure_exact": initial_structure,
        "source_restore_leaf_exact": (
            max(initial_deltas.values(), default=0.0) == 0.0
        ),
        "trained_structure_exact": trained_structure,
        "trained_tree_finite": bool(final_finite),
        "every_policy_leaf_updated": (
            bool(policy_deltas)
            and all(value > 0.0 for value in policy_deltas.values())
        ),
        "every_critic_leaf_updated": (
            bool(critic_deltas)
            and all(value > 0.0 for value in critic_deltas.values())
        ),
        "reward_metric_exact_steps": (
            [row["step"] for row in reward_events] == [0, 1024]
        ),
        "reward_metric_finite": (
            bool(reward_events)
            and all(math.isfinite(row["value"]) for row in reward_events)
        ),
        "step_zero_raw_onnx_byte_exact": (
            initial_deployment["raw"]["sha256"] == frozen_source
        ),
        "step_zero_context_abi_byte_exact": (
            initial_deployment["context_abi"]["sha256"]
            == frozen_context
        ),
        "step_zero_physical_wrapper_byte_exact": (
            initial_deployment["wrapped"]["sha256"] == frozen_wrapped
        ),
        "all_raw_graph_abis_exact": all(
            {
                "inputs": row["raw_io"]["inputs"],
                "outputs": row["raw_io"]["outputs"],
            }
            == expected_raw_io
            for row in deployments.values()
        ),
        "all_context_and_wrapped_abis_exact": all(
            {
                "inputs": row["context_io"]["inputs"],
                "outputs": row["context_io"]["outputs"],
            }
            == expected_context_io
            and {
                "inputs": row["wrapped_io"]["inputs"],
                "outputs": row["wrapped_io"]["outputs"],
            }
            == expected_context_io
            for row in deployments.values()
        ),
        "context_input_is_bit_exactly_ignored": all_context_parity,
        "both_physical_wrapper_contracts_pass": all_wrapper_contracts,
        "command_uses_t19_transition": (
            "--winner_t19_support_trainthrough" in command
            and command[
                command.index(
                    "--ground_up_action_velocity_limits_rad_s"
                )
                + 1
            ]
            == VELOCITY_LIMITS
        ),
        "wall_seconds_at_most_1800": elapsed <= 1800.0,
        "formal_behavior_cells_zero": True,
        "hosted_compute_zero": True,
        "robot_access_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    result_basis = {
        "schema_version": (
            "open_duck.t20_support_trainthrough_one_update_result.v1"
        ),
        "status": (
            "PASS_T20_SUPPORT_TRAINTHROUGH_ONE_UPDATE"
            if not failed
            else "HOLD_T20_SUPPORT_TRAINTHROUGH_ONE_UPDATE"
        ),
        "decision": (
            "EARN_T20_HOSTED_CONTINUATION_PREREGISTRATION"
            if not failed
            else "KEEP_T19_HOSTED_TRAINING_CLOSED"
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "cpu_topology_remap": remap,
        "training": {
            "command": command,
            "elapsed_seconds": elapsed,
            "checkpoint_steps": checkpoint_steps,
            "onnx_steps": onnx_steps,
            "initial_checkpoint": directory_receipt(initial_checkpoint),
            "final_checkpoint": directory_receipt(final_checkpoint),
            "event_file": receipt(event_file),
            "log": receipt(log),
            "reward_events": reward_events,
            "policy_leaf_deltas": policy_deltas,
            "critic_leaf_deltas": critic_deltas,
        },
        "deployments": deployments,
        "execution": {
            "cpu_simulator_steps": 1024,
            "formal_behavior_cells": 0,
            "hosted_or_colab_compute": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "hosted_preregistration_authorized": not failed,
            "hosted_training_authorized": False,
            "behavior_matrix_authorized": False,
            "checkpoint_selection_authorized": False,
            "policy_deployment_authorized": False,
            "gate5_authorized": False,
            "robot_or_rdk_access": False,
            "torque_or_motion": False,
        },
    }
    value = {
        **result_basis,
        "result_sha256": canonical_sha256(result_basis),
    }
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T20 support train-through one-update result",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                f"- Failed checks: `{failed}`",
                "- CPU simulator steps: `1,024`",
                "- Formal behavior cells: `0`",
                "- Hosted/robot execution: `0/0`",
                f"- Result SHA-256: `{value['result_sha256']}`",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
