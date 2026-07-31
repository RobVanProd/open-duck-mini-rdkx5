#!/usr/bin/env python3
"""Correct T94's scalar-versus-expanded-vector home-offset readback report."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
RESULT = ANALYSIS / "t94_r2_calibration_manifold_result.json"
PREREG = ANALYSIS / "t94_r2_calibration_manifold_preregistration_v3.json"
OUTPUT = ANALYSIS / "t94_home_offset_reporting_correction.json"
MARKDOWN = ANALYSIS / "T94_HOME_OFFSET_REPORTING_CORRECTION_20260728.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: dict[str, Any], ignored: str) -> str:
    payload = dict(value)
    payload.pop(ignored, None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite correction: {path}")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    expected_by_id = {
        condition["id"]: next(iter(condition["override"].values()))
        for condition in prereg["conditions"]
        if condition["id"].startswith("HOME_JOINT_OFFSET_")
    }
    corrections = []
    for cell in result["cells"]:
        configuration_id = cell["configuration_id"]
        if configuration_id not in expected_by_id:
            continue
        evaluation_path = Path(cell["evaluation"]["path"])
        if sha256(evaluation_path) != cell["evaluation"]["sha256"]:
            raise ValueError(f"evaluation changed: {evaluation_path}")
        evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
        dynamics = evaluation["runs"][0]["dynamics_override"]
        readback = dynamics["readback"]
        expected = float(expected_by_id[configuration_id])
        expected_vector = np.full(14, expected, dtype=np.float64)
        value = np.asarray(dynamics["value"], dtype=np.float64)
        before = np.asarray(readback["before"], dtype=np.float64)
        after = np.asarray(readback["after"], dtype=np.float64)
        offset = np.asarray(readback["offset"], dtype=np.float64)
        home_before = np.asarray(
            readback["home_init_before"], dtype=np.float64
        )
        home_after = np.asarray(
            readback["home_init_after"], dtype=np.float64
        )
        reporting_checks = {
            "enabled": dynamics["enabled"] is True,
            "key_exact": dynamics["key"] == "joint_qpos0_offset_rad",
            "expanded_value_exact": bool(
                np.array_equal(value, expected_vector)
            ),
            "readback_before_exact": bool(
                np.array_equal(before, np.zeros(14, dtype=np.float64))
            ),
            "readback_after_exact": bool(
                np.array_equal(after, expected_vector)
            ),
            "readback_offset_exact": bool(
                np.array_equal(offset, expected_vector)
            ),
            "home_initialization_delta_exact": bool(
                np.allclose(
                    home_after - home_before,
                    expected_vector,
                    rtol=0.0,
                    atol=1e-12,
                )
            ),
            "all_other_t94_cell_checks_pass": all(
                passed
                for name, passed in cell["checks"].items()
                if name != "dynamics_override_value_exact"
            ),
        }
        corrections.append(
            {
                "configuration_id": configuration_id,
                "fit_id": cell["fit_id"],
                "expected_scalar_rad": expected,
                "reported_expanded_vector_rad": value.tolist(),
                "checks": reporting_checks,
                "corrected_cell_pass": all(reporting_checks.values()),
                "evaluation": cell["evaluation"],
            }
        )
    correction = {
        "status": "CORRECTED_T94_HOME_OFFSET_REPORTING",
        "scope": (
            "Reporting-only correction. No calibration block, policy, "
            "simulation, training, or hardware execution was repeated."
        ),
        "source_result": {
            "path": str(RESULT),
            "sha256": sha256(RESULT),
            "status": result["status"],
            "decision": result["decision"],
        },
        "cause": (
            "T94 compared the evaluator's expanded 14-joint offset vector "
            "directly with the preregistered scalar shorthand."
        ),
        "corrections": corrections,
        "corrected_summary": {
            **result["summary"],
            "passing_calibration_cells": (
                result["summary"]["passing_calibration_cells"]
                + sum(item["corrected_cell_pass"] for item in corrections)
            ),
        },
        "unchanged_routing_failures": {
            "fit_correct_cells": result["summary"]["fit_correct_cells"],
            "fit_total_cells": result["summary"]["cells"],
            "negative_com_false_positives": result["summary"][
                "negative_com_false_positives"
            ],
        },
        "decision": result["decision"],
        "classification": result["classification"],
        "authority": result["authority"],
    }
    if len(corrections) != 4 or not all(
        item["corrected_cell_pass"] for item in corrections
    ):
        raise RuntimeError("T94 reporting correction did not close all cells")
    if correction["corrected_summary"]["passing_calibration_cells"] != 40:
        raise RuntimeError("corrected calibration count is not 40")
    correction["correction_sha256"] = canonical_sha256(
        correction, "correction_sha256"
    )
    OUTPUT.write_text(
        json.dumps(correction, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T94 home-offset reporting correction",
                "",
                f"Status: `{correction['status']}`",
                "",
                "The four apparent home-offset calibration failures were "
                "reporting-only. The evaluator correctly expanded the "
                "preregistered scalar `±0.03 rad` shorthand to all 14 joints, "
                "and every readback and home-initialization delta is exact.",
                "",
                "- Corrected safe calibration cells: **40/40**",
                "- Fit classifications: **23/40**",
                "- Negative-COM false positives: **2**",
                f"- Decision remains: `{correction['decision']}`",
                "",
                "No simulation block was rerun and no hosted compute or "
                "hardware was used. Discrete calibration-routed experts "
                "remain closed because calibration safety was not the routing "
                "failure.",
                "",
                f"Correction SHA-256: `{correction['correction_sha256']}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(correction["status"])
    print(correction["correction_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
