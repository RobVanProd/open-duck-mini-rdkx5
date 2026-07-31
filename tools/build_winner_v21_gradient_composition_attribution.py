#!/usr/bin/env python3
"""Attribute the Winner-v21 zero-update numerical HOLD and freeze its correction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RESULT = ANALYSIS / "winner_v21_predictor_preserving_joint_cpu_result.json"
CONTRACT = ANALYSIS / "winner_v21_predictor_preserving_joint_cpu_contract.json"
OUTPUT = ANALYSIS / "winner_v21_gradient_composition_attribution.json"
MARKDOWN = ANALYSIS / "WINNER_V21_GRADIENT_COMPOSITION_ATTRIBUTION_20260721.md"
SOURCES = {
    "result": RESULT,
    "contract": CONTRACT,
    "runner": ROOT / "tools/run_winner_v21_predictor_preserving_joint_cpu_contract.py",
    "mechanics": ROOT / "patches/winner_v21_predictor_preserving_joint_support.py",
    "importer": ROOT / "tools/import_winner_v21_predictor_preserving_joint_cpu_result.py",
    "builder": Path(__file__).resolve(),
}


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def build_payload() -> dict[str, Any]:
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if (
        result.get("status")
        != "HOLD_WINNER_V21_PREDICTOR_PRESERVING_JOINT_CPU_CONTRACT"
        or result.get("decision") != "DO_NOT_UPDATE_OR_TRAIN_WINNER_V21"
        or result.get("failed_checks")
        != ["combined_gradient_is_exact_sum_at_most_1e_6"]
        or sum(bool(value) for value in result.get("checks", {}).values()) != 16
        or result.get("execution", {}).get("optimizer_updates") != 0
        or contract.get("status")
        != "FROZEN_WINNER_V21_PREDICTOR_PRESERVING_JOINT_CPU_CONTRACT"
    ):
        raise ValueError("Winner-v21 numerical-HOLD source changed")
    objective = result["objective"]
    error = float(objective["combined_gradient_max_abs_error_from_sum"])
    maximum_gradient = max(float(value) for value in objective["combined_gradient_max_abs"].values())
    scale = float(objective["balance"]["predictor_scale"])
    if (
        error != 1.430511474609375e-06
        or not 0.0 < error
        or maximum_gradient <= 0.0
        or scale != 8.393629541414427e-11
        or not result["checks"]["combined_all_12_gradients_nonzero"]
        or not result["checks"]["ppo_gradient_partition_exact"]
        or not result["checks"]["predictor_gradient_partition_exact"]
        or not result["checks"]["parameters_bit_exact_unchanged"]
    ):
        raise ValueError("Winner-v21 numerical-HOLD evidence changed")
    sources = {
        name: {
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "hash_mode": "lf",
            "sha256": lf_sha256(path),
        }
        for name, path in SOURCES.items()
    }
    return {
        "schema_version": "winner_v21.gradient_composition_attribution.v1",
        "status": "PASS_WINNER_V21_GRADIENT_COMPOSITION_ATTRIBUTION",
        "decision": "PREREGISTER_EXPLICITLY_COMPOSED_TWO_UPDATE_CPU_PROOF",
        "source_hold": {
            "github_run_id": result["repository_attribution"]["github_run_id"],
            "artifact_zip_sha256": result["repository_attribution"][
                "artifact_zip_sha256"
            ],
            "failed_check": result["failed_checks"][0],
            "absolute_gradient_difference": error,
            "maximum_combined_gradient": maximum_gradient,
            "relative_to_maximum_combined_gradient": error / maximum_gradient,
            "passing_checks": 16,
            "total_checks": 17,
            "optimizer_updates": 0,
        },
        "frozen_predictor_scale": {
            **objective["balance"],
            "value": scale,
            "evaluations": 1,
            "sweep": False,
        },
        "classification": {
            "objective_or_gradient_partition_failure": False,
            "floating_accumulation_order_only": True,
            "threshold_relaxed": False,
            "source_hold_relabelled_as_pass": False,
            "rerun_of_source_contract_authorized": False,
            "flat_transport_equation_selected": False,
        },
        "correction": {
            "gradient_used_by_optimizer": "g_ppo + frozen_scale * g_predictor",
            "composition": "explicit per-leaf float32 tree composition",
            "independent_combined_autodiff_graph": False,
            "loss_for_logging": "ppo_loss + frozen_scale * predictor_loss",
            "next_proof_optimizer_updates": 2,
            "scale_recomputed_in_next_proof": False,
            "all_other_population_objective_boundary_and_abi_terms_unchanged": True,
        },
        "authority": {
            "optimizer_updates_authorized_now": 0,
            "formal_support_cells_authorized_now": 0,
            "winner_v21_training_authorized": False,
            "locomotion_training_authorized": False,
            "robot_clearance": False,
            "robot_or_rdk_access": False,
            "pass_authorizes_only": (
                "a separately hash-frozen two-update explicit-gradient CPU proof"
            ),
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
    }


def main() -> int:
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("Winner-v21 gradient attribution already exists")
    payload = build_payload()
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    hold = payload["source_hold"]
    MARKDOWN.write_text(
        "\n".join(
            [
                "# Winner-v21 gradient-composition attribution",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                f"- Frozen predictor scale: `{payload['frozen_predictor_scale']['value']}`",
                f"- Absolute / relative gradient difference: `{hold['absolute_gradient_difference']} / {hold['relative_to_maximum_combined_gradient']}`",
                "- Passing checks: `16 / 17`; optimizer updates: `0`",
                "- Threshold relaxed / source relabelled / rerun: `false / false / false`",
                "- Flat-transport equation: `not selected`",
                "",
                "The next proof composes the optimizer gradient tree explicitly from the",
                "two separately verified gradients. It does not change the loss, scale,",
                "population, action boundary, ABI, or authority boundary.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
