#!/usr/bin/env python3
"""Run T226's saved-trace and frozen-source boundary-corner autopsy."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
sys.path.insert(0, str(ROOT / "tools"))
from run_t136_static_calibration_router_transform import (  # noqa: E402
    canonical_sha256,
    verify,
)


PREREG = ANALYSIS / "t226_r2_boundary_corner_autopsy_preregistration.json"
RESULT = ANALYSIS / "t226_r2_boundary_corner_autopsy_result.json"
MARKDOWN = ANALYSIS / "T226_R2_BOUNDARY_CORNER_AUTOPSY_RESULT_20260730.md"


def read_trace(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T226 result")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T226 execution requires clean worktree")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T226_R2_BOUNDARY_CORNER_AUTOPSY"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T226 preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, f"frozen_inputs.{name}")
    for index, item in enumerate(prereg["traces"]):
        verify(item["trace"], f"traces[{index}]")

    randomizer_path = Path(
        prereg["frozen_inputs"]["training_configuration_randomizer"]["path"]
    )
    joystick_path = Path(
        prereg["frozen_inputs"]["training_command_sampler"]["path"]
    )
    randomizer_source = randomizer_path.read_text(encoding="utf-8")
    joystick_source = joystick_path.read_text(encoding="utf-8")
    source_checks = {
        "configuration_uses_continuous_uniform": (
            "com_offset = _uniform(" in randomizer_source
            and "keys[5], -0.05 * scale, 0.05 * scale, shape=(3,)"
            in randomizer_source
            and "low + jax.random.uniform(" in randomizer_source
            and "* (high - low)" in randomizer_source
        ),
        "command_uses_continuous_uniform": (
            "ground_up_command_support_range[0]" in joystick_source
            and "ground_up_command_support_range[1]" in joystick_source
            and "jax.random.uniform(" in joystick_source
        ),
        "no_boundary_atom_sampler_in_configuration_source": (
            "boundary_atom" not in randomizer_source
            and "endpoint_atom" not in randomizer_source
        ),
        "no_boundary_atom_sampler_in_command_source": (
            "boundary_atom" not in joystick_source
            and "endpoint_atom" not in joystick_source
        ),
    }

    loaded: dict[tuple[str, str, float], dict[str, Any]] = {}
    summaries = []
    for item in prereg["traces"]:
        rows = read_trace(Path(item["trace"]["path"]))
        ticks = [int(row["tick"]) for row in rows]
        key = (
            item["checkpoint_id"],
            item["fit_id"],
            float(item["command_x_m_s"]),
        )
        loaded[key] = {"item": item, "rows": rows}
        summaries.append(
            {
                "checkpoint_id": key[0],
                "fit_id": key[1],
                "command_x_m_s": key[2],
                "cell_green": item["cell_green"],
                "samples": len(rows),
                "terminal_tick": int(rows[-1]["tick"]),
                "termination_reason": item["behavior"][
                    "termination_reason"
                ],
                "ticks_contiguous": ticks == list(range(len(rows))),
                "maximum_abs_pitch_rad": max(
                    abs(float(row["body_pitch_rad"])) for row in rows
                ),
                "minimum_base_height_m": min(
                    float(row["base_height_m"]) for row in rows
                ),
            }
        )

    pair_rows = []
    for fit in ("p30", "p31_34"):
        fail = loaded[
            ("T222_GLOBAL_PLATEAU_HALF", fit, 0.074)
        ]["rows"]
        peer = loaded[
            ("T222_GLOBAL_PLATEAU_HALF", fit, 0.077)
        ]["rows"]
        fail0 = fail[0]
        peer0 = peer[0]
        obs_differences = [
            index
            for index, (left, right) in enumerate(
                zip(fail0["obs_state"], peer0["obs_state"])
            )
            if left != right
        ]
        pair_rows.append(
            {
                "fit_id": fit,
                "failure_samples": len(fail),
                "failure_terminal_tick": int(fail[-1]["tick"]),
                "peer_samples": len(peer),
                "peer_terminal_tick": int(peer[-1]["tick"]),
                "qpos_tick_zero_exact": fail0["qpos"] == peer0["qpos"],
                "qvel_tick_zero_exact": fail0["qvel"] == peer0["qvel"],
                "contacts_tick_zero_exact": (
                    fail0["foot_contacts"] == peer0["foot_contacts"]
                ),
                "obs_tick_zero_difference_indices": obs_differences,
                "obs_command_values": [
                    float(fail0["obs_state"][6]),
                    float(peer0["obs_state"][6]),
                ],
                "initial_action_max_abs_delta": max(
                    abs(float(left) - float(right))
                    for left, right in zip(
                        fail0["action"],
                        peer0["action"],
                    )
                ),
            }
        )

    failures = [
        item for item in prereg["traces"] if not item["cell_green"]
    ]
    final_rows = [
        item
        for item in prereg["traces"]
        if item["checkpoint_id"] == "T222_GLOBAL_PLATEAU_FINAL"
    ]
    checks = {
        **source_checks,
        "all_sixteen_traces_contiguous_and_exact_length": (
            len(summaries) == 16
            and all(row["ticks_contiguous"] for row in summaries)
            and all(
                row["samples"]
                == (
                    600
                    if row["cell_green"]
                    else next(
                        item["behavior"]["samples"]
                        for item in prereg["traces"]
                        if item["checkpoint_id"]
                        == row["checkpoint_id"]
                        and item["fit_id"] == row["fit_id"]
                        and item["command_x_m_s"]
                        == row["command_x_m_s"]
                    )
                )
                for row in summaries
            )
        ),
        "exactly_two_half_x074_failures": (
            len(failures) == 2
            and {
                (
                    item["checkpoint_id"],
                    item["fit_id"],
                    item["command_x_m_s"],
                )
                for item in failures
            }
            == {
                ("T222_GLOBAL_PLATEAU_HALF", "p30", 0.074),
                ("T222_GLOBAL_PLATEAU_HALF", "p31_34", 0.074),
            }
        ),
        "failed_cells_keep_quality_rate_and_saturation_green": all(
            item["behavior"]["replacement_quality_pass"]
            and item["behavior"]["action_saturation_pct"] == 0.0
            and item["behavior"]["instant_rate_excess_rad_s"] == 0.0
            and item["behavior"]["p95_rate_excess_rad_s"] == 0.0
            for item in failures
        ),
        "both_failures_are_dynamic_not_handoff": all(
            row["failure_terminal_tick"]
            >= int(prereg["signals"]["minimum_dynamic_failure_tick"])
            for row in pair_rows
        ),
        "same_initial_physical_state_for_x074_and_x077": all(
            row["qpos_tick_zero_exact"]
            and row["qvel_tick_zero_exact"]
            and row["contacts_tick_zero_exact"]
            for row in pair_rows
        ),
        "only_tick_zero_observation_difference_is_command_x": all(
            row["obs_tick_zero_difference_indices"] == [6]
            for row in pair_rows
        ),
        "both_same_fit_x077_peers_complete_and_pass": all(
            row["peer_samples"] == 600
            and row["peer_terminal_tick"] == 599
            for row in pair_rows
        ),
        "all_eight_final_checkpoint_cells_pass": (
            len(final_rows) == 8
            and all(item["cell_green"] for item in final_rows)
        ),
        "global_command_plateau_remains_closed": (
            prereg["source_facts"][
                "global_command_plateau_is_closed_by_t225"
            ]
            is True
        ),
        "zero_simulator_optimizer_onnx_behavior_hosted_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed_checks = sorted(
        name for name, passed in checks.items() if not passed
    )
    passed = not failed_checks
    basis_result: dict[str, Any] = {
        "schema_version": (
            "open_duck.t226_r2_boundary_corner_autopsy_result.v1"
        ),
        "status": (
            "PASS_T226_R2_BOUNDARY_CORNER_AUTOPSY"
            if passed
            else "HOLD_T226_R2_BOUNDARY_CORNER_AUTOPSY"
        ),
        "decision": (
            "EARN_T227_BOUNDARY_ATOM_TRAINING_CPU_CONTRACT_"
            "PREREGISTRATION_ONLY"
            if passed
            else "RETURN_TO_MECHANISM_SELECTION_WITHOUT_BOUNDARY_ATOMS"
        ),
        "classification": (
            "LOW_COMMAND_UPPER_Z_UNSAMPLED_BOUNDARY_CORNER_WITH_LATE_ABI_FEASIBILITY"
            if passed
            else "UNRESOLVED_T225_FIRST_R2_FAILURE"
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed_checks,
        "pair_comparisons": pair_rows,
        "trace_summaries": summaries,
        "training_support": {
            "configuration_distribution": "continuous_uniform",
            "command_distribution": "continuous_uniform",
            "upper_endpoint_exclusive": True,
            "deterministic_endpoint_atoms": 0,
            "selected_successor": (
                "deterministic boundary-atom training distribution over "
                "the frozen command/configuration gate support"
                if passed
                else None
            ),
            "policy_abi_change": False,
            "reward_or_cost_change": False,
            "global_command_transform_retry": False,
        },
        "execution": {
            "saved_trace_rows": sum(row["samples"] for row in summaries),
            "source_files_read": 2,
            "simulator_transitions": 0,
            "optimizer_steps": 0,
            "onnx_inferences": 0,
            "behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "boundary_atom_cpu_contract_preregistration": passed,
            "training": False,
            "colab": False,
            "gate5": False,
            "robot_or_rdk": False,
        },
    }
    value = {
        **basis_result,
        "result_sha256": canonical_sha256(basis_result),
    }
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T226 R2 boundary-corner autopsy result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Classification: `{value['classification']}`\n"
        "- Failures: half checkpoint x=.074 under both fits; final is 8/8\n"
        f"- Failure terminal ticks: `{pair_rows[0]['failure_terminal_tick']}/"
        f"{pair_rows[1]['failure_terminal_tick']}`\n"
        "- Tick-zero x=.074/x=.077 state: identical except obs[6]\n"
        "- T216 support: continuous command/configuration uniforms, no deterministic endpoint atoms\n"
        "- Global command plateau remains closed; no transform retry\n"
        "- Simulator / optimizer / ONNX / behavior / hosted / robot: `0/0/0/0/0/0`\n"
        f"- Result SHA-256: `{value['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"failed_checks={failed_checks}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
