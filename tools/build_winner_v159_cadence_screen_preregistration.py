#!/usr/bin/env python3
"""Freeze V159's one-point, CPU-only cadence falsifier."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v159_cadence_screen_preregistration.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V159_CADENCE_SCREEN_PREREGISTRATION_20260725.md"
)
COMPOSER = ROOT / "tools/compose_winner_v159_cadence_evaluator.py"
V140_RESULT = ANALYSIS / "winner_v140_preservation_projected_actor_result.json"
V141_RUNNER = ROOT / "tools/run_winner_v141_projected_final_behavior.py"
V158_CORRECTION = (
    ANALYSIS / "winner_v158_x077_shadow_census_reporting_correction.json"
)
PHASE_ADVANCE_RESULT = ROOT / "docs/PHASE2_RIGHT_SWING_PHASE_ADVANCE_RESULT.md"
RUNTIME = ROOT / "runtime/scripts/v2_rl_walk_mujoco.py"
BASE_FACTOR = 1.0
OFFSET = -0.05
FACTOR = BASE_FACTOR + OFFSET


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
    evaluator_path = Path(manifest["output"]["path"])
    source_manifest_path = Path(manifest["source"]["manifest_path"])
    source_evaluator_path = Path(manifest["source"]["path"])
    v140 = json.loads(V140_RESULT.read_text(encoding="utf-8"))
    v158 = json.loads(V158_CORRECTION.read_text(encoding="utf-8"))
    policy = Path(v140["artifacts"]["selected_deployed"]["path"])
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V159: {path}")
    checks = {
        "composition_pass": (
            manifest.get("status")
            == "PASS_WINNER_V159_CADENCE_EVALUATOR_COMPOSITION"
        ),
        "v158_census_pass": (
            v158.get("status")
            == "PASS_WINNER_V158_X077_SHADOW_CENSUS_REPORTING_CORRECTION"
            and v158.get("decision")
            == "EARN_V159_POLICY_SPACE_REDESIGN_AUDIT"
        ),
        "one_point_not_sweep": FACTOR == 0.95,
        "runtime_knob_exists": (
            "phase_frequency_factor_offset" in RUNTIME.read_text(
                encoding="utf-8"
            )
        ),
        "previous_phase_advance_not_repeated": (
            "HOLD_RIGHT_SWING_PHASE_ADVANCE_RECIPE"
            in PHASE_ADVANCE_RESULT.read_text(encoding="utf-8")
        ),
        "policy_hash_exact": (
            sha256(policy)
            == v140["artifacts"]["selected_deployed"]["sha256"]
        ),
        "cpu_only_no_training_or_hardware": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    row = {
        "checkpoint_id": "V140_SELECTED_FINAL",
        "plant": "P30_ALL_JOINT",
        "command_x_m_s": 0.077,
        "seed": 167931544,
        "duration_ticks": 600,
        "configuration": None,
        "phase_frequency_factor": FACTOR,
        "phase_frequency_factor_offset": OFFSET,
    }
    input_paths = {
        "builder": Path(__file__).resolve(),
        "composer": COMPOSER,
        "source_evaluator_manifest": source_manifest_path,
        "source_evaluator": source_evaluator_path,
        "composition_manifest": manifest_path,
        "composed_evaluator": evaluator_path,
        "v140_result": V140_RESULT,
        "v141_runner": V141_RUNNER,
        "v158_reporting_correction": V158_CORRECTION,
        "phase_advance_result": PHASE_ADVANCE_RESULT,
        "runtime": RUNTIME,
        "selected_policy": policy,
    }
    payload = {
        "schema_version": "winner_v159.cadence_screen_preregistration.v1",
        "status": (
            "PREREGISTERED_WINNER_V159_CADENCE_SCREEN"
            if not failed
            else "HOLD_WINNER_V159_CADENCE_SCREEN_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {
            name: sha256(path) for name, path in input_paths.items()
        },
        "mechanism": {
            "name": "existing runtime cadence offset",
            "base_factor": BASE_FACTOR,
            "offset": OFFSET,
            "factor": FACTOR,
            "magnitude_rule": (
                "one downward controller quantum from the existing runtime; "
                "no fitted scalar and no second point"
            ),
            "causal_direction": (
                "V158 shows safe actions exist but multi-joint tracking lag "
                "creates torque peaks; slower reference transport gives the "
                "same closed loop more physical settling time"
            ),
            "not_repeated": (
                "the closed three-tick phase-advance reward experiment "
                "changed reward timing, not cycle duration"
            ),
        },
        "matrix": {"cells": 1, "row": row},
        "gates": {
            "all_existing_candidate_checks": True,
            "torque_peak_nm_at_most": 1.91229675,
            "duration_ticks_exact": 600,
            "tracking_p95_rad_at_most": 0.20,
            "zero_rate_excess": True,
            "bilateral_transitions": True,
            "positive_command_consistent_motion": True,
        },
        "stop_rule": (
            "if this exact cell fails any candidate check, close cadence "
            "offset as a post-export mechanism; do not try another factor"
        ),
        "advance_rule": (
            "only a green cell earns a separately preregistered 16-cell "
            "dual-checkpoint nominal matrix at the same fixed factor"
        ),
        "authority": {
            "cpu_behavior_screen": not failed,
            "training": False,
            "hosted_training": False,
            "policy_graph_change": False,
            "runtime_config_change": False,
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
        "# Winner V159 cadence screen preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- One CPU-only cell: V140 final, P30, x=.077, seed "
        "167931544, 600 ticks.\n"
        "- Frozen cadence: factor `0.95`, the existing runtime's one-step "
        "offset `-0.05`.\n"
        "- This is one falsifier, not a sweep. Failure closes the "
        "post-export cadence mechanism.\n"
        "- No training, Colab, runtime edit, deployment, Gate 5, or robot.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
