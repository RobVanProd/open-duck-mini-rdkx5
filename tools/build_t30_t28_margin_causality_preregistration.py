#!/usr/bin/env python3
"""Freeze the one-cell T28 action-margin causal A/B."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T27_PREREG = ANALYSIS / "t27_t23_robustness_matrix_preregistration.json"
T28_TRANSFORM = ANALYSIS / "t28_t23_action_margin_transform_contract.json"
T29_RESULT = ANALYSIS / "t29_t28_remaining_r2_result.json"
RUNNER = ROOT / "tools" / "run_t30_t28_margin_causality.py"
WORKER = ROOT / "tools" / "evaluate_t30_t28_margin_causal_cell.py"
OUTPUT = ANALYSIS / "t30_t28_margin_causality_preregistration.json"
OUTPUT_MD = (
    ANALYSIS / "T30_T28_MARGIN_CAUSALITY_PREREGISTRATION_20260726.md"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    payload = dict(value)
    payload.pop("preregistered_contract_sha256", None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def main() -> int:
    basis = json.loads(T27_PREREG.read_text(encoding="utf-8"))
    transform = json.loads(T28_TRANSFORM.read_text(encoding="utf-8"))
    result = json.loads(T29_RESULT.read_text(encoding="utf-8"))
    failed = [
        (block, cell)
        for block in result["blocks"]
        for cell in block["result"]["cells"]
        if not cell["cell_green"]
    ]
    if len(failed) != 1:
        raise ValueError("T29 does not contain exactly one failed cell")
    failed_block, failed_cell = failed[0]
    manifest_path = Path(failed_block["manifest"]["path"])
    if sha256(manifest_path) != failed_block["manifest"]["sha256"]:
        raise ValueError("changed T29 failed-block manifest")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    wrapped_trace = next(
        item
        for item in manifest["traces"]
        if "x0.077_" in Path(item["path"]).name
    )
    wrapped_trace_path = Path(wrapped_trace["path"])
    if sha256(wrapped_trace_path) != wrapped_trace["sha256"]:
        raise ValueError("changed T29 failed trace")
    threshold = np.float32(
        transform["saturation_observation_threshold_abs"]
    )
    limit = np.float32(transform["stored_float32_limit_abs"])
    intervention_events = []
    with wrapped_trace_path.open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            for joint_index, value in enumerate(row["action"]):
                if abs(float(value)) >= float(limit):
                    intervention_events.append(
                        {
                            "tick": int(row["tick"]),
                            "joint_index": joint_index,
                            "action": float(value),
                        }
                    )
    source = next(
        item
        for item in basis["policies"]
        if item["checkpoint_id"] == "T23_SUPPORT_FINAL"
    )
    source_path = Path(source["path"])
    if sha256(source_path) != source["sha256"]:
        raise ValueError("changed unwrapped T23 final policy")
    p30 = next(item for item in basis["fits"] if item["fit_id"] == "p30")
    checks = {
        "t29_has_exactly_one_failure": len(failed) == 1,
        "failed_cell_is_frozen_target": (
            failed_block["checkpoint_id"] == "T23_SUPPORT_FINAL"
            and failed_block["fit_id"] == "p30"
            and failed_block["condition_id"] == "JOINT_FRICTIONLOSS_LO"
            and float(failed_cell["command_x_m_s"]) == 0.077
        ),
        "failed_cell_is_not_saturation_or_protection": (
            failed_cell["behavior"]["replacement_quality_checks"][
                "zero_saturation"
            ]
            and failed_cell["protection"]["duration_protection_pass"]
            and failed_cell["handoff"]["all_checks_pass"]
        ),
        "wrapped_trace_terminates_early": (
            failed_cell["behavior"]["samples"] < 600
        ),
        "transform_intervened_before_failure": (
            len(intervention_events) > 0
            and intervention_events[0]["tick"]
            < failed_cell["behavior"]["samples"]
        ),
        "limit_is_strictly_below_threshold": float(limit) < float(threshold),
        "runner_and_worker_present": RUNNER.is_file() and WORKER.is_file(),
    }
    failed_checks = [name for name, passed in checks.items() if not passed]
    payload: dict[str, Any] = {
        "schema_version": (
            "open_duck.t30_t28_margin_causality_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T30_T28_MARGIN_CAUSAL_AB"
            if not failed_checks
            else "HOLD_T30_T28_MARGIN_CAUSALITY_PREREGISTRATION"
        ),
        "question": (
            "Did the uniform T28 action-margin transform cause the sole T29 "
            "failure, or does the unwrapped T23 final policy also fail the "
            "identical cell?"
        ),
        "cell": {
            "condition": {
                "condition_index": 3,
                "id": "JOINT_FRICTIONLOSS_LO",
                "override": {"joint_frictionloss_scale": 0.9},
            },
            "checkpoint_id": "T23_SUPPORT_FINAL",
            "fit_id": "p30",
            "command_x_m_s": 0.077,
            "seed": basis["seed"],
            "duration_s": 12.0,
        },
        "wrapped_failure": {
            "trace": wrapped_trace,
            "samples": failed_cell["behavior"]["samples"],
            "termination_reason": failed_cell["behavior"][
                "termination_reason"
            ],
            "intervention_events": intervention_events,
            "first_intervention_tick": intervention_events[0]["tick"],
            "intervention_count": len(intervention_events),
        },
        "unwrapped_policy": source,
        "fit": p30,
        "calibrator": basis["calibrator"],
        "reference_feature_table": basis["reference_feature_table"],
        "playground": basis["playground"],
        "support_handoff": basis["support_handoff"],
        "behavior_contract": basis["behavior_contract"],
        "protection_contract": basis["protection_contract"],
        "decision_rule": {
            "unwrapped_passes": (
                "Classify T28 margin clipping as causal for this cell and "
                "close T28 before choosing a new saturation mechanism."
            ),
            "unwrapped_fails": (
                "The transform is not a sufficient cause; retain T28 and "
                "continue read-only failure attribution."
            ),
            "no_result": (
                "Any provenance, handoff, readback, or trace-continuity "
                "failure has zero policy decision weight."
            ),
        },
        "frozen_inputs": {
            "t27_preregistration": receipt(T27_PREREG),
            "t28_transform_contract": receipt(T28_TRANSFORM),
            "t29_result": receipt(T29_RESULT),
            "runner": receipt(RUNNER),
            "worker": receipt(WORKER),
        },
        "checks": checks,
        "failed_checks": failed_checks,
        "authority": {
            "execute_one_unwrapped_cpu_cell": not failed_checks,
            "training": False,
            "colab": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    payload["preregistered_contract_sha256"] = canonical_sha256(payload)
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# T30 T28 margin-causality preregistration",
                "",
                f"status: `{payload['status']}`",
                "",
                "Run exactly one CPU cell with the original unwrapped T23 "
                "final policy: P30, joint-friction loss 0.9×, x=.077, the "
                "same seed and support handoff as T29.",
                "",
                "If it passes, T28 caused the fall and is closed. If it also "
                "fails, T28 is not a sufficient cause and failure attribution "
                "continues. No training or hardware work is authorized.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"failed_checks={failed_checks}")
    print(f"interventions={len(intervention_events)}")
    print(
        "contract_sha256="
        f"{payload['preregistered_contract_sha256']}"
    )
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed_checks else 1


if __name__ == "__main__":
    raise SystemExit(main())
