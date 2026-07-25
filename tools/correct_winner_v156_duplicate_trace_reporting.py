#!/usr/bin/env python3
"""Correct V156 reporting after two identical runs appended one trace."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from run_winner_v156_state_triggered_causal_behavior import (  # noqa: E402
    gate_from_graph,
)


ANALYSIS = ROOT / "outputs/analysis"
PREREG = (
    ANALYSIS
    / "winner_v156_state_triggered_causal_behavior_preregistration.json"
)
RAW_RESULT = (
    ANALYSIS / "winner_v156_state_triggered_causal_behavior_result.json"
)
V155_RESULT = (
    ANALYSIS / "winner_v155_velocity_gated_phase_residual_result.json"
)
OUTPUT = (
    ANALYSIS
    / "winner_v156_state_triggered_causal_behavior_reporting_correction.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V156_STATE_TRIGGERED_CAUSAL_BEHAVIOR_REPORTING_CORRECTION_20260725.md"
)
RIGHT_ANKLE = 13


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def line_hash(lines: list[str]) -> str:
    payload = ("\n".join(lines) + "\n").encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V156: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    raw = json.loads(RAW_RESULT.read_text(encoding="utf-8"))
    v155 = json.loads(V155_RESULT.read_text(encoding="utf-8"))
    trace_path = Path(raw["causal_contract"]["candidate_trace"]["path"])
    source_path = Path(raw["causal_contract"]["source_trace"]["path"])
    local_raw = Path(v155["artifact"]["raw"]["path"])
    lines = trace_path.read_text(encoding="utf-8").splitlines()
    first_lines = lines[:600]
    second_lines = lines[600:]
    first = [json.loads(line) for line in first_lines]
    source = [
        json.loads(line)
        for line in source_path.read_text(encoding="utf-8").splitlines()
        if line
    ]
    gate = gate_from_graph(local_raw, first)
    source_action = np.asarray(
        [row["action"] for row in source], dtype=np.float32
    )
    candidate_action = np.asarray(
        [row["action"] for row in first], dtype=np.float32
    )
    source_obs = np.asarray(
        [row["obs_state"] for row in source], dtype=np.float32
    )
    candidate_obs = np.asarray(
        [row["obs_state"] for row in first], dtype=np.float32
    )
    source_hidden = np.asarray(
        [row["policy_state_input"]["h_in"][0] for row in source],
        dtype=np.float32,
    )
    candidate_hidden = np.asarray(
        [row["policy_state_input"]["h_in"][0] for row in first],
        dtype=np.float32,
    )
    first_tick = 394
    first_delta = candidate_action[first_tick] - source_action[first_tick]
    changed = np.flatnonzero(np.abs(first_delta) > 1.0e-7).tolist()
    correction = float(gate["correction"][RIGHT_ANKLE])
    physical_checks = dict(raw["cell"]["metrics"]["checks"])
    physical_checks.pop("trace_contract", None)
    checks = {
        "raw_result_is_duplicate_trace_hold": (
            raw.get("status")
            == "HOLD_WINNER_V156_STATE_TRIGGERED_CAUSAL_BEHAVIOR"
            and raw.get("failed_checks")
            == ["causal_contract_green", "cell_all_frozen_gates_pass"]
            and raw["cell"]["failure_reasons"] == ["trace_contract"]
        ),
        "preregistration_unchanged": (
            prereg.get("status")
            == "PREREGISTERED_WINNER_V156_STATE_TRIGGERED_CAUSAL_BEHAVIOR"
            and prereg.get("causal_contract", {}).get("active_ticks")
            == [394, 583]
        ),
        "exactly_two_600_row_blocks": (
            len(lines) == 1_200
            and len(first_lines) == len(second_lines) == 600
        ),
        "two_blocks_byte_identical": first_lines == second_lines,
        "both_blocks_ticks_exact_0_to_599": (
            [json.loads(line)["tick"] for line in first_lines]
            == list(range(600))
            and [json.loads(line)["tick"] for line in second_lines]
            == list(range(600))
        ),
        "first_block_gate_exact_394_583": (
            gate["active_ticks"] == [394, 583]
        ),
        "prefix_state_and_actions_exact": (
            np.array_equal(
                source_obs[: first_tick + 1],
                candidate_obs[: first_tick + 1],
            )
            and np.array_equal(
                source_hidden[: first_tick + 1],
                candidate_hidden[: first_tick + 1],
            )
            and np.array_equal(
                source_action[:first_tick],
                candidate_action[:first_tick],
            )
        ),
        "first_intervention_exact": (
            changed == [RIGHT_ANKLE]
            and abs(float(first_delta[RIGHT_ANKLE]) - correction) <= 5.0e-7
        ),
        "all_non_trace_physical_checks_green": all(
            bool(value) for value in physical_checks.values()
        ),
        "torque_gate_green": (
            raw["cell"]["torque_gate"]["worst_peak_torque_nm"]
            <= 1.91229675
        ),
        "simulator_green": (
            raw["cell"]["simulator"]["status"] == "PASS_CANDIDATE_SIM_GATE"
        ),
        "read_only_no_rerun_training_hosted_compute_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "winner_v156.state_triggered_causal_behavior_reporting_"
            "correction.v1"
        ),
        "status": (
            "PASS_WINNER_V156_STATE_TRIGGERED_CAUSAL_BEHAVIOR_"
            "REPORTING_CORRECTION"
            if not failed
            else "HOLD_WINNER_V156_STATE_TRIGGERED_CAUSAL_BEHAVIOR_"
            "REPORTING_CORRECTION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {
            "runner": sha256(Path(__file__).resolve()),
            "preregistration": sha256(PREREG),
            "raw_result": sha256(RAW_RESULT),
            "v155_result": sha256(V155_RESULT),
            "trace_1200_rows": sha256(trace_path),
            "source_trace": sha256(source_path),
            "local_raw": sha256(local_raw),
        },
        "incident": {
            "cause": (
                "the first shell command timed out while its child process "
                "continued; the second launch appended a deterministic "
                "duplicate run to the same JSONL"
            ),
            "raw_rows": len(lines),
            "first_block_sha256": line_hash(first_lines),
            "second_block_sha256": line_hash(second_lines),
            "blocks_byte_identical": first_lines == second_lines,
            "scientific_rerun": False,
            "selection_or_threshold_change": False,
        },
        "corrected_causal_contract": {
            "rows": len(first),
            "ticks": [first[0]["tick"], first[-1]["tick"]],
            "active_ticks": gate["active_ticks"],
            "active_velocity": gate["active_velocity"],
            "first_action_delta": first_delta.tolist(),
            "state_prefix_obs_linf": float(
                np.max(
                    np.abs(
                        source_obs[: first_tick + 1]
                        - candidate_obs[: first_tick + 1]
                    )
                )
            ),
            "state_prefix_hidden_linf": float(
                np.max(
                    np.abs(
                        source_hidden[: first_tick + 1]
                        - candidate_hidden[: first_tick + 1]
                    )
                )
            ),
        },
        "cell_metrics": {
            "worst_peak_torque_nm": raw["cell"]["torque_gate"][
                "worst_peak_torque_nm"
            ],
            "worst_tracking_p95_rad": raw["cell"]["metrics"][
                "worst_tracking_p95_rad"
            ],
            "mean_local_vx_m_s": raw["cell"]["metrics"][
                "mean_local_vx_m_s"
            ],
            "samples": raw["cell"]["metrics"]["samples"],
            "termination_reason": raw["cell"]["metrics"][
                "termination_reason"
            ],
        },
        "decision": (
            "EARN_V157_DUAL_CHECKPOINT_FULL_MATRIX_PREREGISTRATION"
            if not failed
            else "CLOSE_VELOCITY_GATED_PHASE_RESIDUAL"
        ),
        "authority": {
            "full_matrix_preregistration": not failed,
            "additional_behavior": False,
            "training": False,
            "hosted_training": False,
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
        "# Winner V156 duplicate-trace reporting correction\n\n"
        f"- Status: `{payload['status']}`\n"
        "- The 1,200-row trace is two byte-identical 600-row blocks.\n"
        f"- Corrected block activations: `{gate['active_ticks']}`.\n"
        f"- Peak torque: "
        f"`{payload['cell_metrics']['worst_peak_torque_nm']}` N.m.\n"
        f"- Decision: `{payload['decision']}`\n"
        "- Read-only correction; no simulation rerun, training, Colab, "
        "deployment, or hardware.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(payload["decision"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
