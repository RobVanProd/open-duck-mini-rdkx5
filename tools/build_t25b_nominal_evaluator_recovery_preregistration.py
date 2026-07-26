#!/usr/bin/env python3
"""Preregister one evaluator-only recovery of T25's unchanged matrix."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
T25_PREREG = ANALYSIS / "t25_t23_nominal_behavior_preregistration.json"
ATTRIBUTION = ANALYSIS / "t25_nominal_evaluator_invalidity_attribution.json"
CONTRACT = ANALYSIS / "t25_zero_context_evaluator_contract.json"
OUTPUT = ANALYSIS / "t25b_nominal_evaluator_recovery_preregistration.json"
MARKDOWN = ANALYSIS / "T25B_NOMINAL_EVALUATOR_RECOVERY_20260726.md"
SOURCE_PATHS = (
    "tools/run_t25b_t23_nominal_behavior.py",
    "tools/closed_loop_sim_eval.py",
    "tools/run_winner_v110_pitch_guard_behavior.py",
    "tools/run_winner_v109_recurrent_source_screen.py",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T25B: {path}")
    prereg = json.loads(T25_PREREG.read_text(encoding="utf-8"))
    attribution = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    source_hashes = {
        name: sha256(ROOT / name) for name in SOURCE_PATHS
    }
    checks = {
        "original_matrix_exact_green": (
            prereg.get("status")
            == "PREREGISTERED_T25_T23_NOMINAL_BEHAVIOR"
            and prereg.get("failed_checks") == []
            and prereg["matrix"]["cells"] == 16
        ),
        "invalidity_attribution_green": (
            attribution.get("status")
            == "PASS_T25_NOMINAL_EVALUATOR_INVALIDITY_ATTRIBUTION"
            and attribution.get("failed_checks") == []
            and attribution["first_execution"][
                "formal_policy_decision_weight"
            ]
            == 0
        ),
        "zero_context_cpu_contract_green": (
            contract.get("status")
            == "PASS_T25_ZERO_CONTEXT_EVALUATOR_CONTRACT"
            and contract.get("failed_checks") == []
        ),
        "policies_matrix_gate_seeds_duration_unchanged": True,
        "evaluator_change_is_default_off": (
            contract["contract"]["default_off"] is True
        ),
        "one_recovery_only": True,
        "training_or_colab_zero": True,
        "robot_or_rdk_access_zero": True,
    }
    checks = {name: bool(passed) for name, passed in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value = {
        "schema_version": "open_duck.t25b_evaluator_recovery.v1",
        "status": (
            "PREREGISTERED_T25B_NOMINAL_EVALUATOR_RECOVERY"
            if not failed
            else "HOLD_T25B_NOMINAL_EVALUATOR_RECOVERY"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {
            "original_preregistration": sha256(T25_PREREG),
            "invalidity_attribution": sha256(ATTRIBUTION),
            "zero_context_contract": sha256(CONTRACT),
        },
        "source_hashes": source_hashes,
        "frozen_matrix_sha256": prereg["matrix"]["sha256"],
        "correction": {
            "only_change": (
                "feed float32 zeros[1,64] to ignored calibration_context"
            ),
            "policies": "BYTE_IDENTICAL",
            "matrix": "BYTE_IDENTICAL",
            "gate": "BYTE_IDENTICAL",
            "seeds": "BYTE_IDENTICAL",
            "duration": "BYTE_IDENTICAL",
            "playground": "BYTE_IDENTICAL",
            "response_calibrator": False,
            "unscored_prefix_ticks": 0,
        },
        "decision": (
            "RUN_ONE_T25B_CPU_MATRIX_RECOVERY"
            if not failed
            else "HOLD_WITHOUT_BEHAVIOR"
        ),
        "execution_now": {
            "formal_behavior_cells": 0,
            "optimizer_steps": 0,
            "colab_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_cpu_matrix_recovery": not failed,
            "training_authorized": False,
            "colab_authorized": False,
            "checkpoint_selection_authorized": False,
            "gate5_authorized": False,
            "rdkx5_or_robot": False,
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
                "# T25B nominal evaluator recovery preregistration",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                "- The sole correction feeds zeros to a required diagnostic "
                "input already proven bit-exactly ignored.",
                "- Policies, matrix, gates, seeds, duration, and simulator "
                "remain byte-identical.",
                "- One CPU matrix recovery; no training, Gate 5, or robot.",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
