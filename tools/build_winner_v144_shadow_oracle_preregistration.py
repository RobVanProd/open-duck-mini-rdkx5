#!/usr/bin/env python3
"""Preregister one V144 shadow-oracle causal trajectory."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
COMPOSER = ROOT / "tools/compose_winner_v144_shadow_oracle_evaluator.py"
RUNNER = ROOT / "tools/run_winner_v144_shadow_oracle_causal_screen.py"
V126_PREREG = (
    ANALYSIS / "winner_v126_all_tick_supreme_clip_preregistration.json"
)
BASE_PREREG = (
    ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
)
V140_RESULT = ANALYSIS / "winner_v140_preservation_projected_actor_result.json"
V141_PREREG = (
    ANALYSIS / "winner_v141_projected_final_behavior_preregistration.json"
)
V141_RESULT = ANALYSIS / "winner_v141_projected_final_behavior_result.json"
V142_ATTRIBUTION = (
    ANALYSIS / "winner_v142_transferred_load_attribution.json"
)
PROJECTOR = ROOT / "tools/exact_torque_oracle_two_fit.py"
OUTPUT = ANALYSIS / "winner_v144_shadow_oracle_preregistration_v2.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V144_SHADOW_ORACLE_PREREGISTRATION_V2_20260725.md"
)
EXPECTED = {
    "composer": (
        "0218f1104c4f62e7e54bf68938276a831015dffad5b47a734d019a8d65e3ae28"
    ),
    "runner": (
        "e26d8a28c94e38b000b62a0323099cb5af19f5f14bf330be0fd6627ceb91e4e5"
    ),
    "v126_preregistration": (
        "eb40f17d9c08b8362f068567e1620bdafef21ad9123a633c9536f3637a31c899"
    ),
    "base_preregistration": (
        "c8f986ceb24863f33c1fc99170548d2e255cb6a26737d3f74762f8dcd4485a24"
    ),
    "v140_result": (
        "44921665d80235246737b333a5149ceacb702d477dcc2c7496395bf0c42ba637"
    ),
    "v141_preregistration": (
        "40ac2e58d9a8058697e81011f66051840bcc3f81fe278f44e0356e2f532709a0"
    ),
    "v141_result": (
        "08ecfbeb87a09781228d0657e795e106a1f4fae0e60b844f7055dacead21929b"
    ),
    "v142_attribution": (
        "38049a224d0d6190b6415a5691ecbabd9e5915ac8a6b788245abdc08b2234181"
    ),
    "composition_manifest": (
        "f07967333233c179145fc1b3232ca1d076bd55bbdeb1b0397381ed344298b05f"
    ),
    "composed_evaluator": (
        "43bf3373085ccddd6d56a0bc245e033dca67b15599baef6babc8abe24e118de1"
    ),
    "selected_policy": (
        "ae87508d7bd25c7821cb167d7a61d8eeaa28d7d153be72dd9d537236ae5e92f6"
    ),
    "source_trace": (
        "10471d5a15ccf4f55d188778f9226e94f5c5a050061fcb703a7e2e22a0c7a532"
    ),
    "two_fit_projector": (
        "c9894fa982d0837fbd6281dc778248365c9079e60680c928fd34a50c2e55eb27"
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
    parser.add_argument("--evaluator-root", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V144: {path}")
    evaluator_root = args.evaluator_root.resolve()
    manifest_path = evaluator_root / "composition_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    evaluator_path = Path(manifest["output"]["path"])
    v140 = json.loads(V140_RESULT.read_text(encoding="utf-8"))
    v141 = json.loads(V141_RESULT.read_text(encoding="utf-8"))
    v142 = json.loads(V142_ATTRIBUTION.read_text(encoding="utf-8"))
    policy = Path(v140["artifacts"]["selected_deployed"]["path"])
    source_trace = Path(v141["new_final_cells"][1]["trace"]["path"])
    input_hashes = {
        "composer": sha256(COMPOSER),
        "runner": sha256(RUNNER),
        "v126_preregistration": sha256(V126_PREREG),
        "base_preregistration": sha256(BASE_PREREG),
        "v140_result": sha256(V140_RESULT),
        "v141_preregistration": sha256(V141_PREREG),
        "v141_result": sha256(V141_RESULT),
        "v142_attribution": sha256(V142_ATTRIBUTION),
        "composition_manifest": sha256(manifest_path),
        "composed_evaluator": sha256(evaluator_path),
        "selected_policy": sha256(policy),
        "source_trace": sha256(source_trace),
        "two_fit_projector": sha256(PROJECTOR),
    }
    checks = {
        "all_input_hashes_exact": input_hashes == EXPECTED,
        "composed_evaluator_green": (
            manifest.get("status")
            == "PASS_WINNER_V144_SHADOW_ORACLE_COMPOSITION"
        ),
        "v140_cpu_contract_green": (
            v140.get("status")
            == "PASS_WINNER_V140_PRESERVATION_PROJECTED_ACTOR"
        ),
        "v141_single_moving_miss_is_torque_only": (
            v141["new_final_cells"][1]["failure_reasons"]
            == ["torque_peak_at_most_1p91229675_nm"]
        ),
        "v142_selects_torque_only_followup": (
            v142.get("status")
            == "PASS_WINNER_V142_TRANSFERRED_LOAD_ATTRIBUTION"
        ),
        "one_frozen_cell_only": True,
        "shadow_oracle_does_not_apply_actions": True,
        "training_not_authorized": True,
        "robot_surface_absent": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v144.shadow_oracle_preregistration.v2",
        "status": (
            "PREREGISTERED_WINNER_V144_SHADOW_ORACLE_CAUSAL_SCREEN"
            if not failed
            else "HOLD_WINNER_V144_SHADOW_ORACLE_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": input_hashes,
        "supersedes": {
            "artifact": "winner_v144_shadow_oracle_preregistration.json",
            "reason": (
                "The first invocation stopped before evaluator loading "
                "because the runner's observed-hash map omitted the already "
                "frozen composer entry present in the preregistration. V2 "
                "adds only that provenance key; the cell, evaluator, method, "
                "pass rules, and stop rules are unchanged."
            ),
        },
        "question": (
            "Does the exact two-fit oracle directly label the controllable "
            "precursor of every torque event on the unmodified V140 "
            "closed-loop trajectory?"
        ),
        "matrix": {
            "cells": 1,
            "checkpoint": "V140 projected final",
            "plant": "P30_ALL_JOINT",
            "command_x_m_s": 0.074,
            "seed": 167931544,
            "ticks": 600,
        },
        "method": {
            "policy_action_committed": "unmodified V140 action",
            "teacher_action": (
                "two-fit exact torque projection computed and logged only"
            ),
            "trajectory_identity": (
                "action, force, qpos, qvel, and obs must reproduce the "
                "frozen V141 trace exactly"
            ),
            "event_label": (
                "each actual torque violation must have a non-empty, "
                "nonzero, safe oracle correction at its delay-aligned "
                "source tick"
            ),
        },
        "pass_rule": {
            "trace": "exact 600-tick source-trajectory reproduction",
            "failure": "same right-ankle peak at tick 397; torque only",
            "oracle": (
                "zero empty intersections and every actual violation has "
                "a safe nonzero delay-aligned precursor label"
            ),
        },
        "stop_rule": (
            "if the shadow computation changes the trajectory, misses the "
            "right-ankle precursor, or finds any unlabeled/empty event, "
            "close DAgger from V140; do not train"
        ),
        "authority": {
            "one_cpu_shadow_cell": not failed,
            "dagger_cpu_preregistration": False,
            "training": False,
            "hosted_training": False,
            "behavior_beyond_one_shadow_cell": False,
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
        "# Winner V144 shadow-oracle preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- One frozen P30/x=.074/final trace.\n"
        "- Oracle computes labels in shadow mode; policy actions remain "
        "unchanged.\n"
        "- No training, Colab, policy deployment, or hardware authority.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
