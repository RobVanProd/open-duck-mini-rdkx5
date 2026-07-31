#!/usr/bin/env python3
"""Freeze T222's zero-credit global x=.080 to x=.077 ONNX plateau."""

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


T218_PREREG = (
    ANALYSIS / "t218_t216_postexport_composition_preregistration.json"
)
T218 = ANALYSIS / "t218_t216_postexport_composition_result.json"
T221B_PREREG = (
    ANALYSIS
    / "t221b_command_route_verifier_recovery_preregistration.json"
)
T221B = ANALYSIS / "t221b_command_route_verifier_recovery_result.json"
OUTPUT = ANALYSIS / "t222_global_command_plateau_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T222_GLOBAL_COMMAND_PLATEAU_PREREGISTRATION_20260730.md"
)
RUNNER = ROOT / "tools/run_t222_global_command_plateau_transform.py"
TEST = ROOT / "tests/test_t222_global_command_plateau.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T222 preregistration")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T222 preregistration requires clean worktree")
    values = {
        "t218_prereg": json.loads(T218_PREREG.read_text(encoding="utf-8")),
        "t218": json.loads(T218.read_text(encoding="utf-8")),
        "t221b_prereg": json.loads(
            T221B_PREREG.read_text(encoding="utf-8")
        ),
        "t221b": json.loads(T221B.read_text(encoding="utf-8")),
    }
    graphs = [
        {
            "step": row["step"],
            "role": row["role"],
            "source": row["structure"]["transformed"],
        }
        for row in values["t218"]["graphs"]
        if row["role"] in ("half", "final")
    ]
    pairs = values["t221b_prereg"]["pairs"]
    frozen = {
        "builder": receipt(Path(__file__)),
        "runner": receipt(RUNNER),
        "test": receipt(TEST),
        "t218_preregistration": receipt(T218_PREREG),
        "t218_result": receipt(T218),
        "t221b_preregistration": receipt(T221B_PREREG),
        "t221b_result": receipt(T221B),
    }
    checks = {
        "t218_composition_green": (
            values["t218"]["status"]
            == "PASS_T218_T216_POSTEXPORT_COMPOSITION"
            and not values["t218"]["failed_checks"]
        ),
        "t221b_recovery_green": (
            values["t221b"]["status"]
            == "PASS_T221B_COMMAND_ROUTE_VERIFIER_RECOVERY"
            and not values["t221b"]["failed_checks"]
            and values["t221b"]["decision"]
            == (
                "RECOVER_T221_AND_EARN_T222_GLOBAL_X008_TO_X0077_"
                "PLATEAU_CPU_CONTRACT_PREREGISTRATION_ONLY"
            )
        ),
        "two_exact_candidate_graphs": (
            [row["step"] for row in graphs] == [1_003_520, 2_007_040]
            and all(Path(row["source"]["path"]).is_file() for row in graphs)
        ),
        "forty_frozen_route_contexts": (
            len(values["t218_prereg"]["contexts"]) == 40
        ),
        "four_frozen_sensitivity_pairs": (
            len(pairs) == 4
            and all(
                Path(row["trace"]["path"]).is_file()
                and Path(row["graph"]["path"]).is_file()
                for row in pairs
            )
        ),
        "zero_behavior_training_hosted_or_robot_now": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T222 preregistration checks failed: {failed}")
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t222_global_command_plateau_preregistration.v1"
        ),
        "status": "PREREGISTERED_T222_GLOBAL_COMMAND_PLATEAU",
        "question": (
            "Can a single graph-internal global cap present x=.080 as the "
            "already-passing x=.077 endpoint while preserving x=0/.074/.077, "
            "the existing T149 negative-route .074 cap, every recurrent "
            "output, and the stateful ONNX ABI exactly?"
        ),
        "frozen_inputs": frozen,
        "graphs": graphs,
        "contexts": values["t218_prereg"]["contexts"],
        "trace_pairs": pairs,
        "transform": {
            "observation_command_index": 6,
            "observation_dimension": 115,
            "cap_m_s": 0.077,
            "cap_derivation": (
                "single endpoint selected by T221B; no alternative cap or sweep"
            ),
            "insertion": (
                "prepend Slice/Min/Concat global observation rebuild and "
                "rewire only t149_slice_prefix/t149_slice_command/"
                "t149_slice_suffix to consume it"
            ),
            "existing_t149_cap_m_s": 0.074,
            "existing_t149_cap_order": "global_.077_then_route_specific_.074",
            "new_runtime_inputs": 0,
            "new_runtime_outputs": 0,
            "host_side_command_change": False,
            "runtime_contract_change": False,
            "optimizer_steps": 0,
        },
        "contract": {
            "provider": "CPUExecutionProvider",
            "commands_x_m_s": [0.0, 0.074, 0.077, 0.080],
            "random_seed": 20260730,
            "samples_per_context_command": 8,
            "trace_rows_per_pair": 64,
            "lower_commands": (
                "all outputs bit-exact to untransformed source at "
                "x=0/.074/.077"
            ),
            "upper_command": (
                "all outputs bit-exact to the untransformed source evaluated "
                "on the same state with obs[6]=.077"
            ),
            "source_sensitivity": (
                "frozen T221B trace states must still prove source x=.080 "
                "differs from source x=.077 before transformed equivalence"
            ),
            "abi": "inputs/outputs, names, dtypes, and dimensions exact",
            "structure": (
                "all old initializers exact; all old nodes exact except the "
                "three named T149 Slice input rewires"
            ),
        },
        "decision_rule": {
            "pass": (
                "EARN_T223_GLOBAL_PLATEAU_NOMINAL_MATRIX_"
                "PREREGISTRATION_ONLY"
            ),
            "fail": "CLOSE_GLOBAL_COMMAND_PLATEAU_WITHOUT_BEHAVIOR",
            "no_retry": True,
            "no_alternative_cap": True,
            "no_training": True,
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "onnx_transforms": 0,
            "onnx_inferences": 0,
            "simulator_transitions": 0,
            "optimizer_steps": 0,
            "behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_transform_contract": True,
            "nominal_matrix_preregistration": False,
            "behavior": False,
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
        "# T222 global command plateau preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Transform: graph-internal x=`.080` -> x=`.077`\n"
        "- Preserved exactly: x=`0/.074/.077`, T149 `.074` route cap, ABI/state\n"
        "- Optimizer / behavior / hosted / robot: `0/0/0/0`\n"
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
