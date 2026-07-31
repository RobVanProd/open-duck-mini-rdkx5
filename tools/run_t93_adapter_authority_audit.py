#!/usr/bin/env python3
"""Run T93's frozen read-only recurrent-adapter authority audit."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import onnx
from onnx import TensorProto, helper, numpy_helper
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t93_adapter_authority_preregistration.json"
OUTPUT = ANALYSIS / "t93_adapter_authority_result.json"
MARKDOWN = ANALYSIS / "T93_ADAPTER_AUTHORITY_RESULT_20260728.md"
INTERMEDIATES = {
    "adapter_hidden_pre": 64,
    "h_out": 64,
    "adapter_location": 14,
    "base_anchored_location": 14,
    "raw_continuous_actions": 14,
    "velocity_bounded_actions": 14,
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


def instrument(source: Path, output: Path, zero_adapter: bool) -> None:
    model = onnx.load(source)
    existing = {item.name for item in model.graph.output}
    for name, width in INTERMEDIATES.items():
        if name not in existing:
            model.graph.output.append(
                helper.make_tensor_value_info(
                    name, TensorProto.FLOAT, [1, width]
                )
            )
    if zero_adapter:
        for index, item in enumerate(model.graph.initializer):
            if item.name in {"adapter_weight", "adapter_bias"}:
                zeros = np.zeros_like(numpy_helper.to_array(item))
                model.graph.initializer[index].CopyFrom(
                    numpy_helper.from_array(zeros, name=item.name)
                )
    onnx.checker.check_model(model)
    onnx.save(model, output)


def graph_contract(path: Path) -> dict[str, Any]:
    model = onnx.load(path)
    producers = {
        output: node
        for node in model.graph.node
        for output in node.output
    }
    adapter = producers["adapter_location"]
    anchored = producers["anchored_location"]
    inputs_used = {
        name for node in model.graph.node for name in node.input
    }
    return {
        "adapter_location_producer": adapter.op_type,
        "adapter_location_inputs": list(adapter.input),
        "anchored_location_producer": anchored.op_type,
        "anchored_location_inputs": list(anchored.input),
        "explicit_adapter_cap_present": adapter.op_type in {"Clip", "Mul"},
        "calibration_context_used": "calibration_context" in inputs_used,
        "adapter_path_is_unbounded_linear_head": (
            adapter.op_type == "Gemm"
            and list(adapter.input)
            == ["h_out", "adapter_weight", "adapter_bias"]
            and anchored.op_type == "Add"
            and "adapter_location" in anchored.input
        ),
    }


def percentile(values: list[float], q: float) -> float:
    return float(np.percentile(np.asarray(values, np.float64), q))


def replay(
    trace: Path,
    session: ort.InferenceSession,
    base_session: ort.InferenceSession,
) -> dict[str, Any]:
    names = [item.name for item in session.get_outputs()]
    action_errors: list[float] = []
    hidden_abs: list[float] = []
    adapter_abs: list[float] = []
    pre_delta_abs: list[float] = []
    final_delta_abs: list[float] = []
    material_ticks = 0
    erased_ticks = 0
    rows = 0
    with trace.open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            state = row["policy_state_input"]
            feed = {
                "obs": np.asarray(row["obs_state"], np.float32)[None, :],
                "previous_action": np.asarray(
                    state["previous_action"], np.float32
                ),
                "h_in": np.asarray(state["h_in"], np.float32),
                "calibration_context": np.zeros((1, 64), np.float32),
            }
            current = dict(zip(names, session.run(None, feed)))
            base = dict(zip(names, base_session.run(None, feed)))
            expected = np.asarray(row["action"], np.float32)[None, :]
            action_errors.append(
                float(np.max(np.abs(current["continuous_actions"] - expected)))
            )
            hidden_abs.extend(np.abs(current["h_out"]).ravel().tolist())
            adapter_abs.extend(
                np.abs(current["adapter_location"]).ravel().tolist()
            )
            pre = np.abs(
                current["raw_continuous_actions"]
                - base["raw_continuous_actions"]
            )
            final = np.abs(
                current["continuous_actions"] - base["continuous_actions"]
            )
            pre_delta_abs.extend(pre.ravel().tolist())
            final_delta_abs.extend(final.ravel().tolist())
            if float(np.max(pre)) > 0.005:
                material_ticks += 1
                if float(np.max(final)) <= 1e-7:
                    erased_ticks += 1
            rows += 1
    pre_sum = float(np.sum(pre_delta_abs))
    final_sum = float(np.sum(final_delta_abs))
    return {
        "rows": rows,
        "maximum_trace_action_error": max(action_errors, default=0.0),
        "hidden_abs_p95": percentile(hidden_abs, 95),
        "hidden_abs_max": max(hidden_abs, default=0.0),
        "hidden_abs_ge_0_99_fraction": float(
            np.mean(np.asarray(hidden_abs) >= 0.99)
        ),
        "adapter_location_abs_p95": percentile(adapter_abs, 95),
        "adapter_location_abs_max": max(adapter_abs, default=0.0),
        "preboundary_adapter_action_delta_abs_p95": percentile(
            pre_delta_abs, 95
        ),
        "preboundary_adapter_action_delta_abs_max": max(
            pre_delta_abs, default=0.0
        ),
        "final_adapter_action_delta_abs_p95": percentile(
            final_delta_abs, 95
        ),
        "final_adapter_action_delta_abs_max": max(
            final_delta_abs, default=0.0
        ),
        "final_to_preboundary_l1_retention": (
            final_sum / pre_sum if pre_sum > 0.0 else 1.0
        ),
        "material_adapter_ticks": material_ticks,
        "erased_material_adapter_ticks": erased_ticks,
        "erased_material_adapter_tick_fraction": (
            erased_ticks / material_ticks if material_ticks else 0.0
        ),
    }


def aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total_values = sum(item["rows"] * 64 for item in rows)
    saturated_values = sum(
        item["hidden_abs_ge_0_99_fraction"] * item["rows"] * 64
        for item in rows
    )
    material = sum(item["material_adapter_ticks"] for item in rows)
    erased = sum(item["erased_material_adapter_ticks"] for item in rows)
    pre_proxy = sum(
        item["preboundary_adapter_action_delta_abs_p95"] * item["rows"]
        for item in rows
    )
    final_proxy = sum(
        item["final_adapter_action_delta_abs_p95"] * item["rows"]
        for item in rows
    )
    return {
        "traces": len(rows),
        "rows": sum(item["rows"] for item in rows),
        "maximum_trace_action_error": max(
            item["maximum_trace_action_error"] for item in rows
        ),
        "hidden_abs_ge_0_99_fraction": (
            saturated_values / total_values if total_values else 0.0
        ),
        "adapter_location_abs_p95_max_across_traces": max(
            item["adapter_location_abs_p95"] for item in rows
        ),
        "preboundary_adapter_action_delta_abs_p95_max_across_traces": max(
            item["preboundary_adapter_action_delta_abs_p95"]
            for item in rows
        ),
        "final_adapter_action_delta_abs_p95_max_across_traces": max(
            item["final_adapter_action_delta_abs_p95"] for item in rows
        ),
        "final_to_preboundary_p95_weighted_retention": (
            final_proxy / pre_proxy if pre_proxy > 0.0 else 1.0
        ),
        "material_adapter_ticks": material,
        "erased_material_adapter_ticks": erased,
        "erased_material_adapter_tick_fraction": (
            erased / material if material else 0.0
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise PermissionError("T93 requires --execute")
    for path in (OUTPUT, MARKDOWN, args.work_root):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T93 output: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    if (
        prereg["status"] != "PREREGISTERED_T93_ADAPTER_AUTHORITY_AUDIT"
        or canonical_sha256(prereg, "preregistered_contract_sha256")
        != prereg["preregistered_contract_sha256"]
    ):
        raise ValueError("T93 preregistration changed")
    for item in prereg["traces"]:
        path = Path(item["trace"]["path"])
        if sha256(path) != item["trace"]["sha256"]:
            raise ValueError(f"T93 trace changed: {path}")
    args.work_root.mkdir(parents=True)
    contracts: dict[str, Any] = {}
    sessions: dict[str, tuple[ort.InferenceSession, ort.InferenceSession]] = {}
    for checkpoint, item in prereg["policies"].items():
        source = Path(item["path"])
        if sha256(source) != item["sha256"]:
            raise ValueError(f"T93 policy changed: {source}")
        current_path = args.work_root / f"{checkpoint}_instrumented.onnx"
        base_path = args.work_root / f"{checkpoint}_base_only.onnx"
        instrument(source, current_path, False)
        instrument(source, base_path, True)
        contracts[checkpoint] = graph_contract(source)
        sessions[checkpoint] = (
            ort.InferenceSession(
                str(current_path), providers=["CPUExecutionProvider"]
            ),
            ort.InferenceSession(
                str(base_path), providers=["CPUExecutionProvider"]
            ),
        )
    traces: list[dict[str, Any]] = []
    for item in prereg["traces"]:
        current, base = sessions[item["checkpoint_id"]]
        metrics = replay(Path(item["trace"]["path"]), current, base)
        traces.append({**{k: v for k, v in item.items() if k != "trace"}, **metrics})
    moving = [item for item in traces if item["command_x_m_s"] > 0.0]
    nominal_moving = aggregate(
        [item for item in moving if item["population"] == "nominal"]
    )
    com_moving = aggregate(
        [item for item in moving if item["population"] == "com_x_negative"]
    )
    all_contracts_unbounded = all(
        item["adapter_path_is_unbounded_linear_head"]
        and not item["explicit_adapter_cap_present"]
        for item in contracts.values()
    )
    hard_cap = not all_contracts_unbounded
    hidden_saturation = (
        not hard_cap
        and com_moving["hidden_abs_ge_0_99_fraction"] >= 0.50
        and com_moving["hidden_abs_ge_0_99_fraction"]
        - nominal_moving["hidden_abs_ge_0_99_fraction"]
        >= 0.10
    )
    downstream = (
        not hard_cap
        and not hidden_saturation
        and (
            com_moving["final_to_preboundary_p95_weighted_retention"] <= 0.25
            or com_moving["erased_material_adapter_tick_fraction"] >= 0.50
        )
    )
    if hard_cap:
        classification = "EXPLICIT_ADAPTER_AUTHORITY_CAP_PRESENT"
        decision = "EARN_EXACT_CAP_REMOVAL_CPU_SCREEN_ONLY"
    elif hidden_saturation:
        classification = "COM_FAILURE_ALIGNS_WITH_HIDDEN_SATURATION"
        decision = "EARN_HIDDEN_RANGE_CPU_SCREEN_ONLY"
    elif downstream:
        classification = "DEPLOYMENT_WRAPPERS_SUPPRESS_ADAPTER_AUTHORITY"
        decision = "EARN_WRAPPER_ORDER_CPU_SCREEN_ONLY"
    else:
        classification = "NO_HARD_ADAPTER_AUTHORITY_LIMIT_FOUND"
        decision = "CLOSE_ADAPTER_AUTHORITY_HYPOTHESIS"
    checks = {
        "all_trace_outputs_replay_exact": max(
            item["maximum_trace_action_error"] for item in traces
        )
        <= prereg["measurements"]["trace_output_tolerance"],
        "both_graphs_share_exact_adapter_topology": len(
            {
                json.dumps(value, sort_keys=True)
                for value in contracts.values()
            }
        )
        == 1,
        "calibration_context_is_unused_compatibility_input": all(
            not item["calibration_context_used"] for item in contracts.values()
        ),
        "all_metrics_finite": all(
            np.isfinite(value)
            for item in traces
            for value in item.values()
            if isinstance(value, (float, int))
        ),
        "all_32_frozen_traces_replayed": len(traces) == 32,
        "no_simulator_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value: dict[str, Any] = {
        "schema_version": "open_duck.t93_adapter_authority_result.v1",
        "status": (
            "PASS_T93_ADAPTER_AUTHORITY_AUDIT"
            if not failed
            else "HOLD_T93_ADAPTER_AUTHORITY_AUDIT"
        ),
        "classification": classification if not failed else "INVALID_AUDIT",
        "decision": decision if not failed else "HOLD_WITHOUT_SUCCESSOR",
        "graph_contracts": contracts,
        "aggregates": {
            "nominal_moving": nominal_moving,
            "com_x_negative_moving": com_moving,
        },
        "traces": traces,
        "checks": checks,
        "failed_checks": failed,
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "interpretation": {
            "adapter_cap_source_correction": (
                "T78 uses reference_residual_recurrent_adapter, not the older "
                "response-conditioned actor with ADAPTER_MAX_NORMALIZED=0.25."
            ),
            "hosted_run_earned": False,
        },
        "execution": {
            "trace_rows": sum(item["rows"] for item in traces),
            "simulator_steps": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "successor_cpu_preregistration": bool(not failed and decision.startswith("EARN_")),
            "hosted_training": False,
            "deployment": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["result_sha256"] = canonical_sha256(value, "result_sha256")
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T93 adapter-authority result",
                "",
                f"- Status: `{value['status']}`",
                f"- Classification: `{value['classification']}`",
                f"- Decision: `{value['decision']}`",
                f"- Failed checks: `{failed}`",
                f"- Frozen trace rows replayed: `{value['execution']['trace_rows']}`",
                "- Hosted compute / simulator / robot: `0 / 0 / 0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"classification={value['classification']}")
    print(f"decision={value['decision']}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
