#!/usr/bin/env python3
"""Preregister the read-only T96 state-coherent FiLM audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = (
    ANALYSIS / "t96_film_state_coherent_audit_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T96_FILM_STATE_COHERENT_AUDIT_PREREGISTRATION_20260728.md"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def canonical_sha256(value: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T96: {path}")
    t95 = json.loads(
        (ANALYSIS / "t95_film_conditioned_cpu_result.json").read_text(
            encoding="utf-8"
        )
    )
    sources = {
        "t95_result": receipt(
            ANALYSIS / "t95_film_conditioned_cpu_result.json"
        ),
        "t95_final_graph": t95["training"]["final_onnx"],
        "t11_method": receipt(
            ROOT / "tools" / "run_t11_context_action_observability.py"
        ),
        "t94_contexts": receipt(
            ANALYSIS / "t94_r2_calibration_manifold_result.json"
        ),
        "runner": receipt(
            ROOT / "tools" / "run_t96_film_state_coherent_audit.py"
        ),
        "test": receipt(
            ROOT / "tests" / "test_t96_film_state_coherent_audit.py"
        ),
    }
    checks = {
        "t95_formal_hold_exact": (
            t95["status"] == "HOLD_T95_FILM_CONDITIONED_CPU_CONTRACT"
        ),
        "t95_only_action_binding_checks_failed": all(
            name
            in {
                "at_least_half_context_pairs_change_action",
                "both_negative_com_contexts_change_action",
                "context_action_effect_at_least_ten_x_t11",
                "maximum_context_action_delta_material",
            }
            for name in t95["failed_checks"]
        ),
        "t95_film_leaf_updated": bool(
            t95["training"]["film_leaf_deltas"]
        )
        and all(
            delta > 0
            for delta in t95["training"]["film_leaf_deltas"].values()
        ),
        "t95_protected_actor_exact": all(
            delta == 0
            for delta in t95["training"][
                "protected_actor_leaf_deltas"
            ].values()
        ),
        "no_training_behavior_or_hardware": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    basis = {
        "schema_version": (
            "open_duck.t96_film_state_coherent_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T96_FILM_STATE_COHERENT_AUDIT"
            if not failed
            else "HOLD_T96_FILM_STATE_COHERENT_PREREGISTRATION"
        ),
        "question": (
            "Did T95 produce a real FiLM action effect that its random-"
            "observation recurrent sequence hid behind the frozen rate "
            "projection?"
        ),
        "causal_basis": {
            "t95": (
                "The FiLM kernel changed by 0.007623818, all protected actor "
                "leaves remained exact, but only 2/2560 final actions changed."
            ),
            "t11_control": (
                "T11 established the state-coherent construction: first "
                "evaluate the zero-context raw action, then use that raw "
                "action as previous_action for both counterfactual contexts."
            ),
            "audit_scope": (
                "Read-only graph instrumentation and inference only. The "
                "T95 thresholds are copied unchanged."
            ),
        },
        "sources": sources,
        "formal_contract": {
            "contexts": 40,
            "cases_per_context": 64,
            "total_cases": 2560,
            "minimum_effect_tick_fraction": 0.05,
            "minimum_context_pair_effect_fraction": 0.50,
            "minimum_maximum_action_delta": 1e-5,
            "both_negative_com_contexts_required": True,
            "effect_threshold_abs": 1e-8,
            "x0_exact": True,
            "recurrent_state_invariant": True,
            "rate_excess_tolerance": 1e-7,
        },
        "decision_rule": {
            "pass": (
                "Every unchanged T95 action-binding threshold passes under "
                "the T11 state-coherent construction."
            ),
            "pass_decision": (
                "Invalidate only T95's false-negative observability "
                "interpretation and earn a separately preregistered corrected "
                "CPU contract; do not authorize hosted training."
            ),
            "fail": "Confirm T95 FiLM closure.",
        },
        "authority": {
            "read_only_execution": not failed,
            "corrected_cpu_contract_preregistration_after_pass": not failed,
            "hosted_training": False,
            "behavior": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
        "execution_now": {
            "optimizer_steps": 0,
            "simulator_ticks": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
    }
    value = {
        **basis,
        "failed_checks": failed,
        "preregistered_contract_sha256": canonical_sha256(basis),
    }
    OUTPUT.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T96 FiLM state-coherent audit preregistration",
                "",
                f"Status: `{value['status']}`",
                "",
                "This audit does not weaken or replace any T95 threshold. "
                "It repeats the exact 40 × 64 action-effect census using the "
                "already-established T11 state-coherent previous-action "
                "construction so the rate projection cannot manufacture a "
                "false negative.",
                "",
                "No optimizer, simulator, hosted compute, or hardware is "
                "authorized.",
                "",
                f"Contract SHA-256: "
                f"`{value['preregistered_contract_sha256']}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(value["preregistered_contract_sha256"])
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
