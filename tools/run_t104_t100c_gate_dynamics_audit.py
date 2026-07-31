#!/usr/bin/env python3
"""Run T104's frozen read-only gate-dynamics and expert-effect audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np
import onnx
from onnx import TensorProto, helper
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t104_t100c_gate_dynamics_preregistration.json"
OUTPUT = ANALYSIS / "t104_t100c_gate_dynamics_result.json"
MARKDOWN = ANALYSIS / "T104_T100C_GATE_DYNAMICS_RESULT_20260728.md"
DEFAULT_WORK_ROOT = Path(
    "D:/CodexArtifacts/open-duck-policy/t104_t100c_gate_dynamics_v1"
)
INSTRUMENTED = {
    "hidden_gate_score": (TensorProto.FLOAT, [1, 1]),
    "negative_com_gate": (TensorProto.BOOL, [1, 1]),
    "negative_adapter_location": (TensorProto.FLOAT, [1, 14]),
    "raw_continuous_actions": (TensorProto.FLOAT, [1, 14]),
    "velocity_bounded_actions": (TensorProto.FLOAT, [1, 14]),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any, ignored: str) -> str:
    payload = dict(value)
    payload.pop(ignored, None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def verify_receipt(value: Mapping[str, Any], label: str) -> None:
    path = Path(value["path"])
    if (
        not path.is_file()
        or path.stat().st_size != int(value["bytes"])
        or sha256(path) != value["sha256"]
    ):
        raise RuntimeError(f"T104 frozen receipt changed: {label}={path}")


def load_preregistration() -> dict[str, Any]:
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    if (
        value.get("status")
        != "PREREGISTERED_T104_T100C_GATE_DYNAMICS_AUDIT"
        or value.get("failed_checks")
        or canonical_sha256(value, "preregistered_contract_sha256")
        != value.get("preregistered_contract_sha256")
    ):
        raise RuntimeError("T104 preregistration changed")
    for label, item in value["repository_inputs"].items():
        verify_receipt(item, label)
    verify_receipt(value["gate_asset"], "gate_asset")
    for step, item in value["policies"].items():
        verify_receipt(item, f"policy:{step}")
    for index, item in enumerate(value["traces"]):
        verify_receipt(item["trace"], f"trace:{index}")
    return value


def instrument(source: Path, output: Path) -> None:
    model = onnx.load(source)
    existing = {item.name for item in model.graph.output}
    produced = {
        name for node in model.graph.node for name in node.output
    }
    missing = sorted(set(INSTRUMENTED) - produced)
    if missing:
        raise RuntimeError(f"T104 graph missing intermediates: {missing}")
    for name, (dtype, shape) in INSTRUMENTED.items():
        if name not in existing:
            model.graph.output.append(
                helper.make_tensor_value_info(name, dtype, shape)
            )
    onnx.checker.check_model(model)
    onnx.save(model, output)


def session(path: Path) -> ort.InferenceSession:
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    return ort.InferenceSession(
        str(path),
        sess_options=options,
        providers=["CPUExecutionProvider"],
    )


def feed(row: dict[str, Any]) -> dict[str, np.ndarray]:
    state = row["policy_state_input"]
    return {
        "obs": np.asarray(row["obs_state"], np.float32)[None, :],
        "previous_action": np.asarray(
            state["previous_action"], np.float32
        ),
        "h_in": np.asarray(state["h_in"], np.float32),
        "calibration_context": np.zeros((1, 64), np.float32),
    }


def percentile(values: Iterable[float], q: float) -> float:
    array = np.asarray(list(values), np.float64)
    return float(np.percentile(array, q)) if array.size else 0.0


def transitions(values: list[bool]) -> int:
    return sum(left != right for left, right in zip(values, values[1:]))


def longest_run(values: list[bool], target: bool) -> int:
    longest = 0
    current = 0
    for value in values:
        current = current + 1 if value == target else 0
        longest = max(longest, current)
    return longest


def summarize_trace(
    item: dict[str, Any],
    current: ort.InferenceSession,
    source: ort.InferenceSession,
    gate: dict[str, Any],
    warmup: int,
) -> dict[str, Any]:
    current_names = [output.name for output in current.get_outputs()]
    source_names = [output.name for output in source.get_outputs()]
    scores: list[float] = []
    active: list[bool] = []
    replay_errors: list[float] = []
    score_errors: list[float] = []
    head_abs: list[float] = []
    raw_delta_abs: list[float] = []
    bounded_delta_abs: list[float] = []
    final_delta_abs: list[float] = []
    per_tick_final_linf: list[float] = []
    gate_off_final_linf: list[float] = []
    raw_l1 = 0.0
    final_l1 = 0.0
    rows = 0

    mean = np.asarray(gate["model"]["mean"], np.float64)
    scale = np.asarray(gate["model"]["scale"], np.float64)
    coefficient = np.asarray(
        gate["model"]["coefficient"], np.float64
    )
    intercept = float(gate["model"]["intercept"])
    with Path(item["trace"]["path"]).open(encoding="utf-8") as stream:
        for line in stream:
            if not line.strip():
                continue
            row = json.loads(line)
            inputs = feed(row)
            current_value = dict(
                zip(current_names, current.run(None, inputs), strict=True)
            )
            source_value = dict(
                zip(source_names, source.run(None, inputs), strict=True)
            )
            expected_action = np.asarray(
                row["action"], np.float32
            )[None, :]
            expected_hidden = np.asarray(
                row["policy_state_output"]["h_out"], np.float32
            )
            expected_previous = np.asarray(
                row["policy_state_output"]["previous_action_out"],
                np.float32,
            )
            replay_errors.append(
                max(
                    float(
                        np.max(
                            np.abs(
                                current_value["continuous_actions"]
                                - expected_action
                            )
                        )
                    ),
                    float(
                        np.max(
                            np.abs(
                                current_value["h_out"] - expected_hidden
                            )
                        )
                    ),
                    float(
                        np.max(
                            np.abs(
                                current_value["previous_action_out"]
                                - expected_previous
                            )
                        )
                    ),
                )
            )
            score = float(
                np.asarray(current_value["hidden_gate_score"]).item()
            )
            gate_active = bool(
                np.asarray(current_value["negative_com_gate"]).item()
            )
            manual_score = float(
                ((expected_hidden[0].astype(np.float64) - mean) / scale)
                @ coefficient
                + intercept
            )
            scores.append(score)
            active.append(gate_active)
            score_errors.append(abs(score - manual_score))
            head_abs.extend(
                np.abs(
                    current_value["negative_adapter_location"]
                ).ravel().tolist()
            )
            raw_delta = np.abs(
                current_value["raw_continuous_actions"]
                - source_value["raw_continuous_actions"]
            )
            bounded_delta = np.abs(
                current_value["velocity_bounded_actions"]
                - source_value["velocity_bounded_actions"]
            )
            final_delta = np.abs(
                current_value["continuous_actions"]
                - source_value["continuous_actions"]
            )
            raw_delta_abs.extend(raw_delta.ravel().tolist())
            bounded_delta_abs.extend(bounded_delta.ravel().tolist())
            final_delta_abs.extend(final_delta.ravel().tolist())
            per_tick_final_linf.append(float(np.max(final_delta)))
            if not gate_active:
                gate_off_final_linf.append(float(np.max(final_delta)))
            raw_l1 += float(np.sum(raw_delta))
            final_l1 += float(np.sum(final_delta))
            rows += 1

    post_active = active[warmup:]
    post_scores = scores[warmup:]
    expected_active = item["population"] == "com_x_negative"
    return {
        **{key: value for key, value in item.items() if key != "trace"},
        "trace": item["trace"],
        "rows": rows,
        "post_warmup_rows": len(post_active),
        "expected_gate_active": expected_active,
        "maximum_trace_output_replay_error": max(
            replay_errors, default=0.0
        ),
        "maximum_gate_score_reconstruction_error": max(
            score_errors, default=0.0
        ),
        "gate_active_fraction": float(np.mean(active)),
        "gate_active_fraction_post_warmup": (
            float(np.mean(post_active)) if post_active else 0.0
        ),
        "expected_class_fraction_post_warmup": (
            float(np.mean(post_active))
            if expected_active and post_active
            else (
                float(np.mean(np.logical_not(post_active)))
                if post_active
                else 0.0
            )
        ),
        "gate_transitions": transitions(active),
        "gate_transitions_post_warmup": transitions(post_active),
        "longest_active_run": longest_run(active, True),
        "longest_inactive_run": longest_run(active, False),
        "first_active_tick": (
            next((index for index, value in enumerate(active) if value), None)
        ),
        "first_inactive_tick": (
            next(
                (index for index, value in enumerate(active) if not value),
                None,
            )
        ),
        "gate_score": {
            "minimum": min(scores, default=0.0),
            "p05": percentile(scores, 5),
            "median": percentile(scores, 50),
            "p95": percentile(scores, 95),
            "maximum": max(scores, default=0.0),
            "post_warmup_minimum": min(post_scores, default=0.0),
            "post_warmup_maximum": max(post_scores, default=0.0),
            "minimum_absolute": min(
                (abs(value) for value in scores), default=0.0
            ),
        },
        "negative_head_abs": {
            "p95": percentile(head_abs, 95),
            "maximum": max(head_abs, default=0.0),
        },
        "same_state_current_minus_step0": {
            "raw_abs_p95": percentile(raw_delta_abs, 95),
            "raw_abs_maximum": max(raw_delta_abs, default=0.0),
            "velocity_bounded_abs_p95": percentile(
                bounded_delta_abs, 95
            ),
            "velocity_bounded_abs_maximum": max(
                bounded_delta_abs, default=0.0
            ),
            "final_abs_p95": percentile(final_delta_abs, 95),
            "final_abs_maximum": max(final_delta_abs, default=0.0),
            "per_tick_final_linf_p95": percentile(
                per_tick_final_linf, 95
            ),
            "per_tick_final_linf_maximum": max(
                per_tick_final_linf, default=0.0
            ),
            "first_32_tick_final_linf_p95": percentile(
                per_tick_final_linf[:warmup], 95
            ),
            "post_32_tick_final_linf_p95": percentile(
                per_tick_final_linf[warmup:], 95
            ),
            "final_to_raw_l1_retention": (
                final_l1 / raw_l1 if raw_l1 else 1.0
            ),
            "maximum_gate_off_final_linf": max(
                gate_off_final_linf, default=0.0
            ),
        },
    }


def aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    post_rows = sum(item["post_warmup_rows"] for item in rows)
    active_rows = sum(
        item["gate_active_fraction_post_warmup"]
        * item["post_warmup_rows"]
        for item in rows
    )
    return {
        "traces": len(rows),
        "rows": sum(item["rows"] for item in rows),
        "post_warmup_rows": post_rows,
        "green_traces": sum(item["cell_green"] for item in rows),
        "failed_traces": sum(not item["cell_green"] for item in rows),
        "gate_active_fraction_post_warmup": (
            active_rows / post_rows if post_rows else 0.0
        ),
        "maximum_gate_transitions_post_warmup": max(
            (
                item["gate_transitions_post_warmup"]
                for item in rows
            ),
            default=0,
        ),
        "maximum_trace_output_replay_error": max(
            (
                item["maximum_trace_output_replay_error"]
                for item in rows
            ),
            default=0.0,
        ),
        "maximum_gate_score_reconstruction_error": max(
            (
                item["maximum_gate_score_reconstruction_error"]
                for item in rows
            ),
            default=0.0,
        ),
        "maximum_final_action_delta": max(
            (
                item["same_state_current_minus_step0"][
                    "final_abs_maximum"
                ]
                for item in rows
            ),
            default=0.0,
        ),
        "maximum_per_trace_final_action_delta_p95": max(
            (
                item["same_state_current_minus_step0"]["final_abs_p95"]
                for item in rows
            ),
            default=0.0,
        ),
        "maximum_gate_off_final_action_delta": max(
            (
                item["same_state_current_minus_step0"][
                    "maximum_gate_off_final_linf"
                ]
                for item in rows
            ),
            default=0.0,
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument(
        "--work-root", type=Path, default=DEFAULT_WORK_ROOT
    )
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN, args.work_root):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T104 output: {path}")
    prereg = load_preregistration()
    work_root = args.work_root.resolve()
    work_root.mkdir(parents=True)
    policies: dict[str, ort.InferenceSession] = {}
    for step, item in prereg["policies"].items():
        output = work_root / f"step_{step}_instrumented.onnx"
        instrument(Path(item["path"]), output)
        policies[step] = session(output)
    gate = json.loads(
        Path(prereg["gate_asset"]["path"]).read_text(encoding="utf-8")
    )
    warmup = int(prereg["measurements"]["warmup_ticks"])
    traces = [
        summarize_trace(
            item,
            policies[str(item["step"])],
            policies["0"],
            gate,
            warmup,
        )
        for item in prereg["traces"]
    ]
    moving = [
        item for item in traces if item["command_x_m_s"] > 0.0
    ]
    nominal_moving = [
        item for item in moving if item["population"] == "nominal"
    ]
    endpoint_moving = [
        item
        for item in moving
        if item["population"] == "com_x_negative"
    ]
    endpoint_failing = [
        item for item in endpoint_moving if not item["cell_green"]
    ]
    endpoint_half = [
        item for item in endpoint_moving if item["step"] == 1_003_520
    ]
    endpoint_final = [
        item for item in endpoint_moving if item["step"] == 2_007_040
    ]
    aggregates = {
        "nominal_moving": aggregate(nominal_moving),
        "com_x_negative_moving": aggregate(endpoint_moving),
        "com_x_negative_failing": aggregate(endpoint_failing),
        "com_x_negative_half": aggregate(endpoint_half),
        "com_x_negative_final": aggregate(endpoint_final),
    }
    threshold = float(
        prereg["measurements"][
            "maximum_expected_class_error_fraction"
        ]
    )
    nominal_false_active = aggregates["nominal_moving"][
        "gate_active_fraction_post_warmup"
    ]
    endpoint_false_inactive = (
        1.0
        - aggregates["com_x_negative_moving"][
            "gate_active_fraction_post_warmup"
        ]
    )
    too_many_transitions = any(
        item["gate_transitions_post_warmup"]
        > prereg["measurements"][
            "maximum_post_warmup_transitions_per_trace"
        ]
        for item in endpoint_failing
    )
    gate_inconsistent = bool(
        nominal_false_active > threshold
        or endpoint_false_inactive > threshold
        or too_many_transitions
    )
    material = (
        aggregates["com_x_negative_moving"][
            "maximum_final_action_delta"
        ]
        > prereg["measurements"]["material_final_action_delta"]
    )
    failures_increase = (
        aggregates["com_x_negative_final"]["failed_traces"]
        > aggregates["com_x_negative_half"]["failed_traces"]
    )
    if gate_inconsistent:
        classification = "HARD_GATE_DYNAMICS_INCONSISTENT"
        decision = prereg["decision_rule"]["gate_dynamics_decision"]
    elif material and failures_increase:
        classification = "ACTIVE_EXPERT_CLOSED_LOOP_DRIFT"
        decision = prereg["decision_rule"]["expert_drift_decision"]
    else:
        classification = "NO_HIDDEN_EXPERT_CAUSAL_TARGET"
        decision = prereg["decision_rule"]["otherwise"]
    checks = {
        "all_thirty_two_traces_replayed": len(traces) == 32,
        "all_trace_outputs_replay_exact": max(
            item["maximum_trace_output_replay_error"]
            for item in traces
        )
        <= prereg["measurements"]["trace_replay_max_abs_tolerance"],
        "all_gate_scores_reconstruct_exact": max(
            item["maximum_gate_score_reconstruction_error"]
            for item in traces
        )
        <= prereg["measurements"]["gate_score_reconstruction_tolerance"],
        "gate_boolean_equals_score_sign": all(
            (
                item["gate_active_fraction"] == 0.0
                and item["gate_score"]["maximum"] < 0.0
            )
            or item["gate_score"]["maximum"] >= 0.0
            for item in traces
        ),
        "gate_off_zeroes_expert_effect": max(
            item["same_state_current_minus_step0"][
                "maximum_gate_off_final_linf"
            ]
            for item in traces
        )
        <= 1.0e-7,
        "all_metrics_finite": all(
            np.isfinite(value)
            for item in traces
            for value in (
                item["gate_active_fraction"],
                item["maximum_trace_output_replay_error"],
                item["maximum_gate_score_reconstruction_error"],
                item["same_state_current_minus_step0"][
                    "final_abs_maximum"
                ],
            )
        ),
        "no_simulator_optimizer_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value: dict[str, Any] = {
        "schema_version": "open_duck.t104_t100c_gate_dynamics_result.v1",
        "status": (
            "PASS_T104_T100C_GATE_DYNAMICS_AUDIT"
            if not failed
            else "HOLD_T104_T100C_GATE_DYNAMICS_AUDIT"
        ),
        "classification": classification if not failed else "INVALID_AUDIT",
        "decision": decision if not failed else "HOLD_WITHOUT_SUCCESSOR",
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "aggregates": aggregates,
        "decision_inputs": {
            "nominal_false_active_fraction_post_warmup": (
                nominal_false_active
            ),
            "negative_com_false_inactive_fraction_post_warmup": (
                endpoint_false_inactive
            ),
            "failing_trace_exceeds_transition_limit": (
                too_many_transitions
            ),
            "expert_effect_material": material,
            "negative_com_failures_increase_half_to_final": (
                failures_increase
            ),
        },
        "traces": traces,
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "trace_rows": sum(item["rows"] for item in traces),
            "simulator_steps": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "interpretation": {
            "hosted_run_earned": False,
            "behavior_rerun_earned": False,
            "gate5_open": False,
        },
        "authority": {
            "successor_cpu_preregistration": bool(
                not failed and decision.startswith("EARN_")
            ),
            "training": False,
            "colab": False,
            "deployment": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["result_sha256"] = canonical_sha256(value, "result_sha256")
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T104 T100C gate-dynamics result",
                "",
                f"- Status: `{value['status']}`",
                f"- Classification: `{value['classification']}`",
                f"- Decision: `{value['decision']}`",
                (
                    "- Nominal false-active / negative-COM false-inactive: "
                    f"`{nominal_false_active:.6f} / "
                    f"{endpoint_false_inactive:.6f}`"
                ),
                (
                    "- Negative-COM half/final moving failures: "
                    f"`{aggregates['com_x_negative_half']['failed_traces']} / "
                    f"{aggregates['com_x_negative_final']['failed_traces']}`"
                ),
                (
                    "- Maximum final action correction: "
                    f"`{aggregates['com_x_negative_moving']['maximum_final_action_delta']:.9f}`"
                ),
                "- Training / Colab / robot: `0 / 0 / 0`",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"classification={value['classification']}")
    print(f"decision={value['decision']}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
