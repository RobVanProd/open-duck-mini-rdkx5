#!/usr/bin/env python3
"""Preregister the Winner-v88 flat-transport representation diagnostic."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v88_flat_transport_representation_preregistration.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V88_FLAT_TRANSPORT_REPRESENTATION_PREREGISTRATION_20260722.md"
)
V87_RESULT = ANALYSIS / "winner_v87_pitch_head_linear_feasibility_result.json"
V87_RESULT_SHA256 = "c54bbad33bffec85d7ddafb6ccb45231f83929eadae8c5eb2fb9edb1f94298ac"
FAMILIES = (
    "current_observation",
    "flat_transport_basis",
    "hidden_plus_flat_transport",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


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
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v88 contract: {path}")
    source = json.loads(V87_RESULT.read_text(encoding="utf-8"))
    if (
        sha256(V87_RESULT) != V87_RESULT_SHA256
        or source.get("classification")
        != "FROZEN_HIDDEN_LINEAR_PITCH_HEAD_INSUFFICIENT"
        or source.get("decision") != "PREREGISTER_RECURRENT_REPRESENTATION_DIAGNOSTIC"
        or source.get("next_source_checkpoint_for_mechanism_proof") is not None
        or any(row.get("endpoint_feasible") for row in source.get("endpoints", []))
        or source.get("authority", {}).get("robot_clearance") is not False
    ):
        raise ValueError("Winner-v88 source result changed")
    source_paths = {
        "builder": Path(
            "tools/build_winner_v88_flat_transport_representation_preregistration.py"
        ),
        "runner": Path("tools/run_winner_v88_flat_transport_representation.py"),
        "tests": Path("tests/test_winner_v88_flat_transport_representation.py"),
        "v87_result": V87_RESULT.relative_to(ROOT),
        "v87_runner": Path("tools/run_winner_v87_pitch_head_linear_feasibility.py"),
        "v87b_correction": Path(
            "outputs/analysis/winner_v87b_teacher_population_correction.json"
        ),
        "recurrent_policy": Path("patches/winner_v29_prefix_right_pitch_anchor.py"),
    }
    sources = {
        name: {"path": path.as_posix(), "hash_mode": "lf", "sha256": lf_sha256(ROOT / path)}
        for name, path in source_paths.items()
    }
    value = {
        "schema_version": "winner_v88.flat_transport_representation_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V88_FLAT_TRANSPORT_REPRESENTATION_DIAGNOSTIC",
        "decision": "AUTHORIZE_ONE_READ_ONLY_TWO_ENDPOINT_FEATURE_FAMILY_AUDIT_ONLY",
        "question": (
            "Does the causal uniform-history component from C_n expose a "
            "heldout-transferable pitch-teacher signal that is absent from the "
            "frozen recurrent hidden state?"
        ),
        "equation_boundary": {
            "provided_equation": "K_n,L = rho^L I_n + q(1-rho^L) C_n",
            "c_n_final_row": "(1/n, ..., 1/n)",
            "tested_component": (
                "the exact causal prefix mean C_n x alongside the identity/current "
                "observation x as separate linear-probe basis columns"
            ),
            "rho_or_q_selected_or_searched": False,
            "policy_architecture_changed": False,
        },
        "frozen_source": {
            "v87_result_sha256": V87_RESULT_SHA256,
            "checkpoint_labels_updates": {"half": 705, "final": 755},
            "source_mse_by_checkpoint": {
                row["label"]: row["source_bounded_pitch_error"]["mse"]
                for row in source["endpoints"]
            },
            "training_population_episodes": 80,
            "selected_teacher_configurations": 12,
            "selected_teacher_episodes_per_checkpoint": 24,
            "pitch_indices": [2, 3, 4, 11, 12, 13],
        },
        "feature_families": {
            "current_observation": "obs_t[115]",
            "flat_transport_basis": "concat(obs_t[115], causal_mean(obs_0..obs_t)[115])",
            "hidden_plus_flat_transport": (
                "concat(hidden_t[64], obs_t[115], causal_mean(obs_0..obs_t)[115])"
            ),
        },
        "fit": {
            "families": list(FAMILIES),
            "training_only_standardization": (
                "per-column float32 mean/std from each fit's training rows; "
                "std below 1e-6 maps to 1"
            ),
            "intercept": True,
            "target": "float64 arctanh of six static raw teacher actions",
            "solver": "numpy.linalg.lstsq",
            "rcond": None,
            "coefficients_cast_to_float32_before_scoring": True,
            "cross_validation": "12 leave-one-configuration-out folds per family/endpoint",
            "hyperparameter_or_rho_q_search": False,
            "total_least_squares_fits": 78,
        },
        "classification_rule": {
            "family_viable": (
                "full-fit MSE and aggregate leave-one-configuration-out MSE are "
                "both strictly below the unchanged source-policy MSE"
            ),
            "flat_transport_selected_for_endpoint": (
                "flat_transport_basis is viable and its heldout MSE is strictly "
                "below current_observation heldout MSE"
            ),
            "endpoint_family_priority": (
                "flat_transport_basis if selected; else current_observation if "
                "viable; else hidden_plus_flat_transport if viable; else none"
            ),
            "checkpoint_priority": "half, then final",
            "result_authority": (
                "one separately preregistered CPU mechanism proof for the selected "
                "family only; no policy artifact is written here"
            ),
        },
        "execution_now": {
            "stage2_rollout_episodes": 0,
            "least_squares_fits": 0,
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "snapshot_or_onnx_writes": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "diagnostic_authorized": True,
            "equation_policy_mechanism_authorized_now": False,
            "training_authorized_now": False,
            "support_gate_authorized_now": False,
            "checkpoint_selection_authorized": False,
            "deployment_authorized": False,
            "gate5_authorized": False,
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        },
    }
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v88 flat-transport representation preregistration",
                "",
                "- Source: V87 frozen-hidden linear head is insufficient",
                "- Feature families: current observation / identity + causal mean / hidden + identity + causal mean",
                "- Equation use: diagnostic `I_n` and final-row `C_n` basis only",
                "- `rho`, `q`, architecture changes, or coefficient search: none",
                "- Validation: 12 leave-one-configuration-out folds per family/endpoint",
                "- Optimizer updates / support cells / policy artifacts / robot access: `0 / 0 / 0 / 0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
