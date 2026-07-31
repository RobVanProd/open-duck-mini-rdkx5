#!/usr/bin/env python3
"""Run T22's corrected 1,024-step CPU restore/update/export smoke."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import onnx

import run_t20_support_trainthrough_one_update as t20

from build_ground_up_actual_centered_guard_screen import append_guard
from build_ground_up_command_deadband_repair import wrap as append_deadband
from build_winner_v117_postguard_rate_projection_policies import (
    append_projection,
    inference_contract,
)


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREGISTRATION = (
    ANALYSIS / "t22_corrected_one_update_cpu_preregistration.json"
)
RESULT = ANALYSIS / "t22_corrected_one_update_cpu_result.json"
MARKDOWN = ANALYSIS / "T22_CORRECTED_ONE_UPDATE_CPU_RESULT_20260726.md"
V121_PREREGISTRATION = (
    ANALYSIS / "winner_v121_deployment_transform_preregistration.json"
)
SOURCE_VELOCITY_LIMITS = (
    "1.0,.75,1.4736209064722061,1.4300791546702385,"
    "1.3976470567286015,.5,.5,.5,.5,.5,.75,1.25,1.0,"
    "1.2215287424623966"
)


def validate_preregistration(value: dict) -> None:
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        value.get("status")
        != "PREREGISTERED_T22_CORRECTED_ONE_UPDATE_CPU_SMOKE"
        or t20.canonical_sha256(basis)
        != value.get("preregistered_contract_sha256")
    ):
        raise RuntimeError("T22 preregistration identity changed")
    for name, item in value["sources"].items():
        t20.verify_receipt(item, name)
    for name, item in value["assets"].items():
        t20.verify_receipt(item, name)


def apply_v121_source_deployment(
    source_path: Path,
    output_path: Path,
) -> dict:
    prereg = json.loads(V121_PREREGISTRATION.read_text(encoding="utf-8"))
    transform = prereg["transform"]
    home = np.asarray(transform["home_target_rad"], dtype=np.float32)
    actual_indices = np.asarray(
        transform["measured_joint_offset_indices"],
        dtype=np.int64,
    )
    pitch_indices = np.asarray(
        transform["pitch_chain_action_indices"],
        dtype=np.int64,
    )
    selected_delta = np.asarray(
        transform["exact_train_normalized_action_delta"],
        dtype=np.float32,
    )
    command_index = int(transform["command_x_observation_index"])
    deadband = float(transform["zero_deadband_absolute_command_x"])
    action_scale = float(transform["action_scale_rad"])
    margin = float(transform["g3_margin_rad"])
    source = onnx.load(source_path)
    guarded = append_guard(
        source,
        obs_indices=actual_indices,
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
        source_path,
        output_path,
        selected_delta=selected_delta,
        changed_indices=pitch_indices,
        command_index=command_index,
        deadband=deadband,
        home=home,
        pitch_indices=pitch_indices,
        actual_obs_indices=actual_indices,
        action_scale=action_scale,
        guard_margin=margin,
    )
    return {
        "receipt": t20.receipt(output_path),
        "io": t20.graph_io(output_path),
        "inference": inference,
        "node_counts": {
            "raw": len(source.graph.node),
            "guarded": len(guarded.graph.node),
            "deadbanded": len(deadbanded.graph.node),
            "deployed": len(deployed.graph.node),
        },
    }


def deployment_graph(raw: Path, output_root: Path) -> dict:
    output_root.mkdir(parents=True)
    source_deployed = output_root / "v121_source_deployed.onnx"
    context = output_root / "context_abi.onnx"
    wrapped = output_root / "rate_coherent_support.onnx"
    source_deployment = apply_v121_source_deployment(
        raw,
        source_deployed,
    )
    t20.add_context_input(source_deployed, context)
    context_parity = t20.parity_contract(source_deployed, context)
    wrapper = t20.wrap_rate_coherent_support(context, wrapped)
    verification = t20.verify_wrapper(context, wrapped)
    return {
        "raw": t20.receipt(raw),
        "raw_io": t20.graph_io(raw),
        "source_deployed": source_deployment["receipt"],
        "source_deployed_io": source_deployment["io"],
        "source_deployment": source_deployment,
        "context_abi": t20.receipt(context),
        "context_io": t20.graph_io(context),
        "context_parity": context_parity,
        "wrapped": t20.receipt(wrapped),
        "wrapped_io": t20.graph_io(wrapped),
        "wrapper": wrapper,
        "verification": verification,
    }


def finalize_t22_result() -> int:
    prereg = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    deployments = value["deployments"]
    step_zero = deployments["0"]
    checks = dict(value["checks"])
    checks["step_zero_source_deployed_byte_exact"] = (
        step_zero["source_deployed"]["sha256"]
        == prereg["assets"]["frozen_v121_deployed_half_onnx"]["sha256"]
    )
    checks["both_source_deployment_contracts_pass"] = all(
        row["source_deployment"]["inference"]["pass"]
        and row["source_deployment"]["node_counts"]
        == {
            "raw": 29,
            "guarded": 42,
            "deadbanded": 47,
            "deployed": 56,
        }
        for row in deployments.values()
    )
    checks["command_uses_trained_source_rate_vector"] = (
        value["training"]["command"][
            value["training"]["command"].index(
                "--ground_up_action_velocity_limits_rad_s"
            )
            + 1
        ]
        == SOURCE_VELOCITY_LIMITS
    )
    checks = {name: bool(passed) for name, passed in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value["schema_version"] = (
        "open_duck.t22_corrected_one_update_cpu_result.v1"
    )
    value["status"] = (
        "PASS_T22_CORRECTED_ONE_UPDATE_CPU_SMOKE"
        if not failed
        else "HOLD_T22_CORRECTED_ONE_UPDATE_CPU_SMOKE"
    )
    value["decision"] = (
        "EARN_T22_HOSTED_CONTINUATION_PREREGISTRATION"
        if not failed
        else "KEEP_HOSTED_TRAINING_CLOSED"
    )
    value["checks"] = checks
    value["failed_checks"] = failed
    value["authority"] = {
        "hosted_preregistration_authorized": not failed,
        "hosted_training_authorized": False,
        "behavior_matrix_authorized": False,
        "checkpoint_selection_authorized": False,
        "policy_deployment_authorized": False,
        "gate5_authorized": False,
        "robot_or_rdk_access": False,
        "torque_or_motion": False,
    }
    value.pop("result_sha256", None)
    value["result_sha256"] = t20.canonical_sha256(value)
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T22 corrected one-update CPU result",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                f"- Failed checks: `{failed}`",
                (
                    "- CPU simulator steps / hosted / robot: "
                    f"`{value['execution']['cpu_simulator_steps']}/0/0`"
                ),
                (
                    "- Step-zero raw/source-deployed/context/final hashes: "
                    f"`{step_zero['raw']['sha256']}` / "
                    f"`{step_zero['source_deployed']['sha256']}` / "
                    f"`{step_zero['context_abi']['sha256']}` / "
                    f"`{step_zero['wrapped']['sha256']}`"
                ),
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


def main() -> int:
    t20.PREREGISTRATION = PREREGISTRATION
    t20.RESULT = RESULT
    t20.MARKDOWN = MARKDOWN
    t20.VELOCITY_LIMITS = SOURCE_VELOCITY_LIMITS
    t20.validate_preregistration = validate_preregistration
    t20.deployment_graph = deployment_graph
    t20.main()
    return finalize_t22_result()


if __name__ == "__main__":
    raise SystemExit(main())
