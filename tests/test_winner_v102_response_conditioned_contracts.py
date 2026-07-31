from __future__ import annotations

import hashlib
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


def test_v104_attributes_v102_hold_before_training_and_v105_closes_imports() -> None:
    hold = load("winner_v102_hosted_hold_result_20260723.json")
    receipt = load("winner_v102_hosted_hold_launch_receipt_20260723.json")
    attribution = load("winner_v104_hosted_package_failure_attribution.json")
    prereg = load("winner_v105_hosted_packaging_correction_preregistration.json")
    package = load("winner_v105_response_conditioned_hosted_package_contract.json")
    launch = load("winner_v105_colab_cli_launch_contract.json")

    assert hold["status"] == (
        "HOLD_WINNER_V102_RESPONSE_CONDITIONED_HOSTED_CURRICULUM"
    )
    assert hold["stages"] == []
    assert hold["formal_behavior_cells_executed"] == 0
    assert hold["error"] == (
        "ModuleNotFoundError: No module named "
        "'winner_v6_dynamic_calibration_networks'"
    )
    assert receipt["status"] == "HOLD_WINNER_V102_COLAB_LAUNCH"
    assert receipt["returncode"] == 1
    assert receipt["output_archive_exists"] is False

    assert attribution["status"] == (
        "HOLD_WINNER_V104_V102_PACKAGE_IMPORT_CLOSURE"
    )
    assert attribution["failed_run"]["stages_started"] == 0
    assert attribution["failed_run"]["optimizer_steps"] == 0
    assert attribution["failed_run"]["simulator_locomotion_steps"] == 0
    assert attribution["causal_attribution"][
        "required_member_present_in_failed_package"
    ] is False
    assert attribution["authority"]["hosted_retry_authorized_now"] is False

    assert prereg["status"] == (
        "PREREGISTERED_WINNER_V105_HOSTED_PACKAGING_CORRECTION"
    )
    correction = prereg["correction"]
    assert correction["add_exact_archive_member"].endswith(
        "/winner_v6_dynamic_calibration_networks.py"
    )
    assert correction["reuse_exact_v102_training_driver"] is True
    assert correction["reuse_exact_v102_training_preregistration"] is True
    for field in (
        "policy_equations_changed",
        "calibrator_equations_changed",
        "training_hyperparameters_changed",
        "stage_schedule_changed",
        "export_steps_changed",
        "seeds_or_thresholds_changed",
        "reward_or_selection_changed",
    ):
        assert correction[field] is False

    assert package["status"] == (
        "PASS_WINNER_V105_RESPONSE_CONDITIONED_HOSTED_PACKAGE"
    )
    assert package["failed_checks"] == []
    assert package["checks"]["v6_dependency_present_and_exact"] is True
    assert package["checks"]["static_import_closure_passed"] is True
    assert package["checks"]["isolated_import_preflight_passed"] is True
    assert package["archive"] == {
        "path": (
            "D:\\CodexArtifacts\\open-duck-mini-rdkx5\\"
            "winner-v105-response-conditioned-hosted-20260723.tar.gz"
        ),
        "bytes": 59_201_279,
        "sha256": (
            "30db9b47433543eeeff6e4db6548cd6479916a803891d3aafacd1b63f105be70"
        ),
    }

    assert launch["status"] == "PASS_WINNER_V105_COLAB_CLI_LAUNCH_CONTRACT"
    assert launch["failed_checks"] == []
    assert launch["session"] == {
        "accelerator": "L4",
        "count": 1,
        "max_wall_seconds": 21600,
        "name": "winner-v105-response-20260723",
    }
    assert launch["recovery"]["retry"] is False
    assert launch["recovery"]["resume"] is False
    for name in ("launcher", "executor"):
        assert hashlib.sha256((ROOT / "tools" / {
            "launcher": "launch_winner_v105_response_conditioned_colab.py",
            "executor": "execute_winner_v105_colab_cli.py",
        }[name]).read_bytes()).hexdigest() == launch["hashes"][name]


def test_response_path_does_not_eagerly_import_generic_tensorflow_exporter() -> None:
    patch = (ROOT / "patches/ground_up_response_conditioned_locomotion.patch").read_text(
        encoding="utf-8"
    )
    assert "-from playground.common.export_onnx import export_onnx" in patch
    assert "+            from playground.common.export_onnx import export_onnx" in patch
    assert patch.index(
        '+        elif self.args.policy_architecture == "response_conditioned_reference_residual":'
    ) < patch.index("+            from playground.common.export_onnx import export_onnx")


