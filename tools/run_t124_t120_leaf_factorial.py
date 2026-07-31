#!/usr/bin/env python3
"""Run the read-only T120 router/expert leaf-factorial attribution."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
from typing import Any, Mapping

import numpy as np
import onnx
from onnx import helper, numpy_helper
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t124_t120_leaf_factorial_preregistration.json"
RESULT = ANALYSIS / "t124_t120_leaf_factorial_result.json"
MARKDOWN = ANALYSIS / "T124_T120_LEAF_FACTORIAL_RESULT_20260729.md"
WORK = Path("D:/CodexArtifacts/open-duck-policy/t124_t120_leaf_factorial_v1")
ROUTER = ["hidden_gate_coefficient", "hidden_gate_intercept"]
EXPERT = ["negative_adapter_weight", "negative_adapter_bias"]
INTERNAL_OUTPUTS = {
    "soft_negative_com_weight": [1, 1],
    "negative_adapter_location": [1, 14],
    "conditional_adapter_location": [1, 14],
}


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


def verify(value: Mapping[str, Any]) -> None:
    path = Path(value["path"])
    if (
        not path.is_file()
        or path.stat().st_size != value["bytes"]
        or sha256(path) != value["sha256"]
    ):
        raise RuntimeError(f"changed T124 input: {path}")


def load() -> dict[str, Any]:
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    if (
        value["status"] != "PREREGISTERED_T124_T120_LEAF_FACTORIAL"
        or value["failed_checks"]
        or canonical_sha256(value, "preregistered_contract_sha256")
        != value["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T124 preregistration changed")
    for item in value["frozen_inputs"].values():
        verify(item)
    for item in value["graphs"].values():
        verify(item)
    for item in value["traces"].values():
        verify(item)
    return value


def initializer_map(model: onnx.ModelProto) -> dict[str, onnx.TensorProto]:
    return {item.name: item for item in model.graph.initializer}


def array_map(model: onnx.ModelProto) -> dict[str, np.ndarray]:
    return {
        name: numpy_helper.to_array(item).copy()
        for name, item in initializer_map(model).items()
    }


def replace_initializer(
    model: onnx.ModelProto, name: str, value: np.ndarray
) -> None:
    items = initializer_map(model)
    if name not in items:
        raise RuntimeError(f"T124 missing initializer: {name}")
    items[name].CopyFrom(numpy_helper.from_array(value, name=name))


def instrument(model: onnx.ModelProto) -> onnx.ModelProto:
    existing = {item.name for item in model.graph.output}
    for name, shape in INTERNAL_OUTPUTS.items():
        if name not in existing:
            model.graph.output.append(
                helper.make_tensor_value_info(
                    name, onnx.TensorProto.FLOAT, shape
                )
            )
    onnx.checker.check_model(model)
    return model


def build_variants(
    half_path: Path, final_path: Path
) -> tuple[dict[str, Path], dict[str, Any]]:
    half = onnx.load(half_path)
    final = onnx.load(final_path)
    half_arrays = array_map(half)
    final_arrays = array_map(final)
    changed = sorted(
        name
        for name in half_arrays
        if name in final_arrays
        and not np.array_equal(half_arrays[name], final_arrays[name])
    )
    expected = sorted(ROUTER + EXPERT)
    if changed != expected:
        raise RuntimeError(
            f"T124 exported actor scope changed: {changed} != {expected}"
        )
    paths = {}
    for code, router_source, expert_source in (
        ("HH", half_arrays, half_arrays),
        ("HF", half_arrays, final_arrays),
        ("FH", final_arrays, half_arrays),
        ("FF", final_arrays, final_arrays),
    ):
        model = onnx.load(half_path)
        for name in ROUTER:
            replace_initializer(model, name, router_source[name])
        for name in EXPERT:
            replace_initializer(model, name, expert_source[name])
        path = WORK / f"{code}.onnx"
        onnx.save(instrument(model), path)
        paths[code] = path
    return paths, {
        "changed_initializers": changed,
        "expected_changed_initializers": expected,
        "only_factorial_leaves_changed": changed == expected,
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


def rows(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
    ]


def evaluate(
    sessions: dict[str, ort.InferenceSession], values: list[dict[str, Any]]
) -> dict[str, dict[str, np.ndarray]]:
    output_names = [
        "continuous_actions",
        "soft_negative_com_weight",
        "negative_adapter_location",
        "conditional_adapter_location",
    ]
    output = {
        code: {name: [] for name in output_names} for code in sessions
    }
    for row in values:
        state = row["policy_state_input"]
        feed = {
            "obs": np.asarray(row["obs_state"], np.float32)[None, :],
            "previous_action": np.asarray(
                state["previous_action"], np.float32
            ),
            "h_in": np.asarray(state["h_in"], np.float32),
            "calibration_context": np.zeros((1, 64), np.float32),
        }
        for code, runtime in sessions.items():
            actual = runtime.run(output_names, feed)
            for name, value in zip(output_names, actual, strict=True):
                output[code][name].append(np.asarray(value)[0].copy())
    return {
        code: {
            name: np.asarray(array, dtype=np.float64)
            for name, array in values_by_name.items()
        }
        for code, values_by_name in output.items()
    }


def rms(value: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(value))))


def summarize_window(
    values: dict[str, dict[str, np.ndarray]], selection: slice
) -> dict[str, Any]:
    output = {}
    for name in (
        "continuous_actions",
        "conditional_adapter_location",
    ):
        hh = values["HH"][name][selection]
        hf = values["HF"][name][selection]
        fh = values["FH"][name][selection]
        ff = values["FF"][name][selection]
        components = {
            "router": rms(fh - hh),
            "expert": rms(hf - hh),
            "interaction": rms(ff - fh - hf + hh),
        }
        total = rms(ff - hh)
        output[name] = {
            "half_to_final_rms": total,
            "component_rms": components,
            "dominant_component": max(components, key=components.get),
            "FH_distance_to_final_rms": rms(fh - ff),
            "HF_distance_to_final_rms": rms(hf - ff),
        }
    for code in sorted(values):
        weights = values[code]["soft_negative_com_weight"][selection]
        output.setdefault("router_weight", {})[code] = {
            "min": float(np.min(weights)),
            "mean": float(np.mean(weights)),
            "max": float(np.max(weights)),
            "p95": float(np.percentile(weights, 95)),
        }
    return output


def finite(values: dict[str, dict[str, np.ndarray]]) -> bool:
    return all(
        np.all(np.isfinite(array))
        for by_name in values.values()
        for array in by_name.values()
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--read-only-authorized", action="store_true")
    args = parser.parse_args()
    if not args.read_only_authorized:
        raise PermissionError("T124 requires --read-only-authorized")
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T124: {path}")
    if WORK.exists():
        raise FileExistsError(f"refusing to overwrite T124 work: {WORK}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T124 execution requires clean worktree")
    prereg = load()
    WORK.mkdir(parents=True)
    paths, graph_scope = build_variants(
        Path(prereg["graphs"]["half"]["path"]),
        Path(prereg["graphs"]["final"]["path"]),
    )
    sessions = {code: session(path) for code, path in paths.items()}
    populations = {}
    for name, item in prereg["traces"].items():
        trace_rows = rows(Path(item["path"]))
        outputs = evaluate(sessions, trace_rows)
        last = int(
            prereg["factorial"]["critical_window"]["last_ticks"]
        )
        populations[name] = {
            "rows": len(trace_rows),
            "all": summarize_window(outputs, slice(None)),
            "first_32": summarize_window(outputs, slice(0, 32)),
            "ticks_256_295": summarize_window(
                outputs, slice(256, min(296, len(trace_rows)))
            ),
            "last_40": summarize_window(outputs, slice(-last, None)),
            "all_outputs_finite": finite(outputs),
        }
    critical = populations["half_failed"]["last_40"][
        "continuous_actions"
    ]
    dominant = critical["dominant_component"]
    decision = prereg["decision_rule"][f"{dominant}_dominant"]
    checks = {
        "only_factorial_leaves_changed": graph_scope[
            "only_factorial_leaves_changed"
        ],
        "all_outputs_finite": all(
            item["all_outputs_finite"] for item in populations.values()
        ),
        "critical_component_nonzero": all(
            value > 0.0 for value in critical["component_rms"].values()
        ),
        "formal_behavior_cells_zero": True,
        "simulator_optimizer_colab_and_robot_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value: dict[str, Any] = {
        "schema_version": "open_duck.t124_t120_leaf_factorial_result.v1",
        "status": (
            "PASS_T124_T120_LEAF_FACTORIAL"
            if not failed
            else "HOLD_T124_T120_LEAF_FACTORIAL"
        ),
        "decision": decision if not failed else "HOLD_FOR_ATTRIBUTION_REPAIR",
        "classification": (
            f"{dominant.upper()}_DOMINANT"
            if not failed
            else "UNRESOLVED"
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "graph_scope": graph_scope,
        "variant_graphs": {
            code: receipt(path) for code, path in paths.items()
        },
        "populations": populations,
        "critical_window": critical,
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "trace_rows": sum(
                item["rows"] for item in populations.values()
            ),
            "formal_behavior_cells": 0,
            "simulator_steps": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "selected_cpu_screen_preregistration": not failed,
            "training": False,
            "colab": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["result_sha256"] = canonical_sha256(value, "result_sha256")
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T124 T120 leaf-factorial result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Classification: `{value['classification']}`\n"
        "- Critical-window action RMS components: "
        f"`{json.dumps(critical['component_rms'], sort_keys=True)}`\n"
        "- Simulator / optimizer / Colab / robot: `0 / 0 / 0 / 0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"classification={value['classification']}")
    print(f"decision={value['decision']}")
    print(f"critical={json.dumps(critical, sort_keys=True)}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
