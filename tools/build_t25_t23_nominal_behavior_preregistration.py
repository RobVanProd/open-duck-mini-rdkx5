#!/usr/bin/env python3
"""Preregister T23's unchanged 16-cell nominal physical gate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
TRANSFORM = ANALYSIS / "t24_t23_postexport_result.json"
BASE = ANALYSIS / "winner_v110_pitch_guard_behavior_preregistration.json"
PLAYGROUND_MANIFEST = Path(
    "D:/CodexProjects/Open_Duck_Playground-composed-t19-v6/"
    "T19_COMPOSED_SOURCE_MANIFEST.json"
)
OUTPUT = ANALYSIS / "t25_t23_nominal_behavior_preregistration.json"
MARKDOWN = ANALYSIS / "T25_T23_NOMINAL_BEHAVIOR_PREREGISTRATION_20260726.md"
EXPECTED_TRANSFORM_SHA256 = (
    "accb2027b05b1d861f34d7844a81626eac5706887bef306a7f8858dc379604a1"
)
EXPECTED_BASE_SHA256 = (
    "7698a551fa88cf1b0ca09503f383242e8735ce30436c189876bf4bde4b11b6d0"
)
EXPECTED_PLAYGROUND_MANIFEST_SHA256 = (
    "d7c9b615c32f0e2c8434e958a900cc38485c0db6fea107b6115a69bbd2122a77"
)
SOURCE_PATHS = (
    "tools/run_t25_t23_nominal_behavior.py",
    "tools/run_winner_v110_pitch_guard_behavior.py",
    "tools/run_winner_v109_recurrent_source_screen.py",
    "tools/closed_loop_sim_eval.py",
    "tools/run_winner_v3_variable_configuration_behavior.py",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy-root", type=Path, required=True)
    args = parser.parse_args()
    policy_root = args.policy_root.resolve()
    for path in (OUTPUT, MARKDOWN, policy_root):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T25: {path}")
    transform = json.loads(TRANSFORM.read_text(encoding="utf-8"))
    base = json.loads(BASE.read_text(encoding="utf-8"))
    manifest = json.loads(
        PLAYGROUND_MANIFEST.read_text(encoding="utf-8")
    )
    policy_root.mkdir(parents=True)
    specs = (
        (1_003_520, "T23_SUPPORT_HALF", "T23_SUPPORT_1003520.onnx"),
        (2_007_040, "T23_SUPPORT_FINAL", "T23_SUPPORT_2007040.onnx"),
    )
    policies = []
    for step, identifier, filename in specs:
        source = Path(
            transform["deployments"][str(step)]["wrapped"]["path"]
        )
        expected = transform["deployments"][str(step)]["wrapped"]
        destination = policy_root / filename
        if (
            source.stat().st_size != expected["bytes"]
            or sha256(source) != expected["sha256"]
        ):
            raise ValueError(f"T25 transformed policy changed: {step}")
        shutil.copy2(source, destination)
        policies.append(
            {
                "id": identifier,
                "step": step,
                "filename": filename,
                "path": str(destination),
                "sha256": sha256(destination),
                "bytes": destination.stat().st_size,
            }
        )
    playground = PLAYGROUND_MANIFEST.parent
    composed_source_exact = all(
        sha256(playground / relative) == expected
        for relative, expected in manifest["final_python_hashes"].items()
    )
    source_hashes = {
        name: sha256(ROOT / name) for name in SOURCE_PATHS
    }
    checks = {
        "t24_transform_exact_green": (
            sha256(TRANSFORM) == EXPECTED_TRANSFORM_SHA256
            and transform.get("status")
            == "PASS_T24_T23_POSTEXPORT_TRANSFORM"
            and transform.get("failed_checks") == []
            and transform.get("decision")
            == "EARN_T24_NOMINAL_MATRIX_PREREGISTRATION"
        ),
        "base_gate_exact": (
            sha256(BASE) == EXPECTED_BASE_SHA256
            and base.get("status")
            == "PREREGISTERED_WINNER_V110_PITCH_GUARD_BEHAVIOR"
        ),
        "playground_manifest_exact": (
            sha256(PLAYGROUND_MANIFEST)
            == EXPECTED_PLAYGROUND_MANIFEST_SHA256
            and composed_source_exact
        ),
        "two_postupdate_policy_files_exact": len(policies) == 2
        and all(
            (policy_root / row["filename"]).stat().st_size == row["bytes"]
            and sha256(policy_root / row["filename"]) == row["sha256"]
            for row in policies
        ),
        "both_postupdate_checkpoints_included": {
            row["step"] for row in policies
        }
        == {1_003_520, 2_007_040},
        "evaluator_sources_frozen": len(source_hashes)
        == len(SOURCE_PATHS),
        "manufacturer_gate_unchanged": True,
        "training_steps_zero": True,
        "robot_or_rdk_access_zero": True,
    }
    checks = {name: bool(passed) for name, passed in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    rows = []
    for policy in policies:
        for plant in (
            "P30_ALL_JOINT",
            "P31_34_PITCH_WITH_P30_NONPITCH",
        ):
            for command in (0.0, 0.074, 0.077, 0.080):
                rows.append(
                    {
                        "checkpoint_id": policy["id"],
                        "step": policy["step"],
                        "policy_sha256": policy["sha256"],
                        "plant": plant,
                        "command_x_m_s": command,
                        "seed": 167_931_544,
                        "duration_ticks": 600,
                        "configuration": None,
                        "calibration_ticks": 0,
                        "home_return_ticks": 0,
                        "transport": {
                            "additional_action_delay_ticks": 0,
                            "imu_delay_ticks": 0,
                            "native_quantization": False,
                            "sensor_noise_scales": None,
                        },
                    }
                )
    matrix_hash = canonical_sha256(rows)
    value = {
        "schema_version": "open_duck.t25_t23_nominal_preregistration.v1",
        "status": (
            "PREREGISTERED_T25_T23_NOMINAL_BEHAVIOR"
            if not failed
            else "HOLD_T25_T23_NOMINAL_BEHAVIOR_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {
            "t24_transform": sha256(TRANSFORM),
            "base_nominal_preregistration": sha256(BASE),
            "playground_manifest": sha256(PLAYGROUND_MANIFEST),
        },
        "source_hashes": source_hashes,
        "playground": str(playground),
        "policies": policies,
        "matrix": {
            "cells": len(rows),
            "rows": rows,
            "sha256": matrix_hash,
        },
        "gate": base["gate"],
        "decision_rule": {
            "both_checkpoints_all_eight_cells_pass": (
                "authorize a separate full frozen robustness-matrix "
                "preregistration"
            ),
            "only_one_checkpoint_passes": (
                "reject persistence; do not cherry-pick"
            ),
            "any_behavior_current_or_torque_failure": (
                "hold the policy and attribute before further policy work"
            ),
            "reward_or_training_metric_selection": False,
        },
        "execution_now": {
            "formal_behavior_cells": 0,
            "training_steps": 0,
            "colab_compute_units": 0,
            "rdk_or_robot_access": 0,
        },
        "authority": {
            "formal_behavior_cells_authorized": (
                len(rows) if not failed else 0
            ),
            "cpu_only": True,
            "full_matrix_authorized": False,
            "checkpoint_selection_authorized": False,
            "gate5_authorized": False,
            "rdkx5_or_robot": False,
            "robot_clearance": False,
            "torque_or_motion": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T25 T23 nominal behavior preregistration",
                "",
                f"- Status: `{value['status']}`",
                f"- Matrix SHA-256: `{matrix_hash}`",
                "- The unchanged 16-cell CPU gate covers both checkpoints, "
                "both measured actuator plants, and x=0/.074/.077/.080 for "
                "600 ticks.",
                "- Both checkpoints must pass every behavior, current, and "
                "torque check. No robustness, Gate 5, or robot authority.",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"matrix_sha256={matrix_hash}")
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
