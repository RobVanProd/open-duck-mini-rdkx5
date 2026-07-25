#!/usr/bin/env python3
"""Audit V131 two-fit traces as a robust V132 teacher dataset."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"

from flax.training import orbax_utils
import numpy as np
from orbax import checkpoint as ocp


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from audit_winner_v130_oracle_correction_feature_separability import (  # noqa: E402
    fit_probe,
)


ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v132_robust_teacher_dataset_preregistration.json"
V131_RESULT = ANALYSIS / "winner_v131_two_fit_oracle_behavior_result.json"
OUTPUT = ANALYSIS / "winner_v132_robust_teacher_dataset_audit.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V132_ROBUST_TEACHER_DATASET_AUDIT_20260724.md"
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


def load_rows(run_root: Path) -> dict:
    rows = []
    manifest = []
    for trace_path in sorted((run_root / "traces").glob("*_final_*.jsonl")):
        records = [
            json.loads(line)
            for line in trace_path.read_text(encoding="utf-8").splitlines()
            if line
        ]
        if len(records) != 600:
            raise ValueError(f"incomplete V132 trace: {trace_path}")
        plant = "p31_34" if "p31_34" in trace_path.name else "p30"
        manifest.append(
            {
                "name": trace_path.name,
                "sha256": sha256(trace_path),
                "rows": len(records),
            }
        )
        for record in records:
            oracle = record["exact_torque_oracle"]
            projected_joints = tuple(
                int(value) for value in oracle["projected_joint_indices"]
            )
            corrected = bool(projected_joints)
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
                    "projected_joints": projected_joints,
                    "plant": plant,
                    "command": float(record["command"][0]),
                    "tick": int(record["tick"]),
                    "robust_safe": bool(
                        oracle.get("robust_safe", not corrected)
                    ),
                }
            )
    if len(rows) != 4_800 or len(manifest) != 8:
        raise ValueError("V132 requires exactly 8x600 final-teacher rows")
    return {
        "obs": np.stack([row["obs"] for row in rows]),
        "h_in": np.stack([row["h_in"] for row in rows]),
        "h_out": np.stack([row["h_out"] for row in rows]),
        "correction": np.stack([row["correction"] for row in rows]),
        "corrected": np.asarray(
            [row["corrected"] for row in rows], dtype=np.bool_
        ),
        "plant": np.asarray([row["plant"] for row in rows]),
        "command": np.asarray([row["command"] for row in rows]),
        "tick": np.asarray([row["tick"] for row in rows]),
        "robust_safe": np.asarray(
            [row["robust_safe"] for row in rows], dtype=np.bool_
        ),
        "projected_joint_events": sum(
            len(row["projected_joints"]) for row in rows
        ),
        "manifest": manifest,
    }


def qualifies(
    combined: dict,
    cross: dict[str, dict],
) -> bool:
    return (
        combined["corrected_ratio_to_zero_predictor"] <= 0.25
        and combined["preservation_ratio_to_corrected_baseline"] <= 0.01
        and all(
            row["corrected_ratio_to_zero_predictor"] < 1.0
            and row["preservation_ratio_to_corrected_baseline"] <= 0.01
            for row in cross.values()
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--source-checkpoint", type=Path, required=True)
    parser.add_argument("--cpu-template", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V132: {path}")
    run_root = args.run_root.resolve()
    source = args.source_checkpoint.resolve()
    cpu_template = args.cpu_template.resolve()
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    v131 = json.loads(V131_RESULT.read_text(encoding="utf-8"))
    observed_hashes = {
        "v131_behavior_result": sha256(V131_RESULT),
        "audit_runner": sha256(Path(__file__).resolve()),
        "source_checkpoint": directory_sha256(source),
        "cpu_template": directory_sha256(cpu_template),
    }
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V132_ROBUST_TEACHER_DATASET_AUDIT"
        or prereg.get("failed_checks") != []
        or prereg.get("input_hashes") != observed_hashes
        or v131.get("decision")
        != "EARN_ONE_V132_ROBUST_TEACHER_DATASET_AUDIT"
    ):
        raise ValueError("V132 preregistration changed")
    rows = load_rows(run_root)
    corrected = rows["corrected"]
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
    for feature_name, feature in features.items():
        cross_plant[feature_name] = {}
        for train_plant, test_plant in (
            ("p30", "p31_34"),
            ("p31_34", "p30"),
        ):
            train = rows["plant"] == train_plant
            test = rows["plant"] == test_plant
            cross_plant[feature_name][
                f"{train_plant}_to_{test_plant}"
            ] = fit_probe(
                feature[train],
                rows["correction"][train],
                weights[train],
                feature[test],
                rows["correction"][test],
                corrected[test],
            )
    hidden_qualifies = qualifies(
        combined["current_hidden"], cross_plant["current_hidden"]
    )
    state_qualifies = qualifies(
        combined["normalized_obs_plus_h_in"],
        cross_plant["normalized_obs_plus_h_in"],
    ) and (
        combined["normalized_obs_plus_h_in"]["corrected_mse"]
        + combined["normalized_obs_plus_h_in"]["preservation_mse"]
        <= 0.25
        * (
            combined["current_hidden"]["corrected_mse"]
            + combined["current_hidden"]["preservation_mse"]
        )
    )
    checks = {
        "v131_behavior_green_8_of_8": (
            v131.get("status")
            == "PASS_WINNER_V131_TWO_FIT_ORACLE_BEHAVIOR_VALID_RESULT"
            and v131.get("summary", {}).get("passing_cells") == 8
            and v131.get("summary", {}).get("robust_safe_rows") == 3_600
            and v131.get("summary", {}).get("empty_intersection_events") == 0
        ),
        "dataset_exact_4800": (
            rows["obs"].shape == (4_800, 115)
            and len(rows["manifest"]) == 8
            and set(rows["command"].tolist())
            == {0.0, 0.074, 0.077, 0.08}
            and set(rows["plant"].tolist()) == {"p30", "p31_34"}
        ),
        "projected_joint_event_count_exact": (
            rows["projected_joint_events"] == 45
        ),
        "corrected_rows_nonzero": 0 < int(np.sum(corrected)) <= 45,
        "all_moving_rows_robust_safe": bool(
            np.all(rows["robust_safe"][rows["command"] >= 0.01])
        ),
        "all_probe_values_finite": all(
            math.isfinite(float(value))
            for group in (
                *combined.values(),
                *cross_plant["current_hidden"].values(),
                *cross_plant["normalized_obs"].values(),
                *cross_plant["normalized_obs_plus_h_in"].values(),
            )
            for value in group.values()
        ),
        "read_only_cpu_audit": True,
        "no_training_behavior_or_hosted_compute": True,
    }
    failed_validity = sorted(
        name for name, passed in checks.items() if not passed
    )
    if failed_validity:
        decision = "INVALID_NO_DISTILLATION"
    elif hidden_qualifies:
        decision = "EARN_ONE_V133_ANALYTIC_HIDDEN_RESIDUAL_CPU_CONTRACT"
    elif state_qualifies:
        decision = "EARN_ONE_V133_ANALYTIC_STATE_RESIDUAL_CPU_CONTRACT"
    else:
        decision = "NO_STATIC_LINEAR_ROBUST_TEACHER_DISTILLATION"
    payload = {
        "schema_version": "winner_v132.robust_teacher_dataset_audit.v1",
        "status": (
            "PASS_WINNER_V132_ROBUST_TEACHER_DATASET_AUDIT"
            if not failed_validity
            else "INVALID_WINNER_V132_ROBUST_TEACHER_DATASET_AUDIT"
        ),
        "failed_validity_checks": failed_validity,
        "checks": checks,
        "input_hashes": observed_hashes,
        "dataset": {
            "rows": 4_800,
            "corrected_rows": int(np.sum(corrected)),
            "preservation_rows": int(np.sum(~corrected)),
            "projected_joint_events": rows["projected_joint_events"],
            "correction_weight": float(
                np.sum(~corrected) / np.sum(corrected)
            ),
            "trace_manifest": rows["manifest"],
        },
        "combined_fit": combined,
        "cross_plant_fit": cross_plant,
        "advancement": {
            "hidden_qualifies": hidden_qualifies,
            "state_qualifies": state_qualifies,
            "thresholds": {
                "corrected_ratio_to_zero_predictor": "<=0.25",
                "preservation_ratio_to_corrected_baseline": "<=0.01",
                "both_cross_plant_corrected_ratios": "<1.0",
                "both_cross_plant_preservation_ratios": "<=0.01",
                "state_only_total_error_vs_hidden": "<=0.25",
            },
        },
        "decision": decision,
        "authority": {
            "v133_cpu_contract": decision.startswith("EARN_ONE_V133"),
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
        "# Winner V132 robust teacher dataset audit\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Corrected rows/events: `{payload['dataset']['corrected_rows']}` / "
        f"`{payload['dataset']['projected_joint_events']}`.\n"
        f"- Hidden/state qualify: `{hidden_qualifies}` / "
        f"`{state_qualifies}`.\n"
        f"- Decision: `{decision}`\n"
        "- Read-only CPU evidence; no training or hardware authority.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(decision)
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed_validity else 1


if __name__ == "__main__":
    raise SystemExit(main())
