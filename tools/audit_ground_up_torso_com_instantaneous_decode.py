#!/usr/bin/env python3
"""Audit the raw tick-zero evidence behind the instantaneous COM decode."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from run_ground_up_torso_com_observability_decode import sha256


CONDITIONS = (
    ("TORSO_COM_X_NEG", "NEG"),
    ("NOMINAL", "NOMINAL"),
    ("TORSO_COM_X_POS", "POS"),
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace-root", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()

    result = json.loads(args.result.read_text())
    classes = {}
    for condition, label in CONDITIONS:
        values = []
        for path in sorted((args.trace_root / condition).rglob("*.jsonl")):
            first = json.loads(path.read_text().splitlines()[0])
            if first.get("tick") != 0:
                raise ValueError(f"trace does not start at tick zero: {path}")
            values.append(first["obs0_6"])
        array = np.asarray(values, dtype=np.float64)
        unique = np.unique(array, axis=0)
        classes[label] = {
            "condition": condition,
            "samples": int(array.shape[0]),
            "unique_vectors": int(unique.shape[0]),
            "tick0_obs0_6": unique[0].tolist() if unique.shape[0] == 1 else None,
        }
    labels = [item[1] for item in CONDITIONS]
    pairwise = []
    for index, label_a in enumerate(labels):
        a = np.asarray(classes[label_a]["tick0_obs0_6"], dtype=float)
        for label_b in labels[index + 1 :]:
            b = np.asarray(classes[label_b]["tick0_obs0_6"], dtype=float)
            pairwise.append(
                {
                    "class_a": label_a,
                    "class_b": label_b,
                    "euclidean_distance": float(np.linalg.norm(a - b)),
                    "maximum_absolute_component_difference": float(np.max(np.abs(a - b))),
                }
            )
    checks = {
        "decode_result_status_pass": result["status"]
        == "PASS_TORSO_COM_OBSERVABILITY_DECODE_EVIDENCE",
        "decode_decision_instantaneous": result["decision"]
        == "PASS_INSTANTANEOUS_IMU_COM_DECODE",
        "earliest_window_one_tick": result["earliest_passing_window_ticks"] == 1,
        "n1_all_folds_perfect": all(
            fold["accuracy"] == 1.0 for fold in result["windows"]["1"]["folds"]
        ),
        "exact_48_per_class": all(item["samples"] == 48 for item in classes.values()),
        "one_unique_tick0_vector_per_class": all(
            item["unique_vectors"] == 1 for item in classes.values()
        ),
        "tick0_gyro_zero_all_classes": all(
            np.array_equal(np.asarray(item["tick0_obs0_6"][:3]), np.zeros(3))
            for item in classes.values()
        ),
        "tick0_accelerometer_distinct_all_classes": len(
            {tuple(item["tick0_obs0_6"][3:]) for item in classes.values()}
        )
        == 3,
    }
    failed = [name for name, value in checks.items() if not value]
    status = "PASS_INSTANTANEOUS_IMU_COM_DECODE_RAW_AUDIT" if not failed else "FAIL_INSTANTANEOUS_IMU_COM_DECODE_RAW_AUDIT"
    payload = {
        "schema_version": "ground_up_torso_com_instantaneous_decode_raw_audit.v1",
        "status": status,
        "checks": checks,
        "failed_checks": failed,
        "decode_result_sha256": sha256(args.result),
        "classes": classes,
        "pairwise": pairwise,
        "interpretation": (
            "The instantaneous classification is carried by the exact tick-zero accelerometer, "
            "not gyro, and is invariant across arm, checkpoint, fit, and command within each COM class."
        ),
        "authority": {
            "separate_objective_or_exploitation_preregistration_only": not failed,
            "memory_selected": False,
            "policy_training": False,
            "gpu_or_igpu": False,
            "rdk_or_robot": False,
        },
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Ground-Up Torso-COM Instantaneous Decode Raw Audit",
        "",
        f"status: `{status}`",
        "",
        "| class | samples | unique tick-0 vectors | gyro xyz | accelerometer xyz |",
        "|---|---:|---:|---|---|",
    ]
    for label in labels:
        item = classes[label]
        value = item["tick0_obs0_6"]
        lines.append(
            f"| `{label}` | {item['samples']} | {item['unique_vectors']} | "
            f"`{value[:3]}` | `{value[3:]}` |"
        )
    lines.extend([
        "",
        payload["interpretation"],
        "",
        "This selects no memory architecture and authorizes no training. It supports only a separately preregistered objective/exploitation study.",
        "",
    ])
    args.output_md.write_text("\n".join(lines))
    print(json.dumps({"status": status, "failed_checks": failed}))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
