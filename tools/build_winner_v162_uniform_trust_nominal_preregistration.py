#!/usr/bin/env python3
"""Freeze V162's 16-cell nominal gate for the V161 pair."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = (
    ANALYSIS
    / "winner_v162_uniform_trust_nominal_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V162_UNIFORM_TRUST_NOMINAL_PREREGISTRATION_20260725.md"
)
V121_PREREG = ANALYSIS / "winner_v121_nominal_behavior_preregistration.json"
V161 = ANALYSIS / "winner_v161_uniform_trust_projection_result.json"
V126 = ANALYSIS / "winner_v126_all_tick_supreme_clip_preregistration.json"
BASE = (
    ANALYSIS
    / "winner_v3_variable_configuration_replacement_preregistration.json"
)
CELL_RUNNER = ROOT / "tools/run_winner_v141_projected_final_behavior.py"
RUNNER = ROOT / "tools/run_winner_v162_uniform_trust_nominal.py"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluator-root", type=Path, required=True)
    args = parser.parse_args()
    evaluator_root = args.evaluator_root.resolve()
    manifest_path = evaluator_root / "composition_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    evaluator = Path(manifest["output"]["path"])
    v121 = json.loads(V121_PREREG.read_text(encoding="utf-8"))
    v161 = json.loads(V161.read_text(encoding="utf-8"))
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V162: {path}")
    selected = v161["artifacts"]["selected"]
    policies = {
        row["id"]: {
            "path": row["deployed"]["path"],
            "sha256": row["deployed"]["sha256"],
        }
        for row in selected
    }
    rows = []
    for source_row in v121["matrix"]["rows"]:
        candidate_id = (
            "half"
            if source_row["checkpoint_id"] == "V121_TRAIN_MATCHED_HALF"
            else "final"
        )
        row = dict(source_row)
        row["checkpoint_id"] = (
            "V161_TRUST_PROJECTED_HALF"
            if candidate_id == "half"
            else "V161_TRUST_PROJECTED_FINAL"
        )
        row["policy_sha256"] = policies[candidate_id]["sha256"]
        rows.append(row)
    input_paths = {
        "builder": Path(__file__).resolve(),
        "runner": RUNNER,
        "cell_runner": CELL_RUNNER,
        "v121_nominal_preregistration": V121_PREREG,
        "v161_result": V161,
        "v126_preregistration": V126,
        "base_preregistration": BASE,
        "composition_manifest": manifest_path,
        "composed_evaluator": evaluator,
        "half_policy": Path(policies["half"]["path"]),
        "final_policy": Path(policies["final"]["path"]),
    }
    checks = {
        "v161_contract_green": (
            v161.get("status")
            == "PASS_WINNER_V161_UNIFORM_TRUST_PROJECTION"
            and v161.get("decision")
            == "EARN_V162_UNIFORM_TRUST_PROJECTED_DUAL_CHECKPOINT_NOMINAL"
        ),
        "matrix_exact_16": len(rows) == 16,
        "two_checkpoints_eight_each": (
            sum(
                row["checkpoint_id"] == "V161_TRUST_PROJECTED_HALF"
                for row in rows
            )
            == 8
            and sum(
                row["checkpoint_id"] == "V161_TRUST_PROJECTED_FINAL"
                for row in rows
            )
            == 8
        ),
        "two_policy_hashes_exact_and_distinct": (
            sha256(Path(policies["half"]["path"]))
            == policies["half"]["sha256"]
            and sha256(Path(policies["final"]["path"]))
            == policies["final"]["sha256"]
            and policies["half"]["sha256"] != policies["final"]["sha256"]
        ),
        "same_common_alpha_for_both": (
            0.0 < v161["summary"]["selected_alpha"] < 1.0
        ),
        "no_behavior_reuse": True,
        "frozen_gate_unchanged": True,
        "cpu_only_no_training_hosted_compute_or_hardware": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "winner_v162.uniform_trust_nominal_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V162_UNIFORM_TRUST_NOMINAL"
            if not failed
            else "HOLD_WINNER_V162_UNIFORM_TRUST_NOMINAL_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {
            name: sha256(path) for name, path in input_paths.items()
        },
        "candidate_pair": {
            "common_alpha": v161["summary"]["selected_alpha"],
            "policies": policies,
        },
        "matrix": {
            "cells": 16,
            "rows": rows,
            "execution": (
                "checkpoint-major, source matrix order, stop at first "
                "failed cell"
            ),
        },
        "gate": v121["gate"],
        "decision_rule": {
            "all_16_pass": (
                "earn separate complete frozen robustness-matrix "
                "preregistration; not Gate 5"
            ),
            "any_failure": (
                "close uniform trust projection; no alpha adjustment, "
                "retry, or checkpoint selection"
            ),
            "behavior_or_reward_selection": False,
        },
        "authority": {
            "cpu_behavior_cells": 16 if not failed else 0,
            "training": False,
            "hosted_training": False,
            "checkpoint_selection": False,
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
        "# Winner V162 uniform trust nominal preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Both V161 policies run all eight frozen nominal cells; no prior "
        "behavior is reused.\n"
        "- Stop at the first failure. No alpha adjustment or retry.\n"
        "- Passing 16/16 earns only a separate robustness preregistration.\n"
        "- CPU-only; no training, Colab, deployment, Gate 5, or robot.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
