#!/usr/bin/env python3
"""Freeze T220's command-endpoint and deployed-route attribution audit."""

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


T149B = ANALYSIS / "t149b_negative_context_command_plateau_result.json"
T164 = ANALYSIS / "t164_prior_repair_composition_result.json"
T218_PREREG = (
    ANALYSIS / "t218_t216_postexport_composition_preregistration.json"
)
T218 = ANALYSIS / "t218_t216_postexport_composition_result.json"
T219 = ANALYSIS / "t219_t216_nominal_matrix_result.json"
T220 = ANALYSIS / "t220_t216_targeted_y_negative_result.json"
OUTPUT = ANALYSIS / "t221_t220_command_route_audit_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "T221_T220_COMMAND_ROUTE_AUDIT_PREREGISTRATION_20260730.md"
)
RUNNER = ROOT / "tools/run_t221_t220_command_route_audit.py"
TEST = ROOT / "tests/test_t221_t220_command_route_audit.py"


def cells(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "checkpoint_id": block["checkpoint_id"],
            "step": block["step"],
            "fit_id": block["fit_id"],
            **cell,
        }
        for block in value["blocks"]
        for cell in block["result"]["cells"]
    ]


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T221 preregistration")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T221 preregistration requires clean worktree")
    values = {
        "t149b": json.loads(T149B.read_text(encoding="utf-8")),
        "t164": json.loads(T164.read_text(encoding="utf-8")),
        "t218_prereg": json.loads(T218_PREREG.read_text(encoding="utf-8")),
        "t218": json.loads(T218.read_text(encoding="utf-8")),
        "t219": json.loads(T219.read_text(encoding="utf-8")),
        "t220": json.loads(T220.read_text(encoding="utf-8")),
    }
    graphs = [
        {
            "step": row["step"],
            "role": row["role"],
            "graph": row["structure"]["transformed"],
        }
        for row in values["t218"]["graphs"]
        if row["role"] in ("half", "final")
    ]
    contexts = [
        row
        for row in values["t218_prereg"]["contexts"]
        if row["condition_id"] == "TORSO_COM_Y_NEG"
    ]
    nominal_cells = cells(values["t219"])
    targeted_cells = cells(values["t220"])
    failures = [row for row in targeted_cells if not row["cell_green"]]
    frozen = {
        "builder": receipt(Path(__file__)),
        "runner": receipt(RUNNER),
        "test": receipt(TEST),
        "t149b_result": receipt(T149B),
        "t164_result": receipt(T164),
        "t218_preregistration": receipt(T218_PREREG),
        "t218_result": receipt(T218),
        "t219_result": receipt(T219),
        "t220_result": receipt(T220),
    }
    checks = {
        "prior_negative_cap_green": (
            values["t149b"]["status"]
            == "PASS_T149B_NEGATIVE_CONTEXT_COMMAND_PLATEAU"
            and not values["t149b"]["failed_checks"]
        ),
        "prior_composition_green": (
            values["t164"]["status"]
            == "PASS_T164_PRIOR_REPAIR_COMPOSITION"
            and not values["t164"]["failed_checks"]
            and values["t218"]["status"]
            == "PASS_T218_T216_POSTEXPORT_COMPOSITION"
            and not values["t218"]["failed_checks"]
        ),
        "nominal_matrix_exact_pass": (
            values["t219"]["status"] == "PASS_T219_T216_NOMINAL_MATRIX"
            and values["t219"]["condition"]["green_cells"] == 16
        ),
        "targeted_matrix_exact_hold": (
            values["t220"]["status"]
            == "HOLD_T220_T216_TARGETED_Y_NEGATIVE"
            and values["t220"]["condition"]["green_cells"] == 13
            and values["t220"]["decision"]
            == "CLOSE_T216_AXIS_COMPLETE_TILT_CONTINUATION"
        ),
        "all_three_failures_are_x008_only": (
            len(failures) == 3
            and all(row["command_x_m_s"] == 0.08 for row in failures)
        ),
        "two_candidate_graphs_present": (
            [row["step"] for row in graphs] == [1_003_520, 2_007_040]
            and all(Path(row["graph"]["path"]).is_file() for row in graphs)
        ),
        "two_y_negative_contexts_frozen": (
            len(contexts) == 2
            and {row["fit_id"] for row in contexts} == {"p30", "p31_34"}
        ),
        "sixteen_nominal_and_targeted_cells": (
            len(nominal_cells) == 16 and len(targeted_cells) == 16
        ),
        "zero_simulator_optimizer_behavior_hosted_or_robot_now": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T221 preregistration checks failed: {failed}")
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t221_t220_command_route_audit_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T221_T220_COMMAND_ROUTE_AUDIT",
        "question": (
            "Are T220's three failures confined to x=.080 because both "
            "Y-negative calibration contexts select the nominal route and "
            "therefore bypass the preserved T149 negative-expert cap, while "
            "the already-passing x=.077 cells retain enough velocity to be "
            "judged against the unchanged external x=.080 gate?"
        ),
        "frozen_inputs": frozen,
        "graphs": graphs,
        "contexts": contexts,
        "nominal_cells": nominal_cells,
        "targeted_cells": targeted_cells,
        "audit": {
            "existing_t149_cap_m_s": 0.074,
            "candidate_global_cap_m_s": 0.077,
            "candidate_derivation": (
                "the highest frozen command below the sole failing endpoint; "
                "all four targeted and all four nominal x=.077 cells already "
                "pass across both checkpoints and both measured fits"
            ),
            "external_command_for_counterfactual_ratio_m_s": 0.08,
            "minimum_track_ratio": 0.4,
            "onnx_provider": "CPUExecutionProvider",
            "random_seed": 20260730,
            "samples_per_graph_context": 64,
            "selection_weight": 0,
            "scalar_sweep": False,
        },
        "decision_rule": {
            "earn_transform_contract_if": [
                "all three T220 failures are x=.080 and every x=.077 cell passes",
                "all nominal x=.077 cells pass",
                "all x=.077 mean velocities remain >=.4*.080",
                "both Y-negative contexts select the nominal route",
                "the preserved T149 cap exists but its gate is false for both",
                "same-state source inference differs between x=.077 and x=.080",
            ],
            "pass": (
                "EARN_T222_GLOBAL_X008_TO_X0077_PLATEAU_"
                "CPU_CONTRACT_PREREGISTRATION_ONLY"
            ),
            "fail": "CLOSE_GLOBAL_COMMAND_PLATEAU_WITHOUT_BEHAVIOR",
            "no_alternative_cap": True,
            "no_training": True,
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "onnx_inferences": 0,
            "simulator_transitions": 0,
            "optimizer_steps": 0,
            "behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_route_audit": True,
            "transform_contract_preregistration": False,
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
        "# T221 T220 command-route audit preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Frozen candidate cap: `.077 m/s`; no scalar sweep\n"
        "- Scope: route attribution, saved results, and CPU ONNX inference\n"
        "- Simulator / optimizer / behavior / hosted / robot: `0/0/0/0/0`\n"
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
