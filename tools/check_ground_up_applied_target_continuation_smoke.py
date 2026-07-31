#!/usr/bin/env python3
"""Verify applied-target-state restore/update/export CPU compatibility."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import jax

from check_ground_up_hard_vector_continuation_smoke import (
    inspect_onnx,
    read_metrics,
    restore_and_compare,
    sha256_file,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-checkpoint", type=Path, required=True)
    parser.add_argument("--step-zero-checkpoint", type=Path, required=True)
    parser.add_argument("--final-checkpoint", type=Path, required=True)
    parser.add_argument("--step-zero-onnx", type=Path, required=True)
    parser.add_argument("--final-onnx", type=Path, required=True)
    parser.add_argument("--event-file", type=Path, required=True)
    parser.add_argument("--observation-contract", type=Path, required=True)
    parser.add_argument("--remap-report", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()
    if os.environ.get("JAX_PLATFORMS") != "cpu":
        raise RuntimeError("set JAX_PLATFORMS=cpu")
    if any(device.platform != "cpu" for device in jax.devices()):
        raise RuntimeError(f"non-CPU JAX device visible: {jax.devices()}")

    observation_contract = json.loads(args.observation_contract.read_text())
    remap = json.loads(args.remap_report.read_text())
    checkpoints = restore_and_compare(
        args.source_checkpoint.resolve(),
        args.step_zero_checkpoint.resolve(),
        args.final_checkpoint.resolve(),
    )
    step_zero_onnx = inspect_onnx(args.step_zero_onnx.resolve())
    final_onnx = inspect_onnx(args.final_onnx.resolve())
    metrics = read_metrics(args.event_file.resolve())
    checks = {
        "applied_target_observation_contract_passed": observation_contract["status"]
        == "PASS_CPU_APPLIED_TARGET_OBSERVATION_CONTRACT",
        "cpu_checkpoint_remap_passed": remap["status"] == "PASS_CPU_CHECKPOINT_REMAP",
        **checkpoints["checks"],
        **{f"step_zero_onnx_{key}": value for key, value in step_zero_onnx["checks"].items()},
        **{f"final_onnx_{key}": value for key, value in final_onnx["checks"].items()},
        **metrics["checks"],
    }
    failed = [name for name, passed in checks.items() if not passed]
    status = (
        "PASS_CPU_APPLIED_TARGET_CONTINUATION_SMOKE"
        if not failed
        else "FAIL_CPU_APPLIED_TARGET_CONTINUATION_SMOKE"
    )
    payload = {
        "schema_version": "ground_up_applied_target_continuation_smoke.v1",
        "status": status,
        "execution": {
            "jax_backend": jax.default_backend(),
            "jax_devices": [str(device) for device in jax.devices()],
            "robot_access": False,
            "rdk_access": False,
            "local_gpu_access": False,
            "colab_access": False,
        },
        "checks": checks,
        "failed_checks": failed,
        "observation_contract": {
            "path": str(args.observation_contract.resolve()),
            "sha256": sha256_file(args.observation_contract.resolve()),
            "status": observation_contract["status"],
        },
        "checkpoint_remap": {
            "path": str(args.remap_report.resolve()),
            "sha256": sha256_file(args.remap_report.resolve()),
            "status": remap["status"],
            "max_save_restore_error": remap["max_save_restore_error"],
        },
        "checkpoints": checkpoints,
        "step_zero_onnx": step_zero_onnx,
        "final_onnx": final_onnx,
        "metrics": metrics,
        "failed_invocations": [
            {
                "updated_policy": False,
                "reason": "Direct CUDA-sharded source restore was not CPU-portable and stopped before an update.",
            },
            {
                "updated_policy": False,
                "reason": "Missing composed-checkout PYTHONPATH loaded the editable canonical BaseRunner and stopped before an update.",
            },
        ],
        "interpretation": (
            "This proves CPU restore/update/export compatibility for the frozen "
            "applied-target observation continuation. Reward does not select a policy, "
            "and no robot or RDK clearance follows."
        ),
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Ground-Up Applied-Target Continuation CPU Smoke Result",
        "",
        f"status: `{status}`",
        "",
        f"failed checks: `{', '.join(failed) if failed else 'none'}`",
        "",
        f"source-to-step-zero max error: `{checkpoints['max_source_to_step_zero_error']}`",
        f"changed policy leaves: `{checkpoints['changed_policy_leaf_count']}` / `{checkpoints['policy_leaf_count']}`",
        f"step-zero ONNX SHA-256: `{step_zero_onnx['sha256']}`",
        f"final ONNX SHA-256: `{final_onnx['sha256']}`",
        f"final ONNX max chained bound excess: `{final_onnx['max_bound_excess']}`",
        "",
        payload["interpretation"],
        "",
    ]
    args.output_md.write_text("\n".join(lines))
    print(json.dumps({"status": status, "failed_checks": failed}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
