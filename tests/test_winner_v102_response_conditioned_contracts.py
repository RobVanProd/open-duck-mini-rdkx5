from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_v101_cpu_contract_proves_protected_update_and_stateful_abi() -> None:
    result = load("winner_v101_response_conditioned_cpu_contract.json")
    assert result["status"] == "PASS_WINNER_V101_RESPONSE_CONDITIONED_CPU_CONTRACT"
    assert result["failed_checks"] == []
    deltas = result["update_family_max_delta"]
    assert deltas["protected"] == 0.0
    assert all(
        deltas[name] > 0.0
        for name in ("adapter_state", "adapter_context", "adapter_action", "critic")
    )
    assert result["trained_onnx_abi"] == {
        "inputs": {
            "calibration_context": [1, 64],
            "h_in": [1, 64],
            "obs": [1, 115],
            "previous_action": [1, 14],
        },
        "outputs": {
            "continuous_actions": [1, 14],
            "h_out": [1, 64],
            "previous_action_out": [1, 14],
        },
    }
    assert result["golden_zero_update"]["ticks"] == 1200
    assert result["golden_zero_update"]["x0_exact_zero"] is True
    assert result["automatic_calibration_reset"]["calibration_ticks"] == 250
    assert result["automatic_calibration_reset"]["phase"] == [1.0, 0.0]
    assert result["authority"]["robot_clearance"] is False


def test_v102_preregistration_replaces_manual_com_and_disables_flat_transport() -> None:
    prereg = load(
        "winner_v102_response_conditioned_hosted_curriculum_preregistration.json"
    )
    assert prereg["status"] == (
        "PREREGISTERED_WINNER_V102_RESPONSE_CONDITIONED_HOSTED_CURRICULUM"
    )
    assert prereg["training"]["flat_transport"] is False
    assert prereg["training"]["automatic_calibration_ticks_per_reset"] == 250
    assert prereg["contract"]["powered_off_manual_com_packet_required"] is False
    assert prereg["contract"]["build_specific_response_is_automatically_inferred"]
    assert prereg["training"]["stages"] == [
        {
            "id": "DOMAIN_25_PERCENT",
            "deviation_scale": 0.25,
            "timesteps": 245_760,
        },
        {
            "id": "DOMAIN_50_PERCENT",
            "deviation_scale": 0.5,
            "timesteps": 245_760,
        },
        {
            "id": "DOMAIN_100_PERCENT",
            "deviation_scale": 1.0,
            "timesteps": 2_007_040,
            "exports": [1_003_520, 2_007_040],
        },
    ]
    assert prereg["authority"]["robot_clearance"] is False
    assert prereg["execution_now"] == {
        "formal_behavior_cells": 0,
        "optimizer_steps": 0,
        "robot_or_rdk_access": 0,
        "simulator_locomotion_steps": 0,
    }


def test_v102_package_and_launch_contracts_do_not_broaden_authority() -> None:
    package = load("winner_v102_response_conditioned_hosted_package_contract.json")
    launch = load("winner_v102_colab_launch_contract.json")
    assert package["status"] == (
        "PASS_WINNER_V102_RESPONSE_CONDITIONED_HOSTED_PACKAGE"
    )
    assert launch["status"] == "PASS_WINNER_V102_COLAB_LAUNCH_CONTRACT"
    assert package["failed_checks"] == []
    assert launch["failed_checks"] == []
    assert package["archive"]["bytes"] == 59_176_688
    assert package["archive"]["sha256"] == (
        "cbb6dd1ef5c68e013cbc8e0a29bdbb014cff476064f2ac763aedfeeba6b28017"
    )
    assert launch["hashes"]["package"] == package["archive"]["sha256"]
    for authority in (package["authority"], launch["authority"]):
        assert authority["robot_clearance"] is False
        assert authority["checkpoint_selection"] is False
        assert authority["deployment"] is False
        assert authority["rdkx5_or_robot"] is False


def test_response_path_does_not_eagerly_import_generic_tensorflow_exporter() -> None:
    patch = (ROOT / "patches/ground_up_response_conditioned_locomotion.patch").read_text(
        encoding="utf-8"
    )
    assert "-from playground.common.export_onnx import export_onnx" in patch
    assert "+            from playground.common.export_onnx import export_onnx" in patch
    assert patch.index(
        '+        elif self.args.policy_architecture == "response_conditioned_reference_residual":'
    ) < patch.index("+            from playground.common.export_onnx import export_onnx")
