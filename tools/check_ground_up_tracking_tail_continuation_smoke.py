#!/usr/bin/env python3
"""Verify the preregistered tracking-tail continuation on CPU."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import jax
import numpy as np

from check_ground_up_hard_vector_continuation_smoke import (
    inspect_onnx,
    read_metrics,
    restore_and_compare,
    sha256_file,
)


TAIL_TAG = "eval/episode_cost/tracking_tail_exceedance"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-checkpoint", type=Path, required=True)
    parser.add_argument("--step-zero-checkpoint", type=Path, required=True)
    parser.add_argument("--final-checkpoint", type=Path, required=True)
    parser.add_argument("--step-zero-onnx", type=Path, required=True)
    parser.add_argument("--final-onnx", type=Path, required=True)
    parser.add_argument("--event-file", type=Path, required=True)
    parser.add_argument("--tail-contract", type=Path, required=True)
    parser.add_argument("--remap-report", type=Path, required=True)
    parser.add_argument("--patch", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()

    if os.environ.get("JAX_PLATFORMS") != "cpu":
        raise RuntimeError("set JAX_PLATFORMS=cpu")
    if any(device.platform != "cpu" for device in jax.devices()):
        raise RuntimeError(f"non-CPU JAX device visible: {jax.devices()}")

    contract = json.loads(args.tail_contract.read_text())
    remap = json.loads(args.remap_report.read_text())
    preregistration = json.loads(args.preregistration.read_text())
    patch_sha256 = sha256_file(args.patch.resolve())
    checkpoints = restore_and_compare(
        args.source_checkpoint.resolve(),
        args.step_zero_checkpoint.resolve(),
        args.final_checkpoint.resolve(),
    )
    step_zero_onnx = inspect_onnx(args.step_zero_onnx.resolve())
    final_onnx = inspect_onnx(args.final_onnx.resolve())
    metrics = read_metrics(args.event_file.resolve())
    tail_values = metrics["scalars"].get(TAIL_TAG, [])
    tail_numbers = [entry["value"] for entry in tail_values]
    checks = {
        "tail_cpu_contract_passed": contract["status"]
        == "PASS_TRACKING_TAIL_CPU_CONTRACT",
        "cpu_checkpoint_remap_passed": remap["status"]
        == "PASS_CPU_CHECKPOINT_REMAP",
        "patch_matches_preregistration": preregistration["tail_contract"][
            "patch_sha256"
        ]
        == patch_sha256,
        **checkpoints["checks"],
        "all_policy_leaves_changed": checkpoints["changed_policy_leaf_count"]
        == checkpoints["policy_leaf_count"],
        **{
            f"step_zero_onnx_{key}": value
            for key, value in step_zero_onnx["checks"].items()
        },
        **{
            f"final_onnx_{key}": value
            for key, value in final_onnx["checks"].items()
        },
        **metrics["checks"],
        "tail_metric_present": bool(tail_numbers),
        "tail_metric_finite": bool(tail_numbers)
        and bool(np.all(np.isfinite(tail_numbers))),
        "tail_metric_nonzero": bool(tail_numbers)
        and bool(np.any(np.asarray(tail_numbers) > 0.0)),
        "tail_metric_has_step_zero_and_1024": {0, 1024}.issubset(
            {entry["step"] for entry in tail_values}
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    status = (
        "PASS_CPU_TRACKING_TAIL_CONTINUATION_SMOKE"
        if not failed
        else "FAIL_CPU_TRACKING_TAIL_CONTINUATION_SMOKE"
    )
    payload = {
        "schema_version": "ground_up_tracking_tail_continuation_smoke.v1",
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
        "tail_contract": {
            "path": str(args.tail_contract.resolve()),
            "sha256": sha256_file(args.tail_contract.resolve()),
            "status": contract["status"],
        },
        "checkpoint_remap": {
            "path": str(args.remap_report.resolve()),
            "sha256": sha256_file(args.remap_report.resolve()),
            "status": remap["status"],
            "max_save_restore_error": remap["max_save_restore_error"],
        },
        "implementation": {
            "patch": str(args.patch.resolve()),
            "patch_sha256": patch_sha256,
            "preregistered_patch_sha256": preregistration["tail_contract"][
                "patch_sha256"
            ],
        },
        "checkpoints": checkpoints,
        "step_zero_onnx": step_zero_onnx,
        "final_onnx": final_onnx,
        "metrics": metrics,
        "tail_metric": {"tag": TAIL_TAG, "values": tail_values},
        "failed_invocation": {
            "updated_policy": False,
            "reason": (
                "The first host-CPU invocation reused an incompatible AOT cache and "
                "stopped after step-zero output, before any PPO update. The retry used "
                "a fresh CPU-only cache and is the result evaluated here."
            ),
        },
        "interpretation": (
            "This proves only restore/update/export and metric-wiring compatibility for "
            "the preregistered tracking-tail continuation. Reward does not select a "
            "policy, and no robot, RDK-X5, deployment, or local-GPU clearance follows."
        ),
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Ground-Up Tracking-Tail Continuation CPU Smoke Result",
        "",
        f"status: `{status}`",
        "",
        f"failed checks: `{', '.join(failed) if failed else 'none'}`",
        "",
        f"source-to-step-zero max error: `{checkpoints['max_source_to_step_zero_error']}`",
        f"changed policy leaves: `{checkpoints['changed_policy_leaf_count']}` / `{checkpoints['policy_leaf_count']}`",
        f"tail metric at step 0 / 1,024: `{tail_numbers}`",
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
