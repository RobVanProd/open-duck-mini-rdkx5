from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "outputs/analysis/winner_v12_calibrator_training_preregistration.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def raw_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_training_prereg_follows_winner_v12_without_starting_training() -> None:
    artifact = load(ARTIFACT)
    assert artifact["status"] == "PREREGISTERED_IMPLEMENTATION_NOT_RUN"
    assert artifact["decision"] == (
        "AUTHORIZE_WINNER_V12_CALIBRATOR_IMPLEMENTATION_AND_CPU_SMOKE_CONTRACT_ONLY"
    )
    assert artifact["why_this_follows_evidence"] == {
        "winner_v10_terminal_failure": (
            "HOLD_WINNER_V10_R2_CONDITION7_TORSO_COM_X_NEG"
        ),
        "winner_v12_mechanics_pass": (
            "PASS_WINNER_V12_ZERO_PPO_DECOMPOSED_BACKEND_MECHANICS"
        ),
        "closed_winner_v11_preserved": True,
        "manual_configuration_route_reopened": False,
        "protected_walking_policy_changed": False,
        "locomotion_adapter_trained_in_this_stage": False,
    }
    assert artifact["authority"]["optimizer_steps_now"] == 0
    assert artifact["authority"]["formal_support_cells_now"] == 0
    assert artifact["authority"]["full_calibrator_training"] is False


def test_training_prereg_is_automatic_and_preserves_both_runtime_contracts() -> None:
    artifact = load(ARTIFACT)
    automatic = artifact["automatic_only"]
    assert automatic["manual_measurements_required"] is False
    assert automatic["mass_com_inertia_dimensions_component_identity_inputs"] is False
    assert automatic["true_configuration_actor_inputs"] is False
    assert automatic["true_configuration_auxiliary_targets"] is False
    assert automatic["configuration_visible_only_to_simulator_randomizer"] is True
    assert automatic["runtime_context_persisted_between_sessions"] is False
    routing = automatic["training_data_routing"]
    assert routing["response_encoder_inputs"] == (
        "deployable obs[1,115], previous_action[1,14], and h_in[1,64] only"
    )
    assert routing["action_head_input"] == "response encoder h_out[1,64] only"
    assert routing["training_only_value_head_input"] == (
        "response encoder h_out[1,64] only"
    )
    assert routing["simulator_randomizer_fields_concatenated_to_network_input"] is False
    assert (
        "[0:6], [13:41], and [83:99] only" in routing["training_only_auxiliary_targets"]
    )
    interface = artifact["frozen_interface"]
    assert interface["observation_contract"] == "winner-v2-115d"
    assert interface["runtime_v1_101x14_changed"] is False
    assert interface["runtime_v2_115d_semantics_changed"] is False
    assert interface["calibration_ticks"] == 250


def test_two_stage_training_has_disjoint_trainable_leaves() -> None:
    stages = load(ARTIFACT)["two_stage_training"]
    stage1 = stages["stage_1_response_encoder"]
    stage2 = stages["stage_2_support_controller"]
    assert stage1["frozen_leaves"] == ["action_weight", "action_bias"]
    assert set(stage1["trainable_leaves"]).isdisjoint(stage1["frozen_leaves"])
    assert stage1["true_configuration_label_used"] is False
    assert "{-0.25,0,+0.25}" in stage1["rollout_action"]
    assert "exploration generator is training-only" in stage1["rollout_action"]
    assert "realized bounded action" in stage1["rollout_action"]
    transition_order = " ".join(stage1["transition_order"])
    assert "previous_action is realized action a_(t-1)" in transition_order
    assert "a_(t-2), a_(t-3), and a_(t-4)" in transition_order
    assert "obs[83:97] is applied_target_t" in transition_order
    assert "auxiliary predictor consumes current h_t" in transition_order
    assert "std=max(empirical_std,1e-6)" in stage1["loss"]
    assert "heldout cells excluded" in stage1["loss"]
    assert stage1["required_nonzero_gradient_paths"] == [
        "previous_action_weight",
        "auxiliary_action_weight",
    ]
    assert stage2["trainable_leaves"] == [
        "action_weight",
        "action_bias",
        "training_only_log_std",
        "training_only_value_weight",
        "training_only_value_bias",
    ]
    assert stage2["stochastic_policy"] == {
        "distribution": "training-only diagonal Gaussian",
        "log_std_initialization": (
            "elementwise log(0.25 * per-joint inward action-delta vector)"
        ),
        "deployable_export": "deterministic bounded action mean only",
        "log_std_exported": False,
    }
    assert stage2["discount_factor_gamma"] == 1.0
    assert stage2["true_configuration_input_to_actor_or_critic"] is False
    validity = stage2["transition_validity"]
    assert validity["per_joint_peak_current_a_max"] == 2.5
    assert validity["per_joint_peak_torque_nm_max"] == 1.91229675
    assert validity["per_joint_peak_torque_kgf_cm_max"] == 19.5
    assert validity["strict_overcurrent_threshold_a"] == 2.0
    assert validity["strict_overcurrent_trip_ticks"] == 100
    assert validity["strict_overcurrent_max_consecutive_ticks"] == 99
    assert validity["invalid_transition_terminates_episode"] is True
    assert stage2["terminal_success_bonus"]["value"] == 250.0
    assert "final 50 ticks" in stage2["terminal_success_bonus"]["condition"]
    assert "<= 0.05 rad/s" in stage2["terminal_success_bonus"]["condition"]
    assert stage2["maximum_return_without_terminal_success"] == 250.0
    assert stage2["settled_full_horizon_return"] == 500.0
    assert stage2["other_reward_terms"] == []
    assert stage2["training_reward_selection_weight"] == "NONE"
    assert stages["joint_end_to_end_finetuning"] is False
    assert stages["locomotion_training"] is False


