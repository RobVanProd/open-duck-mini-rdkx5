#!/usr/bin/env python3
"""Select one causal reference start phase without behavior searching."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
V121_DIAGNOSIS = ANALYSIS / "winner_v121_peak_objective_diagnosis.json"
V131_RESULT = ANALYSIS / "winner_v131_two_fit_oracle_behavior_result.json"
OUTPUT = ANALYSIS / "winner_v138_phase20_start_audit_v2.json"
MARKDOWN = ANALYSIS / "WINNER_V138_PHASE20_START_AUDIT_V2_20260725.md"
EXPECTED = {
    "v121_diagnosis": (
        "1c84a48c3f4eff354108240b4084d6546d1232cccd6bf67d715d9c1518b0e26a"
    ),
    "v131_result": (
        "ab1535e11287f191e8ee6b4be5c020c44726c6263465c7cb760892387b07c9ea"
    ),
}
PITCH_CHAIN = np.asarray([2, 3, 4, 11, 12, 13], dtype=np.int64)
REFERENCE_SLICE = slice(101, 115)
PHASE_COS_INDEX = 99
PHASE_SIN_INDEX = 100
PERIOD_TICKS = 27
STARTUP_TICKS = 32
SELECTED_PHASE = 20


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def trace_rows(path: Path) -> list[dict[str, Any]]:
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]
    if len(rows) != 600:
        raise ValueError(f"incomplete V138 source trace: {path}")
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--teacher-run-root", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V138 audit: {path}")
    teacher_root = args.teacher_run_root.resolve()
    v121 = json.loads(V121_DIAGNOSIS.read_text(encoding="utf-8"))
    v131 = json.loads(V131_RESULT.read_text(encoding="utf-8"))
    input_hashes = {
        "v121_diagnosis": sha256(V121_DIAGNOSIS),
        "v131_result": sha256(V131_RESULT),
    }
    paths = sorted(teacher_root.glob("traces/*_final_*.jsonl"))
    if len(paths) != 8:
        raise ValueError("V138 requires the exact eight V131 final traces")
    manifests = []
    moving_rows = []
    projected_ticks = []
    for path in paths:
        rows = trace_rows(path)
        moving = "_x0.000_" not in path.name
        if moving:
            moving_rows.append(rows)
        projected = [
            int(row["tick"])
            for row in rows
            if (
                isinstance(row.get("exact_torque_oracle"), dict)
                and row["exact_torque_oracle"].get(
                    "projected_joint_indices"
                )
            )
        ]
        projected_ticks.extend(projected)
        manifests.append(
            {
                "name": path.name,
                "sha256": sha256(path),
                "moving": moving,
                "projected_ticks": projected,
            }
        )
    reference_tables = []
    for rows in moving_rows:
        reference_tables.append(
            np.asarray(
                [
                    row["obs_state"][REFERENCE_SLICE]
                    for row in rows[:PERIOD_TICKS]
                ],
                dtype=np.float64,
            )
        )
    common_reference = reference_tables[0]
    reference_linf_error = max(
        float(np.max(np.abs(table - common_reference)))
        for table in reference_tables[1:]
    )
    phase_rows = []
    for index, row in enumerate(moving_rows[0][:PERIOD_TICKS]):
        obs = np.asarray(row["obs_state"], dtype=np.float64)
        reference = obs[REFERENCE_SLICE]
        pitch = reference[PITCH_CHAIN]
        phase_fraction = (
            math.atan2(obs[PHASE_SIN_INDEX], obs[PHASE_COS_INDEX])
            % (2.0 * math.pi)
        ) / (2.0 * math.pi)
        phase_rows.append(
            {
                "index": index,
                "phase_fraction": phase_fraction,
                "pitch_reference_linf": float(np.max(np.abs(pitch))),
                "pitch_reference_l2": float(np.linalg.norm(pitch)),
                "reference": reference.tolist(),
            }
        )
    ranked = sorted(
        phase_rows,
        key=lambda row: (row["pitch_reference_linf"], row["index"]),
    )
    selected = phase_rows[SELECTED_PHASE]
    phase_zero = phase_rows[0]
    source_events = int(v121["summary"]["torque_exceed_events"])
    source_early = int(v121["summary"]["early_tick_0_31_events"])
    oracle_events = len(projected_ticks)
    oracle_early = sum(tick < STARTUP_TICKS for tick in projected_ticks)
    checks = {
        "all_input_hashes_exact": input_hashes == EXPECTED,
        "v121_diagnosis_green": (
            v121.get("status")
            == "PASS_WINNER_V121_PEAK_OBJECTIVE_DIAGNOSIS"
        ),
        "v131_teacher_green": (
            v131.get("status")
            == "PASS_WINNER_V131_TWO_FIT_ORACLE_BEHAVIOR_VALID_RESULT"
        ),
        "exact_eight_source_traces": len(paths) == 8,
        "exact_six_moving_traces": len(moving_rows) == 6,
        "reference_table_cross_trace_exact": reference_linf_error == 0.0,
        "period_exact_27": len(phase_rows) == PERIOD_TICKS,
        "phase20_unique_linf_minimum": (
            ranked[0]["index"] == SELECTED_PHASE
            and ranked[0]["pitch_reference_linf"]
            < ranked[1]["pitch_reference_linf"]
        ),
        "phase20_reduces_initial_linf": (
            selected["pitch_reference_linf"]
            < phase_zero["pitch_reference_linf"]
        ),
        "source_startup_events_dominate": (
            source_events == 15 and source_early == 13
        ),
        "oracle_startup_corrections_dominate": (
            oracle_events == 17 and oracle_early == 15
        ),
        "no_behavior_or_training": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v138.phase20_start_audit.v2",
        "supersedes": {
            "artifact": "winner_v138_phase20_start_audit.json",
            "reason": (
                "V1 stopped before behavior because its V121 diagnosis "
                "SHA-256 constant was transcribed incorrectly. V2 changes "
                "only that expected hash; phase metric, selected phase, "
                "thresholds, and authority are unchanged."
            ),
        },
        "status": (
            "PASS_WINNER_V138_PHASE20_START_AUDIT"
            if not failed
            else "HOLD_WINNER_V138_PHASE20_START_AUDIT"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": input_hashes,
        "trace_manifest": manifests,
        "reference_table_cross_trace_linf_error": reference_linf_error,
        "phase_table": phase_rows,
        "selection": {
            "metric": (
                "minimum L-infinity norm of the frozen six-joint pitch "
                "reference vector at reset"
            ),
            "selected_phase_index": SELECTED_PHASE,
            "selected_phase_fraction": selected["phase_fraction"],
            "selected_pitch_reference_linf": selected[
                "pitch_reference_linf"
            ],
            "phase_zero_pitch_reference_linf": phase_zero[
                "pitch_reference_linf"
            ],
            "relative_reduction": (
                1.0
                - selected["pitch_reference_linf"]
                / phase_zero["pitch_reference_linf"]
            ),
            "selection_weight_from_behavior_outcomes": 0,
            "phase_scan_authorized": False,
        },
        "causal_evidence": {
            "v121_torque_events": source_events,
            "v121_startup_torque_events": source_early,
            "v131_projected_ticks": oracle_events,
            "v131_startup_projected_ticks": oracle_early,
        },
        "decision": (
            "EARN_ONE_V138_PHASE20_DUAL_CHECKPOINT_CPU_PREREGISTRATION"
            if not failed
            else "NO_PHASE_START_SCREEN"
        ),
        "authority": {
            "phase20_preregistration": not failed,
            "other_phase_evaluation": False,
            "training": False,
            "hosted_training": False,
            "behavior_evaluation": False,
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
        "# Winner V138 phase-20 start audit V2\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Selected phase: `20/27`, from the minimum frozen pitch-reference "
        "L-infinity departure at reset.\n"
        f"- Initial pitch-reference L-infinity: "
        f"`{phase_zero['pitch_reference_linf']:.9f}` -> "
        f"`{selected['pitch_reference_linf']:.9f}`.\n"
        f"- Startup concentration: V121 `{source_early}/{source_events}`; "
        f"V131 oracle `{oracle_early}/{oracle_events}`.\n"
        "- No behavior cells, training, phase sweep, Colab, or hardware.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(payload["decision"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
