#!/usr/bin/env python3
"""Audit whether oracle corrections are linearly separable in deployable state."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""
os.environ["ROCR_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"

from flax.training import orbax_utils
import numpy as np
from orbax import checkpoint as ocp


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREG = (
    ANALYSIS / "winner_v130_oracle_correction_feature_preregistration.json"
)
V129_FORMAL = ANALYSIS / "winner_v129_oracle_teacher_formal_cpu_result.json"
OUTPUT = ANALYSIS / "winner_v130_oracle_correction_feature_audit.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V130_ORACLE_CORRECTION_FEATURE_AUDIT_20260724.md"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(
        candidate for candidate in path.rglob("*") if candidate.is_file()
    ):
        digest.update(item.relative_to(path).as_posix().encode())
        digest.update(b"\0")
        with item.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        digest.update(b"\0")
    return digest.hexdigest()


def restore_like(path: Path, template):
    checkpointer = ocp.PyTreeCheckpointer()
    return checkpointer.restore(
        str(path),
        item=template,
        restore_args=orbax_utils.restore_args_from_target(template),
    )


def load_rows(run_root: Path) -> dict[str, np.ndarray | list[str]]:
    rows = []
    for trace_path in sorted((run_root / "traces").glob("*_final_*.jsonl")):
        records = [
            json.loads(line)
            for line in trace_path.read_text(encoding="utf-8").splitlines()
            if line
        ]
        if len(records) != 600:
            raise ValueError(f"incomplete V130 trace: {trace_path}")
        plant = "p31_34" if "p31_34" in trace_path.name else "p30"
        for record in records:
            oracle = record["exact_torque_oracle"]
            corrected = bool(oracle["projected_joint_indices"])
            target = np.asarray(oracle["final_action"], dtype=np.float64)
            base = np.asarray(
                record["policy_base_action"], dtype=np.float64
            )
            rows.append(
                {
                    "obs": np.asarray(
                        record["obs_state"], dtype=np.float64
                    ),
                    "h_in": np.asarray(
                        record["policy_state_input"]["h_in"][0],
                        dtype=np.float64,
                    ),
                    "h_out": np.asarray(
                        record["policy_state_output"]["h_out"][0],
                        dtype=np.float64,
                    ),
                    "correction": target - base if corrected else target * 0.0,
                    "corrected": corrected,
                    "plant": plant,
                    "trace": trace_path.name,
                }
            )
    if len(rows) != 4_800:
        raise ValueError("V130 requires 4,800 final-teacher rows")
    return {
        "obs": np.stack([row["obs"] for row in rows]),
        "h_in": np.stack([row["h_in"] for row in rows]),
        "h_out": np.stack([row["h_out"] for row in rows]),
        "correction": np.stack([row["correction"] for row in rows]),
        "corrected": np.asarray(
            [row["corrected"] for row in rows], dtype=np.bool_
        ),
        "plant": np.asarray([row["plant"] for row in rows]),
        "trace": [str(row["trace"]) for row in rows],
    }


def fit_probe(
    train_x: np.ndarray,
    train_y: np.ndarray,
    train_weights: np.ndarray,
    test_x: np.ndarray,
    test_y: np.ndarray,
    test_corrected: np.ndarray,
) -> dict[str, float | int]:
    mean = np.mean(train_x, axis=0)
    std = np.std(train_x, axis=0)
    active = std > 1.0e-9
    train = (train_x[:, active] - mean[active]) / std[active]
    test = (test_x[:, active] - mean[active]) / std[active]
    train = np.concatenate(
        [train, np.ones((train.shape[0], 1), dtype=np.float64)], axis=1
    )
    test = np.concatenate(
        [test, np.ones((test.shape[0], 1), dtype=np.float64)], axis=1
    )
    root_weight = np.sqrt(train_weights)[:, None]
    coefficients, _, rank, singular = np.linalg.lstsq(
        train * root_weight,
        train_y * root_weight,
        rcond=None,
    )
    prediction = test @ coefficients
    error = prediction - test_y
    row_mse = np.mean(np.square(error), axis=1)
    target_row_mse = np.mean(np.square(test_y), axis=1)
    corrected_mse = float(np.mean(row_mse[test_corrected]))
    preservation_mse = float(np.mean(row_mse[~test_corrected]))
    baseline_corrected_mse = float(
        np.mean(target_row_mse[test_corrected])
    )
    corrected_ratio = (
        corrected_mse / baseline_corrected_mse
        if baseline_corrected_mse > 0.0
        else float("inf")
    )
    preservation_ratio = (
        preservation_mse / baseline_corrected_mse
        if baseline_corrected_mse > 0.0
        else float("inf")
    )
    return {
        "active_features": int(np.sum(active)),
        "rank": int(rank),
        "smallest_singular": float(np.min(singular)),
        "coefficient_l2": float(np.linalg.norm(coefficients)),
        "corrected_mse": corrected_mse,
        "preservation_mse": preservation_mse,
        "baseline_corrected_mse": baseline_corrected_mse,
        "corrected_ratio_to_zero_predictor": corrected_ratio,
        "preservation_ratio_to_corrected_baseline": preservation_ratio,
        "prediction_linf": float(np.max(np.abs(prediction))),
        "error_linf": float(np.max(np.abs(error))),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--oracle-run-root", type=Path, required=True)
    parser.add_argument("--source-checkpoint", type=Path, required=True)
    parser.add_argument("--cpu-template", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V130: {path}")
    run_root = args.oracle_run_root.resolve()
    source = args.source_checkpoint.resolve()
    cpu_template = args.cpu_template.resolve()
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    formal = json.loads(V129_FORMAL.read_text(encoding="utf-8"))
    observed_hashes = {
        "v129_formal_result": sha256(V129_FORMAL),
        "audit_runner": sha256(Path(__file__).resolve()),
        "source_checkpoint": directory_sha256(source),
        "cpu_template": directory_sha256(cpu_template),
    }
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V130_ORACLE_CORRECTION_FEATURE_AUDIT"
        or prereg.get("failed_checks") != []
        or prereg.get("input_hashes") != observed_hashes
        or formal.get("decision")
        != "CLOSE_V129_DISTILLATION_WITHOUT_BEHAVIOR"
    ):
        raise ValueError("V130 preregistration changed")

    rows = load_rows(run_root)
    corrected = rows["corrected"]
    if int(np.sum(corrected)) != 14:
        raise ValueError("V130 requires exactly 14 oracle-corrected rows")
    weights = np.where(
        corrected, float(np.sum(~corrected) / np.sum(corrected)), 1.0
    )
    checkpointer = ocp.PyTreeCheckpointer()
    template = checkpointer.restore(str(cpu_template))
    source_tree = restore_like(source, template)
    normalizer = source_tree[0]
    normalized_obs = (
        rows["obs"] - np.asarray(normalizer["mean"]["state"])
    ) / np.asarray(normalizer["std"]["state"])
    features = {
        "current_hidden": rows["h_out"],
        "normalized_obs": normalized_obs,
        "normalized_obs_plus_h_in": np.concatenate(
            [normalized_obs, rows["h_in"]], axis=1
        ),
    }
    combined = {
        name: fit_probe(
            value,
            rows["correction"],
            weights,
            value,
            rows["correction"],
            corrected,
        )
        for name, value in features.items()
    }
    cross_plant = {}
    for train_plant, test_plant in (("p30", "p31_34"), ("p31_34", "p30")):
        train = rows["plant"] == train_plant
        test = rows["plant"] == test_plant
        key = f"{train_plant}_to_{test_plant}"
        cross_plant[key] = fit_probe(
            features["normalized_obs_plus_h_in"][train],
            rows["correction"][train],
            weights[train],
            features["normalized_obs_plus_h_in"][test],
            rows["correction"][test],
            corrected[test],
        )
    hidden = combined["current_hidden"]
    state = combined["normalized_obs_plus_h_in"]
    checks = {
        "cpu_only_read_only_audit": True,
        "v129_formal_closed_without_behavior": (
            formal.get("status")
            == "HOLD_WINNER_V129_ORACLE_TEACHER_FORMAL_CPU_DISTILLATION"
            and formal.get("checks", {}).get("formal_behavior_cells_zero")
            is True
        ),
        "dataset_exact": (
            rows["obs"].shape == (4_800, 115)
            and rows["h_in"].shape == (4_800, 64)
            and rows["h_out"].shape == (4_800, 64)
            and int(np.sum(corrected)) == 14
        ),
        "all_probe_values_finite": all(
            math.isfinite(float(value))
            for group in (*combined.values(), *cross_plant.values())
            for value in group.values()
        ),
        "state_probe_beats_hidden_by_four_x": (
            state["corrected_mse"] + state["preservation_mse"]
            <= 0.25
            * (hidden["corrected_mse"] + hidden["preservation_mse"])
        ),
        "state_corrected_error_at_most_quarter_baseline": (
            state["corrected_ratio_to_zero_predictor"] <= 0.25
        ),
        "state_preservation_error_at_most_one_percent_baseline": (
            state["preservation_ratio_to_corrected_baseline"] <= 0.01
        ),
        "p30_to_p31_improves_corrected_rows": (
            cross_plant["p30_to_p31_34"][
                "corrected_ratio_to_zero_predictor"
            ]
            < 1.0
        ),
        "p31_to_p30_improves_corrected_rows": (
            cross_plant["p31_34_to_p30"][
                "corrected_ratio_to_zero_predictor"
            ]
            < 1.0
        ),
        "both_cross_plant_preservation_below_one_percent": all(
            row["preservation_ratio_to_corrected_baseline"] <= 0.01
            for row in cross_plant.values()
        ),
        "no_training_behavior_or_hosted_compute": True,
    }
    mechanism_checks = (
        "state_probe_beats_hidden_by_four_x",
        "state_corrected_error_at_most_quarter_baseline",
        "state_preservation_error_at_most_one_percent_baseline",
        "p30_to_p31_improves_corrected_rows",
        "p31_to_p30_improves_corrected_rows",
        "both_cross_plant_preservation_below_one_percent",
    )
    validity_checks = tuple(
        name for name in checks if name not in mechanism_checks
    )
    failed_validity = sorted(
        name for name in validity_checks if not checks[name]
    )
    failed_mechanism = sorted(
        name for name in mechanism_checks if not checks[name]
    )
    status = (
        "PASS_WINNER_V130_ORACLE_CORRECTION_FEATURE_AUDIT"
        if not failed_validity
        else "INVALID_WINNER_V130_ORACLE_CORRECTION_FEATURE_AUDIT"
    )
    decision = (
        "EARN_ONE_OBSERVATION_RESIDUAL_CPU_CONTRACT"
        if not failed_validity and not failed_mechanism
        else "NO_OBSERVATION_RESIDUAL_TRAINING"
    )
    payload = {
        "schema_version": (
            "winner_v130.oracle_correction_feature_audit.v1"
        ),
        "status": status,
        "failed_validity_checks": failed_validity,
        "failed_mechanism_checks": failed_mechanism,
        "checks": checks,
        "input_hashes": observed_hashes,
        "dataset": {
            "rows": 4_800,
            "corrected_rows": 14,
            "preservation_rows": 4_786,
            "target": (
                "explicit oracle final action minus V121-final base action "
                "on projected rows; exact zero elsewhere"
            ),
            "fit": (
                "float64 class-balanced unregularized least squares; "
                "no fitted scalar or behavior selection"
            ),
        },
        "combined_fit": combined,
        "cross_plant_fit": cross_plant,
        "decision": decision,
        "interpretation": (
            "This falsifies only a linear correction readout over the frozen "
            "deployable state. It does not prove that a nonlinear gait-level "
            "policy cannot exist."
        ),
        "authority": {
            "observation_residual_cpu_contract": (
                decision == "EARN_ONE_OBSERVATION_RESIDUAL_CPU_CONTRACT"
            ),
            "formal_training": False,
            "hosted_training": False,
            "behavior_evaluation": False,
            "full_matrix": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V130 oracle-correction feature audit\n\n"
        f"- Status: `{status}`\n"
        f"- Decision: `{decision}`\n"
        f"- Failed mechanism checks: `{failed_mechanism}`\n"
        "- No training, behavior evaluation, Colab, RDK, torque, or motion "
        "occurred.\n",
        encoding="utf-8",
    )
    print(status)
    print(decision)
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed_validity else 1


if __name__ == "__main__":
    raise SystemExit(main())
