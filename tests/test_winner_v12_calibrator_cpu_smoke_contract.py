from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "outputs/analysis/winner_v12_calibrator_cpu_smoke_contract.json"
TRAINING = ROOT / "patches/winner_v12_calibrator_training.py"
RUNNER = ROOT / "tools/run_winner_v12_calibrator_cpu_smoke.py"
PREREG = ROOT / "outputs/analysis/winner_v12_calibrator_training_preregistration.json"


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def function_arguments(path: Path, name: str) -> list[str]:
    module = ast.parse(path.read_text(encoding="utf-8"))
    for node in module.body:
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == name
        ):
            return [argument.arg for argument in node.args.args]
    raise AssertionError(f"missing function: {name}")


def load_contract() -> dict:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def test_contract_is_prospective_and_cpu_smoke_only() -> None:
    contract = load_contract()
    assert contract["status"] == "PASS_WINNER_V12_CALIBRATOR_CPU_SMOKE_CONTRACT"
    assert contract["decision"] == "AUTHORIZE_ONE_WINNER_V12_CPU_SMOKE_ONLY"
    assert contract["authority"] == {
        "formal_support_cells": 0,
        "full_calibrator_training": False,
        "hosted_gpu_or_igpu": False,
        "locomotion_training_or_behavior_evaluation": False,
        "optimizer_updates_authorized": {"stage1": 1, "stage2": 1},
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "robot_clearance": False,
    }


def test_smoke_population_is_exact_balanced_and_has_no_heldout() -> None:
    population = load_contract()["smoke_population"]
    assert population["environment_count"] == 16
    assert population["ticks_per_environment"] == 250
    assert population["configuration_ids"] == [
        "MASS_LOW",
        "MASS_HIGH",
        "COM_X_NEG",
        "COM_X_POS",
        "COM_Y_NEG",
        "COM_Y_POS",
        "COM_Z_NEG",
        "COM_Z_POS",
        "INERTIA_X_LOW",
        "INERTIA_X_HIGH",
        "INERTIA_Y_LOW",
        "INERTIA_Y_HIGH",
        "INERTIA_Z_LOW",
        "INERTIA_Z_HIGH",
        "COM_CORNER_00",
        "COM_CORNER_01",
    ]
    assert population["plant_assignments"].count("P30_ALL_JOINT") == 8
    assert population["plant_assignments"].count("P31_34_PITCH_WITH_P30_NONPITCH") == 8
    assert not any(
        value.startswith("HELDOUT") for value in population["configuration_ids"]
    )


def test_training_and_ppo_constants_are_frozen() -> None:
    hyperparameters = load_contract()["hyperparameters"]
    assert hyperparameters["stage1"] == {
        "adam_beta1": 0.9,
        "adam_beta2": 0.999,
        "adam_epsilon": 1e-8,
        "bptt_ticks": 250,
        "learning_rate": 1e-4,
        "optimizer_updates": 1,
        "ternary_probabilities": {"-1": 1 / 3, "0": 1 / 3, "1": 1 / 3},
        "weight_decay": 0.0,
    }
    assert hyperparameters["stage2"] == {
        "adam_beta1": 0.9,
        "adam_beta2": 0.999,
        "adam_epsilon": 1e-8,
        "advantage_normalization": "all valid smoke transitions; float64 population mean/std; std floor 1e-6; cast float32",
        "clip_epsilon": 0.2,
        "entropy_coefficient": 0.001,
        "gae_lambda": 0.95,
        "gamma": 1.0,
        "learning_rate": 1e-4,
        "log_std_clamp": [-5.0, 1.0],
        "minibatches": 1,
        "optimizer_updates": 1,
        "ppo_epochs": 1,
        "timeout_bootstrap": 0.0,
        "value_coefficient": 0.5,
        "weight_decay": 0.0,
    }


def test_network_training_functions_have_no_privileged_arguments() -> None:
    forbidden = {
        "configuration",
        "mass",
        "com",
        "inertia",
        "plant",
        "fit",
        "body",
        "randomizer",
    }
    for name in (
        "response_step",
        "stage1_predictions",
        "stage1_loss",
        "stage2_mean_value",
        "sample_stage2_action",
        "stage2_ppo_loss",
    ):
        arguments = set(function_arguments(TRAINING, name))
        assert not arguments & forbidden, (name, arguments & forbidden)


def test_deployable_mapping_and_stage_isolation_are_literal() -> None:
    source = TRAINING.read_text(encoding="utf-8")
    assert 'DEPLOYABLE_ACTION_KEYS = ("action_weight", "action_bias")' in source
    assert '"training_only_log_std"' in source
    assert '"training_only_value_weight"' in source
    assert '"training_only_value_bias"' in source
    assert (
        "DEPLOYABLE_CALIBRATOR_KEYS = ENCODER_AUXILIARY_KEYS + DEPLOYABLE_ACTION_KEYS"
        in source
    )
    assert "return _select(parameters, DEPLOYABLE_CALIBRATOR_KEYS)" in source
    assert 'updated["training_only_log_std"] = jnp.clip' in source


