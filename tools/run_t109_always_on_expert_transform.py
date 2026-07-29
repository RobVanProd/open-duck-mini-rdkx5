#!/usr/bin/env python3
"""Apply and verify T109's exact always-on expert transform."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import onnx
from onnx import helper, numpy_helper
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t109_always_on_expert_preregistration.json"
T104_PREREG = ANALYSIS / "t104_t100c_gate_dynamics_preregistration.json"
OUTPUT = ANALYSIS / "t109_always_on_expert_result.json"
MARKDOWN = ANALYSIS / "T109_ALWAYS_ON_EXPERT_RESULT_20260728.md"
DEFAULT_WORK_ROOT = Path(
    "D:/CodexArtifacts/open-duck-policy/t109_always_on_expert_v1"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


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
        raise RuntimeError(f"T109 frozen receipt changed: {label}={path}")


def load_preregistration() -> dict[str, Any]:
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    if (
        value.get("status")
        != "PREREGISTERED_T109_ALWAYS_ON_EXPERT_TRANSFORM"
        or value.get("failed_checks")
        or canonical_sha256(value, "preregistered_contract_sha256")
        != value.get("preregistered_contract_sha256")
    ):
        raise RuntimeError("T109 preregistration changed")
    for label, item in value["repository_inputs"].items():
        verify_receipt(item, label)
    for step, item in value["policies"].items():
        verify_receipt(item, f"policy:{step}")
    return value


def initializer_map(model: onnx.ModelProto) -> dict[str, str]:
    return {
        item.name: hashlib.sha256(
            numpy_helper.to_array(item).tobytes()
        ).hexdigest()
        for item in model.graph.initializer
    }


def graph_abi(model: onnx.ModelProto) -> tuple[str, ...]:
    return tuple(
        f"{kind}:{item.name}:{item.type.tensor_type.elem_type}:"
        f"{','.join(str(dim.dim_value) for dim in item.type.tensor_type.shape.dim)}"
        for kind, items in (
            ("input", model.graph.input),
            ("output", model.graph.output),
        )
        for item in items
    )


def transform(source: Path, output: Path) -> dict[str, Any]:
    model = onnx.load(source)
    original = copy.deepcopy(model)
    indices = [
        index
        for index, node in enumerate(model.graph.node)
        if node.op_type == "Where"
        and list(node.input)
        == [
            "negative_com_gate",
            "negative_adapter_location",
            "zero_adapter_location",
        ]
        and list(node.output) == ["conditional_adapter_location"]
    ]
    if len(indices) != 1:
        raise RuntimeError(f"T109 source topology changed: {indices}")
    index = indices[0]
    model.graph.node[index].CopyFrom(
        helper.make_node(
            "Identity",
            ["negative_adapter_location"],
            ["conditional_adapter_location"],
            name="t109_always_on_negative_adapter",
        )
    )
    onnx.checker.check_model(model)
    onnx.save(model, output)
    reloaded = onnx.load(output)
    gate_consumers = [
        node.op_type
        for node in reloaded.graph.node
        if "negative_com_gate" in node.input
    ]
    return {
        "source": receipt(source),
        "output": receipt(output),
        "node_count_exact": (
            len(original.graph.node) == len(reloaded.graph.node)
        ),
        "abi_exact": graph_abi(original) == graph_abi(reloaded),
        "initializers_exact": (
            initializer_map(original) == initializer_map(reloaded)
        ),
        "replacement_exact": (
            reloaded.graph.node[index].op_type == "Identity"
            and list(reloaded.graph.node[index].input)
            == ["negative_adapter_location"]
            and list(reloaded.graph.node[index].output)
            == ["conditional_adapter_location"]
        ),
        "negative_gate_consumer_count": len(gate_consumers),
    }


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


def selected_rows(path: Path, ticks: list[Any]) -> list[dict[str, Any]]:
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    wanted = {int(value) for value in ticks if value != "last"}
    wanted.add(int(rows[-1]["tick"]))
    return [row for row in rows if int(row["tick"]) in wanted]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument(
        "--work-root", type=Path, default=DEFAULT_WORK_ROOT
    )
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN, args.work_root):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T109 output: {path}")
    prereg = load_preregistration()
    trace_basis = json.loads(T104_PREREG.read_text(encoding="utf-8"))
    work_root = args.work_root.resolve()
    work_root.mkdir(parents=True)
    transforms: dict[str, Any] = {}
    hard_sessions: dict[str, ort.InferenceSession] = {}
    always_sessions: dict[str, ort.InferenceSession] = {}
    for step, item in prereg["policies"].items():
        target = work_root / step / "action_margin_always_on.onnx"
        target.parent.mkdir(parents=True)
        transforms[step] = transform(Path(item["path"]), target)
        hard_sessions[step] = session(Path(item["path"]))
        always_sessions[step] = session(target)

    step0_errors: list[float] = []
    x0_errors: list[float] = []
    active_errors: list[float] = []
    inactive_deltas: list[float] = []
    hidden_errors: list[float] = []
    previous_errors: list[float] = []
    sampled = 0
    for item in trace_basis["traces"]:
        step = str(item["step"])
        hard = hard_sessions[step]
        always = always_sessions[step]
        for row in selected_rows(
            Path(item["trace"]["path"]),
            prereg["contract"]["sample_ticks"],
        ):
            inputs = feed(row)
            hard_action, hard_previous, hard_hidden = hard.run(
                ["continuous_actions", "previous_action_out", "h_out"],
                inputs,
            )
            action, previous, hidden = always.run(
                ["continuous_actions", "previous_action_out", "h_out"],
                inputs,
            )
            delta = float(np.max(np.abs(action - hard_action)))
            hidden_errors.append(
                float(np.max(np.abs(hidden - hard_hidden)))
            )
            previous_errors.append(
                float(np.max(np.abs(previous - action)))
            )
            score = float(
                np.asarray(
                    hard.run(["hidden_gate_score"], inputs)[0]
                ).item()
            ) if any(
                output.name == "hidden_gate_score"
                for output in hard.get_outputs()
            ) else None
            # Deployed graphs do not expose score; reconstruct its sign from
            # T104's frozen score asset and the identical h_out.
            if score is None:
                gate = json.loads(
                    (
                        ANALYSIS / "t98_hidden_gate_asset.json"
                    ).read_text(encoding="utf-8")
                )["model"]
                h = hidden[0].astype(np.float64)
                score = float(
                    ((h - np.asarray(gate["mean"])) / np.asarray(gate["scale"]))
                    @ np.asarray(gate["coefficient"])
                    + float(gate["intercept"])
                )
            if step == "0":
                step0_errors.append(delta)
            elif float(item["command_x_m_s"]) == 0.0:
                x0_errors.append(delta)
            elif score >= 0.0:
                active_errors.append(delta)
            else:
                inactive_deltas.append(delta)
            sampled += 1

    checks = {
        "all_three_graphs_transformed": len(transforms) == 3,
        "all_node_counts_exact": all(
            item["node_count_exact"] for item in transforms.values()
        ),
        "all_abis_exact": all(
            item["abi_exact"] for item in transforms.values()
        ),
        "all_initializers_exact": all(
            item["initializers_exact"] for item in transforms.values()
        ),
        "all_replacements_exact": all(
            item["replacement_exact"] for item in transforms.values()
        ),
        "gate_has_no_action_path_consumer": all(
            item["negative_gate_consumer_count"] == 0
            for item in transforms.values()
        ),
        "step_zero_exact": max(step0_errors, default=0.0)
        <= prereg["contract"]["maximum_step0_output_error"],
        "x0_exact": max(x0_errors, default=0.0)
        <= prereg["contract"]["maximum_x0_output_error"],
        "hard_active_branch_exact": max(active_errors, default=0.0)
        <= prereg["contract"]["maximum_active_branch_output_error"],
        "hard_inactive_branch_changes_materially": max(
            inactive_deltas, default=0.0
        )
        > prereg["contract"]["minimum_inactive_branch_output_delta"],
        "recurrent_hidden_exact": max(hidden_errors, default=0.0)
        <= 1.0e-7,
        "previous_action_out_equals_action": max(
            previous_errors, default=0.0
        )
        <= 1.0e-7,
        "all_metrics_finite": all(
            np.isfinite(value)
            for value in [
                *step0_errors,
                *x0_errors,
                *active_errors,
                *inactive_deltas,
                *hidden_errors,
                *previous_errors,
            ]
        ),
        "no_behavior_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value: dict[str, Any] = {
        "schema_version": "open_duck.t109_always_on_expert_result.v1",
        "status": (
            "PASS_T109_ALWAYS_ON_EXPERT_TRANSFORM"
            if not failed
            else "HOLD_T109_ALWAYS_ON_EXPERT_TRANSFORM"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if not failed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "transforms": transforms,
        "metrics": {
            "sampled_rows": sampled,
            "maximum_step0_error": max(step0_errors, default=0.0),
            "maximum_x0_error": max(x0_errors, default=0.0),
            "maximum_active_branch_error": max(
                active_errors, default=0.0
            ),
            "maximum_inactive_branch_delta": max(
                inactive_deltas, default=0.0
            ),
            "maximum_hidden_error": max(hidden_errors, default=0.0),
        },
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "graphs_transformed": len(transforms),
            "sampled_trace_rows": sampled,
            "behavior_cells": 0,
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
            "t110_nominal_preregistration": not failed,
            "behavior": False,
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
                "# T109 always-on expert result",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                f"- Sampled rows: `{sampled}`",
                (
                    "- Maximum inactive-branch action delta: "
                    f"`{value['metrics']['maximum_inactive_branch_delta']:.6f}`"
                ),
                "- Behavior / training / Colab / robot: `0 / 0 / 0 / 0`",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
