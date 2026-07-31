#!/usr/bin/env python3
"""Run V174's preregistered zero-credit nominal behavior falsifier."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from typing import Any

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
PREREG = ANALYSIS / "winner_v174_tangent_nominal_preregistration.json"
RESULT = ANALYSIS / "winner_v174_tangent_nominal_result.json"
MARKDOWN = ANALYSIS / "WINNER_V174_TANGENT_NOMINAL_RESULT_20260725.md"
V121_PREREG = ANALYSIS / "winner_v121_nominal_behavior_preregistration.json"
V121_RESULT = ANALYSIS / "winner_v121_nominal_behavior_result.json"
V126_PREREG = (
    ANALYSIS / "winner_v126_all_tick_supreme_clip_preregistration.json"
)
BASE_PREREG = (
    ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
)
V170_RESULT = (
    ANALYSIS / "winner_v170_exact_oracle_r2_feasibility_result.json"
)
V173_PREREG = (
    ANALYSIS
    / "winner_v173_lexicographic_tangent_cpu_preregistration.json"
)
V173_RESULT = ANALYSIS / "winner_v173_lexicographic_tangent_cpu_result.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def input_paths(
    prereg: dict[str, Any],
    evaluator_root: Path,
) -> dict[str, Path]:
    manifest_path = evaluator_root / "composition_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    return {
        "builder": ROOT
        / "tools/build_winner_v174_tangent_nominal_preregistration.py",
        "runner": Path(__file__).resolve(),
        "cell_runner": ROOT
        / "tools/run_winner_v141_projected_final_behavior.py",
        "v121_preregistration": V121_PREREG,
        "v121_result": V121_RESULT,
        "v126_preregistration": V126_PREREG,
        "base_preregistration": BASE_PREREG,
        "v170_result": V170_RESULT,
        "v173_preregistration": V173_PREREG,
        "v173_result": V173_RESULT,
        "composition_manifest": manifest_path,
        "composed_evaluator": Path(manifest["output"]["path"]),
        "policy": Path(prereg["external_inputs"]["policy"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument("--evaluator-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    args = parser.parse_args()
    evaluator_root = args.evaluator_root.resolve()
    run_root = args.run_root.resolve()
    for path in (RESULT, MARKDOWN, run_root):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V174: {path}")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    paths = input_paths(prereg, evaluator_root)
    observed_hashes = {name: sha256(path) for name, path in paths.items()}
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V174_TANGENT_NOMINAL"
        or prereg.get("failed_checks") != []
        or prereg.get("input_hashes") != observed_hashes
    ):
        raise ValueError("V174 preregistration or inputs changed")
    cpu_only = (
        jax.default_backend() == "cpu"
        and all(device.platform == "cpu" for device in jax.devices())
    )
    if not cpu_only:
        raise RuntimeError("V174 must execute CPU-only")

    evaluator = load_evaluator(paths["composed_evaluator"])
    v126 = json.loads(V126_PREREG.read_text(encoding="utf-8"))
    base = json.loads(BASE_PREREG.read_text(encoding="utf-8"))
    run_root.mkdir(parents=True)
    cells_root = run_root / "cells"
    traces_root = run_root / "traces"
    cells_root.mkdir()
    traces_root.mkdir()
    cells = []
    started = time.time()
    for index, row in enumerate(
        prereg["matrix"]["rows_in_source_margin_risk_order"]
    ):
        stem = (
            f"v174_{str(row['plant']).lower()}_"
            f"x{float(row['command_x_m_s']):.3f}_"
            f"seed{int(row['seed'])}"
        )
        trace_path = traces_root / f"{stem}.jsonl"
        cell = run_cell(
            evaluator=evaluator,
            row=dict(row),
            policy=paths["policy"],
            playground=Path(v126["external_inputs"]["playground"]),
            base_prereg=base,
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
                    "cell": index + 1,
                    "plant": row["plant"],
                    "command_x": row["command_x_m_s"],
                    "pass": cell["pass"],
                    "failure_reasons": cell["failure_reasons"],
                    "worst_peak_torque_nm": cell.get(
                        "torque_gate", {}
                    ).get("worst_peak_torque_nm"),
                }
            ),
            flush=True,
        )
        if not cell["pass"]:
            break

    six_moving_pass = len(cells) == 6 and all(cell["pass"] for cell in cells)
    x0_exact = bool(
        prereg["checks"]["x0_graph_invariants_exact"]
        and prereg["matrix"]["x0_cells_by_exact_graph_invariant"] == 2
    )
    worst_torque = (
        max(
            float(cell["torque_gate"]["worst_peak_torque_nm"])
            for cell in cells
        )
        if cells
        else None
    )
    source_worst = float(
        prereg["source_baseline"]["worst_peak_torque_nm"]
    )
    reserve_improved = bool(
        six_moving_pass
        and worst_torque is not None
        and worst_torque < source_worst
    )
    green = six_moving_pass and x0_exact and reserve_improved
    checks = {
        "cpu_only": cpu_only,
        "policy_hash_exact": (
            sha256(paths["policy"]) == prereg["policy"]["sha256"]
        ),
        "six_moving_cells_pass": six_moving_pass,
        "two_x0_cells_exact_by_graph_invariant": x0_exact,
        "source_worst_torque_strictly_improved": reserve_improved,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v174.tangent_nominal_result.v1",
        "status": (
            "PASS_WINNER_V174_TANGENT_NOMINAL"
            if green
            else "HOLD_WINNER_V174_TANGENT_NOMINAL"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {
            **observed_hashes,
            "preregistration": sha256(PREREG),
        },
        "policy": prereg["policy"],
        "cells": cells,
        "summary": {
            "moving_cells_executed": len(cells),
            "moving_cells_passed": sum(cell["pass"] for cell in cells),
            "x0_cells_exact_by_invariant": 2 if x0_exact else 0,
            "worst_peak_torque_nm": worst_torque,
            "source_worst_peak_torque_nm": source_worst,
            "source_torque_reserve_improvement_nm": (
                source_worst - worst_torque
                if worst_torque is not None
                else None
            ),
            "wall_seconds": time.time() - started,
        },
        "decision": (
            "EARN_ONE_V175_HOSTED_PREREGISTRATION_ONLY"
            if green
            else "CLOSE_LEXICOGRAPHIC_TANGENT_OPTIMIZER_NO_RETRY"
        ),
        "authority": {
            "v175_hosted_preregistration_design": green,
            "hosted_training": False,
            "candidate_selection": False,
            "robustness_matrix": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
        "run_root": str(run_root),
    }
    RESULT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V174 tangent-policy nominal result\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Moving cells executed/passed: `{len(cells)}` / "
        f"`{sum(cell['pass'] for cell in cells)}`.\n"
        f"- Two x=0 cells exact by graph invariant: `{x0_exact}`.\n"
        f"- Worst/source torque: `{worst_torque}` / `{source_worst}` N.m.\n"
        f"- Strict source reserve improvement: `{reserve_improved}`.\n"
        f"- Decision: `{payload['decision']}`\n"
        "- CPU-only, no new training, hosted run, candidate, robustness "
        "matrix, Gate 5, RDK-X5, or robot.\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "failed_checks": failed,
                "output": str(RESULT),
                "sha256": sha256(RESULT),
            }
        )
    )
    return 0 if green else 1


if __name__ == "__main__":
    raise SystemExit(main())
