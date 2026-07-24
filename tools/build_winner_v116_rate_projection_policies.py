#!/usr/bin/env python3
"""Apply the preregistered V116 conservative rate vector to both policies."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import onnx
from onnx import numpy_helper
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from build_winner_v113_postexport_policies import (  # noqa: E402
    graph_io,
    initializers,
    sha256,
)


ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v116_rate_projection_preregistration.json"
CONTRACT = ANALYSIS / "winner_v116_rate_projection_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V116_RATE_PROJECTION_CONTRACT_20260724.md"


def replace_initializer(
    model: onnx.ModelProto, name: str, value: np.ndarray
) -> None:
    for index, initializer in enumerate(model.graph.initializer):
        if initializer.name == name:
            replacement = numpy_helper.from_array(value, name=name)
            model.graph.initializer[index].CopyFrom(replacement)
            return
    raise KeyError(name)


def node_bytes(model: onnx.ModelProto) -> list[bytes]:
    return [node.SerializeToString() for node in model.graph.node]


def inference_contract(
    source_path: Path,
    output_path: Path,
    *,
    selected_delta: np.ndarray,
    changed_indices: set[int],
) -> dict[str, Any]:
    source = ort.InferenceSession(
        source_path.read_bytes(), providers=["CPUExecutionProvider"]
    )
    transformed = ort.InferenceSession(
        output_path.read_bytes(), providers=["CPUExecutionProvider"]
    )
    rng = np.random.default_rng(20260724)
    max_delta_excess = 0.0
    max_unchanged_joint_error = 0.0
    max_hidden_error = 0.0
    max_zero_action = 0.0
    max_zero_previous = 0.0
    all_finite = True
    saw_changed_output = False
    for command_x in (0.0, 0.074, 0.077, 0.080):
        previous = np.zeros((1, 14), dtype=np.float32)
        hidden = np.zeros((1, 64), dtype=np.float32)
        for _ in range(128):
            obs = rng.normal(0.0, 0.25, (1, 115)).astype(np.float32)
            obs[:, 6] = np.float32(command_x)
            feed = {
                "obs": obs,
                "previous_action": previous,
                "h_in": hidden,
            }
            source_values = source.run(None, feed)
            transformed_values = transformed.run(None, feed)
            action, previous_out, hidden_out = transformed_values
            all_finite &= all(
                np.isfinite(value).all()
                for value in (*source_values, *transformed_values)
            )
            max_delta_excess = max(
                max_delta_excess,
                float(
                    np.max(
                        np.abs(action - previous)
                        - selected_delta[None]
                    )
                ),
            )
            unchanged = [
                index for index in range(14) if index not in changed_indices
            ]
            max_unchanged_joint_error = max(
                max_unchanged_joint_error,
                float(
                    np.max(
                        np.abs(
                            action[:, unchanged]
                            - source_values[0][:, unchanged]
                        )
                    )
                ),
            )
            max_hidden_error = max(
                max_hidden_error,
                float(np.max(np.abs(hidden_out - source_values[2]))),
            )
            saw_changed_output |= bool(
                np.any(
                    action[:, sorted(changed_indices)]
                    != source_values[0][:, sorted(changed_indices)]
                )
            )
            if command_x == 0.0:
                max_zero_action = max(
                    max_zero_action, float(np.max(np.abs(action)))
                )
                max_zero_previous = max(
                    max_zero_previous,
                    float(np.max(np.abs(previous_out))),
                )
            previous = previous_out.astype(np.float32)
            hidden = hidden_out.astype(np.float32)
    checks = {
        "cpu_provider_exact": transformed.get_providers()
        == ["CPUExecutionProvider"],
        "all_outputs_finite": bool(all_finite),
        "selected_rate_delta_enforced": max_delta_excess <= 2.0e-7,
        "unchanged_joint_actions_bit_exact": max_unchanged_joint_error == 0.0,
        "recurrent_hidden_output_bit_exact": max_hidden_error == 0.0,
        "zero_action_exact": max_zero_action == 0.0,
        "zero_previous_exact": max_zero_previous == 0.0,
        "changed_projection_is_exercised": saw_changed_output,
    }
    return {
        "pass": all(checks.values()),
        "checks": checks,
        "max_delta_excess": max_delta_excess,
        "max_unchanged_joint_error": max_unchanged_joint_error,
        "max_hidden_error": max_hidden_error,
        "max_zero_action": max_zero_action,
        "max_zero_previous": max_zero_previous,
        "changed_projection_is_exercised": saw_changed_output,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    for path in (args.output_root, CONTRACT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V116: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V116_RATE_PROJECTION"
        or prereg.get("failed_checks") != []
        or sha256(Path(__file__).resolve())
        != prereg["input_hashes"]["transform_tool"]
    ):
        raise ValueError("V116 preregistration changed")
    selected_delta = np.asarray(
        prereg["projection"]["selected_normalized_action_delta"],
        dtype=np.float32,
    )
    current_delta = np.asarray(
        prereg["projection"]["current_normalized_action_delta"],
        dtype=np.float32,
    )
    changed_indices = {
        int(index)
        for index in np.flatnonzero(selected_delta != current_delta)
    }
    args.output_root.mkdir(parents=True)
    rows = []
    for source_spec in prereg["sources"]:
        source_path = args.source_root.resolve() / source_spec["filename"]
        if sha256(source_path) != source_spec["sha256"]:
            raise ValueError(f"V116 source changed: {source_spec['id']}")
        source = onnx.load(source_path)
        transformed = copy.deepcopy(source)
        source_initializers = initializers(source)
        replace_initializer(
            transformed, "max_action_delta", selected_delta[None]
        )
        onnx.checker.check_model(transformed)
        output_path = (
            args.output_root.resolve() / source_spec["output_filename"]
        )
        onnx.save(transformed, output_path)
        transformed_initializers = initializers(transformed)
        changed_initializer_names = sorted(
            name
            for name in set(source_initializers) | set(transformed_initializers)
            if name not in source_initializers
            or name not in transformed_initializers
            or not np.array_equal(
                source_initializers[name], transformed_initializers[name]
            )
        )
        inference = inference_contract(
            source_path,
            output_path,
            selected_delta=selected_delta,
            changed_indices=changed_indices,
        )
        rows.append(
            {
                "id": source_spec["id"],
                "step": source_spec["step"],
                "source_sha256": sha256(source_path),
                "output_path": str(output_path),
                "output_sha256": sha256(output_path),
                "output_bytes": output_path.stat().st_size,
                "graph_nodes_bit_exact": (
                    node_bytes(source) == node_bytes(transformed)
                ),
                "changed_initializer_names": changed_initializer_names,
                "selected_delta_exact": np.array_equal(
                    transformed_initializers["max_action_delta"],
                    selected_delta[None],
                ),
                "all_other_initializers_bit_exact": all(
                    name == "max_action_delta"
                    or (
                        name in transformed_initializers
                        and np.array_equal(
                            value, transformed_initializers[name]
                        )
                    )
                    for name, value in source_initializers.items()
                ),
                "graph_io": graph_io(transformed),
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
        "two_postupdate_policies_transformed": len(rows) == 2,
        "source_hashes_exact": all(
            row["source_sha256"] == source_spec["sha256"]
            for row, source_spec in zip(
                rows, prereg["sources"], strict=True
            )
        ),
        "graph_nodes_bit_exact": all(
            row["graph_nodes_bit_exact"] for row in rows
        ),
        "only_max_action_delta_changed": all(
            row["changed_initializer_names"] == ["max_action_delta"]
            for row in rows
        ),
        "selected_delta_exact": all(
            row["selected_delta_exact"] for row in rows
        ),
        "all_other_initializers_bit_exact": all(
            row["all_other_initializers_bit_exact"] for row in rows
        ),
        "external_abi_exact": all(
            row["graph_io"] == expected_io for row in rows
        ),
        "all_inference_contracts_pass": all(
            row["inference"]["pass"] for row in rows
        ),
        "formal_behavior_cells_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    value = {
        "schema_version": "winner_v116.rate_projection_contract.v1",
        "status": (
            "PASS_WINNER_V116_RATE_PROJECTION_CONTRACT"
            if not failed
            else "HOLD_WINNER_V116_RATE_PROJECTION_CONTRACT"
        ),
        "failed_checks": failed,
        "checks": checks,
        "projection": prereg["projection"],
        "policies": rows,
        "formal_behavior_cells_executed": 0,
        "authority": {
            "nominal_behavior_preregistration_authorized": not failed,
            "behavior_evaluation_authorized": False,
            "full_matrix_authorized": False,
            "checkpoint_selection_authorized": False,
            "gate5_authorized": False,
            "rdkx5_or_robot": False,
            "robot_clearance": False,
            "torque_or_motion": False,
        },
    }
    CONTRACT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner-v116 rate projection contract\n\n"
        f"Status: `{value['status']}`\n\n"
        "Both checkpoint graphs are bit-exact except for the single "
        "`max_action_delta` initializer. The same evidence-derived vector is "
        "applied to both. No training or behavior cell is executed here.\n",
        encoding="utf-8",
    )
    print(value["status"])
    for row in rows:
        print(f"{row['id']}={row['output_sha256']}")
    print(f"sha256={sha256(CONTRACT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
