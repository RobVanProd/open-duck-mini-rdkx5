#!/usr/bin/env python3
"""Freeze T97's full-population live-hidden gate as a T98 asset."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs" / "analysis"
sys.path.insert(0, str(TOOLS))

import audit_t97_hidden_gate as t97  # noqa: E402


T97_RESULT = ANALYSIS / "t97_hidden_gate_result.json"
OUTPUT = ANALYSIS / "t98_hidden_gate_asset.json"
MARKDOWN = ANALYSIS / "T98_HIDDEN_GATE_ASSET_20260728.md"


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def validate_t97_result() -> dict[str, Any]:
    value = json.loads(T97_RESULT.read_text(encoding="utf-8"))
    basis = {key: item for key, item in value.items() if key != "result_sha256"}
    if (
        value.get("status") != "PASS_T97_HIDDEN_GATE_FALSIFIER"
        or value.get("failed_checks")
        or value.get("decision")
        != "EARN_T98_HIDDEN_GATED_EXPERT_CPU_CONTRACT_PREREGISTRATION_ONLY"
        or canonical_sha256(basis) != value.get("result_sha256")
    ):
        raise RuntimeError("T97 passing result identity changed")
    return value


def source_population() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    prereg = t97.load_preregistration()
    ticks = {int(value) for value in prereg["population"]["ticks"]}
    rows: list[dict[str, Any]] = []
    for item in prereg["traces"]:
        rows.extend(
            t97.read_selected_rows(
                item,
                ticks,
                int(prereg["population"]["labels"][item["population"]]),
            )
        )
    return prereg, rows


def population_sha256(rows: list[dict[str, Any]]) -> str:
    payload = [
        {
            **{key: value for key, value in row.items() if key != "hidden"},
            "hidden": np.asarray(row["hidden"], dtype="<f8").tolist(),
        }
        for row in rows
    ]
    return canonical_sha256(payload)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--read-only-authorized", action="store_true")
    args = parser.parse_args()
    if not args.read_only_authorized:
        raise PermissionError("T98 gate derivation requires --read-only-authorized")
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T98 asset: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T98 gate derivation requires a clean worktree")

    t97_result = validate_t97_result()
    prereg, rows = source_population()
    model = t97.fit_ridge(rows)
    predictions = t97.predict(model, rows)
    aggregate = t97.metrics(predictions)
    tick_metrics = {
        str(tick): t97.metrics(
            row for row in predictions if int(row["tick"]) == tick
        )
        for tick in sorted({int(row["tick"]) for row in predictions})
    }
    positive_scores = [
        float(row["score"]) for row in predictions if row["label"] == 1
    ]
    negative_scores = [
        float(row["score"]) for row in predictions if row["label"] == -1
    ]
    checks = {
        "t97_pass_identity_exact": True,
        "population_exact": (
            len(rows) == prereg["population"]["sample_count"] == 72
            and sum(row["label"] == 1 for row in rows) == 36
            and sum(row["label"] == -1 for row in rows) == 36
        ),
        "model_shapes_exact": (
            model["mean"].shape == (64,)
            and model["scale"].shape == (64,)
            and model["weights"].shape == (65,)
        ),
        "model_finite": all(
            np.all(np.isfinite(value)) for value in model.values()
        ),
        "scale_positive": bool(np.all(model["scale"] > 0.0)),
        "full_population_classification_exact": (
            aggregate["balanced_accuracy"] == 1.0
            and all(
                item["balanced_accuracy"] == 1.0
                for item in tick_metrics.values()
            )
        ),
        "strict_zero_threshold_margin": (
            min(positive_scores) > 0.0 and max(negative_scores) < 0.0
        ),
        "optimizer_simulator_hosted_hardware_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T98 gate asset checks failed: {failed}")

    asset: dict[str, Any] = {
        "schema_version": "open_duck.t98_hidden_gate_asset.v1",
        "status": "FROZEN_T98_HIDDEN_GATE_ASSET",
        "derivation": {
            "method": (
                "full-population standardized linear ridge; identity penalty "
                "on 64 coefficients; unpenalized intercept"
            ),
            "ridge_penalty": 1.0,
            "decision": "negative_com_if_score_greater_than_or_equal_to_zero",
            "feature": "policy_state_output.h_out[0]",
            "source_ticks": sorted(
                int(value) for value in prereg["population"]["ticks"]
            ),
            "source_population_sha256": population_sha256(rows),
            "t97_preregistered_contract_sha256": prereg[
                "preregistered_contract_sha256"
            ],
            "t97_result_sha256": t97_result["result_sha256"],
        },
        "model": {
            "mean": model["mean"].astype(np.float64).tolist(),
            "scale": model["scale"].astype(np.float64).tolist(),
            "coefficient": model["weights"][:-1].astype(np.float64).tolist(),
            "intercept": float(model["weights"][-1]),
        },
        "training_population": {
            "metrics": aggregate,
            "tick_metrics": tick_metrics,
            "minimum_negative_com_score": min(positive_scores),
            "maximum_nominal_score": max(negative_scores),
            "minimum_absolute_score": min(
                abs(float(row["score"])) for row in predictions
            ),
            "sample_count": len(rows),
        },
        "constraints": {
            "fixed_not_trainable": True,
            "new_policy_input": False,
            "new_runtime_sensor": False,
            "manual_measurement": False,
            "policy_abi_change": False,
            "scalar_sweep": False,
        },
        "checks": {name: bool(value) for name, value in checks.items()},
        "failed_checks": failed,
        "authority": {
            "t98_cpu_contract_preregistration": True,
            "optimizer_or_simulator": False,
            "hosted_training": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    asset["asset_sha256"] = canonical_sha256(asset)
    OUTPUT.write_text(
        json.dumps(asset, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T98 frozen live-hidden gate asset",
                "",
                f"- Status: `{asset['status']}`",
                (
                    "- Population balanced accuracy: "
                    f"`{aggregate['balanced_accuracy']:.6f}`"
                ),
                (
                    "- Minimum negative-COM / maximum nominal score: "
                    f"`{min(positive_scores):.6f} / "
                    f"{max(negative_scores):.6f}`"
                ),
                (
                    "- Minimum absolute zero-threshold margin: "
                    f"`{asset['training_population']['minimum_absolute_score']:.6f}`"
                ),
                "- New policy input / runtime sensor / manual measurement: `false / false / false`",
                "- Optimizer / simulator / hosted / robot: `0 / 0 / 0 / 0`",
                f"- Asset SHA-256: `{asset['asset_sha256']}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(asset["status"])
    print(f"asset_sha256={asset['asset_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
