#!/usr/bin/env python3
"""Freeze the T13 existing-recurrence shadow-handoff CPU contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "t13_shadow_hidden_preregistration.json"
MARKDOWN = ANALYSIS / "T13_SHADOW_HIDDEN_PREREGISTRATION_20260726.md"
T12_PREREG = ANALYSIS / "t12_response_prefix_com_preregistration.json"
T12_RESULT = ANALYSIS / "t12_response_prefix_com_result.json"
T12_AUDIT = ANALYSIS / "t12_response_prefix_com_independent_audit.json"


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


def receipt(path: Path) -> dict[str, Any]:
    path = path.resolve()
    return {
        "path": str(path),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def main() -> int:
    t12_prereg = json.loads(T12_PREREG.read_text(encoding="utf-8"))
    t12_result = json.loads(T12_RESULT.read_text(encoding="utf-8"))
    t12_audit = json.loads(T12_AUDIT.read_text(encoding="utf-8"))
    if (
        t12_result["status"] != "HOLD_T12_RESPONSE_PREFIX_COM_SCREEN"
        or t12_result["decision"]
        != "CLOSE_RESPONSE_PREFIX_STATE_PREPARATION"
        or t12_result["summary"]["green_cells"] != 5
        or t12_audit["status"]
        != "PASS_T12_RESPONSE_PREFIX_COM_INDEPENDENT_AUDIT"
        or t12_audit["issues"]
    ):
        raise RuntimeError("T13 predecessor evidence changed")

    sources = {
        "builder": receipt(Path(__file__)),
        "runner": receipt(
            ROOT / "tools" / "run_t13_shadow_hidden_contract.py"
        ),
        "worker": receipt(
            ROOT / "tools" / "evaluate_t13_shadow_hidden_contract.py"
        ),
        "adapter": receipt(
            ROOT / "tools" / "t13_shadow_hidden_eval_adapter.py"
        ),
        "independent_auditor": receipt(
            ROOT / "tools" / "audit_t13_shadow_hidden_contract.py"
        ),
        "tests": receipt(
            ROOT / "tests" / "test_t13_shadow_hidden_contract.py"
        ),
        "t8_adapter": receipt(
            ROOT / "tools" / "t8_state_coherent_eval_adapter.py"
        ),
        "closed_loop_source": receipt(
            ROOT / "tools" / "closed_loop_sim_eval.py"
        ),
        "t10_result": receipt(
            ANALYSIS
            / "t10_response_conditioned_continuation_cpu_result.json"
        ),
        "t11_result": receipt(
            ANALYSIS / "t11_context_action_observability_result.json"
        ),
        "t12_result": receipt(T12_RESULT),
        "t12_independent_audit": receipt(T12_AUDIT),
    }
    candidate = {
        "checkpoints": t12_prereg["candidate"]["checkpoints"],
        "fits": t12_prereg["candidate"]["fits"],
        "calibrator": t12_prereg["candidate"]["calibrator"],
        "reference": t12_prereg["candidate"]["reference"],
        "policy_weights_changed": False,
        "new_policy_inputs": False,
        "new_policy_outputs": False,
        "executed_prefix_actions_changed": False,
        "locomotion_action_used_during_prefix": False,
    }
    basis = {
        "schema_version": "open_duck.t13_shadow_hidden_preregistration.v1",
        "status": "PREREGISTERED_T13_SHADOW_HIDDEN_CPU_CONTRACT",
        "question": (
            "Can the already-trained V121 recurrent state observe the exact "
            "250-tick response prefix in shadow mode and carry a finite, "
            "plant-sensitive, action-visible h_in across the state-coherent "
            "handoff, without changing weights or executed prefix actions?"
        ),
        "causal_basis": {
            "t12_result": (
                "The exact response prefix plus ordinary zero-initialized "
                "V121 recurrence passed only 5/12 negative-COM cells. All "
                "handoff, rate, tracking, and COM readback checks were exact; "
                "the remaining failure was closed-loop falls."
            ),
            "t10_t11_closure": (
                "The added response-context adapter family was closed after "
                "its learned context changed the final action on only 9/2048 "
                "coherent states and 1/128 causal sequences."
            ),
            "material_difference": (
                "T13 adds no context-to-action weights. It chains the frozen "
                "V121 actor's own existing h_out over the real calibration "
                "observations and realized previous actions while ignoring "
                "its shadow action, then supplies that semantically aligned "
                "state as the first locomotion h_in."
            ),
            "untried_path": (
                "T8/T12 explicitly required locomotion hidden state to be "
                "zero. Repository response-prefix paths use calibrator h_out "
                "as a separate context; none transfers a shadow-updated V121 "
                "recurrent state at locomotion handoff."
            ),
            "phase_check": (
                "A read-only T12 tick-zero comparison found the calibrated "
                "physical pose already closest to reference phase zero, so "
                "phase reassignment is not selected."
            ),
        },
        "sources": sources,
        "playground": t12_prereg["playground"],
        "candidate": candidate,
        "matrix": {
            "checkpoints": 2,
            "fits": ["p30", "p31_34"],
            "commands_x_m_s": [0.074],
            "torso_com_offset_m": [-0.05, 0.0, 0.0],
            "seed": 167931544,
            "calibration_ticks": 250,
            "scored_locomotion_ticks": 1,
            "simulator_prefix_cells": 4,
            "scored_behavior_cells": 0,
        },
        "shadow_contract": {
            "calibrator_action_remains_executed": True,
            "locomotion_policy_action_during_prefix_is_ignored": True,
            "locomotion_shadow_inputs": [
                "exact 115-D zero-command calibration observation",
                "realized prior calibrator action",
                "chained V121 h_out",
                "zero diagnostic calibration_context because the T8 context branch is exact zero-weight",
            ],
            "handoff": {
                "h_in": "final shadow V121 h_out",
                "previous_action": "final executed calibrator action",
                "calibration_context": "final frozen calibrator h_out",
                "phase": [1.0, 0.0],
                "applied_target": "preserved physical observer state",
            },
        },
        "pass_rule": {
            "all_four_cells_complete_on_cpu": True,
            "all_com_readbacks_exact": True,
            "all_prefix_actions_ignored_and_250_shadow_steps_exact": True,
            "all_shadow_hidden_states_finite_nonzero_and_exact_at_handoff": True,
            "all_tick_zero_graph_replays_bit_exact": True,
            "all_bounds_and_rate_checks_green": True,
            "all_x0_counterfactual_actions_and_state_outputs_exact_zero": True,
            "minimum_shadow_vs_zero_final_action_linf": 1.0e-6,
            "minimum_cross_plant_hidden_linf": 1.0e-7,
            "minimum_same_observation_cross_plant_final_action_linf": 1.0e-6,
        },
        "decision_rule": {
            "pass": (
                "Authorize only a separately preregistered T14 12-cell "
                "negative-COM behavior screen using this exact handoff."
            ),
            "fail": (
                "Close existing-recurrent shadow handoff. Do not train it, "
                "tune a hidden scale, remap coordinates, or run behavior."
            ),
            "partial_results_selection_weight": 0,
            "no_threshold_changes_after_outcome": True,
        },
        "authority": {
            "cpu_only": True,
            "optimizer_steps": 0,
            "hosted_or_colab_compute": False,
            "checkpoint_selection": False,
            "deployment": False,
            "gate5": False,
            "robot_or_rdk_access": False,
        },
        "execution_now": {
            "simulator_prefix_cells": 0,
            "scored_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_or_colab_compute": 0,
            "robot_or_rdk_access": 0,
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
        "\n".join(
            [
                "# T13 shadow-hidden CPU contract preregistration",
                "",
                "T13 tests one materially distinct zero-training handoff: "
                "the frozen V121 recurrence observes the response prefix in "
                "shadow mode, while only the calibrator action is executed.",
                "",
                "- Matrix: `2 checkpoints × 2 fits × 1 tick = 4 prefix cells`",
                "- Scored behavior: `0`",
                "- Optimizer / hosted / robot: `0 / 0 / 0`",
                "- Pass: shadow state must be exact, finite, plant-sensitive, "
                "and visibly change the graph-authoritative final action.",
                "- Fail: close the mechanism without a behavior run or hidden "
                "coordinate tuning.",
                (
                    "- Contract SHA-256: "
                    f"`{value['preregistered_contract_sha256']}`"
                ),
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(value["preregistered_contract_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
