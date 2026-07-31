#!/usr/bin/env python3
"""Attribute why the first Winner-v13 Stage-1 decision is invalid."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RESULT = ANALYSIS / "winner_v13_normalized_response_stage1_result.json"
OUTPUT = ANALYSIS / "winner_v13_normalized_response_stage1_invalid_attribution.json"
MARKDOWN = ANALYSIS / "WINNER_V13_NORMALIZED_RESPONSE_STAGE1_INVALID_ATTRIBUTION_20260721.md"
SOURCES = {
    "builder": Path(
        "tools/build_winner_v13_normalized_response_stage1_invalid_attribution.py"
    ),
    "importer": Path("tools/import_winner_v13_normalized_response_stage1.py"),
    "import_tests": Path(
        "tests/test_winner_v13_normalized_response_stage1_import.py"
    ),
    "raw_import": Path(
        "outputs/analysis/winner_v13_normalized_response_stage1_result.json"
    ),
    "preregistration": Path(
        "outputs/analysis/winner_v13_normalized_response_stage1_preregistration.json"
    ),
    "runner": Path("tools/run_winner_v13_normalized_response_stage1.py"),
    "training_primitives": Path(
        "patches/winner_v13_normalized_calibrator_training.py"
    ),
}


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate_selected_failure(value: dict[str, Any]) -> None:
    if (
        value.get("status") != "HOLD_WINNER_V13_NORMALIZED_RESPONSE_STAGE1"
        or value.get("decision") != "DO_NOT_TRAIN_SUPPORT_CONTROLLER"
        or value.get("failed_checks") != ["both_checkpoints_pass_heldout_gate"]
        or value.get("execution", {}).get("stage1_optimizer_updates") != 100
        or value.get("execution", {}).get("stage2_optimizer_updates") != 0
        or value.get("execution", {}).get("robot_or_rdk_access") != 0
    ):
        raise ValueError("Winner-v13 Stage-1 failure selection changed")
    checkpoints = value.get("checkpoint_results", [])
    if [row.get("label") for row in checkpoints] != ["half", "final"]:
        raise ValueError("Winner-v13 Stage-1 checkpoints changed")
    expected_failure = [
        "checker_onnx_action_exact_zero",
        "checker_onnx_hidden_at_most_1e_7",
    ]
    scientific = {
        "exact_32_heldout_cells",
        "heldout_repeat_bit_exact",
        "learned_prediction_beats_constant_per_plant",
        "all_16_plant_contexts_separate",
        "deployable_onnx_abi_exact",
        "deployable_onnx_training_only_tensors_absent",
        "deployable_onnx_chain_at_most_1e_7",
    }
    for row in checkpoints:
        if row.get("failed_checks") != expected_failure or not all(
            row.get("checks", {}).get(name) is True for name in scientific
        ):
            raise ValueError("Winner-v13 Stage-1 failure mechanism changed")
        if row.get("checker_onnx_hidden_max_abs_error") != 3.5762786865234375e-07:
            raise ValueError("Winner-v13 Stage-1 checker error changed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite invalid attribution: {path}")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    validate_selected_failure(result)
    sources = {
        name: {
            "path": str(path).replace("\\", "/"),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    checkpoints = result["checkpoint_results"]
    payload = {
        "schema_version": "winner_v13.normalized_response_stage1_invalid_attribution.v1",
        "status": "INVALID_WINNER_V13_STAGE1_DECISION_CONTRACT",
        "decision": "DO_NOT_ADVANCE_REVALIDATE_CORRECTED_CHECKER",
        "attribution": {
            "action_checker": (
                "The checker fed a nonzero externally realized previous_action into a "
                "zero-head graph and incorrectly required exact-zero output. The graph's "
                "frozen slew projection must instead produce the JAX-reference bounded "
                "step toward zero."
            ),
            "hidden_checker": (
                "The checker compared an ONNX recurrent chain against an independently "
                "accumulated JAX chain at a one-step 1e-7 threshold. Backend differences "
                "accumulated to 3.5762786865234375e-7, while the established paired-chain "
                "graph contract passed at 8.731149137020111e-11."
            ),
            "learning_rate_declaration": (
                "The preregistration declared 0.0003, while the source-bound runner used "
                "v13.STAGE1_LEARNING_RATE=0.0001. The mismatch invalidates advancement "
                "even though the executed code and artifacts are deterministic."
            ),
        },
        "non_authorizing_observation": {
            "both_checkpoints_pass_prediction_per_plant": all(
                row["checks"]["learned_prediction_beats_constant_per_plant"]
                for row in checkpoints
            ),
            "both_checkpoints_separate_all_16_plant_pairs": all(
                row["checks"]["all_16_plant_contexts_separate"]
                for row in checkpoints
            ),
            "both_checkpoints_repeat_bit_exact": all(
                row["checks"]["heldout_repeat_bit_exact"] for row in checkpoints
            ),
            "half_final_training_loss": [
                result["metrics"][49]["loss"],
                result["metrics"][99]["loss"],
            ],
            "half_final_standard_graph_chain_error": [
                row["graph_contract"]["jax_onnx_max_abs_error"]
                for row in checkpoints
            ],
        },
        "required_correction": {
            "learning_rate": 0.0001,
            "action_check": (
                "compare every ONNX action/output/state against networks.calibrator_step "
                "using the identical observation, externally realized previous_action, "
                "and identical h_in"
            ),
            "hidden_check": "same-input one-step JAX/ONNX maximum absolute error <=1e-7",
            "cpu_contract_before_rerun": True,
            "fresh_preregistration_and_fresh_run_required": True,
        },
        "execution": {
            "additional_optimizer_updates": 0,
            "stage2_optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "support_controller_training_authorized": False,
            "pass_authorizes_only": "a corrected checker CPU contract and fresh preregistration",
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
                "# Winner-v13 Stage-1 invalid-decision attribution",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Training completed: `100` updates; additional training here: `0`",
                "- Stage-2 / locomotion / robot access: `0 / 0 / 0`",
                "",
                "The prediction, plant-separation, repeatability, and standard ONNX",
                "checks passed at half and final, but the decision is not promotable.",
                "The action checker ignored the inherited slew projection, the hidden",
                "checker accumulated independent backend state, and the declared learning",
                "rate (`3e-4`) disagreed with the executed frozen constant (`1e-4`).",
                "A corrected zero-cell checker contract and a fresh preregistered run are",
                "required before any support-controller training may be considered.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
