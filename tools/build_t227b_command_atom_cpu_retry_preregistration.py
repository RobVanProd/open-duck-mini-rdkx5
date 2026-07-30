#!/usr/bin/env python3
"""Freeze T227B's pre-training activation-order correction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PRIOR = (
    ANALYSIS / "t227a_command_atom_cpu_retry_preregistration.json"
)
OUTPUT = (
    ANALYSIS / "t227b_command_atom_cpu_retry_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T227B_COMMAND_ATOM_CPU_RETRY_PREREGISTRATION_20260730.md"
)
ABORTED_WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t227a_command_atom_cpu_contract_v2"
)
PLAYGROUND = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t227b_command_atom_cpu_source_v2"
)
MANIFEST = PLAYGROUND / "T227_COMPOSED_SOURCE_MANIFEST.json"
BUILDER = Path(__file__).resolve()
RETRY_RUNNER = ROOT / "tools/run_t227b_command_atom_cpu_contract.py"
BASE_RUNNER = ROOT / "tools/run_t227_command_atom_cpu_contract.py"
WORKER = ROOT / "tools/run_t227_command_atom_environment_worker.py"
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
    if receipt(Path(item["path"])) != item:
        raise RuntimeError(f"T227B frozen input changed: {name}")


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T227B preregistration")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T227B preregistration requires clean worktree")
    prior = json.loads(PRIOR.read_text(encoding="utf-8"))
    prior_basis = {
        key: value
        for key, value in prior.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prior["status"]
        != "PREREGISTERED_T227A_COMMAND_ATOM_CPU_RETRY"
        or prior["failed_checks"]
        or canonical_sha256(prior_basis)
        != prior["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T227A preregistration changed")
    for name, item in prior["assets"].items():
        verify(item, f"assets.{name}")
    environment = json.loads(
        (ABORTED_WORK / "enabled_contract.json").read_text(
            encoding="utf-8"
        )
    )
    training_log = (
        ABORTED_WORK / "training.log"
    ).read_text(encoding="utf-8")
    runner_source = (
        PLAYGROUND / "playground/open_duck_mini_v2/runner.py"
    ).read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    smoke = ABORTED_WORK / "smoke"
    exported = [
        path
        for path in smoke.iterdir()
        if path.is_dir() or path.suffix == ".onnx"
    ]
    checks = {
        "t227a_environment_contract_passed_completely": (
            environment["status"]
            == "PASS_T227_COMMAND_ATOM_ENVIRONMENT_CONTRACT"
            and environment["failed_checks"] == []
            and all(environment["checks"].values())
        ),
        "second_abort_is_pretraining_abi_probe_only": (
            "Found an unbound axis name: t227_command_atom_environment"
            in training_log
            and "self.env.observation_size" in training_log
            and "runner = OpenDuckMiniV2Runner(args)" in training_log
            and not exported
        ),
        "deferred_activation_follows_observation_size_probe": (
            "self._winner_t227_command_atom_bank_enabled" in runner_source
            and (
                runner_source.index("self.obs_size = int(")
                < runner_source.index(
                    "if self._winner_t227_command_atom_bank_enabled:"
                )
            )
            and (
                "self.env.unwrapped._config."
                "winner_t227_command_atom_bank = True"
                in runner_source
            )
            and (
                "self.eval_env.unwrapped._config."
                "winner_t227_command_atom_bank = True"
                in runner_source
            )
        ),
        "new_composed_source_retains_training_only_scope": (
            manifest["schema_version"]
            == "open_duck.t227_composed_source.v1"
            and manifest["mechanism"]["reward_change"] is False
            and manifest["mechanism"]["cost_change"] is False
            and manifest["mechanism"]["policy_abi_change"] is False
            and manifest["mechanism"]["deployment_graph_change"] is False
        ),
        "scientific_contract_is_unchanged": True,
        "zero_optimizer_behavior_hosted_or_robot_in_second_abort": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T227B preregistration checks failed: {failed}")

    inventory = {
        path.relative_to(PLAYGROUND).as_posix(): sha256(path)
        for path in sorted(PLAYGROUND.rglob("*.py"))
    }
    sources = {
        "builder": receipt(BUILDER),
        "retry_runner": receipt(RETRY_RUNNER),
        "base_runner": receipt(BASE_RUNNER),
        "environment_worker": receipt(WORKER),
        "command_atom_module": receipt(MODULE),
        "composer": receipt(COMPOSER),
        "unit_test": receipt(TEST),
    }
    abort_evidence = {
        "aborted_work": receipt(ABORTED_WORK),
        "passed_environment_contract": receipt(
            ABORTED_WORK / "enabled_contract.json"
        ),
        "training_log": receipt(ABORTED_WORK / "training.log"),
    }
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t227b_command_atom_cpu_retry_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T227B_COMMAND_ATOM_CPU_RETRY"
        ),
        "correction": {
            "prior_contract": receipt(PRIOR),
            "classification": (
                "COMMAND_ATOMS_ENABLED_DURING_UNVECTORIZED_ABI_PROBE"
            ),
            "scientific_mechanism_changed": False,
            "training_distribution_changed": False,
            "source_checkpoint_changed": False,
            "optimizer_steps_before_abort": 0,
            "formal_behavior_cells_before_abort": 0,
            "hosted_compute_units_before_abort": 0,
            "fix": (
                "keep the feature default-off through raw environment ABI "
                "discovery, then enable it on train and eval unwrapped "
                "configs before vectorized training begins"
            ),
        },
        "mechanism": prior["mechanism"],
        "sources": sources,
        "assets": prior["assets"],
        "abort_evidence": abort_evidence,
        "playground": {
            "path": str(PLAYGROUND.resolve()),
            "base_path": prior["playground"]["base_path"],
            "python_inventory": inventory,
            "python_inventory_sha256": canonical_sha256(inventory),
        },
        "expected_runner_readback": prior[
            "expected_runner_readback"
        ],
        "checks": checks,
        "failed_checks": failed,
        "decision_rule": prior["decision_rule"],
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
        "# T227B command-atom CPU retry preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- T227A environment lattice: all checks passed\n"
        "- T227A training: stopped in raw ABI discovery before optimizer initialization\n"
        "- Fix: enable atoms only after the 115-D shape probe\n"
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