def test_v103_freezes_full_matrix_and_selection_before_training_outcome() -> None:
    prereg = load("winner_v103_response_conditioned_behavior_preregistration.json")
    assert prereg["status"] == (
        "PREREGISTERED_WINNER_V103_RESPONSE_CONDITIONED_CPU_BEHAVIOR_"
        "AND_SELECTION_GATE"
    )
    matrix = prereg["formal_matrix"]
    assert matrix["cells_total"] == 1024
    assert matrix["cells_per_checkpoint"] == 512
    assert matrix["conditions"] == 64
    assert matrix["checkpoints_full_domain_relative_steps"] == [
        1_003_520,
        2_007_040,
    ]
    assert matrix["commands_x_m_s"] == [0.0, 0.074, 0.077, 0.08]
    assert matrix["actuator_plants"] == [
        "P30_ALL_JOINT",
        "P31_34_PITCH_WITH_P30_NONPITCH",
    ]
    assert sum(matrix["group_cell_counts"].values()) == 1024

    calibration = prereg["automatic_calibration_per_cell"]
    assert calibration["calibration_ticks"] == 250
    assert calibration["home_return_ticks"] == 250
    assert calibration["ticks_count_toward_scored_duration"] is False
    assert calibration["locomotion_phase_reset"] == [1.0, 0.0]
    assert calibration["locomotion_hidden_reset"] == [0.0] * 64
    assert calibration["locomotion_previous_action_reset"] == [0.0] * 14

    selection = prereg["selection_rule"]
    assert selection["both_checkpoints_must_pass_all_512_cells"] is True
    assert selection["no_closest_checkpoint_or_metric_ranking"] is True
    assert selection["no_selection_if_either_checkpoint_holds"] is True
    assert selection["selected_checkpoint_if_both_pass"] == {
        "label": "final",
        "full_domain_relative_step": 2_007_040,
    }
    assert prereg["execution_now"] == {
        "training_artifacts_observed": 0,
        "formal_behavior_cells": 0,
        "checkpoint_selected": False,
        "robot_clearance": False,
        "robot_or_rdk_access": 0,
    }
    assert all(value is False for value in prereg["authority_now"].values())
    assert (
        prereg["manual_measurement_disposition"][
            "powered_off_46_field_com_packet_required"
        ]
        is False
    )
    builder = ROOT / prereg["frozen_sources"]["builder"]["path"]
    assert hashlib.sha256(builder.read_bytes()).hexdigest() == (
        prereg["frozen_sources"]["builder"]["sha256"]
    )


def test_v103_zero_cell_runner_contract_passes_exact_two_stage_smoke() -> None:
    contract = load(
        "winner_v103_response_conditioned_behavior_runner_contract.json"
    )
    assert contract["status"] == (
        "PASS_WINNER_V103_RESPONSE_CONDITIONED_BEHAVIOR_RUNNER_CONTRACT"
    )
    assert contract["failed_checks"] == []
    assert contract["formal_behavior_cells_executed"] == 0
    assert contract["matrix_cells"] == 1024
    assert contract["matrix_plan_sha256"] == (
        "10b5d3e407636d276275f3f39145233c3cd63688c3229235411ed2734651e073"
    )
    formal_runner = ROOT / "tools/run_winner_v103_response_conditioned_behavior.py"
    assert hashlib.sha256(formal_runner.read_bytes()).hexdigest() == (
        contract["formal_runner_sha256"]
    )
    formal_plan = contract["formal_runner_zero_cell_plan"]
    assert formal_plan["pass"] is True
    assert formal_plan["failed_checks"] == []
    assert formal_plan["formal_behavior_cells_executed"] == 0
    assert formal_plan["matrix_cells"] == 1024
    assert formal_plan["selection_rule"] == {
        "both_checkpoints_must_pass_all_512": True,
        "selected_step_if_both_pass": 2_007_040,
        "no_closest_or_reward_selection": True,
    }
    smoke = contract["nonformal_full_stack_smoke"]
    assert smoke["pass"] is True
    assert smoke["scored_ticks"] == 1
    assert smoke["unscored_calibration_ticks"] == 250
    assert smoke["unscored_home_return_ticks"] == 250
    response = smoke["response_calibration"]
    assert response["context_shape"] == [1, 64]
    assert response["context_finite"] is True
    assert response["locomotion_phase_reset"] == [1.0, 0.0]
    assert response["locomotion_hidden_exact_zero"] is True
    assert response["locomotion_previous_action_exact_zero"] is True
    assert smoke["response_trace"] == {
        "graph_authoritative_every_tick": True,
        "host_action_delta_exact_zero": True,
        "one_immutable_context_hash": True,
        "rows": 1,
    }
    assert contract["authority"]["formal_execution_now"] is False
    assert contract["authority"]["robot_clearance"] is False
    assert contract["authority"]["rdkx5_or_robot"] is False
    builder = ROOT / contract["builder_path"]
    assert hashlib.sha256(builder.read_bytes()).hexdigest() == (
        contract["builder_sha256"]
    )
    for name, expected in contract["supporting_tool_hashes"].items():
        assert hashlib.sha256((ROOT / "tools" / name).read_bytes()).hexdigest() == (
            expected
        )
