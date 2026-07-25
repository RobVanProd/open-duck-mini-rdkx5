#!/usr/bin/env python3
"""Preregister V154's one-cell phase/contact causal behavior test."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RUNNER = ROOT / "tools/run_winner_v154_phase_contact_causal_behavior.py"
V126_PREREG = (
    ANALYSIS / "winner_v126_all_tick_supreme_clip_preregistration.json"
)
BASE_PREREG = (
    ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
)
V141_RESULT = ANALYSIS / "winner_v141_projected_final_behavior_result.json"
V144_CORRECTION = (
    ANALYSIS / "winner_v144_shadow_oracle_reporting_correction.json"
)
V153_RESULT = ANALYSIS / "winner_v153_phase_contact_residual_result.json"
V141_RUNNER = ROOT / "tools/run_winner_v141_projected_final_behavior.py"
OUTPUT = (
    ANALYSIS
    / "winner_v154_phase_contact_causal_behavior_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V154_PHASE_CONTACT_CAUSAL_BEHAVIOR_PREREGISTRATION_20260725.md"
)
EXPECTED = {
    "runner": (
        "7b4b86d50e134be6a04fa63059ede86d3f1e725ccd36db0a3888114daf74f51d"
    ),
    "v126_preregistration": (
        "eb40f17d9c08b8362f068567e1620bdafef21ad9123a633c9536f3637a31c899"
    ),
    "base_preregistration": (
        "c8f986ceb24863f33c1fc99170548d2e255cb6a26737d3f74762f8dcd4485a24"
    ),
    "v141_result": (
        "08ecfbeb87a09781228d0657e795e106a1f4fae0e60b844f7055dacead21929b"
    ),
    "v144_correction": (
        "4d955dacf6d30a0953c306ab6e7d9a1d87fea872a8b646aebd48c9e528c0dd0c"
    ),
    "v153_result": (
        "4548d098902dd260561fb10e3c0a437c68980e9c775cb9c08423336afbf2ee1f"
    ),
    "v141_runner": (
        "41cc51abb21dde2fde8fa4cbf36ad50212794fea0a38eb73b2c3705ee96ac034"
    ),
    "composition_manifest": (
        "39e842470828208dfea08b17d936d3f0e6f0d45b8f9813a1edd139692e4a6f74"
    ),
    "composed_evaluator": (
        "1539ba18b5b207a15538a8a8611475f5c73bcd7164f2fe039cad8b279a587e43"
    ),
    "selected_policy": (
        "3dcb79e1b351c671725665e4c086e1efd85c8054d23b8400e939ad1c632957e8"
    ),
    "local_raw": (
        "53ba507537161e52425579c4c4ec2e7c88e1c9f66065199905e007038fcd05e7"
    ),
    "source_trace": (
        "eb432bdb64c251dcbb466bd795db381891837086dae9dcc7a2564a7f2a2930b5"
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
    parser.add_argument("--source-trace", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V154: {path}")
    evaluator_root = args.evaluator_root.resolve()
    source_trace = args.source_trace.resolve()
    manifest_path = evaluator_root / "composition_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    evaluator_path = Path(manifest["output"]["path"])
    v141 = json.loads(V141_RESULT.read_text(encoding="utf-8"))
    v144 = json.loads(V144_CORRECTION.read_text(encoding="utf-8"))
    v153 = json.loads(V153_RESULT.read_text(encoding="utf-8"))
    policy = Path(v153["artifact"]["deployed"]["path"])
    local_raw = Path(v153["artifact"]["raw"]["path"])
    input_hashes = {
        "runner": sha256(RUNNER),
        "v126_preregistration": sha256(V126_PREREG),
        "base_preregistration": sha256(BASE_PREREG),
        "v141_result": sha256(V141_RESULT),
        "v144_correction": sha256(V144_CORRECTION),
        "v153_result": sha256(V153_RESULT),
        "v141_runner": sha256(V141_RUNNER),
        "composition_manifest": sha256(manifest_path),
        "composed_evaluator": sha256(evaluator_path),
        "selected_policy": sha256(policy),
        "local_raw": sha256(local_raw),
        "source_trace": sha256(source_trace),
    }
    failing = v141["new_final_cells"][1]
    row = failing["identity"]
    checks = {
        "all_input_hashes_exact": input_hashes == EXPECTED,
        "v153_graph_contract_green": (
            v153.get("status")
            == "PASS_WINNER_V153_PHASE_CONTACT_RESIDUAL"
            and v153.get("failed_checks") == []
            and v153.get("checks", {}).get(
                "changes_only_inside_phase_contact_gate"
            )
            and v153.get("checks", {}).get("changes_only_right_ankle")
        ),
        "selected_cell_is_exact_v141_torque_only_failure": (
            failing["failure_reasons"]
            == ["torque_peak_at_most_1p91229675_nm"]
            and str(row["plant"]) == "P30_ALL_JOINT"
            and float(row["command_x_m_s"]) == 0.074
            and int(row["seed"]) == 167_931_544
            and int(row["duration_ticks"]) == 600
        ),
        "source_event_has_exact_causal_label": (
            v144.get("status")
            == "PASS_WINNER_V144_SHADOW_ORACLE_REPORTING_CORRECTION"
            and v144["causal_result"]["peak_event"]["tick"] == 397
            and v144["causal_result"]["peak_event"]["source_tick"] == 394
        ),
        "one_cell_only": True,
        "stop_after_cell": True,
        "training_and_oracle_disabled": True,
        "robot_surface_absent": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "winner_v154.phase_contact_causal_behavior_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V154_PHASE_CONTACT_CAUSAL_BEHAVIOR"
            if not failed
            else "HOLD_WINNER_V154_PHASE_CONTACT_CAUSAL_BEHAVIOR_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": input_hashes,
        "matrix": {
            "rows": 1,
            "row": row,
            "reason": (
                "the exact P30 x=.074 seed cell that isolated V140's "
                "right-ankle torque event"
            ),
        },
        "causal_contract": {
            "prefix": (
                "source trajectory remains bit-exact through the first "
                "phase/contact activation state"
            ),
            "first_intervention": (
                "tick 43 changes only right ankle by the frozen correction"
            ),
            "periodicity": (
                "21 activations from tick 43 through 583, exactly 27 ticks "
                "apart, under right-foot support"
            ),
            "outcome": (
                "all frozen gait, duration, tracking, torque, current, "
                "saturation, guard, and rate gates pass"
            ),
        },
        "pass_rule": (
            "the one causal cell and every causal-contract check pass"
        ),
        "stop_rule": (
            "any failure closes the phase/contact residual; do not change "
            "phase, contact, radius, amplitude, or tolerance"
        ),
        "green_followup": (
            "earn only a preregistration for the remaining dual-checkpoint "
            "offline matrix; no deployment or Gate 5"
        ),
        "authority": {
            "behavior_cells": 1 if not failed else 0,
            "additional_behavior": False,
            "training": False,
            "hosted_training": False,
            "policy_deployment": False,
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
        "# Winner V154 phase/contact causal behavior preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- One CPU cell: P30, x=.074, seed 167931544, 600 ticks.\n"
        "- Require exact prefix, 27-tick periodic right-ankle "
        "interventions, and every frozen behavior gate green.\n"
        "- No training, Colab, deployment, Gate 5, or hardware.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
