#!/usr/bin/env python3
"""Freeze the correction to T226's description of T216 training support."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    receipt,
)


T226 = ANALYSIS / "t226_r2_boundary_corner_autopsy_result.json"
T216 = ANALYSIS / "t216_axis_complete_tilt_hosted_preregistration.json"
T217 = ANALYSIS / "t217_t216_recovered_training_validation.json"
T66 = ANALYSIS / "t66_endpoint_core_cpu_result.json"
T70 = ANALYSIS / "t70_t67_condition7_result.json"
T71 = ANALYSIS / "t71_t67_com_hidden_causal_result.json"
OUTPUT = (
    ANALYSIS
    / "t226b_t216_support_correction_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T226B_T216_SUPPORT_CORRECTION_PREREGISTRATION_20260730.md"
)
RUNNER = ROOT / "tools/run_t226b_t216_support_correction.py"
TEST = ROOT / "tests/test_t226b_t216_support_correction.py"
T216_DRIVER = ROOT / "tools/colab_t216_axis_complete_tilt_continuation.py"
T170_DRIVER = (
    ROOT / "tools/colab_t170_eight_stratum_head_continuation.py"
)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T226B preregistration")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T226B preregistration requires clean worktree")

    t226 = load(T226)
    t216 = load(T216)
    t217 = load(T217)
    t66 = load(T66)
    t70 = load(T70)
    t71 = load(T71)
    playground = Path(t216["paths"]["playground"])
    composed_runner = (
        playground / "playground/open_duck_mini_v2/runner.py"
    )
    endpoint_helper = (
        playground / "playground/common/t66_endpoint_core_continuation.py"
    )
    command_sampler = (
        playground / "playground/open_duck_mini_v2/joystick.py"
    )

    checks = {
        "t226_passed_but_contains_support_claim_to_supersede": (
            t226["status"] == "PASS_T226_R2_BOUNDARY_CORNER_AUTOPSY"
            and t226["failed_checks"] == []
            and t226["training_support"]["configuration_distribution"]
            == "continuous_uniform"
            and t226["training_support"]["deterministic_endpoint_atoms"]
            == 0
        ),
        "t216_preregistration_exact": (
            t216["status"]
            == "PREREGISTERED_T216_AXIS_COMPLETE_TILT_HOSTED_CONTINUATION"
            and t216["failed_checks"] == []
            and t216["training"]["body_configuration_strata"] == 8
            and t216["training"]["environments_per_stratum"] == 32
            and t216["training"]["command_support_change"] is False
        ),
        "t217_confirms_t98_and_eight_strata": (
            t217["status"]
            == "HOLD_T217_T216_RECOVERED_TRAINING_VALIDATION"
            and set(t217["failed_checks"])
            == {"step_zero_cost_tree_reproducible_bit_exact"}
            and t217["checks"]["t215b_and_t98_readbacks_exact"]
            and t217["classification"]["body_configuration_strata"] == 8
        ),
        "t66_exact_endpoint_bank_contract_passed": (
            t66["status"] == "PASS_T66_ENDPOINT_CORE_CPU_CONTRACT"
            and t66["failed_checks"] == []
        ),
        "t67_endpoint_only_family_was_closed": (
            t70["status"] == "HOLD_T70_T67_CONDITION7"
            and t70["decision"] == "CLOSE_T67_ENDPOINT_CORE_CONTINUATION"
            and t71["status"]
            == "PASS_T71_COM_SIGNAL_PRESENT_AND_CAUSALLY_USED"
            and t71["classification"]
            == "COM_SIGNAL_PRESENT_AND_USED_CONTROL_LAW_INADEQUATE"
        ),
        "all_exact_sources_present": all(
            path.is_file()
            for path in (
                T216_DRIVER,
                T170_DRIVER,
                composed_runner,
                endpoint_helper,
                command_sampler,
            )
        ),
        "zero_simulator_optimizer_onnx_behavior_hosted_or_robot_now": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T226B preregistration checks failed: {failed}")

    frozen = {
        "builder": receipt(Path(__file__)),
        "runner": receipt(RUNNER),
        "test": receipt(TEST),
        "t226_result": receipt(T226),
        "t216_preregistration": receipt(T216),
        "t217_validation": receipt(T217),
        "t66_result": receipt(T66),
        "t70_result": receipt(T70),
        "t71_result": receipt(T71),
        "t216_driver": receipt(T216_DRIVER),
        "t170_driver": receipt(T170_DRIVER),
        "composed_runner": receipt(composed_runner),
        "endpoint_bank_helper": receipt(endpoint_helper),
        "command_sampler": receipt(command_sampler),
    }
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t226b_t216_support_correction_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T226B_T216_SUPPORT_CORRECTION",
        "question": (
            "Did T216 already cross its continuous command sampler with "
            "T66's exact eight-stratum configuration bank, making the "
            "remaining unsupported boundary mechanism deterministic "
            "command coverage rather than missing COM endpoint coverage?"
        ),
        "frozen_inputs": frozen,
        "facts_to_verify": {
            "training_population": 256,
            "configuration_strata": 8,
            "environments_per_configuration_stratum": 32,
            "configuration_strata_semantics": (
                "one broad randomized stratum plus isolated nominal and "
                "six exact torso-COM endpoints"
            ),
            "exact_torso_com_z_pos_offset_m": [0.0, 0.0, 0.05],
            "command_support_m_s": [0.074, 0.08],
            "command_sampler": "continuous_uniform_without_guaranteed_atoms",
            "corrected_novelty": (
                "one broad command stratum plus exact .074/.077/.080 "
                "command atoms crossed with the existing eight "
                "configuration strata"
            ),
        },
        "decision_rule": {
            "pass_if": [
                "T216's driver chain enables winner_t98_hidden_expert_continuation",
                "the composed runner wraps the base randomizer with T66's endpoint bank",
                "the bank contains the exact torso-COM z=+.05 endpoint",
                "T217 records the exact T98 readback and eight configuration strata",
                "the command sampler remains a continuous uniform over .074-.080 without deterministic command atoms",
                "the older exact-COM-only T67 family remains closed",
            ],
            "pass": (
                "EARN_T227_COMMAND_ATOM_X_EXISTING_COM_BANK_CPU_"
                "CONTRACT_PREREGISTRATION_ONLY"
            ),
            "fail": "RETURN_TO_SUPPORT_AUDIT_WITHOUT_TRAINING",
            "forbidden_successors": [
                "repeat exact-COM-only T66/T67 training",
                "retry a global command clamp or plateau",
                "change reward, cost, actor ABI, or gate thresholds",
                "launch hosted training",
            ],
            "selection_weight": 0,
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "source_files_read": 0,
            "simulator_transitions": 0,
            "optimizer_steps": 0,
            "onnx_inferences": 0,
            "behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_source_correction_audit": True,
            "t227_cpu_contract_preregistration": False,
            "training": False,
            "colab": False,
            "gate5": False,
            "robot_or_rdk": False,
        },
    }
    value = {
        **basis,
        "preregistered_contract_sha256": canonical_sha256(basis),
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T226B T216 support-correction preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Purpose: supersede T226's configuration-support claim without rewriting T226\n"
        "- Candidate novelty: deterministic command atoms crossed with the existing COM bank\n"
        "- Simulator / optimizer / ONNX / behavior / hosted / robot: `0/0/0/0/0/0`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n",
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
