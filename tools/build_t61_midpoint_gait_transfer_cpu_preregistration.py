#!/usr/bin/env python3
"""Freeze T61's midpoint-to-full transfer CPU smoke contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = (
    ANALYSIS
    / "t61_midpoint_gait_transfer_cpu_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T61_MIDPOINT_GAIT_TRANSFER_CPU_PREREGISTRATION_20260728.md"
)
T60 = ANALYSIS / "t60_t59_persistence_hold_attribution.json"
T56_VALIDATION = ANALYSIS / "t56_recovered_training_validation.json"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
COMPOSED = Path("D:/CodexProjects/Open_Duck_Playground-composed-t61-v1")
BASE = Path("D:/CodexProjects/Open_Duck_Playground-composed-t55-v2")
MANIFEST = COMPOSED / "T61_COMPOSED_SOURCE_MANIFEST.json"
CPU_TEMPLATE = Path(
    "D:/CodexArtifacts/open-duck-mini-rdkx5/"
    "winner-v119-transition-cpu-smoke-20260724/"
    "smoke/2026_07_24_150649_0"
)
T56_ROOT = Path(
    "D:/CodexArtifacts/open-duck-policy/t56_extracted_20260728/"
    "t56_dynamic_single_support_continuation"
)
BALANCE_FINAL = (
    T56_ROOT / "balance_training" / "2026_07_28_112206_1003520"
)
BALANCE_FINAL_ONNX = (
    T56_ROOT / "balance_training" / "2026_07_28_112206_1003520.onnx"
)
MODULE = ROOT / "patches" / "t61_midpoint_gait_transfer.py"
PATCH = ROOT / "patches" / "winner_t61_midpoint_gait_transfer.patch"
COMPOSER = (
    ROOT / "tools" / "compose_t61_midpoint_gait_transfer_playground.py"
)
RUNNER = (
    ROOT / "tools" / "run_t61_midpoint_gait_transfer_cpu_contract.py"
)
MECHANICS_TEST = ROOT / "tests" / "test_t61_midpoint_gait_transfer.py"
RESULT_TEST = (
    ROOT / "tests" / "test_t61_midpoint_gait_transfer_cpu_contract.py"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(
        candidate for candidate in path.rglob("*") if candidate.is_file()
    ):
        relative = item.relative_to(path).as_posix()
        digest.update(relative.encode())
        digest.update(b"\0")
        with item.open("rb") as stream:
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


def file_receipt(path: Path) -> dict[str, Any]:
    return {
        "kind": "file",
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def directory_receipt(path: Path) -> dict[str, Any]:
    return {
        "kind": "directory",
        "path": str(path.resolve()),
        "sha256": directory_sha256(path),
    }


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T61: {path}")
    t60 = json.loads(T60.read_text(encoding="utf-8"))
    t56 = json.loads(T56_VALIDATION.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    balance_checkpoints = {
        int(row["step"]): row["directory_sha256"]
        for row in t56["stages"]["balance"]["checkpoints"]
    }
    balance_graphs = {
        int(row["step"]): row["sha256"]
        for row in t56["stages"]["balance"]["onnx"]
    }
    sources = {
        "t60_attribution": file_receipt(T60),
        "t56_validation": file_receipt(T56_VALIDATION),
        "module": file_receipt(MODULE),
        "patch": file_receipt(PATCH),
        "composer": file_receipt(COMPOSER),
        "runner": file_receipt(RUNNER),
        "mechanics_test": file_receipt(MECHANICS_TEST),
        "result_test": file_receipt(RESULT_TEST),
        "composed_manifest": file_receipt(MANIFEST),
    }
    assets = {
        "cpu_topology_template": directory_receipt(CPU_TEMPLATE),
        "t56_balance_final_checkpoint": directory_receipt(BALANCE_FINAL),
        "t56_balance_final_onnx": file_receipt(BALANCE_FINAL_ONNX),
        "reference_features": file_receipt(REFERENCE),
    }
    python_inventory = {
        path.relative_to(COMPOSED).as_posix(): sha256(path)
        for path in sorted(COMPOSED.rglob("*.py"))
    }
    checks = {
        "t60_earned_only_t61_cpu_preregistration": (
            t60["status"]
            == "PASS_T60_T59_PERSISTENCE_HOLD_ATTRIBUTION"
            and t60["decision"]
            == "EARN_T61_MIDPOINT_GAIT_TRANSFER_CPU_CONTRACT_"
            "PREREGISTRATION_ONLY"
            and t60["failed_checks"] == []
            and not t60["authority"]["hosted_training"]
        ),
        "t56_recovered_training_green": (
            t56["status"] == "PASS_T56_RECOVERED_TRAINING_VALIDATION"
            and t56["failed_checks"] == []
        ),
        "balance_final_checkpoint_exact": (
            assets["t56_balance_final_checkpoint"]["sha256"]
            == balance_checkpoints[1_003_520]
        ),
        "balance_final_onnx_exact": (
            assets["t56_balance_final_onnx"]["sha256"]
            == balance_graphs[1_003_520]
        ),
        "cpu_template_exact": (
            assets["cpu_topology_template"]["sha256"]
            == t56["input_hashes"]["cpu_template"]
        ),
        "composed_manifest_exact": (
            manifest["schema_version"]
            == "open_duck.t61_composed_source.v1"
            and manifest["sources"]["module"]["sha256"]
            == sha256(MODULE)
            and manifest["sources"]["patch"]["sha256"] == sha256(PATCH)
        ),
        "all_sources_and_assets_present": all(
            Path(item["path"]).exists()
            for item in (*sources.values(), *assets.values())
        ),
        "no_behavior_hosted_or_robot_execution": True,
    }
    checks = {name: bool(passed) for name, passed in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t61_midpoint_gait_transfer_cpu_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T61_MIDPOINT_GAIT_TRANSFER_CPU_CONTRACT"
            if not failed
            else "HOLD_T61_MIDPOINT_GAIT_TRANSFER_CPU_PREREGISTRATION"
        ),
        "question": (
            "Does one fixed midpoint locomotion objective preserve the "
            "balance-first source through a 1,024-step CPU update and then "
            "restore the complete gait objective through a second exact "
            "1,024-step CPU update?"
        ),
        "causal_basis": {
            "t59": "10/16 green",
            "half": "x=0 2/2 green; moving 0/6 green",
            "final": "8/8 green",
            "half_failure": (
                "all six moving cells overshoot commanded mean velocity, "
                "then enter delayed positive-pitch collapse with tracking, "
                "rate, saturation, and contract checks green"
            ),
            "transition": (
                "T56 changes in one step from support-only reward to the "
                "complete clipped locomotion reward plus support"
            ),
            "selected_hypothesis": "abrupt transfer consolidation gap",
        },
        "mechanism": {
            "source": "exact recovered T56 balance-final checkpoint",
            "midpoint_stage": (
                "support_reward + 0.5 * complete_frozen_locomotion_reward"
            ),
            "midpoint_derivation": (
                "(0 balance locomotion weight + 1 full locomotion weight) "
                "/ 2; fixed before execution"
            ),
            "full_stage": (
                "complete frozen locomotion reward plus support_reward"
            ),
            "scalar_sweep": False,
            "policy_abi_change": False,
            "runtime_change": False,
            "deployment_graph_change": False,
        },
        "sources": sources,
        "assets": assets,
        "playground": {
            "path": str(COMPOSED.resolve()),
            "base_path": str(BASE.resolve()),
            "manifest_sha256": sha256(MANIFEST),
            "python_inventory": python_inventory,
            "python_inventory_sha256": canonical_sha256(
                python_inventory
            ),
        },
        "cpu_contract": {
            "midpoint_simulator_steps": 1024,
            "full_transfer_simulator_steps": 1024,
            "exports_per_stage": [0, 1024],
            "ppo_envs": 4,
            "required_checks": [
                "T56 balance-final restore exact",
                "midpoint step-zero ONNX byte-exact source ONNX",
                "T55/T61 default-off trajectories bit-exact",
                "both support-side metrics positive and finite",
                "both reward metrics positive and finite",
                "all actor and critic leaves update in both stages",
                "all trees and deployment graphs finite",
                "no observation/action ABI change",
            ],
        },
        "decision_rule": {
            "pass": (
                "Earn only a separately committed T62 hosted-training "
                "preregistration; do not launch compute."
            ),
            "fail": (
                "Close this exact midpoint mechanism without changing its "
                "coefficient, duration, source, or stage order."
            ),
            "hosted_training_earned_now": False,
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "cpu_simulator_steps": 0,
            "formal_behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_one_2048_step_cpu_contract": not failed,
            "hosted_preregistration": False,
            "hosted_training": False,
            "behavior_matrix": False,
            "checkpoint_selection": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    basis["preregistered_contract_sha256"] = canonical_sha256(basis)
    OUTPUT.write_text(
        json.dumps(basis, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T61 midpoint gait-transfer CPU preregistration",
                "",
                f"- Status: `{basis['status']}`",
                "- Source: exact recovered T56 balance-final checkpoint",
                "- Stage 1: 1,024 CPU steps at fixed 0.5 locomotion weight",
                "- Stage 2: 1,024 CPU steps at full locomotion weight",
                "- Both left and right support required",
                "- Scalar search / ABI / runtime changes: `0/0/0`",
                "- Hosted/behavior/Gate5/robot authority: `0/0/0/0`",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(basis["status"])
    print(f"failed_checks={failed}")
    print(f"sha256={sha256(OUTPUT)}")
    print(
        "preregistered_contract_sha256="
        f"{basis['preregistered_contract_sha256']}"
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
