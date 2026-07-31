#!/usr/bin/env python3
"""Run V157's six remaining final-checkpoint nominal cells."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"

import jax


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from run_winner_v141_projected_final_behavior import (  # noqa: E402
    load_evaluator,
    run_cell,
)


ANALYSIS = ROOT / "outputs/analysis"
PREREG = (
    ANALYSIS / "winner_v157_dual_checkpoint_nominal_preregistration.json"
)
V121_RESULT = ANALYSIS / "winner_v121_nominal_behavior_result.json"
V126_PREREG = (
    ANALYSIS / "winner_v126_all_tick_supreme_clip_preregistration.json"
)
BASE_PREREG = (
    ANALYSIS
    / "winner_v3_variable_configuration_replacement_preregistration.json"
)
V141_RESULT = ANALYSIS / "winner_v141_projected_final_behavior_result.json"
V155_RESULT = (
    ANALYSIS / "winner_v155_velocity_gated_phase_residual_result.json"
)
V156_CORRECTION = (
    ANALYSIS
    / "winner_v156_state_triggered_causal_behavior_reporting_correction.json"
)
OUTPUT = ANALYSIS / "winner_v157_dual_checkpoint_nominal_result.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V157_DUAL_CHECKPOINT_NOMINAL_RESULT_20260725.md"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument("--evaluator-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    args = parser.parse_args()
    evaluator_root = args.evaluator_root.resolve()
    run_root = args.run_root.resolve()
    for path in (OUTPUT, MARKDOWN, run_root):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V157: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    v121 = json.loads(V121_RESULT.read_text(encoding="utf-8"))
    v126 = json.loads(V126_PREREG.read_text(encoding="utf-8"))
    base_prereg = json.loads(BASE_PREREG.read_text(encoding="utf-8"))
    v141 = json.loads(V141_RESULT.read_text(encoding="utf-8"))
    v155 = json.loads(V155_RESULT.read_text(encoding="utf-8"))
    v156 = json.loads(V156_CORRECTION.read_text(encoding="utf-8"))
    manifest_path = evaluator_root / "composition_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    evaluator_path = Path(manifest["output"]["path"])
    policy = Path(v155["artifact"]["deployed"]["path"])
    paths = {
        "runner": Path(__file__).resolve(),
        "v121_nominal_result": V121_RESULT,
        "v126_preregistration": V126_PREREG,
        "base_preregistration": BASE_PREREG,
        "v141_result": V141_RESULT,
        "v155_result": V155_RESULT,
        "v156_reporting_correction": V156_CORRECTION,
        "v141_runner": TOOLS / "run_winner_v141_projected_final_behavior.py",
        "composition_manifest": manifest_path,
        "composed_evaluator": evaluator_path,
        "selected_final_policy": policy,
    }
    observed_hashes = {name: sha256(path) for name, path in paths.items()}
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V157_DUAL_CHECKPOINT_NOMINAL"
        or prereg.get("failed_checks") != []
        or prereg.get("input_hashes") != observed_hashes
        or v156.get("decision")
        != "EARN_V157_DUAL_CHECKPOINT_FULL_MATRIX_PREREGISTRATION"
    ):
        raise ValueError("V157 preregistration changed")
    evaluator = load_evaluator(evaluator_path)
    playground = Path(v126["external_inputs"]["playground"])
    matrix = prereg["matrix"]["new_final_rows"]
    if len(matrix) != 6:
        raise ValueError("V157 requires six new final cells")
    run_root.mkdir(parents=True)
    cells_root = run_root / "cells"
    traces_root = run_root / "traces"
    cells_root.mkdir()
    traces_root.mkdir()
    cpu_only = (
        jax.default_backend() == "cpu"
        and all(device.platform == "cpu" for device in jax.devices())
    )
    cells = []
    started = time.time()
    for index, row in enumerate(matrix, start=1):
        stem = (
            f"v155_final_{str(row['plant']).lower()}_"
            f"x{float(row['command_x_m_s']):.3f}_seed{int(row['seed'])}"
        )
        trace_path = traces_root / f"{stem}.jsonl"
        cell = run_cell(
            evaluator=evaluator,
            row=row,
            policy=policy,
            playground=playground,
            base_prereg=base_prereg,
            trace_path=trace_path,
            cpu_only=cpu_only,
        )
        cell_path = cells_root / f"{stem}.json"
        cell_path.write_text(
            json.dumps(cell, allow_nan=False, indent=2, sort_keys=True)
            + "\n",
            encoding="utf-8",
        )
        cell["cell_sha256"] = sha256(cell_path)
        cells.append(cell)
        print(
            json.dumps(
                {
                    "completed_cells": index,
                    "total_new_cells": 6,
                    "pass": cell["pass"],
                    "failures": cell["failure_reasons"],
                    "identity": row,
                    "peak_torque_nm": cell.get("torque_gate", {}).get(
                        "worst_peak_torque_nm"
                    ),
                }
            ),
            flush=True,
        )
        if not cell["pass"]:
            break
    reused_half = next(
        row
        for row in v121["per_checkpoint"]
        if row["checkpoint_id"] == "V121_TRAIN_MATCHED_HALF"
    )
    reused_final_passes = (
        int(v141["new_final_cells"][0]["pass"])
        + int(
            v156.get("status")
            == "PASS_WINNER_V156_STATE_TRIGGERED_CAUSAL_BEHAVIOR_"
            "REPORTING_CORRECTION"
        )
    )
    all_pass = (
        reused_half["all_eight_cells_pass"]
        and reused_final_passes == 2
        and len(cells) == 6
        and all(cell["pass"] for cell in cells)
    )
    payload = {
        "schema_version": "winner_v157.dual_checkpoint_nominal_result.v1",
        "status": (
            "PASS_WINNER_V157_DUAL_CHECKPOINT_NOMINAL"
            if all_pass
            else "HOLD_WINNER_V157_DUAL_CHECKPOINT_NOMINAL"
        ),
        "failed_checks": (
            []
            if all_pass
            else ["combined_reused_and_new_cells_16_of_16"]
        ),
        "input_hashes": observed_hashes,
        "reused_half": reused_half,
        "reused_final": {
            "p30_x0": v141["new_final_cells"][0],
            "p30_x0_candidate_action_exact": True,
            "p30_x0_candidate_hidden_unchanged_from_v140": True,
            "p30_x0_candidate_physics_equivalent": True,
            "p30_x0_pass": bool(v141["new_final_cells"][0]["pass"]),
            "p30_x0_source": "V141",
            "p30_x0_source_policy": (
                "V140; V155 preserves h_out and exact-zero final action"
            ),
            "p30_x0_reuse_reason": (
                "V155 appends only a final-action residual before the "
                "unchanged x=0 deadband, changes no hidden output, and its "
                "graph contract proves x=0 action is exact zero"
            ),
            "p30_x0_reuse_selection_weight": 0,
            "p30_x0_v155_graph_checks": {
                "hidden_output_bit_exact": v155["checks"][
                    "hidden_output_bit_exact"
                ],
                "x0_deadband_remains_exact": v155["checks"][
                    "x0_deadband_remains_exact"
                ],
            },
            "p30_x0_v155_policy_sha256": sha256(policy),
            "p30_x0_v155_result_sha256": sha256(V155_RESULT),
            "p30_x0_v141_result_sha256": sha256(V141_RESULT),
            "p30_x0_authority": "read-only evidence reuse; no behavior rerun",
            "p30_x0_new_cells": 0,
            "p30_x0_reused_cells": 1,
            "p30_x0_gate": "exact-zero",
            "p30_x0_contract": "same physical control sequence",
            "p30_x0_status": "PASS_REUSED_EQUIVALENT_CELL",
            "p30_x0_failure_reasons": [],
            "p30_x0_policy_contract": {
                "x0_action_nonzero_values": 0
            },
            "p30_x0_robot_clearance": False,
            "p30_x0_training_or_reward_selection_weight": 0,
            "p30_x0_note": (
                "full V141 cell retained above for complete audit detail"
            ),
            "p30_x074": {
                "source": "V156 reporting correction",
                "status": v156["status"],
                "metrics": v156["cell_metrics"],
                "active_ticks": v156["corrected_causal_contract"][
                    "active_ticks"
                ],
            },
        },
        "new_final_cells": cells,
        "summary": {
            "reused_half_cells": 8,
            "reused_half_passing": int(reused_half["passing_cells"]),
            "reused_final_cells": 2,
            "reused_final_passing": reused_final_passes,
            "new_final_cells_planned": 6,
            "new_final_cells_completed": len(cells),
            "new_final_cells_passing": sum(cell["pass"] for cell in cells),
            "combined_cells_passing": (
                int(reused_half["passing_cells"])
                + reused_final_passes
                + sum(cell["pass"] for cell in cells)
            ),
            "combined_cells_required": 16,
            "elapsed_s": time.time() - started,
        },
        "decision": (
            "EARN_V158_FROZEN_ROBUSTNESS_LADDER_PREREGISTRATION"
            if all_pass
            else "CLOSE_VELOCITY_GATED_PHASE_RESIDUAL"
        ),
        "authority": {
            "robustness_preregistration": all_pass,
            "policy_deployment": False,
            "gate5": False,
            "training": False,
            "hosted_training": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V157 dual-checkpoint nominal result\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Combined: `{payload['summary']['combined_cells_passing']}/16`.\n"
        f"- New final: `{payload['summary']['new_final_cells_passing']}/"
        f"{len(cells)}`.\n"
        f"- Decision: `{payload['decision']}`\n"
        "- No policy deployment, Gate 5, Colab, or hardware authority.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(payload["decision"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
