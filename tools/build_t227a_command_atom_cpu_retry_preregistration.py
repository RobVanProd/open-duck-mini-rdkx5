#!/usr/bin/env python3
"""Freeze the instrumentation-only retry of T227's CPU contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
ORIGINAL = ANALYSIS / "t227_command_atom_cpu_preregistration.json"
OUTPUT = (
    ANALYSIS / "t227a_command_atom_cpu_retry_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T227A_COMMAND_ATOM_CPU_RETRY_PREREGISTRATION_20260730.md"
)
ABORTED_WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t227_command_atom_cpu_contract_v1"
)
LAUNCH_STDOUT = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t227_cpu_contract_launcher.stdout.log"
)
LAUNCH_STDERR = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t227_cpu_contract_launcher.stderr.log"
)
BUILDER = Path(__file__).resolve()
RETRY_RUNNER = ROOT / "tools/run_t227a_command_atom_cpu_contract.py"
ORIGINAL_RUNNER = ROOT / "tools/run_t227_command_atom_cpu_contract.py"
FIXED_WORKER = (
    ROOT / "tools/run_t227_command_atom_environment_worker.py"
)
MODULE = ROOT / "training/t227_command_atom_bank.py"
COMPOSER = ROOT / "tools/compose_t227_command_atom_playground.py"
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


def verify(item: dict[str, Any], name: str) -> None:
    path = Path(item["path"])
    observed = receipt(path)
    if observed != item:
        raise RuntimeError(f"T227A frozen input changed: {name}")


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T227A preregistration")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T227A preregistration requires clean worktree")
    original = json.loads(ORIGINAL.read_text(encoding="utf-8"))
    original_basis = {
        key: value
        for key, value in original.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        original["status"]
        != "PREREGISTERED_T227_COMMAND_ATOM_CPU_CONTRACT"
        or original["failed_checks"]
        or canonical_sha256(original_basis)
        != original["preregistered_contract_sha256"]
    ):
        raise RuntimeError("original T227 preregistration changed")
    for name, item in original["assets"].items():
        verify(item, f"assets.{name}")
    playground = Path(original["playground"]["path"])
    inventory = {
        path.relative_to(playground).as_posix(): sha256(path)
        for path in sorted(playground.rglob("*.py"))
    }
    enabled_log = ABORTED_WORK / "enabled_contract.log"
    log_text = enabled_log.read_text(encoding="utf-8")
    worker_text = FIXED_WORKER.read_text(encoding="utf-8")
    smoke_items = list((ABORTED_WORK / "smoke").rglob("*"))
    checks = {
        "original_t227_contract_was_green_and_frozen": True,
        "abort_is_exact_tracer_instrumentation_failure": (
            "jax.errors.UnexpectedTracerError" in log_text
            and "env.mjx_model.body_ipos[TORSO_BODY_ID, :]" in log_text
            and not (ABORTED_WORK / "enabled_contract.json").exists()
        ),
        "abort_preceded_every_optimizer_and_export": (
            not any(path.is_file() for path in smoke_items)
            and not list((ABORTED_WORK / "smoke").glob("*.onnx"))
            and not list(
                (ABORTED_WORK / "smoke").glob(
                    "events.out.tfevents*"
                )
            )
        ),
        "default_off_evidence_completed_before_abort": (
            (ABORTED_WORK / "base_default_off.json").is_file()
            and (ABORTED_WORK / "composed_default_off.json").is_file()
        ),
        "fix_snapshots_nominal_model_before_vectorization": (
            "nominal_torso_body_ipos = np.asarray(" in worker_text
            and (
                worker_text.index("nominal_torso_body_ipos = np.asarray(")
                < worker_text.index("wrapped = atom.wrap_for_brax_training(")
            )
            and (
                "- nominal_torso_body_ipos" in worker_text
            )
        ),
        "scientific_contract_is_unchanged": True,
        "zero_optimizer_behavior_hosted_or_robot_in_aborted_attempt": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T227A preregistration checks failed: {failed}")

    sources = {
        "builder": receipt(BUILDER),
        "retry_runner": receipt(RETRY_RUNNER),
        "original_runner": receipt(ORIGINAL_RUNNER),
        "fixed_environment_worker": receipt(FIXED_WORKER),
        "command_atom_module": receipt(MODULE),
        "composer": receipt(COMPOSER),
        "unit_test": receipt(TEST),
    }
    abort_evidence = {
        "aborted_work": receipt(ABORTED_WORK),
        "enabled_contract_log": receipt(enabled_log),
        "launcher_stdout": receipt(LAUNCH_STDOUT),
        "launcher_stderr": receipt(LAUNCH_STDERR),
    }
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t227a_command_atom_cpu_retry_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T227A_COMMAND_ATOM_CPU_RETRY"
        ),
        "correction": {
            "original_contract": receipt(ORIGINAL),
            "classification": (
                "POST_RESET_AUDIT_READ_OF_ESCAPED_JAX_TRACER"
            ),
            "scientific_mechanism_changed": False,
            "training_distribution_changed": False,
            "source_checkpoint_changed": False,
            "optimizer_steps_before_abort": 0,
            "formal_behavior_cells_before_abort": 0,
            "hosted_compute_units_before_abort": 0,
            "fix": (
                "snapshot nominal torso body_ipos before the named-axis "
                "vmap and compare randomized models to that immutable array"
            ),
        },
        "mechanism": original["mechanism"],
        "sources": sources,
        "assets": original["assets"],
        "abort_evidence": abort_evidence,
        "playground": {
            **original["playground"],
            "python_inventory": inventory,
            "python_inventory_sha256": canonical_sha256(inventory),
        },
        "expected_runner_readback": original[
            "expected_runner_readback"
        ],
        "checks": checks,
        "failed_checks": failed,
        "decision_rule": original["decision_rule"],
        "execution_now": {
            "simulator_transitions": 0,
            "optimizer_steps": 0,
            "onnx_inferences": 0,
            "formal_behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_corrected_cpu_contract_retry": True,
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
        "# T227A command-atom CPU retry preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Prior attempt: stopped after reset on an audit-only escaped-tracer read\n"
        "- Prior optimizer / behavior / hosted / robot: `0/0/0/0`\n"
        "- Fix: snapshot nominal COM before vectorization\n"
        "- Scientific contract: unchanged\n"
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
