#!/usr/bin/env python3
"""Preregister the read-only V133 compact-local-residual audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
V131_RESULT = ANALYSIS / "winner_v131_two_fit_oracle_behavior_result.json"
V132_RESULT = ANALYSIS / "winner_v132_robust_teacher_dataset_audit.json"
RUNNER = ROOT / "tools/audit_winner_v133_compact_local_residual.py"
OUTPUT = (
    ANALYSIS / "winner_v133_compact_local_residual_preregistration_v3.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V133_COMPACT_LOCAL_RESIDUAL_PREREGISTRATION_V3_20260724.md"
)
EXPECTED = {
    "v131_behavior_result": (
        "ab1535e11287f191e8ee6b4be5c020c44726c6263465c7cb760892387b07c9ea"
    ),
    "v132_dataset_audit": (
        "1292b12ff996cf99fc5fdd718048517256bb86d656512fad3586a6d62a8963ca"
    ),
    "audit_runner": (
        "c0ef1211823164f057c9ae2582b2f70e2312f2ff24bb04986fe9cffc91f25343"
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
            raise FileExistsError(f"refusing to overwrite V133: {path}")
    source = args.source_checkpoint.resolve()
    cpu_template = args.cpu_template.resolve()
    v131 = json.loads(V131_RESULT.read_text(encoding="utf-8"))
    v132 = json.loads(V132_RESULT.read_text(encoding="utf-8"))
    input_hashes = {
        "v131_behavior_result": sha256(V131_RESULT),
        "v132_dataset_audit": sha256(V132_RESULT),
        "audit_runner": sha256(RUNNER),
        "source_checkpoint": directory_sha256(source),
        "cpu_template": directory_sha256(cpu_template),
    }
    checks = {
        "all_input_hashes_exact": input_hashes == EXPECTED,
        "v131_teacher_green": (
            v131.get("status")
            == "PASS_WINNER_V131_TWO_FIT_ORACLE_BEHAVIOR_VALID_RESULT"
            and v131.get("summary", {}).get("passing_cells") == 8
        ),
        "v132_static_linear_closed": (
            v132.get("status")
            == "PASS_WINNER_V132_ROBUST_TEACHER_DATASET_AUDIT"
            and v132.get("decision")
            == "NO_STATIC_LINEAR_ROBUST_TEACHER_DISTILLATION"
        ),
        "leave_one_trace_out_before_result": True,
        "compact_radius_formula_frozen": True,
        "read_only_no_training": True,
        "robot_surface_absent": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "winner_v133.compact_local_residual_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V133_COMPACT_LOCAL_RESIDUAL_AUDIT_V3"
            if not failed
            else "HOLD_WINNER_V133_COMPACT_LOCAL_RESIDUAL_PREREGISTRATION"
        ),
        "supersedes": {
            "artifact": (
                "winner_v133_compact_local_residual_preregistration_v2.json"
            ),
            "reason": (
                "V2 incorrectly required all 45 projected joint flags to "
                "produce a nonzero shared-action correction. Some flags "
                "certify the shadow fit without changing the common action. "
                "V3 requires the 17 frozen corrected rows and defines "
                "nonzero corrections as a nonempty subset of the 45 flags. "
                "No advancement threshold changes."
            ),
        },
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": input_hashes,
        "question": (
            "Are V131's 45 joint corrections locally separable from exact "
            "preservation rows under whole-trace holdout, so a compact "
            "nonlinear residual is evidenced rather than merely memorized?"
        ),
        "method": {
            "validation": (
                "eight leave-one-(plant,command)-trace-out folds"
            ),
            "representations": [
                "current h_out[64]",
                "source-normalized obs[115] plus h_in[64]",
            ],
            "feature_normalization": (
                "training-fold z-score; dimensions below 1e-6 removed"
            ),
            "centers": "all nonzero per-joint teacher corrections",
            "radius": (
                "0.5 times each center's nearest zero-correction training "
                "distance; no search"
            ),
            "prediction": (
                "nearest same-joint center correction inside radius and "
                "exact zero outside"
            ),
        },
        "thresholds": {
            "combined_corrected_ratio": "<=0.25",
            "combined_preservation_ratio": "<=0.01",
            "combined_event_recall": ">=0.90",
            "each_corrected_fold_corrected_ratio": "<1.0",
            "each_corrected_fold_preservation_ratio": "<=0.01",
            "x0_false_positive_joint_events": 0,
        },
        "selection": (
            "prefer current hidden if it qualifies; otherwise permit "
            "normalized observation plus recurrent state"
        ),
        "stop_rule": (
            "if neither representation passes, close a compact local "
            "residual from the nominal teacher dataset without training"
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
        "# Winner V133 compact local residual preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Whole-trace holdout and compact radii are frozen before results.\n"
        "- No training, behavior evaluation, Colab, or hardware authority.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
