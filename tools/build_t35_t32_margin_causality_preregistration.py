#!/usr/bin/env python3
"""Freeze the one-cell T32 final action-margin causal A/B."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T28_TRANSFORM = ANALYSIS / "t28_t23_action_margin_transform_contract.json"
T33_RESULT = ANALYSIS / "t33_t32_postexport_result.json"
T34_PREREG = ANALYSIS / "t34_t32_nominal_matrix_preregistration.json"
T34_RESULT = ANALYSIS / "t34_t32_nominal_matrix_result.json"
RUNNER = ROOT / "tools" / "run_t35_t32_margin_causality.py"
WORKER = ROOT / "tools" / "evaluate_t30_t28_margin_causal_cell.py"
OUTPUT = ANALYSIS / "t35_t32_margin_causality_preregistration.json"
OUTPUT_MD = ANALYSIS / "T35_T32_MARGIN_CAUSALITY_PREREGISTRATION_20260727.md"


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
    transform = json.loads(T28_TRANSFORM.read_text(encoding="utf-8"))
    postexport = json.loads(T33_RESULT.read_text(encoding="utf-8"))
    prereg = json.loads(T34_PREREG.read_text(encoding="utf-8"))
    result = json.loads(T34_RESULT.read_text(encoding="utf-8"))
    failed = [
        (block, cell)
        for block in result["blocks"]
        for cell in block["result"]["cells"]
        if not cell["cell_green"]
    ]
    if len(failed) != 1:
        raise ValueError("T34 does not contain exactly one failed cell")
    failed_block, failed_cell = failed[0]
    manifest_path = Path(failed_block["manifest"]["path"])
    if sha256(manifest_path) != failed_block["manifest"]["sha256"]:
        raise ValueError("changed T34 failed-block manifest")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    wrapped_trace = next(
        item
        for item in manifest["traces"]
        if "x0.077_" in Path(item["path"]).name
    )
    wrapped_trace_path = Path(wrapped_trace["path"])
    if sha256(wrapped_trace_path) != wrapped_trace["sha256"]:
        raise ValueError("changed T34 failed trace")

    limit = np.float32(transform["stored_float32_limit_abs"])
    intervention_events: list[dict[str, Any]] = []
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

    deployment = postexport["deployments"]["2007040"]
    source = {
        **deployment["pre_margin_wrapped"],
        "checkpoint_id": "T32_PRE_MARGIN_FINAL",
        "step": 2007040,
    }
    fit = next(
        item for item in prereg["fits"] if item["fit_id"] == "p31_34"
    )
    checks = {
        "t34_is_frozen_15_of_16_hold": (
            result["status"] == "HOLD_T34_T32_NOMINAL_MATRIX"
            and result["condition"]["green_cells"] == 15
        ),
        "failed_cell_is_exact_target": (
            failed_block["checkpoint_id"] == "T32_MARGIN_FINAL"
            and failed_block["fit_id"] == "p31_34"
            and failed_block["condition_id"] == "FLOOR_FRICTION_HI"
            and float(failed_cell["command_x_m_s"]) == 0.077
            and failed_cell["behavior"]["samples"] == 494
        ),
        "failed_cell_is_behavior_only": (
            not failed_cell["behavior"]["emergence_pass"]
            and failed_cell["behavior"]["replacement_quality_pass"]
            and failed_cell["protection"]["duration_protection_pass"]
            and failed_cell["handoff"]["all_checks_pass"]
            and failed_cell["override_readback_exact"]
        ),
        "pre_margin_graph_is_exact_final_export": (
            source["sha256"]
            == deployment["pre_margin_wrapped"]["sha256"]
            and Path(source["path"]).is_file()
            and sha256(Path(source["path"])) == source["sha256"]
        ),
        "strict_margin_is_frozen": (
            float(limit)
            < float(transform["saturation_observation_threshold_abs"])
        ),
        "runner_and_worker_present": RUNNER.is_file() and WORKER.is_file(),
    }
    failed_checks = [name for name, passed in checks.items() if not passed]
    payload: dict[str, Any] = {
        "schema_version": (
            "open_duck.t35_t32_margin_causality_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T35_T32_MARGIN_CAUSAL_AB"
            if not failed_checks
            else "HOLD_T35_T32_MARGIN_CAUSALITY_PREREGISTRATION"
        ),
        "question": (
            "Did the final strict 0.98 action-margin clip cause T34's sole "
            "late failure, or does the otherwise identical pre-margin T32 "
            "final graph also fail the same P31/34 x=.077 cell?"
        ),
        "cell": {
            "condition": prereg["conditions"][0],
            "checkpoint_id": "T32_PRE_MARGIN_FINAL",
            "fit_id": "p31_34",
            "command_x_m_s": 0.077,
            "seed": prereg["seed"],
            "duration_s": 12.0,
        },
        "wrapped_failure": {
            "trace": wrapped_trace,
            "samples": failed_cell["behavior"]["samples"],
            "termination_reason": failed_cell["behavior"][
                "termination_reason"
            ],
            "intervention_events": intervention_events,
            "intervention_count": len(intervention_events),
            "first_intervention_tick": (
                intervention_events[0]["tick"]
                if intervention_events
                else None
            ),
        },
        "pre_margin_policy": source,
        "fit": fit,
        "calibrator": prereg["calibrator"],
        "reference_feature_table": prereg["reference_feature_table"],
        "playground": prereg["playground"],
        "support_handoff": prereg["support_handoff"],
        "behavior_contract": prereg["behavior_contract"],
        "protection_contract": prereg["protection_contract"],
        "margin": {
            "stored_float32_limit_abs": float(limit),
            "saturation_observation_threshold_abs": float(
                transform["saturation_observation_threshold_abs"]
            ),
        },
        "decision_rule": {
            "no_wrapped_intervention": (
                "Attribute the failure to trained actor/state drift without "
                "a proximate deployment-margin intervention; execute no new "
                "behavior cell."
            ),
            "pre_margin_passes": (
                "The strict deployment margin is causal for the late fall. "
                "Keep T32 closed and do not repeat a hard postexport margin."
            ),
            "pre_margin_fails": (
                "The strict deployment margin is not a sufficient cause. "
                "Attribute the hold to continued-training actor/state drift "
                "and require a new persistence-preserving mechanism."
            ),
            "invalid": (
                "Any provenance, pre-intervention equality, handoff, "
                "readback, or trace-continuity failure has zero decision "
                "weight."
            ),
            "no_training_or_retry": True,
        },
        "frozen_inputs": {
            "t28_transform": receipt(T28_TRANSFORM),
            "t33_postexport_result": receipt(T33_RESULT),
            "t34_preregistration": receipt(T34_PREREG),
            "t34_result": receipt(T34_RESULT),
            "runner": receipt(RUNNER),
            "worker": receipt(WORKER),
        },
        "checks": checks,
        "failed_checks": failed_checks,
        "authority": {
            "execute_one_pre_margin_cpu_cell": (
                not failed_checks and bool(intervention_events)
            ),
            "read_only_trace_attribution": not failed_checks,
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
                "# T35 T32 margin-causality preregistration",
                "",
                f"status: `{payload['status']}`",
                "",
                (
                    "- wrapped intervention events before/through failure: "
                    f"`{len(intervention_events)}`"
                ),
                (
                    "- first wrapped intervention tick: "
                    f"`{payload['wrapped_failure']['first_intervention_tick']}`"
                ),
                "",
                (
                    "If the margin never intervened, no new cell runs. "
                    "Otherwise run exactly the failed final/P31-34/x=.077 "
                    "cell with the frozen pre-margin graph."
                ),
                "",
                (
                    "No training, hosted compute, Gate 5, RDK-X5, robot, "
                    "torque, or motion is authorized."
                ),
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"failed_checks={failed_checks}")
    print(f"interventions={len(intervention_events)}")
    print(
        "first_intervention_tick="
        f"{payload['wrapped_failure']['first_intervention_tick']}"
    )
    print(
        "contract_sha256="
        f"{payload['preregistered_contract_sha256']}"
    )
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed_checks else 1


if __name__ == "__main__":
    raise SystemExit(main())
