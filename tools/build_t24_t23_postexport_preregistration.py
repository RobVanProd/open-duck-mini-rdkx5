#!/usr/bin/env python3
"""Preregister T23's exact post-export deployment transform."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
VALIDATION = ANALYSIS / "t23_recovered_training_validation.json"
T22_RESULT = ANALYSIS / "t22_corrected_one_update_cpu_result.json"
V121_PREREGISTRATION = (
    ANALYSIS / "winner_v121_deployment_transform_preregistration.json"
)
OUTPUT = ANALYSIS / "t24_t23_postexport_preregistration.json"
MARKDOWN = ANALYSIS / "T24_T23_POSTEXPORT_PREREGISTRATION_20260726.md"
RAW_ROOT = Path(
    "D:/CodexArtifacts/open-duck-policy/t23b_extracted_20260726/"
    "t23_support_trainthrough_continuation/training"
)
EXPECTED_STEPS = [0, 1_003_520, 2_007_040]
SOURCE_PATHS = (
    "tools/run_t24_t23_postexport_transform.py",
    "tools/run_t22_corrected_one_update_cpu_smoke.py",
    "tools/run_t20_support_trainthrough_one_update.py",
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


def canonical_sha256(value: object) -> str:
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
            raise FileExistsError(f"refusing to overwrite T24: {path}")
    validation = json.loads(VALIDATION.read_text(encoding="utf-8"))
    t22 = json.loads(T22_RESULT.read_text(encoding="utf-8"))
    v121 = json.loads(V121_PREREGISTRATION.read_text(encoding="utf-8"))
    graphs = sorted(RAW_ROOT.glob("*.onnx"), key=graph_step)
    steps = [graph_step(path) for path in graphs]
    raw_graphs = {str(graph_step(path)): sha256(path) for path in graphs}
    validation_graphs = {
        str(int(row["step"])): row["sha256"]
        for row in validation["onnx"]
    }
    source_hashes = {
        name: sha256(ROOT / name) for name in SOURCE_PATHS
    }
    checks = {
        "t23_recovered_training_validation_green": (
            validation.get("status")
            == "PASS_T23_RECOVERED_TRAINING_VALIDATION"
            and validation.get("failed_checks") == []
            and validation.get("authority", {}).get(
                "postexport_transform_preregistration_authorized"
            )
            is True
        ),
        "exact_three_raw_exports": steps == EXPECTED_STEPS,
        "raw_export_hashes_match_cpu_validation": (
            raw_graphs == validation_graphs
        ),
        "t22_golden_chain_green": (
            t22.get("status") == "PASS_T22_CORRECTED_ONE_UPDATE_CPU_SMOKE"
            and t22.get("failed_checks") == []
            and all(
                t22["checks"][name]
                for name in (
                    "both_source_deployment_contracts_pass",
                    "both_physical_wrapper_contracts_pass",
                    "step_zero_context_abi_byte_exact",
                    "step_zero_physical_wrapper_byte_exact",
                    "step_zero_source_deployed_byte_exact",
                )
            )
        ),
        "v121_transform_preregistered": (
            v121.get("status")
            == "PREREGISTERED_WINNER_V121_DEPLOYMENT_TRANSFORM"
            and v121.get("failed_checks") == []
        ),
        "all_transform_sources_present": len(source_hashes)
        == len(SOURCE_PATHS),
        "behavior_not_run": True,
        "robot_or_rdk_access_zero": True,
    }
    checks = {name: bool(passed) for name, passed in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value = {
        "schema_version": "open_duck.t24_t23_postexport_preregistration.v1",
        "status": (
            "PREREGISTERED_T24_T23_POSTEXPORT_TRANSFORM"
            if not failed
            else "HOLD_T24_T23_POSTEXPORT_TRANSFORM"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {
            "t23_validation": sha256(VALIDATION),
            "t22_result": sha256(T22_RESULT),
            "v121_transform_preregistration": sha256(
                V121_PREREGISTRATION
            ),
        },
        "source_hashes": source_hashes,
        "raw_root": str(RAW_ROOT),
        "raw_graphs": raw_graphs,
        "frozen_chain": [
            "v121_actual_centered_guard",
            "x0_command_deadband",
            "v121_source_trained_rate_projection",
            "diagnostic_context_abi_noop",
            "support_homeomorphism_and_external_physical_rate_projection",
        ],
        "golden_requirement": (
            "step_zero_all_intermediate_and_final_hashes_byte_exact_to_T22"
        ),
        "postupdate_steps": EXPECTED_STEPS[1:],
        "decision": (
            "RUN_ONE_CPU_ONLY_T24_POSTEXPORT_TRANSFORM"
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
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T24 T23 post-export transform preregistration",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                "- Three raw exports are hash-exact to T23 CPU validation.",
                "- Step zero must reproduce every T22 golden chain hash; "
                "both post-update exports receive the identical transform.",
                "- No optimizer, behavior, Gate 5, or robot authority.",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