def test_runner_uses_fixed_p30_observer_and_selected_hidden_plant_separately() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "self.bridge = ActuatorBridgeModel(" in source
    assert "self.observer = observer_type(canonical_fit, HOME_RAD)" in source
    assert "observed_target = self.observer.step(sent_target, CONTROL_DT_S)" in source
    assert "applied_target = self.bridge.step(sent_target, CONTROL_DT_S)" in source
    assert (
        "next_observation[83:97], episode.observer.value.astype(np.float32)" in source
    )
    assert (
        "P31/34"
        not in source[
            source.index("def load_runtime_observer") : source.index(
                "def plant_parameters"
            )
        ]
    )


def test_runner_has_exact_transition_timing_and_no_retry_surface() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "self.history = [action.copy(), *self.history[:3]]" in source
    assert "self.history[1]" in source
    assert "self.history[2]" in source
    assert "self.history[3]" in source
    assert "np.asarray([1.0, 0.0]" in source
    assert "np.zeros(14" in source
    assert '"retry_count": 0' in source
    assert "while True" not in source
    assert "subprocess.run(" in source  # read-only git attribution only
    assert '["git", *arguments]' in source


def test_terminal_action_is_retained_and_support_boundaries_are_canaried() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "sample_mask[environment, tick] = 1.0" in source
    assert "done[environment, tick] = 1.0" in source
    assert "valid_transition_mask[environment, tick] = 1.0" in source
    assert "nonterminal = np.float32(1.0 - done[environment, tick])" in source
    assert '"stage2_terminal_actions_retained_with_done"' in source
    assert "def support_boundary_canary()" in source
    assert "np.nextafter(MINIMUM_BASE_Z_M, -math.inf)" in source
    assert "np.nextafter(TORQUE_LIMIT_NM, math.inf)" in source
    assert "np.nextafter(CURRENT_LIMIT_A, math.inf)" in source
    support = load_contract()["support_logic"]
    assert support["invalid_transition_action_in_ppo_batch"] is True
    assert support["invalid_next_state_in_auxiliary_batch"] is False


def test_runner_fails_closed_on_assets_versions_and_contract_line_endings() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    importer = (ROOT / "tools/import_winner_v12_calibrator_cpu_smoke.py").read_text(
        encoding="utf-8"
    )
    assert "def validate_playground_tree(" in source
    assert "PLAYGROUND_RECEIPT_LF_SHA256" in source
    assert "Playground composition receipt identity mismatch" in source
    assert 'git_output(root, "status", "--porcelain=v1")' in source
    assert "observed_paths != expected_paths" in source
    assert "def validate_software_versions(" in source
    assert '"software_versions_exact": software_versions["exact"]' in source
    assert '"canonical_lf_sha256": lf_sha256(args.contract)' in source
    assert '"canonical_lf_sha256"' in importer
    assert "lf_sha256(CONTRACT)" in importer
    assert load_contract()["software_versions"] == {
        "python": "3.12.13",
        "jax": "0.7.2",
        "jaxlib": "0.7.2",
        "mujoco": "3.9.0",
        "onnx": "1.22.0",
        "onnxruntime": "1.27.0",
        "numpy": "2.0.2",
    }
    workflow = (
        ROOT / ".github/workflows/winner-v12-calibrator-cpu-smoke.yml"
    ).read_text(encoding="utf-8")
    assert "push:" in workflow
    assert "workflow_dispatch:" not in workflow
    assert "codex/winner-v4-response-contract" in workflow
    assert 'python-version: "3.12.13"' in workflow
    assert "fetch-depth: 0" in workflow
    assert "matrix:" not in workflow


def test_nonfinite_simulator_and_onnx_values_fail_closed() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    importer = (ROOT / "tools/import_winner_v12_calibrator_cpu_smoke.py").read_text(
        encoding="utf-8"
    )
    assert "nonfinite MuJoCo transition state" in source
    assert "nonfinite bridge or observer target" in source
    assert "nonfinite JAX or ONNX chain output" in source
    assert '"onnx_chain_outputs_finite": graph["all_chain_outputs_finite"]' in source
    assert "allow_nan=False" in source
    assert '"onnx_chain_outputs_finite"' in importer


def test_protected_policies_are_never_opened_by_onnxruntime() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "InferenceSession(str(graph)" in source
    assert "InferenceSession(str(args.policy_half)" not in source
    assert "InferenceSession(str(args.policy_final)" not in source
    assert '"protected_policy_inference_calls": 0' in source


def test_contract_hashes_every_execution_source() -> None:
    contract = load_contract()
    for item in contract["sources"].values():
        path = ROOT / item["path"]
        observed = (
            lf_sha256(path)
            if item["hash_mode"] == "lf"
            else hashlib.sha256(path.read_bytes()).hexdigest()
        )
        assert observed == item["sha256"], item["path"]
    assert contract["sources"]["calibrator_preregistration"]["sha256"] == lf_sha256(
        PREREG
    )


def test_pass_does_not_authorize_full_training_or_robot() -> None:
    contract = load_contract()
    assert contract["pass_authorizes_only"] == (
        "one no-retry CPU smoke producing an auditable result; a pass permits only "
        "a separate prospective full-calibrator training preregistration"
    )
    assert contract["post_smoke_stop"] is True
