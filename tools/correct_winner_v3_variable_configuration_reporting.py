#!/usr/bin/env python3
"""Correct winner-v3 reporting defects without rerunning behavior cells."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

import jax


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
CELLS = ANALYSIS / "winner_v3_variable_configuration_cells"
TRACES = ANALYSIS / "winner_v3_variable_configuration_traces"
CONDITIONS = ANALYSIS / "winner_v3_variable_configuration_conditions"
RAW_RESULT = ANALYSIS / "winner_v3_variable_configuration_result.json"
RAW_RESULT_MD = ANALYSIS / "WINNER_V3_VARIABLE_CONFIGURATION_RESULT_20260719.md"
PREREG = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
RUNNER_CONTRACT = ANALYSIS / "winner_v3_variable_configuration_behavior_runner_contract.json"
TRANSFORM_CONTRACT = ANALYSIS / "winner_v3_variable_configuration_eval_policy_transform_contract.json"
TRAINING_CHECK = ANALYSIS / "winner_v3_recurrent_adapter_training_artifact_check.json"
PROCESS_ATTESTATION = ANALYSIS / "winner_v3_formal_process_cpu_attestation_20260719.txt"
TRACE_MANIFEST = ANALYSIS / "winner_v3_variable_configuration_trace_manifest.json"
CORRECTED_RESULT = ANALYSIS / "winner_v3_variable_configuration_result_corrected.json"
CORRECTED_RESULT_MD = ANALYSIS / "WINNER_V3_VARIABLE_CONFIGURATION_RESULT_CORRECTED_20260720.md"
CORRECTION = ANALYSIS / "winner_v3_variable_configuration_reporting_correction.json"
CORRECTION_MD = ANALYSIS / "WINNER_V3_VARIABLE_CONFIGURATION_REPORTING_CORRECTION_20260720.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def dump(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def parse_attestation(path: Path) -> dict[str, str]:
    rows: dict[str, str] = {}
    for line in path.read_text().splitlines():
        if not line or "=" not in line:
            continue
        key, value = line.split("=", 1)
        rows[key] = value
    return rows


def identity_key(cell: dict[str, Any]) -> str:
    return json.dumps(cell["identity"], sort_keys=True, separators=(",", ":"))


def main() -> int:
    raw = load(RAW_RESULT)
    prereg = load(PREREG)
    runner_contract = load(RUNNER_CONTRACT)
    transform = load(TRANSFORM_CONTRACT)
    training_check = load(TRAINING_CHECK)
    attestation = parse_attestation(PROCESS_ATTESTATION)
    expected_policy_hashes = {
        int(row["step"]): row["output_sha256"] for row in transform["policies"]
    }

    condition_paths = sorted(CONDITIONS.glob("*.json"))
    condition_payloads = [load(path) for path in condition_paths]
    referenced_cells: dict[str, str] = {}
    condition_reference_valid = True
    for condition in condition_payloads:
        condition_reference_valid &= len(condition["cells"]) == 16
        for summary in condition["cells"]:
            relative = summary["cell_path"]
            if relative in referenced_cells:
                condition_reference_valid = False
            referenced_cells[relative] = summary["cell_sha256"]

    cell_paths = sorted(CELLS.glob("*.json"))
    cells = [load(path) for path in cell_paths]
    physical_rows: list[dict[str, Any]] = []
    trace_hashes_exact = True
    trace_evidence_consistent = True
    cell_hashes_exact = True
    policy_hashes_exact = True
    readbacks_exact = True
    reward_weight_zero = True
    identities: set[str] = set()
    trace_manifest_rows: list[dict[str, Any]] = []
    early_termination_cells = 0
    raw_cpu_false_cells = 0
    for path, cell in zip(cell_paths, cells, strict=True):
        relative = str(path.relative_to(ROOT))
        cell_hashes_exact &= referenced_cells.get(relative) == sha256(path)
        identities.add(identity_key(cell))
        trace_path = ROOT / cell["trace"]["path"]
        trace_digest = sha256(trace_path) if trace_path.exists() else None
        trace_hashes_exact &= trace_digest == cell["trace"]["sha256"]
        trace_manifest_rows.append(
            {
                "cell_path": relative,
                "cell_sha256": sha256(path),
                "trace_path": cell["trace"]["path"],
                "trace_sha256": trace_digest,
                "trace_bytes": trace_path.stat().st_size if trace_path.exists() else None,
                "trace_rows": int(cell["trace"]["rows"]),
                "recorded_samples": int(cell["metrics"]["samples"]),
                "termination_reason": cell["metrics"]["termination_reason"],
            }
        )
        samples = int(cell["metrics"]["samples"])
        termination = cell["metrics"]["termination_reason"]
        early = samples < 600
        early_termination_cells += int(early)
        trace_evidence_consistent &= (
            0 < samples <= 600
            and int(cell["trace"]["rows"]) == samples
            and bool(cell["trace"]["ticks_contiguous"])
            and bool(cell["trace"]["required_fields_every_tick"])
            and bool(cell["trace"]["all_values_finite"])
            and bool(cell["trace"]["reset_h_exact_zero"])
            and bool(cell["trace"]["reset_previous_action_exact_zero"])
            and (termination != "duration_complete" or samples == 600)
            and (not early or termination != "duration_complete")
        )
        readbacks_exact &= all(bool(value) for value in cell["readback_checks"].values())
        step = int(cell["identity"]["step"])
        policy_hashes_exact &= cell["policy"]["sha256"] == expected_policy_hashes[step]
        reward_weight_zero &= int(cell["training_or_simulator_reward_selection_weight"]) == 0
        raw_cpu_false_cells += int(not cell["metrics"]["checks"]["cpu_only"])
        physical_failures = [
            name for name in cell["failure_reasons"] if name != "cpu_only"
        ]
        corrected_pass = not physical_failures
        checks_pass = all(
            bool(value)
            for name, value in cell["metrics"]["checks"].items()
            if name != "cpu_only"
        )
        physical_rows.append(
            {
                "cell": cell,
                "pass": corrected_pass,
                "checks_pass": checks_pass,
                "failures": physical_failures,
            }
        )

    devices = list(jax.devices())
    current_cpu = {
        "CUDA_VISIBLE_DEVICES": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "JAX_PLATFORMS": os.environ.get("JAX_PLATFORMS"),
        "jax_backend": jax.default_backend(),
        "jax_devices": [str(device) for device in devices],
        "jax_device_platforms": [device.platform for device in devices],
    }
    process_cpu_attested = (
        attestation.get("CUDA_VISIBLE_DEVICES") == ""
        and attestation.get("JAX_PLATFORMS") == "cpu"
        and attestation.get("cmdline")
        == "/home/lsd/robots/envs/ground-up-control/bin/python tools/run_winner_v3_variable_configuration_behavior.py --execute"
        and attestation.get("runner_sha256") == raw["runner_sha256"]
        and attestation.get("repository_head") == raw["runner_commit"]
        and runner_contract["environment"]["CUDA_VISIBLE_DEVICES"] == ""
        and runner_contract["environment"]["JAX_PLATFORMS"] == "cpu"
    )
    current_cpu_attested = (
        current_cpu["CUDA_VISIBLE_DEVICES"] == ""
        and current_cpu["JAX_PLATFORMS"] == "cpu"
        and current_cpu["jax_backend"] == "cpu"
        and bool(devices)
        and all(device.platform == "cpu" for device in devices)
    )
    historical_tfrt_cpu_contract = (
        training_check["checks"]["cpu_only"]
        and training_check["devices"] == ["TFRT_CPU_0"]
    )

    physical_pass_count = sum(row["pass"] for row in physical_rows)
    failure_names = sorted(
        {name for row in physical_rows for name in row["failures"]}
    )
    failures_by_reason = {
        name: sum(name in row["failures"] for row in physical_rows)
        for name in failure_names
    }
    groups = sorted(
        {row["cell"]["identity"]["condition_group"] for row in physical_rows}
    )
    passing_by_group = {
        group: sum(
            row["pass"]
            for row in physical_rows
            if row["cell"]["identity"]["condition_group"] == group
        )
        for group in groups
    }
    failing_by_group = {
        group: sum(
            not row["pass"]
            for row in physical_rows
            if row["cell"]["identity"]["condition_group"] == group
        )
        for group in groups
    }
    per_checkpoint: dict[str, Any] = {}
    for step in sorted(expected_policy_hashes):
        subset = [
            row for row in physical_rows if int(row["cell"]["identity"]["step"]) == step
        ]
        per_checkpoint[str(step)] = {
            "cells": len(subset),
            "passing_cells": sum(row["pass"] for row in subset),
            "all_512_cells_pass": len(subset) == 512 and all(row["pass"] for row in subset),
            "worst_tracking_p95_rad": max(
                row["cell"]["metrics"]["worst_tracking_p95_rad"] for row in subset
            ),
            "worst_current_p95_a": max(
                row["cell"]["metrics"]["worst_current_p95_a"] for row in subset
            ),
            "minimum_moving_mean_vx_m_s": min(
                float(row["cell"]["metrics"]["mean_local_vx_m_s"])
                for row in subset
                if float(row["cell"]["identity"]["command_x_m_s"]) > 0.0
                and row["cell"]["metrics"]["mean_local_vx_m_s"] is not None
            ),
            "policy_sha256": expected_policy_hashes[step],
        }

    validity = {
        "all_1024_cells_present_unique": len(cells) == 1024 and len(identities) == 1024,
        "all_64_condition_artifacts_present": len(condition_payloads) == 64,
        "condition_to_cell_hashes_exact": condition_reference_valid
        and len(referenced_cells) == 1024
        and cell_hashes_exact,
        "all_trace_hashes_exact": trace_hashes_exact,
        "all_trace_evidence_consistent_with_recorded_termination": trace_evidence_consistent,
        "all_per_run_readbacks_exact": readbacks_exact,
        "all_policy_hashes_exact": policy_hashes_exact,
        "all_cpu_only_platform_attested": process_cpu_attested
        and current_cpu_attested
        and historical_tfrt_cpu_contract,
        "physical_pass_matches_checks_without_cpu_label": all(
            row["pass"] == row["checks_pass"] for row in physical_rows
        ),
        "raw_cpu_label_false_for_all_cells": raw_cpu_false_cells == 1024,
        "early_termination_count_matches_raw_trace_contract_failures": early_termination_cells
        == raw["failures_by_reason"]["trace_contract"]
        == raw["failures_by_reason"]["duration_complete_600"],
        "no_training_or_simulator_reward_selection": reward_weight_zero,
        "raw_runner_and_matrix_hashes_preserved": raw["runner_sha256"]
        == runner_contract["runner_sha256"]
        and raw["matrix_plan_sha256"] == runner_contract["matrix_plan_sha256"],
    }
    failed_validity = sorted(name for name, value in validity.items() if not value)
    trace_manifest = {
        "schema_version": "winner_v3.variable_configuration_trace_manifest.v1",
        "status": "PASS_WINNER_V3_VARIABLE_CONFIGURATION_TRACE_MANIFEST"
        if trace_hashes_exact and trace_evidence_consistent and len(trace_manifest_rows) == 1024
        else "HOLD_WINNER_V3_VARIABLE_CONFIGURATION_TRACE_MANIFEST",
        "trace_count": len(trace_manifest_rows),
        "total_trace_bytes": sum(int(row["trace_bytes"] or 0) for row in trace_manifest_rows),
        "all_trace_hashes_exact": trace_hashes_exact,
        "all_trace_rows_match_recorded_samples": trace_evidence_consistent,
        "raw_result_sha256": sha256(RAW_RESULT),
        "runner_sha256": raw["runner_sha256"],
        "matrix_plan_sha256": raw["matrix_plan_sha256"],
        "traces": trace_manifest_rows,
    }
    dump(TRACE_MANIFEST, trace_manifest)
    both_pass = all(row["all_512_cells_pass"] for row in per_checkpoint.values())
    decision = (
        prereg["advancement"]["pass_token"]
        if not failed_validity and both_pass
        else prereg["advancement"]["fail_token"]
        if not failed_validity
        else prereg["advancement"]["invalid_token"]
    )
    status = (
        "PASS_WINNER_V3_VARIABLE_CONFIGURATION_RESULT_REPORTING_CORRECTED"
        if decision == prereg["advancement"]["pass_token"]
        else "HOLD_WINNER_V3_VARIABLE_CONFIGURATION_RESULT_REPORTING_CORRECTED"
        if decision == prereg["advancement"]["fail_token"]
        else "INVALID_WINNER_V3_VARIABLE_CONFIGURATION_REPORTING_CORRECTION"
    )
    corrected = {
        "schema_version": "winner_v3.variable_configuration_result.reporting_corrected.v1",
        "status": status,
        "decision": decision,
        "selected_policy": None,
        "validity_checks": validity,
        "failed_validity_checks": failed_validity,
        "cells": len(cells),
        "passing_cells": physical_pass_count,
        "failing_cells": len(cells) - physical_pass_count,
        "passing_cells_by_group": passing_by_group,
        "failing_cells_by_group": failing_by_group,
        "failures_by_reason": failures_by_reason,
        "per_checkpoint": per_checkpoint,
        "early_termination_cells": early_termination_cells,
        "matrix_plan_sha256": raw["matrix_plan_sha256"],
        "runner_sha256": raw["runner_sha256"],
        "runner_commit": raw["runner_commit"],
        "runner_contract_sha256": sha256(RUNNER_CONTRACT),
        "preregistration_sha256": sha256(PREREG),
        "transform_contract_sha256": sha256(TRANSFORM_CONTRACT),
        "raw_result": {
            "path": str(RAW_RESULT.relative_to(ROOT)),
            "sha256": sha256(RAW_RESULT),
            "status": raw["status"],
            "decision": raw["decision"],
        },
        "raw_result_md_sha256": sha256(RAW_RESULT_MD),
        "process_cpu_attestation": {
            "path": str(PROCESS_ATTESTATION.relative_to(ROOT)),
            "sha256": sha256(PROCESS_ATTESTATION),
            "capture": attestation,
            "current_read_only_cpu_check": current_cpu,
        },
        "trace_manifest": {
            "path": str(TRACE_MANIFEST.relative_to(ROOT)),
            "sha256": sha256(TRACE_MANIFEST),
            "trace_count": trace_manifest["trace_count"],
            "total_trace_bytes": trace_manifest["total_trace_bytes"],
        },
        "reporting_correction": {
            "scope": [
                "recognize TFRT_CPU_0 through device.platform == cpu rather than a CpuDevice display-name substring",
                "treat an early-termination trace as complete evidence when its rows equal recorded samples and its hash, schema, finite-value, reset and readback audits pass",
            ],
            "behavior_cells_rerun": 0,
            "cell_or_trace_artifacts_mutated": False,
            "physics_policy_threshold_or_gate_changes": 0,
            "cpu_only_cell_failure_removed": True,
            "duration_and_trace_behavior_failures_preserved": True,
        },
        "training_or_simulator_reward_selection_weight": 0,
        "no_closest_promotion": True,
        "wall_seconds_original_run": raw["wall_seconds"],
        "authority": {
            "policy_asset_and_clearance_commit_sequence": False,
            "robot_clearance": False,
            "runtime_or_gate5": False,
            "rdkx5_or_robot": False,
            "training_or_retry": False,
        },
    }
    dump(CORRECTED_RESULT, corrected)

    checkpoint_rows = "\n".join(
        f"| {step} | {row['cells']} | {row['passing_cells']} | `{row['all_512_cells_pass']}` | "
        f"{row['worst_tracking_p95_rad']:.9f} | {row['worst_current_p95_a']:.9f} | "
        f"{row['minimum_moving_mean_vx_m_s']:.9f} |"
        for step, row in per_checkpoint.items()
    )
    failure_rows = "\n".join(
        f"- `{name}`: `{count}`" for name, count in failures_by_reason.items()
    )
    CORRECTED_RESULT_MD.write_text(
        "# Winner-v3 Variable-Configuration Corrected Result\n\n"
        f"status: `{status}`\n\n"
        f"decision: `{decision}`\n\n"
        f"Cells: `{physical_pass_count}/{len(cells)}` pass after removing only the false CPU display-name failure.\n\n"
        "| checkpoint | cells | passing | all pass | worst tracking p95 | worst current p95 | minimum moving vx |\n"
        "|---:|---:|---:|---|---:|---:|---:|\n"
        f"{checkpoint_rows}\n\n"
        "## Physical failure counts\n\n"
        f"{failure_rows}\n\n"
        "The raw aggregate is preserved. Its `INVALID` token came from two reporting defects: JAX exposed "
        "`TFRT_CPU_0` instead of a display string containing `CpuDevice`, and the aggregate treated every "
        "expected early-termination trace as missing evidence. All 1,024 trace hashes, row/sample counts, "
        "schemas, finite-value audits, reset audits and per-run readbacks validate. Duration and trace-contract "
        "failures remain behavioral failures in the corrected result.\n\n"
        "Both persistent checkpoints fail the frozen all-512 rule. No graph, closest configuration, reward, "
        "or sibling checkpoint is promoted. Robot clearance and runtime adoption remain `NO`.\n"
    )

    correction_checks = {
        "corrected_result_valid": not failed_validity,
        "corrected_decision_is_frozen_hold_token": decision == prereg["advancement"]["fail_token"],
        "raw_result_preserved_invalid": raw["status"] == "INVALID_WINNER_V3_VARIABLE_CONFIGURATION_RESULT",
        "no_behavior_rerun": corrected["reporting_correction"]["behavior_cells_rerun"] == 0,
        "no_cell_or_trace_mutation": not corrected["reporting_correction"]["cell_or_trace_artifacts_mutated"],
        "physical_failures_remain": len(cells) - physical_pass_count > 0,
        "both_checkpoints_fail_all_cells": not both_pass,
        "robot_clearance_false": corrected["authority"]["robot_clearance"] is False,
    }
    correction_failed = sorted(
        name for name, value in correction_checks.items() if not value
    )
    correction = {
        "schema_version": "winner_v3.variable_configuration_reporting_correction.v1",
        "status": "PASS_WINNER_V3_VARIABLE_CONFIGURATION_REPORTING_CORRECTION"
        if not correction_failed
        else "HOLD_WINNER_V3_VARIABLE_CONFIGURATION_REPORTING_CORRECTION",
        "checks": correction_checks,
        "failed_checks": correction_failed,
        "scope": corrected["reporting_correction"],
        "raw_result": corrected["raw_result"],
        "corrected_result": {
            "path": str(CORRECTED_RESULT.relative_to(ROOT)),
            "sha256": sha256(CORRECTED_RESULT),
            "md_path": str(CORRECTED_RESULT_MD.relative_to(ROOT)),
            "md_sha256": sha256(CORRECTED_RESULT_MD),
            "status": status,
            "decision": decision,
        },
        "correction_tool": {
            "path": str(Path(__file__).resolve().relative_to(ROOT)),
            "sha256": sha256(Path(__file__).resolve()),
        },
        "process_cpu_attestation_sha256": sha256(PROCESS_ATTESTATION),
        "trace_manifest": {
            "path": str(TRACE_MANIFEST.relative_to(ROOT)),
            "sha256": sha256(TRACE_MANIFEST),
            "status": trace_manifest["status"],
        },
        "authority": corrected["authority"],
    }
    dump(CORRECTION, correction)
    CORRECTION_MD.write_text(
        "# Winner-v3 Variable-Configuration Reporting Correction\n\n"
        f"status: `{correction['status']}`\n\n"
        f"corrected decision: `{decision}`\n\n"
        "This read-only correction reran zero behavior cells and changed no policy, model, trace, threshold, "
        "gate, seed or physics parameter. It fixes only the CPU device-display test and the aggregate-level "
        "interpretation of complete early-termination evidence. The raw invalid aggregate remains preserved.\n\n"
        f"Corrected result SHA-256: `{correction['corrected_result']['sha256']}`.\n\n"
        f"Correction JSON SHA-256: `{sha256(CORRECTION)}`.\n\n"
        "The corrected evidence is a clean negative result: both checkpoints fail, no policy is selected, "
        "and robot/runtime clearance remains false.\n"
    )
    print(json.dumps({
        "status": correction["status"],
        "decision": decision,
        "passing_cells": physical_pass_count,
        "failing_cells": len(cells) - physical_pass_count,
        "corrected_result_sha256": sha256(CORRECTED_RESULT),
        "correction_sha256": sha256(CORRECTION),
    }, sort_keys=True))
    return 0 if not correction_failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
