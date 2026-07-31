from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "tools/check_winner_v12_calibrator_support_gate_cpu_contract.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("winner_v12_gate_check", CHECKER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def valid_header() -> dict:
    return {
        "schema_version": "winner_v12.calibrator_support_gate_cpu_contract.v1",
        "status": "PASS_WINNER_V12_CALIBRATOR_SUPPORT_GATE_CPU_CONTRACT_FROZEN",
        "decision": "AUTHORIZE_ONE_ZERO_CELL_SUPPORT_GATE_CPU_CONTRACT_RUN_ONLY",
        "execution_now": {
            "formal_support_cells": 0,
            "heldout_repeat_cells": 0,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        },
        "formal_gate_after_contract": {
            "checkpoint_labels": ["half", "final"],
            "main_cells_per_checkpoint": 124,
            "main_cells_total": 248,
            "heldout_repeat_cells_total": 64,
            "duration_ticks_per_cell": 250,
            "all_cells_at_both_checkpoints_must_pass": True,
        },
        "verified_checkpoints": {"half": {}, "final": {}},
    }


def test_zero_cell_header_is_exact() -> None:
    checker = load_checker()
    checker.validate_contract_header(valid_header())
    assert checker.EXPECTED_EXECUTION["formal_support_cells"] == 0


@pytest.mark.parametrize(
    ("section", "key", "value"),
    [
        ("execution_now", "formal_support_cells", 1),
        ("execution_now", "robot_or_rdk_access", 1),
        ("authority", "robot_clearance", True),
        ("formal_gate_after_contract", "main_cells_total", 247),
    ],
)
def test_header_rejects_authority_or_dimension_drift(
    section: str, key: str, value: object
) -> None:
    checker = load_checker()
    contract = valid_header()
    contract[section][key] = value
    with pytest.raises(ValueError):
        checker.validate_contract_header(contract)


def test_checker_cannot_execute_formal_cell() -> None:
    source = CHECKER.read_text(encoding="utf-8")
    assert "gate.run_cell(" not in source
    assert "gate.step_episode(" not in source
    assert '"formal_support_cells": 0' in source
    assert "--zero-cell-contract-authorized" in source
