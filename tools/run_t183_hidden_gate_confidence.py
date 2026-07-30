#!/usr/bin/env python3
"""Audit whether T170's existing hidden-gate confidence separates T175 roles."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Mapping, Sequence

import numpy as np
import onnx
from onnx import numpy_helper


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t183_hidden_gate_confidence_preregistration.json"
RESULT = ANALYSIS / "t183_hidden_gate_confidence_result.json"
MARKDOWN = ANALYSIS / "T183_HIDDEN_GATE_CONFIDENCE_RESULT_20260730.md"

sys.path.insert(0, str(ROOT / "tools"))
from run_t27_t23_robustness_matrix import (  # noqa: E402
    canonical_sha256,
    verify_receipt,
)


class T183Error(RuntimeError):
    """The frozen T183 contract was violated."""


def _require(condition: object, message: str) -> None:
    if not condition:
        raise T183Error(message)


def _load(path: Path) -> dict[str, Any]:
    _require(path.is_file(), f"missing input: {path}")
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


def initializer_arrays(path: Path) -> dict[str, np.ndarray]:
    model = onnx.load(path)
    return {
        item.name: numpy_helper.to_array(item).copy()
        for item in model.graph.initializer
    }


def hidden_gate_score(
    h_out: np.ndarray, initializers: Mapping[str, np.ndarray]
) -> np.ndarray:
    hidden = np.asarray(h_out, dtype=np.float32)
    mean = np.asarray(initializers["hidden_gate_mean"], dtype=np.float32)
    scale = np.asarray(initializers["hidden_gate_scale"], dtype=np.float32)
    coefficient = np.asarray(
        initializers["hidden_gate_coefficient"], dtype=np.float32
    )
    intercept = np.asarray(
        initializers["hidden_gate_intercept"], dtype=np.float32
    )
    standardized = np.divide(
        np.subtract(hidden, mean, dtype=np.float32),
        scale,
        dtype=np.float32,
    )
    linear = np.matmul(standardized, coefficient, dtype=np.float32)
    return np.add(linear, intercept, dtype=np.float32).reshape(-1)


def confidence_threshold(
    rescue_scores: Sequence[float], regression_scores: Sequence[float]
) -> tuple[float, float]:
    _require(bool(rescue_scores), "no effective rescue rows")
    _require(bool(regression_scores), "no effective regression rows")
    minimum_rescue = min(float(value) for value in rescue_scores)
    maximum_regression = max(float(value) for value in regression_scores)
    margin = minimum_rescue - maximum_regression
    threshold = 0.5 * (minimum_rescue + maximum_regression)
    return threshold, margin


def _read_rows(
    trace: Mapping[str, Any],
    *,
    ticks: int,
    expected_command: float,
    expected_context_sha256: str,
) -> list[dict[str, Any]]:
    verify_receipt(trace, f"trace:{trace['path']}")
    rows = []
    with Path(trace["path"]).open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if len(rows) >= ticks:
                break
            row = json.loads(line)
            _require(
                int(row.get("tick", -1)) == line_number - 1,
                f"noncontiguous trace: {trace['path']}:{line_number}",
            )
            _require(
                row.get("policy_calibration_context_sha256")
                == expected_context_sha256,
                f"context differs: {trace['path']}:{line_number}",
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
                f"observation missing: {trace['path']}:{line_number}",
            )
            state_input = row.get("policy_state_input")
            state_output = row.get("policy_state_output")
            _require(
                isinstance(state_input, dict)
                and isinstance(state_output, dict),
                f"policy state missing: {trace['path']}:{line_number}",
            )
            _require(
                np.asarray(state_output.get("h_out")).shape == (1, 64),
                f"h_out shape differs: {trace['path']}:{line_number}",
            )
            rows.append(row)
    _require(
        len(rows) == ticks,
        f"trace shorter than frozen window: {trace['path']}",
    )
    return rows


def _feed(
    row: Mapping[str, Any], context: np.ndarray
) -> dict[str, np.ndarray]:
    return {
        "obs": np.asarray(row["obs_state"], dtype=np.float32)[None, :],
        "calibration_context": context[None, :],
        "previous_action": np.asarray(
            row["policy_state_input"]["previous_action"], dtype=np.float32
        ),
        "h_in": np.asarray(
            row["policy_state_input"]["h_in"], dtype=np.float32
        ),
    }


def replay_bank(
    rows: Sequence[Mapping[str, Any]],
    *,
    context: np.ndarray,
    source_session: Any,
    transformed_session: Any,
    gate_initializers: Mapping[str, np.ndarray],
    own_graph: str | None,
    delta_threshold: float,
) -> dict[str, Any]:
    scores = []
    effective_scores = []
    own_errors = []
    delta_maxima = []
    for row in rows:
        feed = _feed(row, context)
        source_output = source_session.run(
            ["continuous_actions", "h_out"], feed
        )
        transformed_output = transformed_session.run(
            ["continuous_actions", "h_out"], feed
        )
        source_action = np.asarray(source_output[0][0], dtype=np.float32)
        transformed_action = np.asarray(
            transformed_output[0][0], dtype=np.float32
        )
        source_hidden = np.asarray(source_output[1], dtype=np.float32)
        transformed_hidden = np.asarray(
            transformed_output[1], dtype=np.float32
        )
        recorded_hidden = np.asarray(
            row["policy_state_output"]["h_out"], dtype=np.float32
        )
        _require(
            np.array_equal(source_hidden, transformed_hidden),
            "head-only graph pair changed h_out",
        )
        _require(
            np.array_equal(source_hidden, recorded_hidden),
            "recorded h_out differs from exact replay",
        )
        score = float(
            hidden_gate_score(source_hidden, gate_initializers)[0]
        )
        scores.append(score)
        delta = float(np.max(np.abs(transformed_action - source_action)))
        delta_maxima.append(delta)
        if delta > delta_threshold:
            effective_scores.append(score)
        if own_graph is not None:
            recorded_action = np.asarray(row["action"], dtype=np.float32)
            own_action = (
                source_action if own_graph == "source" else transformed_action
            )
            own_errors.append(
                float(np.max(np.abs(own_action - recorded_action)))
            )
    return {
        "rows": len(rows),
        "effective_rows": len(effective_scores),
        "score_min": min(scores),
        "score_mean": float(np.mean(scores, dtype=np.float64)),
        "score_max": max(scores),
        "effective_score_min": (
            None if not effective_scores else min(effective_scores)
        ),
        "effective_score_mean": (
            None
            if not effective_scores
            else float(np.mean(effective_scores, dtype=np.float64))
        ),
        "effective_score_max": (
            None if not effective_scores else max(effective_scores)
        ),
        "maximum_action_delta": max(delta_maxima),
        "maximum_own_replay_error": (
            None if not own_errors else max(own_errors)
        ),
        "effective_scores": effective_scores,
    }


def _graph_pair(
    case: Mapping[str, Any],
    sessions: dict[str, Any],
    gate_names: Sequence[str],
) -> tuple[Any, Any, dict[str, np.ndarray]]:
    import onnxruntime as ort

    graphs = (case["source_graph"], case["transformed_graph"])
    arrays = []
    for graph in graphs:
        verify_receipt(graph, f"graph:{graph['path']}")
        if graph["sha256"] not in sessions:
            sessions[graph["sha256"]] = ort.InferenceSession(
                graph["path"], providers=["CPUExecutionProvider"]
            )
        arrays.append(initializer_arrays(Path(graph["path"])))
    for name in gate_names:
        _require(name in arrays[0] and name in arrays[1], f"missing {name}")
        _require(
            np.array_equal(arrays[0][name], arrays[1][name]),
            f"gate initializer differs across pair: {name}",
        )
        _require(
            np.all(np.isfinite(arrays[0][name])),
            f"gate initializer is nonfinite: {name}",
        )
    return (
        sessions[graphs[0]["sha256"]],
        sessions[graphs[1]["sha256"]],
        arrays[0],
    )


def _strip_scores(value: dict[str, Any]) -> dict[str, Any]:
    result = dict(value)
    result.pop("effective_scores", None)
    return result


def run() -> dict[str, Any]:
    _require(not RESULT.exists(), f"refusing to overwrite: {RESULT}")
    _require(not MARKDOWN.exists(), f"refusing to overwrite: {MARKDOWN}")
    _require(
        not subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=ROOT, text=True
        ).strip(),
        "T183 execution requires committed clean preregistration",
    )
    prereg = _load(PREREG)
    _require(
        prereg.get("status")
        == "PREREGISTERED_T183_HIDDEN_GATE_CONFIDENCE",
        "unexpected T183 status",
    )
    _require(
        _canonical_without(prereg, "preregistered_contract_sha256")
        == prereg.get("preregistered_contract_sha256"),
        "T183 preregistration hash differs",
    )
    for name, item in prereg["frozen_inputs"].items():
        verify_receipt(item, name)

    sessions: dict[str, Any] = {}
    gate_names = prereg["frozen_gate_initializers"]
    delta_threshold = 1.0e-7
    prefix_ticks = int(prereg["analysis_contract"]["prefix_ticks"])
    derivation: dict[str, list[float]] = {
        "negative_y_rescue": [],
        "positive_z_regression": [],
    }
    validation: dict[str, list[float]] = {
        "negative_y_rescue": [],
        "positive_z_regression": [],
    }
    case_results = []
    maximum_own_replay_error = 0.0
    started = time.time()
    for case in prereg["labeled_cases"]:
        source_session, transformed_session, gate = _graph_pair(
            case, sessions, gate_names
        )
        context = np.asarray(case["context"], dtype=np.float32)
        _require(context.shape == (64,), f"context shape: {case['case_id']}")
        _require(
            array_sha256(context) == case["context_sha256"],
            f"context hash: {case['case_id']}",
        )
        banks = []
        for bank_role, own_graph, target in (
            ("source_trace", "source", derivation),
            ("transformed_trace", "transformed", validation),
        ):
            rows = _read_rows(
                case[bank_role],
                ticks=prefix_ticks,
                expected_command=float(case["command_x_m_s"]),
                expected_context_sha256=case["context_sha256"],
            )
            bank = replay_bank(
                rows,
                context=context,
                source_session=source_session,
                transformed_session=transformed_session,
                gate_initializers=gate,
                own_graph=own_graph,
                delta_threshold=delta_threshold,
            )
            _require(
                bank["effective_rows"] > 0,
                f"no effective rows: {case['case_id']}:{bank_role}",
            )
            maximum_own_replay_error = max(
                maximum_own_replay_error,
                float(bank["maximum_own_replay_error"]),
            )
            target[case["family"]].extend(bank["effective_scores"])
            banks.append({"bank_role": bank_role, **_strip_scores(bank)})
        case_results.append(
            {
                key: case[key]
                for key in (
                    "case_id",
                    "family",
                    "checkpoint_pair",
                    "fit_id",
                    "command_x_m_s",
                )
            }
            | {"banks": banks}
        )

    threshold, derivation_margin = confidence_threshold(
        derivation["negative_y_rescue"],
        derivation["positive_z_regression"],
    )
    derivation_exact = (
        derivation_margin > 0.0
        and all(
            score >= threshold
            for score in derivation["negative_y_rescue"]
        )
        and all(
            score < threshold
            for score in derivation["positive_z_regression"]
        )
    )
    validation_rescue_correct = sum(
        score >= threshold for score in validation["negative_y_rescue"]
    )
    validation_regression_correct = sum(
        score < threshold for score in validation["positive_z_regression"]
    )
    validation_exact = (
        validation_rescue_correct
        == len(validation["negative_y_rescue"])
        and validation_regression_correct
        == len(validation["positive_z_regression"])
    )

    shared_results = []
    for case in prereg["unlabeled_shared_cases"]:
        source_session, transformed_session, gate = _graph_pair(
            case, sessions, gate_names
        )
        context = np.asarray(case["context"], dtype=np.float32)
        banks = []
        for bank_role, own_graph in (
            ("source_trace", "source"),
            ("transformed_trace", "transformed"),
        ):
            rows = _read_rows(
                case[bank_role],
                ticks=prefix_ticks,
                expected_command=float(case["command_x_m_s"]),
                expected_context_sha256=case["context_sha256"],
            )
            bank = replay_bank(
                rows,
                context=context,
                source_session=source_session,
                transformed_session=transformed_session,
                gate_initializers=gate,
                own_graph=own_graph,
                delta_threshold=delta_threshold,
            )
            maximum_own_replay_error = max(
                maximum_own_replay_error,
                float(bank["maximum_own_replay_error"]),
            )
            active = sum(
                score >= threshold for score in bank["effective_scores"]
            )
            banks.append(
                {
                    "bank_role": bank_role,
                    **_strip_scores(bank),
                    "would_select_transformed_rows": active,
                }
            )
        shared_results.append(
            {
                "case_id": case["case_id"],
                "role": "unlabeled_reporting_only",
                "banks": banks,
            }
        )

    alpha = prereg["unlabeled_alpha_case"]
    source_session, transformed_session, gate = _graph_pair(
        alpha, sessions, gate_names
    )
    alpha_context = np.asarray(alpha["context"], dtype=np.float32)
    _require(
        array_sha256(alpha_context) == alpha["context_sha256"],
        "T182B alpha context hash differs",
    )
    alpha_rows = _read_rows(
        alpha["candidate_trace"],
        ticks=int(prereg["analysis_contract"]["alpha_trace_ticks"]),
        expected_command=float(alpha["command_x_m_s"]),
        expected_context_sha256=alpha["context_sha256"],
    )
    alpha_bank = replay_bank(
        alpha_rows,
        context=alpha_context,
        source_session=source_session,
        transformed_session=transformed_session,
        gate_initializers=gate,
        own_graph=None,
        delta_threshold=delta_threshold,
    )
    alpha_selected = sum(
        score >= threshold for score in alpha_bank["effective_scores"]
    )
    alpha_report = {
        "case_id": alpha["case_id"],
        "role": "unlabeled_reporting_only",
        **_strip_scores(alpha_bank),
        "would_select_transformed_rows": alpha_selected,
    }

    checks = {
        "maximum_own_graph_replay_error_at_most_1e_6": (
            maximum_own_replay_error <= 1.0e-6
        ),
        "all_labeled_banks_have_effective_rows": all(
            bank["effective_rows"] > 0
            for case in case_results
            for bank in case["banks"]
        ),
        "positive_derivation_margin": derivation_margin > 0.0,
        "derivation_exact": derivation_exact,
        "validation_exact": validation_exact,
        "cpu_only_no_behavior_optimizer_hosted_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    basis: dict[str, Any] = {
        "schema_version": "open_duck.t183_hidden_gate_confidence_result.v1",
        "status": (
            "PASS_T183_HIDDEN_GATE_CONFIDENCE"
            if passed
            else "HOLD_T183_HIDDEN_GATE_CONFIDENCE"
        ),
        "decision": (
            prereg["decision_rule"]["pass"]
            if passed
            else prereg["decision_rule"]["fail"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "threshold": threshold,
        "derivation_margin": derivation_margin,
        "derivation": {
            "rescue_rows": len(derivation["negative_y_rescue"]),
            "regression_rows": len(derivation["positive_z_regression"]),
            "minimum_rescue_score": min(
                derivation["negative_y_rescue"]
            ),
            "maximum_regression_score": max(
                derivation["positive_z_regression"]
            ),
        },
        "validation": {
            "rescue_correct": validation_rescue_correct,
            "rescue_rows": len(validation["negative_y_rescue"]),
            "regression_correct": validation_regression_correct,
            "regression_rows": len(
                validation["positive_z_regression"]
            ),
        },
        "labeled_cases": case_results,
        "unlabeled_shared_cases": shared_results,
        "unlabeled_alpha_case": alpha_report,
        "execution": {
            "saved_trace_rows": (
                len(prereg["labeled_cases"]) * 2 * prefix_ticks
                + len(prereg["unlabeled_shared_cases"]) * 2 * prefix_ticks
                + len(alpha_rows)
            ),
            "new_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
            "wall_seconds": time.time() - started,
        },
        "authority": prereg["authority_after_result"],
    }
    basis["result_sha256"] = canonical_sha256(basis)
    RESULT.write_text(
        json.dumps(basis, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T183 hidden-gate confidence result\n\n"
        f"- Status: `{basis['status']}`\n"
        f"- Decision: `{basis['decision']}`\n"
        f"- Derivation margin: `{derivation_margin:.9g}`\n"
        f"- Validation rescue: `{validation_rescue_correct}/"
        f"{len(validation['negative_y_rescue'])}`\n"
        f"- Validation regression: `{validation_regression_correct}/"
        f"{len(validation['positive_z_regression'])}`\n"
        f"- Failed checks: `{failed}`\n"
        "- Behavior / optimizer / hosted compute / robot: `0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    return basis


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    result = run()
    print(result["status"])
    print(f"decision={result['decision']}")
    print(f"result_sha256={result['result_sha256']}")
    return 0 if result["status"].startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
