#!/usr/bin/env python3
"""Decompose gate failures into bridge, servo, or compound error events."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


NAMES = [
    "left_hip_pitch", "left_knee", "left_ankle",
    "right_hip_pitch", "right_knee", "right_ankle",
]
CLASSES = (
    "BOTH_INDIVIDUALLY_SUFFICIENT",
    "BRIDGE_ONLY_SUFFICIENT",
    "SERVO_ONLY_SUFFICIENT",
    "COMPOUND_SUBTHRESHOLD",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def summarize(path: Path, family: str, indices: np.ndarray, threshold: float) -> dict:
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    sent = np.asarray([row["sent_target_rad"] for row in rows], dtype=np.float64)[:, indices]
    applied = np.asarray([row["applied_target_rad"] for row in rows], dtype=np.float64)[:, indices]
    actual = np.asarray([row["actual_position_rad"] for row in rows], dtype=np.float64)[:, indices]
    total = sent - actual
    bridge = sent - applied
    servo = applied - actual
    identity_error = float(np.max(np.abs(total - bridge - servo)))
    p95 = np.percentile(np.abs(total), 95, axis=0)
    joint = int(np.argmax(p95))
    failing = bool(p95[joint] > threshold)
    event_mask = np.abs(total[:, joint]) > threshold
    bridge_sufficient = np.abs(bridge[:, joint]) > threshold
    servo_sufficient = np.abs(servo[:, joint]) > threshold
    counts = {name: 0 for name in CLASSES}
    counts["BOTH_INDIVIDUALLY_SUFFICIENT"] = int(
        np.sum(event_mask & bridge_sufficient & servo_sufficient)
    )
    counts["BRIDGE_ONLY_SUFFICIENT"] = int(
        np.sum(event_mask & bridge_sufficient & ~servo_sufficient)
    )
    counts["SERVO_ONLY_SUFFICIENT"] = int(
        np.sum(event_mask & ~bridge_sufficient & servo_sufficient)
    )
    counts["COMPOUND_SUBTHRESHOLD"] = int(
        np.sum(event_mask & ~bridge_sufficient & ~servo_sufficient)
    )
    event_count = int(np.sum(event_mask))
    aligned = int(np.sum(event_mask & (bridge[:, joint] * servo[:, joint] > 0.0)))
    return {
        "family": family,
        "group": path.parent.name,
        "path": str(path.resolve()),
        "sha256": sha256(path),
        "rows": len(rows),
        "command_x": float(rows[0]["command"][0]),
        "seed": int(rows[0]["seed"]),
        "failing": failing,
        "gate_joint": NAMES[joint],
        "gate_joint_index": int(indices[joint]),
        "gate_p95_rad": float(p95[joint]),
        "event_count": event_count,
        "event_classes": counts,
        "aligned_component_events": aligned,
        "aligned_component_fraction": float(aligned / event_count) if event_count else None,
        "bridge_component_p95_rad": float(np.percentile(np.abs(bridge[:, joint]), 95)),
        "servo_component_p95_rad": float(np.percentile(np.abs(servo[:, joint]), 95)),
        "decomposition_identity_max_error_rad": identity_error,
    }


def majority(counts: dict[str, int]) -> str:
    total = sum(counts.values())
    if not total:
        return "MIXED"
    name, count = max(counts.items(), key=lambda item: item[1])
    return name if count > total / 2 else "MIXED"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()

    prereg = json.loads(args.preregistration.read_text())
    indices = np.asarray(prereg["pitch_chain_indices"], dtype=np.int64)
    threshold = float(prereg["threshold_rad"])
    all_rows = []
    family_counts_found = {}
    for family, spec in prereg["trace_families"].items():
        root = Path(spec["root"])
        paths = sorted(root.glob("*/*.jsonl"))
        family_counts_found[family] = len(paths)
        all_rows.extend(summarize(path, family, indices, threshold) for path in paths)

    unique_seed = int(prereg["unique_seed"])
    unique = [row for row in all_rows if row["seed"] == unique_seed]
    failing = [row for row in unique if row["failing"]]
    pairs = {}
    for row in all_rows:
        pairs.setdefault((row["family"], row["group"], row["command_x"]), []).append(row)
    reproduction_deltas = []
    for key, rows in sorted(pairs.items()):
        if len(rows) != 2:
            reproduction_deltas.append({"key": key, "missing_pair": True})
            continue
        left, right = sorted(rows, key=lambda row: row["seed"])
        delta = max(
            abs(left[name] - right[name])
            for name in (
                "gate_p95_rad",
                "bridge_component_p95_rad",
                "servo_component_p95_rad",
                "decomposition_identity_max_error_rad",
            )
        )
        exact_fields = all(
            left[name] == right[name]
            for name in ("failing", "gate_joint", "event_count", "event_classes")
        )
        reproduction_deltas.append(
            {"family": key[0], "group": key[1], "command_x": key[2], "max_float_delta": delta, "exact_fields": exact_fields}
        )
    max_reproduction_delta = max(
        (item.get("max_float_delta", float("inf")) for item in reproduction_deltas),
        default=float("inf"),
    )

    families = {}
    for family in prereg["trace_families"]:
        rows = [row for row in failing if row["family"] == family]
        counts = {name: sum(row["event_classes"][name] for row in rows) for name in CLASSES}
        total = sum(counts.values())
        families[family] = {
            "unique_traces": sum(row["family"] == family for row in unique),
            "failing_traces": len(rows),
            "event_count": total,
            "event_classes": counts,
            "event_fractions": {
                name: float(value / total) if total else None for name, value in counts.items()
            },
            "majority_class": majority(counts),
            "aligned_component_fraction": float(
                sum(row["aligned_component_events"] for row in rows) / total
            ) if total else None,
        }
    family_classes = [item["majority_class"] for item in families.values()]
    global_class = (
        family_classes[0]
        if family_classes
        and family_classes[0] != "MIXED"
        and all(name == family_classes[0] for name in family_classes)
        else "MIXED"
    )
    checks = {
        "preregistration_status_valid": prereg["status"] == "PREREGISTERED_READ_ONLY_CPU_AUDIT",
        "all_family_trace_counts_exact": all(
            family_counts_found[name] == spec["expected_traces"]
            for name, spec in prereg["trace_families"].items()
        ),
        "all_156_traces_present": len(all_rows) == sum(
            item["expected_traces"] for item in prereg["trace_families"].values()
        ),
        "all_78_unique_traces_present": len(unique) == prereg["expected_unique_traces"],
        "all_traces_have_600_rows": all(row["rows"] == prereg["expected_rows_per_trace"] for row in all_rows),
        "seed_reproduction_exact": max_reproduction_delta == 0.0
        and all(item.get("exact_fields", False) for item in reproduction_deltas),
        "decomposition_identity_within_1e_12": max(
            row["decomposition_identity_max_error_rad"] for row in all_rows
        ) <= 1e-12,
        "every_failing_trace_has_events": all(row["event_count"] > 0 for row in failing),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        status = "FAIL_TRACKING_ERROR_DECOMPOSITION_EVIDENCE_CONTRACT"
        decision = "INVALID_EVIDENCE"
    elif global_class == "COMPOUND_SUBTHRESHOLD":
        status = "PASS_TRACKING_ERROR_DECOMPOSITION"
        decision = "PREREGISTER_ACTUAL_CENTERED_ABSOLUTE_TARGET_GUARD_CPU_CONTRACT"
    elif global_class == "BRIDGE_ONLY_SUFFICIENT":
        status = "PASS_TRACKING_ERROR_DECOMPOSITION"
        decision = "RETURN_TO_MEASURED_BRIDGE_IDENTIFICATION"
    elif global_class == "SERVO_ONLY_SUFFICIENT":
        status = "PASS_TRACKING_ERROR_DECOMPOSITION"
        decision = "RETURN_TO_ACTUATOR_PHYSICS_AND_LOW_LEVEL_CONTROL"
    else:
        status = "PASS_TRACKING_ERROR_DECOMPOSITION_MIXED"
        decision = "LOCALIZE_JOINT_AND_PHASE_WITHOUT_TRAINING"

    payload = {
        "schema_version": "ground_up_tracking_error_decomposition_result.v1",
        "status": status,
        "decision": decision,
        "checks": checks,
        "failed_checks": failed,
        "family_trace_counts_found": family_counts_found,
        "unique_trace_count": len(unique),
        "failing_unique_trace_count": len(failing),
        "max_seed_reproduction_delta": max_reproduction_delta,
        "global_class": global_class,
        "families": families,
        "traces": all_rows,
        "authority": {
            "actual_centered_guard_cpu_contract": not failed and global_class == "COMPOUND_SUBTHRESHOLD",
            "modify_policy_or_runtime": False,
            "training": False,
            "colab": False,
            "local_gpu": False,
            "rdk_or_robot": False,
        },
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Ground-Up Tracking-Error Decomposition Result",
        "",
        f"status: `{status}`",
        f"decision: `{decision}`",
        f"global class: `{global_class}`",
        "",
        "| family | failing traces | events | bridge only | servo only | both | compound | aligned | majority |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for family, item in families.items():
        count = item["event_classes"]
        lines.append(
            f"| `{family}` | {item['failing_traces']} | {item['event_count']} | "
            f"{count['BRIDGE_ONLY_SUFFICIENT']} | {count['SERVO_ONLY_SUFFICIENT']} | "
            f"{count['BOTH_INDIVIDUALLY_SUFFICIENT']} | {count['COMPOUND_SUBTHRESHOLD']} | "
            f"{item['aligned_component_fraction']:.6f} | `{item['majority_class']}` |"
        )
    lines.extend(
        [
            "",
            f"unique traces: `{len(unique)}`; failing unique traces: `{len(failing)}`",
            f"maximum seed reproduction delta: `{max_reproduction_delta}`",
            "",
            "The selected follow-up, if any, is a CPU contract only. No training, Colab, RDK-X5, or robot access is authorized.",
            "",
        ]
    )
    args.output_md.write_text("\n".join(lines))
    print(json.dumps({"status": status, "decision": decision, "global_class": global_class, "failed": failed}))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
