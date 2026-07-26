from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import t9_command_aware_eval_adapter as adapter  # noqa: E402
from run_t9_command_aware_prefix_bypass import (  # noqa: E402
    bypass_checks,
    canonical_sha256,
)


def test_t9_adapter_is_versioned_narrow_and_default_off() -> None:
    contract = adapter.contract()
    assert contract["base_patched_source_sha256"] == (
        "1c7de5aba3b498975c3ef02c13599d176527028caaa0058172760125734e5a88"
    )
    assert contract["patched_source_sha256"] == (
        "c9750a4aa493425a128c743a040dcb7358c44060da141b341efd8ebfb19afea1"
    )
    assert contract["patch_count"] == 5
    module = adapter.load_module()
    field = module.ClosedLoopConfig.__dataclass_fields__[
        "response_zero_context_bypass"
    ]
    assert field.default is False


def test_bypass_checks_require_zero_context_and_exact_state_chains() -> None:
    zero_context_sha = hashlib.sha256(
        np.zeros((1, 64), dtype=np.float32).tobytes()
    ).hexdigest()
    response = {
        "enabled": False,
        "zero_context_bypass": True,
        "calibration_ticks": 0,
        "home_return_ticks": 0,
        "context_sha256": zero_context_sha,
        "context_shape": [1, 64],
        "context_finite": True,
        "locomotion_phase_reset": [1.0, 0.0],
        "locomotion_hidden_exact_zero": True,
        "locomotion_previous_action_exact_zero": True,
        "applied_target_observation_matches_bridge": True,
    }
    run = {"modes": {"fitted": {"response_calibration": response}}}
    rows = []
    for tick in range(2):
        rows.append(
            {
                "obs_state": [0.0] * 115,
                "applied_target_rad": [0.0] * 14,
                "action": [0.0] * 14,
                "policy_state_input": {
                    "previous_action": [[0.0] * 14],
                    "h_in": [[0.0] * 64],
                },
                "policy_state_output": {
                    "previous_action_out": [[0.0] * 14],
                    "h_out": [[0.0] * 64],
                },
                "policy_calibration_context_sha256": zero_context_sha,
                "policy_graph_authoritative_output": True,
                "policy_host_action_delta_max_abs": 0.0,
                "tick": tick,
            }
        )
    assert all(bypass_checks(run, rows).values())
    rows[1]["policy_calibration_context_sha256"] = "changed"
    assert bypass_checks(run, rows)["context_immutable"] is False


def test_t9_preregistration_is_canonical_when_present() -> None:
    path = (
        ROOT
        / "outputs"
        / "analysis"
        / "t9_command_aware_prefix_bypass_preregistration.json"
    )
    if not path.is_file():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    basis = {
        key: value[key]
        for key in (
            "question",
            "causal_basis",
            "repository_inputs",
            "playground",
            "candidate",
            "matrix",
            "bypass_contract",
            "behavior_contract",
            "protection_contract",
            "reused_t8_evidence",
            "decision_rule",
            "authority",
            "execution_contract",
        )
    }
    assert canonical_sha256(basis) == value["preregistered_contract_sha256"]
    assert value["matrix"]["new_cells"] == 4
    assert value["matrix"]["reused_t8_moving_cells"] == 12
    assert value["authority"]["training_or_hosted_compute"] is False


def test_t9_independent_auditor_does_not_import_runner() -> None:
    source = (
        ROOT / "tools" / "audit_t9_command_aware_prefix_bypass.py"
    ).read_text(encoding="utf-8")
    forbidden = "run_" + "t9_command_aware_prefix_bypass"
    assert forbidden not in source
