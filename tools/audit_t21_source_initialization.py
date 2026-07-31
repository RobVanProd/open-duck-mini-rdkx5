#!/usr/bin/env python3
"""Attribute T21's sole prefix-rate failure without optimizer execution."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

import jax.numpy as jnp
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
RESULT = ANALYSIS / "t21_two_rate_separation_cpu_result.json"
MODULE = ROOT / "patches" / "t19_support_trainthrough.py"
OUTPUT = ANALYSIS / "t21_source_initialization_attribution.json"
MARKDOWN = (
    ANALYSIS / "T21_SOURCE_INITIALIZATION_ATTRIBUTION_20260726.md"
)


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    resolved = path.resolve()
    digest = hashlib.sha256(resolved.read_bytes()).hexdigest()
    return {
        "path": str(resolved),
        "bytes": resolved.stat().st_size,
        "sha256": digest,
    }


def load_module():
    spec = importlib.util.spec_from_file_location(
        "t21_source_initialization_audit_module",
        MODULE,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load frozen T21 module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite attribution: {path}")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    module = load_module()
    previous = jnp.zeros(14, dtype=jnp.float32)
    action_history = []
    for _ in range(module.CALIBRATION_TICKS):
        previous = module.next_calibration_action(previous)
        action_history.append(np.asarray(previous))
    external_actions = np.asarray(action_history, dtype=np.float32)
    source_actions = np.asarray(
        module.inverse_action(jnp.asarray(external_actions)),
        dtype=np.float32,
    )
    coherent_initial = np.asarray(
        module.inverse_action(jnp.zeros(14, dtype=jnp.float32)),
        dtype=np.float32,
    )
    zero_initial_previous = np.concatenate(
        (np.zeros((1, 14), dtype=np.float32), source_actions[:-1]),
        axis=0,
    )
    coherent_previous = np.concatenate(
        (coherent_initial[None, :], source_actions[:-1]),
        axis=0,
    )
    source_delta_limit = np.asarray(
        module.SOURCE_MAX_ACTION_DELTA,
        dtype=np.float32,
    )
    zero_initial_excess = np.maximum(
        np.abs(source_actions - zero_initial_previous)
        - source_delta_limit[None, :],
        0.0,
    )
    coherent_excess = np.maximum(
        np.abs(source_actions - coherent_previous)
        - source_delta_limit[None, :],
        0.0,
    )
    zero_location = np.unravel_index(
        int(np.argmax(zero_initial_excess)),
        zero_initial_excess.shape,
    )
    measured_excess_rad = result["prefix_diagnostic"]["maximum_errors"][
        "source_rate_excess_rad_per_tick"
    ]
    predicted_excess_rad = float(
        np.max(zero_initial_excess) * module.ACTION_SCALE_RAD
    )
    checks = {
        "formal_hold_is_only_prefix_diagnostic": (
            result.get("status")
            == "HOLD_T21_TWO_RATE_SEPARATION_CPU_CONTRACT"
            and result.get("failed_checks")
            == ["all_250_prefix_diagnostic_checks_pass"]
        ),
        "sole_prefix_failure_is_source_rate": (
            result.get("prefix_diagnostic", {}).get("failed_checks")
            == ["source_trained_rate_all_ticks"]
        ),
        "all_external_and_reset_contracts_green": all(
            result["prefix_diagnostic"]["checks"][name]
            for name in (
                "external_physical_rate_all_ticks",
                "external_target_matches_action_all_ticks",
                "final_external_support_exact",
                "final_external_target_exact",
                "final_source_target_returns_home",
            )
        )
        and result["checks"]["all_64_variable_configuration_checks_pass"]
        and result["checks"]["default_off_canonical_trajectory_9_of_9"],
        "zero_source_initialization_predicts_measured_excess": (
            abs(predicted_excess_rad - measured_excess_rad) <= 1.0e-7
        ),
        "coherent_source_initialization_removes_algebraic_excess": (
            float(np.max(coherent_excess)) == 0.0
        ),
        "coherent_initial_is_inverse_of_external_home": (
            np.count_nonzero(coherent_initial) > 0
        ),
        "no_optimizer_hosted_or_robot_execution": (
            result["execution"]
            == {
                "hosted_or_colab_compute": 0,
                "optimizer_steps": 0,
                "robot_or_rdk_access": 0,
            }
        ),
    }
    checks = {name: bool(passed) for name, passed in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    basis = {
        "schema_version": "open_duck.t21_source_initialization_audit.v1",
        "status": (
            "PASS_T21_SOURCE_INITIALIZATION_ATTRIBUTION"
            if not failed
            else "HOLD_T21_SOURCE_INITIALIZATION_ATTRIBUTION"
        ),
        "decision": (
            "PREREGISTER_T21B_SOURCE_COORDINATE_INITIALIZATION"
            if not failed
            else "KEEP_T22_CLOSED"
        ),
        "inputs": {
            "t21_result": receipt(RESULT),
            "t21_module": receipt(MODULE),
        },
        "attribution": {
            "cause": (
                "The physical target begins at external action zero, but the "
                "source-coordinate target was initialized at source action "
                "zero. Under the support homeomorphism those are different "
                "points: external zero maps to inverse_action(0)."
            ),
            "coherent_initial_source_action": coherent_initial.astype(
                float
            ).tolist(),
            "maximum_zero_initial_excess_normalized": float(
                np.max(zero_initial_excess)
            ),
            "maximum_zero_initial_excess_rad": predicted_excess_rad,
            "maximum_zero_initial_excess_tick": int(zero_location[0]),
            "maximum_zero_initial_excess_joint": int(zero_location[1]),
            "measured_maximum_excess_rad": float(measured_excess_rad),
            "maximum_coherent_initial_excess_normalized": float(
                np.max(coherent_excess)
            ),
            "correction": (
                "Initialize only the unscored prefix's internal source-target "
                "state to home + inverse_action(external_zero)*0.25. Keep the "
                "physical target at home and retain both frozen rate vectors."
            ),
            "t21_partial_or_policy_selection_weight": 0,
            "new_optimizer_steps_authorized": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "checks": checks,
        "failed_checks": failed,
    }
    value = {
        **basis,
        "attribution_sha256": canonical_sha256(basis),
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T21 source-coordinate initialization attribution",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                f"- Failed checks: `{failed}`",
                (
                    "- Predicted/measured excess: "
                    f"`{predicted_excess_rad:.9f}/"
                    f"{measured_excess_rad:.9f} rad`"
                ),
                (
                    "- Coherent-initialization algebraic excess: "
                    f"`{float(np.max(coherent_excess)):.9f}`"
                ),
                "- Optimizer/hosted/robot execution: `0/0/0`",
                f"- Attribution SHA-256: `{value['attribution_sha256']}`",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"failed_checks={failed}")
    print(f"attribution_sha256={value['attribution_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
