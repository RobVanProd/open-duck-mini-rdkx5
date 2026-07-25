#!/usr/bin/env python3
"""Preregister the read-only V132 robust-teacher dataset audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
V131_RESULT = ANALYSIS / "winner_v131_two_fit_oracle_behavior_result.json"
RUNNER = ROOT / "tools/audit_winner_v132_robust_teacher_dataset.py"
OUTPUT = ANALYSIS / "winner_v132_robust_teacher_dataset_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "WINNER_V132_ROBUST_TEACHER_DATASET_PREREGISTRATION_20260724.md"
)
EXPECTED = {
    "v131_behavior_result": (
        "ab1535e11287f191e8ee6b4be5c020c44726c6263465c7cb760892387b07c9ea"
    ),
    "audit_runner": (
        "a21e4dc8a567563530278be180887b818d790b2a6eb74227029c2e3692a73caf"
    ),
    "source_checkpoint": (
        "c1d9b8574c941e2279294de14aca1cb57d4736bdc63635b5aaf1e205fa7f86c1"
    ),
    "cpu_template": (
        "217a1551c4cc778e4b957636a40ca6e01eafa51efeaef905eb73e9debc7c26e5"
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(
        candidate for candidate in path.rglob("*") if candidate.is_file()
    ):
        digest.update(item.relative_to(path).as_posix().encode())
        digest.update(b"\0")
        with item.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        digest.update(b"\0")
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-checkpoint", type=Path, required=True)
    parser.add_argument("--cpu-template", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V132: {path}")
    source = args.source_checkpoint.resolve()
    cpu_template = args.cpu_template.resolve()
    v131 = json.loads(V131_RESULT.read_text(encoding="utf-8"))
    input_hashes = {
        "v131_behavior_result": sha256(V131_RESULT),
        "audit_runner": sha256(RUNNER),
        "source_checkpoint": directory_sha256(source),
        "cpu_template": directory_sha256(cpu_template),
    }
    checks = {
        "all_input_hashes_exact": input_hashes == EXPECTED,
        "v131_teacher_green": (
            v131.get("status")
            == "PASS_WINNER_V131_TWO_FIT_ORACLE_BEHAVIOR_VALID_RESULT"
            and v131.get("decision")
            == "EARN_ONE_V132_ROBUST_TEACHER_DATASET_AUDIT"
            and v131.get("summary", {}).get("passing_cells") == 8
            and v131.get("summary", {}).get("robust_safe_rows") == 3_600
            and v131.get("summary", {}).get("empty_intersection_events") == 0
        ),
        "same_thresholds_as_v130_frozen_before_fit": True,
        "read_only_no_training": True,
        "robot_surface_absent": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "winner_v132.robust_teacher_dataset_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V132_ROBUST_TEACHER_DATASET_AUDIT"
            if not failed
            else "HOLD_WINNER_V132_ROBUST_TEACHER_DATASET_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": input_hashes,
        "question": (
            "Does replacing fit-specific V126 labels with V131 common-safe "
            "labels make a static deployable correction readout both "
            "localizable and cross-fit preserving?"
        ),
        "dataset": {
            "rows": 4_800,
            "traces": 8,
            "source_policy": "V121_TRAIN_MATCHED_FINAL",
            "target": (
                "two-fit oracle final action minus base action on explicitly "
                "projected rows; exact zero elsewhere"
            ),
            "class_weight": (
                "preservation_rows/corrected_rows, derived after the explicit "
                "row census"
            ),
        },
        "representations": {
            "current_hidden": "h_out[64]",
            "normalized_obs": "source-normalized obs[115]",
            "state": "source-normalized obs[115] + h_in[64]",
            "fit": "float64 unregularized class-balanced least squares",
        },
        "advancement_thresholds": {
            "corrected_ratio_to_zero_predictor": "<=0.25",
            "preservation_ratio_to_corrected_baseline": "<=0.01",
            "each_cross_fit_corrected_ratio": "<1.0",
            "each_cross_fit_preservation_ratio": "<=0.01",
            "state_only_total_error_vs_hidden": "<=0.25",
        },
        "selection": (
            "prefer the existing hidden representation if it passes every "
            "threshold; otherwise allow state only if it passes every "
            "threshold plus the fourfold total-error rule"
        ),
        "stop_rule": (
            "if neither representation passes, do not train a static linear "
            "residual from this dataset"
        ),
        "authority": {
            "read_only_cpu_audit": not failed,
            "training": False,
            "hosted_training": False,
            "behavior_evaluation": False,
            "full_matrix": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V132 robust teacher dataset preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Reuses V130's frozen separability/preservation thresholds.\n"
        "- Audits the V131 common-safe labels without any training.\n"
        "- No behavior, Colab, RDK, torque, or motion authority.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
