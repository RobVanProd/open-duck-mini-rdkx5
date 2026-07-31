import importlib.util
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "build_winner_v4_response_pretraining_contract.py"
SPEC = importlib.util.spec_from_file_location("response_pretraining_contract", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_support_mode_is_exact_and_requires_no_manual_measurement() -> None:
    contract = MODULE.build_contract()
    support = contract["support_mode"]
    assert support["id"] == "feet_supported_flat_floor_free_body_passive_fall_catch_v1"
    assert support["manual_measurement_required"] is False
    assert support["simulator_realization"]["floating_base"] is True
    assert support["simulator_realization"]["accepted_contact_state"] == [1, 1]
    assert "torso_supported_or_clamped" in support["rejected_modes"]
    assert "free_hanging_or_suspended" in support["rejected_modes"]


def test_cpu_falsification_is_exact_and_pretraining_only() -> None:
    contract = MODULE.build_contract()
    experiment = contract["experiment"]
    assert experiment["training_steps"] == 0
    assert experiment["formal_behavior_cells"] == 0
    assert experiment["torso_x_offsets_m"] == [-0.05, 0.05]
    assert experiment["repeats_per_endpoint_and_fit"] == 2
    assert experiment["excitation"]["tick_count"] == 2814
    assert experiment["profile_extraction"].endswith("profile.v4 builder")


def test_contract_does_not_authorize_training_hardware_or_runtime_changes() -> None:
    authority = MODULE.build_contract()["authority"]
    assert authority["one_cpu_falsification_run"] is True
    assert authority["hosted_cpu_allowed_if_local_cpu_unavailable"] is True
    assert authority["ppo_or_training"] is False
    assert authority["gpu_or_igpu"] is False
    assert authority["policy_architecture_implementation"] is False
    assert authority["runtime_implementation"] is False
    assert authority["rdkx5_or_robot"] is False
    assert authority["torque_or_motion"] is False


def test_both_fits_must_distinguish_signed_endpoints_without_retry() -> None:
    contract = MODULE.build_contract()
    rules = contract["persistence_and_stop_rules"]
    assert rules["pass_requires_both_fits"] is True
    assert rules["retry_allowed"] is False
    assert rules["if_endpoint_collapses"] == "close response73 before PPO"
    assert rules["true_mass_com_inertia_or_component_identity_rescue_forbidden"] is True


def test_generated_contract_matches_builder() -> None:
    path = ROOT / "outputs/analysis/winner_v4_response_pretraining_contract.json"
    assert json.loads(path.read_text(encoding="utf-8")) == MODULE.build_contract()


def test_completed_result_and_support_diagnostic_are_frozen_negative_evidence() -> None:
    formal_path = ROOT / "outputs/analysis/winner_v4_response_identifiability_result.json"
    assert hashlib.sha256(formal_path.read_bytes()).hexdigest() == (
        "b7eb0a5d8ccdfa4034fec85fdd98cd21e6888f7d4bd5b106c6e2052a07966730"
    )
    formal = json.loads(formal_path.read_text(encoding="utf-8"))
    assert formal["decision"] == "DO_NOT_IMPLEMENT_OR_TRAIN_RESPONSE73"
    assert formal["checks"]["both_signed_pairs_noncollapsed"] is True
    assert formal["checks"]["both_feet_contact_every_settle_tick"] is False

    diagnostic_path = ROOT / "outputs/analysis/winner_v4_support_failure_diagnostic.json"
    assert hashlib.sha256(diagnostic_path.read_bytes()).hexdigest() == (
        "acf5af92261fd4f15d69dcc212698d5726a2fb12aa8e17f7f3e1892139882e40"
    )
    diagnostic = json.loads(diagnostic_path.read_text(encoding="utf-8"))
    assert diagnostic["formal_result_sha256"] == hashlib.sha256(
        formal_path.read_bytes()
    ).hexdigest()
    negative, positive = diagnostic["endpoints"]
    assert negative["torso_x_offset_m"] == -0.05
    assert negative["final_base_xyz_m"][2] < 0.0
    assert negative["absolute_roll_distance_to_pi_rad"] < 0.002
    assert positive["torso_x_offset_m"] == 0.05
    assert positive["final_base_xyz_m"][2] > 0.0
    assert diagnostic["authority"]["training"] is False
