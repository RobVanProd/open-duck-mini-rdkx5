#!/usr/bin/env python3
"""Freeze T23 nominal reclassification under the already-reviewed T5 gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "t26_t23_corrected_nominal_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T26_T23_CORRECTED_NOMINAL_PREREGISTRATION_20260726.md"
)
RUN_ROOT = Path(
    r"D:\CodexArtifacts\open-duck-policy\t25b_t23_nominal_run_v1"
)

REPOSITORY_INPUTS = {
    "t5_preregistration": (
        ANALYSIS / "t5_actuator_protection_reanalysis_preregistration.json"
    ),
    "t5_result": ANALYSIS / "t5_actuator_protection_reanalysis_result.json",
    "t25b_result": ANALYSIS / "t25b_t23_nominal_behavior_result.json",
    "runner": ROOT / "tools" / "run_t26_t23_corrected_nominal.py",
}


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


def line_count(path: Path) -> int:
    with path.open("rb") as stream:
        return sum(1 for _ in stream)


def run_manifest(root: Path) -> dict[str, Any]:
    files = sorted(
        [
            path
            for path in root.rglob("*")
            if path.is_file()
            and (
                (path.parent.name == "cells" and path.suffix == ".json")
                or (path.parent.name == "traces" and path.suffix == ".jsonl")
            )
        ],
        key=lambda path: path.relative_to(root).as_posix(),
    )
    entries = []
    for path in files:
        entry = {
            "relative_path": path.relative_to(root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        if path.suffix == ".jsonl":
            entry["rows"] = line_count(path)
        entries.append(entry)
    return {
        "root": str(root.resolve()),
        "files": entries,
        "cell_files": sum(
            entry["relative_path"].startswith("cells/") for entry in entries
        ),
        "trace_files": sum(
            entry["relative_path"].startswith("traces/") for entry in entries
        ),
        "manifest_sha256": canonical_sha256(entries),
    }


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T26 preregistration")

    missing_inputs = [
        name for name, path in REPOSITORY_INPUTS.items() if not path.is_file()
    ]
    repository_inputs = {
        name: {
            "path": str(path.resolve()),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for name, path in REPOSITORY_INPUTS.items()
        if path.is_file()
    }
    manifest = run_manifest(RUN_ROOT) if RUN_ROOT.is_dir() else None
    t5_prereg = (
        load_json(REPOSITORY_INPUTS["t5_preregistration"])
        if REPOSITORY_INPUTS["t5_preregistration"].is_file()
        else {}
    )
    t5_result = (
        load_json(REPOSITORY_INPUTS["t5_result"])
        if REPOSITORY_INPUTS["t5_result"].is_file()
        else {}
    )
    t25b = (
        load_json(REPOSITORY_INPUTS["t25b_result"])
        if REPOSITORY_INPUTS["t25b_result"].is_file()
        else {}
    )
    checks = {
        "t5_mis_specification_result_passed": (
            t5_result.get("status")
            == "PASS_T5_MIS_SPECIFIED_INSTANTANEOUS_CONSTRAINT"
        ),
        "t25b_is_valid_complete_behavior_result": (
            t25b.get("status")
            == "PASS_T25B_T23_NOMINAL_BEHAVIOR_VALID_RESULT"
            and t25b.get("summary", {}).get("cells") == 16
            and not t25b.get("failed_validity_checks")
        ),
        "raw_matrix_exists": manifest is not None,
        "raw_matrix_has_16_cells_and_traces": (
            manifest is not None
            and manifest["cell_files"] == 16
            and manifest["trace_files"] == 16
        ),
        "repository_inputs_present": not missing_inputs,
        "t5_duration_contract_available": bool(
            t5_prereg.get("corrected_protection_contract")
        ),
    }
    failed_checks = [name for name, passed in checks.items() if not passed]
    status = (
        "PREREGISTERED_T26_T23_CORRECTED_NOMINAL_RECLASSIFICATION"
        if not failed_checks
        else "HOLD_T26_T23_CORRECTED_NOMINAL_PREREGISTRATION"
    )
    payload = {
        "schema_version": (
            "open_duck.t26_t23_corrected_nominal_preregistration.v1"
        ),
        "status": status,
        "question": (
            "Does the complete valid T25B nominal matrix pass persistently "
            "when only its obsolete one-tick stall checks are replaced by "
            "the already-reviewed T5 manufacturer-duration protections?"
        ),
        "checks": checks,
        "failed_checks": failed_checks,
        "repository_inputs": repository_inputs,
        "external_run_manifest": manifest,
        "frozen_reclassification": {
            "expected_cells": 16,
            "expected_checkpoints": [
                "T23_SUPPORT_HALF",
                "T23_SUPPORT_FINAL",
            ],
            "cells_per_checkpoint": 8,
            "old_instantaneous_failure_reasons_removed": [
                "current_peak_at_most_2p5",
                "torque_peak_at_most_1p91229675_nm",
            ],
            "corrected_protection_contract": t5_prereg.get(
                "corrected_protection_contract"
            ),
            "all_other_failure_reasons_preserved": True,
            "all_original_behavior_metrics_preserved": True,
            "simulation_ticks": 0,
            "optimizer_steps": 0,
        },
        "decision_rule": {
            "pass": (
                "all 16 frozen cells pass the T5 duration protections and "
                "retain zero non-protection failure reasons; both frozen "
                "checkpoints must independently pass all eight cells"
            ),
            "pass_decision": (
                "EARN_T23_FULL_ROBUSTNESS_MATRIX_PREREGISTRATION"
            ),
            "fail_decision": (
                "HOLD_T23_AND_ATTRIBUTE_CORRECTED_NOMINAL_FAILURE"
            ),
            "no_checkpoint_cherry_pick": True,
        },
        "authority": {
            "offline_read_only_reanalysis": True,
            "new_simulation_or_behavior_cells": False,
            "training_authorized": False,
            "robustness_execution_authorized": False,
            "gate5_authorized": False,
            "rdkx5_or_robot": False,
        },
    }
    payload["preregistered_contract_sha256"] = canonical_sha256(
        {
            "repository_inputs": repository_inputs,
            "external_run_manifest": {
                "root": manifest["root"] if manifest else None,
                "manifest_sha256": (
                    manifest["manifest_sha256"] if manifest else None
                ),
                "cell_files": manifest["cell_files"] if manifest else None,
                "trace_files": manifest["trace_files"] if manifest else None,
            },
            "frozen_reclassification": payload["frozen_reclassification"],
            "decision_rule": payload["decision_rule"],
        }
    )
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# T26 T23 corrected nominal preregistration\n\n"
        f"- Status: `{status}`\n"
        f"- Contract SHA-256: `{payload['preregistered_contract_sha256']}`\n"
        "- Input: the complete, valid 16-cell T25B matrix.\n"
        "- Only change: replace the obsolete one-tick stall checks with the "
        "already-reviewed T5 100-tick manufacturer protections.\n"
        "- No simulation, training, checkpoint selection, Gate 5, or robot "
        "action is authorized.\n",
        encoding="utf-8",
    )
    print(status)
    print(f"contract_sha256={payload['preregistered_contract_sha256']}")
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if status.startswith("PREREGISTERED_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
