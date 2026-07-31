#!/usr/bin/env python3
"""Run T228's one frozen command-atom persistence continuation."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import tarfile
from typing import Any

import jax

sys.path.insert(0, str(Path(__file__).resolve().parent))

import colab_t216_axis_complete_tilt_continuation as base
from colab_t32_action_margin_trainthrough_continuation import (
    canonical_sha256,
    source_inventory,
)
from colab_winner_v114_linear_torque_continuation import (
    directory_sha256,
    sha256,
)


PREREGISTRATION_NAME = "t228_command_atom_hosted_preregistration.json"
CPU_RESULT_NAME = "t227d_recovered_cpu_validation_result.json"
SOURCE_CHECKPOINT_NAME = "source_checkpoint"
STEP_ZERO_NAME = "expected_step_zero_raw.onnx"
REFERENCE_NAME = base.REFERENCE_NAME
GATE_NAME = base.GATE_NAME
EXPECTED_READBACK = (
    "T227_COMMAND_ATOM_BANK=configuration_strata=8,command_strata=4,"
    "command_groups=broad|0.074|0.077|0.080,"
    "cartesian_repetitions=8,reward=unchanged,cost=unchanged,"
    "policy_abi=unchanged,deployment_graph=unchanged"
)
_BASE_RUNNER_COMMAND = base.runner_command
_BASE_RUN = base.run


def runner_command(
    playground: Path,
    output: Path,
    source: Path,
    reference: Path,
) -> list[str]:
    """Add only T227's deterministic command atoms to T216."""
    command = _BASE_RUNNER_COMMAND(playground, output, source, reference)
    anchor = command.index("--winner_t19_support_trainthrough") + 1
    command[anchor:anchor] = ["--winner_t227_command_atom_bank"]
    return command


def validate_inputs(bundle: Path) -> dict[str, Any]:
    preregistration = bundle / PREREGISTRATION_NAME
    cpu_result_path = bundle / CPU_RESULT_NAME
    playground = bundle / "playground"
    assets = bundle / "assets"
    source = assets / SOURCE_CHECKPOINT_NAME
    reference = assets / REFERENCE_NAME
    step_zero = assets / STEP_ZERO_NAME
    gate = assets / GATE_NAME
    prereg = json.loads(preregistration.read_text(encoding="utf-8"))
    cpu = json.loads(cpu_result_path.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg.get("status")
        != "PREREGISTERED_T228_COMMAND_ATOM_HOSTED_CONTINUATION"
        or prereg.get("failed_checks")
        or canonical_sha256(basis)
        != prereg.get("preregistered_contract_sha256")
        or cpu.get("status")
        != "PASS_T227D_RECOVERED_CPU_VALIDATION"
        or cpu.get("failed_checks")
        or cpu.get("decision")
        != "EARN_T228_COMMAND_ATOM_HOSTED_CONTINUATION_PREREGISTRATION_ONLY"
    ):
        raise ValueError("T228 prerequisite status or identity changed")
    inventory = source_inventory(playground)
    observed = {
        "driver": sha256(Path(__file__).resolve()),
        "base_t216_driver": sha256(Path(base.__file__).resolve()),
        "cpu_result": sha256(cpu_result_path),
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
        raise ValueError("T228 frozen inputs changed")
    devices = [str(device) for device in jax.devices()]
    if (
        not devices
        or not all(device.platform == "gpu" for device in jax.devices())
        or jax.process_count() != 1
    ):
        raise RuntimeError(f"T228 requires one GPU process: {devices}")
    return {
        "input_hashes": observed,
        "devices": devices,
        "process_count": jax.process_count(),
        "preregistration_sha256": sha256(preregistration),
    }


def _repack(work: Path, destination: Path) -> dict[str, Any]:
    if destination.exists():
        destination.unlink()
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    with tarfile.open(temporary, "w:gz") as archive:
        archive.add(work, arcname="t228_command_atom_continuation")
    temporary.replace(destination)
    return {
        "path": str(destination),
        "sha256": sha256(destination),
        "bytes": destination.stat().st_size,
    }


def _rebrand(
    work: Path,
    output_json: Path,
    output_archive: Path,
) -> int:
    payload = json.loads(output_json.read_text(encoding="utf-8"))
    log_text = (work / "training.log").read_text(encoding="utf-8")
    command = payload["command"]
    checks = dict(payload["checks"])
    checks.update(
        {
            "t227_command_atom_flag_exact": (
                command.count("--winner_t227_command_atom_bank") == 1
            ),
            "t227_hosted_runner_readback_exact": (
                EXPECTED_READBACK in log_text
            ),
            "source_is_t216_final_policy": (
                payload["validation"]["input_hashes"]["source_checkpoint"]
                == (
                    "d0e969cab98cbb8cf779792935c58058019c07d41a5e7ae008"
                    "7136830ef21c0c"
                )
            ),
            "command_atom_population_exact": (
                command[command.index("--ppo_num_envs") + 1] == "256"
            ),
        }
    )
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload.update(
        {
            "schema_version": (
                "open_duck.t228_command_atom_hosted_result.v1"
            ),
            "status": (
                "PASS_T228_TRAINING_ARTIFACT_PENDING_CPU_VALIDATION"
                if not failed
                else "HOLD_T228_COMMAND_ATOM_CONTINUATION"
            ),
            "checks": checks,
            "failed_checks": failed,
            "mechanism": {
                **payload["mechanism"],
                "source": "exact_T216_final_checkpoint_2007040",
                "configuration_strata": 8,
                "command_strata": 4,
                "cartesian_strata": 32,
                "environments_per_cartesian_stratum": 8,
                "command_groups": [
                    "broad_continuous_[.074,.080)",
                    "exact_.074",
                    "exact_.077",
                    "exact_.080",
                ],
                "reward_change": False,
                "cost_change": False,
                "actor_update_mask_change": False,
                "policy_abi_change": False,
                "deployment_graph_change": False,
            },
            "authority": {
                "behavior_evaluation_authorized": False,
                "checkpoint_selection_authorized": False,
                "gate5_authorized": False,
                "robot_clearance": False,
                "rdkx5_or_robot": False,
            },
        }
    )
    run_state = work / "run_state.json"
    run_state.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    if failed:
        output_json.write_text(
            json.dumps(payload, allow_nan=False, indent=2, sort_keys=True)
            + "\n",
            encoding="utf-8",
        )
        raise ValueError(f"T228 artifact checks failed: {failed}")
    payload["artifact"] = _repack(work, output_archive)
    output_json.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    print(payload["status"], flush=True)
    print(f"sha256={sha256(output_json)}", flush=True)
    return 0


def run(
    bundle: Path,
    work: Path,
    output_json: Path,
    output_archive: Path,
) -> int:
    original_validate = base.validate_inputs
    original_runner = base.runner_command
    try:
        base.validate_inputs = validate_inputs
        base.runner_command = runner_command
        _BASE_RUN(bundle, work, output_json, output_archive)
    finally:
        base.validate_inputs = original_validate
        base.runner_command = original_runner
    return _rebrand(work, output_json, output_archive)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle-root", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-archive", type=Path, required=True)
    parser.add_argument("--hosted-gpu-authorized", action="store_true")
    args = parser.parse_args()
    if not args.hosted_gpu_authorized:
        raise PermissionError("T228 requires hosted GPU authorization")
    return run(
        args.bundle_root.resolve(),
        args.work_root.resolve(),
        args.output_json.resolve(),
        args.output_archive.resolve(),
    )


if __name__ == "__main__":
    raise SystemExit(main())
