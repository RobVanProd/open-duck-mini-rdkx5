#!/usr/bin/env python3
"""Run T250 with the preregistered full-handoff extractor recovery."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any, Mapping

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    receipt,
    sha256,
)


PREREG = ANALYSIS / "t250b_reporter_recovery_preregistration.json"
ORIGINAL = ROOT / "tools/run_t250_offline_deployment_contract_audit.py"
T250_RESULT = ANALYSIS / "t250_offline_deployment_contract_audit_result.json"
RESULT = ANALYSIS / "t250b_reporter_recovery_result.json"
MARKDOWN = ANALYSIS / "T250B_REPORTER_RECOVERY_RESULT_20260731.md"

IMPORT_BEFORE = """from run_t136_static_calibration_router_transform import (  # noqa: E402
    canonical_sha256,
    receipt,
    sha256,
)
"""
IMPORT_AFTER = IMPORT_BEFORE + """from run_t242_bounded_router_home_offset import (  # noqa: E402
    corrected_extract_block,
)
from run_t27_t23_robustness_matrix import extract_block  # noqa: E402
"""
LOOP_BEFORE = """    fresh_runs: list[dict[str, Any]] = []
    selected_golden_manifest = None
    selected_golden_evaluation = None
    for manifest, evaluation in iter_t249_evaluations(t249b):
        for run in evaluation[\"runs\"]:
            response = run[\"response_calibration\"]
            response_green = (
                response[\"enabled\"]
                and response[\"calibration_ticks\"] == 250
                and response[\"home_return_ticks\"] == 0
                and response[\"handoff_state_preserved\"]
                and response[\"locomotion_hidden_exact_zero\"]
                and response[\"locomotion_previous_action_matches_calibration\"]
                and response[\"applied_target_observation_matches_bridge\"]
                and response[\"locomotion_phase_reset\"] == [1.0, 0.0]
                and response[\"context_shape\"] == [1, 64]
                and response[\"context_finite\"]
            )
            fresh_runs.append(
                {
                    \"condition_id\": manifest[\"block_contract\"][\"condition\"][\"id\"],
                    \"checkpoint_id\": manifest[\"block_contract\"][\"policy\"][\"checkpoint_id\"],
                    \"fit_id\": manifest[\"block_contract\"][\"fit\"][\"fit_id\"],
                    \"command_x\": float(run[\"command_x\"]),
                    \"status\": run[\"status\"],
                    \"response_handoff_green\": bool(response_green),
                }
            )
        contract = manifest[\"block_contract\"]
        if (
            contract[\"condition\"][\"id\"] == \"KP_HI\"
            and contract[\"policy\"][\"checkpoint_id\"] == selected[\"checkpoint_id\"]
            and contract[\"fit\"][\"fit_id\"] == \"p30\"
        ):
            selected_golden_manifest = manifest
            selected_golden_evaluation = evaluation

    if selected_golden_manifest is None or selected_golden_evaluation is None:
        raise RuntimeError(\"T250 frozen golden block not found\")
    golden_run = next(
        row
        for row in selected_golden_evaluation[\"runs\"]
        if float(row[\"command_x\"]) == 0.074
    )
"""
LOOP_AFTER = """    fresh_runs: list[dict[str, Any]] = []
    selected_golden_manifest = None
    selected_golden_block = None
    for manifest, _evaluation in iter_t249_evaluations(t249b):
        contract = manifest[\"block_contract\"]
        condition = next(
            row
            for row in t249[\"remaining_conditions\"]
            if row[\"id\"] == contract[\"condition\"][\"id\"]
        )
        extractor = (
            corrected_extract_block
            if \"joint_qpos0_offset_rad\" in condition[\"override\"]
            else extract_block
        )
        block = extractor(
            t249,
            condition,
            {**manifest, \"evaluation_path\": manifest[\"evaluation\"][\"path\"]},
        )
        for cell in block[\"cells\"]:
            fresh_runs.append(
                {
                    \"condition_id\": contract[\"condition\"][\"id\"],
                    \"checkpoint_id\": contract[\"policy\"][\"checkpoint_id\"],
                    \"fit_id\": contract[\"fit\"][\"fit_id\"],
                    \"command_x\": float(cell[\"command_x_m_s\"]),
                    \"cell_green\": bool(cell[\"cell_green\"]),
                    \"trace_valid\": bool(cell[\"trace_valid\"]),
                    \"response_handoff_green\": handoff_checks(cell[\"handoff\"]),
                }
            )
        if (
            contract[\"condition\"][\"id\"] == \"KP_HI\"
            and contract[\"policy\"][\"checkpoint_id\"] == selected[\"checkpoint_id\"]
            and contract[\"fit\"][\"fit_id\"] == \"p30\"
        ):
            selected_golden_manifest = manifest
            selected_golden_block = block

    if selected_golden_manifest is None or selected_golden_block is None:
        raise RuntimeError(\"T250 frozen golden block not found\")
    golden_cell = next(
        row
        for row in selected_golden_block[\"cells\"]
        if float(row[\"command_x_m_s\"]) == 0.074
    )
"""
RESPONSE_BEFORE = '    response = golden_run["response_calibration"]\n'
RESPONSE_AFTER = '    response = golden_cell["handoff"]["response_audit"]\n'
COMPLETE_BEFORE = """        \"all_fresh_worker_runs_complete\": all(
            row[\"status\"] == \"COMPLETE\" for row in fresh_runs
        ),
"""
COMPLETE_AFTER = """        \"all_fresh_worker_runs_complete\": all(
            row[\"cell_green\"] and row[\"trace_valid\"] for row in fresh_runs
        ),
"""


def verify(value: Mapping[str, Any]) -> Path:
    path = Path(value["path"])
    if (
        not path.is_file()
        or path.stat().st_size != int(value["bytes"])
        or sha256(path) != value["sha256"]
    ):
        raise RuntimeError(f"changed T250B input: {path}")
    return path


def patched_source() -> str:
    source = ORIGINAL.read_text(encoding="utf-8").replace("\r\n", "\n")
    for index, (before, after) in enumerate(
        (
            (IMPORT_BEFORE, IMPORT_AFTER),
            (LOOP_BEFORE, LOOP_AFTER),
            (RESPONSE_BEFORE, RESPONSE_AFTER),
            (COMPLETE_BEFORE, COMPLETE_AFTER),
        )
    ):
        if source.count(before) != 1:
            raise RuntimeError(f"T250B source patch {index} is not unique")
        source = source.replace(before, after, 1)
    compile(source, f"{ORIGINAL}::T250B", "exec")
    return source


def main() -> int:
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T250B result")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T250B execution requires a clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"] != "PREREGISTERED_T250B_REPORTER_RECOVERY"
        or prereg["failed_checks"]
        or canonical_sha256(basis) != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T250B preregistration changed")
    for value in prereg["frozen_inputs"].values():
        verify(value)

    namespace = {
        "__name__": "__main__",
        "__file__": str(ORIGINAL),
        "__package__": None,
    }
    exit_code = 1
    try:
        exec(compile(patched_source(), f"{ORIGINAL}::T250B", "exec"), namespace)
    except SystemExit as exc:
        exit_code = int(exc.code or 0)

    t250 = json.loads(T250_RESULT.read_text(encoding="utf-8"))
    recovered = (
        exit_code == 0
        and t250["status"] == "PASS_T250_OFFLINE_DEPLOYMENT_CONTRACT_AUDIT"
        and not t250["failed_checks"]
    )
    result_basis: dict[str, Any] = {
        "schema_version": "open_duck.t250b_reporter_recovery_result.v1",
        "status": (
            "PASS_T250B_REPORTER_RECOVERY"
            if recovered
            else "HOLD_T250B_REPORTER_RECOVERY"
        ),
        "decision": (
            t250["decision"]
            if recovered
            else prereg["decision_rule"]["fail"]
        ),
        "classification": prereg["classification"],
        "preregistered_contract_sha256": prereg["preregistered_contract_sha256"],
        "t250_result": receipt(T250_RESULT),
        "recovery": {
            "in_memory_patch": True,
            "frozen_block_extractors_used": True,
            "behavior_cells_rerun": 0,
            "original_onnx_cpu_audit_preserved": True,
        },
        "execution": {
            "simulator_steps": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "versioned_runtime_integration_preregistration": recovered,
            "training": False,
            "hosted": False,
            "policy_staging": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    result = {**result_basis, "result_sha256": canonical_sha256(result_basis)}
    RESULT.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T250B reporter recovery result\n\n"
        f"- Status: `{result['status']}`\n"
        f"- Decision: `{result['decision']}`\n"
        "- Behavior cells rerun: `0`\n"
        "- Simulator/optimizer/hosted/robot: `0/0/0/0`\n"
        "- Gate 5: `NOT_AUTHORIZED`\n"
        f"- Result SHA-256: `{result['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(result["status"])
    print(f"decision={result['decision']}")
    print(f"result_sha256={result['result_sha256']}")
    return 0 if recovered else 1


if __name__ == "__main__":
    raise SystemExit(main())
