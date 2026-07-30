#!/usr/bin/env python3
"""Execute T226B's source-only correction of T216 support semantics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
sys.path.insert(0, str(ROOT / "tools"))
from run_t136_static_calibration_router_transform import (  # noqa: E402
    canonical_sha256,
    verify,
)


PREREG = (
    ANALYSIS / "t226b_t216_support_correction_preregistration.json"
)
RESULT = ANALYSIS / "t226b_t216_support_correction_result.json"
MARKDOWN = (
    ANALYSIS / "T226B_T216_SUPPORT_CORRECTION_RESULT_20260730.md"
)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T226B result")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T226B execution requires clean worktree")

    prereg = load(PREREG)
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T226B_T216_SUPPORT_CORRECTION"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T226B preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, f"frozen_inputs.{name}")

    frozen = prereg["frozen_inputs"]
    t226 = load(Path(frozen["t226_result"]["path"]))
    t216 = load(Path(frozen["t216_preregistration"]["path"]))
    t217 = load(Path(frozen["t217_validation"]["path"]))
    t66 = load(Path(frozen["t66_result"]["path"]))
    t70 = load(Path(frozen["t70_result"]["path"]))
    t71 = load(Path(frozen["t71_result"]["path"]))
    t216_driver = Path(frozen["t216_driver"]["path"]).read_text(
        encoding="utf-8"
    )
    t170_driver = Path(frozen["t170_driver"]["path"]).read_text(
        encoding="utf-8"
    )
    runner = Path(frozen["composed_runner"]["path"]).read_text(
        encoding="utf-8"
    )
    endpoint = Path(frozen["endpoint_bank_helper"]["path"]).read_text(
        encoding="utf-8"
    )
    command = Path(frozen["command_sampler"]["path"]).read_text(
        encoding="utf-8"
    )

    checks = {
        "t226_claim_is_explicitly_superseded_not_rewritten": (
            t226["status"] == "PASS_T226_R2_BOUNDARY_CORNER_AUTOPSY"
            and t226["training_support"]["configuration_distribution"]
            == "continuous_uniform"
            and t226["training_support"]["deterministic_endpoint_atoms"]
            == 0
        ),
        "t216_driver_inherits_t170_chain": (
            "import colab_t170_eight_stratum_head_continuation as base"
            in t216_driver
            and "_BASE_RUNNER_COMMAND = base.runner_command"
            in t216_driver
            and 'command.index("--winner_t98_hidden_expert_continuation")'
            in t216_driver
        ),
        "t170_replaces_predecessor_with_t98": (
            'old = "--winner_t77_endpoint_joint_adapter_continuation"'
            in t170_driver
            and (
                'command[command.index(old)] = '
                '"--winner_t98_hidden_expert_continuation"'
            )
            in t170_driver
        ),
        "composed_runner_wraps_t98_with_endpoint_bank": (
            "args.winner_t98_hidden_expert_continuation" in runner
            and "make_endpoint_bank_randomizer" in runner
            and "self.randomizer = make_endpoint_bank_randomizer(" in runner
            and "T98_HIDDEN_EXPERT_CONTINUATION=" in runner
            and "strata=8,broad=1,isolated=7" in runner
        ),
        "endpoint_bank_has_exact_upper_z_and_eight_categories": (
            "[0.0, 0.0, 0.05]" in endpoint
            and '"torso_com_z_pos"' in endpoint
            and "jnp.arange(population, dtype=jnp.int32)" in endpoint
            and "% len(ENDPOINT_NAMES)" in endpoint
            and "population % len(ENDPOINT_NAMES) != 0" in endpoint
        ),
        "t216_population_assigns_32_envs_per_stratum": (
            t216["training"]["body_configuration_strata"] == 8
            and t216["training"]["environments_per_stratum"] == 32
            and prereg["facts_to_verify"]["training_population"] == 256
        ),
        "t217_confirms_hosted_t98_readback": (
            t217["failed_checks"] == []
            and t217["checks"]["t215b_and_t98_readbacks_exact"]
            and t217["classification"]["body_configuration_strata"] == 8
        ),
        "command_support_remains_continuous_without_atoms": (
            "def sample_command(" in command
            and "ground_up_command_support_range[0]" in command
            and "ground_up_command_support_range[1]" in command
            and "jax.random.uniform(" in command
            and "command_atom" not in command
            and "endpoint_command" not in command
            and t216["training"]["command_support_change"] is False
        ),
        "older_exact_com_only_family_closed": (
            t66["status"] == "PASS_T66_ENDPOINT_CORE_CPU_CONTRACT"
            and t70["decision"] == "CLOSE_T67_ENDPOINT_CORE_CONTINUATION"
            and t71["classification"]
            == "COM_SIGNAL_PRESENT_AND_USED_CONTROL_LAW_INADEQUATE"
        ),
        "zero_simulator_optimizer_onnx_behavior_hosted_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed_checks = sorted(
        name for name, passed in checks.items() if not passed
    )
    passed = not failed_checks
    basis_result: dict[str, Any] = {
        "schema_version": (
            "open_duck.t226b_t216_support_correction_result.v1"
        ),
        "status": (
            "PASS_T226B_T216_SUPPORT_CORRECTION"
            if passed
            else "HOLD_T226B_T216_SUPPORT_CORRECTION"
        ),
        "decision": (
            "EARN_T227_COMMAND_ATOM_X_EXISTING_COM_BANK_CPU_"
            "CONTRACT_PREREGISTRATION_ONLY"
            if passed
            else "RETURN_TO_SUPPORT_AUDIT_WITHOUT_TRAINING"
        ),
        "classification": (
            "LOW_COMMAND_BOUNDARY_NOT_DETERMINISTICALLY_COVERED_"
            "WITH_EXACT_UPPER_Z_STRATUM_AND_LATE_ABI_FEASIBILITY"
            if passed
            else "T216_TRAINING_SUPPORT_UNRESOLVED"
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed_checks,
        "supersedes": {
            "artifact": "t226_r2_boundary_corner_autopsy_result.json",
            "preserved_findings": [
                "the only tick-zero x=.074/x=.077 observation difference is obs[6]",
                "both half-checkpoint x=.074 upper-Z failures are dynamic",
                "the final checkpoint proves late actor-ABI feasibility",
                "the global command plateau remains closed",
            ],
            "corrected_claims": {
                "configuration_distribution": {
                    "t226": "continuous_uniform",
                    "correct": (
                        "eight-stratum endpoint bank: one broad randomized "
                        "plus seven deterministic isolated configurations"
                    ),
                },
                "deterministic_configuration_atoms": {
                    "t226": 0,
                    "correct": 7,
                },
                "upper_z_exact_training_environments": {
                    "t226": 0,
                    "correct": 32,
                },
            },
        },
        "training_support": {
            "configuration_distribution": (
                "one broad randomized stratum plus seven deterministic "
                "isolated strata"
            ),
            "configuration_strata": 8,
            "environments_per_configuration_stratum": 32,
            "exact_upper_z_stratum": True,
            "command_distribution": "continuous_uniform",
            "deterministic_command_atoms": 0,
            "lower_command_endpoint_guaranteed_per_batch": False,
            "selected_successor": (
                "cross one broad continuous command stratum and exact "
                ".074/.077/.080 command atoms with T216's existing eight "
                "configuration strata"
                if passed
                else None
            ),
            "policy_abi_change": False,
            "reward_or_cost_change": False,
            "global_command_transform_retry": False,
        },
        "novelty_boundary": {
            "closed": [
                "exact-COM-only endpoint continuation",
                "global command clamp or plateau",
            ],
            "open": (
                "deterministic command coverage crossed with the already "
                "active exact configuration bank"
            ),
        },
        "execution": {
            "source_files_read": 5,
            "simulator_transitions": 0,
            "optimizer_steps": 0,
            "onnx_inferences": 0,
            "behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "t227_cpu_contract_preregistration": passed,
            "training": False,
            "colab": False,
            "gate5": False,
            "robot_or_rdk": False,
        },
    }
    value = {
        **basis_result,
        "result_sha256": canonical_sha256(basis_result),
    }
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T226B T216 support-correction result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Classification: `{value['classification']}`\n"
        "- Correction: T216 already had an exact z=+.05 COM stratum (32 environments)\n"
        "- Remaining gap: no guaranteed .074/.077/.080 command atoms\n"
        "- Successor: command atoms crossed with the existing COM bank; no reward/ABI change\n"
        "- Simulator / optimizer / ONNX / behavior / hosted / robot: `0/0/0/0/0/0`\n"
        f"- Result SHA-256: `{value['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"failed_checks={failed_checks}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
