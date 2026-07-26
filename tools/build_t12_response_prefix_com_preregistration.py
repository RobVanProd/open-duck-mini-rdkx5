#!/usr/bin/env python3
"""Preregister T12 response-prefix handoff at torso COM x = -0.05 m."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t12_response_prefix_com_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T12_RESPONSE_PREFIX_COM_PREREGISTRATION_20260726.md"
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


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def load(name: str) -> dict[str, Any]:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if not args.write:
        raise SystemExit("T12 preregistration requires --write")
    if PREREG.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T12 preregistration")
    t8_prereg = load("t8_state_coherent_handoff_preregistration.json")
    t9_prereg = load("t9_command_aware_prefix_bypass_preregistration.json")
    t9_result = load("t9_command_aware_prefix_bypass_result.json")
    t11_result = load("t11_context_action_observability_result.json")
    t11_audit = load(
        "t11_context_action_observability_independent_audit.json"
    )
    if (
        t9_result["status"] != "PASS_T9_COMMAND_AWARE_PREFIX_BYPASS"
        or t11_result["status"]
        != "HOLD_T11_CONTEXT_ACTION_OBSERVABILITY"
        or t11_audit["status"]
        != "HOLD_T11_CONTEXT_ACTION_INDEPENDENT_AUDIT"
    ):
        raise RuntimeError("T12 causal inputs do not match")
    sources = {
        "builder": receipt(Path(__file__)),
        "runner": receipt(
            ROOT / "tools" / "run_t12_response_prefix_com_screen.py"
        ),
        "worker": receipt(
            ROOT / "tools" / "evaluate_t12_response_prefix_com.py"
        ),
        "independent_auditor": receipt(
            ROOT / "tools" / "audit_t12_response_prefix_com_screen.py"
        ),
        "t6_result": receipt(
            ANALYSIS / "t6_corrected_robustness_screen_result.json"
        ),
        "t7_result": receipt(
            ANALYSIS / "t7_universal_response_support_result.json"
        ),
        "t8_result": receipt(
            ANALYSIS / "t8_state_coherent_handoff_result.json"
        ),
        "t8_independent_audit": receipt(
            ANALYSIS
            / "t8_state_coherent_handoff_independent_audit_v2.json"
        ),
        "t9_result": receipt(
            ANALYSIS / "t9_command_aware_prefix_bypass_result.json"
        ),
        "t9_independent_audit": receipt(
            ANALYSIS
            / "t9_command_aware_prefix_bypass_independent_audit_v2.json"
        ),
        "t11_result": receipt(
            ANALYSIS / "t11_context_action_observability_result.json"
        ),
        "t11_independent_audit": receipt(
            ANALYSIS
            / "t11_context_action_observability_independent_audit.json"
        ),
        "closed_loop_source": receipt(
            ROOT / "tools" / "closed_loop_sim_eval.py"
        ),
        "t6_helpers": receipt(
            ROOT / "tools" / "run_t6_corrected_robustness_screen.py"
        ),
        "t8_helpers": receipt(
            ROOT / "tools" / "run_t8_state_coherent_handoff.py"
        ),
        "t8_worker_helpers": receipt(
            ROOT / "tools" / "evaluate_t8_state_coherent_handoff.py"
        ),
        "t8_adapter": receipt(
            ROOT / "tools" / "t8_state_coherent_eval_adapter.py"
        ),
    }
    checkpoints = [
        {
            "checkpoint_id": item["checkpoint_id"],
            "policy": item["wrapped"],
        }
        for item in t8_prereg["candidate"]["checkpoints"]
    ]
    fits = {
        name: t8_prereg["repository_inputs"][f"fit_{name}"]
        for name in ("p30", "p31_34")
    }
    basis = {
        "schema_version": (
            "open_duck.t12_response_prefix_com_preregistration.v1"
        ),
        "status": "PREREGISTERED_T12_RESPONSE_PREFIX_COM_SCREEN",
        "question": (
            "Does the already-green T9 automatic response-support prefix "
            "prepare enough physical and recurrent state for unchanged V121 "
            "to survive the exact T6 torso-COM-x=-0.05 m failure condition "
            "without learning a context-to-action path?"
        ),
        "causal_basis": {
            "t6": (
                "direct V121 has zero robust survivors at the first failed "
                "R2 endpoint, torso COM x = -0.05 m"
            ),
            "t7": (
                "the universal response-support action is stable and its "
                "response is configuration-sensitive at this endpoint"
            ),
            "t8_t9": (
                "state-coherent response handoff is green for every nominal "
                "moving cell and command-aware bypass is green at x=0"
            ),
            "t10_t11": (
                "learned context-to-action binding is closed before hosted "
                "training; its effect is deployment-visible in only 9/2048 "
                "coherent cases and 1/128 recurrent sequences"
            ),
            "materially_distinct_mechanism": (
                "T12 uses only automatic physical/state preparation plus "
                "V121's existing observation feedback; calibration context "
                "remains diagnostic and policy weights remain unchanged"
            ),
        },
        "sources": sources,
        "playground": {
            "path": t8_prereg["playground"]["path"],
            "control_commit": t8_prereg["playground"]["control_commit"],
            "required_file_sha256": t8_prereg["playground"][
                "required_file_sha256"
            ],
        },
        "candidate": {
            "checkpoints": checkpoints,
            "fits": fits,
            "calibrator": t8_prereg["calibrator"],
            "reference": t8_prereg["repository_inputs"][
                "reference_features"
            ],
            "policy_weights_changed": False,
            "context_policy_effect": "diagnostic only; exact zero-weight ABI",
        },
        "matrix": {
            "checkpoints": 2,
            "fits": ["p30", "p31_34"],
            "commands_x_m_s": [0.074, 0.077, 0.080],
            "torso_com_offset_m": [-0.05, 0.0, 0.0],
            "seed": 167931544,
            "ticks": 600,
            "frequency_hz": 50,
            "formal_cells": 12,
        },
        "handoff_contract": {
            **t8_prereg["handoff_contract"],
            "calibration_ticks": 250,
            "home_return_ticks": 0,
            "policy_hidden_at_handoff": "exact zero",
            "previous_action_at_handoff": (
                "exact final universal response action"
            ),
            "calibration_context": (
                "immutable diagnostic 64-D response context"
            ),
            "applied_target_slot": [83, 97],
        },
        "behavior_contract": t9_prereg["behavior_contract"],
        "protection_contract": t9_prereg["protection_contract"],
        "decision_rule": {
            "pass": (
                "all 12 cells pass core and replacement-quality behavior, "
                "corrected duration protection, exact COM readback, exact "
                "handoff/recurrent/applied-target chains, and zero measured "
                "rate excess"
            ),
            "pass_next_action": (
                "earn only a separately preregistered sequential full R2 "
                "response-prefix ladder; do not authorize hardware"
            ),
            "fail": (
                "close response-prefix state preparation and do not revive "
                "the closed T10/T11 context-action architecture"
            ),
            "partial_results_selection_weight": 0,
            "no_closest_result_promotion": True,
        },
        "authority": {
            "offline_cpu_behavior_cells": 12,
            "optimizer_steps": 0,
            "hosted_or_colab_compute": False,
            "robot_or_rdk_access": False,
            "gate5": False,
            "torque_or_motion": False,
        },
        "execution_now": {
            "simulator_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_or_colab_compute": 0,
            "robot_or_rdk_access": 0,
        },
    }
    value = {
        **basis,
        "preregistered_contract_sha256": canonical_sha256(basis),
    }
    PREREG.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T12 response-prefix negative-COM preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Condition: `torso COM x = -0.05 m`\n"
        "- Matrix: `2 checkpoints × 2 fits × 3 moving commands = 12`\n"
        "- Optimizer/hosted/robot execution: `0/0/0`\n"
        "- Pass earns only a separately preregistered full R2 ladder.\n"
        f"- Canonical SHA-256: "
        f"`{value['preregistered_contract_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(
        "preregistered_contract_sha256="
        f"{value['preregistered_contract_sha256']}"
    )
    print(f"file_sha256={sha256(PREREG)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
