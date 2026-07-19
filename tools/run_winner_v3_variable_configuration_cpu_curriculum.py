#!/usr/bin/env python3
"""Run the one frozen winner-v3 CPU curriculum without retry or subprocesses."""

from __future__ import annotations

import argparse
import contextlib
import gc
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tarfile
import time
import traceback
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""
os.environ["ROCR_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"

import flax
from flax.training import orbax_utils
import jax
import numpy as np
import onnx
from orbax import checkpoint as ocp


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
RECURRENT_CONTRACT = ANALYSIS / "winner_v3_recurrent_adapter_cpu_contract.json"
CURRICULUM_CONTRACT = ANALYSIS / "winner_v3_variable_configuration_curriculum_contract.json"
LAUNCH_CONTRACT = ANALYSIS / "winner_v3_cpu_curriculum_launch_contract.json"
ARCHIVE = ANALYSIS / "GROUND_UP_TRACKING_TAIL_artifacts.tar.gz"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
OUTPUT_JSON = ANALYSIS / "winner_v3_recurrent_adapter_training_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V3_RECURRENT_ADAPTER_TRAINING_RESULT_20260719.md"
OUTPUT_ARCHIVE = ANALYSIS / "winner_v3_recurrent_adapter_artifacts.tar.gz"
SOURCE_MEMBER = Path(
    "ground_up_tracking_tail_outputs/T2_EQUAL/2026_07_14_190026_512000"
)
STAGES = (
    {
        "id": "DOMAIN_25_PERCENT",
        "deviation_scale": 0.25,
        "steps": 245_760,
        "num_evals": 2,
        "expected_steps": [0, 245_760],
    },
    {
        "id": "DOMAIN_50_PERCENT",
        "deviation_scale": 0.5,
        "steps": 245_760,
        "num_evals": 2,
        "expected_steps": [0, 245_760],
    },
    {
        "id": "DOMAIN_100_PERCENT",
        "deviation_scale": 1.0,
        "steps": 2_007_040,
        "num_evals": 3,
        "expected_steps": [0, 1_003_520, 2_007_040],
    },
)
VELOCITY_LIMITS = "1.0,.75,1.5,1.5,1.5,.5,.5,.5,.5,.5,.75,1.25,1.0,1.25"
MAX_WALL_SECONDS = 43_200


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_directory(path: Path) -> str:
    digest = hashlib.sha256()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(str(child.relative_to(path)).encode())
        digest.update(b"\0")
        with child.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    return digest.hexdigest()


def tree_error(left: Any, right: Any) -> tuple[bool, float]:
    if jax.tree_util.tree_structure(left) != jax.tree_util.tree_structure(right):
        return False, float("inf")
    errors = [
        float(np.max(np.abs(np.asarray(a) - np.asarray(b))))
        for a, b in zip(
            jax.tree_util.tree_leaves(left),
            jax.tree_util.tree_leaves(right),
            strict=True,
        )
    ]
    return True, max(errors, default=0.0)


def tree_finite(value: Any) -> bool:
    return all(
        bool(np.all(np.isfinite(np.asarray(leaf))))
        for leaf in jax.tree_util.tree_leaves(value)
    )


def validate_inputs(playground: Path) -> dict[str, Any]:
    launch = json.loads(LAUNCH_CONTRACT.read_text())
    prereg = json.loads(PREREG.read_text())
    recurrent = json.loads(RECURRENT_CONTRACT.read_text())
    curriculum = json.loads(CURRICULUM_CONTRACT.read_text())
    manifest_path = playground / "WINNER_V3_COMPOSED_SOURCE_MANIFEST.json"
    current_hashes = {
        "driver": sha256(Path(__file__).resolve()),
        "preregistration": sha256(PREREG),
        "recurrent_cpu_contract": sha256(RECURRENT_CONTRACT),
        "curriculum_cpu_contract": sha256(CURRICULUM_CONTRACT),
        "source_archive": sha256(ARCHIVE),
        "reference_features": sha256(REFERENCE),
        "composed_manifest": sha256(manifest_path),
    }
    checks = {
        "launch_contract_passed": launch.get("status")
        == "PASS_WINNER_V3_CPU_CURRICULUM_LAUNCH_CONTRACT",
        "launch_hashes_exact": launch.get("input_hashes") == current_hashes,
        "preregistration_exact": prereg.get("training", {}).get("stages")
        == [
            {
                "id": row["id"],
                "steps": row["steps"],
                "deviation_scale": row["deviation_scale"],
                **(
                    {"persistent_exports_relative_steps": [1_003_520, 2_007_040]}
                    if row["id"] == "DOMAIN_100_PERCENT"
                    else {}
                ),
            }
            for row in STAGES
        ],
        "recurrent_contract_passed": recurrent.get("status")
        == "PASS_WINNER_V3_RECURRENT_ADAPTER_CPU_CONTRACT",
        "curriculum_contract_passed": curriculum.get("status")
        == "PASS_WINNER_V3_VARIABLE_CONFIGURATION_CURRICULUM_CONTRACT",
        "curriculum_contract_zero_outcome": curriculum.get(
            "formal_training_steps_executed"
        )
        == 0
        and curriculum.get("formal_behavior_cells_executed") == 0,
        "composed_manifest_matches_formal_contract": sha256(manifest_path)
        == curriculum.get("winner_v3_composed_manifest_sha256"),
        "cpu_only": bool(jax.devices())
        and all(device.platform == "cpu" for device in jax.devices()),
        "single_jax_process": jax.process_count() == 1,
        "frozen_stage_steps": [row["steps"] for row in STAGES]
        == [245_760, 245_760, 2_007_040],
        "frozen_stage_scales": [row["deviation_scale"] for row in STAGES]
        == [0.25, 0.5, 1.0],
        "persistent_exports_exact": STAGES[-1]["expected_steps"]
        == [0, 1_003_520, 2_007_040],
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise ValueError(f"winner-v3 launch input contract failed: {failed}")
    return {
        "checks": checks,
        "input_hashes": current_hashes,
        "devices": [str(device) for device in jax.devices()],
    }


def runner_args(output: Path, restore: Path, stage: dict[str, Any]):
    import argparse as argparse_module

    return argparse_module.Namespace(
        output_dir=str(output),
        num_timesteps=stage["steps"],
        ppo_seed=100,
        ppo_num_envs=256,
        ppo_num_evals=stage["num_evals"],
        ppo_episode_length=600,
        ppo_unroll_length=20,
        ppo_batch_size=256,
        ppo_num_minibatches=4,
        ppo_num_updates_per_batch=4,
        ppo_learning_rate=0.0003,
        ppo_discounting=0.97,
        ppo_entropy_cost=0.005,
        policy_architecture="reference_residual_recurrent_adapter",
        recurrent_hidden_size=64,
        imitation_scale=1.0,
        reference_feature_table_path=str(REFERENCE),
        ground_up_command_curriculum=False,
        nominal_reference_bootstrap=True,
        nominal_reference_command_x=0.074,
        ground_up_torso_com_randomization=False,
        ground_up_torso_com_x_min_m=-0.05,
        ground_up_torso_com_x_max_m=0.05,
        ground_up_torso_com_distribution="uniform",
        ground_up_hard_vector_command_support=True,
        ground_up_command_support_min_x=0.074,
        ground_up_command_support_max_x=0.080,
        ground_up_action_velocity_limits_rad_s=VELOCITY_LIMITS,
        ground_up_measured_actuator_bridge=True,
        ground_up_applied_target_observation=True,
        ground_up_tracking_tail_exceedance_scale=-6572.254964031055,
        ground_up_tracking_tail_threshold_rad=0.20,
        ground_up_actuator_bridge_delay_ticks=(
            "3,3,3,3,3,3,2,3,3,3,2,3,2,3"
        ),
        ground_up_actuator_bridge_tau_s=(
            ".015,.015,.005,.010,.010,.120,.120,.120,.120,.020,.035,.010,.030,.005"
        ),
        reference_start_phase=0,
        ground_up_signed_progress_objective=True,
        winner_v3_variable_configuration=True,
        winner_v3_deviation_scale=stage["deviation_scale"],
        critic_observation="privileged_state",
        env="joystick",
        task="flat_terrain_backlash",
        restore_checkpoint_path=str(restore),
    )


def step_from_name(path: Path) -> int:
    return int(path.stem.rsplit("_", 1)[1])


def inspect_onnx(path: Path) -> dict[str, Any]:
    model = onnx.load(path)
    inputs = {
        item.name: [dim.dim_value for dim in item.type.tensor_type.shape.dim]
        for item in model.graph.input
    }
    outputs = {
        item.name: [dim.dim_value for dim in item.type.tensor_type.shape.dim]
        for item in model.graph.output
    }
    initializers_finite = all(
        np.all(np.isfinite(onnx.numpy_helper.to_array(item)))
        for item in model.graph.initializer
    )
    return {
        "path": str(path),
        "sha256": sha256(path),
        "inputs": inputs,
        "outputs": outputs,
        "abi_exact": inputs
        == {"obs": [1, 115], "previous_action": [1, 14], "h_in": [1, 64]}
        and outputs
        == {
            "continuous_actions": [1, 14],
            "previous_action_out": [1, 14],
            "h_out": [1, 64],
        },
        "initializers_finite": bool(initializers_finite),
    }


def inspect_stage(
    stage: dict[str, Any], output: Path, checkpointer: ocp.PyTreeCheckpointer
) -> dict[str, Any]:
    checkpoints = sorted(
        (path for path in output.iterdir() if path.is_dir()), key=step_from_name
    )
    onnx_paths = sorted(output.glob("*.onnx"), key=step_from_name)
    checkpoint_steps = [step_from_name(path) for path in checkpoints]
    onnx_steps = [step_from_name(path) for path in onnx_paths]
    if checkpoint_steps != stage["expected_steps"] or onnx_steps != stage["expected_steps"]:
        raise ValueError(
            f"unexpected {stage['id']} exports: {checkpoint_steps}, {onnx_steps}"
        )
    checkpoint_rows = []
    for path in checkpoints:
        value = checkpointer.restore(str(path))
        if not tree_finite(value):
            raise FloatingPointError(f"nonfinite checkpoint: {path}")
        checkpoint_rows.append(
            {
                "step": step_from_name(path),
                "path": str(path),
                "directory_sha256": sha256_directory(path),
                "all_leaves_finite": True,
            }
        )
    onnx_rows = []
    for path in onnx_paths:
        row = inspect_onnx(path)
        if not row["abi_exact"] or not row["initializers_finite"]:
            raise ValueError(f"invalid ONNX artifact: {row}")
        row["step"] = step_from_name(path)
        onnx_rows.append(row)
    return {
        "id": stage["id"],
        "deviation_scale": stage["deviation_scale"],
        "requested_steps": stage["steps"],
        "checkpoint_steps": checkpoint_steps,
        "onnx_steps": onnx_steps,
        "checkpoints": checkpoint_rows,
        "onnx": onnx_rows,
        "initial_checkpoint": checkpoints[0],
        "final_checkpoint": checkpoints[-1],
    }


class Tee:
    def __init__(self, stream, file_stream):
        self.stream = stream
        self.file_stream = file_stream

    def write(self, value):
        self.stream.write(value)
        self.file_stream.write(value)
        self.file_stream.flush()
        return len(value)

    def flush(self):
        self.stream.flush()
        self.file_stream.flush()


def write_markdown(payload: dict[str, Any]) -> None:
    stages = payload.get("stages", [])
    stage_lines = "\n".join(
        f"- {row['id']}: scale `{row['deviation_scale']}`, exports "
        f"`{row['checkpoint_steps']}`, wall `{row['wall_seconds']:.3f}` s"
        for row in stages
    )
    OUTPUT_MD.write_text(
        f"""# Winner-v3 Recurrent-Adapter CPU Curriculum — 2026-07-19

Status: `{payload['status']}`

- process id: `{payload.get('process_id')}`
- JAX devices: `{payload.get('devices')}`
- total wall seconds: `{payload.get('wall_seconds')}`
- formal behavior cells executed: `0`
- training reward selection weight: `NONE`
{stage_lines}

This artifact reports only whether the single preregistered CPU curriculum and
its checkpoint/export contract completed. It makes no behavior, robustness,
supported-configuration, runtime, deployment, Gate 5, or robot-clearance claim.
No hosted allocation, GPU/iGPU, RDK-X5, robot, serial, torque or motion was used.
"""
    )


def make_artifact(work: Path) -> dict[str, Any]:
    temporary = OUTPUT_ARCHIVE.with_suffix(OUTPUT_ARCHIVE.suffix + ".tmp")
    if temporary.exists() or OUTPUT_ARCHIVE.exists():
        raise FileExistsError("refusing to overwrite winner-v3 training archive")
    with tarfile.open(temporary, "w:gz") as archive:
        archive.add(work, arcname="winner_v3_recurrent_adapter_training")
    temporary.replace(OUTPUT_ARCHIVE)
    return {"path": str(OUTPUT_ARCHIVE), "sha256": sha256(OUTPUT_ARCHIVE), "bytes": OUTPUT_ARCHIVE.stat().st_size}


def run(playground: Path, work: Path) -> int:
    if work.exists():
        raise FileExistsError(f"single-run no-retry work root exists: {work}")
    for output in (OUTPUT_JSON, OUTPUT_MD, OUTPUT_ARCHIVE):
        if output.exists():
            raise FileExistsError(f"single-run output already exists: {output}")
    validation = validate_inputs(playground)
    work.mkdir(parents=True)
    started = time.monotonic()
    process_id = os.getpid()
    payload: dict[str, Any] = {
        "schema_version": "winner_v3.recurrent_adapter_cpu_curriculum.v1",
        "status": "RUNNING_WINNER_V3_RECURRENT_ADAPTER_CPU_CURRICULUM",
        "process_id": process_id,
        "devices": validation["devices"],
        "input_hashes": validation["input_hashes"],
        "checks": validation["checks"],
        "stages": [],
        "formal_behavior_cells_executed": 0,
        "training_reward_selection_weight": "NONE",
        "max_wall_seconds": MAX_WALL_SECONDS,
    }
    (work / "run_state.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    sys.path.insert(0, str(ROOT / "tools"))
    import check_winner_v3_recurrent_adapter_cpu_contract as recurrent_helper

    sys.path.insert(0, str(playground))
    os.chdir(playground)
    from playground.common.reference_residual_recurrent_adapter_ppo_networks import (
        make_reference_residual_recurrent_adapter_ppo_networks,
    )
    from playground.open_duck_mini_v2.runner import OpenDuckMiniV2Runner

    checkpointer = ocp.PyTreeCheckpointer()
    try:
        source_root = work / "protected_source"
        source_root.mkdir()
        with tarfile.open(ARCHIVE, "r:gz") as archive:
            members = [
                member
                for member in archive
                if member.name == str(SOURCE_MEMBER)
                or member.name.startswith(str(SOURCE_MEMBER) + "/")
            ]
            archive.extractall(source_root, members=members, filter="data")
        source_path = source_root / SOURCE_MEMBER
        if sha256_directory(source_path) != recurrent_helper.SOURCE_DIRECTORY_SHA256:
            raise ValueError("protected source directory hash mismatch")
        if sha256_directory(recurrent_helper.CPU_TEMPLATE) != recurrent_helper.CPU_TEMPLATE_SHA256:
            raise ValueError("CPU restore template hash mismatch")
        template = checkpointer.restore(str(recurrent_helper.CPU_TEMPLATE))
        restore_args = orbax_utils.restore_args_from_target(template)
        source = checkpointer.restore(
            str(source_path), item=template, restore_args=restore_args
        )
        networks = make_reference_residual_recurrent_adapter_ppo_networks(
            {"state": (115,), "privileged_state": (226,), "policy_hidden": (64,)},
            14,
            recurrent_hidden_size=64,
        )
        expanded = recurrent_helper.expand_checkpoint(source, networks)
        expanded_path = work / "expanded_checkpoint"
        checkpointer.save(
            str(expanded_path),
            expanded,
            save_args=orbax_utils.save_args_from_target(expanded),
        )
        restored_expanded = checkpointer.restore(str(expanded_path))
        structure, error = tree_error(expanded, restored_expanded)
        if not structure or error != 0.0 or not tree_finite(restored_expanded):
            raise ValueError(f"expanded checkpoint round trip failed: {structure}, {error}")
        payload["expanded_checkpoint"] = {
            "directory_sha256": sha256_directory(expanded_path),
            "save_restore_max_abs_error": error,
            "all_leaves_finite": True,
        }

        restore = expanded_path
        prior_final = None
        full_log = work / "training.log"
        with full_log.open("w") as log_stream, contextlib.redirect_stdout(
            Tee(sys.__stdout__, log_stream)
        ), contextlib.redirect_stderr(Tee(sys.__stderr__, log_stream)):
            for stage_index, stage in enumerate(STAGES, start=1):
                stage_output = work / f"stage{stage_index}_{stage['id'].lower()}"
                stage_output.mkdir()
                stage_started = time.monotonic()
                print(
                    f"WINNER_V3_STAGE_START={stage['id']},scale={stage['deviation_scale']},"
                    f"steps={stage['steps']},pid={os.getpid()}",
                    flush=True,
                )
                runner = OpenDuckMiniV2Runner(runner_args(stage_output, restore, stage))
                if os.getpid() != process_id:
                    raise RuntimeError("training process identity changed")
                metrics_rows: list[dict[str, Any]] = []
                original_progress = runner.progress_callback
                original_save = runner.policy_params_fn

                def progress(step, metrics, *, _stage=stage):
                    if time.monotonic() - started > MAX_WALL_SECONDS:
                        raise TimeoutError("frozen CPU curriculum wall ceiling exceeded")
                    row = {"step": int(step), "metrics": {}}
                    for name, value in metrics.items():
                        array = np.asarray(value)
                        if not np.all(np.isfinite(array)):
                            raise FloatingPointError(
                                f"nonfinite metric {_stage['id']} {step} {name}"
                            )
                        row["metrics"][name] = float(np.mean(array))
                    metrics_rows.append(row)
                    original_progress(step, metrics)

                def save(step, make_policy, params, *, _stage=stage):
                    if not tree_finite(params):
                        raise FloatingPointError(
                            f"nonfinite params {_stage['id']} {step}"
                        )
                    original_save(step, make_policy, params)

                runner.progress_callback = progress
                runner.policy_params_fn = save
                try:
                    runner.train()
                finally:
                    runner.writer.close()
                row = inspect_stage(stage, stage_output, checkpointer)
                row["wall_seconds"] = time.monotonic() - stage_started
                row["metrics"] = metrics_rows
                if prior_final is not None:
                    current_initial = checkpointer.restore(str(row["initial_checkpoint"]))
                    continuity_structure, continuity_error = tree_error(
                        prior_final, current_initial
                    )
                    row["restore_continuity"] = {
                        "tree_structure_exact": continuity_structure,
                        "max_abs_error": continuity_error,
                    }
                    if not continuity_structure or continuity_error != 0.0:
                        raise ValueError(
                            f"stage restore continuity failed: {stage['id']}"
                        )
                prior_final = checkpointer.restore(str(row["final_checkpoint"]))
                restore = row["final_checkpoint"]
                row["initial_checkpoint"] = str(row["initial_checkpoint"])
                row["final_checkpoint"] = str(row["final_checkpoint"])
                payload["stages"].append(row)
                payload["status"] = f"COMPLETED_{stage['id']}"
                payload["wall_seconds"] = time.monotonic() - started
                (work / "run_state.json").write_text(
                    json.dumps(payload, indent=2, sort_keys=True) + "\n"
                )
                print(
                    f"WINNER_V3_STAGE_COMPLETE={stage['id']},"
                    f"wall={row['wall_seconds']:.3f},pid={os.getpid()}",
                    flush=True,
                )
                del runner
                gc.collect()

        payload["checks"].update(
            {
                "one_os_process_for_all_stages": os.getpid() == process_id,
                "all_stage_exports_exact": all(
                    row["checkpoint_steps"] == list(stage["expected_steps"])
                    and row["onnx_steps"] == list(stage["expected_steps"])
                    for row, stage in zip(payload["stages"], STAGES, strict=True)
                ),
                "all_stage_artifacts_finite": all(
                    all(item["all_leaves_finite"] for item in row["checkpoints"])
                    and all(
                        item["initializers_finite"] and item["abi_exact"]
                        for item in row["onnx"]
                    )
                    for row in payload["stages"]
                ),
                "stage_restore_continuity_exact": all(
                    row.get("restore_continuity", {}).get("max_abs_error") == 0.0
                    for row in payload["stages"][1:]
                ),
                "full_domain_persistent_exports_exact": payload["stages"][-1][
                    "checkpoint_steps"
                ]
                == [0, 1_003_520, 2_007_040],
                "within_wall_ceiling": time.monotonic() - started <= MAX_WALL_SECONDS,
                "formal_behavior_cells_zero": True,
            }
        )
        failed = sorted(name for name, passed in payload["checks"].items() if not passed)
        if failed:
            raise ValueError(f"training artifact contract failed: {failed}")
        payload["status"] = "PASS_WINNER_V3_RECURRENT_ADAPTER_TRAINING_ARTIFACT"
        payload["failed_checks"] = []
        payload["wall_seconds"] = time.monotonic() - started
        payload["training_log"] = {
            "path": str(full_log),
            "sha256": sha256(full_log),
        }
        (work / "run_state.json").write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n"
        )
        payload["artifact"] = make_artifact(work)
        OUTPUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        write_markdown(payload)
        print(payload["status"], flush=True)
        return 0
    except BaseException as exc:
        payload["status"] = "HOLD_WINNER_V3_RECURRENT_ADAPTER_TRAINING"
        payload["error"] = f"{type(exc).__name__}: {exc}"
        payload["traceback"] = traceback.format_exc()
        payload["wall_seconds"] = time.monotonic() - started
        (work / "run_state.json").write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n"
        )
        OUTPUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        write_markdown(payload)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--work-root", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    playground = args.playground_root.resolve()
    validation = validate_inputs(playground)
    if args.validate_only:
        print(
            json.dumps(
                {
                    "status": "PASS_WINNER_V3_CPU_CURRICULUM_DRIVER_VALIDATION",
                    **validation,
                    "formal_training_steps_executed": 0,
                    "formal_behavior_cells_executed": 0,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    if args.work_root is None:
        raise ValueError("formal run requires --work-root")
    return run(playground, args.work_root.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
