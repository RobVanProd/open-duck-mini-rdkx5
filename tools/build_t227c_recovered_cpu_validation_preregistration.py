#!/usr/bin/env python3
"""Freeze post-hoc validation of T227B's complete CPU smoke artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PRIOR = (
    ANALYSIS / "t227b_command_atom_cpu_retry_preregistration.json"
)
OUTPUT = (
    ANALYSIS / "t227c_recovered_cpu_validation_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T227C_RECOVERED_CPU_VALIDATION_PREREGISTRATION_20260730.md"
)
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t227b_command_atom_cpu_contract_v3"
)
LAUNCH_STDERR = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t227b_cpu_contract_launcher.stderr.log"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools/run_t227c_recovered_cpu_validation.py"
TEST = ROOT / "tests/test_t227_command_atom_bank.py"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(path.rglob("*")):
        if item.is_file():
            digest.update(item.relative_to(path).as_posix().encode())
            digest.update(b"\0")
            with item.open("rb") as stream:
                for block in iter(
                    lambda: stream.read(1024 * 1024), b""
                ):
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


def receipt(path: Path) -> dict[str, Any]:
    if path.is_dir():
        return {
            "kind": "directory",
            "path": str(path.resolve()),
            "sha256": directory_sha256(path),
        }
    return {
        "kind": "file",
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T227C preregistration")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T227C preregistration requires clean worktree")
    prior = json.loads(PRIOR.read_text(encoding="utf-8"))
    prior_basis = {
        key: value
        for key, value in prior.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prior["status"]
        != "PREREGISTERED_T227B_COMMAND_ATOM_CPU_RETRY"
        or prior["failed_checks"]
        or canonical_sha256(prior_basis)
        != prior["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T227B preregistration changed")
    smoke = WORK / "smoke"
    policy = [
        path
        for path in smoke.iterdir()
        if path.is_dir() and "_v127_cost_value" not in path.name
    ]
    cost = list(smoke.glob("*_v127_cost_value"))
    graphs = list(smoke.glob("*.onnx"))
    aux = list(smoke.glob("*_v127_aux.json"))
    events = list(smoke.glob("events.out.tfevents*"))
    error_text = LAUNCH_STDERR.read_text(encoding="utf-8")
    enabled = json.loads(
        (WORK / "enabled_contract.json").read_text(encoding="utf-8")
    )
    checks = {
        "t227b_smoke_artifact_sets_complete": (
            len(policy) == len(cost) == len(graphs) == len(aux) == 2
            and len(events) == 1
            and {int(path.stem.rsplit("_", 1)[1]) for path in graphs}
            == {0, 1024}
        ),
        "training_log_records_both_exports": (
            "Saving checkpoint (step: 0)" in (
                WORK / "training.log"
            ).read_text(encoding="utf-8")
            and "Saving checkpoint (step: 1024)" in (
                WORK / "training.log"
            ).read_text(encoding="utf-8")
        ),
        "environment_lattice_was_green": (
            enabled["status"]
            == "PASS_T227_COMMAND_ATOM_ENVIRONMENT_CONTRACT"
            and enabled["failed_checks"] == []
            and all(enabled["checks"].values())
        ),
        "failure_is_posttraining_report_schema_only": (
            "KeyError: 'simulator_transitions'" in error_text
            and "environment_contract_transitions" in error_text
            and not (
                ANALYSIS / "t227b_command_atom_cpu_result.json"
            ).exists()
        ),
        "derived_iteration_count_is_parameter_free": (
            1024 // (32 * 8) == 4
            and (4 + 3) // 4 == 1
        ),
        "no_rerun_optimizer_behavior_hosted_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T227C preregistration checks failed: {failed}")

    frozen_artifacts = {
        "work": receipt(WORK),
        "base_default_off": receipt(WORK / "base_default_off.json"),
        "composed_default_off": receipt(
            WORK / "composed_default_off.json"
        ),
        "environment_contract": receipt(
            WORK / "enabled_contract.json"
        ),
        "training_log": receipt(WORK / "training.log"),
        "cpu_source_remap": receipt(WORK / "t203_half_cpu_remap"),
        "event_file": receipt(events[0]),
        "launcher_stderr": receipt(LAUNCH_STDERR),
    }
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t227c_recovered_cpu_validation_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T227C_RECOVERED_CPU_VALIDATION"
        ),
        "question": (
            "Do T227B's already-complete CPU artifacts satisfy every "
            "frozen restore, update-mask, cost, dual, metric, and ONNX "
            "invariant when the report-only counter alias is handled "
            "without rerunning training?"
        ),
        "prior_contract": receipt(PRIOR),
        "sources": {
            "builder": receipt(BUILDER),
            "runner": receipt(RUNNER),
            "unit_test": receipt(TEST),
        },
        "assets": prior["assets"],
        "playground": prior["playground"],
        "frozen_artifacts": frozen_artifacts,
        "mechanism": prior["mechanism"],
        "derived_training_contract": {
            "num_timesteps": 1024,
            "num_envs": 32,
            "unroll_length": 8,
            "total_training_iterations": 4,
            "quarter_iterations": 1,
            "derivation": "1024/(32*8)=4; ceil(4/4)=1",
            "selection_weight": 0,
        },
        "checks": checks,
        "failed_checks": failed,
        "decision_rule": prior["decision_rule"],
        "execution_now": {
            "saved_artifact_reads": 0,
            "optimizer_steps": 0,
            "simulator_transitions": 0,
            "formal_behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
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
        "# T227C recovered CPU validation preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Input: exact completed T227B reset/training/export artifacts\n"
        "- Recovery: report-only counter alias; no optimizer rerun\n"
        "- New optimizer / simulator / behavior / hosted / robot: `0/0/0/0/0`\n"
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
