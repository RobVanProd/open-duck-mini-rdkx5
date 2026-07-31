#!/usr/bin/env python3
"""Attribute the V141 miss to an unlabeled transferred joint load."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
V121_RESULT = ANALYSIS / "winner_v121_nominal_behavior_result.json"
V140_RESULT = ANALYSIS / "winner_v140_preservation_projected_actor_result.json"
V141_RESULT = ANALYSIS / "winner_v141_projected_final_behavior_result.json"
OUTPUT = ANALYSIS / "winner_v142_transferred_load_attribution.json"
MARKDOWN = ANALYSIS / "WINNER_V142_TRANSFERRED_LOAD_ATTRIBUTION_20260725.md"
TORQUE_LIMIT = 1.91229675
LEFT_KNEE = 3
RIGHT_ANKLE = 13


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_trace(path: Path) -> list[dict]:
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]
    if len(rows) != 600:
        raise ValueError(f"incomplete V142 trace: {path}")
    return rows


def peak(rows: list[dict]) -> tuple[int, int, float]:
    force = np.abs(
        np.asarray([row["actuator_force_nm"] for row in rows], dtype=np.float64)
    )
    tick, joint = np.unravel_index(np.argmax(force), force.shape)
    return int(tick), int(joint), float(force[tick, joint])


def joint_peak(rows: list[dict], joint: int) -> float:
    return float(
        np.max(
            np.abs(
                np.asarray(
                    [row["actuator_force_nm"][joint] for row in rows],
                    dtype=np.float64,
                )
            )
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--teacher-run-root", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V142: {path}")
    v121 = json.loads(V121_RESULT.read_text(encoding="utf-8"))
    v140 = json.loads(V140_RESULT.read_text(encoding="utf-8"))
    v141 = json.loads(V141_RESULT.read_text(encoding="utf-8"))
    source_trace = (
        Path(v121["run_root"])
        / "traces"
        / "v121_train_matched_final_p30_all_joint_x0.074_seed167931544.jsonl"
    )
    new_cell = v141["new_final_cells"][1]
    new_trace = Path(new_cell["trace"]["path"])
    teacher_trace = (
        args.teacher_run_root.resolve()
        / "traces"
        / "v121_train_matched_final_p30_all_joint_x0.074_seed167931544.jsonl"
    )
    source_rows = load_trace(source_trace)
    new_rows = load_trace(new_trace)
    teacher_rows = load_trace(teacher_trace)
    source_peak = peak(source_rows)
    new_peak = peak(new_rows)
    new_tick = new_peak[0]
    oracle = teacher_rows[new_tick]["exact_torque_oracle"]
    base_action = np.asarray(
        teacher_rows[new_tick]["policy_base_action"], dtype=np.float64
    )
    teacher_action = np.asarray(oracle["final_action"], dtype=np.float64)
    teacher_state = teacher_rows[new_tick]["policy_state_input"]
    candidate_session = ort.InferenceSession(
        v140["artifacts"]["selected_dynamic"]["path"],
        providers=["CPUExecutionProvider"],
    )
    candidate_on_teacher = candidate_session.run(
        None,
        {
            "obs": np.asarray(
                teacher_rows[new_tick]["obs_state"], dtype=np.float32
            )[None, :],
            "previous_action": np.asarray(
                teacher_state["previous_action"], dtype=np.float32
            ),
            "h_in": np.asarray(teacher_state["h_in"], dtype=np.float32),
        },
    )[0][0]
    source_action = float(source_rows[new_tick]["action"][RIGHT_ANKLE])
    new_action = float(new_rows[new_tick]["action"][RIGHT_ANKLE])
    source_left_knee = joint_peak(source_rows, LEFT_KNEE)
    new_left_knee = joint_peak(new_rows, LEFT_KNEE)
    source_right_ankle = joint_peak(source_rows, RIGHT_ANKLE)
    new_right_ankle = joint_peak(new_rows, RIGHT_ANKLE)
    checks = {
        "v140_cpu_projection_green": (
            v140.get("status")
            == "PASS_WINNER_V140_PRESERVATION_PROJECTED_ACTOR"
        ),
        "v141_only_failure_torque": (
            new_cell["failure_reasons"]
            == ["torque_peak_at_most_1p91229675_nm"]
        ),
        "source_peak_left_knee": source_peak[:2] == (28, LEFT_KNEE),
        "new_peak_right_ankle": new_peak[:2] == (397, RIGHT_ANKLE),
        "left_knee_repaired_below_limit": (
            source_left_knee > TORQUE_LIMIT
            and new_left_knee < TORQUE_LIMIT
        ),
        "right_ankle_transferred_above_limit": (
            source_right_ankle < TORQUE_LIMIT
            and new_right_ankle > TORQUE_LIMIT
        ),
        "peak_tick_has_no_torque_teacher_label": (
            oracle["projected_joint_indices"] == []
        ),
        "peak_joint_has_exact_zero_teacher_delta": (
            teacher_action[RIGHT_ANKLE] == base_action[RIGHT_ANKLE]
        ),
        "candidate_preserves_teacher_state_peak_joint": (
            candidate_on_teacher[RIGHT_ANKLE] == base_action[RIGHT_ANKLE]
        ),
        "closed_loop_action_shift_at_peak_tick": new_action != source_action,
        "no_new_behavior_or_training": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v142.transferred_load_attribution.v1",
        "status": (
            "PASS_WINNER_V142_TRANSFERRED_LOAD_ATTRIBUTION"
            if not failed
            else "HOLD_WINNER_V142_TRANSFERRED_LOAD_ATTRIBUTION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {
            "v121_result": sha256(V121_RESULT),
            "v140_result": sha256(V140_RESULT),
            "v141_result": sha256(V141_RESULT),
            "source_trace": sha256(source_trace),
            "new_trace": sha256(new_trace),
            "teacher_trace": sha256(teacher_trace),
        },
        "source": {
            "peak": {
                "tick": source_peak[0],
                "joint": source_peak[1],
                "torque_nm": source_peak[2],
            },
            "left_knee_peak_nm": source_left_knee,
            "right_ankle_peak_nm": source_right_ankle,
        },
        "projected": {
            "peak": {
                "tick": new_peak[0],
                "joint": new_peak[1],
                "torque_nm": new_peak[2],
            },
            "left_knee_peak_nm": new_left_knee,
            "right_ankle_peak_nm": new_right_ankle,
            "right_ankle_action_at_peak": new_action,
        },
        "teacher_at_new_peak": {
            "tick": new_tick,
            "projected_joint_indices": oracle["projected_joint_indices"],
            "right_ankle_action_delta": float(
                teacher_action[RIGHT_ANKLE] - base_action[RIGHT_ANKLE]
            ),
            "candidate_on_teacher_right_ankle_action": float(
                candidate_on_teacher[RIGHT_ANKLE]
            ),
            "candidate_on_teacher_minus_base": float(
                candidate_on_teacher[RIGHT_ANKLE] - base_action[RIGHT_ANKLE]
            ),
            "source_right_ankle_action": source_action,
            "projected_right_ankle_action": new_action,
            "projected_minus_source_action": new_action - source_action,
        },
        "diagnosis": (
            "the aggregate-preservation projection repaired the labeled "
            "left-knee startup peak but changed the closed-loop trajectory "
            "enough to move the mature right ankle above the torque box; "
            "the candidate still exactly preserves the right-ankle output "
            "on the corresponding unwrapped teacher state, so this is a "
            "trajectory-transfer effect rather than a direct label there"
        ),
        "decision": (
            "PREREGISTER_TORQUE_ONLY_PRESERVATION_CONSTRAINED_ACTOR_CPU"
            if not failed
            else "NO_TORQUE_ONLY_ACTOR_ROUTE"
        ),
        "authority": {
            "cpu_contract_preregistration": not failed,
            "training": False,
            "behavior": False,
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
        "# Winner V142 transferred-load attribution\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Left knee: `{source_left_knee:.6f}` -> "
        f"`{new_left_knee:.6f}` N.m.\n"
        f"- Right ankle: `{source_right_ankle:.6f}` -> "
        f"`{new_right_ankle:.6f}` N.m.\n"
        "- The corresponding teacher row/joint had exactly zero torque "
        "correction, and the candidate preserves that output exactly on "
        "the teacher state; the miss is a closed-loop trajectory transfer.\n"
        f"- Decision: `{payload['decision']}`\n"
        "- Read-only attribution; no training, behavior, Colab, or hardware.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(payload["decision"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
