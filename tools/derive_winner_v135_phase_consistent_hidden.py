#!/usr/bin/env python3
"""Derive and contract a phase-consistent recurrent warm-start state."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = ""

import numpy as np
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREG = (
    ANALYSIS / "winner_v135_phase_consistent_hidden_preregistration.json"
)
V126_PREREG = (
    ANALYSIS / "winner_v126_all_tick_supreme_clip_preregistration.json"
)
V131_RESULT = ANALYSIS / "winner_v131_two_fit_oracle_behavior_result.json"
V134_RESULT = ANALYSIS / "winner_v134_full_actor_teacher_cpu_result_v3.json"
PERIOD_RESULT = ANALYSIS / "winner_v11_zero_ppo_cpu_mechanics_result.json"
TRANSFORM = ANALYSIS / "winner_v121_deployment_transform_contract.json"
VECTOR = ANALYSIS / "winner_v135_phase_consistent_hidden_vector.json"
OUTPUT = ANALYSIS / "winner_v135_phase_consistent_hidden_contract.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V135_PHASE_CONSISTENT_HIDDEN_CONTRACT_20260725.md"
)
EXPECTED_PERIOD_TICKS = 27
EXPECTED_ROWS = 600
FINAL_PHASE_ZERO_TICK = 594


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_trace(path: Path) -> list[dict]:
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]
    if len(rows) != EXPECTED_ROWS:
        raise ValueError(f"V135 trace is not 600 rows: {path}")
    return rows


def run_policy(
    session: ort.InferenceSession,
    obs: np.ndarray,
    hidden: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    outputs = session.run(
        ["continuous_actions", "previous_action_out", "h_out"],
        {
            "obs": obs.astype(np.float32)[None, :],
            "previous_action": np.zeros((1, 14), dtype=np.float32),
            "h_in": hidden.astype(np.float32)[None, :],
        },
    )
    return tuple(np.asarray(value, dtype=np.float32) for value in outputs)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--teacher-run-root", type=Path, required=True)
    args = parser.parse_args()
    for path in (VECTOR, OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V135: {path}")
    run_root = args.teacher_run_root.resolve()
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    v126 = json.loads(V126_PREREG.read_text(encoding="utf-8"))
    v131 = json.loads(V131_RESULT.read_text(encoding="utf-8"))
    v134 = json.loads(V134_RESULT.read_text(encoding="utf-8"))
    period = json.loads(PERIOD_RESULT.read_text(encoding="utf-8"))
    transform = json.loads(TRANSFORM.read_text(encoding="utf-8"))["transform"]
    traces = sorted((run_root / "traces").glob("*_x0.000_*.jsonl"))
    if len(traces) != 2:
        raise ValueError("V135 requires exactly the two final x=0 traces")
    observed_hashes = {
        "runner": sha256(Path(__file__).resolve()),
        "v126_preregistration": sha256(V126_PREREG),
        "v131_behavior_result": sha256(V131_RESULT),
        "v134_full_actor_result": sha256(V134_RESULT),
        "phase_period_result": sha256(PERIOD_RESULT),
        "v121_transform": sha256(TRANSFORM),
        "p30_x0_trace": sha256(
            next(path for path in traces if "p30_all_joint" in path.name)
        ),
        "p31_34_x0_trace": sha256(
            next(path for path in traces if "p31_34" in path.name)
        ),
    }
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V135_PHASE_CONSISTENT_HIDDEN"
        or prereg.get("failed_checks") != []
        or prereg.get("input_hashes") != observed_hashes
    ):
        raise ValueError("V135 preregistration changed")
    rows_by_trace = [read_trace(path) for path in traces]
    phase_zero_ticks = [
        index
        for index, row in enumerate(rows_by_trace[0])
        if np.array_equal(
            np.asarray(row["obs_state"][99:101], dtype=np.float32),
            np.asarray([1.0, 0.0], dtype=np.float32),
        )
    ]
    hidden_sequences = [
        np.stack(
            [
                np.asarray(
                    row["policy_state_input"]["h_in"][0],
                    dtype=np.float32,
                )
                for row in rows
            ]
        )
        for rows in rows_by_trace
    ]
    hidden_cross_plant_error = float(
        np.max(np.abs(hidden_sequences[0] - hidden_sequences[1]))
    )
    warm = hidden_sequences[0][FINAL_PHASE_ZERO_TICK].copy()
    phase_cycle_deltas = [
        float(
            np.linalg.norm(
                hidden_sequences[0][tick]
                - hidden_sequences[0][tick - EXPECTED_PERIOD_TICKS]
            )
        )
        for tick in phase_zero_ticks
        if tick >= EXPECTED_PERIOD_TICKS
    ]
    policy_spec = next(
        item
        for item in v126["policies"]
        if item["id"] == "V121_TRAIN_MATCHED_FINAL"
    )
    policy = (
        Path(v126["external_inputs"]["policy_root"])
        / policy_spec["filename"]
    )
    if sha256(policy) != policy_spec["sha256"]:
        raise ValueError("V135 source policy changed")
    session = ort.InferenceSession(
        policy.read_bytes(), providers=["CPUExecutionProvider"]
    )
    x0_action, x0_previous, x0_hidden = run_policy(
        session,
        np.asarray(rows_by_trace[0][0]["obs_state"], dtype=np.float32),
        warm,
    )
    moving_rows = [
        (path, read_trace(path)[0])
        for path in sorted(
            (run_root / "traces").glob("*_x0.080_*.jsonl")
        )
    ]
    moving_audits = []
    action_delta = np.asarray(
        transform["exact_train_normalized_action_delta"],
        dtype=np.float32,
    )
    for trace_path, row in moving_rows:
        obs = np.asarray(row["obs_state"], dtype=np.float32)
        warm_action, warm_previous, warm_hidden = run_policy(
            session, obs, warm
        )
        zero_action, _, zero_hidden = run_policy(
            session, obs, np.zeros(64, dtype=np.float32)
        )
        moving_audits.append(
            {
                "trace": trace_path.name,
                "warm_action": warm_action[0].astype(float).tolist(),
                "zero_hidden_action": zero_action[0].astype(float).tolist(),
                "warm_vs_zero_action_linf": float(
                    np.max(np.abs(warm_action - zero_action))
                ),
                "warm_action_delta_excess": float(
                    np.max(np.maximum(np.abs(warm_action[0]) - action_delta, 0.0))
                ),
                "previous_output_error": float(
                    np.max(np.abs(warm_previous - warm_action))
                ),
                "warm_hidden_norm": float(np.linalg.norm(warm_hidden)),
                "zero_hidden_output_norm": float(np.linalg.norm(zero_hidden)),
            }
        )
    vector_payload = {
        "schema_version": "winner_v135.phase_consistent_hidden_vector.v1",
        "source_policy_id": policy_spec["id"],
        "source_policy_sha256": policy_spec["sha256"],
        "derivation": {
            "source": "V131 final x=0 home-hold policy_state_input.h_in",
            "phase_period_ticks": EXPECTED_PERIOD_TICKS,
            "selected_tick": FINAL_PHASE_ZERO_TICK,
            "selected_phase": [1.0, 0.0],
            "selection_rule": (
                "last complete phase-zero tick strictly inside the frozen "
                "600-tick home hold"
            ),
        },
        "h_in": warm.astype(float).tolist(),
    }
    VECTOR.write_text(
        json.dumps(vector_payload, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    period_candidates = []
    for value in period.values():
        if isinstance(value, dict) and "phase_period_ticks" in value:
            period_candidates.append(value["phase_period_ticks"])
    checks = {
        "v131_teacher_green": (
            v131.get("status")
            == "PASS_WINNER_V131_TWO_FIT_ORACLE_BEHAVIOR_VALID_RESULT"
            and v131.get("summary", {}).get("passing_cells") == 8
        ),
        "v134_teacher_distillation_closed": (
            v134.get("status")
            == "HOLD_WINNER_V134_FULL_ACTOR_TEACHER_CPU_CONTRACT"
            and v134.get("decision")
            == "NO_FULL_ACTOR_TEACHER_DISTILLATION"
        ),
        "two_x0_traces_exact": len(rows_by_trace) == 2,
        "phase_period_27_source_backed": (
            EXPECTED_PERIOD_TICKS in period_candidates
            or json.dumps(period).count('"phase_period_ticks": 27') > 0
        ),
        "phase_zero_ticks_exact": phase_zero_ticks
        == list(range(0, EXPECTED_ROWS, EXPECTED_PERIOD_TICKS)),
        "selected_tick_594": phase_zero_ticks[-1] == FINAL_PHASE_ZERO_TICK,
        "cross_plant_hidden_bit_exact": hidden_cross_plant_error == 0.0,
        "warm_vector_shape_64": warm.shape == (64,),
        "warm_vector_finite": bool(np.all(np.isfinite(warm))),
        "warm_vector_nonzero": float(np.linalg.norm(warm)) > 1.0,
        "x0_action_exact_zero": np.count_nonzero(x0_action) == 0,
        "x0_previous_exact_zero": np.count_nonzero(x0_previous) == 0,
        "x0_hidden_output_finite": bool(np.all(np.isfinite(x0_hidden))),
        "two_moving_tick_zero_audits": len(moving_audits) == 2,
        "moving_outputs_finite": all(
            all(
                math.isfinite(float(value))
                for value in (
                    row["warm_vs_zero_action_linf"],
                    row["warm_action_delta_excess"],
                    row["previous_output_error"],
                    row["warm_hidden_norm"],
                    row["zero_hidden_output_norm"],
                )
            )
            for row in moving_audits
        ),
        "moving_first_action_rate_bound_exact": all(
            row["warm_action_delta_excess"] <= 1.0e-7
            for row in moving_audits
        ),
        "moving_previous_output_exact": all(
            row["previous_output_error"] == 0.0 for row in moving_audits
        ),
        "cpu_inference_only": session.get_providers()
        == ["CPUExecutionProvider"],
        "no_training_behavior_or_hosted_compute": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v135.phase_consistent_hidden_contract.v1",
        "status": (
            "PASS_WINNER_V135_PHASE_CONSISTENT_HIDDEN_CONTRACT"
            if not failed
            else "HOLD_WINNER_V135_PHASE_CONSISTENT_HIDDEN_CONTRACT"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": observed_hashes,
        "vector": {
            "path": str(VECTOR),
            "sha256": sha256(VECTOR),
            "l2_norm": float(np.linalg.norm(warm)),
            "linf": float(np.max(np.abs(warm))),
        },
        "phase_zero_ticks": phase_zero_ticks,
        "phase_cycle_hidden_l2_delta": {
            "last": phase_cycle_deltas[-1],
            "minimum": min(phase_cycle_deltas),
            "median": float(np.median(phase_cycle_deltas)),
            "maximum": max(phase_cycle_deltas),
        },
        "cross_plant_hidden_linf": hidden_cross_plant_error,
        "moving_tick_zero": moving_audits,
        "decision": (
            "EARN_ONE_V136_WARM_START_STARTUP_SCREEN_PREREGISTRATION"
            if not failed
            else "NO_WARM_START_SCREEN"
        ),
        "authority": {
            "v136_startup_screen_preregistration": not failed,
            "formal_behavior": False,
            "training": False,
            "hosted_training": False,
            "full_matrix": False,
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
        "# Winner V135 phase-consistent hidden contract\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Warm-state tick/period: `{FINAL_PHASE_ZERO_TICK}` / "
        f"`{EXPECTED_PERIOD_TICKS}`.\n"
        f"- Hidden norm: `{payload['vector']['l2_norm']}`.\n"
        f"- Decision: `{payload['decision']}`\n"
        "- CPU inference only; no behavior, training, Colab, or hardware "
        "authority.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(payload["decision"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
