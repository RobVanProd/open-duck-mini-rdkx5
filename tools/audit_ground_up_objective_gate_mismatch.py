#!/usr/bin/env python3
"""Measure reference-imitation versus actuator-tracking drift on frozen traces."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

import numpy as np


JOINTS = [
    "left_hip_yaw", "left_hip_roll", "left_hip_pitch", "left_knee",
    "left_ankle", "neck_pitch", "head_pitch", "head_yaw", "head_roll",
    "right_hip_yaw", "right_hip_roll", "right_hip_pitch", "right_knee",
    "right_ankle",
]
EXPECTED_REFERENCE_TABLE_SHA256 = (
    "8102d9cd139584816d807ca635bcca6d37fa6b3c455848e00395b6d565968212"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def stats(values: np.ndarray) -> dict[str, float]:
    values = np.asarray(values, dtype=np.float64).reshape(-1)
    return {
        "mean": float(np.mean(values)),
        "rms": float(np.sqrt(np.mean(np.square(values)))),
        "p50": float(np.percentile(values, 50)),
        "p95": float(np.percentile(values, 95)),
        "max": float(np.max(values)),
    }


def load_rows(root: Path) -> tuple[list[dict], list[dict]]:
    rows: list[dict] = []
    manifest: list[dict] = []
    for path in sorted(root.glob("*.jsonl")):
        file_rows = [
            json.loads(line) for line in path.read_text().splitlines() if line.strip()
        ]
        fitted = [row for row in file_rows if row.get("mode") == "fitted"]
        if not fitted:
            raise ValueError(f"no fitted rows in {path}")
        rows.extend(fitted)
        manifest.append(
            {
                "path": str(path.resolve()),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
                "fitted_rows": len(fitted),
            }
        )
    if not rows:
        raise ValueError(f"no JSONL traces in {root}")
    return rows, manifest


def analyze_rows(
    rows: list[dict],
    home: np.ndarray,
    action_scale: float,
    table_commands: np.ndarray,
    table_actions: np.ndarray,
    projection_scales: np.ndarray,
) -> dict:
    actual = np.asarray([row["actual_position_rad"] for row in rows], dtype=np.float64)
    sent = np.asarray([row["sent_target_rad"] for row in rows], dtype=np.float64)
    applied = np.asarray([row["applied_target_rad"] for row in rows], dtype=np.float64)
    projected_reference_action = np.asarray(
        [row["obs_state"][101:115] for row in rows], dtype=np.float64
    )
    projected_reference = home[None, :] + action_scale * projected_reference_action
    reward_reference = []
    phase_match_error = []
    for row, observed_action in zip(rows, projected_reference_action, strict=True):
        command = np.asarray(row["command"][:3], dtype=np.float64)
        command_index = int(np.argmin(np.sum(np.abs(table_commands - command), axis=1)))
        phase_errors = np.max(
            np.abs(table_actions[command_index] - observed_action[None, :]), axis=1
        )
        phase_index = int(np.argmin(phase_errors))
        phase_match_error.append(float(phase_errors[phase_index]))
        scale = projection_scales[command_index]
        unprojected_delta = np.divide(
            action_scale * observed_action,
            scale,
            out=np.zeros_like(observed_action),
            where=np.abs(scale) > 1e-12,
        )
        reward_reference.append(home + unprojected_delta)
    reward_reference = np.asarray(reward_reference, dtype=np.float64)
    errors = {
        "projected_reference_to_actual": np.abs(projected_reference - actual),
        "reward_reference_to_actual": np.abs(reward_reference - actual),
        "sent_target_to_actual": np.abs(sent - actual),
        "applied_target_to_actual": np.abs(applied - actual),
        "sent_target_to_projected_reference": np.abs(sent - projected_reference),
        "sent_target_to_reward_reference": np.abs(sent - reward_reference),
        "applied_target_to_projected_reference": np.abs(applied - projected_reference),
        "applied_target_to_reward_reference": np.abs(applied - reward_reference),
    }
    reward_keys = sorted(
        set.intersection(*(set(row.get("reward_terms", {})) for row in rows))
    )
    commands = np.asarray([row["command"][0] for row in rows], dtype=np.float64)
    result = {
        "samples": len(rows),
        "commands_x": sorted(float(value) for value in np.unique(commands)),
        "reference_table_phase_match_max_error": max(phase_match_error),
        "errors_rad": {},
        "reward_terms_mean": {
            key: float(np.mean([row["reward_terms"][key] for row in rows]))
            for key in reward_keys
        },
    }
    for name, values in errors.items():
        result["errors_rad"][name] = {
            "global": stats(values),
            "per_joint": {
                joint: stats(values[:, index])
                for index, joint in enumerate(JOINTS)
            },
            "per_command": {
                f"{command:.3f}": stats(values[np.isclose(commands, command)])
                for command in np.unique(commands)
            },
        }
    return result


def deltas(one: dict, two: dict) -> dict:
    result: dict = {"errors_rad": {}, "reward_terms_mean": {}}
    for name in one["errors_rad"]:
        result["errors_rad"][name] = {
            "global": {
                metric: two["errors_rad"][name]["global"][metric]
                - one["errors_rad"][name]["global"][metric]
                for metric in one["errors_rad"][name]["global"]
            },
            "per_joint": {
                joint: {
                    metric: two["errors_rad"][name]["per_joint"][joint][metric]
                    - one["errors_rad"][name]["per_joint"][joint][metric]
                    for metric in one["errors_rad"][name]["per_joint"][joint]
                }
                for joint in JOINTS
            },
        }
    for key in one["reward_terms_mean"]:
        result["reward_terms_mean"][key] = (
            two["reward_terms_mean"][key] - one["reward_terms_mean"][key]
        )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--traces-1m", type=Path, required=True)
    parser.add_argument("--traces-2m", type=Path, required=True)
    parser.add_argument("--reference-table", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()

    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise RuntimeError("set CUDA_VISIBLE_DEVICES='' for this CPU-only audit")
    reference_sha = sha256_file(args.reference_table)
    if reference_sha != EXPECTED_REFERENCE_TABLE_SHA256:
        raise RuntimeError(f"unexpected reference table SHA-256: {reference_sha}")
    with np.load(args.reference_table) as table:
        home = np.asarray(table["home_rad"], dtype=np.float64)
        action_scale = float(np.asarray(table["action_scale_rad"]))
        table_commands = np.asarray(table["commands"], dtype=np.float64)
        table_actions = np.asarray(table["actions"], dtype=np.float64)
        projection_scales = np.asarray(table["projection_scales"], dtype=np.float64)

    rows_one, manifest_one = load_rows(args.traces_1m)
    rows_two, manifest_two = load_rows(args.traces_2m)
    one = analyze_rows(
        rows_one, home, action_scale, table_commands, table_actions, projection_scales
    )
    two = analyze_rows(
        rows_two, home, action_scale, table_commands, table_actions, projection_scales
    )
    drift = deltas(one, two)

    projected_ref_actual_rms = drift["errors_rad"]["projected_reference_to_actual"]["global"]["rms"]
    reward_ref_actual_rms = drift["errors_rad"]["reward_reference_to_actual"]["global"]["rms"]
    sent_actual_rms = drift["errors_rad"]["sent_target_to_actual"]["global"]["rms"]
    sent_projected_ref_rms = drift["errors_rad"]["sent_target_to_projected_reference"]["global"]["rms"]
    sent_reward_ref_rms = drift["errors_rad"]["sent_target_to_reward_reference"]["global"]["rms"]
    applied_actual_rms = drift["errors_rad"]["applied_target_to_actual"]["global"]["rms"]
    lead_compensation = (
        reward_ref_actual_rms < 0.0
        and sent_actual_rms > 0.0
        and sent_reward_ref_rms > 0.0
        and applied_actual_rms > 0.0
    )
    checks = {
        "reference_table_hash_matches_frozen_contract": reference_sha
        == EXPECTED_REFERENCE_TABLE_SHA256,
        "trace_corpora_have_identical_sample_count": len(rows_one) == len(rows_two),
        "trace_corpora_have_identical_commands": one["commands_x"] == two["commands_x"],
        "reference_feature_rows_match_frozen_table": max(
            one["reference_table_phase_match_max_error"],
            two["reference_table_phase_match_max_error"],
        )
        <= 1e-6,
        "all_reconstructed_values_are_finite": all(
            np.isfinite(value)
            for checkpoint in (one, two)
            for error in checkpoint["errors_rad"].values()
            for scope in error["global"].values()
            for value in [scope]
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    mechanism = (
        "REFERENCE_LEAD_COMPENSATION_CONFLICTS_WITH_TARGET_TRACKING_GATE"
        if lead_compensation
        else "NO_UNIQUE_OBJECTIVE_GATE_MECHANISM"
    )
    status = (
        "PASS_OBJECTIVE_GATE_MISMATCH_AUDIT"
        if not failed
        else "FAIL_OBJECTIVE_GATE_MISMATCH_AUDIT"
    )
    payload = {
        "schema_version": "ground_up_objective_gate_mismatch.v1",
        "status": status,
        "mechanism": mechanism,
        "checks": checks,
        "failed_checks": failed,
        "checkpoints": {"1M": one, "2M": two},
        "delta_2M_minus_1M": drift,
        "inputs": {
            "reference_table": {
                "path": str(args.reference_table.resolve()),
                "sha256": reference_sha,
            },
            "traces_1M": manifest_one,
            "traces_2M": manifest_two,
        },
        "execution": {
            "cpu_only": True,
            "robot_access": False,
            "rdk_access": False,
            "gpu_access": False,
            "colab_access": False,
        },
        "authority": {
            "training_authorized": False,
            "robot_or_rdk_authorized": False,
            "gpu_authorized": False,
        },
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    key_deltas = [
        ("projected reference→actual RMS", projected_ref_actual_rms),
        ("reward reference→actual RMS", reward_ref_actual_rms),
        ("sent target→actual RMS", sent_actual_rms),
        ("applied target→actual RMS", applied_actual_rms),
        ("sent target→projected reference RMS", sent_projected_ref_rms),
        ("sent target→reward reference RMS", sent_reward_ref_rms),
    ]
    joint_rows = sorted(
        (
            (
                joint,
                drift["errors_rad"]["reward_reference_to_actual"]["per_joint"][joint]["rms"],
                drift["errors_rad"]["sent_target_to_actual"]["per_joint"][joint]["rms"],
                drift["errors_rad"]["sent_target_to_reward_reference"]["per_joint"][joint]["rms"],
            )
            for joint in JOINTS
        ),
        key=lambda row: row[2],
        reverse=True,
    )
    lines = [
        "# Ground-Up Objective/Gate Mismatch Audit",
        "",
        f"status: `{status}`",
        f"measured mechanism: `{mechanism}`",
        "",
        "## 2M minus 1M error change",
        "",
        *[f"- {name}: `{value:+.8f} rad`" for name, value in key_deltas],
        "",
        "The actor feature uses the velocity-projected reference. The imitation",
        "reward uses the unprojected polynomial joint positions, reconstructed here",
        "by reversing the frozen per-command projection scale. A negative reward-",
        "reference-to-actual change means realized motion became closer to the exact",
        "joint-position target optimized by imitation.",
        "",
        "## Largest joint-level sent-target tracking changes",
        "",
        "| joint | reward ref→actual RMS Δ | sent→actual RMS Δ | sent→reward ref RMS Δ |",
        "|---|---:|---:|---:|",
        *[
            f"| {joint} | {ref_delta:+.8f} | {sent_delta:+.8f} | {lead_delta:+.8f} |"
            for joint, ref_delta, sent_delta, lead_delta in joint_rows[:6]
        ],
        "",
        "## Decision boundary",
        "",
        (
            "This audit identifies a measured objective/gate conflict."
            if lead_compensation
            else "This audit does not identify a unique objective/gate mechanism."
        ),
        "It does not select a penalty scale, authorize training, or weaken the",
        "frozen hardware tracking gate. Any next causal arm requires separate",
        "preregistration and a CPU transition/reward contract.",
        "",
    ]
    args.output_md.write_text("\n".join(lines))
    print(json.dumps({"status": status, "mechanism": mechanism, "failed_checks": failed}))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
