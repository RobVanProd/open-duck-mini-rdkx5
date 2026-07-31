#!/usr/bin/env python3
"""Contract the preregistered torso-COM decode implementation before use."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import numpy as np

from run_ground_up_torso_com_observability_decode import (
    canonical_manifest,
    metrics,
    parse_trace,
    ridge_projection,
    sha256,
    validate_matrix_references,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--probe", type=Path, required=True)
    parser.add_argument("--trace-root", type=Path, required=True)
    parser.add_argument("--eval-root", type=Path, required=True)
    parser.add_argument("--source-decision", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()

    prereg = json.loads(args.preregistration.read_text())
    source = prereg["source"]
    trace_root = args.trace_root.resolve()
    manifest_hash, manifest = canonical_manifest(trace_root)
    samples = [
        parse_trace(trace_root / item["path"], trace_root, source["minimum_trace_ticks"])
        for item in manifest
    ]
    matrix = validate_matrix_references(
        args.eval_root.resolve(), trace_root, {Path(sample["path"]) for sample in samples}
    )

    # Deterministic synthetic contract: the fixed ridge implementation must
    # recover three linearly separable classes without using the real labels.
    train_y = np.repeat(np.arange(3), 8)
    test_y = np.repeat(np.arange(3), 4)
    train_x = np.eye(3)[train_y]
    test_x = np.eye(3)[test_y]
    projection = ridge_projection(train_x, test_x, float(prereg["probe"]["l2"]))
    pred = np.argmax(projection @ np.eye(3)[train_y], axis=1)
    synthetic = metrics(test_y, pred, 3)

    source_text = args.probe.read_text()
    checks = {
        "preregistration_status_exact": prereg["status"]
        == "PREREGISTERED_READ_ONLY_CPU_LINEAR_DECODE",
        "trace_manifest_exact": manifest_hash == source["trace_manifest_sha256"],
        "trace_count_exact": len(samples) == 144,
        "trace_bytes_exact": sum(item["bytes"] for item in manifest)
        == source["trace_bytes"],
        "source_decision_hash_exact": sha256(args.source_decision)
        == source["decision_sha256"],
        "minimum_trace_length_exact": min(sample["ticks"] for sample in samples)
        == source["minimum_trace_ticks"],
        "full_observation_absent": all(sample["obs"].shape[1] == 6 for sample in samples),
        "matrix_trace_bijection_exact": matrix["trace_reference_bijection"],
        "synthetic_linear_decode_exact": synthetic["accuracy"] == 1.0,
        "windows_frozen": prereg["windows_ticks"] == [1, 2, 4, 8, 16, 24, 32, 40],
        "nine_group_folds_frozen": sum(len(value) for value in prereg["folds"].values())
        == 9,
        "permutation_count_and_seed_frozen": prereg["permutations"]["count"] == 1000
        and prereg["permutations"]["seed"] == 167931544,
        "probe_source_uses_obs0_6": 'row.get("obs0_6")' in source_text,
        "probe_source_rejects_obs_state": '"obs_state" in row' in source_text,
        "probe_source_has_no_policy_runtime": "onnxruntime" not in source_text
        and "run_closed_loop_sim" not in source_text,
        "cpu_only": os.environ.get("CUDA_VISIBLE_DEVICES") == "",
    }
    failed = [name for name, value in checks.items() if not value]
    status = (
        "PASS_TORSO_COM_OBSERVABILITY_DECODE_CONTRACT"
        if not failed
        else "FAIL_TORSO_COM_OBSERVABILITY_DECODE_CONTRACT"
    )
    payload = {
        "schema_version": "ground_up_torso_com_observability_decode_contract.v1",
        "status": status,
        "checks": checks,
        "failed_checks": failed,
        "inputs": {
            "preregistration_sha256": sha256(args.preregistration),
            "probe_sha256": sha256(args.probe),
            "source_decision_sha256": sha256(args.source_decision),
            "trace_manifest_sha256": manifest_hash,
        },
        "corpus": {
            "trace_files": len(samples),
            "trace_bytes": sum(item["bytes"] for item in manifest),
            "minimum_ticks": min(sample["ticks"] for sample in samples),
            **matrix,
        },
        "synthetic": synthetic,
        "authority": {
            "run_exact_read_only_probe_once": not failed,
            "policy_training": False,
            "simulator_replay": False,
            "gpu_or_igpu": False,
            "rdk_or_robot": False,
        },
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Ground-Up Torso-COM Observability Decode Contract",
        "",
        f"status: `{status}`",
        "",
    ]
    lines.extend(f"- {name}: `{value}`" for name, value in checks.items())
    lines.extend([
        "",
        "A pass authorizes one execution of only the preregistered read-only CPU probe. It does not authorize policy training, simulator replay, GPU, RDK-X5, or robot access.",
        "",
    ])
    args.output_md.write_text("\n".join(lines))
    print(json.dumps({"status": status, "failed_checks": failed}))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
