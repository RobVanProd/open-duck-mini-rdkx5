#!/usr/bin/env python3
"""Run T214B's saved-trace predicted-tilt-box source transfer."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
sys.path.insert(0, str(ROOT / "tools"))
from run_t136_static_calibration_router_transform import (  # noqa: E402
    canonical_sha256,
    verify,
)


PREREG = (
    ANALYSIS
    / "t214b_axis_complete_tilt_source_transfer_preregistration.json"
)
RESULT = ANALYSIS / "t214b_axis_complete_tilt_source_transfer_result.json"
MARKDOWN = (
    ANALYSIS
    / "T214B_AXIS_COMPLETE_TILT_SOURCE_TRANSFER_RESULT_20260730.md"
)


def label(item: dict[str, Any]) -> str:
    checkpoint = (
        "half" if item["checkpoint_id"].endswith("HALF") else "final"
    )
    command = f"{float(item['command_x_m_s']):.3f}".replace(".", "p")
    return f"{item['family']}_{checkpoint}_{item['fit_id']}_x{command}"


def load_rows(item: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [
        json.loads(line)
        for line in Path(item["trace"]["path"]).read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]
    if len(rows) != int(item["samples"]):
        raise RuntimeError(f"trace row count changed: {item}")
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T214B result")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T214B execution requires clean worktree")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T214B_AXIS_COMPLETE_TILT_SOURCE_TRANSFER"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T214B preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, f"frozen_inputs.{name}")
    for index, item in enumerate(prereg["traces"]):
        verify(item["trace"], f"traces[{index}]")

    started = time.time()
    horizon = float(prereg["analysis"]["prediction_horizon_s"])
    metadata = {label(item): item for item in prereg["traces"]}
    if len(metadata) != len(prereg["traces"]):
        raise RuntimeError("T214B trace labels are not unique")
    rows_by_trace = {
        label(item): load_rows(item) for item in prereg["traces"]
    }
    axes: dict[str, dict[str, np.ndarray]] = {}
    contiguous: dict[str, bool] = {}
    for name, rows in rows_by_trace.items():
        ticks = np.asarray([row["tick"] for row in rows], np.int64)
        roll = np.asarray(
            [row["body_roll_rad"] for row in rows], np.float64
        )
        roll_rate = np.asarray(
            [row["body_roll_rate_rad_s"] for row in rows], np.float64
        )
        pitch = np.asarray(
            [row["body_pitch_rad"] for row in rows], np.float64
        )
        pitch_rate = np.asarray(
            [row["body_pitch_rate_rad_s"] for row in rows], np.float64
        )
        axes[name] = {
            "roll": np.abs(roll + horizon * roll_rate),
            "pitch": np.abs(pitch + horizon * pitch_rate),
        }
        contiguous[name] = bool(
            np.array_equal(ticks, np.arange(len(rows)))
        )

    passing = [
        name for name, item in metadata.items() if item["cell_green"]
    ]
    failures = [
        name for name, item in metadata.items() if not item["cell_green"]
    ]
    pass_maximum = {
        axis: max(float(np.max(axes[name][axis])) for name in passing)
        for axis in ("roll", "pitch")
    }
    envelope = {
        axis: float(np.nextafter(pass_maximum[axis], np.inf))
        for axis in ("roll", "pitch")
    }
    summaries: dict[str, dict[str, Any]] = {}
    for name, risks in axes.items():
        normalized = {
            axis: risks[axis] / envelope[axis]
            for axis in ("roll", "pitch")
        }
        score = np.maximum(normalized["roll"], normalized["pitch"])
        excess = np.maximum(0.0, score - 1.0)
        indices = np.flatnonzero(excess > 0.0)
        dominant = np.where(
            normalized["pitch"] > normalized["roll"],
            "pitch",
            "roll",
        )
        dominant_counts = {
            axis: int(np.sum(dominant[indices] == axis))
            for axis in ("roll", "pitch")
        }
        summaries[name] = {
            "family": metadata[name]["family"],
            "cell_green": bool(metadata[name]["cell_green"]),
            "rows": len(score),
            "maximum_roll_risk_rad": float(np.max(risks["roll"])),
            "maximum_pitch_risk_rad": float(np.max(risks["pitch"])),
            "maximum_box_score": float(np.max(score)),
            "exceedance_rows": int(len(indices)),
            "first_exceedance_tick": (
                int(indices[0]) if len(indices) else None
            ),
            "lead_ticks_to_terminal": (
                int(len(score) - 1 - indices[0])
                if len(indices)
                else None
            ),
            "dominant_axis_counts": dominant_counts,
            "dominant_failure_axis": (
                max(dominant_counts, key=dominant_counts.get)
                if len(indices)
                else None
            ),
            "maximum_normalized_excess": float(np.max(excess)),
            "squared_excess_integral": float(np.sum(np.square(excess))),
        }

    rule = prereg["analysis"]["per_failure_rule"]
    per_failure = {
        name: (
            summaries[name]["exceedance_rows"]
            >= int(rule["minimum_exceedance_rows"])
            and summaries[name]["lead_ticks_to_terminal"] is not None
            and summaries[name]["lead_ticks_to_terminal"]
            >= int(rule["minimum_lead_ticks"])
            and summaries[name]["maximum_box_score"] > 1.0
        )
        for name in failures
    }
    dominant_failure_axes = {
        summaries[name]["dominant_failure_axis"] for name in failures
    }
    required_axes = set(
        prereg["analysis"]["required_dominant_axes_across_failures"]
    )
    separation = (
        all(summaries[name]["exceedance_rows"] == 0 for name in passing)
        and all(per_failure.values())
        and dominant_failure_axes == required_axes
    )
    checks = {
        "thirty_six_traces_thirty_three_passes_three_failures": (
            len(axes) == 36
            and len(passing) == 33
            and len(failures) == 3
        ),
        "all_row_counts_exact": all(
            len(rows_by_trace[name]) == int(metadata[name]["samples"])
            for name in axes
        ),
        "all_ticks_contiguous": all(contiguous.values()),
        "all_axis_risks_and_scores_finite": all(
            np.all(np.isfinite(risk))
            for item in axes.values()
            for risk in item.values()
        )
        and all(
            np.isfinite(row["maximum_box_score"])
            and np.isfinite(row["squared_excess_integral"])
            for row in summaries.values()
        ),
        "axis_envelopes_are_nextafter_pass_maxima": all(
            envelope[axis] > pass_maximum[axis]
            and envelope[axis]
            == np.nextafter(pass_maximum[axis], np.inf)
            for axis in ("roll", "pitch")
        ),
        "all_passes_have_zero_box_exceedance": all(
            summaries[name]["exceedance_rows"] == 0 for name in passing
        ),
        "all_three_failures_pass_frozen_rule": all(per_failure.values()),
        "known_failures_require_both_tilt_axes": (
            dominant_failure_axes == required_axes
        ),
        "candidate_cost_nonnegative": all(
            row["squared_excess_integral"] >= 0.0
            for row in summaries.values()
        ),
        "zero_simulator_optimizer_onnx_behavior_hosted_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    earned = not failed and separation
    decision = (
        prereg["decision_rule"][
            "all_failures_separable_and_both_axes_required"
        ]
        if earned
        else prereg["decision_rule"]["otherwise"]
    )
    basis_result: dict[str, Any] = {
        "schema_version": (
            "open_duck.t214b_axis_complete_tilt_source_transfer_result.v1"
        ),
        "status": (
            "PASS_T214B_AXIS_COMPLETE_TILT_SOURCE_TRANSFER"
            if not failed
            else "HOLD_T214B_AXIS_COMPLETE_TILT_SOURCE_TRANSFER"
        ),
        "classification": (
            "AXIS_COMPLETE_TILT_BOX_UNIFIES_ROLL_AND_PITCH_FALLS"
            if separation
            else "TILT_BOX_NOT_EARLY_DENSE_PASS_SEPARABLE"
        ),
        "decision": decision,
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "separation_rule_passed": separation,
        "prediction_horizon_s": horizon,
        "passing_maximum_rad": pass_maximum,
        "passing_envelope_rad": envelope,
        "dominant_failure_axes": sorted(dominant_failure_axes),
        "failure_rules": per_failure,
        "failure_summaries": {
            name: summaries[name] for name in failures
        },
        "trace_summaries": summaries,
        "prior_art_ruling": prereg["prior_art_ruling"],
        "execution": {
            "saved_trace_rows": sum(
                len(rows) for rows in rows_by_trace.values()
            ),
            "simulator_transitions": 0,
            "optimizer_steps": 0,
            "onnx_inferences": 0,
            "behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
            "wall_seconds": time.time() - started,
        },
        "authority": {
            "cpu_contract_preregistration": earned,
            "training": False,
            "colab": False,
            "behavior": False,
            "full_r2": False,
            "gate5": False,
            "robot_or_rdk": False,
        },
    }
    value = {
        **basis_result,
        "result_sha256": canonical_sha256(basis_result),
    }
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    failures_text = {
        name: {
            "first": summaries[name]["first_exceedance_tick"],
            "lead": summaries[name]["lead_ticks_to_terminal"],
            "rows": summaries[name]["exceedance_rows"],
            "axis": summaries[name]["dominant_failure_axis"],
        }
        for name in failures
    }
    MARKDOWN.write_text(
        "# T214B axis-complete predicted-tilt source-transfer result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Classification: `{value['classification']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Passing roll/pitch envelopes: "
        f"`{envelope['roll']:.9f}/{envelope['pitch']:.9f}` rad\n"
        f"- Failure first/lead/rows/axis: `{failures_text}`\n"
        "- Simulator / optimizer / ONNX / behavior / hosted / robot: "
        "`0/0/0/0/0/0`\n"
        f"- Result SHA-256: `{value['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"classification={value['classification']}")
    print(f"decision={value['decision']}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
