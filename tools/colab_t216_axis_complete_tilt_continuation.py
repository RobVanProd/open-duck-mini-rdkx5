#!/usr/bin/env python3
"""Run T216's one frozen axis-complete tilt continuation."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import time
import traceback
from typing import Any

import jax

sys.path.insert(0, str(Path(__file__).resolve().parent))

import colab_t170_eight_stratum_head_continuation as base
from colab_t32_action_margin_trainthrough_continuation import (
    canonical_sha256,
    source_inventory,
)
from colab_t78_endpoint_joint_adapter_continuation import (
    describe_onnx,
    step_from_path,
)
from colab_winner_v114_linear_torque_continuation import (
    directory_sha256,
    sha256,
)


PREREGISTRATION_NAME = "t216_axis_complete_tilt_hosted_preregistration.json"
CPU_RESULT_NAME = "t215b_axis_complete_tilt_cpu_result.json"
T204_VALIDATION_NAME = "t204_t203_recovered_training_validation.json"
T214B_SELECTION_NAME = "t214b_axis_complete_tilt_source_transfer_result.json"
GATE_NAME = base.GATE_NAME
REFERENCE_NAME = base.REFERENCE_NAME
STEP_ZERO_NAME = base.STEP_ZERO_NAME
SOURCE_CHECKPOINT_NAME = base.SOURCE_CHECKPOINT_NAME
EXPECTED_STEPS = [0, 1_003_520, 2_007_040]
MAX_WALL_SECONDS = 21_600
_BASE_RUNNER_COMMAND = base.runner_command


def runner_command(
    playground: Path,
    output: Path,
    source: Path,
    reference: Path,
) -> list[str]:
    """Add only T215B's frozen axis-complete tilt cost to T170."""
    command = _BASE_RUNNER_COMMAND(playground, output, source, reference)
    anchor = command.index("--winner_t98_hidden_expert_continuation") + 1
    command[anchor:anchor] = [
        "--winner_v127_constrained_cost",
        "--winner_t215b_axis_complete_tilt_cost",
    ]
    for flag in (
        "--ground_up_peak_torque_exceedance_scale",
        "--ground_up_linear_peak_torque_exceedance_scale",
    ):
        command[command.index(flag) + 1] = "0"
    return command


