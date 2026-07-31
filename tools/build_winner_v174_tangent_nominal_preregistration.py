#!/usr/bin/env python3
"""Preregister V174's zero-credit nominal behavior falsifier."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v174_tangent_nominal_preregistration.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V174_TANGENT_NOMINAL_PREREGISTRATION_20260725.md"
)
RUNNER = TOOLS / "run_winner_v174_tangent_nominal.py"
CELL_RUNNER = TOOLS / "run_winner_v141_projected_final_behavior.py"
V121_PREREG = ANALYSIS / "winner_v121_nominal_behavior_preregistration.json"
V121_RESULT = ANALYSIS / "winner_v121_nominal_behavior_result.json"
V126_PREREG = (
    ANALYSIS / "winner_v126_all_tick_supreme_clip_preregistration.json"
)
BASE_PREREG = (
    ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
)
V170_RESULT = (
    ANALYSIS / "winner_v170_exact_oracle_r2_feasibility_result.json"
)
V173_PREREG = (
    ANALYSIS
    / "winner_v173_lexicographic_tangent_cpu_preregistration.json"
)
V173_RESULT = ANALYSIS / "winner_v173_lexicographic_tangent_cpu_result.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def cell_key(row: dict[str, Any]) -> tuple[str, float]:
    return str(row["plant"]), float(row["command_x_m_s"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluator-root", type=Path, required=True)
    args = parser.parse_args()
    evaluator_root = args.evaluator_root.resolve()
    manifest_path = evaluator_root / "composition_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    evaluator_path = Path(manifest["output"]["path"])
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V174: {path}")

    v121_prereg = json.loads(V121_PREREG.read_text(encoding="utf-8"))
    v121_result = json.loads(V121_RESULT.read_text(encoding="utf-8"))
    v170 = json.loads(V170_RESULT.read_text(encoding="utf-8"))
    v173_prereg = json.loads(V173_PREREG.read_text(encoding="utf-8"))
    v173 = json.loads(V173_RESULT.read_text(encoding="utf-8"))
    policy = Path(v173["deployment"]["graphs"]["1024"]["path"])
    source_checkpoint = next(
        row
        for row in v121_result["per_checkpoint"]
        if row["checkpoint_id"] == "V121_TRAIN_MATCHED_HALF"
    )
    rows = [
        dict(row)
        for row in v121_prereg["matrix"]["rows"]
        if row["checkpoint_id"] == "V121_TRAIN_MATCHED_HALF"
        and float(row["command_x_m_s"]) > 0.01
    ]
    rows_by_key = {cell_key(row): row for row in rows}
    risk_order = [
        ("P31_34_PITCH_WITH_P30_NONPITCH", 0.080),
        ("P31_34_PITCH_WITH_P30_NONPITCH", 0.074),
        ("P30_ALL_JOINT", 0.080),
        ("P30_ALL_JOINT", 0.077),
        ("P31_34_PITCH_WITH_P30_NONPITCH", 0.077),
        ("P30_ALL_JOINT", 0.074),
    ]
    ordered_rows = []
    for plant, command in risk_order:
        row = dict(rows_by_key[(plant, command)])
        row["checkpoint_id"] = "V173_TANGENT_CPU_1024"
        row["step"] = 1024
        row["policy_sha256"] = sha256(policy)
        ordered_rows.append(row)

    input_paths = {
        "builder": Path(__file__).resolve(),
        "runner": RUNNER,
        "cell_runner": CELL_RUNNER,
        "v121_preregistration": V121_PREREG,
        "v121_result": V121_RESULT,
        "v126_preregistration": V126_PREREG,
        "base_preregistration": BASE_PREREG,
        "v170_result": V170_RESULT,
        "v173_preregistration": V173_PREREG,
        "v173_result": V173_RESULT,
        "composition_manifest": manifest_path,
        "composed_evaluator": evaluator_path,
        "policy": policy,
    }
    checks = {
        "v173_cpu_contract_green": (
            v173.get("status")
            == "PASS_WINNER_V173_LEXICOGRAPHIC_TANGENT_CPU_CONTRACT"
            and v173.get("failed_checks") == []
            and v173.get("decision")
            == "EARN_V174_NOMINAL_BEHAVIOR_SCREEN_ONLY"
        ),
        "v173_preregistration_exact": (
            v173_prereg.get("status")
            == "PREREGISTERED_WINNER_V173_LEXICOGRAPHIC_TANGENT_CPU_CONTRACT"
        ),
        "v170_nearby_safe_r2_gait_green": (
            v170.get("status")
            == "PASS_WINNER_V170_EXACT_ORACLE_R2_FEASIBILITY_VALID_RESULT"
        ),
        "source_v121_half_exact_eight_of_eight": (
            source_checkpoint["all_eight_cells_pass"]
            and source_checkpoint["cells"] == 8
        ),
        "candidate_policy_hash_exact": (
            sha256(policy)
            == v173["deployment"]["graphs"]["1024"]["sha256"]
        ),
        "moving_matrix_exact_six_in_frozen_risk_order": (
            len(ordered_rows) == 6
            and [cell_key(row) for row in ordered_rows] == risk_order
        ),
        "x0_graph_invariants_exact": (
            v173["deployment"]["graphs"]["1024"]["inference"]["checks"][
                "zero_action_exact"
            ]
            and v173["deployment"]["graphs"]["1024"]["inference"]["checks"][
                "zero_previous_exact"
            ]
        ),
        "cpu_only_zero_new_training": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    source_worst = float(source_checkpoint["worst_peak_torque_nm"])
    payload = {
        "schema_version": "winner_v174.tangent_nominal_preregistration.v1",
        "status": (
            "PREREGISTERED_WINNER_V174_TANGENT_NOMINAL"
            if not failed
            else "HOLD_WINNER_V174_TANGENT_NOMINAL_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {
            name: sha256(path) for name, path in input_paths.items()
        },
        "external_inputs": {
            "evaluator_root": str(evaluator_root),
            "playground": json.loads(
                V126_PREREG.read_text(encoding="utf-8")
            )["external_inputs"]["playground"],
            "policy": str(policy),
        },
        "policy": {
            "id": "V173_TANGENT_CPU_1024",
            "path": str(policy),
            "sha256": sha256(policy),
            "new_training_in_v174": False,
        },
        "matrix": {
            "moving_cells": 6,
            "rows_in_source_margin_risk_order": ordered_rows,
            "x0_cells_by_exact_graph_invariant": 2,
            "stop_on_first_failure": True,
        },
        "gate": v121_prereg["gate"],
        "source_baseline": {
            "policy": "V121_TRAIN_MATCHED_HALF",
            "all_eight_cells_pass": True,
            "worst_peak_torque_nm": source_worst,
            "strict_improvement_required": True,
        },
        "decision_rule": {
            "green": (
                "all six moving cells pass every unchanged gate, both x0 "
                "invariants are exact, and worst torque is strictly below "
                "the V121-half source value; earn one hosted preregistration"
            ),
            "hold": (
                "stop at the first failed moving cell or reject a complete "
                "matrix that does not strictly improve source worst torque; "
                "close this optimizer without another CPU step count, lr, "
                "norm cap, source, or retry"
            ),
        },
        "authority": {
            "maximum_cpu_cells": 6 if not failed else 0,
            "hosted_preregistration_design": False,
            "hosted_training": False,
            "candidate_selection": False,
            "robustness_matrix": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V174 tangent-policy nominal preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Tests the V173 1,024-step deployment graph over the six moving "
        "V121 nominal cells in frozen source-risk order; stop on first "
        "failure.\n"
        "- The two x=0 cells are carried only by the exact deployment "
        "deadband invariants already checked in V173.\n"
        f"- Worst torque must be strictly below the source "
        f"`{source_worst} N.m`, not merely below the gate.\n"
        "- Passing earns one hosted preregistration only. No hosted launch, "
        "candidate, robustness matrix, Gate 5, RDK-X5, or robot.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
