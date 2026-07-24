#!/usr/bin/env python3
"""Preregister the V124 S0 float32 ctrl/applied closure correction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v124_predictive_torque_s0_s2_preregistration.json"
OUTPUT = ANALYSIS / "winner_v124_s0_ctrl_tolerance_amendment.json"
MARKDOWN = ANALYSIS / "WINNER_V124_S0_CTRL_TOLERANCE_AMENDMENT_20260724.md"
EXPECTED = {
    "preregistration": (
        "61364c864ef3bf97d13df92a79645140a3918ecc8923f52810dd360f16b8042f"
    ),
    "invalid_firstpass": (
        "e7e62c3d84e18cd38b1ab27d67c43897dd4ad1a5371a3359f3c0fc03980d4f81"
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--invalid-firstpass", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite amendment: {path}")
    firstpass = args.invalid_firstpass.resolve()
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    first = json.loads(firstpass.read_text(encoding="utf-8"))
    hashes = {
        "preregistration": sha256(PREREG),
        "invalid_firstpass": sha256(firstpass),
    }
    s0_checks = first["s0"]["checks"]
    other_s0 = {
        name: passed
        for name, passed in s0_checks.items()
        if name != "ctrl_equals_applied_target"
    }
    measured = float(first["s0"]["summary"]["ctrl_applied_max_abs_error_rad"])
    prereg_tolerance = float(
        prereg["s0_model_closure"]["bridge_trace_max_abs_error_rad_max"]
    )
    checks = {
        "input_hashes_exact": hashes == EXPECTED,
        "preregistration_was_green": (
            prereg.get("status")
            == "PREREGISTERED_WINNER_V124_PREDICTIVE_TORQUE_S0_S2"
            and prereg.get("failed_checks") == []
        ),
        "only_s0_ctrl_check_failed": (
            s0_checks.get("ctrl_equals_applied_target") is False
            and all(other_s0.values())
        ),
        "s1_passed_unchanged": first["s1"]["pass"] is True,
        "s2_failed_unchanged": first["s2"]["pass"] is False,
        "measured_ctrl_error_inside_existing_preregistered_tolerance": (
            measured <= prereg_tolerance
        ),
        "firstpass_wrote_no_behavior_or_training": (
            first["execution"]["behavior_rollouts"] == 0
            and first["execution"]["training_steps"] == 0
            and first["execution"]["colab_compute_units"] == 0
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    value = {
        "schema_version": "winner_v124.s0_ctrl_tolerance_amendment.v1",
        "status": (
            "PREREGISTERED_WINNER_V124_S0_CTRL_TOLERANCE_AMENDMENT"
            if not failed
            else "HOLD_WINNER_V124_S0_CTRL_TOLERANCE_AMENDMENT"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": hashes,
        "defect": (
            "The implementation added an unpreregistered 1e-12 ctrl/applied "
            "float comparison. Both values represent the same applied target, "
            "but one trace path is float32; the observed 5.9603646e-8 rad "
            "difference is already inside the preregistered 6e-8 bridge "
            "closure tolerance."
        ),
        "correction": {
            "ctrl_applied_tolerance_rad": prereg_tolerance,
            "source": (
                "reuse the already preregistered bridge trace closure "
                "tolerance; introduce no new or result-selected threshold"
            ),
            "measured_firstpass_error_rad": measured,
            "all_other_equations_thresholds_inputs_and_decisions_unchanged": True,
        },
        "decision": (
            "AUTHORIZE_ONE_EXACT_S0_S2_RERUN_WITH_CTRL_TOLERANCE_CORRECTION"
            if not failed
            else "HOLD_WITHOUT_RERUN"
        ),
        "execution_now": {
            "training_steps": 0,
            "behavior_rollouts": 0,
            "colab_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_exact_s0_s2_rerun_authorized": not failed,
            "s3_behavior_screen_authorized": False,
            "hosted_training_authorized": False,
            "gate5_authorized": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner-v124 S0 ctrl-tolerance amendment\n\n"
        f"Status: `{value['status']}`\n\n"
        "The first pass added an unpreregistered `1e-12` comparison between "
        "two float representations of the same applied target. The measured "
        "difference is inside the already frozen `6e-8 rad` bridge closure "
        "tolerance. One exact rerun may reuse that existing tolerance; every "
        "other equation, threshold, input, and decision remains unchanged.\n\n"
        "No rollout, training, Colab, RDK-X5, robot, torque, or motion is "
        "authorized.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