def validate_inputs(bundle: Path) -> dict[str, Any]:
    preregistration = bundle / PREREGISTRATION_NAME
    cpu_result_path = bundle / CPU_RESULT_NAME
    t204_path = bundle / T204_VALIDATION_NAME
    t214b_path = bundle / T214B_SELECTION_NAME
    playground = bundle / "playground"
    assets = bundle / "assets"
    source = assets / SOURCE_CHECKPOINT_NAME
    reference = assets / REFERENCE_NAME
    step_zero = assets / STEP_ZERO_NAME
    gate = assets / GATE_NAME
    prereg = json.loads(preregistration.read_text(encoding="utf-8"))
    cpu = json.loads(cpu_result_path.read_text(encoding="utf-8"))
    t204 = json.loads(t204_path.read_text(encoding="utf-8"))
    t214b = json.loads(t214b_path.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg.get("status")
        != "PREREGISTERED_T216_AXIS_COMPLETE_TILT_HOSTED_CONTINUATION"
        or prereg.get("failed_checks")
        or canonical_sha256(basis)
        != prereg.get("preregistered_contract_sha256")
        or cpu.get("status")
        != "PASS_T215B_AXIS_COMPLETE_TILT_CPU_CONTRACT"
        or cpu.get("failed_checks")
        or cpu.get("decision")
        != "EARN_T216_AXIS_COMPLETE_TILT_HOSTED_PREREGISTRATION_ONLY"
        or t204.get("status")
        != "PASS_T204_T203_RECOVERED_TRAINING_VALIDATION"
        or t214b.get("status")
        != "PASS_T214B_AXIS_COMPLETE_TILT_SOURCE_TRANSFER"
        or t214b.get("failed_checks")
        or t214b.get("classification")
        != "AXIS_COMPLETE_TILT_BOX_UNIFIES_ROLL_AND_PITCH_FALLS"
        or t214b.get("decision")
        != (
            "EARN_T215B_AXIS_COMPLETE_TILT_DUAL_CPU_CONTRACT_"
            "PREREGISTRATION_ONLY"
        )
    ):
        raise ValueError("T216 prerequisite status or identity changed")
    inventory = source_inventory(playground)
    observed = {
        "driver": sha256(Path(__file__).resolve()),
        "base_t170_driver": sha256(Path(base.__file__).resolve()),
        "base_t78_driver": sha256(Path(base.base.__file__).resolve()),
        "t32_driver": sha256(
            Path(
                sys.modules[
                    "colab_t32_action_margin_trainthrough_continuation"
                ].__file__
            ).resolve()
        ),
        "helper": sha256(
            Path(
                sys.modules[
                    "colab_winner_v114_linear_torque_continuation"
                ].__file__
            ).resolve()
        ),
        "cpu_result": sha256(cpu_result_path),
        "t204_validation": sha256(t204_path),
        "t214b_selection": sha256(t214b_path),
        "source_checkpoint": directory_sha256(source),
        "reference_features": sha256(reference),
        "expected_step_zero_raw": sha256(step_zero),
        "hidden_gate_static_asset": sha256(gate),
        "playground_inventory": canonical_sha256(inventory),
    }
    if (
        observed != prereg["input_hashes"]
        or inventory != prereg["playground"]["file_inventory"]
    ):
        raise ValueError("T216 frozen inputs changed")
    devices = [str(device) for device in jax.devices()]
    if (
        not devices
        or not all(device.platform == "gpu" for device in jax.devices())
        or jax.process_count() != 1
    ):
        raise RuntimeError(f"T216 requires one GPU process: {devices}")
    return {
        "input_hashes": observed,
        "devices": devices,
        "process_count": jax.process_count(),
        "preregistration_sha256": sha256(preregistration),
    }


def make_artifact(work: Path, destination: Path) -> dict[str, Any]:
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    with tarfile.open(temporary, "w:gz") as archive:
        archive.add(work, arcname="t216_axis_complete_tilt_continuation")
    temporary.replace(destination)
    return {
        "path": str(destination),
        "sha256": sha256(destination),
        "bytes": destination.stat().st_size,
    }


def cost_step(path: Path) -> int:
    return int(
        path.name.split("_v127_cost_value", 1)[0].rsplit("_", 1)[1]
    )


