#!/usr/bin/env python3
"""Import and summarize the completed winner-v5 support-recovery result."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "outputs/analysis/winner_v5_automatic_support_recovery_preregistration.json"
OUTPUT = ROOT / "outputs/analysis/winner_v5_automatic_support_recovery_result.json"
MARKDOWN = ROOT / "outputs/analysis/WINNER_V5_AUTOMATIC_SUPPORT_RECOVERY_RESULT_20260720.md"
EXPECTED_CONTRACT_SHA256 = "0e9e1d78444ce2f9d5e3d8c14d4f5805369e39ac645ad5b097b0cf7c4d3a2276"
EXPECTED_RESULT_SHA256 = "f36855923f91f683ebe691b0726e1231c04c5036ab7dff27836534ade7b0d17a"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def nearest_opposing_p30(cells: list[dict[str, Any]]) -> dict[str, Any]:
    candidates = [
        cell for cell in cells
        if cell["sensor_case"] == "NOMINAL_QUANTIZED"
        and cell["fit"] == "fit_p30"
        and cell["triggered"]
    ]
    passing = [cell for cell in candidates if cell["pass"]]
    failing = [cell for cell in candidates if not cell["pass"]]
    best: tuple[float, dict[str, Any], dict[str, Any]] | None = None
    for accepted in passing:
        for rejected in failing:
            distance = float(
                np.linalg.norm(
                    np.asarray(accepted["decision_gyro_rad_s_xy"], dtype=float)
                    - np.asarray(rejected["decision_gyro_rad_s_xy"], dtype=float)
                )
            )
            if best is None or distance < best[0]:
                best = (distance, accepted, rejected)
    if best is None:
        raise ValueError("missing opposing P30 trigger outcomes")
    return {
        "euclidean_distance_rad_s": best[0],
        "passing_configuration_id": best[1]["configuration_id"],
        "passing_gyro_rad_s_xy": best[1]["decision_gyro_rad_s_xy"],
        "failing_configuration_id": best[2]["configuration_id"],
        "failing_gyro_rad_s_xy": best[2]["decision_gyro_rad_s_xy"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("result", type=Path)
    args = parser.parse_args()
    if sha256(CONTRACT) != EXPECTED_CONTRACT_SHA256:
        raise ValueError("winner-v5 contract hash mismatch")
    if sha256(args.result) != EXPECTED_RESULT_SHA256:
        raise ValueError("winner-v5 result hash mismatch")
    payload = json.loads(args.result.read_text(encoding="utf-8"))
    if payload["status"] != "HOLD_WINNER_V5_AUTOMATIC_SUPPORT_RECOVERY":
        raise ValueError("winner-v5 result is not the completed hold")
    if payload["contract"]["sha256"] != EXPECTED_CONTRACT_SHA256:
        raise ValueError("result references a different contract")
    if payload["counts"] != {
        "configurations": 96, "cells": 960, "triggered": 290,
        "passed": 784, "failed": 176,
    }:
        raise ValueError(f"unexpected result counts: {payload['counts']}")

    failures = [cell for cell in payload["cells"] if not cell["pass"]]
    collapsed = [
        cell for cell in failures
        if not cell["checks"]["minimum_base_z"]
        or not cell["checks"]["maximum_abs_tilt"]
    ]
    contact_only = [
        cell for cell in failures
        if cell["checks"]["minimum_base_z"]
        and cell["checks"]["maximum_abs_tilt"]
        and not cell["checks"]["two_foot_contact"]
    ]
    nominal = [cell for cell in payload["cells"] if cell["sensor_case"] == "NOMINAL_QUANTIZED"]
    by_configuration: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for cell in nominal:
        by_configuration[cell["configuration_id"]][cell["fit"]] = cell
    fit_pairs = Counter(
        (
            rows["fit_p30"]["pass"],
            rows["fit_p31_34"]["pass"],
        )
        for rows in by_configuration.values()
    )
    attribution = {
        "all_failures_were_triggered": all(cell["triggered"] for cell in failures),
        "failed_cells": len(failures),
        "collapsed_cells": len(collapsed),
        "contact_only_cells": len(contact_only),
        "unique_failed_configurations": len(
            {cell["configuration_id"] for cell in failures}
        ),
        "nominal_configuration_fit_outcomes": {
            "both_pass": fit_pairs[(True, True)],
            "both_fail": fit_pairs[(False, False)],
            "p30_pass_p31_fail": fit_pairs[(True, False)],
            "p30_fail_p31_pass": fit_pairs[(False, True)],
        },
        "nearest_opposing_p30_trigger_pair": nearest_opposing_p30(payload["cells"]),
        "finding": (
            "The trigger did not miss any failed cell. The fixed recovery target itself "
            "is non-universal: every failure followed a trigger, 58 cells collapsed, and "
            "nominal outcomes split between the two measured actuator fits in 12 of 96 "
            "configurations. Opposing P30 outcomes occur only one native gyro count apart."
        ),
    }
    payload["failure_attribution"] = attribution
    payload["decision"] = "CLOSE_ONE_SHOT_IMU_THRESHOLD_FIXED_RECOVERY"
    payload["next_allowed_question"] = (
        "A new prospective contract may test dynamic state feedback that adapts throughout "
        "support recovery. Threshold or fixed-target retuning is forbidden."
    )
    # Preserve the completed raw result separately by hash, while the repository copy
    # appends only deterministic read-only attribution.
    payload["raw_result_sha256"] = EXPECTED_RESULT_SHA256
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    imported_sha = sha256(OUTPUT)
    nearest = attribution["nearest_opposing_p30_trigger_pair"]
    MARKDOWN.write_text(
        "# Winner-v5 Automatic Support-Recovery Result\n\n"
        f"status: `{payload['status']}`\n\n"
        f"raw result SHA-256: `{EXPECTED_RESULT_SHA256}`\n\n"
        f"attributed repository result SHA-256: `{imported_sha}`\n\n"
        "The frozen 960-cell gate failed: 784 cells passed and 176 failed across "
        "28 configurations. All 176 failures were triggered recoveries; the rule "
        "did not fail because it overlooked an unstable case. Fifty-eight cells "
        "collapsed, while 118 remained upright but violated uninterrupted two-foot "
        "support. The fixed recovery target is therefore non-universal.\n\n"
        f"Under nominal quantized input, 73 configurations pass both actuator fits, "
        f"11 fail both, 8 pass only P30, and 4 pass only P31/34. The nearest P30 "
        f"pass/fail trigger pair is only `{nearest['euclidean_distance_rad_s']:.12f}` "
        "rad/s apart—one BNO055 gyro count in this contract.\n\n"
        "Decision: close the one-shot IMU threshold plus fixed recovery target. Do "
        "not retune it. A later prospective study may test dynamic state feedback "
        "that continues adapting after the first sample; no training, runtime, or "
        "robot action is authorized by this result.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": payload["status"], "decision": payload["decision"], "sha256": imported_sha}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
