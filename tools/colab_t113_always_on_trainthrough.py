#!/usr/bin/env python3
"""Run the single frozen T113 always-on expert hosted continuation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import jax

sys.path.insert(0, str(Path(__file__).resolve().parent))

import colab_t78_endpoint_joint_adapter_continuation as base
from colab_t32_action_margin_trainthrough_continuation import (
    canonical_sha256,
    source_inventory,
)
from colab_winner_v114_linear_torque_continuation import (
    directory_sha256,
    sha256,
)


PREREGISTRATION_NAME = (
    "t113_always_on_trainthrough_hosted_preregistration.json"
)
CPU_RESULT_NAME = "t112b_cpu_recovery_result.json"
GATE_NAME = "t98_hidden_gate_asset.json"
REFERENCE_NAME = base.REFERENCE_NAME
STEP_ZERO_NAME = base.STEP_ZERO_NAME
SOURCE_CHECKPOINT_NAME = base.SOURCE_CHECKPOINT_NAME
EXPECTED_STEPS = [0, 1_003_520, 2_007_040]
_BASE_RUNNER_COMMAND = base.runner_command


def runner_command(
    playground: Path,
    output: Path,
    source: Path,
    reference: Path,
) -> list[str]:
    """Use T78's frozen recipe with the always-on expert update path."""
    command = _BASE_RUNNER_COMMAND(playground, output, source, reference)
    old = "--winner_t77_endpoint_joint_adapter_continuation"
    command[command.index(old)] = "--winner_t98_hidden_expert_continuation"
    index = command.index("--winner_t98_hidden_expert_continuation") + 1
    command[index:index] = [
        "--winner_t98_hidden_gate_asset_path",
        str(source.parent / GATE_NAME),
    ]
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
    cpu_result = json.loads(cpu_result_path.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg.get("status")
        != "PREREGISTERED_T113_ALWAYS_ON_TRAINTHROUGH_HOSTED_CONTINUATION"
        or prereg.get("failed_checks") != []
        or canonical_sha256(basis)
        != prereg.get("preregistered_contract_sha256")
        or cpu_result.get("status")
        != "PASS_T112B_READ_ONLY_CPU_RECOVERY"
        or cpu_result.get("failed_checks") != []
        or cpu_result.get("decision")
        != "EARN_T113_ALWAYS_ON_TRAINTHROUGH_HOSTED_PREREGISTRATION_ONLY"
    ):
        raise ValueError("T113 prerequisite status or identity changed")
    inventory = source_inventory(playground)
    observed = {
        "driver": sha256(Path(__file__).resolve()),
        "base_driver": sha256(Path(base.__file__).resolve()),
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
        raise ValueError("T113 frozen inputs changed")
    devices = [str(device) for device in jax.devices()]
    if (
        not devices
        or not all(device.platform == "gpu" for device in jax.devices())
        or jax.process_count() != 1
    ):
        raise RuntimeError(f"T113 requires one GPU process: {devices}")
    return {
        "input_hashes": observed,
        "devices": devices,
        "process_count": jax.process_count(),
        "preregistration_sha256": sha256(preregistration),
    }


def run(
    bundle: Path,
    work: Path,
    output_json: Path,
    output_archive: Path,
) -> int:
    base.runner_command = runner_command
    base.validate_inputs = validate_inputs
    returncode = base.run(bundle, work, output_json, output_archive)
    value = json.loads(output_json.read_text(encoding="utf-8"))
    value["schema_version"] = (
        "open_duck.t113_always_on_trainthrough_hosted_result.v1"
    )
    value["status"] = (
        "PASS_T113_TRAINING_ARTIFACT_PENDING_CPU_VALIDATION"
        if value["status"] == "PASS_T78_TRAINING_ARTIFACT_PENDING_CPU_VALIDATION"
        else "HOLD_T113_ALWAYS_ON_TRAINTHROUGH"
    )
    value["mechanism"] = {
        "forward_path": "negative_adapter_location_always_on",
        "trainable_actor_group": "negative_adapter_location",
        "source": "exact_T100C_half_checkpoint",
        "endpoint_strata": 8,
        "retry": False,
        "same_run_resume": False,
    }
    output_json.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["status"], flush=True)
    return returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle-root", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-archive", type=Path, required=True)
    parser.add_argument("--hosted-gpu-authorized", action="store_true")
    args = parser.parse_args()
    if not args.hosted_gpu_authorized:
        raise PermissionError("T113 requires hosted GPU authorization")
    return run(
        args.bundle_root.resolve(),
        args.work_root.resolve(),
        args.output_json.resolve(),
        args.output_archive.resolve(),
    )


if __name__ == "__main__":
    raise SystemExit(main())
