#!/usr/bin/env python3
"""Run V162's preregistered 16-cell nominal pair gate."""

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
PREREG = ANALYSIS / "winner_v162_uniform_trust_nominal_preregistration.json"
V126 = ANALYSIS / "winner_v126_all_tick_supreme_clip_preregistration.json"
BASE = (
    ANALYSIS
    / "winner_v3_variable_configuration_replacement_preregistration.json"
)
V161 = ANALYSIS / "winner_v161_uniform_trust_projection_result.json"
OUTPUT = ANALYSIS / "winner_v162_uniform_trust_nominal_result.json"
MARKDOWN = ANALYSIS / "WINNER_V162_UNIFORM_TRUST_NOMINAL_RESULT_20260725.md"


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
            raise FileExistsError(f"refusing to overwrite V162: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    v126 = json.loads(V126.read_text(encoding="utf-8"))
    base = json.loads(BASE.read_text(encoding="utf-8"))
    v161 = json.loads(V161.read_text(encoding="utf-8"))
    manifest_path = evaluator_root / "composition_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    evaluator_path = Path(manifest["output"]["path"])
    policies = {
        name: Path(spec["path"])
        for name, spec in prereg["candidate_pair"]["policies"].items()
    }
    paths = {
        "builder": TOOLS
        / "build_winner_v162_uniform_trust_nominal_preregistration.py",
        "runner": Path(__file__).resolve(),
        "cell_runner": TOOLS
        / "run_winner_v141_projected_final_behavior.py",
        "v121_nominal_preregistration": ANALYSIS
        / "winner_v121_nominal_behavior_preregistration.json",
        "v161_result": V161,
        "v126_preregistration": V126,
        "base_preregistration": BASE,
        "composition_manifest": manifest_path,
        "composed_evaluator": evaluator_path,
        "half_policy": policies["half"],
        "final_policy": policies["final"],
    }
    observed_hashes = {name: sha256(path) for name, path in paths.items()}
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V162_UNIFORM_TRUST_NOMINAL"
        or prereg.get("failed_checks") != []
        or prereg.get("input_hashes") != observed_hashes
        or v161.get("decision")
        != "EARN_V162_UNIFORM_TRUST_PROJECTED_DUAL_CHECKPOINT_NOMINAL"
    ):
        raise ValueError("V162 preregistration changed")
    evaluator = load_evaluator(evaluator_path)
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
    for index, row in enumerate(prereg["matrix"]["rows"], start=1):
        candidate_id = (
            "half"
            if row["checkpoint_id"] == "V161_TRUST_PROJECTED_HALF"
            else "final"
        )
        stem = (
            f"v162_{candidate_id}_{str(row['plant']).lower()}_"
            f"x{float(row['command_x_m_s']):.3f}_seed{int(row['seed'])}"
        )
        trace_path = traces_root / f"{stem}.jsonl"
        cell = run_cell(
            evaluator=evaluator,
            row=row,
            policy=policies[candidate_id],
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
                    "completed": index,
                    "total": 16,
                    "checkpoint": candidate_id,
                    "plant": row["plant"],
                    "command_x": row["command_x_m_s"],
                    "pass": cell["pass"],
                    "failures": cell["failure_reasons"],
                    "peak_torque_nm": cell.get("torque_gate", {}).get(
                        "worst_peak_torque_nm"
                    ),
                }
            ),
            flush=True,
        )
        if not cell["pass"]:
            break
    all_pass = len(cells) == 16 and all(cell["pass"] for cell in cells)
    per_checkpoint = []
    for candidate_id in ("half", "final"):
        subset = [
            cell
            for cell in cells
            if cell["identity"]["checkpoint_id"]
            == (
                "V161_TRUST_PROJECTED_HALF"
                if candidate_id == "half"
                else "V161_TRUST_PROJECTED_FINAL"
            )
        ]
        per_checkpoint.append(
            {
                "id": candidate_id,
                "cells": len(subset),
                "passing": sum(cell["pass"] for cell in subset),
                "all_eight_pass": (
                    len(subset) == 8 and all(cell["pass"] for cell in subset)
                ),
                "worst_peak_torque_nm": (
                    max(
                        cell["torque_gate"]["worst_peak_torque_nm"]
                        for cell in subset
                    )
                    if subset
                    else None
                ),
                "worst_tracking_p95_rad": (
                    max(
                        cell["metrics"]["worst_tracking_p95_rad"]
                        for cell in subset
                    )
                    if subset
                    else None
                ),
            }
        )
    payload = {
        "schema_version": "winner_v162.uniform_trust_nominal_result.v1",
        "status": (
            "PASS_WINNER_V162_UNIFORM_TRUST_NOMINAL"
            if all_pass
            else "HOLD_WINNER_V162_UNIFORM_TRUST_NOMINAL"
        ),
        "failed_checks": (
            [] if all_pass else ["both_checkpoints_all_eight_cells_pass"]
        ),
        "input_hashes": {
            **observed_hashes,
            "preregistration": sha256(PREREG),
        },
        "cells": cells,
        "per_checkpoint": per_checkpoint,
        "summary": {
            "planned_cells": 16,
            "completed_cells": len(cells),
            "passing_cells": sum(cell["pass"] for cell in cells),
            "common_alpha": prereg["candidate_pair"]["common_alpha"],
            "wall_seconds": time.time() - started,
        },
        "artifacts": {"run_root": str(run_root)},
        "decision": (
            "EARN_V163_COMPLETE_FROZEN_ROBUSTNESS_PREREGISTRATION"
            if all_pass
            else "CLOSE_UNIFORM_TRUST_PROJECTION_NO_ALPHA_RETRY"
        ),
        "authority": {
            "nominal_behavior": True,
            "full_robustness_preregistration": all_pass,
            "training": False,
            "hosted_training": False,
            "checkpoint_selection": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V162 uniform trust nominal result\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Completed/passing: `{len(cells)}/"
        f"{sum(cell['pass'] for cell in cells)}` of 16 planned.\n"
        f"- Common alpha: `{prereg['candidate_pair']['common_alpha']}`.\n"
        f"- Decision: `{payload['decision']}`\n"
        "- CPU-only; no training, Colab, checkpoint selection, "
        "deployment, Gate 5, or robot.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(payload["decision"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
