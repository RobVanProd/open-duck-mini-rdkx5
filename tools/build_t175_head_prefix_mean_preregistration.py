#!/usr/bin/env python3
"""Freeze a two-leaf prefix mean for T170's nominal adapter head."""

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


T174 = ANALYSIS / "t174_t173_failure_autopsy_result.json"
T173 = ANALYSIS / "t173_t170_targeted_y_negative_result.json"
T172 = ANALYSIS / "t172_t170_postexport_composition_result.json"
T172_PREREG = ANALYSIS / "t172_t170_postexport_composition_preregistration.json"
OLD_SWA = ANALYSIS / "ground_up_actor_swa_screen_result.json"
OLD_SWA_PREREG = ANALYSIS / "ground_up_actor_swa_screen_preregistration.json"
OUTPUT = ANALYSIS / "t175_head_prefix_mean_preregistration.json"
MARKDOWN = ANALYSIS / "T175_HEAD_PREFIX_MEAN_PREREGISTRATION_20260729.md"
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t175_head_prefix_mean.py"
TEST = ROOT / "tests" / "test_t175_head_prefix_mean.py"
HEAD_NAMES = [
    "nominal_condition_negative_adapter_weight",
    "nominal_condition_negative_adapter_bias",
]


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T175: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T175 preregistration requires clean worktree")
    values = {
        "t174": json.loads(T174.read_text(encoding="utf-8")),
        "t173": json.loads(T173.read_text(encoding="utf-8")),
        "t172": json.loads(T172.read_text(encoding="utf-8")),
        "t172_prereg": json.loads(T172_PREREG.read_text(encoding="utf-8")),
        "old_swa": json.loads(OLD_SWA.read_text(encoding="utf-8")),
        "old_swa_prereg": json.loads(
            OLD_SWA_PREREG.read_text(encoding="utf-8")
        ),
    }
    graphs = {
        {
            0: "source",
            1_003_520: "half",
            2_007_040: "final",
        }[int(row["step"])]: row["structure"]["transformed"]
        for row in values["t172"]["graphs"]
    }
    old_actor_names = values["old_swa_prereg"]["transform"][
        "actor_initializers"
    ]
    frozen = {
        "builder": receipt(BUILDER),
        "runner": receipt(RUNNER),
        "test": receipt(TEST),
        "t174_autopsy": receipt(T174),
        "t173_targeted_result": receipt(T173),
        "t172_composition": receipt(T172),
        "t172_composition_preregistration": receipt(T172_PREREG),
        "old_actor_swa_result": receipt(OLD_SWA),
        "old_actor_swa_preregistration": receipt(OLD_SWA_PREREG),
    }
    checks = {
        "t174_exact_head_attribution_green": (
            values["t174"]["status"] == "PASS_T174_T173_FAILURE_AUTOPSY"
            and not values["t174"]["failed_checks"]
            and values["t174"]["checks"][
                "head_difference_does_not_change_hidden_state"
            ]
        ),
        "t173_is_single_cell_persistence_hold": (
            values["t173"]["status"]
            == "HOLD_T173_T170_TARGETED_Y_NEGATIVE"
            and values["t173"]["condition"]["green_cells"] == 15
        ),
        "t172_graph_contract_green": (
            values["t172"]["status"]
            == "PASS_T172_T170_POSTEXPORT_COMPOSITION"
            and not values["t172"]["failed_checks"]
        ),
        "source_half_final_graphs_present": (
            set(graphs) == {"source", "half", "final"}
            and all(Path(row["path"]).is_file() for row in graphs.values())
        ),
        "old_actor_swa_is_closed_and_scope_disjoint": (
            values["old_swa"]["status"] == "PASS_ACTOR_SWA_SCREEN_NO_WINNER"
            and values["old_swa"]["decision"]
            == "CLOSE_ACTOR_SWA_STABILIZATION_FORMULATION"
            and set(old_actor_names).isdisjoint(HEAD_NAMES)
            and len(old_actor_names) == 8
        ),
        "new_scope_is_only_two_previously_absent_head_leaves": (
            len(HEAD_NAMES) == 2 and set(old_actor_names).isdisjoint(HEAD_NAMES)
        ),
        "zero_behavior_training_hosted_robot_now": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T175 preregistration checks failed: {failed}")
    basis: dict[str, Any] = {
        "schema_version": "open_duck.t175_head_prefix_mean_preregistration.v1",
        "status": "PREREGISTERED_T175_HEAD_PREFIX_MEAN",
        "question": (
            "Does cumulative averaging of only the newly trained nominal "
            "adapter head remove the late single-cell drift while leaving "
            "the frozen mature actor and prior deployment repairs exact?"
        ),
        "frozen_inputs": frozen,
        "graphs": graphs,
        "contexts": values["t172_prereg"]["contexts"],
        "transform": {
            "head_initializers": HEAD_NAMES,
            "arithmetic": (
                "float64 arithmetic mean of prefix members, one final "
                "float32 cast per tensor"
            ),
            "half_members": ["source", "half"],
            "final_members": ["source", "half", "final"],
            "all_other_initializers": "source bit-exact",
            "all_nodes": "source bit-exact",
            "scalar_search": False,
            "tunable_parameters": 0,
            "new_runtime_inputs": 0,
            "new_runtime_outputs": 0,
        },
        "prior_family_boundary": {
            "closed_old_actor_swa_initializers": old_actor_names,
            "new_head_initializers": HEAD_NAMES,
            "sets_disjoint": True,
            "causal_new_evidence": (
                "T171 froze the old mature actor exactly; T174 localized "
                "the only behavior failure to the two-leaf head."
            ),
        },
        "inference": {
            "provider": "CPUExecutionProvider",
            "seed": 20260729,
            "commands_x_m_s": [0.0, 0.074, 0.077, 0.080],
            "samples_per_context_command": 8,
            "required_exactness": (
                "all inactive routes and all x0 outputs bit-exact to source"
            ),
        },
        "decision_rule": {
            "pass": (
                "EARN_T176_HEAD_PREFIX_MEAN_TARGETED_MATRIX_"
                "PREREGISTRATION_ONLY"
            ),
            "fail": "CLOSE_HEAD_PREFIX_MEAN_WITHOUT_BEHAVIOR",
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
            "execute_transform_contract": True,
            "behavior": False,
            "training": False,
            "full_r2": False,
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
        "# T175 head-prefix-mean preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Scope: two nominal adapter-head leaves only\n"
        "- Half: mean(source, half); final: mean(source, half, final)\n"
        "- Mature actor, normalizer, routers, repairs, ABI: exact\n"
        "- Behavior/training/hosted/robot: `0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
