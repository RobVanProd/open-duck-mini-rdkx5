#!/usr/bin/env python3
"""Freeze T76's paired COM-hidden response-geometry audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "t76_com_hidden_geometry_preregistration.json"
MARKDOWN = ANALYSIS / "T76_COM_HIDDEN_GEOMETRY_PREREGISTRATION_20260728.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    value = path.resolve()
    return {
        "path": str(value),
        "bytes": value.stat().st_size,
        "sha256": sha256(value),
    }


def canonical_sha256(value: Any, hash_key: str) -> str:
    payload = dict(value)
    payload.pop(hash_key, None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def main() -> int:
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T76 preregistration")

    t71_prereg_path = (
        ANALYSIS / "t71_t67_com_hidden_causal_preregistration_v2.json"
    )
    t71_prereg = json.loads(t71_prereg_path.read_text(encoding="utf-8"))
    policies = t71_prereg["policies"]
    nominal = t71_prereg["nominal_traces"]
    shifted = t71_prereg["shifted_traces"]
    expected_keys = {
        f"{checkpoint}|{fit}|{command:.3f}"
        for checkpoint in ("T67_ENDPOINT_CORE_HALF", "T67_ENDPOINT_CORE_FINAL")
        for fit in ("p30", "p31_34")
        for command in (0.0, 0.074, 0.077, 0.080)
    }

    auditor = ROOT / "tools" / "audit_t76_com_hidden_geometry.py"
    test = ROOT / "tests" / "test_t76_com_hidden_geometry.py"
    frozen_inputs = {
        "builder": receipt(Path(__file__)),
        "auditor": receipt(auditor),
        "test": receipt(test),
        "t71_preregistration": receipt(t71_prereg_path),
        "t71_result": receipt(
            ANALYSIS / "t71_t67_com_hidden_causal_result.json"
        ),
        "t73_result": receipt(
            ANALYSIS / "t73_signed_core_mirror_condition7_result.json"
        ),
        "t75_result": receipt(
            ANALYSIS / "t75_signed_core_secant_condition7_result.json"
        ),
    }
    checks = {
        "t71_population_exact": (
            set(nominal) == expected_keys
            and set(shifted) == expected_keys
            and t71_prereg["population"]["sample_ticks"]
            == [0, 8, 16, 32, 64, 80]
        ),
        "exact_two_persistent_policies": (
            [item["checkpoint_id"] for item in policies]
            == ["T67_ENDPOINT_CORE_HALF", "T67_ENDPOINT_CORE_FINAL"]
        ),
        "all_trace_receipts_exist": all(
            Path(item["path"]).is_file()
            for population in (nominal, shifted)
            for item in population.values()
        ),
        "t71_wrong_response_classification_frozen": (
            json.loads(
                (
                    ANALYSIS / "t71_t67_com_hidden_causal_result.json"
                ).read_text(encoding="utf-8")
            )["classification"]
            == "COM_SIGNAL_PRESENT_AND_USED_CONTROL_LAW_INADEQUATE"
        ),
        "signed_core_families_closed": (
            json.loads(
                (
                    ANALYSIS / "t73_signed_core_mirror_condition7_result.json"
                ).read_text(encoding="utf-8")
            )["decision"]
            == "CLOSE_SIGNED_CORE_MIRROR"
            and json.loads(
                (
                    ANALYSIS / "t75_signed_core_secant_condition7_result.json"
                ).read_text(encoding="utf-8")
            )["decision"]
            == "CLOSE_SIGNED_CORE_SECANT_FAMILY"
        ),
        "read_only_cpu_audit_only": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T76 preregistration checks failed: {failed}")

    value: dict[str, Any] = {
        "schema_version": "open_duck.t76_com_hidden_geometry_preregistration.v1",
        "status": "PREREGISTERED_T76_COM_HIDDEN_GEOMETRY",
        "question": (
            "Is T67's paired nominal-to-torso-COM-x-negative h_out displacement "
            "a coherent, low-rank, held-out-stable axis that can earn one exact "
            "per-checkpoint adapter-output-head reflection falsifier?"
        ),
        "causal_basis": {
            "t71": (
                "The shifted plant is already represented in recurrent state "
                "and swapping that state causally changes deployed actions."
            ),
            "t73_t75": (
                "Core mirroring improved the failed boundary but neither the "
                "mirror nor fixed secant family met persistent 16/16 behavior."
            ),
            "distinct_mechanism": (
                "T76 tests the geometry seen by the frozen adapter output head; "
                "it does not extrapolate recurrent-core parameters."
            ),
            "expert_router_not_selected": (
                "The complementary T73 checkpoint cells are diagnostic only. "
                "Routing between them would merge/select checkpoints and add a "
                "250-tick response-calibration startup contract, so it cannot "
                "serve as the frozen-persistence candidate."
            ),
        },
        "population": {
            "checkpoints": [
                "T67_ENDPOINT_CORE_HALF",
                "T67_ENDPOINT_CORE_FINAL",
            ],
            "fits": ["p30", "p31_34"],
            "commands_x_m_s": [0.074, 0.077, 0.080],
            "sample_ticks": [8, 16, 32, 64, 80],
            "h_out_pairs_per_checkpoint": 30,
            "basis_rule": {
                "fit": "p30",
                "commands_x_m_s": [0.074, 0.080],
                "pairs_per_checkpoint": 10,
            },
            "heldout_rule": {
                "cells": [
                    ["p30", 0.077],
                    ["p31_34", 0.074],
                    ["p31_34", 0.077],
                    ["p31_34", 0.080],
                ],
                "pairs_per_checkpoint": 20,
            },
        },
        "geometry": {
            "delta_definition": "h_out_shifted - h_out_nominal",
            "basis_direction": (
                "leading right singular vector of the uncentered basis-delta "
                "matrix, oriented to have nonnegative dot product with the "
                "basis arithmetic-mean delta"
            ),
            "no_rank_or_threshold_search": True,
            "downstream_head_initializer": "adapter_weight",
        },
        "thresholds": {
            "minimum_basis_first_singular_energy_fraction": 0.50,
            "minimum_heldout_positive_projection_fraction": 0.80,
            "minimum_heldout_median_absolute_cosine": 0.25,
            "minimum_heldout_projected_energy_fraction": 0.20,
            "minimum_basis_mean_delta_l2": 1e-6,
            "minimum_head_axis_response_l2": 1e-3,
        },
        "decision_rule": {
            "pass": (
                "Both checkpoints independently clear every frozen geometry "
                "and output-head actionability threshold."
            ),
            "pass_decision": (
                "EARN_T77_EXACT_COM_AXIS_OUTPUT_HEAD_REFLECTION_PREREGISTRATION"
            ),
            "fail_decision": "CLOSE_COM_AXIS_OUTPUT_HEAD_REFLECTION",
            "no_behavior_run": True,
            "no_optimizer_step": True,
            "no_hosted_run_earned": True,
        },
        "policies": policies,
        "nominal_traces": nominal,
        "shifted_traces": shifted,
        "frozen_inputs": frozen_inputs,
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "new_simulator_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_read_only_geometry_audit": True,
            "build_or_evaluate_transformed_policy": False,
            "training": False,
            "colab": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(
        value, "preregistered_contract_sha256"
    )
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T76 COM-hidden response-geometry preregistration",
                "",
                f"- Status: `{value['status']}`",
                (
                    "- Question: Does each persistent T67 endpoint expose a "
                    "held-out-stable, rank-one COM response axis at `h_out`?"
                ),
                "- Formal behavior / optimizer / Colab / robot: `0/0/0/0`",
                "",
                "A pass earns only an exact output-head transform "
                "preregistration. It does not earn behavior or hosted training.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"contract={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
