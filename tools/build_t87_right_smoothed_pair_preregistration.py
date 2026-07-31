#!/usr/bin/env python3
"""Attribute T86 and freeze one exact right-smoothed adapter-pair transform."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T86 = ANALYSIS / "t86_rolling_midpoint_r2_result.json"
T84 = ANALYSIS / "t84_t78_rolling_midpoint_result.json"
RUNNER = ROOT / "tools" / "run_t87_right_smoothed_pair_transform.py"
BUILDER = ROOT / "tools" / Path(__file__).name
TEST = ROOT / "tests" / "test_t87_right_smoothed_pair.py"
OUTPUT = ANALYSIS / "t87_right_smoothed_pair_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T87_RIGHT_SMOOTHED_PAIR_PREREGISTRATION_20260728.md"
)
EXPECTED_INITIALIZERS = [
    "adapter_bias",
    "adapter_hidden_bias",
    "adapter_hidden_weight",
    "adapter_obs_weight",
    "adapter_weight",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


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


def cells(result: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "condition_id": block["condition_id"],
            "checkpoint_id": block["checkpoint_id"],
            "fit_id": block["fit_id"],
            **cell,
        }
        for block in result["blocks"]
        for cell in block["result"]["cells"]
    ]


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T87 prereg: {path}")
    t86 = json.loads(T86.read_text(encoding="utf-8"))
    t84 = json.loads(T84.read_text(encoding="utf-8"))
    rows = cells(t86)
    failed_rows = [row for row in rows if not row["cell_green"]]
    failure = failed_rows[0] if len(failed_rows) == 1 else {}
    paired_final = next(
        (
            row
            for row in rows
            if row["condition_id"] == "JOINT_FRICTIONLOSS_HI"
            and row["checkpoint_id"] == "T84_ROLLING_FINAL"
            and row["fit_id"] == "p30"
            and row["command_x_m_s"] == 0.08
        ),
        {},
    )
    behavior = failure.get("behavior") or {}
    protection = failure.get("protection") or {}
    sources = {
        "t86_result": T86,
        "t84_result": T84,
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
    }
    checks = {
        "t86_stopped_at_exact_condition_four": (
            t86["status"] == "HOLD_T86_ROLLING_MIDPOINT_R2"
            and t86["summary"]["completed_conditions"] == 4
            and t86["summary"]["completed_cells"] == 64
            and t86["summary"]["green_cells"] == 63
            and t86["summary"]["first_failed_condition"]
            == "JOINT_FRICTIONLOSS_HI"
        ),
        "exactly_one_failed_cell": len(failed_rows) == 1,
        "failure_is_early_window_p30_x008": (
            failure.get("condition_id") == "JOINT_FRICTIONLOSS_HI"
            and failure.get("checkpoint_id") == "T84_ROLLING_HALF"
            and failure.get("fit_id") == "p30"
            and failure.get("command_x_m_s") == 0.08
        ),
        "failure_is_stability_not_quality_or_protection": (
            behavior.get("samples") == 479
            and behavior.get("termination_reason") == "fall_or_nan"
            and behavior.get("pitch_tracking_p95_rad", 1.0) < 0.2
            and behavior.get("action_saturation_pct") == 0.0
            and behavior.get("instant_rate_excess_rad_s") == 0.0
            and behavior.get("p95_rate_excess_rad_s") == 0.0
            and behavior.get("replacement_quality_pass") is True
            and failure.get("handoff", {}).get("all_checks_pass") is True
            and failure.get("override_readback_exact") is True
            and protection.get("duration_protection_pass") is True
            and protection.get(
                "maximum_full_measured_vector_excess_rad_s"
            )
            == 0.0
        ),
        "same_fit_final_window_x008_is_green": (
            paired_final.get("cell_green") is True
            and paired_final.get("behavior", {}).get("samples") == 600
            and paired_final.get("behavior", {}).get("termination_reason")
            == "duration_complete"
        ),
        "other_three_condition_four_blocks_green": (
            sum(
                block["result"]["block_green"]
                for block in t86["blocks"]
                if block["condition_id"] == "JOINT_FRICTIONLOSS_HI"
            )
            == 3
        ),
        "t84_pair_contract_green": (
            t84["status"] == "PASS_T84_T78_ROLLING_ADAPTER_MIDPOINTS"
            and t84["failed_checks"] == []
        ),
        "all_sources_present": all(path.is_file() for path in sources.values()),
        "zero_behavior_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t87_right_smoothed_pair_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T87_RIGHT_SMOOTHED_ADAPTER_PAIR"
            if not failed
            else "HOLD_T87_RIGHT_SMOOTHED_ADAPTER_PAIR_PREREGISTRATION"
        ),
        "question": (
            "Does one additional exact right-looking midpoint pass over "
            "the two T84 rolling exports produce a valid persistent pair "
            "without training or coefficient search?"
        ),
        "attribution": {
            "classification": (
                "EARLY_ROLLING_WINDOW_FIT_SPECIFIC_STABILITY_GAP"
            ),
            "passed_before_stop": {
                "conditions": 3,
                "cells": 48,
            },
            "failed_condition": {
                "condition_index": 4,
                "condition_id": "JOINT_FRICTIONLOSS_HI",
                "green_cells": 15,
                "cells": 16,
            },
            "only_failed_cell": {
                "checkpoint_id": failure.get("checkpoint_id"),
                "fit_id": failure.get("fit_id"),
                "command_x_m_s": failure.get("command_x_m_s"),
                "samples": behavior.get("samples"),
                "termination_reason": behavior.get("termination_reason"),
                "pitch_tracking_p95_rad": behavior.get(
                    "pitch_tracking_p95_rad"
                ),
                "action_saturation_pct": behavior.get(
                    "action_saturation_pct"
                ),
                "instant_rate_excess_rad_s": behavior.get(
                    "instant_rate_excess_rad_s"
                ),
                "worst_overcurrent_run_ticks": protection.get(
                    "worst_strict_overcurrent_run_ticks"
                ),
                "worst_overload_run_ticks": protection.get(
                    "worst_strict_overload_run_ticks"
                ),
            },
            "same_fit_later_window_x008_green": bool(
                paired_final.get("cell_green")
            ),
        },
        "transform": {
            "series": [
                "T84_ROLLING_HALF",
                "T84_ROLLING_FINAL",
            ],
            "rule": (
                "z[i] = 0.5 * (y[i] + y[min(i+1, N-1)])"
            ),
            "right_smoothed_half": (
                "mean(T84_ROLLING_HALF, T84_ROLLING_FINAL)"
            ),
            "right_smoothed_final": (
                "mean(T84_ROLLING_FINAL, T84_ROLLING_FINAL)"
            ),
            "terminal_edge_rule": "replicate_last",
            "initializers": EXPECTED_INITIALIZERS,
            "formula": (
                "float32((float64(earlier) + float64(later)) * 0.5)"
            ),
            "coefficient": 0.5,
            "coefficient_sweep": False,
            "all_other_initializers_bit_exact": True,
            "final_raw_and_deployment_byte_exact_to_t84": True,
        },
        "persistence_contract": {
            "exports": [
                "right_smoothed_half",
                "right_smoothed_final",
            ],
            "same_filter_with_terminal_edge_replication": True,
            "both_required": True,
            "no_checkpoint_selection": True,
        },
        "sources": {
            name: receipt(path) for name, path in sources.items()
        },
        "checks": checks,
        "failed_checks": failed,
        "decision_rule": {
            "pass": (
                "The new half is the exact five-adapter midpoint of both "
                "T84 rolling exports; the terminal final is byte-exact to "
                "T84 rolling-final; all deployment contracts pass."
            ),
            "pass_decision": (
                "EARN_T88_RIGHT_SMOOTHED_PAIR_TARGETED_BEHAVIOR_"
                "PREREGISTRATION"
            ),
            "fail_decision": "CLOSE_RIGHT_SMOOTHED_ADAPTER_PAIR",
            "no_retry": True,
        },
        "execution_now": {
            "onnx_graphs_built": 0,
            "formal_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_one_cpu_graph_transform": not failed,
            "behavior_preregistration": False,
            "behavior_execution": False,
            "training": False,
            "colab": False,
            "candidate_promotion": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T87 right-smoothed adapter pair preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- T86: `63/64`, one half/p30/x=.08 fall at 479 ticks",
                "- Same-fit rolling-final/x=.08: `GREEN`",
                "- Rule: exact right-looking 0.5 midpoint; terminal replicate",
                "- Search/training/Colab/Gate5/robot: `0/0/0/0/0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
