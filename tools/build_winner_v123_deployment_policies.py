#!/usr/bin/env python3
"""Apply the exact trained-delta hierarchy to both V122 checkpoints."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np
import onnx


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from build_ground_up_actual_centered_guard_screen import (  # noqa: E402
    append_guard,
)
from build_ground_up_command_deadband_repair import (  # noqa: E402
    wrap as append_deadband,
)
from build_winner_v113_postexport_policies import (  # noqa: E402
    graph_io,
    initializers,
    sha256,
    source_prefix_exact,
)
from build_winner_v117_postguard_rate_projection_policies import (  # noqa: E402
    append_projection,
    inference_contract,
    normalized_source_nodes,
)


ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v123_deployment_transform_preregistration.json"
CONTRACT = ANALYSIS / "winner_v123_deployment_transform_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V123_DEPLOYMENT_TRANSFORM_CONTRACT_20260724.md"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    for path in (args.output_root, CONTRACT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V123: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V123_DEPLOYMENT_TRANSFORM"
        or prereg.get("failed_checks") != []
    ):
        raise ValueError("V123 transform preregistration changed")

    transform = prereg["transform"]
    home = np.asarray(transform["home_target_rad"], dtype=np.float32)
    actual_obs_indices = np.asarray(
        transform["measured_joint_offset_indices"], dtype=np.int64
    )
    pitch_indices = np.asarray(
        transform["pitch_chain_action_indices"], dtype=np.int64
    )
    selected_delta = np.asarray(
        transform["exact_train_normalized_action_delta"], dtype=np.float32
    )
    command_index = int(transform["command_x_observation_index"])
    deadband = float(transform["zero_deadband_absolute_command_x"])
    action_scale = float(transform["action_scale_rad"])
    margin = float(transform["g3_margin_rad"])
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
    args.output_root.mkdir(parents=True)
    rows = []
    for spec in prereg["sources"]:
        source_path = args.source_root.resolve() / spec["filename"]
        if (
            source_path.stat().st_size != spec["bytes"]
            or sha256(source_path) != spec["sha256"]
        ):
            raise ValueError(f"raw V122 source changed: {spec['id']}")
        source = onnx.load(source_path)
        source_initializers = initializers(source)
        guarded = append_guard(
            source,
            obs_indices=actual_obs_indices,
            pitch_indices=pitch_indices,
            home=home,
            action_scale=action_scale,
            margin=margin,
        )
        deadbanded = append_deadband(
            guarded,
            command_index=command_index,
            deadband=deadband,
        )
        final = append_projection(
            deadbanded,
            selected_delta=selected_delta,
            command_index=command_index,
            deadband=deadband,
        )
        output_path = args.output_root.resolve() / spec["output_filename"]
        onnx.checker.check_model(final)
        onnx.save(final, output_path)
        final_initializers = initializers(final)
        inference = inference_contract(
            source_path,
            output_path,
            selected_delta=selected_delta,
            changed_indices=pitch_indices,
            command_index=command_index,
            deadband=deadband,
            home=home,
            pitch_indices=pitch_indices,
            actual_obs_indices=actual_obs_indices,
            action_scale=action_scale,
            guard_margin=margin,
        )
        rows.append(
            {
                "id": spec["id"],
                "step": spec["step"],
                "source_path": str(source_path),
                "source_sha256": sha256(source_path),
                "output_path": str(output_path),
                "output_sha256": sha256(output_path),
                "output_bytes": output_path.stat().st_size,
                "source_nodes_preserved_through_guard_deadband": (
                    source_prefix_exact(source, deadbanded)
                ),
                "preprojection_nodes_preserved": (
                    [
                        node.SerializeToString()
                        for node in final.graph.node[: len(deadbanded.graph.node)]
                    ]
                    == normalized_source_nodes(deadbanded)
                ),
                "source_initializers_preserved": all(
                    name in final_initializers
                    and np.array_equal(value, final_initializers[name])
                    for name, value in source_initializers.items()
                ),
                "source_train_delta_exact": bool(
                    "max_action_delta" in source_initializers
                    and np.array_equal(
                        source_initializers["max_action_delta"],
                        selected_delta[None],
                    )
                ),
                "final_projection_delta_exact": bool(
                    np.array_equal(
                        final_initializers["v117_max_action_delta"],
                        selected_delta[None],
                    )
                ),
                "guard_nodes_added": (
                    len(guarded.graph.node) - len(source.graph.node)
                ),
                "first_deadband_nodes_added": (
                    len(deadbanded.graph.node) - len(guarded.graph.node)
                ),
                "final_projection_nodes_added": (
                    len(final.graph.node) - len(deadbanded.graph.node)
                ),
                "graph_io": graph_io(final),
                "inference": inference,
            }
        )
    checks = {
        "two_postupdate_sources_transformed": len(rows) == 2,
        "all_source_hashes_exact": all(
            row["source_sha256"] == spec["sha256"]
            for row, spec in zip(rows, prereg["sources"], strict=True)
        ),
        "all_source_nodes_preserved": all(
            row["source_nodes_preserved_through_guard_deadband"]
            and row["preprojection_nodes_preserved"]
            for row in rows
        ),
        "all_source_initializers_preserved": all(
            row["source_initializers_preserved"] for row in rows
        ),
        "all_source_train_deltas_exact": all(
            row["source_train_delta_exact"] for row in rows
        ),
        "all_final_projection_deltas_exact": all(
            row["final_projection_delta_exact"] for row in rows
        ),
        "all_append_exact_hierarchy": all(
            row["guard_nodes_added"] == 13
            and row["first_deadband_nodes_added"] == 5
            and row["final_projection_nodes_added"] == 9
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
    value = {
        "schema_version": "winner_v123.deployment_transform_contract.v1",
        "status": (
            "PASS_WINNER_V123_DEPLOYMENT_TRANSFORM_CONTRACT"
            if not failed
            else "HOLD_WINNER_V123_DEPLOYMENT_TRANSFORM_CONTRACT"
        ),
        "failed_checks": failed,
        "checks": checks,
        "transform": transform,
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
        "# Winner-v123 deployment transform contract\n\n"
        f"Status: `{value['status']}`\n\n"
        "Both V122 post-update graphs preserve trained nodes and use the "
        "exact trained float32 delta for the final post-G3 projection. No "
        "behavior, Gate 5, RDK-X5, or robot authority.\n",
        encoding="utf-8",
    )
    print(value["status"])
    for row in rows:
        print(f"{row['id']}={row['output_sha256']}")
    print(f"sha256={sha256(CONTRACT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
