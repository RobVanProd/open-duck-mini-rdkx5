from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools" / "run_t22_corrected_one_update_cpu_smoke.py"
T21B_RESULT = (
    ROOT
    / "outputs"
    / "analysis"
    / "t21b_source_initialization_cpu_result.json"
)


def test_t21b_earns_exactly_the_corrected_cpu_smoke() -> None:
    value = json.loads(T21B_RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T21B_SOURCE_INITIALIZATION_CPU_CONTRACT"
    assert value["decision"] == "EARN_T22_CORRECTED_ONE_UPDATE_CPU_SMOKE"
    assert value["failed_checks"] == []
    assert value["execution"] == {
        "hosted_or_colab_compute": 0,
        "optimizer_steps": 0,
        "robot_or_rdk_access": 0,
    }


def test_training_command_uses_exact_v121_source_rates() -> None:
    text = RUNNER.read_text(encoding="utf-8")
    assert "1.4736209064722061" in text
    assert "1.4300791546702385" in text
    assert "1.3976470567286015" in text
    assert "1.2215287424623966" in text
    assert "t20.VELOCITY_LIMITS = SOURCE_VELOCITY_LIMITS" in text


def test_deployment_chain_orders_source_transform_before_context_wrapper() -> None:
    text = RUNNER.read_text(encoding="utf-8")
    start = text.index("def deployment_graph(")
    end = text.index("\n\ndef finalize_t22_result", start)
    function = text[start:end]
    source = function.index("apply_v121_source_deployment(")
    context = function.index("t20.add_context_input(source_deployed, context)")
    physical = function.index(
        "t20.wrap_rate_coherent_support(context, wrapped)"
    )
    assert source < context < physical


def test_step_zero_contract_freezes_all_four_graph_stages() -> None:
    text = RUNNER.read_text(encoding="utf-8")
    base = (
        ROOT / "tools" / "run_t20_support_trainthrough_one_update.py"
    ).read_text(encoding="utf-8")
    assert "step_zero_source_deployed_byte_exact" in text
    assert "frozen_v121_deployed_half_onnx" in text
    assert "step_zero_raw_onnx_byte_exact" in base
    assert "step_zero_context_abi_byte_exact" in base
    assert "step_zero_physical_wrapper_byte_exact" in base


def test_t22_cannot_directly_authorize_hosted_or_hardware_execution() -> None:
    text = RUNNER.read_text(encoding="utf-8")
    assert '"hosted_training_authorized": False' in text
    assert '"policy_deployment_authorized": False' in text
    assert '"gate5_authorized": False' in text
    assert '"robot_or_rdk_access": False' in text
    assert '"torque_or_motion": False' in text
