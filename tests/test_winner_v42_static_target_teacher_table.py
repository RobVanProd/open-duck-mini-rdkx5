from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v42_static_target_teacher_table.py"


def load():
    spec = importlib.util.spec_from_file_location("winner_v42_runner", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_teacher_table_scope_is_exact() -> None:
    module = load()
    assert module.CONFIGURATION_IDS == (
        "COM_X_NEG", "COM_CORNER_00", "COM_CORNER_01", "COM_CORNER_02",
        "COM_CORNER_03", "OPTIONAL_AGGREGATE_HEAVY_AFT", "DISCOVERY_02",
        "DISCOVERY_03", "DISCOVERY_06", "DISCOVERY_09", "DISCOVERY_10",
        "HELDOUT_04", "HELDOUT_07", "HELDOUT_09", "HELDOUT_15",
    )
    assert module.PLANTS == ("P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH")
    assert module.TARGETS_PER_CONFIGURATION == 729
    assert module.EXPECTED_CANDIDATE_PLANT_CELLS == 21_870
    assert module.TICKS == 250


def test_compact_receipt_preserves_selection_and_safety_fields() -> None:
    module = load()
    value = {
        "plant": module.PLANTS[0],
        "terminal": {"tick": 17},
        "episode": {
            "valid_ticks": 17,
            "minimum_base_z_m": 0.12,
            "maximum_abs_tilt_rad": 0.35,
            "maximum_final_window_gyro_xy_norm_rad_s": 1.2,
            "maximum_current_a": 1.4,
            "maximum_torque_nm": 1.1,
        },
        "support_pass": False,
        "all_actions_bounded": True,
        "raw_target_sha256": "a" * 64,
        "action_trace_sha256": "b" * 64,
        "action_hash_chain_sha256": "c" * 64,
    }
    compact = module.compact_plant_result(value)
    assert compact["terminal_tick"] == 17
    assert compact["valid_ticks"] == 17
    assert compact["maximum_current_a"] == 1.4
    assert compact["all_actions_bounded"] is True


def test_runner_uses_corrected_static_expansion_and_no_training_or_hardware() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "v41.v38.expand_mirrored_blocks = v41_v2.expand_static_target" in source
    assert "v41.candidate_coordinates()" in source
    assert "v41.candidate_key" in source
    assert "training.adam_step" not in source
    assert "np.random" not in source
    assert "--hardware-authorized" not in source
    assert '"optimizer_updates": 0' in source
    assert '"locomotion_training_steps": 0' in source
    assert '"robot_or_rdk_access": 0' in source
    assert '"training_authorized": False' in source
    assert '"closest_result_selection": False' in source
    assert "diagnostic_best_not_promoted" in source
