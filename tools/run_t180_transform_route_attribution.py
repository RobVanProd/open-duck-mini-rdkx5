#!/usr/bin/env python3
"""Replay paired source/T175 graphs on frozen decisive trace states."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping, Sequence

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREGISTRATION = (
    ANALYSIS / "t180_transform_route_attribution_preregistration.json"
)
RESULT = ANALYSIS / "t180_transform_route_attribution_result.json"
MARKDOWN = ANALYSIS / "T180_TRANSFORM_ROUTE_ATTRIBUTION_RESULT_20260730.md"

sys.path.insert(0, str(ROOT / "tools"))
from actuator_bridge_model import JOINT_NAMES  # noqa: E402
from run_t27_t23_robustness_matrix import (  # noqa: E402
    canonical_sha256,
    verify_receipt,
)


class T180Error(RuntimeError):
    """The frozen T180 replay attribution contract was violated."""


def _require(condition: object, message: str) -> None:
    if not condition:
        raise T180Error(message)


def _load_json(path: Path) -> dict[str, Any]:
    _require(path.is_file(), f"missing JSON artifact: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def _canonical_without(value: Mapping[str, Any], field: str) -> str:
    basis = dict(value)
    basis.pop(field, None)
    return canonical_sha256(basis)


def array_sha256(value: np.ndarray) -> str:
    return hashlib.sha256(
        np.ascontiguousarray(value, dtype=np.float32).tobytes()
    ).hexdigest()


def _read_prefix(
    trace: Mapping[str, Any],
    *,
    prefix_ticks: int,
    expected_command: float,
    expected_context_sha256: str,
) -> list[dict[str, Any]]:
    verify_receipt(trace, f"trace:{trace['path']}")
    rows = []
    with Path(trace["path"]).open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if len(rows) >= prefix_ticks:
                break
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise T180Error(
                    f"invalid trace JSON: {trace['path']}:{line_number}"
                ) from exc
            _require(
                int(row.get("tick", -1)) == line_number - 1,
                f"noncontiguous trace: {trace['path']}:{line_number}",
            )
            _require(
                row.get("policy_calibration_context_sha256")
                == expected_context_sha256,
                f"context SHA differs: {trace['path']}:{line_number}",
            )
            command = [float(item) for item in row.get("command", [])]
            _require(
                command
                == [expected_command, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                f"command differs: {trace['path']}:{line_number}",
            )
            _require(
                isinstance(row.get("obs_state"), list)
                and len(row["obs_state"]) == 115,
                f"115-D observation missing: {trace['path']}:{line_number}",
            )
            _require(
                isinstance(row.get("policy_state_input"), dict),
                f"policy state missing: {trace['path']}:{line_number}",
            )
            _require(
                isinstance(row.get("action"), list)
                and len(row["action"]) == 14,
                f"action missing: {trace['path']}:{line_number}",
            )
            rows.append(row)
    _require(
        len(rows) == prefix_ticks,
        f"trace is shorter than frozen prefix: {trace['path']}",
    )
    return rows


def _feed(
    row: Mapping[str, Any], context: np.ndarray
) -> dict[str, np.ndarray]:
    feed = {
        "obs": np.asarray(row["obs_state"], dtype=np.float32)[None, :],
        "calibration_context": context[None, :],
    }
    for name in ("previous_action", "h_in"):
        value = row["policy_state_input"].get(name)
        _require(value is not None, f"missing policy state input: {name}")
        feed[name] = np.asarray(value, dtype=np.float32)
    return feed


def replay_bank(
    rows: Sequence[Mapping[str, Any]],
    *,
    context: np.ndarray,
    source_session: Any,
    transformed_session: Any,
    own_graph: str,
    gait_period_ticks: int,
) -> dict[str, Any]:
    source_actions = []
    transformed_actions = []
    recorded_actions = []
    for row in rows:
        feed = _feed(row, context)
        source_actions.append(
            np.asarray(
                source_session.run(["continuous_actions"], feed)[0][0],
                dtype=np.float32,
            )
        )
        transformed_actions.append(
            np.asarray(
                transformed_session.run(["continuous_actions"], feed)[0][0],
                dtype=np.float32,
            )
        )
        recorded_actions.append(np.asarray(row["action"], dtype=np.float32))
    source = np.asarray(source_actions, dtype=np.float32)
    transformed = np.asarray(transformed_actions, dtype=np.float32)
    recorded = np.asarray(recorded_actions, dtype=np.float32)
    own = source if own_graph == "source" else transformed
    replay_error = np.abs(own - recorded)
    delta = transformed.astype(np.float64) - source.astype(np.float64)
    per_joint_rms = np.sqrt(np.mean(np.square(delta), axis=0))
    per_joint_mean = np.mean(delta, axis=0)
    total_energy = float(np.sum(np.square(delta)))
    joint_energy = np.sum(np.square(delta), axis=0)
    dominant = int(np.argmax(joint_energy))
    first_nonzero = None
    for tick, row in enumerate(delta):
        if float(np.max(np.abs(row))) > 1.0e-7:
            first_nonzero = tick
            break
    phase_mean = [
        np.mean(
            delta[np.arange(len(delta)) % gait_period_ticks == phase],
            axis=0,
        ).tolist()
        for phase in range(gait_period_ticks)
    ]
    return {
        "own_graph": own_graph,
        "ticks": len(rows),
        "own_replay_max_abs_error": float(np.max(replay_error)),
        "first_action_delta_tick_gt_1e_7": first_nonzero,
        "action_delta_l_inf": float(np.max(np.abs(delta))),
        "action_delta_rms": float(np.sqrt(np.mean(np.square(delta)))),
        "signed_mean_delta": per_joint_mean.tolist(),
        "per_joint_rms_delta": {
            joint: float(per_joint_rms[index])
            for index, joint in enumerate(JOINT_NAMES)
        },
        "dominant_joint": JOINT_NAMES[dominant],
        "dominant_joint_energy_fraction": (
            0.0 if total_energy == 0.0 else float(joint_energy[dominant] / total_energy)
        ),
        "phase_mean_delta": phase_mean,
    }


def aggregate_banks(
    banks: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    signed = np.asarray(
        [bank["signed_mean_delta"] for bank in banks], dtype=np.float64
    )
    rms = np.asarray(
        [
            [bank["per_joint_rms_delta"][joint] for joint in JOINT_NAMES]
            for bank in banks
        ],
        dtype=np.float64,
    )
    mean_signed = np.mean(signed, axis=0)
    mean_rms = np.mean(rms, axis=0)
    dominant = int(np.argmax(mean_rms))
    return {
        "banks": len(banks),
        "signed_mean_delta": mean_signed.tolist(),
        "per_joint_mean_rms_delta": {
            joint: float(mean_rms[index])
            for index, joint in enumerate(JOINT_NAMES)
        },
        "dominant_joint": JOINT_NAMES[dominant],
        "dominant_joint_rms": float(mean_rms[dominant]),
    }


def cosine(left: Sequence[float], right: Sequence[float]) -> float:
    a = np.asarray(left, dtype=np.float64)
    b = np.asarray(right, dtype=np.float64)
    denominator = float(np.linalg.norm(a) * np.linalg.norm(b))
    return 0.0 if denominator == 0.0 else float(np.dot(a, b) / denominator)


def classify_route(
    *,
    replay_max_error: float,
    helpful: Mapping[str, Any],
    harmful: Mapping[str, Any],
    signed_cosine: float,
    cosine_threshold: float,
) -> tuple[str, str]:
    if replay_max_error > 1.0e-6:
        return "INVALID_ONNX_TRACE_REPLAY", "NO_SUCCESSOR_AUTHORIZED"
    if (
        helpful["dominant_joint"] == harmful["dominant_joint"]
        and abs(signed_cosine) >= cosine_threshold
    ):
        return (
            "SHARED_HEAD_DIRECTION_CONTEXT_AMPLITUDE_TRADEOFF",
            "EARN_T181_ONE_DIMENSIONAL_HEAD_INTERPOLATION_"
            "FEASIBILITY_PREREGISTRATION_ONLY",
        )
    return (
        "DISTRIBUTED_CONTEXT_DEPENDENT_HEAD_TRADEOFF",
        "EARN_T181_CONTEXT_GATED_HEAD_FEASIBILITY_PREREGISTRATION_ONLY",
    )


def _markdown(value: Mapping[str, Any]) -> str:
    return (
        "# T180 T175 transform-route attribution\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Classification: `{value['classification']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Maximum own-graph replay error: "
        f"`{value['summary']['maximum_own_replay_error']:.9g}`\n"
        f"- Helpful dominant joint: "
        f"`{value['family_aggregates']['negative_y_rescue']['dominant_joint']}`\n"
        f"- Harmful dominant joint: "
        f"`{value['family_aggregates']['positive_z_regression']['dominant_joint']}`\n"
        f"- Signed family cosine: "
        f"`{value['summary']['helpful_harmful_signed_cosine']:.6f}`\n"
        "- New simulation / optimizer / hosted compute / robot: `0/0/0/0`\n\n"
        "This result attributes the already measured transform tradeoff only. "
        "It does not authorize a graph change, behavior test, training, "
        "deployment audit, Gate 5, or hardware.\n"
    )


def run(
    preregistration_path: Path = PREREGISTRATION,
    result_path: Path = RESULT,
    markdown_path: Path = MARKDOWN,
) -> dict[str, Any]:
    _require(not result_path.exists(), f"refusing to overwrite: {result_path}")
    _require(not markdown_path.exists(), f"refusing to overwrite: {markdown_path}")
    _require(
        not subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=ROOT, text=True
        ).strip(),
        "T180 execution requires committed clean preregistration",
    )
    prereg = _load_json(preregistration_path)
    _require(
        prereg.get("status")
        == "PREREGISTERED_T180_TRANSFORM_ROUTE_ATTRIBUTION",
        "unexpected T180 preregistration status",
    )
    _require(
        _canonical_without(prereg, "preregistered_contract_sha256")
        == prereg.get("preregistered_contract_sha256"),
        "T180 preregistration hash differs",
    )
    for label, item in prereg["frozen_inputs"].items():
        verify_receipt(item, label)
    import onnxruntime as ort

    sessions: dict[str, Any] = {}
    case_results = []
    all_banks: dict[str, list[dict[str, Any]]] = {
        "negative_y_rescue": [],
        "positive_z_regression": [],
        "positive_z_shared_failure": [],
    }
    prefix_ticks = int(prereg["analysis_contract"]["prefix_ticks"])
    gait_period = int(prereg["analysis_contract"]["gait_period_ticks"])
    for case in prereg["cases"]:
        for role in ("source_graph", "transformed_graph"):
            graph = case[role]
            verify_receipt(graph, f"{case['case_id']}:{role}")
            if graph["sha256"] not in sessions:
                sessions[graph["sha256"]] = ort.InferenceSession(
                    graph["path"], providers=["CPUExecutionProvider"]
                )
        context = np.asarray(case["context"], dtype=np.float32)
        _require(context.shape == (64,), f"context shape differs: {case['case_id']}")
        _require(
            array_sha256(context) == case["context_sha256"],
            f"context hash differs: {case['case_id']}",
        )
        banks = []
        for bank_role in ("source_trace", "transformed_trace"):
            trace = case[bank_role]
            rows = _read_prefix(
                trace,
                prefix_ticks=prefix_ticks,
                expected_command=float(case["command_x_m_s"]),
                expected_context_sha256=case["context_sha256"],
            )
            bank = replay_bank(
                rows,
                context=context,
                source_session=sessions[case["source_graph"]["sha256"]],
                transformed_session=sessions[
                    case["transformed_graph"]["sha256"]
                ],
                own_graph=(
                    "source" if bank_role == "source_trace" else "transformed"
                ),
                gait_period_ticks=gait_period,
            )
            bank["bank_role"] = bank_role
            banks.append(bank)
            all_banks[case["family"]].append(bank)
        case_results.append(
            {
                key: case[key]
                for key in (
                    "case_id",
                    "family",
                    "checkpoint_pair",
                    "fit_id",
                    "command_x_m_s",
                    "source_cell_green",
                    "transformed_cell_green",
                )
            }
            | {"banks": banks}
        )
    aggregates = {
        name: aggregate_banks(banks) for name, banks in all_banks.items()
    }
    replay_max = max(
        bank["own_replay_max_abs_error"]
        for banks in all_banks.values()
        for bank in banks
    )
    family_cosine = cosine(
        aggregates["negative_y_rescue"]["signed_mean_delta"],
        aggregates["positive_z_regression"]["signed_mean_delta"],
    )
    classification, decision = classify_route(
        replay_max_error=replay_max,
        helpful=aggregates["negative_y_rescue"],
        harmful=aggregates["positive_z_regression"],
        signed_cosine=family_cosine,
        cosine_threshold=float(
            prereg["analysis_contract"]["shared_direction_cosine_threshold"]
        ),
    )
    basis: dict[str, Any] = {
        "schema_version": "open_duck.t180_transform_route_attribution_result.v1",
        "status": "COMPLETE_T180_TRANSFORM_ROUTE_ATTRIBUTION",
        "classification": classification,
        "decision": decision,
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "summary": {
            "cases": len(case_results),
            "banks": sum(len(item["banks"]) for item in case_results),
            "ticks_per_bank": prefix_ticks,
            "maximum_own_replay_error": replay_max,
            "helpful_harmful_signed_cosine": family_cosine,
        },
        "family_aggregates": aggregates,
        "cases": case_results,
        "execution": {
            "saved_trace_banks": 12,
            "saved_trace_rows": 12 * prefix_ticks,
            "onnx_graphs": len(sessions),
            "new_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": prereg["authority_after_result"],
    }
    basis["result_sha256"] = canonical_sha256(basis)
    result_path.write_text(
        json.dumps(basis, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    markdown_path.write_text(
        _markdown(basis), encoding="utf-8", newline="\n"
    )
    return basis


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preregistration", type=Path, default=PREREGISTRATION)
    parser.add_argument("--result", type=Path, default=RESULT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    result = run(args.preregistration, args.result, args.markdown)
    print(result["status"])
    print(f"classification={result['classification']}")
    print(f"decision={result['decision']}")
    print(f"result_sha256={result['result_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
