#!/usr/bin/env python3
"""Freeze a read-only audit of T169's two diagnostic false negatives."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    receipt,
)


OUTPUT = ANALYSIS / "t169b_cpu_diagnostic_validity_preregistration.json"
T169_PREREG = (
    ANALYSIS
    / "t169_eight_stratum_head_continuation_cpu_preregistration.json"
)
T169_RESULT = (
    ANALYSIS / "t169_eight_stratum_head_continuation_cpu_result.json"
)
T168_RESULT = (
    ANALYSIS / "t168_nominal_adapter_persistence_attribution_result.json"
)


def main() -> int:
    if OUTPUT.exists():
        raise FileExistsError(f"refusing to overwrite T169B: {OUTPUT}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T169B builder requires clean worktree")
    prereg = json.loads(T169_PREREG.read_text(encoding="utf-8"))
    result = json.loads(T169_RESULT.read_text(encoding="utf-8"))
    t168 = json.loads(T168_RESULT.read_text(encoding="utf-8"))
    graphs = {
        step: item["receipt"]
        for step, item in result["training"]["graphs"].items()
    }
    checks = {
        "t169_failed_only_the_two_diagnostic_checks": (
            result["status"]
            == "HOLD_T169_EIGHT_STRATUM_HEAD_CONTINUATION_CPU_CONTRACT"
            and set(result["failed_checks"])
            == {
                "eight_stratum_model_contract_exact",
                "postupdate_random_action_binding",
            }
        ),
        "all_safety_and_scope_checks_already_green": all(
            result["checks"][name]
            for name in (
                "command_exact_original_mechanism_reduced_only_for_cpu",
                "runner_readback_exact",
                "source_cpu_remap_exact",
                "step_zero_tree_exact",
                "update_structure_exact",
                "only_nominal_expert_actor_changed",
                "normalizer_bit_exact",
                "every_critic_leaf_changed",
                "trees_finite",
                "step_zero_raw_onnx_byte_exact",
                "step_zero_trace_exact",
                "step_zero_random_chain_exact",
                "postupdate_trace_action_binding",
                "graph_abi_and_cpu_chain_exact",
                "no_behavior_hosted_or_hardware",
            )
        ),
        "t168_selection_remains_exact": (
            t168["status"]
            == "PASS_T168_NOMINAL_ADAPTER_PERSISTENCE_ATTRIBUTION"
            and t168["stored_trace_replay"]["rows"] == 8152
        ),
        "two_frozen_graphs_available": (
            set(graphs) == {"0", "1024"}
            and all(Path(item["path"]).is_file() for item in graphs.values())
        ),
        "no_optimizer_rerun_or_behavior": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T169B preregistration failed: {failed}")
    value = {
        "schema_version": (
            "open_duck.t169b_cpu_diagnostic_validity_preregistration.v1"
        ),
        "status": "PREREGISTERED_T169B_CPU_DIAGNOSTIC_VALIDITY_AUDIT",
        "question": (
            "Were T169's two failed checks diagnostic false negatives: "
            "JSON/Python-vs-float32 endpoint equality and out-of-distribution "
            "random inputs saturating tanh after a real adapter update?"
        ),
        "frozen_inputs": {
            "builder": receipt(Path(__file__).resolve()),
            "runner": receipt(
                ROOT / "tools/run_t169b_cpu_diagnostic_validity.py"
            ),
            "test": receipt(
                ROOT / "tests/test_t169b_cpu_diagnostic_validity.py"
            ),
            "t169_preregistration": receipt(T169_PREREG),
            "t169_result": receipt(T169_RESULT),
            "t168_result": receipt(T168_RESULT),
            "step0_graph": graphs["0"],
            "step1024_graph": graphs["1024"],
        },
        "audit": {
            "endpoint_equality": (
                "compare actual and preregistered endpoint arrays after "
                "both are represented as float32, the simulator dtype"
            ),
            "random_population": {
                "seed": 1690001,
                "rows": 256,
                "obs": "standard_normal_float32_[1,115]",
                "previous_action": "uniform_-0.5_0.5_float32_[1,14]",
                "h_in": "standard_normal_float32_[1,64]",
            },
            "instrumented_values": [
                "hidden_gate_score",
                "negative_adapter_location",
                "conditional_adapter_location",
                "anchored_location",
                "raw_continuous_actions",
            ],
            "pass_rule": [
                "endpoint arrays are bit-exact after float32 representation",
                "the random population activates the dynamic gate at least once",
                "the updated head, conditional head, and anchored location change",
                "every changed anchored element masked at raw output is exactly tanh-saturated to abs(value)=1",
                "T169 protected in-distribution traces already bind the update to final action on at least 5 percent of rows",
                "no optimizer, simulator, formal behavior, hosted compute, or robot work is rerun",
            ],
        },
        "decision_rule": {
            "pass_decision": (
                "EARN_T170_EIGHT_STRATUM_HEAD_HOSTED_CONTINUATION_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": (
                "CLOSE_EIGHT_STRATUM_NOMINAL_HEAD_CONTINUATION"
            ),
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "stored_onnx_inference_rows": 0,
            "optimizer_steps": 0,
            "simulator_steps": 0,
            "formal_behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "read_only_diagnostic_audit": True,
            "optimizer_rerun": False,
            "hosted_preregistration": False,
            "hosted_training": False,
            "behavior_evaluation": False,
            "policy_promotion": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(
        "preregistered_contract_sha256="
        f"{value['preregistered_contract_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
