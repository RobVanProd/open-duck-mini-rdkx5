#!/usr/bin/env python3
"""Freeze read-only recovery of T112's completed CPU smoke."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

try:
    from tools import (
        build_t112_always_on_trainthrough_preregistration as t112,
    )
except ModuleNotFoundError:
    import build_t112_always_on_trainthrough_preregistration as t112


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "t112b_cpu_recovery_preregistration.json"
MARKDOWN = ANALYSIS / "T112B_CPU_RECOVERY_PREREGISTRATION_20260729.md"
T112_PREREG = ANALYSIS / "t112_always_on_trainthrough_preregistration.json"
T112_RESULT = ANALYSIS / "t112_always_on_trainthrough_result.json"
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/t112_always_on_trainthrough_cpu_v1"
)
SMOKE = WORK / "smoke"
CPU_SOURCE = WORK / "t100c_half_cpu_remap"
EXPECTED = WORK / "t100c_half_expected_always_on.onnx"
LOG = WORK / "training.log"

SOURCE_FILES = {
    "builder": Path(__file__).resolve(),
    "runner": ROOT / "tools" / "run_t112b_cpu_recovery.py",
    "test": ROOT / "tests" / "test_t112b_cpu_recovery.py",
    "original_t112_runner": (
        ROOT / "tools" / "run_t112_always_on_trainthrough_cpu_contract.py"
    ),
    "original_t112_preregistration": T112_PREREG,
}


def validate_t112_prereg(value: dict[str, Any]) -> None:
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        value["status"]
        != "PREREGISTERED_T112_ALWAYS_ON_TRAINTHROUGH_CPU_CONTRACT"
        or value["failed_checks"]
        or t112.canonical_sha256(basis)
        != value["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T112 preregistration identity changed")


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T112B prereg: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T112B preregistration requires clean worktree")

    original = json.loads(T112_PREREG.read_text(encoding="utf-8"))
    validate_t112_prereg(original)
    checkpoints = sorted(path for path in SMOKE.iterdir() if path.is_dir())
    graphs = sorted(SMOKE.glob("*.onnx"))
    checks = {
        "original_preregistration_valid": True,
        "original_result_absent": not T112_RESULT.exists(),
        "completed_exports_exact": (
            [int(path.name.rsplit("_", 1)[1]) for path in checkpoints]
            == [0, 1024]
            and [int(path.stem.rsplit("_", 1)[1]) for path in graphs]
            == [0, 1024]
        ),
        "training_readback_exact": (
            "T98_HIDDEN_EXPERT_CONTINUATION="
            "strata=8,broad=1,isolated=7,"
            "gate=always_on,"
            "actor_updates=negative_adapter_location_only"
            in LOG.read_text(encoding="utf-8", errors="replace")
            and "Saving checkpoint (step: 0)" in LOG.read_text(
                encoding="utf-8", errors="replace"
            )
            and "Saving checkpoint (step: 1024)" in LOG.read_text(
                encoding="utf-8", errors="replace"
            )
        ),
        "key_mismatch_static_attribution": (
            "prereg[\"assets\"][\"t97_preregistration\"]"
            in SOURCE_FILES["original_t112_runner"].read_text(
                encoding="utf-8"
            )
            or "prereg[\"assets\"][\"t97_preregistration\"]"
            in (
                ROOT / "tools" / "run_t98_hidden_expert_cpu_contract.py"
            ).read_text(encoding="utf-8")
        )
        and "trace_population" in original["assets"],
        "recovery_is_read_only": True,
        "no_additional_optimizer_behavior_hosted_or_robot_execution": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T112B preregistration checks failed: {failed}")

    value: dict[str, Any] = {
        "schema_version": "open_duck.t112b_cpu_recovery_preregistration.v1",
        "status": "PREREGISTERED_T112B_READ_ONLY_CPU_RECOVERY",
        "question": (
            "Do the already-produced T112 step-0 and step-1024 artifacts "
            "pass the preregistered CPU contract when the frozen trace asset "
            "is routed under the verifier's inherited key?"
        ),
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "attribution": {
            "classification": "POST_TRAINING_VERIFIER_KEY_MISMATCH",
            "optimizer_completed": True,
            "exports_completed": [0, 1024],
            "selection_or_contract_judgment_completed": False,
            "mismatch": {
                "frozen_asset_key": "trace_population",
                "inherited_helper_key": "t97_preregistration",
            },
            "training_semantics_affected": False,
            "export_bytes_affected": False,
        },
        "recovery": {
            "additional_optimizer_steps": 0,
            "additional_simulator_behavior_steps": 0,
            "additional_hosted_compute_units": 0,
            "mutation_of_recovered_artifacts": False,
            "contract_thresholds": original["thresholds"],
            "decision_rule": original["decision_rule"],
        },
        "sources": {
            name: t112.file_receipt(path)
            for name, path in SOURCE_FILES.items()
        },
        "assets": {
            "original_contract": t112.file_receipt(T112_PREREG),
            "source_checkpoint": original["assets"]["source_checkpoint"],
            "source_raw_onnx": original["assets"]["source_raw_onnx"],
            "cpu_topology_template": original["assets"][
                "cpu_topology_template"
            ],
            "trace_population": original["assets"]["trace_population"],
            "cpu_remapped_source": t112.directory_receipt(CPU_SOURCE),
            "expected_always_on_graph": t112.file_receipt(EXPECTED),
            "training_log": t112.file_receipt(LOG),
            "checkpoints": [
                t112.directory_receipt(path) for path in checkpoints
            ],
            "graphs": [t112.file_receipt(path) for path in graphs],
        },
        "checks": {name: bool(passed) for name, passed in checks.items()},
        "failed_checks": failed,
        "authority": {
            "read_only_recovery_validation": True,
            "additional_optimizer_steps": False,
            "hosted_preregistration": False,
            "hosted_training": False,
            "behavior_evaluation": False,
            "policy_promotion": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    value["preregistered_contract_sha256"] = t112.canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T112B read-only CPU recovery preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Attribution: post-training verifier key mismatch",
                "- Existing exports: step 0 and step 1,024, hash-frozen",
                "- Additional optimizer / behavior / hosted / robot: `0/0/0/0`",
                "- Recovery may only apply the original frozen thresholds.",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
