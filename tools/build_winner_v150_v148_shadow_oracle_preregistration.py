#!/usr/bin/env python3
"""Preregister one V150 shadow-oracle diagnostic on V148."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RUNNER = ROOT / "tools/run_winner_v150_v148_shadow_oracle.py"
V126_PREREG = (
    ANALYSIS / "winner_v126_all_tick_supreme_clip_preregistration.json"
)
BASE_PREREG = (
    ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
)
V148_RESULT = ANALYSIS / "winner_v148_single_center_residual_result.json"
V149_RESULT = (
    ANALYSIS / "winner_v149_single_center_causal_behavior_result.json"
)
V144_COMPOSER = ROOT / "tools/compose_winner_v144_shadow_oracle_evaluator.py"
PROJECTOR = ROOT / "tools/exact_torque_oracle_two_fit.py"
OUTPUT = ANALYSIS / "winner_v150_v148_shadow_oracle_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "WINNER_V150_V148_SHADOW_ORACLE_PREREGISTRATION_20260725.md"
)
EXPECTED = {
    "runner": (
        "d29c62ba6c8c97461da07f4503e42aae9d8eb4551df02e426ac934c18243e402"
    ),
    "v126_preregistration": (
        "eb40f17d9c08b8362f068567e1620bdafef21ad9123a633c9536f3637a31c899"
    ),
    "base_preregistration": (
        "c8f986ceb24863f33c1fc99170548d2e255cb6a26737d3f74762f8dcd4485a24"
    ),
    "v148_result": (
        "a7c0087dc18db1b4371b3ea7598bf768bb55fef881b57b0732e97e766be72d3d"
    ),
    "v149_result": (
        "67ac7db8517bd72c32bf3b171e400aa40a73508d8acc3eaf8d33373fef0654f1"
    ),
    "v144_composer": (
        "0218f1104c4f62e7e54bf68938276a831015dffad5b47a734d019a8d65e3ae28"
    ),
    "two_fit_projector": (
        "c9894fa982d0837fbd6281dc778248365c9079e60680c928fd34a50c2e55eb27"
    ),
    "composition_manifest": (
        "f07967333233c179145fc1b3232ca1d076bd55bbdeb1b0397381ed344298b05f"
    ),
    "composed_evaluator": (
        "43bf3373085ccddd6d56a0bc245e033dca67b15599baef6babc8abe24e118de1"
    ),
    "selected_policy": (
        "4d5e3a69ce33fcdce6e714c180f8533b551d604aee5edb8d0b0b143a1a0f1f4b"
    ),
    "source_trace": (
        "31eb42dd5b145ed23fb9b56f869a4645cc5917012792ba4c0a333fc1b474f3a4"
    ),
}
TORQUE_LIMIT = 1.91229675


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
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V150: {path}")
    evaluator_root = args.evaluator_root.resolve()
    manifest_path = evaluator_root / "composition_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    evaluator_path = Path(manifest["output"]["path"])
    v148 = json.loads(V148_RESULT.read_text(encoding="utf-8"))
    v149 = json.loads(V149_RESULT.read_text(encoding="utf-8"))
    policy = Path(v148["artifact"]["deployed"]["path"])
    source_trace = Path(v149["cell"]["trace"]["path"])
    input_hashes = {
        "runner": sha256(RUNNER),
        "v126_preregistration": sha256(V126_PREREG),
        "base_preregistration": sha256(BASE_PREREG),
        "v148_result": sha256(V148_RESULT),
        "v149_result": sha256(V149_RESULT),
        "v144_composer": sha256(V144_COMPOSER),
        "two_fit_projector": sha256(PROJECTOR),
        "composition_manifest": sha256(manifest_path),
        "composed_evaluator": sha256(evaluator_path),
        "selected_policy": sha256(policy),
        "source_trace": sha256(source_trace),
    }
    rows = [
        json.loads(line)
        for line in source_trace.read_text(encoding="utf-8").splitlines()
        if line
    ]
    forces = np.abs(
        np.asarray(
            [row["actuator_force_nm"] for row in rows], dtype=np.float64
        )
    )
    violations = np.argwhere(forces > TORQUE_LIMIT)
    checks = {
        "all_input_hashes_exact": input_hashes == EXPECTED,
        "v148_graph_contract_green": (
            v148.get("status")
            == "PASS_WINNER_V148_SINGLE_CENTER_RESIDUAL"
        ),
        "v149_exact_causal_intervention_but_torque_hold": (
            v149.get("status")
            == "HOLD_WINNER_V149_SINGLE_CENTER_CAUSAL_BEHAVIOR"
            and v149.get("causal_contract", {}).get("failed_checks") == []
            and v149.get("failed_checks")
            == ["cell_all_frozen_gates_pass", "torque_event_removed"]
        ),
        "source_has_exact_single_displaced_event": (
            violations.tolist() == [[586, 13]]
            and 1.9200 < float(forces[586, 13]) < 1.9201
        ),
        "source_other_behavior_gates_green": (
            v149["cell"]["metrics"]["candidate_gate_status"]
            == "PASS_CANDIDATE_SIM_GATE"
            and v149["cell"]["prospective_current_gate"]["pass"]
        ),
        "one_shadow_cell_only": True,
        "shadow_actions_not_applied": True,
        "training_not_authorized": True,
        "robot_surface_absent": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "winner_v150.v148_shadow_oracle_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V150_V148_SHADOW_ORACLE"
            if not failed
            else "HOLD_WINNER_V150_V148_SHADOW_ORACLE_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": input_hashes,
        "question": (
            "Is V148's new tick-586 right-ankle event preventable by a "
            "safe, nonempty delay-aligned exact-oracle action?"
        ),
        "matrix": {
            "cells": 1,
            "row": v149["cell"]["identity"],
            "policy": str(policy),
            "ticks": 600,
        },
        "method": {
            "trajectory": "exact reproduction of the frozen V149 trace",
            "oracle": "two-fit exact torque oracle in shadow mode",
            "committed_action": "unchanged V148 graph action",
            "selection_weight": 0,
        },
        "pass_rule": {
            "reproduction": (
                "action, force, qpos, qvel, and obs are bit-exact to V149"
            ),
            "event": "exactly one actual violation at tick 586 joint 13",
            "label": (
                "the event has a nonempty, nonzero, safe delay-aligned "
                "oracle label"
            ),
        },
        "stop_rule": (
            "any reproduction or label failure closes the finite-local "
            "residual family; no policy modification or hosted run"
        ),
        "green_followup": (
            "earn only a separate bounded two-center CPU graph "
            "preregistration; the single-center mechanism remains closed"
        ),
        "authority": {
            "one_cpu_shadow_cell": not failed,
            "policy_change": False,
            "behavior_selection": False,
            "training": False,
            "hosted_training": False,
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
        "# Winner V150 V148 shadow-oracle preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- One P30/x=.074/seed-167931544 shadow replay.\n"
        "- Diagnose the new tick-586 right-ankle event without applying "
        "oracle actions.\n"
        "- No policy change, behavior selection, training, Colab, "
        "deployment, or hardware.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
