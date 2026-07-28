#!/usr/bin/env python3
"""Preregister T78's exact frozen deployment transforms."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
VALIDATION = ANALYSIS / "t78_recovered_training_validation.json"
T31_PREREGISTRATION = (
    ANALYSIS / "t31_action_margin_trainthrough_cpu_preregistration.json"
)
T31_RESULT = ANALYSIS / "t31_action_margin_trainthrough_cpu_result.json"
OUTPUT = ANALYSIS / "t79_t78_postexport_preregistration.json"
MARKDOWN = ANALYSIS / "T79_T78_POSTEXPORT_PREREGISTRATION_20260728.md"
RAW_ROOT = Path(
    "D:/CodexArtifacts/open-duck-policy/t78_extracted_20260728/"
    "t78_endpoint_joint_adapter_continuation/training"
)
EXPECTED_STEPS = [0, 1_003_520, 2_007_040]
SOURCE_PATHS = (
    "tools/run_t79_t78_postexport_transform.py",
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
            raise FileExistsError(f"refusing to overwrite T79: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        text=True,
    ).strip():
        raise RuntimeError("T79 preregistration requires a clean worktree")
    validation = json.loads(VALIDATION.read_text(encoding="utf-8"))
    t31_prereg = json.loads(
        T31_PREREGISTRATION.read_text(encoding="utf-8")
    )
    t31 = json.loads(T31_RESULT.read_text(encoding="utf-8"))
    graphs = sorted(RAW_ROOT.glob("*.onnx"), key=graph_step)
    steps = [graph_step(path) for path in graphs]
    raw_graphs = {str(graph_step(path)): sha256(path) for path in graphs}
    validation_graphs = {
        str(int(row["step"])): row["sha256"]
        for row in validation["exports"]["onnx"]
    }
    source_hashes = {name: sha256(ROOT / name) for name in SOURCE_PATHS}
    checks = {
        "t78_recovered_training_validation_green": (
            validation["status"]
            == "PASS_T78_RECOVERED_TRAINING_VALIDATION"
            and validation["failed_checks"] == []
            and validation["authority"][
                "postexport_transform_preregistration_authorized"
            ]
        ),
        "exact_three_t78_exports": steps == EXPECTED_STEPS,
        "raw_export_hashes_match_cpu_validation": (
            raw_graphs == validation_graphs
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
        "all_transform_sources_present": (
            len(source_hashes) == len(SOURCE_PATHS)
        ),
        "behavior_not_run": True,
        "robot_or_rdk_access_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, value in checks.items() if not value)
    value: dict[str, Any] = {
        "schema_version": "open_duck.t79_t78_postexport_preregistration.v1",
        "status": (
            "PREREGISTERED_T79_T78_POSTEXPORT_TRANSFORM"
            if not failed
            else "HOLD_T79_T78_POSTEXPORT_TRANSFORM"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {
            "t78_validation": sha256(VALIDATION),
            "t31_preregistration": sha256(T31_PREREGISTRATION),
            "t31_result": sha256(T31_RESULT),
        },
        "source_hashes": source_hashes,
        "raw_root": str(RAW_ROOT.resolve()),
        "raw_graphs": raw_graphs,
        "frozen_chain": [
            "v121_actual_centered_guard",
            "x0_command_deadband",
            "v121_source_trained_rate_projection",
            "diagnostic_context_abi_noop",
            "support_homeomorphism_and_external_physical_rate_projection",
            "strict_0p98_two_output_action_margin",
        ],
        "golden_requirement": (
            "use the hash-frozen T31 transform implementation and require "
            "every deployment sub-contract on every T78 export"
        ),
        "postupdate_steps": EXPECTED_STEPS[1:],
        "decision": (
            "RUN_ONE_CPU_ONLY_T79_POSTEXPORT_TRANSFORM"
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
            "robustness_evaluation": False,
            "checkpoint_selection": False,
            "deployment": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "robot_clearance": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T79 T78 post-export preregistration",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                "- Three raw exports must match T78 CPU validation",
                "- Identical frozen deployment chain for 0/half/final",
                "- Optimizer/behavior/Gate5/robot authority: `0/0/0/0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
