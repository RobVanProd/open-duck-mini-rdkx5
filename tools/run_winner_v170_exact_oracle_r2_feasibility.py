#!/usr/bin/env python3
"""Run the frozen one-cell V170 exact-oracle R2 feasibility screen."""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Mapping

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"

import jax


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import run_winner_v126_exact_oracle_behavior as v126_behavior  # noqa: E402
from run_winner_v131_two_fit_oracle_behavior import (  # noqa: E402
    robust_trace_audit,
)


ANALYSIS = ROOT / "outputs/analysis"
PREREG = (
    ANALYSIS / "winner_v170_exact_oracle_r2_feasibility_preregistration.json"
)
OUTPUT = ANALYSIS / "winner_v170_exact_oracle_r2_feasibility_result.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V170_EXACT_ORACLE_R2_FEASIBILITY_RESULT_20260725.md"
)
V126_PREREG = (
    ANALYSIS / "winner_v126_all_tick_supreme_clip_preregistration.json"
)
BASE_PREREG = v126_behavior.BASE_PREREG
V140_RESULT = ANALYSIS / "winner_v140_preservation_projected_actor_result.json"
V169_RESULT = ANALYSIS / "winner_v169_v128_final_r2_anchor_result.json"
EXECUTION_CORRECTION = (
    ANALYSIS / "winner_v170b_execution_input_correction.json"
)
EXECUTION_CORRECTION_SHA256 = (
    "1aea59bfff28f4646d620b5f358d8f9106fbfacdfd1bf79fbc82d4a412b3ea58"
)
BUILDER = (
    TOOLS
    / "build_winner_v170_exact_oracle_r2_feasibility_preregistration.py"
)
PROJECTOR = TOOLS / "exact_torque_oracle_two_fit.py"
V126_RUNNER = TOOLS / "run_winner_v126_exact_oracle_behavior.py"
V131_RUNNER = TOOLS / "run_winner_v131_two_fit_oracle_behavior.py"
TORQUE_LIMIT_NM = 1.91229675
CURRENT_LIMIT_A = 2.5


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_evaluator(path: Path):
    spec = importlib.util.spec_from_file_location(
        "closed_loop_sim_eval_v170_two_fit", path
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load V170 evaluator: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def floor_friction_readback_checks(
    row: Mapping[str, Any],
    result: Mapping[str, Any],
    _base_prereg: Mapping[str, Any],
) -> dict[str, bool]:
    expected = row["configuration"]
    dynamics = (result.get("env") or {}).get("dynamics_override") or {}
    readback = dynamics.get("readback") or {}
    return {
        "dynamics_override_enabled": bool(dynamics.get("enabled")),
        "floor_friction_key_exact": dynamics.get("key") == "floor_friction",
        "floor_friction_requested_exact": expected
        == {"floor_friction": 0.5},
        "floor_friction_value_exact": float(dynamics.get("value", -1.0))
        == 0.5,
        "floor_friction_before_exact": float(readback.get("before", -1.0))
        == 1.0,
        "floor_friction_after_exact": float(readback.get("after", -1.0))
        == 0.5,
        "floor_friction_changed_index_exact": readback.get("changed_indices")
        == [[0, 0]],
    }


def frozen_paths(
    *,
    evaluator_root: Path,
    evaluator_path: Path,
    policy: Path,
) -> dict[str, Path]:
    return {
        "builder": BUILDER,
        "runner": Path(__file__).resolve(),
        "v126_runner": V126_RUNNER,
        "v131_runner": V131_RUNNER,
        "two_fit_projector": PROJECTOR,
        "v126_preregistration": V126_PREREG,
        "base_preregistration": BASE_PREREG,
        "v131_cpu_contract": ANALYSIS
        / "winner_v131_two_fit_oracle_cpu_contract.json",
        "v131_behavior_result": ANALYSIS
        / "winner_v131_two_fit_oracle_behavior_result.json",
        "v140_result": V140_RESULT,
        "v160_result": ANALYSIS
        / "winner_v160_remaining_shadow_census_result.json",
        "v168_result": ANALYSIS
        / "winner_v168_fit_conditioned_policy_bank_cpu_result.json",
        "v169_result": V169_RESULT,
        "composition_manifest": evaluator_root / "composition_manifest.json",
        "composed_evaluator": evaluator_path,
        "selected_policy": policy,
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
            raise FileExistsError(f"refusing to overwrite V170: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("V170 execution requires a clean worktree")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    correction = json.loads(
        EXECUTION_CORRECTION.read_text(encoding="utf-8")
    )
    v126 = json.loads(V126_PREREG.read_text(encoding="utf-8"))
    base = json.loads(BASE_PREREG.read_text(encoding="utf-8"))
    v140 = json.loads(V140_RESULT.read_text(encoding="utf-8"))
    manifest_path = evaluator_root / "composition_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    evaluator_path = Path(manifest["output"]["path"])
    policy = Path(v140["artifacts"]["selected_deployed"]["path"])
    observed_hashes = {
        name: sha256(path)
        for name, path in frozen_paths(
            evaluator_root=evaluator_root,
            evaluator_path=evaluator_path,
            policy=policy,
        ).items()
    }
    expected_except_runner = {
        name: value
        for name, value in prereg.get("input_hashes", {}).items()
        if name != "runner"
    }
    observed_except_runner = {
        name: value
        for name, value in observed_hashes.items()
        if name != "runner"
    }
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V170_EXACT_ORACLE_R2_FEASIBILITY"
        or prereg.get("failed_checks") != []
        or expected_except_runner != observed_except_runner
        or correction.get("status")
        != "FROZEN_WINNER_V170B_EXECUTION_INPUT_CORRECTION"
        or sha256(EXECUTION_CORRECTION) != EXECUTION_CORRECTION_SHA256
        or correction.get("preregistration_sha256") != sha256(PREREG)
        or correction.get("prior_runner_sha256")
        != prereg.get("input_hashes", {}).get("runner")
    ):
        raise ValueError("V170 preregistration or correction changed")
    matrix = prereg["matrix"]["rows"]
    if len(matrix) != 1:
        raise ValueError("V170 must contain exactly one cell")
    row = matrix[0]

    evaluator = load_evaluator(evaluator_path)

    def make_config(**kwargs):
        configuration = kwargs.pop("winner_v3_configuration_override")
        if configuration != {"floor_friction": 0.5}:
            raise ValueError("V170 floor-friction request changed")
        kwargs["eval_dynamics_override"] = configuration
        kwargs["winner_v3_configuration_override"] = None
        return evaluator.ClosedLoopConfig(**kwargs)

    active = str(row["plant"])
    shadow = (
        "P31_34_PITCH_WITH_P30_NONPITCH"
        if active == "P30_ALL_JOINT"
        else "P30_ALL_JOINT"
    )

    def run_with_shadow(config):
        return evaluator.run_closed_loop_sim(
            dataclasses.replace(
                config,
                exact_torque_oracle_shadow_fit=v126_behavior.actuator_fit(
                    base, shadow
                ),
                exact_torque_oracle_maximum_fit_passes=14,
            )
        )

    v126_behavior.ClosedLoopConfig = make_config
    v126_behavior.run_closed_loop_sim = run_with_shadow
    v126_behavior.readback_checks = floor_friction_readback_checks

    run_root.mkdir(parents=True)
    traces_root = run_root / "traces"
    cells_root = run_root / "cells"
    traces_root.mkdir()
    cells_root.mkdir()
    trace_path = traces_root / "v170_v140_p31_34_x0.077_floor0.5.jsonl"
    cpu_only = (
        jax.default_backend() == "cpu"
        and all(device.platform == "cpu" for device in jax.devices())
    )
    started = time.time()
    try:
        cell = v126_behavior.execute_cell(
            row=row,
            base_prereg=base,
            policy=policy,
            playground=Path(v126["external_inputs"]["playground"]),
            trace_path=trace_path,
            action_delta=tuple(
                float(value) for value in v126["oracle"]["action_delta"]
            ),
            schedule_ticks=None,
            cpu_only=cpu_only,
        )
        robust = robust_trace_audit(trace_path, moving=True)
        cell["two_fit_oracle"] = robust
        strict_checks = {
            "two_fit_complete_600": robust["checks"]["complete_600"],
            "two_fit_all_rows_robust_safe": robust["checks"][
                "moving_all_robust"
            ],
            "two_fit_zero_empty_intersections": robust["checks"][
                "zero_empty_intersections"
            ],
            "strict_torque_peak": float(
                cell["torque_gate"]["peak_torque_nm"]
            )
            <= TORQUE_LIMIT_NM,
            "strict_current_peak": float(
                cell["prospective_current_gate"]["peak_current_a"]
            )
            <= CURRENT_LIMIT_A,
            "floor_friction_readback_exact": all(
                cell["readback_checks"].values()
            ),
        }
        cell["strict_checks"] = strict_checks
        for name, passed in strict_checks.items():
            if not passed:
                cell["failure_reasons"].append(name)
        cell["failure_reasons"] = sorted(set(cell["failure_reasons"]))
        cell["pass"] = not cell["failure_reasons"]
        cell["status"] = (
            "PASS_WINNER_V170_EXACT_ORACLE_R2_FEASIBILITY_CELL"
            if cell["pass"]
            else "HOLD_WINNER_V170_EXACT_ORACLE_R2_FEASIBILITY_CELL"
        )
    except Exception as exc:
        cell = {
            "schema_version": (
                "winner_v170.exact_oracle_r2_feasibility_cell.v1"
            ),
            "status": "INVALID_WINNER_V170_EXACT_ORACLE_R2_FEASIBILITY_CELL",
            "pass": False,
            "failure_reasons": [
                f"runner_exception_{type(exc).__name__}"
            ],
            "identity": dict(row),
            "simulator": {
                "status": f"RUNNER_EXCEPTION_{type(exc).__name__}",
                "error": str(exc),
            },
            "policy": {"path": str(policy), "sha256": sha256(policy)},
        }

    cell = v126_behavior.json_finite(cell)
    cell_path = cells_root / "v170_v140_p31_34_x0.077_floor0.5.json"
    cell_path.write_text(
        json.dumps(cell, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    valid = (
        not any(
            reason.startswith("runner_exception_")
            for reason in cell["failure_reasons"]
        )
        and trace_path.is_file()
        and int((cell.get("trace") or {}).get("rows", -1)) == 600
    )
    screen_pass = valid and bool(cell["pass"])
    decision = (
        "EARN_V171_SAFE_ARCHITECTURE_DESIGN_ONLY"
        if screen_pass
        else (
            "CLOSE_V140_NEARBY_SAFE_GAIT_AT_FIRST_R2_CONDITION"
            if valid
            else "INVALID_V170_REQUIRES_EXECUTION_CORRECTION"
        )
    )
    payload = {
        "schema_version": "winner_v170.exact_oracle_r2_feasibility_result.v1",
        "status": (
            "PASS_WINNER_V170_EXACT_ORACLE_R2_FEASIBILITY_VALID_RESULT"
            if valid
            else "INVALID_WINNER_V170_EXACT_ORACLE_R2_FEASIBILITY_RESULT"
        ),
        "decision": decision,
        "failed_validity_checks": (
            []
            if valid
            else ["one_complete_nonexception_600_tick_cell"]
        ),
        "screen_pass": screen_pass,
        "cell": cell,
        "cell_sha256": sha256(cell_path),
        "trace_sha256": sha256(trace_path) if trace_path.is_file() else None,
        "wall_seconds": time.time() - started,
        "run_root": str(run_root),
        "input_hashes": observed_hashes,
        "authority": {
            "safe_architecture_design": screen_pass,
            "training": False,
            "hosted_training": False,
            "candidate_selection": False,
            "later_r2_condition": False,
            "full_matrix": False,
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
        "# Winner V170 exact-oracle first-R2 feasibility result\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Decision: `{payload['decision']}`\n"
        f"- Cell pass: `{cell['pass']}`.\n"
        f"- Failures: `{cell['failure_reasons']}`.\n"
        "- One CPU cell only; no training, Colab, hardware, motion, "
        "candidate selection, or later robustness condition.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(payload["decision"])
    print(
        json.dumps(
            {
                "pass": cell["pass"],
                "failures": cell["failure_reasons"],
                "metrics": cell.get("metrics"),
                "two_fit_oracle": cell.get("two_fit_oracle"),
            }
        )
    )
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
