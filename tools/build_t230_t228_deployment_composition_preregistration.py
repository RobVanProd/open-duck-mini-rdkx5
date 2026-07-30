#!/usr/bin/env python3
"""Freeze T228 deployment repairs and the retained x=.080 plateau."""

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


OUTPUT = (
    ANALYSIS / "t230_t228_deployment_composition_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T230_T228_DEPLOYMENT_COMPOSITION_PREREGISTRATION_20260730.md"
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T230 preregistration")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T230 preregistration requires clean worktree")
    paths = {
        "t229": ANALYSIS / "t229_t228_recovered_training_validation.json",
        "t218": ANALYSIS / "t218_t216_postexport_composition_result.json",
        "t222b": ANALYSIS / "t222b_abi_helper_recovery_result.json",
        "t164": ANALYSIS / "t164_prior_repair_composition_result.json",
        "t167": ANALYSIS / "t167_calibration_context_separability_result.json",
    }
    values = {name: load(path) for name, path in paths.items()}
    t229 = values["t229"]
    graph_by_step = {
        int(row["step"]): row for row in t229["exports"]["onnx"]
    }
    checkpoint_by_step = {
        int(row["step"]): row
        for row in t229["exports"]["policy_checkpoints"]
    }
    t164_final = next(
        row["structure"]["transformed"]
        for row in values["t164"]["graphs"]
        if int(row["step"]) == 2_007_040
    )
    expected_steps = [0, 1_003_520, 2_007_040]
    graphs = [
        {
            "step": value,
            "role": (
                "source_anchor"
                if value == 0
                else ("half" if value == 1_003_520 else "final")
            ),
            "raw": {
                "path": f"{checkpoint_by_step[value]['path']}.onnx",
                "bytes": Path(
                    f"{checkpoint_by_step[value]['path']}.onnx"
                ).stat().st_size,
                "sha256": graph_by_step[value]["sha256"],
            },
            "base": t164_final,
        }
        for value in expected_steps
    ]
    contexts = [
        {
            "condition_id": row["condition_id"],
            "condition_index": row["condition_index"],
            "fit_id": row["fit_id"],
            "context": row["context"],
            "context_sha256": row["context_sha256"],
        }
        for row in values["t167"]["cells"]
    ]
    frozen = {
        "builder": receipt(Path(__file__)),
        "runner": receipt(
            ROOT / "tools/run_t230_t228_deployment_composition.py"
        ),
        "t218_composition_helper": receipt(
            ROOT / "tools/run_t218_t216_postexport_composition.py"
        ),
        "t172_transform_helper": receipt(
            ROOT / "tools/run_t172_t170_postexport_composition.py"
        ),
        "t222_plateau_helper": receipt(
            ROOT / "tools/run_t222_global_command_plateau_transform.py"
        ),
        **{name: receipt(path) for name, path in paths.items()},
    }
    checks = {
        "t229_earns_only_composition_preregistration": (
            t229["status"]
            == "PASS_T229_T228_RECOVERED_TRAINING_VALIDATION"
            and t229["failed_checks"] == []
            and t229["decision"]
            == "EARN_T230_T228_POSTEXPORT_COMPOSITION_PREREGISTRATION_ONLY"
        ),
        "prior_composition_contract_green": (
            values["t218"]["status"]
            == "PASS_T218_T216_POSTEXPORT_COMPOSITION"
            and values["t218"]["failed_checks"] == []
        ),
        "retained_plateau_contract_green": (
            values["t222b"]["status"]
            == "PASS_T222B_ABI_HELPER_RECOVERY"
            and values["t222b"]["failed_checks"] == []
        ),
        "t164_deployment_base_green": (
            values["t164"]["status"]
            == "PASS_T164_PRIOR_REPAIR_COMPOSITION"
            and values["t164"]["failed_checks"] == []
        ),
        "three_raw_exports_exact": (
            sorted(graph_by_step) == expected_steps
            and sorted(checkpoint_by_step) == expected_steps
            and all(Path(row["raw"]["path"]).is_file() for row in graphs)
        ),
        "single_frozen_t164_final_base": (
            all(
                row["base"]["sha256"] == t164_final["sha256"]
                for row in graphs
            )
            and Path(t164_final["path"]).is_file()
        ),
        "forty_frozen_contexts": (
            len(contexts) == 40
            and sum(
                row["condition_id"] == "TORSO_COM_Y_NEG"
                for row in contexts
            )
            == 2
        ),
        "zero_behavior_training_hosted_robot_now": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T230 preregistration checks failed: {failed}")
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t230_t228_deployment_composition_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T230_T228_DEPLOYMENT_COMPOSITION",
        "question": (
            "Can both new T228 heads be inserted into the frozen T164 "
            "deployment graph and retain T222's global x=.080 to .077 "
            "plateau with exact ABI and lower-command behavior?"
        ),
        "frozen_inputs": frozen,
        "graphs": graphs,
        "contexts": contexts,
        "composition": {
            "source_pair": [
                "negative_adapter_weight",
                "negative_adapter_bias",
            ],
            "destination_pair": [
                "nominal_condition_negative_adapter_weight",
                "nominal_condition_negative_adapter_bias",
            ],
            "base": "T164_COMPOSED_FINAL_FOR_ALL_T228_EXPORTS",
            "global_command_cap_m_s": 0.077,
            "global_command_cap_scope": "obs[6]_only",
            "all_other_initializers_exact": True,
            "all_prior_nodes_exact_except_plateau_rewires": True,
            "new_runtime_inputs": 0,
            "new_runtime_outputs": 0,
            "optimizer_steps": 0,
        },
        "inference": {
            "provider": "CPUExecutionProvider",
            "seed": 20260730,
            "commands_x_m_s": [0.0, 0.074, 0.077, 0.080],
            "samples_per_context_command": 4,
            "required_exactness": (
                "T164 inactive routes and x=0 stay exact after head "
                "composition; plateau outputs are exact to composed source "
                "for x<=.077 and exact to same-state x=.077 at x=.080"
            ),
        },
        "decision_rule": {
            "pass": (
                "EARN_T231_T228_NOMINAL_BEHAVIOR_MATRIX_"
                "PREREGISTRATION_ONLY"
            ),
            "fail": "HOLD_T228_BEHAVIOR_AND_AUDIT_COMPOSITION",
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
            "execute_composition_contract": True,
            "nominal_behavior_matrix": False,
            "decisive_condition_matrices": False,
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
    MARKDOWN.write_text(
        "# T230 T228 deployment composition preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Three raw T228 graphs; one frozen T164-final deployment base\n"
        "- Retained global x=.080 to .077 plateau\n"
        "- New behavior / optimizer / hosted / robot: `0/0/0/0`\n"
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
