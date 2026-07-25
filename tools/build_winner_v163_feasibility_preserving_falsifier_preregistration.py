#!/usr/bin/env python3
"""Preregister V163's zero-training feasibility-preserving update falsifier."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = (
    ANALYSIS
    / "winner_v163_feasibility_preserving_falsifier_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V163_FEASIBILITY_PRESERVING_FALSIFIER_PREREGISTRATION_20260725.md"
)
V121_PREREG = ANALYSIS / "winner_v121_nominal_behavior_preregistration.json"
V121_RESULT = ANALYSIS / "winner_v121_nominal_behavior_result.json"
V127_CPU = ANALYSIS / "winner_v127_constrained_cpu_result.json"
V162_RESULT = ANALYSIS / "winner_v162_uniform_trust_nominal_result.json"
V126 = ANALYSIS / "winner_v126_all_tick_supreme_clip_preregistration.json"
BASE = (
    ANALYSIS
    / "winner_v3_variable_configuration_replacement_preregistration.json"
)
RUNNER = ROOT / "tools/run_winner_v163_feasibility_preserving_falsifier.py"
CELL_RUNNER = ROOT / "tools/run_winner_v141_projected_final_behavior.py"
INTERPOLATOR = ROOT / "tools/audit_winner_v140_preservation_projected_actor.py"
DEPLOYER = ROOT / "tools/run_winner_v129_oracle_teacher_cpu_contract.py"


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
            raise FileExistsError(f"refusing to overwrite V163: {path}")

    v121_prereg = json.loads(V121_PREREG.read_text(encoding="utf-8"))
    v121_result = json.loads(V121_RESULT.read_text(encoding="utf-8"))
    v127 = json.loads(V127_CPU.read_text(encoding="utf-8"))
    v162 = json.loads(V162_RESULT.read_text(encoding="utf-8"))

    source_policy = next(
        row
        for row in json.loads(
            (
                ANALYSIS / "winner_v121_deployment_transform_contract.json"
            ).read_text(encoding="utf-8")
        )["policies"]
        if row["id"] == "V121_TRAIN_MATCHED_HALF"
    )
    source_raw = Path(source_policy["source_path"])
    smoke_root = Path(v127["deployment"]["graphs"]["1024"]["path"]).parent / "smoke"
    proposal_matches = sorted(smoke_root.glob("*_1024.onnx"))
    if len(proposal_matches) != 1:
        raise ValueError(
            f"expected one V127 CPU proposal graph, found {proposal_matches}"
        )
    proposal_raw = proposal_matches[0]
    proposal_iterations = int(
        v127["training"]["aux"]["1024"]["total_training_iterations"]
    )
    if proposal_iterations != 32:
        raise ValueError("V127 CPU proposal no longer represents 32 iterations")

    half_rows = [
        dict(row)
        for row in v121_prereg["matrix"]["rows"]
        if row["checkpoint_id"] == "V121_TRAIN_MATCHED_HALF"
        and float(row["command_x_m_s"]) > 0.01
    ]
    rows_by_key = {cell_key(row): row for row in half_rows}
    risk_order = [
        ("P31_34_PITCH_WITH_P30_NONPITCH", 0.080),
        ("P31_34_PITCH_WITH_P30_NONPITCH", 0.074),
        ("P30_ALL_JOINT", 0.080),
        ("P30_ALL_JOINT", 0.077),
        ("P31_34_PITCH_WITH_P30_NONPITCH", 0.077),
        ("P30_ALL_JOINT", 0.074),
    ]
    moving_rows = [rows_by_key[key] for key in risk_order]

    source_run_root = Path(v121_result["run_root"])
    source_cell_paths = sorted(
        (source_run_root / "cells").glob("v121_train_matched_half_*.json")
    )
    source_cells = [
        {
            "path": str(path),
            "sha256": sha256(path),
        }
        for path in source_cell_paths
    ]
    source_checkpoint = next(
        row
        for row in v121_result["per_checkpoint"]
        if row["checkpoint_id"] == "V121_TRAIN_MATCHED_HALF"
    )
    source_worst_torque = float(source_checkpoint["worst_peak_torque_nm"])
    torque_limit = float(v121_prereg["gate"]["per_joint_peak_torque_nm_max"])

    alphas = [1.0 / (2**power) for power in range(6)]
    input_paths = {
        "builder": Path(__file__).resolve(),
        "runner": RUNNER,
        "cell_runner": CELL_RUNNER,
        "interpolator": INTERPOLATOR,
        "deployer": DEPLOYER,
        "v121_preregistration": V121_PREREG,
        "v121_result": V121_RESULT,
        "v127_cpu_result": V127_CPU,
        "v162_result": V162_RESULT,
        "v126_preregistration": V126,
        "base_preregistration": BASE,
        "composition_manifest": manifest_path,
        "composed_evaluator": evaluator_path,
        "source_raw": source_raw,
        "proposal_raw": proposal_raw,
    }
    checks = {
        "v121_half_exact_eight_of_eight": (
            source_checkpoint["all_eight_cells_pass"]
            and source_checkpoint["cells"] == 8
        ),
        "v127_cpu_contract_green": (
            v127["status"] == "PASS_WINNER_V127_CONSTRAINED_CPU_CONTRACT"
            and v127["failed_checks"] == []
        ),
        "v162_closed_without_alpha_retry": (
            v162["decision"]
            == "CLOSE_UNIFORM_TRUST_PROJECTION_NO_ALPHA_RETRY"
        ),
        "source_raw_hash_exact": (
            sha256(source_raw)
            == v127["deployment"]["graphs"]["0"]["raw_sha256"]
        ),
        "proposal_raw_hash_exact": (
            sha256(proposal_raw)
            == v127["deployment"]["graphs"]["1024"]["raw_sha256"]
        ),
        "proposal_has_exactly_32_iterations": proposal_iterations == 32,
        "ladder_exact_and_derived": (
            alphas == [1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125]
            and alphas[-1] == 1.0 / proposal_iterations
        ),
        "moving_matrix_exact_six": (
            len(moving_rows) == 6
            and len({cell_key(row) for row in moving_rows}) == 6
        ),
        "source_eight_cell_artifacts_exact": len(source_cells) == 8,
        "source_strictly_inside_torque_gate": (
            source_worst_torque < torque_limit
        ),
        "cpu_only_zero_training": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "winner_v163.feasibility_preserving_falsifier_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V163_FEASIBILITY_PRESERVING_FALSIFIER"
            if not failed
            else "HOLD_WINNER_V163_FEASIBILITY_PRESERVING_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {
            name: sha256(path) for name, path in input_paths.items()
        },
        "sources": {
            "source_raw": {
                "path": str(source_raw),
                "sha256": sha256(source_raw),
            },
            "proposal_raw": {
                "path": str(proposal_raw),
                "sha256": sha256(proposal_raw),
            },
            "source_cells": source_cells,
            "source_worst_peak_torque_nm": source_worst_torque,
            "source_torque_margin_nm": torque_limit - source_worst_torque,
        },
        "proposal": {
            "origin": "hash_frozen V127 CPU step-1024 constrained proposal",
            "aggregated_ppo_iterations": proposal_iterations,
            "new_training": False,
            "alternate_batch_or_proposal": False,
        },
        "backtracking": {
            "alphas_descending": alphas,
            "minimum_nontrivial_alpha": 1.0 / proposal_iterations,
            "derivation": (
                "the proposal aggregates 32 PPO iterations; 1/32 is one "
                "average-iteration displacement"
            ),
            "first_feasible_alpha_is_decisive": True,
            "retry_or_finer_ladder": False,
        },
        "matrix": {
            "moving_cells": 6,
            "rows_in_source_margin_risk_order": moving_rows,
            "x0_cells_reused": 2,
            "x0_basis": (
                "both source x0 cells passed and the unchanged deployment "
                "deadband forces exact zero final actions at x=0"
            ),
        },
        "gate": v121_prereg["gate"],
        "decision_rule": {
            "earn_next_cpu_contract_only": (
                "the first alpha whose six moving cells all pass also has "
                "worst peak torque strictly below the frozen source value"
            ),
            "close": (
                "no alpha through 1/32 passes, or the first feasible alpha "
                "does not improve the frozen source worst-torque reserve"
            ),
            "behavior_or_reward_checkpoint_selection": False,
            "hosted_run_authorized_by_pass": False,
        },
        "authority": {
            "cpu_cells_maximum": 36,
            "training": False,
            "hosted_training": False,
            "full_robustness": False,
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
        "# Winner V163 feasibility-preserving falsifier preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Reuses the hash-frozen V127 32-iteration CPU proposal; no new "
        "training.\n"
        "- Fixed descending alpha ladder: `1, 1/2, 1/4, 1/8, 1/16, 1/32`.\n"
        "- `1/32` is the derived nontrivial floor: one average-iteration "
        "displacement.\n"
        "- The first feasible alpha is decisive and must strictly improve "
        "the source worst-torque reserve.\n"
        "- Passing earns only a separate CPU implementation contract, never "
        "hosted training.\n"
        "- CPU-only; no Colab, deployment, Gate 5, RDK-X5, or robot.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