def test_episode_and_future_support_gate_are_exact() -> None:
    artifact = load(ARTIFACT)
    episode = artifact["calibration_episode"]
    assert episode["frequency_hz"] == 50
    assert episode["duration_ticks"] == 250
    assert episode["command"] == "exact float32 zeros[7]"
    assert episode["phase"] == [1.0, 0.0]
    assert episode["phase_advances"] is False
    assert episode["x0_deadband_on_calibrator"] is False
    gate = artifact["future_support_gate"]
    assert gate["duration_ticks"] == 250
    assert gate["maximum_abs_tilt_rad"] == 0.35
    assert gate["maximum_final_window_gyro_rad_s"] == 0.05
    assert gate["final_window_ticks"] == 50
    assert "unbiased simulator gyro XY" in gate["final_window_gyro_definition"]
    assert gate["minimum_base_z_m"] == 0.1
    assert gate["two_foot_contact_failure_ticks"] == 0
    current = gate["current_safety"]
    assert current["per_joint_peak_current_a_max"] == 2.5
    assert current["per_joint_peak_torque_nm_max"] == 1.91229675
    assert current["strict_overcurrent_threshold_a"] == 2.0
    assert current["strict_overcurrent_trip_ticks"] == 100
    assert current["strict_overcurrent_max_consecutive_ticks"] == 99
    assert current["rated_current_p95"]["candidate_pass_fail"] is False
    assert current["rated_current_p95"]["value_a"] == 0.65
    assert gate["current_estimator"] == (
        "abs(MuJoCo data.actuator_force[joint] N.m) / 0.784532 N.m/A"
    )
    assert gate["model_cells"] == 56
    assert gate["actuator_plants_per_model"] == 2
    assert gate["core_model_actuator_cells_per_checkpoint"] == 112
    assert gate["sensor_transport_conditions_on_nominal_model"] == 6
    assert gate["sensor_transport_actuator_cells_per_checkpoint"] == 12
    assert gate["total_cells_per_checkpoint"] == 124
    assert gate["all_cells_must_pass"] is True
    assert gate["executed_by_this_preregistration"] is False


def test_hidden_domain_binds_all_frozen_model_populations() -> None:
    domain = load(ARTIFACT)["hidden_configuration_domain"]
    assert domain["fixed_anchor_count"] == 24
    assert domain["discovery_count"] == 16
    assert domain["heldout_count"] == 16
    assert len(domain["fixed_anchor_ids"]) == 24
    assert len(domain["discovery_ids"]) == 16
    assert len(domain["heldout_ids"]) == 16
    assert len(domain["sensor_transport_ids"]) == 6
    assert domain["actuator_plants"] == [
        "P30_ALL_JOINT",
        "P31_34_PITCH_WITH_P30_NONPITCH",
    ]
    assert domain["heldout_never_used_for_training_normalization_or_checkpoint_choice"]
    for name in (
        "continuous_domain_canonical_sha256",
        "fixed_anchors_canonical_sha256",
        "discovery_canonical_sha256",
        "heldout_canonical_sha256",
        "sensor_transport_canonical_sha256",
    ):
        assert len(domain[name]) == 64


def test_cpu_smoke_is_required_before_full_training() -> None:
    artifact = load(ARTIFACT)
    smoke = artifact["required_implementation_contract"]
    assert smoke["before_any_optimizer_step"] is True
    assert smoke["smoke_seed"] == 120120
    assert smoke["smoke_environments"] == 16
    assert smoke["smoke_ticks_per_environment"] == 250
    assert smoke["stage_1_optimizer_updates"] == 1
    assert smoke["stage_2_optimizer_updates"] == 1
    assert smoke["formal_support_cells"] == 0
    checks = " ".join(smoke["checks"])
    assert "t-2/t-3/t-4 action histories" in checks
    assert "terminal gyro bonus" in checks
    assert "action/log_std/value leaf" in checks
    assert "auxiliary-target JAX routing" in checks
    assert "1.91229675 N.m / 19.5 kgf.cm" in checks
    assert "training-only value head are absent" in checks
    assert artifact["pass_authorizes_only"].startswith(
        "freeze and run one exact CPU implementation smoke contract"
    )


def test_architecture_is_not_changed_without_transport_evidence() -> None:
    scope = load(ARTIFACT)["attention_or_architecture_scope"]
    assert scope["quadratic_attention_added"] is False
    assert scope["flat_transport_kernel_added"] is False


def test_every_frozen_source_hash_reproduces() -> None:
    artifact = load(ARTIFACT)
    for source in artifact["sources"].values():
        path = ROOT / source["path"]
        assert path.is_file()
        observed = (
            raw_sha256(path) if source["hash_mode"] == "raw sha256" else lf_sha256(path)
        )
        assert observed == source["sha256"]
    markdown = (
        ROOT
        / "outputs/analysis/WINNER_V12_CALIBRATOR_TRAINING_PREREGISTRATION_20260720.md"
    )
    assert lf_sha256(ARTIFACT) in markdown.read_text(encoding="utf-8")
