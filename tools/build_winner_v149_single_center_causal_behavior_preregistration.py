#!/usr/bin/env python3
"""Preregister V149's one-cell causal behavior test."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RUNNER = ROOT / "tools/run_winner_v149_single_center_causal_behavior.py"
V141_RUNNER = ROOT / "tools/run_winner_v141_projected_final_behavior.py"
V141_RESULT = ANALYSIS / "winner_v141_projected_final_behavior_result.json"
V148_RESULT = ANALYSIS / "winner_v148_single_center_residual_result.json"
V126_PREREG = (
    ANALYSIS / "winner_v126_all_tick_supreme_clip_preregistration.json"
)
BASE_PREREG = (
    ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
)
OUTPUT = (
    ANALYSIS
    / "winner_v149_single_center_causal_behavior_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V149_SINGLE_CENTER_CAUSAL_BEHAVIOR_PREREGISTRATION_20260725.md"
)
EXPECTED = {
    "runner": (
        "4103c421022964df2e69892d89fba4cbae04081e98bf7616eafcefbcef2340f1"
    ),
    "v141_behavior_result": (
        "08ecfbeb87a09781228d0657e795e106a1f4fae0e60b844f7055dacead21929b"
    ),
    "v148_residual_result": (
        "a7c0087dc18db1b4371b3ea7598bf768bb55fef881b57b0732e97e766be72d3d"
    ),
    "v126_preregistration": (
        "eb40f17d9c08b8362f068567e1620bdafef21ad9123a633c9536f3637a31c899"
    ),
    "v141_runner": (
        "41cc51abb21dde2fde8fa4cbf36ad50212794fea0a38eb73b2c3705ee96ac034"
    ),
    "base_preregistration": (
        "c8f986ceb24863f33c1fc99170548d2e255cb6a26737d3f74762f8dcd4485a24"
    ),
    "composition_manifest": (
        "39e842470828208dfea08b17d936d3f0e6f0d45b8f9813a1edd139692e4a6f74"
    ),
    "composed_evaluator": (
        "1539ba18b5b207a15538a8a8611475f5c73bcd7164f2fe039cad8b279a587e43"
    ),
    "selected_policy": (
        "4d5e3a69ce33fcdce6e714c180f8533b551d604aee5edb8d0b0b143a1a0f1f4b"
    ),
    "local_raw": (
        "d60b9c59710bd8f636a6cbe28086fb702a6d15aaf3b249668ada7631a5aca214"
    ),
    "shadow_trace": (
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
    parser.add_argument("--shadow-trace", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V149: {path}")
    evaluator_root = args.evaluator_root.resolve()
    shadow_trace = args.shadow_trace.resolve()
    manifest_path = evaluator_root / "composition_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    evaluator_path = Path(manifest["output"]["path"])
    v141 = json.loads(V141_RESULT.read_text(encoding="utf-8"))
    v148 = json.loads(V148_RESULT.read_text(encoding="utf-8"))
    policy = Path(v148["artifact"]["deployed"]["path"])
    local_raw = Path(v148["artifact"]["raw"]["path"])
    input_hashes = {
        "runner": sha256(RUNNER),
        "v141_behavior_result": sha256(V141_RESULT),
        "v148_residual_result": sha256(V148_RESULT),
        "v126_preregistration": sha256(V126_PREREG),
        "v141_runner": sha256(V141_RUNNER),
        "base_preregistration": sha256(BASE_PREREG),
        "composition_manifest": sha256(manifest_path),
        "composed_evaluator": sha256(evaluator_path),
        "selected_policy": sha256(policy),
        "local_raw": sha256(local_raw),
        "shadow_trace": sha256(shadow_trace),
    }
    failing = v141["new_final_cells"][1]
    row = failing["identity"]
    checks = {
        "all_input_hashes_exact": input_hashes == EXPECTED,
        "v148_graph_contract_green": (
            v148.get("status")
            == "PASS_WINNER_V148_SINGLE_CENTER_RESIDUAL"
            and v148.get("failed_checks") == []
            and v148.get("aggregate", {}).get("gate_rows") == [5_194]
            and v148.get("aggregate", {}).get("changed_elements")
            == [[5_194, 13]]
        ),
        "selected_cell_is_exact_v141_torque_only_failure": (
            failing["failure_reasons"]
            == ["torque_peak_at_most_1p91229675_nm"]
            and str(row["plant"]) == "P30_ALL_JOINT"
            and float(row["command_x_m_s"]) == 0.074
            and int(row["seed"]) == 167_931_544
            and int(row["duration_ticks"]) == 600
        ),
        "source_cell_other_gates_green": (
            failing["metrics"]["candidate_gate_status"]
            == "PASS_CANDIDATE_SIM_GATE"
            and failing["prospective_current_gate"]["pass"]
            and failing["torque_gate"]["worst_peak_torque_nm"]
            > 1.91229675
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
            "winner_v149.single_center_causal_behavior_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V149_SINGLE_CENTER_CAUSAL_BEHAVIOR"
            if not failed
            else "HOLD_WINNER_V149_SINGLE_CENTER_CAUSAL_BEHAVIOR_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": input_hashes,
        "matrix": {
            "rows": 1,
            "row": row,
            "reason": (
                "the exact P30 x=.074 seed cell that isolated V140's sole "
                "right-ankle torque failure"
            ),
        },
        "causal_contract": {
            "prefix": (
                "obs, h_in, and actions remain exact to the V144 source "
                "through the tick-394 precursor"
            ),
            "intervention": (
                "only action index 13 changes at tick 394 and matches the "
                "frozen exact-oracle target within 1e-7"
            ),
            "activation": "the local graph gate fires only at tick 394",
            "outcome": (
                "all frozen gait, duration, tracking, torque, current, "
                "saturation, guard, and rate gates pass"
            ),
        },
        "pass_rule": (
            "the one causal cell and every causal-contract check pass"
        ),
        "stop_rule": (
            "any failure closes the single-center local residual; do not "
            "change its center, radius, correction, or feature"
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
        "# Winner V149 single-center causal behavior preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- One CPU cell: P30, x=.074, seed 167931544, 600 ticks.\n"
        "- Require an exact source prefix, one tick-394 right-ankle "
        "intervention, and every frozen behavior gate green.\n"
        "- No training, Colab, deployment, Gate 5, or hardware.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
