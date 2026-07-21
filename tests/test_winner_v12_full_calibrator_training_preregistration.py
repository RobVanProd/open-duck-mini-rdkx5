from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREREG = (
    ROOT / "outputs/analysis/winner_v12_full_calibrator_training_preregistration.json"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load() -> dict:
    return json.loads(PREREG.read_text(encoding="utf-8"))


def test_preregistration_authorizes_implementation_contract_only() -> None:
    prereg = load()
    assert prereg["status"] == "PREREGISTERED_WINNER_V12_FULL_CALIBRATOR_TRAINING"
    assert (
        prereg["decision"] == "AUTHORIZE_FULL_CALIBRATOR_RUNNER_AND_CPU_CONTRACT_ONLY"
    )
    assert prereg["authority"] == {
        "implement_full_training_runner": True,
        "run_fresh_cpu_implementation_contract": True,
        "optimizer_updates_now": 0,
        "full_calibrator_training_now": False,
        "formal_support_cells_now": 0,
        "locomotion_training_or_behavior_cells": False,
        "colab_or_other_hosted_compute_now": False,
        "local_gpu_or_igpu": False,
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "gate5_deployment_or_robot_clearance": False,
    }


def test_schedule_and_population_are_exact_and_heldout_is_excluded() -> None:
    prereg = load()
    population = prereg["population"]
    assert population["training_configuration_count"] == 40
    assert population["heldout_configuration_count"] == 16
    assert population["episodes_per_update"] == 80
    assert population["scheduled_tick_slots_per_update"] == 20_000
    assert "actual" in population["sample_accounting"]
    assert not set(population["training_configuration_ids"]) & set(
        population["heldout_configuration_ids"]
    )
    assert prereg["stage1"]["update_count"] == 100
    assert prereg["stage1"]["scheduled_tick_slot_capacity"] == 2_000_000
    assert prereg["stage2"]["update_count"] == 100
    assert prereg["stage2"]["scheduled_tick_slot_capacity"] == 2_000_000


def test_parameter_initialization_and_stage_handoff_are_frozen() -> None:
    prereg = load()
    initialization = prereg["parameter_initialization"]
    assert initialization["seed"] == 60720
    assert initialization["tree_sha256"] == (
        "2b8cbc46517c1e6b073c7b93a9fe4c1b50e66e1ee7be514371bafd2b050e0127"
    )
    assert initialization["action_head_exact_zero"] is True
    assert initialization["value_head_exact_zero"] is True
    assert "fresh Adam count 0" in prereg["stage1"]["optimizer_initialization"]
    assert "exact final Stage-1" in prereg["stage2"]["stage1_to_stage2_handoff"]
    assert (
        "do not carry Stage-1 Adam state"
        in prereg["stage2"]["stage1_to_stage2_handoff"]
    )
    assert "fresh Adam count 0" in prereg["stage2"]["optimizer_initialization"]


def test_calibrator_is_not_misrepresented_as_trained_locomotion() -> None:
    prereg = load()
    scope = prereg["architectural_scope"]
    assert scope["calibrator_only"] is True
    assert scope["locomotion_adapter_training"] is False
    assert scope["locomotion_adapter_enabled"] is False
    assert scope["calibration_context_used_for_walking_in_this_run"] is False
    assert prereg["future_frozen_support_gate"]["pass_authorizes_only"].startswith(
        "a separate response-conditioned locomotion-training preregistration"
    )


def test_two_persistent_checkpoints_require_complete_persistence_gate() -> None:
    prereg = load()
    assert prereg["persistent_checkpoints"] == [
        {
            "label": "half",
            "stage2_scheduled_tick_slots": 1_000_000,
            "stage2_update": 50,
        },
        {
            "label": "final",
            "stage2_scheduled_tick_slots": 2_000_000,
            "stage2_update": 100,
        },
    ]
    gate = prereg["future_frozen_support_gate"]
    assert gate["cells_per_checkpoint"] == 124
    assert gate["all_cells_at_both_checkpoints_must_pass"] is True
    assert gate["selection_by_closest_result"] is False
    assert [row["id"] for row in gate["sensor_transport_population"]] == [
        "NATIVE_INPUT_QUANTIZATION",
        "DECLARED_SENSOR_NOISE",
        "ACTION_DELAY_1",
        "ACTION_DELAY_2",
        "IMU_DELAY_1",
        "IMU_DELAY_2",
    ]
    assert "checkpoint_index" in gate["sensor_noise_seed_derivation"]
    context = gate["heldout_context_gate"]
    assert "strictly below" in context["required_prediction_rule"]
    assert "exceed 1e-7" in context["matched_plant_context_rule"]
    assert "bit-exact" in context["repeat_rule"]
    assert context["true_configuration_or_plant_label_enters_network"] is False


def test_every_update_is_an_atomic_recovery_boundary() -> None:
    artifact = load()["artifact_contract"]
    assert artifact["atomic_recovery_snapshot_every_updates"] == 1
    assert "only after its snapshot rename commits" in artifact["resume_rule"]


def test_attention_is_deferred_until_response_state_transport_fails() -> None:
    scope = load()["architectural_scope"]
    assert scope["flat_transport_kernel_added"] is False
    assert scope["quadratic_attention_added"] is False
    assert "No evidence yet" in scope["reason_attention_is_deferred"]


def test_fresh_contract_must_use_the_recovered_cpu_environment() -> None:
    assert load()["implementation_contract_environment"] == {
        "platform": "CPU only",
        "python": "3.12.13",
        "jax": "0.7.2",
        "jaxlib": "0.7.2",
        "mujoco": "3.9.0",
        "numpy": "2.0.2",
        "onnx": "1.22.0",
        "onnxruntime": "1.27.0",
    }


def test_every_source_hash_reproduces_and_evidence_checks_pass() -> None:
    prereg = load()
    assert prereg["checks"] and all(prereg["checks"].values())
    for item in prereg["sources"].values():
        path = ROOT / item["path"]
        observed = lf_sha256(path) if item["hash_mode"] == "lf" else sha256(path)
        assert observed == item["sha256"], item["path"]
