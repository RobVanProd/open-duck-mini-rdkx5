import importlib.util
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "build_winner_v3_current_gate_application_contract.py"
SPEC = importlib.util.spec_from_file_location("current_gate_contract", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_primary_source_conversion_is_exact() -> None:
    assert math.isclose(MODULE.MOTOR_CONSTANT_NM_PER_A, 0.784532, abs_tol=1e-12)
    assert MODULE.OVERCURRENT_TICKS == 100


def test_prospective_gate_does_not_reclassify_winner_v3() -> None:
    contract = MODULE.build_contract()
    assert contract["scope"]["completed_winner_v3_result_reclassified"] is False
    assert contract["scope"]["training_authorized"] is False
    gate = contract["prospective_offline_candidate_gate"]
    assert gate["strict_overcurrent_threshold_a"] == 2.0
    assert gate["strict_overcurrent_trip_ticks"] == 100
    assert gate["rated_current_p95"]["candidate_pass_fail"] is False


def test_stall_envelope_matches_manufacturer_values() -> None:
    contract = MODULE.build_contract()
    gate = contract["prospective_offline_candidate_gate"]
    assert gate["per_joint_peak_current_a_max"] == 2.5
    assert math.isclose(
        gate["per_joint_peak_torque_nm_max"],
        19.5 * MODULE.KGF_CM_TO_NM,
        abs_tol=1e-12,
    )
