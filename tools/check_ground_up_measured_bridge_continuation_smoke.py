#!/usr/bin/env python3
"""Verify the preregistered measured-bridge restore/update/export CPU smoke."""

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


def require_cpu() -> None:
    if os.environ.get("JAX_PLATFORMS") != "cpu":
        raise RuntimeError("set JAX_PLATFORMS=cpu")
    if any(device.platform != "cpu" for device in jax.devices()):
        raise RuntimeError(f"non-CPU JAX device visible: {jax.devices()}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-checkpoint", type=Path, required=True)
    parser.add_argument("--step-zero-checkpoint", type=Path, required=True)
    parser.add_argument("--final-checkpoint", type=Path, required=True)
    parser.add_argument("--step-zero-onnx", type=Path, required=True)
    parser.add_argument("--final-onnx", type=Path, required=True)
    parser.add_argument("--event-file", type=Path, required=True)
    parser.add_argument("--bridge-contract", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()
    require_cpu()

    bridge_contract = json.loads(args.bridge_contract.read_text())
    checkpoints = restore_and_compare(
        args.source_checkpoint.resolve(),
        args.step_zero_checkpoint.resolve(),
        args.final_checkpoint.resolve(),
    )
    step_zero_onnx = inspect_onnx(args.step_zero_onnx.resolve())
    final_onnx = inspect_onnx(args.final_onnx.resolve())
    metrics = read_metrics(args.event_file.resolve())
    checks = {
        "bridge_environment_contract_passed": bridge_contract["status"]
        == "PASS_CPU_MEASURED_BRIDGE_CONTRACT",
        **checkpoints["checks"],
        **{
            f"step_zero_onnx_{key}": value
            for key, value in step_zero_onnx["checks"].items()
        },
        **{
            f"final_onnx_{key}": value
            for key, value in final_onnx["checks"].items()
        },
        **metrics["checks"],
    }
    failed = [name for name, passed in checks.items() if not passed]
    status = (
        "PASS_CPU_MEASURED_BRIDGE_CONTINUATION_SMOKE"
        if not failed
        else "FAIL_CPU_MEASURED_BRIDGE_CONTINUATION_SMOKE"
    )
    payload = {
        "schema_version": "ground_up_measured_bridge_continuation_smoke.v1",
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
        "bridge_contract": {
            "path": str(args.bridge_contract.resolve()),
            "sha256": sha256_file(args.bridge_contract.resolve()),
            "status": bridge_contract["status"],
        },
        "checkpoints": checkpoints,
        "step_zero_onnx": step_zero_onnx,
        "final_onnx": final_onnx,
        "metrics": metrics,
        "interpretation": (
            "This proves CPU restore/update/export compatibility with the bridge-only "
            "transition. Training reward and this short rollout are not policy-selection "
            "evidence, and no robot clearance follows."
        ),
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Ground-Up Measured-Bridge Continuation CPU Smoke Result",
        "",
        f"status: `{status}`",
        "",
        f"failed checks: `{', '.join(failed) if failed else 'none'}`",
        "",
        f"source-to-step-zero max error: `{checkpoints['max_source_to_step_zero_error']}`",
        f"changed policy leaves: `{checkpoints['changed_policy_leaf_count']}` / "
        f"`{checkpoints['policy_leaf_count']}`",
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
