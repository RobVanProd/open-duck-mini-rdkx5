#!/usr/bin/env python3
"""Preregister V158's shadow-only x=.077 causal census."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RUNNER = ROOT / "tools/run_winner_v158_x077_shadow_census.py"
COMPOSER = ROOT / "tools/compose_winner_v144_shadow_oracle_evaluator.py"
PROJECTOR = ROOT / "tools/exact_torque_oracle_two_fit.py"
V126_PREREG = (
    ANALYSIS / "winner_v126_all_tick_supreme_clip_preregistration.json"
)
BASE_PREREG = (
    ANALYSIS
    / "winner_v3_variable_configuration_replacement_preregistration.json"
)
V140_RESULT = ANALYSIS / "winner_v140_preservation_projected_actor_result.json"
V155_RESULT = (
    ANALYSIS / "winner_v155_velocity_gated_phase_residual_result.json"
)
V157_RESULT = ANALYSIS / "winner_v157_dual_checkpoint_nominal_result.json"
OUTPUT = (
    ANALYSIS / "winner_v158_x077_shadow_census_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V158_X077_SHADOW_CENSUS_PREREGISTRATION_20260725.md"
)


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
            raise FileExistsError(f"refusing to overwrite V158: {path}")
    evaluator_root = args.evaluator_root.resolve()
    manifest_path = evaluator_root / "composition_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    evaluator_path = Path(manifest["output"]["path"])
    v126 = json.loads(V126_PREREG.read_text(encoding="utf-8"))
    v140 = json.loads(V140_RESULT.read_text(encoding="utf-8"))
    v155 = json.loads(V155_RESULT.read_text(encoding="utf-8"))
    v157 = json.loads(V157_RESULT.read_text(encoding="utf-8"))
    policy = Path(v140["artifacts"]["selected_deployed"]["path"])
    row = next(
        row
        for row in v126["matrix"]["rows"]
        if row["checkpoint_id"] == "V121_TRAIN_MATCHED_FINAL"
        and row["plant"] == "P30_ALL_JOINT"
        and float(row["command_x_m_s"]) == 0.077
    )
    paths = {
        "runner": RUNNER,
        "composer": COMPOSER,
        "projector": PROJECTOR,
        "v126_preregistration": V126_PREREG,
        "base_preregistration": BASE_PREREG,
        "v140_result": V140_RESULT,
        "v155_result": V155_RESULT,
        "v157_result": V157_RESULT,
        "composition_manifest": manifest_path,
        "composed_evaluator": evaluator_path,
        "selected_policy": policy,
    }
    input_hashes = {name: sha256(path) for name, path in paths.items()}
    failed_cell = v157["new_final_cells"][0]
    checks = {
        "composed_shadow_evaluator_green": (
            manifest.get("status")
            == "PASS_WINNER_V144_SHADOW_ORACLE_COMPOSITION"
        ),
        "v140_source_graph_green": (
            v140.get("status")
            == "PASS_WINNER_V140_PRESERVATION_PROJECTED_ACTOR"
        ),
        "v155_state_trigger_family_closed": (
            v157.get("decision")
            == "CLOSE_VELOCITY_GATED_PHASE_RESIDUAL"
            and v157.get("status")
            == "HOLD_WINNER_V157_DUAL_CHECKPOINT_NOMINAL"
        ),
        "selected_failure_is_p30_x077_torque_only": (
            failed_cell["failure_reasons"]
            == ["torque_peak_at_most_1p91229675_nm"]
            and failed_cell["identity"]["plant"] == "P30_ALL_JOINT"
            and float(failed_cell["identity"]["command_x_m_s"]) == 0.077
        ),
        "selected_row_exact": (
            row["plant"] == "P30_ALL_JOINT"
            and float(row["command_x_m_s"]) == 0.077
            and int(row["seed"]) == 167_931_544
            and int(row["duration_ticks"]) == 600
        ),
        "one_shadow_cell_only": True,
        "oracle_actions_never_applied": True,
        "no_training_behavior_selection_colab_or_robot": True,
        "closed_v155_policy_not_reused": (
            sha256(policy)
            != v155["artifact"]["deployed"]["sha256"]
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "winner_v158.x077_shadow_census_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V158_X077_SHADOW_CENSUS"
            if not failed
            else "HOLD_WINNER_V158_X077_SHADOW_CENSUS"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": input_hashes,
        "question": (
            "On the unmodified V140 P30 x=.077 trajectory, which joints "
            "and precursor states require exact two-fit torque corrections, "
            "and are all violations controllable?"
        ),
        "matrix": {"cells": 1, "row": row},
        "method": {
            "policy": "unmodified V140 selected deployed graph",
            "oracle": (
                "exact two-fit projection computed and logged every tick"
            ),
            "application": False,
            "census": (
                "all actual torque violations, delay-aligned source ticks, "
                "joint identities, action deltas, and empty intersections"
            ),
        },
        "pass_rule": {
            "trace": "600 ticks, CPU only, no oracle action application",
            "labels": (
                "every actual violation has a nonempty, nonzero, safe "
                "delay-aligned oracle label"
            ),
            "scope": "reporting/diagnosis only; no candidate advancement",
        },
        "stop_rule": (
            "if any violation is unlabeled, empty, or the shadow changes "
            "the policy action, close deployable residual learning from "
            "this source and escalate directly to gait-level redesign"
        ),
        "green_followup": (
            "earn only a read-only mechanism-classification audit; no "
            "training or hosted compute"
        ),
        "authority": {
            "one_cpu_shadow_cell": not failed,
            "mechanism_classification": False,
            "training": False,
            "hosted_training": False,
            "behavior_candidate": False,
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
        "# Winner V158 x=.077 shadow census preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- One CPU shadow trace on unmodified V140; oracle actions are "
        "never applied.\n"
        "- No training, Colab, candidate behavior selection, deployment, "
        "Gate 5, or hardware.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
