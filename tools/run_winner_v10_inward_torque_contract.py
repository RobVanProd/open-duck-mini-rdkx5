#!/usr/bin/env python3
"""Run the frozen zero-behavior winner-v10 torque-representation contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
from typing import Any
import xml.etree.ElementTree as ET

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""

import numpy as np
import onnx
import onnxruntime as ort
from onnx import numpy_helper


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "winner_v10_inward_torque_contract_preregistration.json"
IMPORTER = ROOT / "tools" / "import_winner_v10_inward_torque_contract.py"
BUILDER = ROOT / "tools" / "build_winner_v10_inward_torque_preregistration.py"
ATTRIBUTION = ANALYSIS / "winner_v9_numeric_torque_hold_attribution.json"
V9_RESULT = ANALYSIS / "winner_v9_nominal_behavior_result.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def abi(model: onnx.ModelProto) -> dict[str, Any]:
    def describe(values: Any) -> list[dict[str, Any]]:
        rows = []
        for value in values:
            tensor = value.type.tensor_type
            rows.append(
                {
                    "name": value.name,
                    "dtype": onnx.TensorProto.DataType.Name(tensor.elem_type).lower(),
                    "shape": [dim.dim_value for dim in tensor.shape.dim],
                }
            )
        return rows

    return {"inputs": describe(model.graph.input), "outputs": describe(model.graph.output)}


def initializers(model: onnx.ModelProto) -> dict[str, np.ndarray]:
    return {item.name: numpy_helper.to_array(item) for item in model.graph.initializer}


def inference_contract(path: Path, seed: int) -> dict[str, Any]:
    model = onnx.load(path)
    session = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
    inits = initializers(model)
    stored_delta = inits["max_action_delta"].astype(np.float32)
    rng = np.random.default_rng(seed)
    maximum_excess = 0.0
    finite = True
    state_exact = True
    for _ in range(256):
        obs = rng.normal(0.0, 1.0, size=(1, 115)).astype(np.float32)
        previous = rng.uniform(-0.75, 0.75, size=(1, 14)).astype(np.float32)
        action, state = session.run(
            ["continuous_actions", "previous_action_out"],
            {"obs": obs, "previous_action": previous},
        )
        finite = finite and bool(np.all(np.isfinite(action))) and bool(
            np.all(np.isfinite(state))
        )
        state_exact = state_exact and np.array_equal(action, state)
        maximum_excess = max(
            maximum_excess,
            float(np.max(np.maximum(np.abs(action - previous) - stored_delta, 0.0))),
        )
    return {
        "abi": abi(model),
        "all_finite": finite,
        "state_equals_action_bit_exact": state_exact,
        "maximum_stored_delta_excess": maximum_excess,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-half", type=Path, required=True)
    parser.add_argument("--source-final", type=Path, required=True)
    parser.add_argument("--source-model-xml", type=Path, required=True)
    parser.add_argument("--source-scene-xml", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source_policies = {
        "half": args.source_half.resolve(),
        "final": args.source_final.resolve(),
    }
    source_model = args.source_model_xml.resolve()
    source_scene = args.source_scene_xml.resolve()
    work_root = args.work_root.resolve()
    output = args.output.resolve()
    if work_root.exists() or output.exists():
        raise FileExistsError("winner-v10 output already exists")
    work_root.mkdir(parents=True)
    output.parent.mkdir(parents=True, exist_ok=True)

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    observed = {
        "runner": sha256(Path(__file__)),
        "importer": sha256(IMPORTER),
        "builder": sha256(BUILDER),
        "numeric_attribution": sha256(ATTRIBUTION),
        "winner_v9_result": sha256(V9_RESULT),
        "source_half": sha256(source_policies["half"]),
        "source_final": sha256(source_policies["final"]),
        "source_model_xml": sha256(source_model),
        "source_scene_xml": sha256(source_scene),
    }
    if observed != prereg["input_hashes"]:
        raise ValueError("winner-v10 frozen input hash mismatch")

    policies = []
    for index, (label, source) in enumerate(source_policies.items()):
        destination = work_root / f"winner_v10_{label}_inward_torque.onnx"
        shutil.copyfile(source, destination)
        row = {
            "label": label,
            "source_path": str(source),
            "source_sha256": sha256(source),
            "output_path": str(destination),
            "output_sha256": sha256(destination),
            "output_bytes": destination.stat().st_size,
            **inference_contract(destination, 110010 + index),
        }
        row["byte_identical_to_source"] = row["source_sha256"] == row["output_sha256"]
        policies.append(row)

    xml_root = work_root / "xmls"
    xml_root.mkdir()
    output_model = xml_root / source_model.name
    output_scene = xml_root / source_scene.name
    old = prereg["transform"]["source_force_range_xml"].encode("utf-8")
    new = prereg["transform"]["output_force_range_xml"].encode("utf-8")
    source_bytes = source_model.read_bytes()
    if source_bytes.count(old) != 1:
        raise ValueError("source XML does not contain exactly one frozen force range")
    output_model.write_bytes(source_bytes.replace(old, new))
    shutil.copyfile(source_scene, output_scene)
    root = ET.parse(output_model).getroot()
    defaults = [
        position
        for default in root.findall(".//default")
        if default.attrib.get("class") == "sts3215"
        for position in default.findall("position")
    ]
    actuators = list(root.find("actuator").findall("position"))
    force_range = [float(item) for item in defaults[0].attrib["forcerange"].split()]
    represented_positive = float(np.float32(force_range[1]))
    xml = {
        "source_model_path": str(source_model),
        "source_model_sha256": sha256(source_model),
        "output_model_path": str(output_model),
        "output_model_sha256": sha256(output_model),
        "source_scene_path": str(source_scene),
        "source_scene_sha256": sha256(source_scene),
        "output_scene_path": str(output_scene),
        "output_scene_sha256": sha256(output_scene),
        "only_exact_force_range_bytes_changed": output_model.read_bytes().replace(
            new, old
        )
        == source_bytes,
        "sts3215_default_count": len(defaults),
        "actuator_count": len(actuators),
        "all_actuators_inherit_sts3215": all(
            actuator.attrib.get("class") == "sts3215" for actuator in actuators
        ),
        "force_range_nm": force_range,
        "represented_positive_float32_nm": represented_positive,
    }

    checks = {
        "frozen_input_hashes_exact": observed == prereg["input_hashes"],
        "both_policy_graphs_byte_identical": all(
            row["byte_identical_to_source"] for row in policies
        ),
        "both_115d_stateful_abis_exact": all(
            row["abi"] == prereg["expected_abi"] for row in policies
        ),
        "both_cpu_inference_contracts_pass": all(
            row["all_finite"]
            and row["state_equals_action_bit_exact"]
            and row["maximum_stored_delta_excess"] == 0.0
            for row in policies
        ),
        "xml_only_one_force_range_changed": xml[
            "only_exact_force_range_bytes_changed"
        ],
        "all_14_actuators_inherit_inward_limit": xml["sts3215_default_count"] == 1
        and xml["actuator_count"] == 14
        and xml["all_actuators_inherit_sts3215"],
        "inward_float32_boundary_exact": represented_positive
        == prereg["transform"]["inward_float32_torque_nm"]
        and represented_positive < prereg["transform"]["frozen_decimal_torque_gate_nm"],
        "scene_bytes_exact": xml["output_scene_sha256"]
        == xml["source_scene_sha256"],
        "cpu_only_no_behavior_or_training": ort.get_available_providers()
        and os.environ["CUDA_VISIBLE_DEVICES"] == ""
        and os.environ["HIP_VISIBLE_DEVICES"] == "",
    }
    failed = [name for name, passed in checks.items() if not passed]
    status = (
        "PASS_WINNER_V10_INWARD_TORQUE_REPRESENTATION_CONTRACT"
        if not failed
        else "HOLD_WINNER_V10_INWARD_TORQUE_REPRESENTATION_CONTRACT"
    )
    payload = {
        "schema_version": "open_duck_mini.winner_v10_inward_torque_contract_result.v1",
        "status": status,
        "decision": "AUTHORIZE_SEPARATE_WINNER_V10_NOMINAL_PREREGISTRATION_ONLY"
        if not failed
        else "CLOSE_WINNER_V10_INWARD_TORQUE_ROUTE",
        "preregistration_sha256": sha256(PREREG),
        "checks": checks,
        "failed_checks": failed,
        "input_hashes": observed,
        "policies": policies,
        "xml": xml,
        "authority": {
            "nominal_preregistration_design": not failed,
            "behavior_training_gpu_colab": False,
            "runtime_robot_torque_motion_gate5": False,
            "robot_clearance": False,
        },
    }
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(status)
    print(f"RESULT={output}")
    print(f"RESULT_SHA256={sha256(output)}")
    return 0 if not failed else 2


if __name__ == "__main__":
    raise SystemExit(main())
