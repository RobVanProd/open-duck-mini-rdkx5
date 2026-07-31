#!/usr/bin/env python3
"""Run the zero-behavior winner-v8 physical-envelope interaction contract."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""

import numpy as np
import onnx
from onnx import TensorProto, numpy_helper
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "winner_v8_physical_envelope_contract_preregistration.json"
MARGIN = np.float32(4.0) * np.finfo(np.float32).eps


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def initializers(model: onnx.ModelProto) -> dict[str, np.ndarray]:
    return {item.name: np.asarray(numpy_helper.to_array(item)) for item in model.graph.initializer}


def abi(model: onnx.ModelProto) -> dict[str, list[dict[str, Any]]]:
    def describe(values: Any) -> list[dict[str, Any]]:
        rows = []
        for value in values:
            tensor = value.type.tensor_type
            rows.append({
                "name": value.name,
                "dtype": "float32" if tensor.elem_type == TensorProto.FLOAT else TensorProto.DataType.Name(tensor.elem_type).lower(),
                "shape": [dimension.dim_value for dimension in tensor.shape.dim],
            })
        return rows
    return {"inputs": describe(model.graph.input), "outputs": describe(model.graph.output)}


def replace_initializer(model: onnx.ModelProto, name: str, value: np.ndarray) -> None:
    for item in model.graph.initializer:
        if item.name == name:
            item.CopyFrom(numpy_helper.from_array(value.astype(np.float32), name=name))
            return
    raise KeyError(name)


def transform_graph(source: onnx.ModelProto, full_delta: np.ndarray) -> onnx.ModelProto:
    model = copy.deepcopy(source)
    replace_initializer(model, "max_action_delta", full_delta)
    replace_initializer(model, "v7_safe_max_action_delta", full_delta - MARGIN)
    model.graph.name = "winner_v8_full_measured_vector_physical_envelope"
    model.producer_name = "open-duck-winner-v8"
    model.ir_version = min(model.ir_version, 10)
    onnx.checker.check_model(model)
    return model


def graph_change(source: onnx.ModelProto, output: onnx.ModelProto, full_delta: np.ndarray) -> dict[str, Any]:
    source_inits = initializers(source)
    output_inits = initializers(output)
    changed = sorted(
        name for name in source_inits
        if not np.array_equal(source_inits[name], output_inits[name])
    )
    nodes_exact = [node.SerializeToString() for node in source.graph.node] == [
        node.SerializeToString() for node in output.graph.node
    ]
    unchanged_initializers_exact = all(
        np.array_equal(value, output_inits[name])
        for name, value in source_inits.items()
        if name not in changed
    )
    return {
        "changed_initializers": changed,
        "nodes_exact": nodes_exact,
        "unchanged_initializers_exact": unchanged_initializers_exact,
        "abi_exact": abi(source) == abi(output),
        "max_action_delta_exact": np.array_equal(output_inits["max_action_delta"], full_delta),
        "safe_delta_exact": np.array_equal(output_inits["v7_safe_max_action_delta"], full_delta - MARGIN),
    }


def random_observation(rng: np.random.Generator, command_x: float) -> np.ndarray:
    obs = rng.normal(0.0, 0.25, (1, 115)).astype(np.float32)
    obs[:, 6] = np.float32(command_x)
    obs[:, 97:99] = 1.0
    return obs


def stress(session: ort.InferenceSession, safe_delta: np.ndarray, seed: int, cases: int) -> dict[str, Any]:
    rng = np.random.Generator(np.random.PCG64(seed))
    maximum_excess = 0.0
    finite = True
    state_exact = True
    for _ in range(cases):
        obs = random_observation(rng, 0.077)
        previous = rng.uniform(-1.0, 1.0, (1, 14)).astype(np.float32)
        action, state = session.run(
            ["continuous_actions", "previous_action_out"],
            {"obs": obs, "previous_action": previous},
        )
        excess = np.maximum(np.abs(action - previous) - safe_delta, 0.0)
        maximum_excess = max(maximum_excess, float(np.max(excess)))
        finite &= bool(np.isfinite(action).all() and np.isfinite(state).all())
        state_exact &= np.array_equal(action, state)
    return {
        "seed": seed,
        "cases": cases,
        "all_finite": finite,
        "state_equals_action_bit_exact": state_exact,
        "maximum_safe_delta_excess": maximum_excess,
        "strictly_bounded": maximum_excess == 0.0,
    }


def chain(
    session: ort.InferenceSession,
    inits: dict[str, np.ndarray],
    safe_delta: np.ndarray,
    seed: int,
    command_x: float,
    ticks: int,
) -> dict[str, Any]:
    rng = np.random.Generator(np.random.PCG64(seed))
    previous = np.zeros((1, 14), dtype=np.float32)
    history = [previous.copy(), previous.copy(), previous.copy()]
    home = inits["guard_home"].astype(np.float32)
    maximum_excess = 0.0
    finite = True
    zero_exact = True
    changed_ticks = 0
    for tick in range(ticks):
        obs = random_observation(rng, command_x)
        phase = np.float32((2.0 * np.pi * tick) / 27.0)
        obs[:, 13:27] = previous * np.float32(0.25)
        obs[:, 27:41] = 0.0
        obs[:, 41:55] = history[0]
        obs[:, 55:69] = history[1]
        obs[:, 69:83] = history[2]
        obs[:, 83:97] = home + previous * np.float32(0.25)
        obs[:, 99:101] = [np.cos(phase), np.sin(phase)]
        action, state = session.run(
            ["continuous_actions", "previous_action_out"],
            {"obs": obs, "previous_action": previous},
        )
        excess = np.maximum(np.abs(action - previous) - safe_delta, 0.0)
        maximum_excess = max(maximum_excess, float(np.max(excess)))
        finite &= bool(np.isfinite(action).all() and np.isfinite(state).all())
        changed_ticks += not np.array_equal(action, previous)
        if command_x == 0.0:
            zero_exact &= bool(
                np.array_equal(action, np.zeros_like(action))
                and np.array_equal(state, np.zeros_like(state))
            )
        history = [state.copy(), history[0], history[1]]
        previous = state
    return {
        "seed": seed,
        "command_x": command_x,
        "ticks": ticks,
        "all_finite": finite,
        "zero_action_and_state_exact": zero_exact,
        "changed_ticks": changed_ticks,
        "maximum_safe_delta_excess": maximum_excess,
        "strictly_bounded": maximum_excess == 0.0,
    }


def transform_xml(source_model: Path, source_scene: Path, output_root: Path, force_limit_nm: float) -> dict[str, Any]:
    output_root.mkdir(parents=True)
    output_model = output_root / source_model.name
    output_scene = output_root / source_scene.name
    source_text = source_model.read_text(encoding="utf-8")
    old = 'forcerange="-3.23 3.23"'
    new = f'forcerange="-{force_limit_nm:.8f} {force_limit_nm:.8f}"'
    if source_text.count(old) != 1:
        raise ValueError("source XML does not contain exactly one active 3.23 N.m range")
    output_model.write_text(source_text.replace(old, new), encoding="utf-8")
    shutil.copyfile(source_scene, output_scene)
    root = ET.parse(output_model).getroot()
    defaults = [
        position
        for default in root.findall(".//default")
        if default.attrib.get("class") == "sts3215"
        for position in default.findall("position")
    ]
    actuators = list(root.find("actuator").findall("position"))
    force_range = [float(value) for value in defaults[0].attrib["forcerange"].split()]
    include = ET.parse(output_scene).getroot().find("include")
    return {
        "source_model_sha256": sha256(source_model),
        "source_scene_sha256": sha256(source_scene),
        "output_model_path": str(output_model),
        "output_model_sha256": sha256(output_model),
        "output_scene_path": str(output_scene),
        "output_scene_sha256": sha256(output_scene),
        "only_active_range_text_changed": output_model.read_text(encoding="utf-8").replace(new, old) == source_text,
        "sts3215_default_count": len(defaults),
        "actuator_count": len(actuators),
        "all_actuators_inherit_sts3215": all(item.attrib.get("class") == "sts3215" for item in actuators),
        "force_range_nm": force_range,
        "scene_include_exact": include is not None and include.attrib.get("file") == source_model.name,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-half", type=Path, required=True)
    parser.add_argument("--source-final", type=Path, required=True)
    parser.add_argument("--model-xml", type=Path, required=True)
    parser.add_argument("--scene-xml", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    work_root = args.work_root.resolve()
    output = args.output.resolve()
    if work_root.exists() or output.exists():
        raise FileExistsError("winner-v8 physical-envelope output already exists")
    work_root.mkdir(parents=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    expected = prereg["frozen_inputs"]
    observed = {
        "runner_sha256": sha256(Path(__file__)),
        "source_half_sha256": sha256(args.source_half),
        "source_final_sha256": sha256(args.source_final),
        "model_xml_sha256": sha256(args.model_xml),
        "scene_xml_sha256": sha256(args.scene_xml),
    }
    for name in ("force_attribution", "full_vector_attribution", "current_contract", "measured_envelope"):
        path = ROOT / expected[name]["path"]
        observed[f"{name}_sha256"] = sha256(path)
    expected_flat = {
        "runner_sha256": expected["runner_sha256"],
        "source_half_sha256": expected["source_half"]["sha256"],
        "source_final_sha256": expected["source_final"]["sha256"],
        "model_xml_sha256": expected["model_xml_sha256"],
        "scene_xml_sha256": expected["scene_xml_sha256"],
        **{f"{name}_sha256": expected[name]["sha256"] for name in ("force_attribution", "full_vector_attribution", "current_contract", "measured_envelope")},
    }
    if observed != expected_flat:
        raise ValueError("winner-v8 frozen input mismatch")

    rate_vector = np.asarray(prereg["transform"]["full_measured_rate_limits_rad_s"], dtype=np.float32)
    full_delta = rate_vector * np.float32(0.02 / 0.25)
    safe_delta = full_delta - MARGIN
    policy_rows = []
    for index, (label, path) in enumerate(
        (("half", args.source_half), ("final", args.source_final))
    ):
        source_model = onnx.load(path)
        transformed = transform_graph(source_model, full_delta.reshape(1, 14))
        output_path = work_root / f"winner_v8_{label}_physical_envelope.onnx"
        onnx.save(transformed, output_path)
        session = ort.InferenceSession(str(output_path), providers=["CPUExecutionProvider"])
        output_inits = initializers(transformed)
        policy_rows.append({
            "label": label,
            "source_path": str(path),
            "source_sha256": sha256(path),
            "output_path": str(output_path),
            "output_sha256": sha256(output_path),
            "output_bytes": output_path.stat().st_size,
            "abi": abi(transformed),
            "graph_change": graph_change(source_model, transformed, full_delta.reshape(1, 14)),
            "stress": stress(session, safe_delta.reshape(1, 14), 80770 + index, 4096),
            "x0_chain": chain(session, output_inits, safe_delta.reshape(1, 14), 80780 + index, 0.0, 256),
            "moving_chain": chain(session, output_inits, safe_delta.reshape(1, 14), 80740 + index, 0.077, 256),
        })
    xml = transform_xml(args.model_xml, args.scene_xml, work_root / "xmls", float(prereg["transform"]["physical_force_limit_nm"]))
    expected_abi = prereg["expected_abi"]
    checks = {
        "frozen_inputs_exact": observed == expected_flat,
        "both_abis_exact": all(row["abi"] == expected_abi for row in policy_rows),
        "only_two_rate_initializers_changed": all(
            row["graph_change"]["changed_initializers"] == ["max_action_delta", "v7_safe_max_action_delta"]
            and row["graph_change"]["nodes_exact"]
            and row["graph_change"]["unchanged_initializers_exact"]
            and row["graph_change"]["abi_exact"]
            and row["graph_change"]["max_action_delta_exact"]
            and row["graph_change"]["safe_delta_exact"]
            for row in policy_rows
        ),
        "all_8192_stress_cases_strictly_bounded": all(row["stress"]["strictly_bounded"] and row["stress"]["state_equals_action_bit_exact"] for row in policy_rows),
        "both_256_tick_x0_chains_exact_zero": all(row["x0_chain"]["zero_action_and_state_exact"] and row["x0_chain"]["strictly_bounded"] for row in policy_rows),
        "both_256_tick_moving_chains_strictly_bounded": all(row["moving_chain"]["strictly_bounded"] and row["moving_chain"]["all_finite"] for row in policy_rows),
        "xml_only_force_range_changed": xml["only_active_range_text_changed"] and xml["output_scene_sha256"] == xml["source_scene_sha256"],
        "all_14_actuators_inherit_physical_force_limit": xml["sts3215_default_count"] == 1 and xml["actuator_count"] == 14 and xml["all_actuators_inherit_sts3215"] and xml["force_range_nm"] == [-float(prereg["transform"]["physical_force_limit_nm"]), float(prereg["transform"]["physical_force_limit_nm"])] and xml["scene_include_exact"],
        "cpu_only_no_behavior_or_training": True,
    }
    failed = [name for name, passed in checks.items() if not passed]
    status = "PASS_WINNER_V8_PHYSICAL_ENVELOPE_CONTRACT" if not failed else "HOLD_WINNER_V8_PHYSICAL_ENVELOPE_CONTRACT"
    payload = {
        "schema_version": "open_duck_mini.winner_v8_physical_envelope_contract_result.v1",
        "status": status,
        "decision": "AUTHORIZE_SEPARATE_WINNER_V8_NOMINAL_PREREGISTRATION_ONLY" if not failed else "CLOSE_WINNER_V8_PHYSICAL_ENVELOPE_INTERACTION_ROUTE",
        "preregistration_sha256": sha256(PREREG),
        "checks": checks,
        "failed_checks": failed,
        "observed_input_hashes": observed,
        "rate_limits_rad_s": rate_vector.tolist(),
        "max_action_delta": full_delta.tolist(),
        "safe_max_action_delta": safe_delta.tolist(),
        "policies": policy_rows,
        "xml": xml,
        "authority": {"behavior_training_gpu_colab": False, "runtime_robot_torque_motion_gate5": False, "robot_clearance": False},
    }
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(status)
    print(f"RESULT={output}")
    print(f"RESULT_SHA256={sha256(output)}")
    return 0 if not failed else 2


if __name__ == "__main__":
    raise SystemExit(main())
