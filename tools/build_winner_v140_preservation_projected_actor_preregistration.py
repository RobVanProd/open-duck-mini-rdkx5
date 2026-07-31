#!/usr/bin/env python3
"""Preregister the V140 preservation-projected actor CPU audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RUNNER = ROOT / "tools/audit_winner_v140_preservation_projected_actor.py"
V121_TRANSFORM = ANALYSIS / "winner_v121_deployment_transform_contract.json"
V131_RESULT = ANALYSIS / "winner_v131_two_fit_oracle_behavior_result.json"
V134_RESULT = ANALYSIS / "winner_v134_full_actor_teacher_cpu_result_v3.json"
V139_RESULT = ANALYSIS / "winner_v139_reference_input_controllability_result.json"
TEACHER = ROOT / "training/winner_v134_full_actor_teacher_distillation.py"
OUTPUT = (
    ANALYSIS / "winner_v140_preservation_projected_actor_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V140_PRESERVATION_PROJECTED_ACTOR_PREREGISTRATION_20260725.md"
)
EXPECTED = {
    "runner": (
        "db60701cde771326a96d2a0c4bbfd12c63c21527bcd8a67ca8ffbc827bd35271"
    ),
    "v121_transform": (
        "4bd5eab5343cd8401db1789773fa3cc345727d903cb31222e0ea9870f0e9e640"
    ),
    "v131_behavior_result": (
        "ab1535e11287f191e8ee6b4be5c020c44726c6263465c7cb760892387b07c9ea"
    ),
    "v134_cpu_result": (
        "e25691c219eec4b76dea0f18b14e47b6fd840b6c0bc53c6c1817cdd5fbf3f387"
    ),
    "v139_reference_result": (
        "1407587ad6ee15d44220a17860411f55d4f4988118d2f7cb191b4b91225dee0b"
    ),
    "teacher_loader": (
        "632a2e12ae10d940be38858c52e738281ca6a2de1736d1be90b8adcbdbd8baa8"
    ),
    "source_raw": (
        "a8f883e8b087e940647fa62e5b79f4e7961db0ecb5bd36fc3bd88411b6e7bdce"
    ),
    "candidate_raw": (
        "5e50991556f13aaf2148a782de23341b549e58079ad62c02c77d8fe8bd307e87"
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
    parser.add_argument("--source-raw", type=Path, required=True)
    parser.add_argument("--candidate-raw", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V140: {path}")
    source_raw = args.source_raw.resolve()
    candidate_raw = args.candidate_raw.resolve()
    v134 = json.loads(V134_RESULT.read_text(encoding="utf-8"))
    v139 = json.loads(V139_RESULT.read_text(encoding="utf-8"))
    input_hashes = {
        "runner": sha256(RUNNER),
        "v121_transform": sha256(V121_TRANSFORM),
        "v131_behavior_result": sha256(V131_RESULT),
        "v134_cpu_result": sha256(V134_RESULT),
        "v139_reference_result": sha256(V139_RESULT),
        "teacher_loader": sha256(TEACHER),
        "source_raw": sha256(source_raw),
        "candidate_raw": sha256(candidate_raw),
    }
    checks = {
        "all_input_hashes_exact": input_hashes == EXPECTED,
        "v134_closed_only_on_preservation": (
            v134.get("failed_checks")
            == ["preservation_leakage_within_one_percent"]
            and v134.get("smoke", {})
            .get("metrics", {})
            .get("corrected_ratio_to_zero_predictor", 1.0)
            < 0.95
        ),
        "reference_redirection_closed": (
            v139.get("decision") == "CLOSE_REFERENCE_INPUT_REDIRECTION"
        ),
        "constraint_projection_is_distinct_from_optimizer_retry": True,
        "alpha_uses_preservation_only": True,
        "fixed_twenty_step_bisection": True,
        "corrected_error_has_zero_selection_weight": True,
        "training_and_behavior_not_authorized": True,
        "robot_surface_absent": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "winner_v140.preservation_projected_actor_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V140_PRESERVATION_PROJECTED_ACTOR"
            if not failed
            else "HOLD_WINNER_V140_PRESERVATION_PROJECTED_ACTOR_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": input_hashes,
        "mechanism": {
            "source": "V134 raw step 0 / frozen V121 final actor",
            "direction": "V134 two-update raw actor minus source actor",
            "operation": (
                "interpolate every changed floating ONNX initializer by one "
                "shared alpha"
            ),
            "alpha": (
                "largest feasible value under the existing full-dataset 1% "
                "preservation boundary"
            ),
            "why_distinct": (
                "the optimizer and its constants are not retried; the already "
                "observed update direction is projected onto an explicit "
                "behavior-preservation constraint"
            ),
        },
        "selection": {
            "bisection_steps": 20,
            "preservation_limit": 0.01,
            "population": "all 4,729 V131 non-correction rows",
            "corrected_error_selection_weight": 0,
            "parameter_search": False,
        },
        "pass_rule": {
            "source": "reproduces all recorded base actions <=1e-6",
            "full_update": "reproduces preservation ratio >0.01",
            "selected_preservation": "<=0.01",
            "selected_correction": "<=0.95 times source on all 71 corrections",
            "alpha": "strictly between 0 and 1",
            "x0": "exact zero",
            "exports": "source, full, and selected deployment contracts pass",
        },
        "stop_rule": (
            "if any pass rule fails, close preservation-projected actor; do "
            "not alter the boundary, interpolation path, bisection count, or "
            "use corrected error to select alpha"
        ),
        "green_followup": (
            "a pass earns only preregistration of one dual-checkpoint CPU "
            "behavior screen using frozen V121 half and the projected final"
        ),
        "authority": {
            "cpu_projection_audit": not failed,
            "behavior_preregistration": False,
            "behavior_evaluation": False,
            "training": False,
            "hosted_training": False,
            "checkpoint_selection": False,
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
        "# Winner V140 preservation-projected actor preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- One graph direction, one frozen 1% preservation constraint, "
        "twenty bisection steps.\n"
        "- Corrected error is evaluated only after alpha is fixed.\n"
        "- No optimizer retry, training, behavior, Colab, or hardware.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
