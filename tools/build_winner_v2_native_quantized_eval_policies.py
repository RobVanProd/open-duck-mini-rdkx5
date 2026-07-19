#!/usr/bin/env python3
"""Build eval-only winner-v2 graphs with native RDK-X5 input quantization."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Iterable

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "artifacts/runtime_handoff/rdkx5_native_20260719"
POLICY_CONTRACT = HANDOFF / "policy_contract.json"
SOURCE_POLICIES = {
    512000: HANDOFF / "policies/T2_EQUAL_512000.onnx",
    1024000: HANDOFF / "policies/T2_EQUAL_1024000.onnx",
}
DEFAULT_OUTPUT = ROOT / "outputs/analysis/winner_v2_native_quantized_eval_policies"

SOFT_OFFSETS_RAD = np.asarray(
    [
        0.0844,
        0.0721,
        -0.0890,
        0.0371,
        -0.0767,
        0.0245,
        0.0,
        -0.0890,
        -0.0399,
        0.0951,
        -0.0476,
        0.0660,
        0.0798,
        0.1887,
    ],
    dtype=np.float32,
)
GYRO_LSB_RAD_S = np.float32(math.pi / (180.0 * 16.0))
ACCEL_LSB_M_S2 = np.float32(0.01)
POSITION_LSB_RAD = np.float32(2.0 * math.pi / 4096.0)
VELOCITY_OBS_LSB = np.float32((2.0 * math.pi / 4095.0) * 0.05)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def home_rad() -> np.ndarray:
    payload = json.loads(POLICY_CONTRACT.read_text())
    values = np.asarray(payload["action_contract"]["home_rad"], dtype=np.float32)
    if values.shape != (14,) or not np.all(np.isfinite(values)):
        raise ValueError("policy contract home_rad must be finite float32[14]")
    return values


def numpy_quantize_observation(obs: np.ndarray) -> np.ndarray:
    """Independent float32 expression mirrored by the ONNX quantizer prefix."""
    values = np.asarray(obs, dtype=np.float32)
    if values.shape[-1] != 115:
        raise ValueError("winner-v2 observation must end in 115 elements")
    result = values.copy()
    result[..., 0:3] = (
        np.round(values[..., 0:3] / GYRO_LSB_RAD_S) * GYRO_LSB_RAD_S
    ).astype(np.float32)
    result[..., 3:6] = (
        np.round(values[..., 3:6] / ACCEL_LSB_M_S2) * ACCEL_LSB_M_S2
    ).astype(np.float32)
    origin = (home_rad() + SOFT_OFFSETS_RAD + np.float32(math.pi)).astype(np.float32)
    result[..., 13:27] = (
        np.round((values[..., 13:27] + origin) / POSITION_LSB_RAD)
        * POSITION_LSB_RAD
        - origin
    ).astype(np.float32)
    result[..., 27:41] = (
        np.round(values[..., 27:41] / VELOCITY_OBS_LSB) * VELOCITY_OBS_LSB
    ).astype(np.float32)
    return result


def valid_binary_contacts(obs: np.ndarray) -> bool:
    values = np.asarray(obs, dtype=np.float32)
    if values.shape[-1] != 115 or not np.all(np.isfinite(values)):
        return False
    contacts = values[..., 97:99]
    return bool(np.all((contacts == np.float32(0.0)) | (contacts == np.float32(1.0))))


def _tensor(name: str, values: np.ndarray, *, data_type: int | None = None):
    import onnx
    from onnx import numpy_helper

    array = np.asarray(values)
    if data_type is not None:
        return onnx.helper.make_tensor(
            name,
            data_type,
            list(array.shape),
            array.reshape(-1).tolist(),
        )
    return numpy_helper.from_array(array, name=name)


def _slice_initializers(name: str, start: int, end: int) -> list:
    import onnx

    return [
        _tensor(f"native_quant_{name}_starts", np.asarray([start], dtype=np.int64)),
        _tensor(f"native_quant_{name}_ends", np.asarray([end], dtype=np.int64)),
        _tensor(f"native_quant_{name}_axes", np.asarray([1], dtype=np.int64)),
        _tensor(f"native_quant_{name}_steps", np.asarray([1], dtype=np.int64)),
    ]


def _slice_node(name: str, output: str):
    import onnx

    return onnx.helper.make_node(
        "Slice",
        [
            "obs",
            f"native_quant_{name}_starts",
            f"native_quant_{name}_ends",
            f"native_quant_{name}_axes",
            f"native_quant_{name}_steps",
        ],
        [output],
        name=f"native_quant_slice_{name}",
    )


def quantizer_graph_parts() -> tuple[list, list]:
    import onnx

    slices = {
        "gyro": (0, 3),
        "accel": (3, 6),
        "command": (6, 13),
        "position": (13, 27),
        "velocity": (27, 41),
        "tail": (41, 115),
    }
    initializers: list = []
    for name, (start, end) in slices.items():
        initializers.extend(_slice_initializers(name, start, end))
    origin = (home_rad() + SOFT_OFFSETS_RAD + np.float32(math.pi)).astype(np.float32)
    initializers.extend(
        [
            _tensor("native_quant_gyro_lsb", np.asarray([GYRO_LSB_RAD_S], dtype=np.float32)),
            _tensor("native_quant_accel_lsb", np.asarray([ACCEL_LSB_M_S2], dtype=np.float32)),
            _tensor("native_quant_position_lsb", np.asarray([POSITION_LSB_RAD], dtype=np.float32)),
            _tensor("native_quant_velocity_obs_lsb", np.asarray([VELOCITY_OBS_LSB], dtype=np.float32)),
            _tensor("native_quant_position_origin", origin.reshape(1, 14)),
        ]
    )

    nodes = [
        _slice_node("gyro", "native_quant_gyro_raw"),
        onnx.helper.make_node(
            "Div",
            ["native_quant_gyro_raw", "native_quant_gyro_lsb"],
            ["native_quant_gyro_units"],
            name="native_quant_gyro_div",
        ),
        onnx.helper.make_node(
            "Round",
            ["native_quant_gyro_units"],
            ["native_quant_gyro_rounded"],
            name="native_quant_gyro_round",
        ),
        onnx.helper.make_node(
            "Mul",
            ["native_quant_gyro_rounded", "native_quant_gyro_lsb"],
            ["native_quant_gyro"],
            name="native_quant_gyro_mul",
        ),
        _slice_node("accel", "native_quant_accel_raw"),
        onnx.helper.make_node(
            "Div",
            ["native_quant_accel_raw", "native_quant_accel_lsb"],
            ["native_quant_accel_units"],
            name="native_quant_accel_div",
        ),
        onnx.helper.make_node(
            "Round",
            ["native_quant_accel_units"],
            ["native_quant_accel_rounded"],
            name="native_quant_accel_round",
        ),
        onnx.helper.make_node(
            "Mul",
            ["native_quant_accel_rounded", "native_quant_accel_lsb"],
            ["native_quant_accel"],
            name="native_quant_accel_mul",
        ),
        _slice_node("command", "native_quant_command"),
        _slice_node("position", "native_quant_position_raw"),
        onnx.helper.make_node(
            "Add",
            ["native_quant_position_raw", "native_quant_position_origin"],
            ["native_quant_position_shifted"],
            name="native_quant_position_add_origin",
        ),
        onnx.helper.make_node(
            "Div",
            ["native_quant_position_shifted", "native_quant_position_lsb"],
            ["native_quant_position_units"],
            name="native_quant_position_div",
        ),
        onnx.helper.make_node(
            "Round",
            ["native_quant_position_units"],
            ["native_quant_position_rounded"],
            name="native_quant_position_round",
        ),
        onnx.helper.make_node(
            "Mul",
            ["native_quant_position_rounded", "native_quant_position_lsb"],
            ["native_quant_position_shifted_quantized"],
            name="native_quant_position_mul",
        ),
        onnx.helper.make_node(
            "Sub",
            ["native_quant_position_shifted_quantized", "native_quant_position_origin"],
            ["native_quant_position"],
            name="native_quant_position_sub_origin",
        ),
        _slice_node("velocity", "native_quant_velocity_raw"),
        onnx.helper.make_node(
            "Div",
            ["native_quant_velocity_raw", "native_quant_velocity_obs_lsb"],
            ["native_quant_velocity_units"],
            name="native_quant_velocity_div",
        ),
        onnx.helper.make_node(
            "Round",
            ["native_quant_velocity_units"],
            ["native_quant_velocity_rounded"],
            name="native_quant_velocity_round",
        ),
        onnx.helper.make_node(
            "Mul",
            ["native_quant_velocity_rounded", "native_quant_velocity_obs_lsb"],
            ["native_quant_velocity"],
            name="native_quant_velocity_mul",
        ),
        _slice_node("tail", "native_quant_tail"),
        onnx.helper.make_node(
            "Concat",
            [
                "native_quant_gyro",
                "native_quant_accel",
                "native_quant_command",
                "native_quant_position",
                "native_quant_velocity",
                "native_quant_tail",
            ],
            ["native_quantized_obs"],
            axis=1,
            name="native_quant_concat_obs",
        ),
    ]
    return nodes, initializers


def build_wrapper(source_path: Path, output_path: Path, *, enabled: bool = True) -> Path:
    """Write one wrapper; default-off is an exact byte copy for contract use."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not enabled:
        output_path.write_bytes(source_path.read_bytes())
        return output_path

    import onnx

    source = onnx.load(source_path)
    model = copy.deepcopy(source)
    prefix_nodes, prefix_initializers = quantizer_graph_parts()
    for node in model.graph.node:
        for index, value in enumerate(node.input):
            if value == "obs":
                node.input[index] = "native_quantized_obs"
    original_nodes = list(model.graph.node)
    del model.graph.node[:]
    model.graph.node.extend([*prefix_nodes, *original_nodes])
    model.graph.initializer.extend(prefix_initializers)
    metadata = {item.key: item.value for item in model.metadata_props}
    metadata.update(
        {
            "eval_only_native_quantized": "true",
            "native_quantizer_schema": "winner_v2.native_input_quantizer.v1",
            "native_quantizer_source_sha256": sha256(source_path),
        }
    )
    del model.metadata_props[:]
    for key, value in sorted(metadata.items()):
        item = model.metadata_props.add()
        item.key = key
        item.value = value
    onnx.checker.check_model(model)
    onnx.save(model, output_path)
    return output_path


def build_all(output_dir: Path = DEFAULT_OUTPUT) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for step, source in SOURCE_POLICIES.items():
        output = output_dir / f"T2_EQUAL_{step}_native_quantized_eval.onnx"
        build_wrapper(source, output)
        rows.append(
            {
                "step": step,
                "source": str(source.relative_to(ROOT)),
                "source_sha256": sha256(source),
                "wrapper": str(output.relative_to(ROOT)),
                "wrapper_sha256": sha256(output),
                "bytes": output.stat().st_size,
            }
        )
    manifest = {
        "schema_version": "winner_v2.native_quantized_eval_policy_manifest.v1",
        "eval_only": True,
        "policies": rows,
        "constants": {
            "gyro_lsb_rad_s": float(GYRO_LSB_RAD_S),
            "acceleration_lsb_m_s2": float(ACCEL_LSB_M_S2),
            "position_lsb_rad": float(POSITION_LSB_RAD),
            "velocity_observation_lsb": float(VELOCITY_OBS_LSB),
            "soft_offsets_rad": SOFT_OFFSETS_RAD.astype(float).tolist(),
            "home_rad": home_rad().astype(float).tolist(),
        },
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    manifest = build_all(args.output_dir.resolve())
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
