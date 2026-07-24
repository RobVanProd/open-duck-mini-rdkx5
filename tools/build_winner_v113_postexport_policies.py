#!/usr/bin/env python3
"""Apply the frozen G3 guard and x=0 deadband to V112 exports."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
from typing import Any

import numpy as np
import onnx
from onnx import numpy_helper
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from build_ground_up_actual_centered_guard_screen import (  # noqa: E402
    append_guard,
)
from build_ground_up_command_deadband_repair import (  # noqa: E402
    wrap as append_deadband,
)


ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v113_postexport_transform_preregistration.json"
GUARD_PREREG = (
    ANALYSIS / "ground_up_actual_centered_guard_screen_preregistration.json"
)
DEADBAND_PREREG = (
    ANALYSIS / "ground_up_command_deadband_repair_preregistration.json"
)
CONTRACT = ANALYSIS / "winner_v113_postexport_transform_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V113_POSTEXPORT_TRANSFORM_CONTRACT_20260724.md"
CONSERVATIVE_LIMITS_RAD_S = np.asarray(
    [1.0, 0.75, 1.5, 1.5, 1.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.75, 1.25, 1.0, 1.25],
    dtype=np.float32,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def tensor_shape(value: Any) -> list[int]:
    return [int(dim.dim_value) for dim in value.type.tensor_type.shape.dim]


def graph_io(model: onnx.ModelProto) -> dict[str, dict[str, list[int]]]:
    return {
        "inputs": {item.name: tensor_shape(item) for item in model.graph.input},
        "outputs": {
            item.name: tensor_shape(item) for item in model.graph.output
        },
    }


def initializers(model: onnx.ModelProto) -> dict[str, np.ndarray]:
    return {
        item.name: np.asarray(numpy_helper.to_array(item))
        for item in model.graph.initializer
    }


def normalize_source_node(node: onnx.NodeProto) -> bytes:
    item = copy.deepcopy(node)
    for index, value in enumerate(item.input):
        if value == "continuous_actions":
            item.input[index] = "velocity_bounded_actions"
    for index, value in enumerate(item.output):
        if value == "continuous_actions":
            item.output[index] = "velocity_bounded_actions"
        elif value == "previous_action_out":
            item.output[index] = "velocity_bounded_previous_action_out"
    return item.SerializeToString()


def source_prefix_exact(
    source: onnx.ModelProto, transformed: onnx.ModelProto
) -> bool:
    return [normalize_source_node(node) for node in source.graph.node] == [
        node.SerializeToString()
        for node in transformed.graph.node[: len(source.graph.node)]
    ]


def inference_contract(
    source_path: Path,
    guarded_path: Path,
    final_path: Path,
    *,
    home: np.ndarray,
    pitch_indices: np.ndarray,
    command_index: int,
    deadband: float,
    margin: float,
) -> dict[str, Any]:
    source = ort.InferenceSession(
        str(source_path), providers=["CPUExecutionProvider"]
    )
    guarded = ort.InferenceSession(
        str(guarded_path), providers=["CPUExecutionProvider"]
    )
    final = ort.InferenceSession(
        str(final_path), providers=["CPUExecutionProvider"]
    )
    rng = np.random.default_rng(20260724)
    max_positive_action_error = 0.0
    max_positive_previous_error = 0.0
    max_positive_hidden_error = 0.0
    max_zero_action = 0.0
    max_zero_previous = 0.0
    max_zero_hidden_error = 0.0
    max_guard_excess = 0.0
    all_finite = True
    for command_x in (0.0, 0.074, 0.077, 0.080):
        previous = np.zeros((1, 14), dtype=np.float32)
        hidden = np.zeros((1, 64), dtype=np.float32)
        actual_offset = np.zeros((1, 14), dtype=np.float32)
        for _ in range(64):
            obs = rng.normal(0.0, 0.25, (1, 115)).astype(np.float32)
            obs[:, command_index] = np.float32(command_x)
            obs[:, 13:27] = actual_offset
            feed = {
                "obs": obs,
                "previous_action": previous,
                "h_in": hidden,
            }
            source_values = source.run(None, feed)
            guard_values = guarded.run(None, feed)
            final_values = final.run(None, feed)
            all_finite &= all(
                np.isfinite(value).all()
                for value in (*source_values, *guard_values, *final_values)
            )
            action, previous_out, hidden_out = final_values
            if command_x == 0.0:
                max_zero_action = max(
                    max_zero_action, float(np.max(np.abs(action)))
                )
                max_zero_previous = max(
                    max_zero_previous,
                    float(np.max(np.abs(previous_out))),
                )
                max_zero_hidden_error = max(
                    max_zero_hidden_error,
                    float(np.max(np.abs(hidden_out - guard_values[2]))),
                )
            else:
                max_positive_action_error = max(
                    max_positive_action_error,
                    float(np.max(np.abs(action - guard_values[0]))),
                )
                max_positive_previous_error = max(
                    max_positive_previous_error,
                    float(np.max(np.abs(previous_out - guard_values[1]))),
                )
                max_positive_hidden_error = max(
                    max_positive_hidden_error,
                    float(np.max(np.abs(hidden_out - guard_values[2]))),
                )
                sent = home[None] + action * np.float32(0.25)
                actual = home[None] + actual_offset
                max_guard_excess = max(
                    max_guard_excess,
                    float(
                        np.max(
                            np.abs(
                                sent[:, pitch_indices]
                                - actual[:, pitch_indices]
                            )
                            - margin
                        )
                    ),
                )
                actual_offset += np.clip(
                    action * np.float32(0.25) - actual_offset, -0.04, 0.04
                )
            previous = previous_out.astype(np.float32)
            hidden = hidden_out.astype(np.float32)
    checks = {
        "cpu_provider_exact": final.get_providers()
        == ["CPUExecutionProvider"],
        "all_outputs_finite": bool(all_finite),
        "positive_action_bit_exact_to_guarded": (
            max_positive_action_error == 0.0
        ),
        "positive_previous_bit_exact_to_guarded": (
            max_positive_previous_error == 0.0
        ),
        "positive_hidden_bit_exact_to_guarded": (
            max_positive_hidden_error == 0.0
        ),
        "zero_action_exact": max_zero_action == 0.0,
        "zero_previous_exact": max_zero_previous == 0.0,
        "zero_hidden_preserved": max_zero_hidden_error == 0.0,
        "g3_guard_enforced": max_guard_excess <= 2.0e-7,
    }
    return {
        "checks": checks,
        "pass": all(checks.values()),
        "max_positive_action_error": max_positive_action_error,
        "max_positive_previous_error": max_positive_previous_error,
        "max_positive_hidden_error": max_positive_hidden_error,
        "max_zero_action": max_zero_action,
        "max_zero_previous": max_zero_previous,
        "max_zero_hidden_error": max_zero_hidden_error,
        "max_guard_excess_rad": max_guard_excess,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    for path in (args.output_root, CONTRACT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V113: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    guard_prereg = json.loads(GUARD_PREREG.read_text(encoding="utf-8"))
    deadband_prereg = json.loads(
        DEADBAND_PREREG.read_text(encoding="utf-8")
    )
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V113_POSTEXPORT_TRANSFORM"
        or prereg.get("failed_checks") != []
        or sha256(Path(__file__).resolve())
        != prereg["input_hashes"]["transform_tool"]
    ):
        raise ValueError("V113 transform preregistration changed")
    guard = guard_prereg["guard_contract"]
    selected = next(
        row
        for row in guard_prereg["arms"]
        if row["name"] == "G3_FULL_TICK_BUFFER"
    )
    home = np.asarray(guard["home_target_rad"], dtype=np.float32)
    obs_indices = np.asarray(
        guard["measured_joint_offset_indices"], dtype=np.int64
    )
    pitch_indices = np.asarray(
        guard["pitch_chain_action_indices"], dtype=np.int64
    )
    margin = float(selected["margin_rad"])
    command_index = int(
        deadband_prereg["transform"]["command_x_observation_index"]
    )
    deadband = float(
        deadband_prereg["transform"][
            "zero_deadband_absolute_command_x"
        ]
    )
    expected_delta = CONSERVATIVE_LIMITS_RAD_S * np.float32(
        guard["control_dt_s"] / guard["action_scale_rad"]
    )
    args.output_root.mkdir(parents=True)
    rows = []
    for spec in prereg["sources"]:
        source_path = args.source_root.resolve() / spec["filename"]
        if sha256(source_path) != spec["sha256"]:
            raise ValueError(f"raw source changed: {spec['id']}")
        source = onnx.load(source_path)
        source_initializers = initializers(source)
        guarded = append_guard(
            source,
            obs_indices=obs_indices,
            pitch_indices=pitch_indices,
            home=home,
            action_scale=float(guard["action_scale_rad"]),
            margin=margin,
        )
        final = append_deadband(
            guarded, command_index=command_index, deadband=deadband
        )
        output_path = args.output_root.resolve() / spec["output_filename"]
        onnx.checker.check_model(final)
        onnx.save(final, output_path)
        final_initializers = initializers(final)
        with tempfile.TemporaryDirectory(prefix="winner_v113_") as temporary:
            guarded_path = Path(temporary) / "guarded.onnx"
            onnx.save(guarded, guarded_path)
            inference = inference_contract(
                source_path,
                guarded_path,
                output_path,
                home=home,
                pitch_indices=pitch_indices,
                command_index=command_index,
                deadband=deadband,
                margin=margin,
            )
        rows.append(
            {
                "id": spec["id"],
                "step": spec["step"],
                "source_sha256": sha256(source_path),
                "output_path": str(output_path),
                "output_sha256": sha256(output_path),
                "output_bytes": output_path.stat().st_size,
                "source_nodes_preserved": source_prefix_exact(source, final),
                "source_initializers_preserved": all(
                    name in final_initializers
                    and np.array_equal(value, final_initializers[name])
                    for name, value in source_initializers.items()
                ),
                "source_rate_projection_exact": bool(
                    "max_action_delta" in source_initializers
                    and np.array_equal(
                        source_initializers["max_action_delta"],
                        expected_delta[None],
                    )
                ),
                "guard_nodes_added": len(guarded.graph.node)
                - len(source.graph.node),
                "deadband_nodes_added": len(final.graph.node)
                - len(guarded.graph.node),
                "graph_io": graph_io(final),
                "inference": inference,
            }
        )
    expected_io = {
        "inputs": {
            "obs": [1, 115],
            "previous_action": [1, 14],
            "h_in": [1, 64],
        },
        "outputs": {
            "continuous_actions": [1, 14],
            "previous_action_out": [1, 14],
            "h_out": [1, 64],
        },
    }
    checks = {
        "two_postupdate_sources_transformed": len(rows) == 2,
        "all_source_hashes_exact": all(
            row["source_sha256"] == spec["sha256"]
            for row, spec in zip(rows, prereg["sources"], strict=True)
        ),
        "all_source_nodes_preserved": all(
            row["source_nodes_preserved"] for row in rows
        ),
        "all_source_initializers_preserved": all(
            row["source_initializers_preserved"] for row in rows
        ),
        "all_source_rate_projections_exact": all(
            row["source_rate_projection_exact"] for row in rows
        ),
        "all_append_exactly_13_guard_and_5_deadband_nodes": all(
            row["guard_nodes_added"] == 13
            and row["deadband_nodes_added"] == 5
            for row in rows
        ),
        "all_external_abis_exact": all(
            row["graph_io"] == expected_io for row in rows
        ),
        "all_inference_contracts_pass": all(
            row["inference"]["pass"] for row in rows
        ),
        "formal_behavior_cells_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    contract = {
        "schema_version": "winner_v113.postexport_transform_contract.v1",
        "status": (
            "PASS_WINNER_V113_POSTEXPORT_TRANSFORM_CONTRACT"
            if not failed
            else "HOLD_WINNER_V113_POSTEXPORT_TRANSFORM_CONTRACT"
        ),
        "failed_checks": failed,
        "checks": checks,
        "transform": {
            "order": [
                "source conservative all-joint previous-action projection",
                "G3 actual-centered pitch guard at 0.165 rad",
                "exact x=0 command deadband",
            ],
            "g3_margin_rad": margin,
            "deadband_abs_command_x": deadband,
        },
        "policies": rows,
        "formal_behavior_cells_executed": 0,
        "authority": {
            "nominal_behavior_preregistration_authorized": not failed,
            "behavior_evaluation_authorized": False,
            "checkpoint_selection_authorized": False,
            "gate5_authorized": False,
            "rdkx5_or_robot": False,
            "robot_clearance": False,
            "torque_or_motion": False,
        },
    }
    CONTRACT.write_text(
        json.dumps(contract, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner-v113 post-export transform contract\n\n"
        f"Status: `{contract['status']}`\n\n"
        "Both post-update V112 ONNX graphs retain every learned node and "
        "initializer, then append the already-frozen G3 actual-centered guard "
        "and exact x=0 deadband. No behavior, Gate 5, robot, torque, or motion "
        "is authorized by this transform.\n",
        encoding="utf-8",
    )
    print(contract["status"])
    for row in rows:
        print(f"{row['id']}={row['output_sha256']}")
    print(f"contract_sha256={sha256(CONTRACT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
