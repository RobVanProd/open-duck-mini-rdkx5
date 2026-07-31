#!/usr/bin/env python3
"""Apply the frozen G3 guard and x=0 deadband to V114 exports."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile

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
    CONSERVATIVE_LIMITS_RAD_S,
    graph_io,
    inference_contract,
    initializers,
    sha256,
    source_prefix_exact,
)


ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v115_postexport_transform_preregistration.json"
GUARD_PREREG = (
    ANALYSIS / "ground_up_actual_centered_guard_screen_preregistration.json"
)
DEADBAND_PREREG = (
    ANALYSIS / "ground_up_command_deadband_repair_preregistration.json"
)
CONTRACT = ANALYSIS / "winner_v115_postexport_transform_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V115_POSTEXPORT_TRANSFORM_CONTRACT_20260724.md"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    for path in (args.output_root, CONTRACT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V115: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    guard_prereg = json.loads(GUARD_PREREG.read_text(encoding="utf-8"))
    deadband_prereg = json.loads(
        DEADBAND_PREREG.read_text(encoding="utf-8")
    )
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V115_POSTEXPORT_TRANSFORM"
        or prereg.get("failed_checks") != []
        or sha256(Path(__file__).resolve())
        != prereg["input_hashes"]["transform_tool"]
    ):
        raise ValueError("V115 transform preregistration changed")
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
        with tempfile.TemporaryDirectory(prefix="winner_v115_") as temporary:
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
        "schema_version": "winner_v115.postexport_transform_contract.v1",
        "status": (
            "PASS_WINNER_V115_POSTEXPORT_TRANSFORM_CONTRACT"
            if not failed
            else "HOLD_WINNER_V115_POSTEXPORT_TRANSFORM_CONTRACT"
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
        "# Winner-v115 post-export transform contract\n\n"
        f"Status: `{contract['status']}`\n\n"
        "Both post-update V114 graphs retain every learned node and "
        "initializer, then append the frozen G3 actual-centered guard and "
        "exact x=0 deadband. This authorizes no behavior, Gate 5, robot, "
        "torque, or motion.\n",
        encoding="utf-8",
    )
    print(contract["status"])
    for row in rows:
        print(f"{row['id']}={row['output_sha256']}")
    print(f"contract_sha256={sha256(CONTRACT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
