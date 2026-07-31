from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
ASSETS = Path(
    r"D:\CodexArtifacts\open-duck-policy"
    r"\t10_response_conditioned_assets_v1"
)
PLAYGROUND = Path(
    r"D:\CodexProjects\Open_Duck_Playground-t10-response-conditioned-v2"
)


def canonical_sha256(value) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def test_t10_zero_update_assets_are_canonical_and_exact() -> None:
    value = json.loads(
        (ASSETS / "manifest.json").read_text(encoding="utf-8")
    )
    basis = {
        key: item
        for key, item in value.items()
        if key != "manifest_sha256"
    }
    assert canonical_sha256(basis) == value["manifest_sha256"]
    assert value["status"] == "PASS_T10_RESPONSE_CONDITIONED_ASSETS"
    assert value["failed_checks"] == []
    assert value["expansion"]["added_actor_parameter_families"] == [
        "context_hidden_projection",
        "context_location",
    ]
    assert value["expansion"]["added_normalizer_keys"] == [
        "calibration_context",
        "policy_previous_action",
    ]
    assert value["step_zero_parity"]["ticks"] == 1024
    assert value["step_zero_parity"]["all_outputs_bit_exact"] is True
    assert (
        value["step_zero_parity"][
            "arbitrary_context_has_zero_step_effect"
        ]
        is True
    )
    assert value["execution"] == {
        "optimizer_steps": 0,
        "simulator_behavior_cells": 0,
        "robot_or_rdk_access": 0,
    }


def test_t10_composed_source_is_default_off_and_canonical() -> None:
    value = json.loads(
        (PLAYGROUND / "T10_COMPOSED_SOURCE_MANIFEST.json").read_text(
            encoding="utf-8"
        )
    )
    basis = {
        key: item
        for key, item in value.items()
        if key != "manifest_sha256"
    }
    assert canonical_sha256(basis) == value["manifest_sha256"]
    assert value["composition"]["patch_count"] == 7
    assert value["execution"] == {
        "optimizer_steps": 0,
        "simulator_behavior_cells": 0,
        "robot_or_rdk_access": 0,
    }
    robot_runner = (
        PLAYGROUND / "playground" / "open_duck_mini_v2" / "runner.py"
    ).read_text(encoding="utf-8")
    common_runner = (
        PLAYGROUND / "playground" / "common" / "runner.py"
    ).read_text(encoding="utf-8")
    assert '"response_conditioned_v121"' in robot_runner
    assert (
        'self.args.policy_architecture == "response_conditioned_v121"'
        in common_runner
    )


def test_t10_preregistration_is_canonical_and_spends_no_hosted_compute() -> None:
    value = json.loads(
        (
            ANALYSIS
            / "t10_response_conditioned_continuation_cpu_preregistration.json"
        ).read_text(encoding="utf-8")
    )
    basis = {
        key: value[key]
        for key in (
            "schema_version",
            "status",
            "question",
            "causal_basis",
            "sources",
            "assets",
            "software_contract",
            "cpu_smoke",
            "decision_rule",
            "authority",
            "execution_now",
            "preexecution_amendment",
        )
    }
    assert canonical_sha256(basis) == value[
        "preregistered_contract_sha256"
    ]
    assert value["status"] == (
        "PREREGISTERED_T10_RESPONSE_CONDITIONED_CPU_CONTRACT"
    )
    assert value["cpu_smoke"]["optimizer_steps_exact"] == 1024
    assert value["cpu_smoke"]["export_steps"] == [0, 1024]
    assert value["authority"]["hosted_or_colab_compute"] is False
    assert value["authority"]["formal_behavior_cells"] == 0
    assert value["authority"]["robot_or_rdkx5_access"] is False
    assert value["execution_now"] == {
        "optimizer_steps": 0,
        "formal_behavior_cells": 0,
        "hosted_or_colab_compute": 0,
        "robot_or_rdk_access": 0,
    }
    amendment = value["preexecution_amendment"]
    assert amendment["failure_class"] == "RESET_PREFLIGHT_RELATIVE_PATH"
    assert amendment["formal_optimizer_steps_observed"] == 0
    assert amendment["unchanged_decision_rule"] is True
    assert amendment["unchanged_optimizer_steps_exact"] == 1024


def test_t10_independent_auditor_does_not_import_runner() -> None:
    source = (
        ROOT / "tools" / "audit_t10_response_conditioned_cpu_contract.py"
    ).read_text(encoding="utf-8")
    assert "run_" + "t10_response_conditioned_cpu_contract" not in source


def test_t10_result_is_canonical_and_holds_hosted_training() -> None:
    value = json.loads(
        (
            ANALYSIS
            / "t10_response_conditioned_continuation_cpu_result.json"
        ).read_text(encoding="utf-8")
    )
    basis = {
        key: item for key, item in value.items() if key != "result_sha256"
    }
    assert canonical_sha256(basis) == value["result_sha256"]
    assert value["status"] == "HOLD_T10_RESPONSE_CONDITIONED_CPU_CONTRACT"
    assert value["decision"] == (
        "HOLD_RESPONSE_CONDITIONED_HOSTED_CONTINUATION"
    )
    assert value["failed_checks"] == [
        "trained_graph_uses_context_action"
    ]
    assert value["checks"]["both_context_families_updated"] is True
    assert value["checks"]["trained_graph_uses_context_state"] is True
    assert value["execution"] == {
        "optimizer_steps": 1024,
        "formal_behavior_cells": 0,
        "hosted_or_colab_compute": 0,
        "robot_or_rdk_access": 0,
    }


def test_t10_independent_audit_reproduces_the_single_hold() -> None:
    value = json.loads(
        (
            ANALYSIS
            / "t10_response_conditioned_continuation_cpu_independent_audit.json"
        ).read_text(encoding="utf-8")
    )
    basis = {
        key: item for key, item in value.items() if key != "audit_sha256"
    }
    assert canonical_sha256(basis) == value["audit_sha256"]
    assert value["status"] == (
        "HOLD_T10_RESPONSE_CONDITIONED_CPU_INDEPENDENT_AUDIT"
    )
    assert value["decision"] == (
        "HOLD_RESPONSE_CONDITIONED_HOSTED_CONTINUATION"
    )
    assert value["issues"] == ["trained_context_action_effect"]
    assert value["execution"] == {
        "optimizer_steps": 0,
        "formal_behavior_cells": 0,
        "hosted_or_colab_compute": 0,
        "robot_or_rdk_access": 0,
    }
