#!/usr/bin/env python3
"""Run V163's preregistered feasibility-preserving update falsifier."""

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
import onnx


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from audit_winner_v140_preservation_projected_actor import (  # noqa: E402
    interpolate_model,
)
from run_winner_v129_oracle_teacher_cpu_contract import (  # noqa: E402
    deploy_graph,
)
from run_winner_v141_projected_final_behavior import (  # noqa: E402
    load_evaluator,
    run_cell,
)


ANALYSIS = ROOT / "outputs/analysis"
PREREG = (
    ANALYSIS
    / "winner_v163_feasibility_preserving_falsifier_preregistration.json"
)
OUTPUT = (
    ANALYSIS / "winner_v163_feasibility_preserving_falsifier_result.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V163_FEASIBILITY_PRESERVING_FALSIFIER_RESULT_20260725.md"
)
V121_PREREG = ANALYSIS / "winner_v121_nominal_behavior_preregistration.json"
V121_RESULT = ANALYSIS / "winner_v121_nominal_behavior_result.json"
V127_CPU = ANALYSIS / "winner_v127_constrained_cpu_result.json"
V162_RESULT = ANALYSIS / "winner_v162_uniform_trust_nominal_result.json"
V126 = ANALYSIS / "winner_v126_all_tick_supreme_clip_preregistration.json"
BASE = (
    ANALYSIS
    / "winner_v3_variable_configuration_replacement_preregistration.json"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def input_paths(
    prereg: dict[str, Any], evaluator_root: Path
) -> dict[str, Path]:
    manifest_path = evaluator_root / "composition_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    return {
        "builder": TOOLS
        / "build_winner_v163_feasibility_preserving_falsifier_preregistration.py",
        "runner": Path(__file__).resolve(),
        "cell_runner": TOOLS / "run_winner_v141_projected_final_behavior.py",
        "interpolator": TOOLS
        / "audit_winner_v140_preservation_projected_actor.py",
        "deployer": TOOLS / "run_winner_v129_oracle_teacher_cpu_contract.py",
        "v121_preregistration": V121_PREREG,
        "v121_result": V121_RESULT,
        "v127_cpu_result": V127_CPU,
        "v162_result": V162_RESULT,
        "v126_preregistration": V126,
        "base_preregistration": BASE,
        "composition_manifest": manifest_path,
        "composed_evaluator": Path(manifest["output"]["path"]),
        "source_raw": Path(prereg["sources"]["source_raw"]["path"]),
        "proposal_raw": Path(prereg["sources"]["proposal_raw"]["path"]),
    }


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
            raise FileExistsError(f"refusing to overwrite V163: {path}")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    paths = input_paths(prereg, evaluator_root)
    observed_hashes = {name: sha256(path) for name, path in paths.items()}
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V163_FEASIBILITY_PRESERVING_FALSIFIER"
        or prereg.get("failed_checks") != []
        or prereg.get("input_hashes") != observed_hashes
    ):
        raise ValueError("V163 preregistration changed")

    v126 = json.loads(V126.read_text(encoding="utf-8"))
    base = json.loads(BASE.read_text(encoding="utf-8"))
    transform = json.loads(
        (
            ANALYSIS / "winner_v121_deployment_transform_contract.json"
        ).read_text(encoding="utf-8")
    )["transform"]
    evaluator = load_evaluator(paths["composed_evaluator"])
    source_model = onnx.load(paths["source_raw"])
    proposal_model = onnx.load(paths["proposal_raw"])
    run_root.mkdir(parents=True)
    policies_root = run_root / "policies"
    cells_root = run_root / "cells"
    traces_root = run_root / "traces"
    policies_root.mkdir()
    cells_root.mkdir()
    traces_root.mkdir()
    cpu_only = (
        jax.default_backend() == "cpu"
        and all(device.platform == "cpu" for device in jax.devices())
    )
    if not cpu_only:
        raise RuntimeError("V163 must execute CPU-only")

    trials = []
    accepted = None
    started = time.time()
    source_worst = float(
        prereg["sources"]["source_worst_peak_torque_nm"]
    )
    for alpha_index, alpha in enumerate(
        prereg["backtracking"]["alphas_descending"]
    ):
        label = f"a{alpha_index:02d}_{float(alpha):.8f}".replace(".", "p")
        raw_model, changed = interpolate_model(
            source_model, proposal_model, float(alpha)
        )
        raw_path = policies_root / f"winner_v163_{label}_raw.onnx"
        deployed_path = policies_root / f"winner_v163_{label}_deployed.onnx"
        onnx.save(raw_model, raw_path)
        deployment = deploy_graph(raw_path, deployed_path, transform)
        trial_cells = []
        for cell_index, source_row in enumerate(
            prereg["matrix"]["rows_in_source_margin_risk_order"]
        ):
            row = dict(source_row)
            row["checkpoint_id"] = f"V163_ALPHA_{float(alpha):.8f}"
            row["policy_sha256"] = sha256(deployed_path)
            stem = (
                f"v163_{label}_{str(row['plant']).lower()}_"
                f"x{float(row['command_x_m_s']):.3f}_"
                f"seed{int(row['seed'])}"
            )
            trace_path = traces_root / f"{stem}.jsonl"
            cell = run_cell(
                evaluator=evaluator,
                row=row,
                policy=deployed_path,
                playground=Path(v126["external_inputs"]["playground"]),
                base_prereg=base,
                trace_path=trace_path,
                cpu_only=cpu_only,
            )
            cell_path = cells_root / f"{stem}.json"
            cell_path.write_text(
                json.dumps(
                    cell, allow_nan=False, indent=2, sort_keys=True
                )
                + "\n",
                encoding="utf-8",
            )
            cell["cell_sha256"] = sha256(cell_path)
            trial_cells.append(cell)
            print(
                json.dumps(
                    {
                        "alpha_index": alpha_index,
                        "alpha": alpha,
                        "cell": cell_index + 1,
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

        six_moving_pass = (
            len(trial_cells) == 6
            and all(cell["pass"] for cell in trial_cells)
        )
        worst_torque = (
            max(
                cell["torque_gate"]["worst_peak_torque_nm"]
                for cell in trial_cells
            )
            if trial_cells
            else None
        )
        source_reserve_improved = bool(
            six_moving_pass
            and worst_torque is not None
            and worst_torque < source_worst
        )
        x0_exact = bool(
            deployment["inference"]["checks"]["zero_action_exact"]
            and deployment["inference"]["checks"]["zero_previous_exact"]
        )
        trial = {
            "alpha_index": alpha_index,
            "alpha": float(alpha),
            "changed_initializers": changed,
            "raw": {
                "path": str(raw_path),
                "sha256": sha256(raw_path),
            },
            "deployed": deployment,
            "cells": trial_cells,
            "completed_moving_cells": len(trial_cells),
            "six_moving_cells_pass": six_moving_pass,
            "two_x0_cells_exact_by_invariant": x0_exact,
            "all_eight_nominal_cells_pass": six_moving_pass and x0_exact,
            "worst_peak_torque_nm": worst_torque,
            "source_worst_peak_torque_nm": source_worst,
            "source_reserve_strictly_improved": source_reserve_improved,
        }
        trials.append(trial)
        if six_moving_pass and x0_exact:
            accepted = trial
            break

    earned = bool(
        accepted is not None
        and accepted["source_reserve_strictly_improved"]
    )
    payload = {
        "schema_version": (
            "winner_v163.feasibility_preserving_falsifier_result.v1"
        ),
        "status": (
            "PASS_WINNER_V163_FEASIBILITY_PRESERVING_FALSIFIER"
            if earned
            else "HOLD_WINNER_V163_FEASIBILITY_PRESERVING_FALSIFIER"
        ),
        "failed_checks": (
            []
            if earned
            else [
                "nontrivial_first_feasible_update_preserves_all_eight_"
                "and_improves_source_reserve"
            ]
        ),
        "input_hashes": {
            **observed_hashes,
            "preregistration": sha256(PREREG),
        },
        "cpu_only": cpu_only,
        "trials": trials,
        "accepted": (
            {
                "alpha": accepted["alpha"],
                "all_eight_nominal_cells_pass": accepted[
                    "all_eight_nominal_cells_pass"
                ],
                "worst_peak_torque_nm": accepted["worst_peak_torque_nm"],
                "source_reserve_strictly_improved": accepted[
                    "source_reserve_strictly_improved"
                ],
                "policy": accepted["deployed"],
            }
            if accepted is not None
            else None
        ),
        "summary": {
            "alphas_attempted": len(trials),
            "moving_cells_executed": sum(
                len(trial["cells"]) for trial in trials
            ),
            "source_worst_peak_torque_nm": source_worst,
            "wall_seconds": time.time() - started,
        },
        "decision": (
            "EARN_V164_FEASIBILITY_PRESERVING_UPDATE_CPU_CONTRACT_ONLY"
            if earned
            else "CLOSE_FEASIBILITY_PRESERVING_FIRST_PROPOSAL_NO_RETRY"
        ),
        "authority": {
            "next_cpu_contract": earned,
            "training": False,
            "hosted_training": False,
            "full_robustness": False,
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
        "# Winner V163 feasibility-preserving falsifier result\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Alphas attempted: `{len(trials)}`.\n"
        f"- Moving cells executed: "
        f"`{payload['summary']['moving_cells_executed']}`.\n"
        f"- First feasible alpha: "
        f"`{None if accepted is None else accepted['alpha']}`.\n"
        f"- Source reserve improved: "
        f"`{False if accepted is None else accepted['source_reserve_strictly_improved']}`.\n"
        f"- Decision: `{payload['decision']}`\n"
        "- CPU-only; no new training, Colab, deployment, Gate 5, RDK-X5, "
        "or robot.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(payload["decision"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if earned else 1


if __name__ == "__main__":
    raise SystemExit(main())
