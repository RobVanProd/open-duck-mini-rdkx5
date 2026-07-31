#!/usr/bin/env python3
"""Freeze a source-and-trace autopsy of T225's first R2 failure."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    receipt,
)


T225 = ANALYSIS / "t225_global_plateau_full_r2_result.json"
T216 = ANALYSIS / "t216_axis_complete_tilt_hosted_preregistration.json"
OUTPUT = ANALYSIS / "t226_r2_boundary_corner_autopsy_preregistration.json"
MARKDOWN = ANALYSIS / "T226_R2_BOUNDARY_CORNER_AUTOPSY_PREREGISTRATION_20260730.md"
RUNNER = ROOT / "tools/run_t226_r2_boundary_corner_autopsy.py"
TEST = ROOT / "tests/test_t226_r2_boundary_corner_autopsy.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T226 preregistration")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T226 preregistration requires clean worktree")

    t225 = json.loads(T225.read_text(encoding="utf-8"))
    t216 = json.loads(T216.read_text(encoding="utf-8"))
    playground = Path(t216["paths"]["playground"])
    randomizer = (
        playground
        / "playground/common/winner_v3_variable_configuration.py"
    )
    joystick = playground / "playground/open_duck_mini_v2/joystick.py"

    traces: list[dict[str, Any]] = []
    for block in t225["blocks"]:
        if block["condition_id"] != "TORSO_COM_Z_POS":
            continue
        for cell in block["result"]["cells"]:
            protection = cell["protection"]
            traces.append(
                {
                    "checkpoint_id": block["checkpoint_id"],
                    "step": int(block["step"]),
                    "fit_id": block["fit_id"],
                    "command_x_m_s": float(cell["command_x_m_s"]),
                    "cell_green": bool(cell["cell_green"]),
                    "behavior": {
                        "samples": int(cell["behavior"]["samples"]),
                        "termination_reason": cell["behavior"][
                            "termination_reason"
                        ],
                        "core_pass": bool(cell["behavior"]["core_pass"]),
                        "replacement_quality_pass": bool(
                            cell["behavior"]["replacement_quality_pass"]
                        ),
                        "action_saturation_pct": float(
                            cell["behavior"]["action_saturation_pct"]
                        ),
                        "instant_rate_excess_rad_s": float(
                            cell["behavior"]["instant_rate_excess_rad_s"]
                        ),
                        "p95_rate_excess_rad_s": float(
                            cell["behavior"]["p95_rate_excess_rad_s"]
                        ),
                    },
                    "trace": receipt(Path(protection["path"])),
                }
            )

    failures = [row for row in traces if not row["cell_green"]]
    failure_keys = {
        (
            row["checkpoint_id"],
            row["fit_id"],
            row["command_x_m_s"],
        )
        for row in failures
    }
    expected_failures = {
        ("T222_GLOBAL_PLATEAU_HALF", "p30", 0.074),
        ("T222_GLOBAL_PLATEAU_HALF", "p31_34", 0.074),
    }
    t216_inventory = t216["playground"]["file_inventory"]
    checks = {
        "t225_formal_first_condition_hold_exact": (
            t225["status"] == "HOLD_T225_GLOBAL_PLATEAU_FULL_R2"
            and t225["decision"]
            == "CLOSE_GLOBAL_COMMAND_PLATEAU_AT_FIRST_FAILED_R2_CONDITION"
            and t225["summary"]["completed_conditions"] == 12
            and t225["summary"]["green_cells"] == 190
            and t225["summary"]["completed_cells"] == 192
            and t225["summary"]["first_failed_condition"]
            == "TORSO_COM_Z_POS"
        ),
        "condition_twelve_complete_fourteen_of_sixteen": (
            len(traces) == 16
            and len(failures) == 2
            and failure_keys == expected_failures
        ),
        "all_condition_twelve_traces_present": all(
            Path(row["trace"]["path"]).is_file() for row in traces
        ),
        "both_final_checkpoint_fits_green": all(
            row["cell_green"]
            for row in traces
            if row["checkpoint_id"] == "T222_GLOBAL_PLATEAU_FINAL"
        ),
        "half_x077_peers_green": all(
            row["cell_green"]
            for row in traces
            if row["checkpoint_id"] == "T222_GLOBAL_PLATEAU_HALF"
            and row["command_x_m_s"] == 0.077
        ),
        "t216_used_continuous_configuration_strata": (
            t216["training"]["body_configuration_strata"] == 8
            and t216["training"]["environments_per_stratum"] == 32
            and t216["training"]["command_support_change"] is False
        ),
        "training_sources_match_t216_inventory": (
            receipt(randomizer)["sha256"]
            == t216_inventory[
                "playground/common/winner_v3_variable_configuration.py"
            ]["sha256"]
            and receipt(joystick)["sha256"]
            == t216_inventory[
                "playground/open_duck_mini_v2/joystick.py"
            ]["sha256"]
        ),
        "zero_simulator_optimizer_onnx_behavior_hosted_or_robot_now": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T226 preregistration checks failed: {failed}")

    frozen = {
        "builder": receipt(Path(__file__)),
        "runner": receipt(RUNNER),
        "test": receipt(TEST),
        "t225_result": receipt(T225),
        "t216_preregistration": receipt(T216),
        "training_configuration_randomizer": receipt(randomizer),
        "training_command_sampler": receipt(joystick),
    }
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t226_r2_boundary_corner_autopsy_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T226_R2_BOUNDARY_CORNER_AUTOPSY",
        "question": (
            "Is T225's first R2 failure localized to the intersection of "
            "the lower moving-command boundary and the upper torso-COM-Z "
            "boundary, both sampled by continuous training distributions "
            "without deterministic endpoint atoms, while the later "
            "checkpoint proves the frozen actor ABI can solve the cell?"
        ),
        "frozen_inputs": frozen,
        "traces": traces,
        "source_facts": {
            "jax_uniform_semantics": "minval_inclusive_maxval_exclusive",
            "configuration_formula": (
                "low + jax.random.uniform([0,1)) * (high - low)"
            ),
            "torso_com_range_m_at_full_scale": [-0.05, 0.05],
            "moving_command_range_m_s": [0.074, 0.08],
            "deterministic_endpoint_atoms_in_t216": 0,
            "global_command_plateau_is_closed_by_t225": True,
        },
        "signals": {
            "same_initial_physical_state": (
                "qpos, qvel, and foot_contacts exact between half x=.074 "
                "failure and same-fit x=.077 pass"
            ),
            "only_initial_observation_difference": (
                "obs_state differs only at index 6 command_x"
            ),
            "minimum_dynamic_failure_tick": 200,
            "failed_cells": sorted(
                [
                    {
                        "checkpoint_id": key[0],
                        "fit_id": key[1],
                        "command_x_m_s": key[2],
                    }
                    for key in expected_failures
                ],
                key=lambda row: row["fit_id"],
            ),
        },
        "decision_rule": {
            "select_boundary_atom_training_distribution_if": [
                "both failed traces begin from the same physical state as their same-fit x=.077 passing peers",
                "the only tick-zero observation difference is obs[6]",
                "both failures occur after tick 200 rather than at handoff",
                "all final-checkpoint cells pass the same upper-Z condition",
                "T216 configuration and command samplers contain no deterministic endpoint atoms",
            ],
            "pass": (
                "EARN_T227_BOUNDARY_ATOM_TRAINING_CPU_CONTRACT_"
                "PREREGISTRATION_ONLY"
            ),
            "fail": "RETURN_TO_MECHANISM_SELECTION_WITHOUT_BOUNDARY_ATOMS",
            "forbidden_successor": (
                "no lower-command plateau, command clamp retry, checkpoint "
                "selection, threshold change, or hosted run"
            ),
            "selection_weight": 0,
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "saved_trace_rows": 0,
            "simulator_transitions": 0,
            "optimizer_steps": 0,
            "onnx_inferences": 0,
            "behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_saved_trace_and_source_autopsy": True,
            "boundary_atom_cpu_contract_preregistration": False,
            "training": False,
            "colab": False,
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
        "# T226 R2 boundary-corner autopsy preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Inputs: T225 condition-12 traces and exact T216 sampler sources\n"
        "- Question: did continuous sampling omit the exact command/configuration corner that failed?\n"
        "- Global command plateau remains closed; no transform retry\n"
        "- Simulator / optimizer / ONNX / behavior / hosted / robot: `0/0/0/0/0/0`\n"
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
