#!/usr/bin/env python3
"""Preregister T129's exact hard-gated deployment transforms."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
VALIDATION = ANALYSIS / "t130_t129_recovered_training_validation.json"
RECOVERY = ANALYSIS / "t130d_step_zero_node_name_result.json"
T31_PREREGISTRATION = (
    ANALYSIS / "t31_action_margin_trainthrough_cpu_preregistration.json"
)
T31_RESULT = ANALYSIS / "t31_action_margin_trainthrough_cpu_result.json"
T128_RESULT = ANALYSIS / "t128_negative_only_expert_cpu_result.json"
OUTPUT = ANALYSIS / "t131_t129_postexport_preregistration.json"
MARKDOWN = ANALYSIS / "T131_T129_POSTEXPORT_PREREGISTRATION_20260729.md"
RAW_ROOT = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t129_colab_extracted_20260729/"
    "t129_negative_only_expert_continuation/training"
)
HARD_REFERENCE = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t100c_colab_extracted_20260728/"
    "t78_endpoint_joint_adapter_continuation/training/"
    "2026_07_29_023820_1003520.onnx"
)
EXPECTED_STEPS = [0, 1_003_520, 2_007_040]
SOURCE_PATHS = (
    "tools/run_t131_t129_postexport_transform.py",
    "tools/t131_restore_hard_expert_gate.py",
    "tools/run_t31_action_margin_trainthrough_cpu_smoke.py",
    "tools/run_t22_corrected_one_update_cpu_smoke.py",
    "tools/run_t20_support_trainthrough_one_update.py",
    "tools/build_t28_t23_action_margin_assets.py",
    "tools/build_ground_up_actual_centered_guard_screen.py",
    "tools/build_ground_up_command_deadband_repair.py",
    "tools/build_winner_v117_postguard_rate_projection_policies.py",
    "tools/build_t8_state_coherent_handoff_assets.py",
    "tools/t18_rate_coherent_support_onnx.py",
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


def graph_step(path: Path) -> int:
    return int(path.stem.rsplit("_", 1)[1])


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T131: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T131 preregistration requires clean worktree")

    validation = json.loads(VALIDATION.read_text(encoding="utf-8"))
    recovery = json.loads(RECOVERY.read_text(encoding="utf-8"))
    t31_prereg = json.loads(T31_PREREGISTRATION.read_text(encoding="utf-8"))
    t31 = json.loads(T31_RESULT.read_text(encoding="utf-8"))
    t128 = json.loads(T128_RESULT.read_text(encoding="utf-8"))
    graphs = sorted(RAW_ROOT.glob("*.onnx"), key=graph_step)
    steps = [graph_step(path) for path in graphs]
    raw_graphs = {str(graph_step(path)): sha256(path) for path in graphs}
    validation_graphs = {
        str(int(row["step"])): row["sha256"]
        for row in validation["exports"]["onnx"]
    }
    source_hashes = {name: sha256(ROOT / name) for name in SOURCE_PATHS}
    validation_checks_except_serialization = {
        name: passed
        for name, passed in validation["checks"].items()
        if name != "step_zero_raw_onnx_byte_exact"
    }
    checks = {
        "t129_recovered_validation_single_serialization_hold": (
            validation["status"]
            == "HOLD_T130_T129_RECOVERED_TRAINING_VALIDATION"
            and validation["failed_checks"]
            == ["step_zero_raw_onnx_byte_exact"]
            and all(validation_checks_except_serialization.values())
        ),
        "t130d_recovers_serialization_hold": (
            recovery["status"]
            == "PASS_T130D_STEP_ZERO_NODE_NAME_RECOVERY"
            and recovery["failed_checks"] == []
            and recovery["classification"]
            == "OPTIONAL_ONNX_NODE_NAME_METADATA_ONLY"
            and all(recovery["checks"].values())
        ),
        "exact_three_t129_exports": steps == EXPECTED_STEPS,
        "raw_export_hashes_match_cpu_validation": (
            raw_graphs == validation_graphs
        ),
        "t128_architecture_cpu_contract_green": (
            t128["status"]
            == "PASS_T128_NEGATIVE_ONLY_EXPERT_CPU_CONTRACT"
            and t128["failed_checks"] == []
        ),
        "t31_golden_chain_green": (
            t31["status"]
            == "PASS_T31_ACTION_MARGIN_TRAINTHROUGH_CPU_SMOKE"
            and t31["failed_checks"] == []
            and all(
                t31["checks"][name]
                for name in (
                    "both_margin_export_contracts_pass",
                    "both_physical_wrapper_contracts_pass",
                    "step_zero_context_abi_byte_exact",
                    "step_zero_pre_margin_wrapper_byte_exact",
                    "step_zero_margin_wrapper_byte_exact",
                    "step_zero_raw_onnx_byte_exact",
                )
            )
        ),
        "t31_frozen_assets_present": all(
            Path(item["path"]).exists()
            for item in t31_prereg["assets"].values()
        ),
        "hard_gate_step_zero_reference_present": HARD_REFERENCE.is_file(),
        "all_transform_sources_present": (
            len(source_hashes) == len(SOURCE_PATHS)
        ),
        "behavior_not_run": True,
        "robot_or_rdk_access_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, value in checks.items() if not value)
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t131_t129_postexport_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T131_T129_HARD_GATE_POSTEXPORT_TRANSFORM"
            if not failed
            else "HOLD_T131_T129_HARD_GATE_POSTEXPORT_TRANSFORM"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {
            "t130_validation": sha256(VALIDATION),
            "t130d_recovery": sha256(RECOVERY),
            "t31_preregistration": sha256(T31_PREREGISTRATION),
            "t31_result": sha256(T31_RESULT),
            "t128_result": sha256(T128_RESULT),
        },
        "source_hashes": source_hashes,
        "raw_root": str(RAW_ROOT.resolve()),
        "raw_graphs": raw_graphs,
        "hard_gate_step_zero_reference": str(HARD_REFERENCE.resolve()),
        "hard_gate_step_zero_reference_sha256": sha256(HARD_REFERENCE),
        "expected_source_node_counts": {
            "raw": 37,
            "guarded": 50,
            "deadbanded": 55,
            "deployed": 64,
        },
        "frozen_chain": [
            "restore_t98_hard_hidden_gate",
            "v121_actual_centered_guard",
            "x0_command_deadband",
            "v121_source_trained_rate_projection",
            "diagnostic_context_abi_noop",
            "support_homeomorphism_and_external_physical_rate_projection",
            "strict_0p98_two_output_action_margin",
        ],
        "postupdate_steps": EXPECTED_STEPS[1:],
        "decision": (
            "RUN_ONE_CPU_ONLY_T131_POSTEXPORT_TRANSFORM"
            if not failed
            else "HOLD_WITHOUT_TRANSFORM"
        ),
        "execution_now": {
            "onnx_graphs_transformed": 0,
            "optimizer_steps": 0,
            "simulator_locomotion_steps": 0,
            "formal_behavior_cells": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_cpu_only_postexport_transform": not failed,
            "behavior_evaluation": False,
            "checkpoint_selection": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T131 T129 post-export preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Three raw exports match recovered T129 validation\n"
        "- Hard negative-COM gate restored before frozen T31 chain\n"
        "- Step zero must exactly reproduce the frozen hard-gate graph\n"
        "- Optimizer / behavior / Gate 5 / robot: `0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
