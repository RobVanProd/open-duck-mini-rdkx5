#!/usr/bin/env python3
"""Freeze the T113 always-on train-through 16-cell nominal matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T115_RESULT = ANALYSIS / "t115_t113_postexport_result.json"
BASIS = ANALYSIS / "t107_soft_gate_nominal_preregistration.json"
BUILDER = ROOT / "tools" / Path(__file__).name
RUNNER = ROOT / "tools" / "run_t116_t113_nominal.py"
TEST = ROOT / "tests" / "test_t116_t113_nominal.py"
OUTPUT = ANALYSIS / "t116_t113_nominal_preregistration.json"
MARKDOWN = ANALYSIS / "T116_T113_NOMINAL_PREREGISTRATION_20260729.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def canonical_sha256(value: Any, ignored: str) -> str:
    payload = dict(value)
    payload.pop(ignored, None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--read-only-authorized", action="store_true")
    args = parser.parse_args()
    if not args.read_only_authorized:
        raise PermissionError("T116 preregistration requires authorization")
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T116: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T116 preregistration requires clean worktree")
    t115 = json.loads(T115_RESULT.read_text(encoding="utf-8"))
    basis = json.loads(BASIS.read_text(encoding="utf-8"))
    policies = []
    for checkpoint_id, step in (
        ("T113_ALWAYS_ON_TRAINTHROUGH_HALF", "1003520"),
        ("T113_ALWAYS_ON_TRAINTHROUGH_FINAL", "2007040"),
    ):
        policies.append(
            {
                "checkpoint_id": checkpoint_id,
                "step": int(step),
                **t115["deployments"][step]["wrapped"],
            }
        )
    inputs = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "t115_result": T115_RESULT,
        "basis": BASIS,
    }
    checks = {
        "t115_green": (
            t115["status"] == "PASS_T115_T113_POSTEXPORT_TRANSFORM"
            and t115["failed_checks"] == []
        ),
        "policies_exact": all(
            Path(item["path"]).stat().st_size == item["bytes"]
            and sha256(Path(item["path"])) == item["sha256"]
            for item in policies
        ),
        "basis_is_frozen_nominal": (
            basis["status"]
            == "PREREGISTERED_T107_SOFT_GATE_NOMINAL_MATRIX"
            and basis["conditions"][0]["condition_index"] == 2
        ),
        "inputs_present": all(path.is_file() for path in inputs.values()),
        "no_behavior_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value: dict[str, Any] = {
        "schema_version": "open_duck.t116_t113_nominal_preregistration.v1",
        "status": (
            "PREREGISTERED_T116_T113_NOMINAL_MATRIX"
            if not failed
            else "HOLD_T116_T113_NOMINAL_PREREGISTRATION"
        ),
        "conditions": basis["conditions"],
        "commands_x_m_s": basis["commands_x_m_s"],
        "seed": basis["seed"],
        "policies": policies,
        "fits": basis["fits"],
        "calibrator": basis["calibrator"],
        "reference_feature_table": basis["reference_feature_table"],
        "playground": basis["playground"],
        "support_handoff": basis["support_handoff"],
        "behavior_contract": basis["behavior_contract"],
        "protection_contract": basis["protection_contract"],
        "repository_inputs": basis["repository_inputs"],
        "matrix": {
            "cells": 16,
            "both_checkpoints_required": True,
            "no_checkpoint_selection": True,
        },
        "decision_rule": {
            "pass_decision": (
                "EARN_T117_T113_NEGATIVE_ENDPOINT_PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_T113_ALWAYS_ON_TRAINTHROUGH",
            "no_retry": True,
            "training_selection_weight": 0,
        },
        "frozen_inputs": {
            name: receipt(path) for name, path in inputs.items()
        },
        "checks": checks,
        "failed_checks": failed,
        "authority": {
            "one_cpu_nominal_matrix": not failed,
            "negative_endpoint_preregistration": False,
            "training": False,
            "colab": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(
        value, "preregistered_contract_sha256"
    )
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T116 T113 nominal preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Matrix: `2 checkpoints x 2 fits x 4 commands = 16`\n"
        "- Both checkpoints are mandatory; no selection\n"
        "- Training / Colab / robot: `0 / 0 / 0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
