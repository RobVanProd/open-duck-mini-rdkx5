#!/usr/bin/env python3
"""Preregister the protected-policy control for the V107 prefix failure."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
V101 = ANALYSIS / "winner_v101_response_conditioned_cpu_contract.json"
V107 = ANALYSIS / "winner_v107_stage_boundary_result.json"
BASE_PREREG = (
    ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
)
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
SOURCE = (
    ROOT
    / "artifacts/runtime_handoff/rdkx5_native_20260719/policies"
    / "T2_EQUAL_512000.onnx"
)
OUTPUT = ANALYSIS / "winner_v108_prefix_handoff_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V108_PREFIX_HANDOFF_PREREGISTRATION_20260724.md"

V101_SHA256 = "4f44c2ff9de0ee715b09c1c95048bedb0a43f3334eaa70970dac8c08d6e047d0"
V107_SHA256 = "3f9bd6f9173131dbb17e9eef570831df5a67fc291bee094fe76b61772f8e6f6a"
BASE_PREREG_SHA256 = (
    "c8f986ceb24863f33c1fc99170548d2e255cb6a26737d3f74762f8dcd4485a24"
)
REFERENCE_SHA256 = (
    "8102d9cd139584816d807ca635bcca6d37fa6b3c455848e00395b6d565968212"
)
SOURCE_SHA256 = "99d3afce0dfac127816c6327665c35b3c403e005f25cd0a505dfcb37f01304de"
EXPANDED_SHA256 = (
    "0076e743edb67bc8139d6c70ed6ee2973945c483640180b9de90da190a5a038e"
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


def graph_equivalence(source: Path, expanded: Path) -> dict[str, Any]:
    source_session = ort.InferenceSession(
        str(source), providers=["CPUExecutionProvider"]
    )
    expanded_session = ort.InferenceSession(
        str(expanded), providers=["CPUExecutionProvider"]
    )
    rng = np.random.default_rng(108)
    maximum_action_error = 0.0
    maximum_state_error = 0.0
    maximum_context_action_effect = 0.0
    maximum_hidden_action_effect = 0.0
    cases = 256
    for index in range(cases):
        obs = rng.normal(0.0, 0.35, size=(1, 115)).astype(np.float32)
        obs[:, 13:83] = np.clip(obs[:, 13:83], -1.5, 1.5)
        obs[:, 101:115] = np.clip(obs[:, 101:115], -1.0, 1.0)
        if index % 4 == 0:
            obs[:, 6] = 0.0
        else:
            obs[:, 6] = rng.uniform(0.074, 0.08)
        previous = rng.uniform(-1.0, 1.0, size=(1, 14)).astype(np.float32)
        zero_hidden = np.zeros((1, 64), dtype=np.float32)
        zero_context = np.zeros((1, 64), dtype=np.float32)
        source_action, source_state = source_session.run(
            ["continuous_actions", "previous_action_out"],
            {"obs": obs, "previous_action": previous},
        )
        expanded_action, expanded_state, _ = expanded_session.run(
            ["continuous_actions", "previous_action_out", "h_out"],
            {
                "obs": obs,
                "previous_action": previous,
                "h_in": zero_hidden,
                "calibration_context": zero_context,
            },
        )
        alternate_context = rng.uniform(
            -1.0, 1.0, size=(1, 64)
        ).astype(np.float32)
        alternate_hidden = rng.uniform(
            -1.0, 1.0, size=(1, 64)
        ).astype(np.float32)
        context_action = expanded_session.run(
            ["continuous_actions"],
            {
                "obs": obs,
                "previous_action": previous,
                "h_in": zero_hidden,
                "calibration_context": alternate_context,
            },
        )[0]
        hidden_action = expanded_session.run(
            ["continuous_actions"],
            {
                "obs": obs,
                "previous_action": previous,
                "h_in": alternate_hidden,
                "calibration_context": zero_context,
            },
        )[0]
        maximum_action_error = max(
            maximum_action_error,
            float(np.max(np.abs(source_action - expanded_action))),
        )
        maximum_state_error = max(
            maximum_state_error,
            float(np.max(np.abs(source_state - expanded_state))),
        )
        maximum_context_action_effect = max(
            maximum_context_action_effect,
            float(np.max(np.abs(expanded_action - context_action))),
        )
        maximum_hidden_action_effect = max(
            maximum_hidden_action_effect,
            float(np.max(np.abs(expanded_action - hidden_action))),
        )
    return {
        "cases": cases,
        "maximum_source_to_expanded_action_error": maximum_action_error,
        "maximum_source_to_expanded_previous_action_error": maximum_state_error,
        "maximum_context_action_effect": maximum_context_action_effect,
        "maximum_hidden_action_effect": maximum_hidden_action_effect,
        "exact": all(
            value == 0.0
            for value in (
                maximum_action_error,
                maximum_state_error,
                maximum_context_action_effect,
                maximum_hidden_action_effect,
            )
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expanded-policy", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(
                f"refusing to overwrite Winner-v108 preregistration: {path}"
            )

    expanded = args.expanded_policy.resolve()
    v101 = json.loads(V101.read_text(encoding="utf-8"))
    v107 = json.loads(V107.read_text(encoding="utf-8"))
    equivalence = graph_equivalence(SOURCE, expanded)
    checks = {
        "v101_contract_exact": sha256(V101) == V101_SHA256
        and v101.get("status") == "PASS_WINNER_V101_RESPONSE_CONDITIONED_CPU_CONTRACT",
        "v107_result_exact": sha256(V107) == V107_SHA256
        and v107.get("decision", {}).get("status") == "EXPANDED_INITIAL_FAILED",
        "base_preregistration_exact": sha256(BASE_PREREG)
        == BASE_PREREG_SHA256,
        "reference_exact": sha256(REFERENCE) == REFERENCE_SHA256,
        "protected_source_exact": sha256(SOURCE) == SOURCE_SHA256,
        "expanded_initial_exact": sha256(expanded) == EXPANDED_SHA256,
        "zero_adapter_graph_equivalence_exact": equivalence["exact"],
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    matrix = [
        {
            "arm": "PROTECTED_SOURCE_NO_PREFIX",
            "policy_sha256": SOURCE_SHA256,
            "plant": "P30_ALL_JOINT",
            "command_x_m_s": command,
            "seed": 167_931_544,
            "configuration": None,
            "transport": {
                "sensor_noise_scales": None,
                "native_quantization": False,
                "additional_action_delay_ticks": 0,
                "imu_delay_ticks": 0,
            },
            "duration_ticks": 600,
            "calibration_ticks": 0,
            "home_return_ticks": 0,
        }
        for command in (0.0, 0.074, 0.077, 0.08)
    ]
    value = {
        "schema_version": "winner_v108.prefix_handoff_preregistration.v1",
        "status": (
            "PREREGISTERED_WINNER_V108_PREFIX_HANDOFF_DIAGNOSTIC"
            if not failed
            else "HOLD_WINNER_V108_PREFIX_HANDOFF_DIAGNOSTIC"
        ),
        "failed_checks": failed,
        "checks": checks,
        "causal_question": (
            "Does the byte-frozen repaired source policy pass the exact V107 "
            "nominal matrix when the sole removed treatment is the 250-tick "
            "calibration plus 250-tick home-return physical prefix?"
        ),
        "graph_equivalence": equivalence,
        "policies": {
            "protected_source": {
                "path": str(SOURCE.relative_to(ROOT)),
                "sha256": SOURCE_SHA256,
            },
            "expanded_initial": {
                "path": str(expanded),
                "sha256": EXPANDED_SHA256,
            },
        },
        "matrix": {
            "cells": len(matrix),
            "sha256": canonical_sha256(matrix),
            "rows": matrix,
        },
        "frozen_comparator": {
            "result": str(V107.relative_to(ROOT)),
            "result_sha256": V107_SHA256,
            "checkpoint": "EXPANDED_INITIAL",
            "same_commands_seed_plant_configuration_transport_and_duration": True,
            "only_treatment_difference": (
                "V107 applies the 250 calibration plus 250 home-return "
                "physical prefix; V108 does not."
            ),
        },
        "decision_rule": {
            "all_four_source_no_prefix_cells_pass": (
                "Select CALIBRATION_PREFIX_PHYSICAL_STATE_HANDOFF as the "
                "preoptimizer defect because graph action/state equivalence is exact."
            ),
            "any_source_no_prefix_cell_fails": (
                "Select BASELINE_SEED_OR_EVALUATOR_MISMATCH and stop before "
                "changing the calibration prefix."
            ),
            "no_checkpoint_selection": True,
            "no_reward_or_closest_ranking": True,
            "no_training_until_result": True,
        },
        "input_hashes": {
            "v101_cpu_contract": sha256(V101),
            "v107_result": sha256(V107),
            "base_preregistration": sha256(BASE_PREREG),
            "reference_features": sha256(REFERENCE),
        },
        "authority": {
            "prefix_handoff_diagnostic_authorized": not failed,
            "formal_behavior_cells_authorized": 4 if not failed else 0,
            "hosted_training_authorized": False,
            "checkpoint_selection_authorized": False,
            "gate5_authorized": False,
            "robot_clearance": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "# Winner-v108 calibration-prefix handoff preregistration\n\n"
        f"Status: `{value['status']}`\n\n"
        "The protected repaired source graph is evaluated in four nominal P30 "
        "cells with the V107 seed and transport, but without the unscored "
        "calibration/home-return prefix. The expanded step-zero graph is "
        "action- and previous-action-exact to the source and its action is "
        "independent of both new adapter inputs before training. Therefore a "
        "four-cell pass attributes the V107 preoptimizer regression to physical "
        "prefix state handoff. This diagnostic cannot select a checkpoint, "
        "authorize training, open Gate 5, or access the robot.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"matrix_sha256={value['matrix']['sha256']}")
    print(f"sha256={sha256(args.output)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
