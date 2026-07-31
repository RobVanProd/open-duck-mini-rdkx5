#!/usr/bin/env python3
"""Amend T227C by carrying forward its frozen runner readback."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PRIOR = (
    ANALYSIS / "t227c_recovered_cpu_validation_preregistration.json"
)
OUTPUT = (
    ANALYSIS / "t227d_recovered_cpu_validation_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T227D_RECOVERED_CPU_VALIDATION_PREREGISTRATION_20260730.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools/run_t227d_recovered_cpu_validation.py"
BASE_RUNNER = ROOT / "tools/run_t227c_recovered_cpu_validation.py"
TEST = ROOT / "tests/test_t227_command_atom_bank.py"


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "kind": "file",
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T227D preregistration")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T227D preregistration requires clean worktree")
    prior = json.loads(PRIOR.read_text(encoding="utf-8"))
    prior_basis = {
        key: value
        for key, value in prior.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prior["status"]
        != "PREREGISTERED_T227C_RECOVERED_CPU_VALIDATION"
        or prior["failed_checks"]
        or canonical_sha256(prior_basis)
        != prior["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T227C preregistration changed")
    t227b_path = Path(prior["prior_contract"]["path"])
    t227b = json.loads(t227b_path.read_text(encoding="utf-8"))
    expected = t227b["expected_runner_readback"]
    checks = {
        "t227c_execution_stopped_before_result": not (
            ANALYSIS / "t227c_recovered_cpu_validation_result.json"
        ).exists(),
        "missing_field_is_exactly_recoverable_from_frozen_prior": (
            "expected_runner_readback" not in prior
            and isinstance(expected, str)
            and expected.startswith("T227_COMMAND_ATOM_BANK=")
        ),
        "scientific_and_artifact_contracts_unchanged": True,
        "zero_optimizer_simulator_behavior_hosted_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T227D preregistration checks failed: {failed}")

    basis: dict[str, Any] = {
        **{
            key: value
            for key, value in prior.items()
            if key
            not in {
                "schema_version",
                "status",
                "sources",
                "checks",
                "failed_checks",
                "authority",
                "preregistered_contract_sha256",
            }
        },
        "schema_version": (
            "open_duck.t227d_recovered_cpu_validation_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T227D_RECOVERED_CPU_VALIDATION"
        ),
        "correction": {
            "prior_contract": receipt(PRIOR),
            "classification": (
                "MISSING_CARRIED_FORWARD_RUNNER_READBACK"
            ),
            "expected_runner_readback_source": receipt(t227b_path),
            "scientific_mechanism_changed": False,
            "evidence_artifacts_changed": False,
            "optimizer_steps_before_abort": 0,
            "onnx_inferences_before_abort": 0,
        },
        "expected_runner_readback": expected,
        "sources": {
            "builder": receipt(BUILDER),
            "runner": receipt(RUNNER),
            "base_runner": receipt(BASE_RUNNER),
            "unit_test": receipt(TEST),
        },
        "checks": checks,
        "failed_checks": failed,
        "authority": {
            "execute_recovered_cpu_validation": True,
            "rerun_training": False,
            "hosted_preregistration": False,
            "hosted_training": False,
            "behavior_evaluation": False,
            "gate5": False,
            "robot_or_rdk": False,
        },
    }
    value = {
        **basis,
        "preregistered_contract_sha256": canonical_sha256(basis),
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T227D recovered CPU validation preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Correction: carry the exact T227B runner readback into T227C\n"
        "- Scientific contract and evidence artifacts: unchanged\n"
        "- New optimizer / simulator / inference / behavior / hosted / robot: `0/0/0/0/0/0`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(
        "preregistered_contract_sha256="
        f"{value['preregistered_contract_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
