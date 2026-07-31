#!/usr/bin/env python3
"""Separate the V105 policy failure from the V103 evaluator defects."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
FORMAL_RESULT = ANALYSIS / "winner_v103_response_conditioned_result.json"
REPRODUCTION = ANALYSIS / "winner_v106_com_prefix_reproduction.json"
FORMAL_RUNNER = ROOT / "tools/run_winner_v103_response_conditioned_behavior.py"
BASE_RUNNER = ROOT / "tools/run_winner_v3_variable_configuration_behavior.py"
OUTPUT = ANALYSIS / "winner_v106_response_gate_attribution.json"
MARKDOWN = ANALYSIS / "WINNER_V106_RESPONSE_GATE_ATTRIBUTION_20260724.md"
FORMAL_RESULT_SHA256 = (
    "f3a0ed34d46b6013c0910afe29fcd9f424729c94b61b8abdb4f416457ad3922b"
)
REPRODUCTION_SHA256 = (
    "ded813c4ca8e96862a6db377b4010c84eac1c49d741484767c5d430599de6581"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def load_cells(path: Path) -> tuple[list[dict[str, Any]], int]:
    files = sorted(path.glob("*.json"))
    cells = [json.loads(file.read_text(encoding="utf-8")) for file in files]
    return cells, sum(file.stat().st_size for file in files)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cells", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(
                f"refusing to overwrite Winner-v106 attribution: {path}"
            )
    if (
        sha256(FORMAL_RESULT) != FORMAL_RESULT_SHA256
        or sha256(REPRODUCTION) != REPRODUCTION_SHA256
    ):
        raise ValueError("Winner-v106 attribution inputs changed")

    formal = json.loads(FORMAL_RESULT.read_text(encoding="utf-8"))
    reproduction = json.loads(REPRODUCTION.read_text(encoding="utf-8"))
    cells, cell_bytes = load_cells(args.cells.resolve())
    identities = [
        {
            "identity": cell["identity"],
            "cell_sha256": sha256(args.cells.resolve() / f"{cell['cell_path'].split('/')[-1]}")
            if cell.get("cell_path")
            else canonical_sha256(cell),
        }
        for cell in cells
    ]
    unique = {
        (
            cell["identity"]["condition_group"],
            cell["identity"]["condition_id"],
            int(cell["identity"]["seed"]),
            int(cell["identity"]["step"]),
            cell["identity"]["plant"],
            float(cell["identity"]["command_x_m_s"]),
        )
        for cell in cells
    }
    behavior_failures = [
        cell
        for cell in cells
        if any(reason != "cpu_only" for reason in cell["failure_reasons"])
    ]
    cpu_label_only = [
        cell
        for cell in cells
        if cell["failure_reasons"] == ["cpu_only"]
    ]
    exceptions = [
        cell
        for cell in cells
        if "runner_exception_ValueError" in cell["failure_reasons"]
    ]
    exception_conditions = sorted(
        {cell["identity"]["condition_id"] for cell in exceptions}
    )
    per_checkpoint: dict[str, Any] = {}
    for step in (1_003_520, 2_007_040):
        subset = [
            cell for cell in cells if int(cell["identity"]["step"]) == step
        ]
        per_checkpoint[str(step)] = {
            "cells": len(subset),
            "cpu_label_only_cells": sum(
                cell["failure_reasons"] == ["cpu_only"] for cell in subset
            ),
            "behavior_failure_cells": sum(
                any(reason != "cpu_only" for reason in cell["failure_reasons"])
                for cell in subset
            ),
            "runner_exception_cells": sum(
                "runner_exception_ValueError" in cell["failure_reasons"]
                for cell in subset
            ),
        }

    formal_exact = (
        formal.get("status")
        == "INVALID_WINNER_V103_RESPONSE_CONDITIONED_RESULT"
        and formal.get("decision") == "NO_RESPONSE_CONDITIONED_CHECKPOINT_SELECTED"
        and formal.get("robot_clearance") is False
        and formal.get("cells") == 1024
        and formal.get("passing_cells") == 0
        and formal.get("failing_cells") == 1024
        and formal.get("failed_validity_checks")
        == [
            "all_cell_trace_and_response_contracts_complete",
            "all_cpu_only",
        ]
        and formal.get("failures_by_reason", {}).get("cpu_only") == 864
        and formal.get("failures_by_reason", {}).get(
            "runner_exception_ValueError"
        )
        == 160
    )
    reproduction_exact = (
        reproduction.get("status")
        == "PASS_WINNER_V106_COM_PREFIX_REPRODUCTION"
        and reproduction.get("failed_checks") == []
        and reproduction.get("observed", {}).get("simulator_status")
        == "HOLD_RESPONSE_CALIBRATION_PREFIX"
        and reproduction.get("observed", {}).get("simulator_error")
        == "calibration prefix terminated early"
        and reproduction.get("observed", {}).get(
            "environment_readback_present"
        )
        is False
        and reproduction.get("cpu_environment", {}).get("jax_backend") == "cpu"
        and reproduction.get("cpu_environment", {}).get("device_platforms")
        == ["cpu"]
    )
    base_runner_text = BASE_RUNNER.read_text(encoding="utf-8")
    checks = {
        "formal_result_exact": formal_exact,
        "reproduction_exact": reproduction_exact,
        "all_1024_cells_present_unique": len(cells) == 1024
        and len(unique) == 1024,
        "cpu_label_only_count_exact": len(cpu_label_only) == 100,
        "behavior_failure_count_exact": len(behavior_failures) == 924,
        "runner_exception_count_exact": len(exceptions) == 160,
        "exception_condition_count_exact": len(exception_conditions) == 10,
        "v103_cpu_string_assumption_present": (
            'all("CpuDevice" in value' in base_runner_text
        ),
        "unguarded_missing_com_readback_expression_present": (
            'nominal.get("torso_body_ipos_m", [])' in base_runner_text
            and "+ offset" in base_runner_text
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    value = {
        "schema_version": "winner_v106.response_gate_attribution.v1",
        "status": (
            "HOLD_WINNER_V106_V105_POLICY_AND_V103_EVALUATOR"
            if not failed
            else "INVALID_WINNER_V106_RESPONSE_GATE_ATTRIBUTION"
        ),
        "decision": (
            "AUTHORIZE_EVALUATOR_CORRECTION_AND_STAGE_BOUNDARY_DIAGNOSTIC"
            if not failed
            else "NO_FOLLOWUP_AUTHORIZED"
        ),
        "failed_checks": failed,
        "checks": checks,
        "formal_result": {
            "sha256": sha256(FORMAL_RESULT),
            "status": formal["status"],
            "decision": formal["decision"],
            "robot_clearance": formal["robot_clearance"],
            "cells": formal["cells"],
            "passing_cells": formal["passing_cells"],
            "wall_seconds": formal["wall_seconds"],
        },
        "raw_cell_evidence": {
            "cells": len(cells),
            "bytes": cell_bytes,
            "identity_manifest_sha256": canonical_sha256(identities),
            "cpu_label_only_cells": len(cpu_label_only),
            "behavior_failure_cells": len(behavior_failures),
            "runner_exception_cells": len(exceptions),
            "runner_exception_conditions": exception_conditions,
            "per_checkpoint": per_checkpoint,
        },
        "causal_attribution": {
            "policy_failure": {
                "present": True,
                "evidence": (
                    "924 cells have at least one non-cpu-only failure; fixing "
                    "the evaluator cannot promote either checkpoint."
                ),
            },
            "cpu_detection_defect": {
                "present": True,
                "cause": (
                    "V103 requires the rendered device string to contain "
                    "'CpuDevice'; the verified Windows CPU renders TFRT_CPU_0."
                ),
                "policy_behavior_implicated": False,
            },
            "early_return_readback_defect": {
                "present": True,
                "cause": (
                    "The simulator correctly returns "
                    "HOLD_RESPONSE_CALIBRATION_PREFIX without env readback, "
                    "then the base classifier broadcasts an empty COM vector "
                    "against the planned three-vector."
                ),
                "underlying_policy_or_calibration_failure_present": True,
                "policy_behavior_implicated": True,
            },
        },
        "prospective_correction": {
            "verify_cpu_from_backend_and_device_platforms": True,
            "classify_early_simulator_returns_without_readback_broadcasts": True,
            "preserve_all_thresholds_and_matrix_cells": True,
            "do_not_reinterpret_v103": True,
            "run_stage_boundary_diagnostic_before_training": True,
            "hosted_retry_authorized": False,
        },
        "input_hashes": {
            "formal_result": sha256(FORMAL_RESULT),
            "com_prefix_reproduction": sha256(REPRODUCTION),
            "formal_runner": sha256(FORMAL_RUNNER),
            "base_runner": sha256(BASE_RUNNER),
        },
        "authority": {
            "evaluator_correction_authorized": not failed,
            "stage_boundary_diagnostic_authorized": not failed,
            "hosted_training_authorized": False,
            "checkpoint_selection_authorized": False,
            "gate5_authorized": False,
            "robot_clearance": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "# Winner-v106 response-gate attribution\n\n"
        f"Status: `{value['status']}`\n\n"
        "The completed V103 matrix cannot select either V105 checkpoint. "
        "The evaluator has two defects, but they do not explain away the "
        "policy failure: 924/1,024 cells have a non-CPU-label failure. The "
        "negative-X COM cases genuinely terminate during the unscored "
        "calibration prefix; the readback validator then masks that status "
        "with a broadcasting exception. The next authorized work is a "
        "versioned evaluator correction and a small stage-boundary diagnostic. "
        "No hosted training, checkpoint selection, Gate 5, or robot action is "
        "authorized by this attribution.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(args.output)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