def run(
    bundle: Path,
    work: Path,
    output_json: Path,
    output_archive: Path,
) -> int:
    for path in (work, output_json, output_archive):
        if path.exists():
            raise FileExistsError(f"T216 no-retry path exists: {path}")
    validation = validate_inputs(bundle)
    work.mkdir(parents=True)
    output = work / "training"
    output.mkdir()
    log = work / "training.log"
    playground = bundle / "playground"
    source = bundle / "assets" / SOURCE_CHECKPOINT_NAME
    reference = bundle / "assets" / REFERENCE_NAME
    command = runner_command(playground, output, source, reference)
    started = time.monotonic()
    payload: dict[str, Any] = {
        "schema_version": "open_duck.t216_axis_complete_tilt_hosted_result.v1",
        "status": "RUNNING_T216_AXIS_COMPLETE_TILT_HOSTED_CONTINUATION",
        "validation": validation,
        "command": command,
        "formal_behavior_cells_executed": 0,
        "authority": {
            "behavior_evaluation_authorized": False,
            "checkpoint_selection_authorized": False,
            "gate5_authorized": False,
            "robot_clearance": False,
            "rdkx5_or_robot": False,
        },
    }
    run_state = work / "run_state.json"
    run_state.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    try:
        environment = dict(os.environ)
        environment["PYTHONPATH"] = str(playground)
        with log.open("w", encoding="utf-8") as stream:
            completed = subprocess.run(
                command,
                cwd=playground,
                env=environment,
                text=True,
                stdout=stream,
                stderr=subprocess.STDOUT,
                timeout=MAX_WALL_SECONDS,
                check=False,
            )
        if completed.returncode != 0:
            raise RuntimeError(f"T216 runner returned {completed.returncode}")
        elapsed = time.monotonic() - started
        policy_checkpoints = sorted(
            (
                path
                for path in output.iterdir()
                if path.is_dir()
                and "_v127_cost_value" not in path.name
            ),
            key=step_from_path,
        )
        cost_checkpoints = sorted(
            output.glob("*_v127_cost_value"), key=cost_step
        )
        graphs = sorted(output.glob("*.onnx"), key=step_from_path)
        aux_paths = sorted(output.glob("*_v127_aux.json"))
        policy_steps = [step_from_path(path) for path in policy_checkpoints]
        cost_steps = [cost_step(path) for path in cost_checkpoints]
        onnx_steps = [step_from_path(path) for path in graphs]
        aux = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in aux_paths
        ]
        aux.sort(key=lambda item: int(item["step"]))
        aux_steps = [int(item["step"]) for item in aux]
        graph_rows = [describe_onnx(path) for path in graphs]
        log_text = log.read_text(encoding="utf-8")
        checks = {
            "gpu_only": all(
                device.platform == "gpu" for device in jax.devices()
            ),
            "single_jax_process": jax.process_count() == 1,
            "exact_policy_cost_aux_and_onnx_exports": (
                policy_steps
                == cost_steps
                == aux_steps
                == onnx_steps
                == EXPECTED_STEPS
            ),
            "all_checkpoint_directories_nonempty": all(
                any(path.rglob("*"))
                for path in (*policy_checkpoints, *cost_checkpoints)
            ),
            "all_raw_onnx_contracts_pass": all(
                row["abi_exact"]
                and row["initializers_finite"]
                and row["cpu_256_tick_chain_finite"]
                and row["providers"] == ["CPUExecutionProvider"]
                for row in graph_rows
            ),
            "initial_dual_state_zero": (
                aux[0]["lambda"] == 0.0
                and aux[0]["eta"] == 0.0
                and aux[0]["initial_cost"] == 0.0
                and aux[0]["initialized"] is False
            ),
            "all_dual_state_finite": all(
                all(
                    isinstance(item[name], (int, float))
                    and float("-inf") < float(item[name]) < float("inf")
                    for name in ("lambda", "eta", "initial_cost")
                )
                for item in aux
            ),
            "t215b_and_t98_readbacks_exact": (
                "T215B_AXIS_COMPLETE_TILT_COST=" in log_text
                and "T98_HIDDEN_EXPERT_CONTINUATION=" in log_text
            ),
            "fixed_t202_reward_flag_absent": (
                "--winner_t202_predicted_roll_risk" not in command
            ),
            "roll_only_t209_flag_absent": (
                "--winner_t209_dual_roll_cost" not in command
            ),
            "legacy_constraint_reward_penalties_zero": all(
                command[command.index(flag) + 1] == "0"
                for flag in (
                    "--ground_up_peak_torque_exceedance_scale",
                    "--ground_up_linear_peak_torque_exceedance_scale",
                )
            ),
            "within_wall_ceiling": elapsed <= MAX_WALL_SECONDS,
            "formal_behavior_cells_zero": True,
            "hosted_axis_complete_cost_exercised": (
                len(aux) == 3
                and all(
                    bool(item["initialized"])
                    and float(item["initial_cost"]) > 0.0
                    and float(item["eta"]) > 0.0
                    and float(item["lambda"]) > 0.0
                    for item in aux[1:]
                )
            ),
            "final_dual_price_not_below_half": (
                len(aux) == 3
                and float(aux[2]["lambda"]) >= float(aux[1]["lambda"])
            ),
        }
        checks = {name: bool(passed) for name, passed in checks.items()}
        failed = sorted(name for name, passed in checks.items() if not passed)
        payload.update(
            {
                "status": (
                    "PASS_T216_TRAINING_ARTIFACT_PENDING_CPU_VALIDATION"
                    if not failed
                    else "HOLD_T216_AXIS_COMPLETE_TILT_CONTINUATION"
                ),
                "checks": checks,
                "failed_checks": failed,
                "wall_seconds": elapsed,
                "policy_checkpoint_steps": policy_steps,
                "cost_checkpoint_steps": cost_steps,
                "onnx_steps": onnx_steps,
                "aux": aux,
                "policy_checkpoints": [
                    {
                        "step": step_from_path(path),
                        "directory_sha256": directory_sha256(path),
                    }
                    for path in policy_checkpoints
                ],
                "cost_checkpoints": [
                    {
                        "step": cost_step(path),
                        "directory_sha256": directory_sha256(path),
                    }
                    for path in cost_checkpoints
                ],
                "onnx": graph_rows,
                "training_log_sha256": sha256(log),
                "cpu_topology_validation_required": True,
                "mechanism": {
                    "source": "exact_T203_half_checkpoint_1003520",
                    "prediction_horizon_s": 0.08,
                    "score": (
                        "max(abs(roll+0.08*roll_rate)/"
                        "0.3541802655745987,"
                        "abs(pitch+0.08*pitch_rate)/"
                        "0.2379576557426921)"
                    ),
                    "passing_envelope_rad": {
                        "roll": 0.3541802655745987,
                        "pitch": 0.2379576557426921,
                    },
                    "cost": "square(max(0,score-1))",
                    "cost_critic": "separate",
                    "dual_eta": "1/(ceil(K/4)*J_C0)",
                    "reward_channel": "unchanged",
                    "body_configuration_strata": 8,
                    "environments_per_stratum": 32,
                    "trainable_actor_group": "negative_adapter_location",
                    "normalizer_frozen": True,
                    "deployment_graph_change": False,
                    "retry": False,
                    "same_run_resume": False,
                },
            }
        )
        run_state.write_text(
            json.dumps(payload, allow_nan=False, indent=2, sort_keys=True)
            + "\n",
            encoding="utf-8",
        )
        if failed:
            raise ValueError(f"T216 artifact checks failed: {failed}")
        payload["artifact"] = make_artifact(work, output_archive)
        output_json.write_text(
            json.dumps(payload, allow_nan=False, indent=2, sort_keys=True)
            + "\n",
            encoding="utf-8",
        )
        print(payload["status"], flush=True)
        print(f"sha256={sha256(output_json)}", flush=True)
        return 0
    except BaseException as exc:
        payload["status"] = "HOLD_T216_AXIS_COMPLETE_TILT_CONTINUATION"
        payload["error"] = f"{type(exc).__name__}: {exc}"
        payload["traceback"] = traceback.format_exc()
        payload["wall_seconds"] = time.monotonic() - started
        run_state.write_text(
            json.dumps(payload, allow_nan=False, indent=2, sort_keys=True)
            + "\n",
            encoding="utf-8",
        )
        output_json.write_text(
            json.dumps(payload, allow_nan=False, indent=2, sort_keys=True)
            + "\n",
            encoding="utf-8",
        )
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle-root", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-archive", type=Path, required=True)
    parser.add_argument("--hosted-gpu-authorized", action="store_true")
    args = parser.parse_args()
    if not args.hosted_gpu_authorized:
        raise PermissionError("T216 requires hosted GPU authorization")
    return run(
        args.bundle_root.resolve(),
        args.work_root.resolve(),
        args.output_json.resolve(),
        args.output_archive.resolve(),
    )


if __name__ == "__main__":
    raise SystemExit(main())
