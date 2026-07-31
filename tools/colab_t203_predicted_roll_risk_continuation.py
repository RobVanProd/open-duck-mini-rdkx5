#!/usr/bin/env python3
"""Run T203's one frozen predicted-roll-risk continuation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tarfile
from typing import Any

import jax

sys.path.insert(0, str(Path(__file__).resolve().parent))

import colab_t170_eight_stratum_head_continuation as base
from colab_t32_action_margin_trainthrough_continuation import (
    canonical_sha256,
    source_inventory,
)
from colab_winner_v114_linear_torque_continuation import (
    directory_sha256,
    sha256,
)


PREREGISTRATION_NAME = (
    "t203_predicted_roll_risk_hosted_preregistration.json"
)
CPU_RESULT_NAME = "t202_predicted_roll_risk_cpu_result.json"
RECOVERY_RESULT_NAME = "t202b_metric_namespace_recovery_result.json"
T171_VALIDATION_NAME = "t171_t170_recovered_training_validation.json"
GATE_NAME = base.GATE_NAME
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
    """Add only T202's frozen training objective to the T170 recipe."""
    command = _BASE_RUNNER_COMMAND(playground, output, source, reference)
    anchor = command.index("--winner_t98_hidden_expert_continuation") + 1
    command.insert(anchor, "--winner_t202_predicted_roll_risk")
    return command


def validate_inputs(bundle: Path) -> dict[str, Any]:
    preregistration = bundle / PREREGISTRATION_NAME
    cpu_result_path = bundle / CPU_RESULT_NAME
    recovery_result_path = bundle / RECOVERY_RESULT_NAME
    t171_path = bundle / T171_VALIDATION_NAME
    playground = bundle / "playground"
    assets = bundle / "assets"
    source = assets / SOURCE_CHECKPOINT_NAME
    reference = assets / REFERENCE_NAME
    step_zero = assets / STEP_ZERO_NAME
    gate = assets / GATE_NAME
    prereg = json.loads(preregistration.read_text(encoding="utf-8"))
    cpu = json.loads(cpu_result_path.read_text(encoding="utf-8"))
    recovery = json.loads(
        recovery_result_path.read_text(encoding="utf-8")
    )
    t171 = json.loads(t171_path.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    substantive = {
        name: passed
        for name, passed in cpu["checks"].items()
        if name != "training_roll_risk_metrics_finite"
    }
    if (
        prereg.get("status")
        != "PREREGISTERED_T203_PREDICTED_ROLL_RISK_HOSTED_CONTINUATION"
        or prereg.get("failed_checks")
        or canonical_sha256(basis)
        != prereg.get("preregistered_contract_sha256")
        or cpu.get("status")
        != "HOLD_T202_PREDICTED_ROLL_RISK_CPU_CONTRACT"
        or cpu.get("failed_checks")
        != ["training_roll_risk_metrics_finite"]
        or not all(substantive.values())
        or recovery.get("status")
        != "PASS_T202B_METRIC_NAMESPACE_RECOVERY"
        or recovery.get("failed_checks")
        or recovery.get("decision")
        != (
            "EARN_T203_PREDICTED_ROLL_RISK_HOSTED_"
            "PREREGISTRATION_ONLY"
        )
        or t171.get("status")
        != "PASS_T171_T170_RECOVERED_TRAINING_VALIDATION"
        or t171.get("failed_checks")
    ):
        raise ValueError("T203 prerequisite status or identity changed")
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
        "recovery_result": sha256(recovery_result_path),
        "t171_validation": sha256(t171_path),
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
        raise ValueError("T203 frozen inputs changed")
    devices = [str(device) for device in jax.devices()]
    if (
        not devices
        or not all(device.platform == "gpu" for device in jax.devices())
        or jax.process_count() != 1
    ):
        raise RuntimeError(f"T203 requires one GPU process: {devices}")
    return {
        "input_hashes": observed,
        "devices": devices,
        "process_count": jax.process_count(),
        "preregistration_sha256": sha256(preregistration),
    }


def make_artifact(work: Path, destination: Path) -> dict[str, Any]:
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    with tarfile.open(temporary, "w:gz") as archive:
        archive.add(
            work,
            arcname="t203_predicted_roll_risk_continuation",
        )
    temporary.replace(destination)
    return {
        "path": str(destination),
        "sha256": sha256(destination),
        "bytes": destination.stat().st_size,
    }


def run(
    bundle: Path,
    work: Path,
    output_json: Path,
    output_archive: Path,
) -> int:
    base.runner_command = runner_command
    base.validate_inputs = validate_inputs
    base.make_artifact = make_artifact
    returncode = base.run(bundle, work, output_json, output_archive)
    value = json.loads(output_json.read_text(encoding="utf-8"))
    value["schema_version"] = (
        "open_duck.t203_predicted_roll_risk_hosted_result.v1"
    )
    value["status"] = (
        "PASS_T203_TRAINING_ARTIFACT_PENDING_CPU_VALIDATION"
        if value["status"]
        == "PASS_T170_TRAINING_ARTIFACT_PENDING_CPU_VALIDATION"
        else "HOLD_T203_PREDICTED_ROLL_RISK_CONTINUATION"
    )
    value["mechanism"] = {
        "source": "exact_T170_half_checkpoint_1003520",
        "risk": "abs(body_roll_rad + 0.08 * body_roll_rate_rad_s)",
        "passing_envelope_rad": 0.3541802655745987,
        "scale": 0.8017763166551805,
        "objective": "original_clipped_reward_minus_scaled_squared_excess",
        "cost_placement": "outside_existing_positive_reward_clip",
        "support_objective": False,
        "body_configuration_strata": 8,
        "environments_per_stratum": 32,
        "trainable_actor_group": "negative_adapter_location",
        "critic_trainable": True,
        "normalizer_frozen": True,
        "deployment_graph_change": False,
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
        raise PermissionError("T203 requires hosted GPU authorization")
    return run(
        args.bundle_root.resolve(),
        args.work_root.resolve(),
        args.output_json.resolve(),
        args.output_archive.resolve(),
    )


if __name__ == "__main__":
    raise SystemExit(main())
