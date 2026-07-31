#!/usr/bin/env python3
"""Freeze the disjoint T149B + T162 repair composition contract."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    receipt,
)


OUTPUT = ANALYSIS / "t164_prior_repair_composition_preregistration.json"


def main() -> int:
    if OUTPUT.exists():
        raise FileExistsError("refusing to overwrite T164 preregistration")
    paths = {
        "t149b": (
            ANALYSIS / "t149b_negative_context_command_plateau_result.json"
        ),
        "t151": ANALYSIS / "t151_command_plateau_full_r2_result.json",
        "t156": ANALYSIS / "t156_three_way_positive_router_result.json",
        "t162": ANALYSIS / "t162_exact_command_endpoint_transform_result.json",
        "t163": ANALYSIS / "t163_command_endpoint_positive_matrix_result.json",
        "contexts": (
            ANALYSIS
            / "t135b_interrupted_calibration_context_router_recovery_result.json"
        ),
    }
    values = {
        name: json.loads(path.read_text(encoding="utf-8"))
        for name, path in paths.items()
    }
    contexts = [
        *[
            {
                "fit_id": row["fit_id"],
                "population": row["population"],
                "context": row["context"],
                "context_sha256": row["context_sha256"],
            }
            for row in values["contexts"]["runs"]
        ],
        *[
            {
                "fit_id": row["fit_id"],
                "population": row["population"],
                "context": row["context"],
                "context_sha256": row["context_sha256"],
            }
            for row in values["t156"]["positive_contexts"]
        ],
    ]
    t162_by_step = {
        str(row["step"]): row["structure"]["transformed"]
        for row in values["t162"]["graphs"]
    }
    graphs = [
        {
            "step": int(step),
            "t149b": values["t149b"]["transforms"][step]["transformed"],
            "t162": t162_by_step[step],
        }
        for step in ("1003520", "2007040")
    ]
    frozen = {
        "builder": receipt(Path(__file__)),
        "runner": receipt(
            ROOT / "tools" / "run_t164_prior_repair_composition.py"
        ),
        "test": receipt(
            ROOT / "tests" / "test_t164_prior_repair_composition.py"
        ),
        **{name: receipt(path) for name, path in paths.items()},
    }
    conditions = values["t151"]["conditions"]
    checks = {
        "t149b_contract_green": (
            values["t149b"]["status"]
            == "PASS_T149B_NEGATIVE_CONTEXT_COMMAND_PLATEAU"
            and not values["t149b"]["failed_checks"]
        ),
        "t151_first_seven_conditions_green": (
            len(conditions) == 8
            and all(row["condition_green"] for row in conditions[:7])
            and conditions[6]["condition_id"] == "TORSO_COM_X_NEG"
            and not conditions[7]["condition_green"]
            and conditions[7]["condition_id"] == "TORSO_COM_X_POS"
        ),
        "t163_positive_condition_green": (
            values["t163"]["status"]
            == "PASS_T163_COMMAND_ENDPOINT_POSITIVE_MATRIX"
            and values["t163"]["condition"]["green_cells"] == 16
        ),
        "t162_does_not_contain_t149_repair": all(
            "t149" not in Path(row["t162"]["path"]).name.lower()
            and row["t162"]["sha256"]
            != row["t149b"]["sha256"]
            for row in graphs
        ),
        "two_graph_pairs_present": (
            len(graphs) == 2
            and all(
                Path(row[key]["path"]).is_file()
                for row in graphs
                for key in ("t149b", "t162")
            )
        ),
        "six_calibration_contexts": (
            len(contexts) == 6
            and {row["population"] for row in contexts}
            == {"nominal", "com_x_negative", "com_x_positive"}
        ),
        "zero_behavior_training_hosted_robot_now": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t164_prior_repair_composition_preregistration.v1"
        ),
        "status": "PREREGISTERED_T164_PRIOR_REPAIR_COMPOSITION",
        "question": (
            "Can the previously green T149B negative-context command cap "
            "be composed with T162 so negative contexts remain bit-exact "
            "to T149B while nominal and positive contexts remain bit-exact "
            "to T162?"
        ),
        "frozen_inputs": frozen,
        "graphs": graphs,
        "contexts": contexts,
        "composition": {
            "negative_context": "T149B cap command_x to 0.074 m/s",
            "positive_context": "T162 checkpoint endpoint rewrite",
            "nominal_context": "unchanged T162/T143C path",
            "gates_expected_disjoint": True,
            "source_nodes_otherwise_byte_exact": True,
            "scalar_search": False,
            "new_runtime_inputs": 0,
            "new_runtime_outputs": 0,
        },
        "inference": {
            "provider": "CPUExecutionProvider",
            "seed": 20260729,
            "commands_x_m_s": [0.0, 0.074, 0.077, 0.080],
            "required_exactness": "bit_exact_all_outputs_and_state_chains",
        },
        "decision_rule": {
            "pass": "EARN_T165_COMPOSED_FULL_R2_PREREGISTRATION_ONLY",
            "fail": "HOLD_FULL_R2_AND_AUDIT_REPAIR_COMPOSITION",
            "no_retry": True,
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "inference_samples": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_composition_contract": not failed,
            "full_r2": False,
            "training": False,
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
    print(value["status"])
    print(
        "preregistered_contract_sha256="
        f"{value['preregistered_contract_sha256']}"
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
