#!/usr/bin/env python3
"""Attribute the Winner-v24 GAE one-ULP hold without new simulation."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RESULT = ANALYSIS / "winner_v24_symmetric_failure_cpu_result.json"
OUTPUT = ANALYSIS / "winner_v24_gae_one_ulp_attribution.json"
MARKDOWN = ANALYSIS / "WINNER_V24_GAE_ONE_ULP_ATTRIBUTION_20260722.md"
SOURCES = {
    "builder": Path("tools/build_winner_v24_gae_one_ulp_attribution.py"),
    "tests": Path("tests/test_winner_v24_gae_one_ulp_attribution.py"),
    "cpu_result": Path("outputs/analysis/winner_v24_symmetric_failure_cpu_result.json"),
    "cpu_importer": Path("tools/import_winner_v24_symmetric_failure_cpu_result.py"),
    "cpu_runner": Path("tools/run_winner_v24_symmetric_failure_cpu_contract.py"),
    "mechanics": Path("patches/winner_v24_symmetric_support_failure.py"),
    "contract": Path("outputs/analysis/winner_v24_symmetric_failure_cpu_contract.json"),
}


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    if args.output.exists() or args.markdown.exists():
        raise FileExistsError("refusing to overwrite Winner-v24 attribution")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    return_error = float(
        result["batch_evidence"]["baseline_return_replay_max_abs_error"]
    )
    advantage_error = float(
        result["batch_evidence"]["baseline_advantage_replay_max_abs_error"]
    )
    one_ulp_at_250 = float(np.spacing(np.float32(250.0)))
    other_failed = [
        name
        for name, passed in result["checks"].items()
        if not passed and name != "baseline_gae_replay_at_most_1e_6"
    ]
    checks = {
        "source_is_imported_attempt1_hold": result.get("status")
        == "HOLD_WINNER_V24_SYMMETRIC_FAILURE_CPU_CONTRACT"
        and result.get("decision") == "DO_NOT_RUN_WINNER_V24_OPTIMIZER_UPDATE"
        and result.get("repository_attribution", {}).get("github_run_attempt") == 1,
        "only_baseline_gae_check_failed": result.get("failed_checks")
        == ["baseline_gae_replay_at_most_1e_6"]
        and other_failed == [],
        "return_error_is_exactly_one_float32_ulp_at_250": return_error
        == one_ulp_at_250,
        "advantage_error_passed_original_threshold": advantage_error <= 1.0e-6,
        "default_off_and_objective_locality_passed": result["checks"].get(
            "default_off_batch_bit_exact"
        )
        is True
        and result["checks"].get(
            "enabled_changes_only_rewards_returns_advantages"
        )
        is True
        and result["checks"].get("all_other_rewards_bit_exact") is True,
        "predictor_and_policy_gradient_causal_checks_passed": result["checks"].get(
            "predictor_loss_and_gradients_bit_exact"
        )
        is True
        and result["checks"].get("ppo_action_head_gradient_changes") is True
        and result["checks"].get("ppo_recurrent_gradient_changes") is True,
        "zero_optimizer_support_locomotion_robot": result.get("execution")
        == {
            "rollout_episode_slots": 80,
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "errors_are_finite": math.isfinite(return_error)
        and math.isfinite(advantage_error),
    }
    failed_checks = sorted(name for name, passed in checks.items() if not passed)
    sources = {
        name: {
            "path": str(path).replace("\\", "/"),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    payload = {
        "schema_version": "winner_v24.gae_one_ulp_attribution.v1",
        "status": (
            "PASS_WINNER_V24_GAE_ONE_ULP_ATTRIBUTION"
            if not failed_checks
            else "HOLD_WINNER_V24_GAE_ONE_ULP_ATTRIBUTION"
        ),
        "decision": (
            "AUTHORIZE_BASELINE_ANCHORED_SYMMETRIC_FAILURE_CPU_CONTRACT_ONLY"
            if not failed_checks
            else "STOP_WINNER_V24_OBJECTIVE_ROUTE"
        ),
        "checks": checks,
        "failed_checks": failed_checks,
        "evidence": {
            "baseline_return_replay_max_abs_error": return_error,
            "baseline_advantage_replay_max_abs_error": advantage_error,
            "float32_ulp_at_250": one_ulp_at_250,
            "return_error_over_ulp": return_error / one_ulp_at_250,
            "causal_checks_passed": sum(result["checks"].values()),
            "causal_checks_total": len(result["checks"]),
        },
        "prospective_correction": {
            "anchor": "recorded baseline returns and values",
            "change": (
                "apply only the analytically propagated -250 terminal reward delta, then "
                "renormalize the resulting advantages; do not reconstruct unchanged GAE"
            ),
            "old_result_rewritten": False,
            "threshold_relaxed": False,
            "new_simulation_now": False,
        },
        "execution": {
            "new_simulation_cells": 0,
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "training_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "manual_mass_com_inertia_measurements_required": False,
            "pass_authorizes_only": "a separately frozen baseline-anchored zero-update CPU contract",
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
    }
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v24 GAE one-ULP attribution",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                f"- Return replay error / float32 ULP at 250: `{return_error} / {one_ulp_at_250}`",
                f"- Advantage replay error: `{advantage_error}`",
                "- Old result rewritten / threshold relaxed / new simulation: `false / false / false`",
                "- Optimizer / robot: `0 / 0`",
                "",
                "The correction must anchor to recorded baseline returns and apply only the",
                "analytic terminal-reward delta. It cannot authorize an optimizer update.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0 if not failed_checks else 1


if __name__ == "__main__":
    raise SystemExit(main())
