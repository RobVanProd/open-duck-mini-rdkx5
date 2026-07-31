#!/usr/bin/env python3
"""Audit the exact V126 oracle traces as a V129 teacher dataset."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
ORACLE_RESULT = (
    ANALYSIS / "winner_v126_all_tick_supreme_clip_behavior_result.json"
)
V128_ATTRIBUTION = ANALYSIS / "winner_v128_nominal_failure_attribution.json"
OUTPUT = ANALYSIS / "winner_v129_oracle_teacher_dataset_audit.json"
MARKDOWN = ANALYSIS / "WINNER_V129_ORACLE_TEACHER_DATASET_AUDIT_20260724.md"
EXPECTED = {
    "oracle_result": (
        "bd967fde399a0b429c3707589ae40c790d66d5d719f9b2035848ba2596b3436f"
    ),
    "v128_attribution": (
        "3fcf28bc2a70d35008968881afe45e6865ddb8f19e30bb13bf9737584a92e6d1"
    ),
    "source_half_policy": (
        "d4f280e8ebb4accd5c5c983bbf83042ec0162647efb446f0f6c8bffda42bc17a"
    ),
    "teacher_final_policy": (
        "bc54ea1bf39e617f76771e7416de91db2ccfe0b1bf903de08faaa64a67ce4aab"
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def summary(values: np.ndarray) -> dict[str, float]:
    absolute = np.abs(values).reshape(-1)
    return {
        "mean": float(np.mean(absolute)),
        "p95": float(np.percentile(absolute, 95)),
        "p99": float(np.percentile(absolute, 99)),
        "max": float(np.max(absolute)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--oracle-run-root", type=Path, required=True)
    parser.add_argument("--source-half-policy", type=Path, required=True)
    parser.add_argument("--teacher-final-policy", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V129: {path}")
    run_root = args.oracle_run_root.resolve()
    source_path = args.source_half_policy.resolve()
    teacher_path = args.teacher_final_policy.resolve()
    oracle = json.loads(ORACLE_RESULT.read_text(encoding="utf-8"))
    attribution = json.loads(
        V128_ATTRIBUTION.read_text(encoding="utf-8")
    )
    input_hashes = {
        "oracle_result": sha256(ORACLE_RESULT),
        "v128_attribution": sha256(V128_ATTRIBUTION),
        "source_half_policy": sha256(source_path),
        "teacher_final_policy": sha256(teacher_path),
    }
    source_session = ort.InferenceSession(
        source_path.read_bytes(), providers=["CPUExecutionProvider"]
    )
    teacher_session = ort.InferenceSession(
        teacher_path.read_bytes(), providers=["CPUExecutionProvider"]
    )
    trace_paths = sorted((run_root / "traces").glob("*_final_*.jsonl"))
    cell_paths = sorted((run_root / "cells").glob("*_final_*.json"))
    cells = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in cell_paths
    ]
    trace_manifest = []
    teacher_action_errors = []
    teacher_hidden_errors = []
    teacher_previous_errors = []
    oracle_trace_errors = []
    previous_chain_errors = []
    teacher_corrections = []
    source_action_gaps = []
    source_hidden_gaps = []
    projected_events = []
    commands: set[float] = set()
    plants: set[str] = set()
    rows = 0
    reset_previous_exact = True
    for trace_path in trace_paths:
        records = [
            json.loads(line)
            for line in trace_path.read_text(encoding="utf-8").splitlines()
            if line
        ]
        if len(records) != 600:
            raise ValueError(f"V129 incomplete teacher trace: {trace_path}")
        trace_manifest.append(
            {
                "name": trace_path.name,
                "rows": len(records),
                "sha256": sha256(trace_path),
            }
        )
        prior_action = np.zeros((1, 14), dtype=np.float32)
        for record in records:
            obs = np.asarray(record["obs_state"], dtype=np.float32)[None]
            previous = np.asarray(
                record["policy_state_input"]["previous_action"],
                dtype=np.float32,
            )
            hidden = np.asarray(
                record["policy_state_input"]["h_in"], dtype=np.float32
            )
            teacher_action, teacher_previous, teacher_hidden = (
                teacher_session.run(
                    [
                        "continuous_actions",
                        "previous_action_out",
                        "h_out",
                    ],
                    {
                        "obs": obs,
                        "previous_action": previous,
                        "h_in": hidden,
                    },
                )
            )
            source_action, _, source_hidden = source_session.run(
                [
                    "continuous_actions",
                    "previous_action_out",
                    "h_out",
                ],
                {
                    "obs": obs,
                    "previous_action": previous,
                    "h_in": hidden,
                },
            )
            base = np.asarray(
                record["policy_base_action"], dtype=np.float32
            )[None]
            state_previous_out = np.asarray(
                record["policy_state_output"]["previous_action_out"],
                dtype=np.float32,
            )
            state_hidden_out = np.asarray(
                record["policy_state_output"]["h_out"], dtype=np.float32
            )
            target = np.asarray(
                record["exact_torque_oracle"]["final_action"],
                dtype=np.float32,
            )[None]
            trace_action = np.asarray(record["action"], dtype=np.float32)[
                None
            ]
            teacher_action_errors.append(teacher_action - base)
            teacher_previous_errors.append(
                teacher_previous - state_previous_out
            )
            teacher_hidden_errors.append(
                teacher_hidden - state_hidden_out
            )
            oracle_trace_errors.append(target - trace_action)
            previous_chain_errors.append(previous - prior_action)
            teacher_corrections.append(target - teacher_action)
            source_action_gaps.append(target - source_action)
            source_hidden_gaps.append(teacher_hidden - source_hidden)
            oracle_row = record["exact_torque_oracle"]
            if oracle_row["projected_joint_indices"]:
                projected_events.append(
                    {
                        "trace": trace_path.name,
                        "tick": record["tick"],
                        "joint_indices": oracle_row[
                            "projected_joint_indices"
                        ],
                        "clip_linf": oracle_row[
                            "torque_projection_clip_linf"
                        ],
                    }
                )
            reset_previous_exact &= (
                record["tick"] != 0
                or bool(np.array_equal(previous, np.zeros_like(previous)))
            )
            prior_action = trace_action
            commands.add(float(record["command"][0]))
            rows += 1
        plants.add(
            "P31_34_PITCH_WITH_P30_NONPITCH"
            if "p31_34" in trace_path.name
            else "P30_ALL_JOINT"
        )
    teacher_action_error = np.concatenate(teacher_action_errors)
    teacher_hidden_error = np.concatenate(teacher_hidden_errors)
    teacher_previous_error = np.concatenate(teacher_previous_errors)
    oracle_trace_error = np.concatenate(oracle_trace_errors)
    previous_chain_error = np.concatenate(previous_chain_errors)
    teacher_correction = np.concatenate(teacher_corrections)
    source_action_gap = np.concatenate(source_action_gaps)
    source_hidden_gap = np.concatenate(source_hidden_gaps)
    nonzero_teacher_elements = int(
        np.sum(np.abs(teacher_correction) > 1.0e-7)
    )
    checks = {
        "all_input_hashes_exact": input_hashes == EXPECTED,
        "oracle_screen_green": (
            oracle.get("status")
            == "PASS_WINNER_V126_ALL_TICK_SUPREME_CLIP_BEHAVIOR_VALID_RESULT"
            and oracle.get("summary", {}).get("passing_cells") == 16
            and oracle.get("summary", {}).get(
                "empty_intersection_events"
            )
            == 0
        ),
        "v128_closes_ppo_and_authorizes_distillation_prereg": (
            attribution.get("status")
            == "PASS_WINNER_V128_NOMINAL_FAILURE_ATTRIBUTION"
            and attribution.get("authority", {}).get(
                "teacher_distillation_preregistration_authorized"
            )
            is True
            and attribution.get("authority", {}).get(
                "additional_ppo_lagrangian"
            )
            is False
        ),
        "eight_final_teacher_cells_pass": (
            len(cells) == 8 and all(cell["pass"] for cell in cells)
        ),
        "dataset_shape_exact": (
            len(trace_paths) == 8
            and rows == 4_800
            and commands == {0.0, 0.074, 0.077, 0.08}
            and plants
            == {
                "P30_ALL_JOINT",
                "P31_34_PITCH_WITH_P30_NONPITCH",
            }
        ),
        "teacher_graph_replays_trace_action": (
            float(np.max(np.abs(teacher_action_error))) <= 1.0e-6
        ),
        "teacher_graph_replays_trace_previous_output": (
            float(np.max(np.abs(teacher_previous_error))) <= 1.0e-6
        ),
        "teacher_graph_replays_trace_hidden_output": (
            float(np.max(np.abs(teacher_hidden_error))) <= 1.0e-6
        ),
        "oracle_target_equals_executed_action": (
            float(np.max(np.abs(oracle_trace_error))) <= 1.0e-6
        ),
        "previous_action_chain_exact": (
            reset_previous_exact
            and float(np.max(np.abs(previous_chain_error))) <= 1.0e-6
        ),
        "teacher_correction_nonzero_but_bounded": (
            len(projected_events) == 14
            and nonzero_teacher_elements >= 14
            and float(np.max(np.abs(teacher_correction))) < 0.05
        ),
        "all_values_finite": all(
            np.isfinite(value).all()
            for value in (
                teacher_action_error,
                teacher_hidden_error,
                teacher_previous_error,
                oracle_trace_error,
                previous_chain_error,
                teacher_correction,
                source_action_gap,
                source_hidden_gap,
            )
        ),
        "cpu_only": source_session.get_providers()
        == teacher_session.get_providers()
        == ["CPUExecutionProvider"],
        "no_training_or_behavior_run": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v129.oracle_teacher_dataset_audit.v1",
        "status": (
            "PASS_WINNER_V129_ORACLE_TEACHER_DATASET_AUDIT"
            if not failed
            else "HOLD_WINNER_V129_ORACLE_TEACHER_DATASET_AUDIT"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": input_hashes,
        "trace_manifest": trace_manifest,
        "dataset": {
            "traces": len(trace_paths),
            "rows": rows,
            "commands": sorted(commands),
            "plants": sorted(plants),
            "source": "V121_TRAIN_MATCHED_FINAL plus exact oracle",
            "student_restore": "V121_TRAIN_MATCHED_HALF",
            "inputs": ["obs[115]", "previous_action[14]", "h_in[64]"],
            "targets": [
                "oracle final action[14]",
                "teacher h_out[64]",
            ],
        },
        "replay_error": {
            "teacher_action": summary(teacher_action_error),
            "teacher_previous_action_out": summary(
                teacher_previous_error
            ),
            "teacher_h_out": summary(teacher_hidden_error),
            "oracle_target_vs_trace_action": summary(oracle_trace_error),
            "previous_action_chain": summary(previous_chain_error),
        },
        "teacher_correction": {
            **summary(teacher_correction),
            "projected_events": projected_events,
            "nonzero_elements_at_1e_minus_7": nonzero_teacher_elements,
        },
        "source_to_teacher_gap": {
            "action": summary(source_action_gap),
            "hidden": summary(source_hidden_gap),
        },
        "decision": (
            "AUTHORIZE_ONE_V129_CPU_DISTILLATION_CONTRACT"
            if not failed
            else "NO_DISTILLATION"
        ),
        "authority": {
            "cpu_distillation_contract_authorized": not failed,
            "formal_distillation_training": False,
            "hosted_training": False,
            "behavior_evaluation": False,
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
        "# Winner V129 oracle-teacher dataset audit\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Rows: `{rows}` across 8 green teacher cells.\n"
        f"- Projected events: `{len(projected_events)}`.\n"
        f"- Max teacher correction: "
        f"`{payload['teacher_correction']['max']}` normalized action.\n"
        f"- Source-to-teacher action p95/max: "
        f"`{payload['source_to_teacher_gap']['action']['p95']}` / "
        f"`{payload['source_to_teacher_gap']['action']['max']}`.\n"
        "- Authority: one CPU contract only; no training or behavior yet.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
