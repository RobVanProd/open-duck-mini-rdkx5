#!/usr/bin/env python3
"""Preregister V164's actor-only accepted-state coherence screen."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v164_state_coherence_preregistration.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V164_STATE_COHERENCE_PREREGISTRATION_20260725.md"
)
V121_PREREG = ANALYSIS / "winner_v121_nominal_behavior_preregistration.json"
V121_RESULT = ANALYSIS / "winner_v121_nominal_behavior_result.json"
V127_PREREG = ANALYSIS / "winner_v127_constrained_cpu_preregistration.json"
V127_RESULT = ANALYSIS / "winner_v127_constrained_cpu_result.json"
V163_RESULT = (
    ANALYSIS / "winner_v163_feasibility_preserving_falsifier_result.json"
)
V126 = ANALYSIS / "winner_v126_all_tick_supreme_clip_preregistration.json"
BASE = (
    ANALYSIS
    / "winner_v3_variable_configuration_replacement_preregistration.json"
)
RUNNER = ROOT / "tools/run_winner_v164_state_coherence.py"
STATE_MODULE = ROOT / "training/winner_v164_feasibility_preserving_state.py"
CELL_RUNNER = ROOT / "tools/run_winner_v141_projected_final_behavior.py"
DEPLOYER = ROOT / "tools/run_winner_v129_oracle_teacher_cpu_contract.py"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(child.relative_to(path).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(sha256(child)))
    return digest.hexdigest()


def key(row: dict[str, Any]) -> tuple[str, float]:
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
            raise FileExistsError(f"refusing to overwrite V164: {path}")

    v121_prereg = json.loads(V121_PREREG.read_text(encoding="utf-8"))
    v121_result = json.loads(V121_RESULT.read_text(encoding="utf-8"))
    v127_prereg = json.loads(V127_PREREG.read_text(encoding="utf-8"))
    v127_result = json.loads(V127_RESULT.read_text(encoding="utf-8"))
    v163 = json.loads(V163_RESULT.read_text(encoding="utf-8"))
    smoke = (
        Path(v127_result["deployment"]["graphs"]["1024"]["path"]).parent
        / "smoke"
    )
    source_checkpoints = sorted(
        path
        for path in smoke.glob("*_0")
        if path.is_dir() and "_v127_" not in path.name
    )
    proposal_checkpoints = sorted(
        path
        for path in smoke.glob("*_1024")
        if path.is_dir() and "_v127_" not in path.name
    )
    proposal_costs = sorted(
        path for path in smoke.glob("*_1024_v127_cost_value") if path.is_dir()
    )
    proposal_aux = sorted(smoke.glob("*_1024_v127_aux.json"))
    if not (
        len(source_checkpoints)
        == len(proposal_checkpoints)
        == len(proposal_costs)
        == len(proposal_aux)
        == 1
    ):
        raise ValueError("V164 expected one source/proposal/cost/aux state")

    source_raw = sorted(smoke.glob("*_0.onnx"))
    proposal_raw = sorted(smoke.glob("*_1024.onnx"))
    if len(source_raw) != 1 or len(proposal_raw) != 1:
        raise ValueError("V164 expected one source and proposal raw graph")
    source_checkpoint = source_checkpoints[0]
    proposal_checkpoint = proposal_checkpoints[0]
    proposal_cost = proposal_costs[0]
    aux_path = proposal_aux[0]
    source_raw_path = source_raw[0]
    proposal_raw_path = proposal_raw[0]

    half_rows = [
        dict(row)
        for row in v121_prereg["matrix"]["rows"]
        if row["checkpoint_id"] == "V121_TRAIN_MATCHED_HALF"
        and float(row["command_x_m_s"]) > 0.01
    ]
    rows = {key(row): row for row in half_rows}
    risk_order = [
        ("P31_34_PITCH_WITH_P30_NONPITCH", 0.080),
        ("P31_34_PITCH_WITH_P30_NONPITCH", 0.074),
        ("P30_ALL_JOINT", 0.080),
        ("P30_ALL_JOINT", 0.077),
        ("P31_34_PITCH_WITH_P30_NONPITCH", 0.077),
        ("P30_ALL_JOINT", 0.074),
    ]
    matrix = [rows[item] for item in risk_order]

    alpha = 1.0 / 28.0
    source_summary = next(
        row
        for row in v121_result["per_checkpoint"]
        if row["checkpoint_id"] == "V121_TRAIN_MATCHED_HALF"
    )
    input_files = {
        "builder": Path(__file__).resolve(),
        "runner": RUNNER,
        "state_module": STATE_MODULE,
        "cell_runner": CELL_RUNNER,
        "deployer": DEPLOYER,
        "v121_preregistration": V121_PREREG,
        "v121_result": V121_RESULT,
        "v127_preregistration": V127_PREREG,
        "v127_result": V127_RESULT,
        "v163_result": V163_RESULT,
        "v126_preregistration": V126,
        "base_preregistration": BASE,
        "composition_manifest": manifest_path,
        "composed_evaluator": evaluator_path,
        "proposal_aux": aux_path,
        "source_raw": source_raw_path,
        "proposal_raw": proposal_raw_path,
    }
    input_directories = {
        "source_checkpoint": source_checkpoint,
        "proposal_checkpoint": proposal_checkpoint,
        "proposal_cost_checkpoint": proposal_cost,
    }
    checks = {
        "v163_earned_state_contract_only": (
            v163["status"]
            == "PASS_WINNER_V163_FEASIBILITY_PRESERVING_FALSIFIER"
            and v163["decision"]
            == "EARN_V164_FEASIBILITY_PRESERVING_UPDATE_CPU_CONTRACT_ONLY"
        ),
        "source_is_exact_green_v121_half": (
            source_summary["all_eight_cells_pass"]
            and source_summary["cells"] == 8
        ),
        "source_and_proposal_hashes_match_v127": (
            sha256(source_raw_path)
            == v127_result["deployment"]["graphs"]["0"]["raw_sha256"]
            and sha256(proposal_raw_path)
            == v127_result["deployment"]["graphs"]["1024"]["raw_sha256"]
        ),
        "seven_equal_blocks_land_on_half_export": 7 * 28 == 196,
        "fourteen_equal_blocks_land_on_final_export": 14 * 28 == 392,
        "alpha_is_inverse_block_iterations": alpha == 1.0 / 28.0,
        "moving_matrix_exact_six": len(matrix) == 6,
        "cpu_only_no_new_update": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v164.state_coherence_preregistration.v1",
        "status": (
            "PREREGISTERED_WINNER_V164_STATE_COHERENCE"
            if not failed
            else "HOLD_WINNER_V164_STATE_COHERENCE_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {
            **{name: sha256(path) for name, path in input_files.items()},
            **{
                name: directory_sha256(path)
                for name, path in input_directories.items()
            },
        },
        "paths": {
            **{name: str(path) for name, path in input_files.items()},
            **{name: str(path) for name, path in input_directories.items()},
            "playground": v127_prereg["external_paths"]["playground"],
        },
        "state_rule": {
            "block_iterations": 28,
            "blocks_to_half_export": 7,
            "blocks_to_final_export": 14,
            "accepted_alpha": alpha,
            "normalizer": "source exact and frozen",
            "actor": "source + alpha * (proposal - source)",
            "reward_critic": "proposal exact",
            "cost_critic": "proposal exact",
            "dual_state": "proposal exact",
            "optimizer": "fresh zero-moment Adam after backtracking",
            "environment": "fresh deterministic reset after backtracking",
        },
        "matrix": {
            "moving_cells": 6,
            "rows_in_source_margin_risk_order": matrix,
            "x0_cells_reused": 2,
            "x0_basis": (
                "source x0 cells passed and unchanged final deadband makes "
                "the accepted graph exactly zero at x=0"
            ),
        },
        "source_worst_peak_torque_nm": source_summary[
            "worst_peak_torque_nm"
        ],
        "gate": v121_prereg["gate"],
        "decision_rule": {
            "pass": (
                "state composition/export is exact, optimizer reset is finite "
                "and zero-moment, all six moving cells plus both x0 invariants "
                "pass, and worst torque is strictly below the source"
            ),
            "pass_earns": (
                "one separate V165 trainer-integration CPU smoke only"
            ),
            "failure_closes": (
                "actor-only/frozen-normalizer state rule; no alpha or block "
                "length retry"
            ),
            "hosted_training_authorized": False,
        },
        "authority": {
            "cpu_state_and_behavior_contract": not failed,
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
        "# Winner V164 state-coherence preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Fixed 28-iteration blocks land exactly on both 196/392-iteration "
        "exports.\n"
        "- Fixed acceptance alpha: `1/28`; no alternate alpha or block "
        "length.\n"
        "- Source normalizer frozen; actor backtracked; proposal critics and "
        "dual retained; Adam reset.\n"
        "- Passing earns only a separate trainer-integration CPU smoke.\n"
        "- CPU-only; no new PPO update, Colab, Gate 5, RDK-X5, or robot.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
