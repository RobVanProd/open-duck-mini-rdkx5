#!/usr/bin/env python3
"""Import and independently verify the frozen Winner-v12 CPU smoke artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "outputs/analysis/winner_v12_calibrator_cpu_smoke_contract.json"
DEFAULT_OUTPUT = ROOT / "outputs/analysis/winner_v12_calibrator_cpu_smoke_result.json"
DEFAULT_MARKDOWN = (
    ROOT / "outputs/analysis/WINNER_V12_CALIBRATOR_CPU_SMOKE_RESULT_20260720.md"
)
EXPECTED_CHECKPOINT = "winner_v12_calibrator_smoke_checkpoint.npz"
EXPECTED_GRAPH = "winner_v12_calibrator_after_smoke.onnx"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def git_output(*arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(completed.stdout)
    return completed.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-result", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    args = parser.parse_args()
    if args.output.exists() or args.markdown.exists():
        raise FileExistsError("refusing to overwrite an imported Winner-v12 result")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    raw = json.loads(args.raw_result.read_text(encoding="utf-8"))
    graph = args.artifact_root / EXPECTED_GRAPH
    checkpoint = args.artifact_root / EXPECTED_CHECKPOINT
    checks = {
        "contract_passed_before_execution": contract.get("status")
        == "PASS_WINNER_V12_CALIBRATOR_CPU_SMOKE_CONTRACT",
        "raw_schema_exact": raw.get("schema_version")
        == "winner_v12.calibrator_cpu_smoke_result.v1",
        "raw_status_pass": raw.get("status") == "PASS_WINNER_V12_CALIBRATOR_CPU_SMOKE",
        "raw_contract_hash_exact": (raw.get("contract") or {}).get(
            "canonical_lf_sha256"
        )
        == lf_sha256(CONTRACT)
        and (raw.get("contract") or {}).get("hash_mode") == "lf",
        "software_versions_exact": (raw.get("environment") or {})
        .get("software_versions", {})
        .get("exact")
        is True
        and (raw.get("environment") or {}).get("software_versions", {}).get("expected")
        == contract["software_versions"]
        and (raw.get("environment") or {}).get("software_versions", {}).get("observed")
        == contract["software_versions"],
        "all_raw_checks_pass": bool(raw.get("checks"))
        and all(bool(value) for value in raw["checks"].values())
        and not raw.get("failed_checks"),
        "one_update_per_stage": (raw.get("execution") or {}).get("optimizer_updates")
        == {"stage1": 1, "stage2": 1},
        "zero_formal_cells": (raw.get("execution") or {}).get("formal_support_cells")
        == 0,
        "zero_locomotion_training": (raw.get("execution") or {}).get(
            "locomotion_training_steps"
        )
        == 0,
        "zero_protected_policy_calls": (raw.get("execution") or {}).get(
            "protected_policy_inference_calls"
        )
        == 0,
        "zero_robot_access": (raw.get("execution") or {}).get("robot_or_rdk_access")
        == 0,
        "no_retry": (raw.get("execution") or {}).get("retry_count") == 0,
        "population_exact": (raw.get("smoke_population") or {}).get("configuration_ids")
        == contract["smoke_population"]["configuration_ids"],
        "balanced_plants": (raw.get("smoke_population") or {}).get("plant_counts")
        == {
            "P30_ALL_JOINT": 8,
            "P31_34_PITCH_WITH_P30_NONPITCH": 8,
        },
        "graph_present": graph.is_file(),
        "checkpoint_present": checkpoint.is_file(),
        "graph_hash_exact": graph.is_file()
        and sha256(graph) == (raw.get("onnx") or {}).get("sha256"),
        "checkpoint_hash_exact": checkpoint.is_file()
        and sha256(checkpoint) == (raw.get("checkpoint") or {}).get("sha256"),
        "jax_onnx_bound": float(
            (raw.get("onnx") or {}).get("jax_onnx_max_abs_error", float("inf"))
        )
        <= 1.0e-7,
        "training_only_graph_state_absent": bool(
            (raw.get("onnx") or {}).get("training_only_tensors_absent")
        ),
        "onnx_chain_outputs_finite": bool(
            (raw.get("onnx") or {}).get("all_chain_outputs_finite")
        ),
        "protected_hashes_exact": raw.get("protected_policies")
        == contract["protected_policies"],
        "authority_remains_offline": not any(
            bool((raw.get("authority") or {}).get(key))
            for key in (
                "full_training_executed",
                "formal_behavior_evaluation_executed",
                "robot_clearance",
                "rdkx5_robot_serial_gpio_i2c_torque_motion",
            )
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    passed = not failed
    payload: dict[str, Any] = {
        "schema_version": "winner_v12.calibrator_cpu_smoke_import.v1",
        "status": (
            "PASS_WINNER_V12_CALIBRATOR_CPU_SMOKE_ARTIFACT"
            if passed
            else "HOLD_WINNER_V12_CALIBRATOR_CPU_SMOKE_ARTIFACT"
        ),
        "decision": (
            "AUTHORIZE_FULL_CALIBRATOR_TRAINING_PREREGISTRATION_ONLY"
            if passed
            else "STOP_WINNER_V12_CALIBRATOR_IMPLEMENTATION"
        ),
        "raw_result": {
            "path": str(args.raw_result),
            "sha256": sha256(args.raw_result),
            "bytes": args.raw_result.stat().st_size,
        },
        "contract": {
            "path": str(CONTRACT),
            "canonical_lf_sha256": lf_sha256(CONTRACT),
            "hash_mode": "lf",
        },
        "artifacts": {
            "checkpoint": {
                "path": str(checkpoint),
                "sha256": sha256(checkpoint) if checkpoint.is_file() else None,
            },
            "calibrator_onnx": {
                "path": str(graph),
                "sha256": sha256(graph) if graph.is_file() else None,
            },
        },
        "checks": checks,
        "failed_checks": failed,
        "smoke_summary": {
            "stage1_valid_transitions": (raw.get("stage1") or {}).get(
                "valid_transitions"
            ),
            "stage2_valid_transitions": (raw.get("stage2") or {}).get(
                "valid_transitions"
            ),
            "jax_onnx_max_abs_error": (raw.get("onnx") or {}).get(
                "jax_onnx_max_abs_error"
            ),
            "final_deployable_parameter_sha256": (
                raw.get("parameter_hashes") or {}
            ).get("final_deployable"),
        },
        "repository_attribution": {
            "import_commit_parent": git_output("rev-parse", "HEAD"),
            "raw_artifact_committed": False,
            "onnx_checkpoint_committed": False,
        },
        "authority": {
            "full_training": False,
            "formal_behavior_evaluation": False,
            "hosted_gpu_or_igpu": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "robot_clearance": False,
            "pass_authorizes_only": (
                "a separate prospective full-calibrator training preregistration"
            ),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# Winner-v12 calibrator CPU-smoke artifact",
        "",
        f"- Status: `{payload['status']}`",
        f"- Decision: `{payload['decision']}`",
        f"- Raw result SHA-256: `{payload['raw_result']['sha256']}`",
        f"- Calibrator ONNX SHA-256: `{payload['artifacts']['calibrator_onnx']['sha256']}`",
        f"- Checkpoint SHA-256: `{payload['artifacts']['checkpoint']['sha256']}`",
        f"- Stage-1 valid transitions: `{payload['smoke_summary']['stage1_valid_transitions']}`",
        f"- Stage-2 valid transitions: `{payload['smoke_summary']['stage2_valid_transitions']}`",
        f"- JAX/ONNX maximum absolute error: `{payload['smoke_summary']['jax_onnx_max_abs_error']}`",
        "",
        "This is one implementation smoke with one optimizer update per stage. It is not",
        "full training, behavior evidence, deployment selection, Gate 5 authority, or robot",
        "clearance. A pass authorizes only a separate prospective full-training",
        "preregistration.",
        "",
    ]
    if failed:
        lines.extend(["## Failed checks", ""])
        lines.extend(f"- `{name}`" for name in failed)
        lines.append("")
    args.markdown.write_text("\n".join(lines), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "failed_checks": failed,
                "output_sha256": sha256(args.output),
            },
            sort_keys=True,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
