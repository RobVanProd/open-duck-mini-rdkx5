#!/usr/bin/env python3
"""Freeze the zero-update CPU contract for the Winner-v12 full trainer."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import re
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs/analysis/winner_v12_full_calibrator_training_cpu_contract.json"
MARKDOWN = (
    ROOT
    / "outputs/analysis/WINNER_V12_FULL_CALIBRATOR_TRAINING_CPU_CONTRACT_20260721.md"
)
PREREGISTRATION = (
    ROOT / "outputs/analysis/winner_v12_full_calibrator_training_preregistration.json"
)
RUNNER = ROOT / "tools/run_winner_v12_full_calibrator_training.py"

SOURCE_PATHS = {
    "workflow": (
        ".github/workflows/winner-v12-full-calibrator-training-cpu-contract.yml",
        "lf",
    ),
    "dispatch_attribution": (
        "outputs/analysis/winner_v12_full_calibrator_training_cpu_contract_dispatch_attribution.json",
        "lf",
    ),
    "dispatch_attribution_markdown": (
        "outputs/analysis/WINNER_V12_FULL_CALIBRATOR_TRAINING_CPU_CONTRACT_DISPATCH_ATTRIBUTION_20260721.md",
        "lf",
    ),
    "serialization_failure_attribution": (
        "outputs/analysis/winner_v12_full_calibrator_training_cpu_contract_serialization_failure_attribution.json",
        "lf",
    ),
    "serialization_failure_attribution_markdown": (
        "outputs/analysis/WINNER_V12_FULL_CALIBRATOR_TRAINING_CPU_CONTRACT_SERIALIZATION_FAILURE_ATTRIBUTION_20260721.md",
        "lf",
    ),
    "training_preupdate_failure_attribution": (
        "outputs/analysis/winner_v12_full_calibrator_training_preupdate_failure_attribution.json",
        "lf",
    ),
    "training_preupdate_failure_attribution_markdown": (
        "outputs/analysis/WINNER_V12_FULL_CALIBRATOR_TRAINING_PREUPDATE_FAILURE_ATTRIBUTION_20260721.md",
        "lf",
    ),
    "playground_composer": ("tools/compose_winner_v7_playground.py", "lf"),
    "winner_v7_transform": ("tools/run_winner_v7_inward_projection_contract.py", "lf"),
    "winner_v7_importer": (
        "tools/import_winner_v7_inward_projection_contract.py",
        "lf",
    ),
    "winner_v7_preregistration": (
        "outputs/analysis/winner_v7_inward_projection_preregistration.json",
        "lf",
    ),
    "winner_v8_helper": ("tools/run_winner_v8_physical_envelope_contract.py", "lf"),
    "winner_v9_transform": ("tools/run_winner_v9_stored_bound_contract.py", "lf"),
    "winner_v9_preregistration": (
        "outputs/analysis/winner_v9_stored_bound_contract_preregistration.json",
        "lf",
    ),
    "winner_v10_transform": ("tools/run_winner_v10_inward_torque_contract.py", "lf"),
    "winner_v10_importer": ("tools/import_winner_v10_inward_torque_contract.py", "lf"),
    "winner_v10_builder": (
        "tools/build_winner_v10_inward_torque_preregistration.py",
        "lf",
    ),
    "winner_v10_preregistration": (
        "outputs/analysis/winner_v10_inward_torque_contract_preregistration.json",
        "lf",
    ),
    "winner_v6b_numeric_attribution": (
        "outputs/analysis/winner_v6b_numeric_hold_attribution.json",
        "lf",
    ),
    "winner_v8_numeric_attribution": (
        "outputs/analysis/winner_v8_numeric_hold_attribution.json",
        "lf",
    ),
    "winner_v9_numeric_attribution": (
        "outputs/analysis/winner_v9_numeric_torque_hold_attribution.json",
        "lf",
    ),
    "winner_v9_nominal_result": (
        "outputs/analysis/winner_v9_nominal_behavior_result.json",
        "lf",
    ),
    "protected_t2_equal_half": (
        "outputs/analysis/ground_up_dual_fit_conservative_envelope_repair_policies/T2_EQUAL_512000.onnx",
        "raw",
    ),
    "protected_t2_equal_final": (
        "outputs/analysis/ground_up_dual_fit_conservative_envelope_repair_policies/T2_EQUAL_1024000.onnx",
        "raw",
    ),
    "reference_residual_network": ("patches/reference_residual_ppo_networks.py", "lf"),
    "patch_search_runner": ("patches/ground_up_search_runner.patch", "lf"),
    "patch_reference_conditioned": (
        "patches/ground_up_reference_conditioned.patch",
        "lf",
    ),
    "patch_recipe_search": ("patches/ground_up_recipe_search.patch", "lf"),
    "patch_stage1_mechanism": (
        "patches/ground_up_stage1_mechanism_stack.patch",
        "lf",
    ),
    "patch_nominal_bootstrap": (
        "patches/ground_up_nominal_reference_bootstrap.patch",
        "lf",
    ),
    "patch_signed_progress": (
        "patches/ground_up_signed_progress_objective.patch",
        "lf",
    ),
    "patch_reference_residual": (
        "patches/ground_up_reference_residual_actor.patch",
        "lf",
    ),
    "patch_hard_vector": (
        "patches/ground_up_hard_vector_command_support.patch",
        "lf",
    ),
    "patch_measured_bridge": (
        "patches/ground_up_measured_actuator_bridge.patch",
        "lf",
    ),
    "patch_applied_target": (
        "patches/ground_up_applied_target_observation.patch",
        "lf",
    ),
    "patch_tracking_tail": (
        "patches/ground_up_tracking_tail_exceedance.patch",
        "lf",
    ),
    "builder": (
        "tools/build_winner_v12_full_calibrator_training_cpu_contract.py",
        "lf",
    ),
    "checker": (
        "tools/check_winner_v12_full_calibrator_training_cpu_contract.py",
        "lf",
    ),
    "tests": ("tests/test_winner_v12_full_calibrator_training_cpu_contract.py", "lf"),
    "runner": ("tools/run_winner_v12_full_calibrator_training.py", "lf"),
    "preregistration": (
        "outputs/analysis/winner_v12_full_calibrator_training_preregistration.json",
        "lf",
    ),
    "training_primitives": ("patches/winner_v12_calibrator_training.py", "lf"),
    "decomposed_network": ("patches/winner_v12_decomposed_backend_networks.py", "lf"),
    "smoke_runner": ("tools/run_winner_v12_calibrator_cpu_smoke.py", "lf"),
    "smoke_contract": (
        "outputs/analysis/winner_v12_calibrator_cpu_smoke_contract.json",
        "lf",
    ),
    "calibrator_design": (
        "outputs/analysis/winner_v12_calibrator_training_preregistration.json",
        "lf",
    ),
    "domain": (
        "outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json",
        "lf",
    ),
    "p30_fit": ("outputs/analysis/fixed_target_p30_actuator_fit_20260712.json", "lf"),
    "p31_34_fit": (
        "outputs/analysis/fixed_target_p31_34_actuator_fit_20260712.json",
        "lf",
    ),
    "actuator_bridge": ("tools/actuator_bridge_model.py", "lf"),
    "runtime_observer": (
        "artifacts/runtime_handoff/rdkx5_native_20260719/observer/winner_v2_contract.py",
        "lf",
    ),
    "runtime_observer_contract": (
        "artifacts/runtime_handoff/rdkx5_native_20260719/observer_contract.json",
        "lf",
    ),
    "reference_table": (
        "artifacts/runtime_handoff/rdkx5_native_20260719/reference/ground_up_projected_reference_feature_table.npz",
        "raw",
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def source_manifest() -> dict[str, dict[str, str]]:
    manifest = {}
    for name, (relative, mode) in SOURCE_PATHS.items():
        path = ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        manifest[name] = {
            "path": relative,
            "hash_mode": mode,
            "sha256": lf_sha256(path) if mode == "lf" else sha256(path),
        }
    return manifest


def assigned_integer(module: ast.Module, name: str) -> int:
    for node in module.body:
        if isinstance(node, ast.Assign):
            if any(
                isinstance(target, ast.Name) and target.id == name
                for target in node.targets
            ):
                return int(ast.literal_eval(node.value))
    raise ValueError(f"missing literal assignment: {name}")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def main() -> int:
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    dispatch_attribution = json.loads(
        (
            ROOT
            / "outputs/analysis/winner_v12_full_calibrator_training_cpu_contract_dispatch_attribution.json"
        ).read_text(encoding="utf-8")
    )
    serialization_failure_attribution = json.loads(
        (
            ROOT
            / "outputs/analysis/winner_v12_full_calibrator_training_cpu_contract_serialization_failure_attribution.json"
        ).read_text(encoding="utf-8")
    )
    training_preupdate_failure = json.loads(
        (
            ROOT
            / "outputs/analysis/winner_v12_full_calibrator_training_preupdate_failure_attribution.json"
        ).read_text(encoding="utf-8")
    )
    source = RUNNER.read_text(encoding="utf-8")
    workflow_source = (
        ROOT / ".github/workflows/winner-v12-full-calibrator-training-cpu-contract.yml"
    ).read_text(encoding="utf-8")
    workflow_python_tools = set(
        re.findall(r"python (tools/[A-Za-z0-9_./-]+\.py)", workflow_source)
    )
    manifest_paths = {relative for relative, _mode in SOURCE_PATHS.values()}
    module = ast.parse(source)
    schedule = {
        "root_seed": assigned_integer(module, "ROOT_SEED"),
        "parameter_seed": assigned_integer(module, "PARAMETER_SEED"),
        "episode_ticks": assigned_integer(module, "EPISODE_TICKS"),
        "stage1_updates": assigned_integer(module, "STAGE1_UPDATES"),
        "stage2_updates": assigned_integer(module, "STAGE2_UPDATES"),
        "scheduled_tick_slots_per_update": assigned_integer(
            module, "SCHEDULED_TICK_SLOTS_PER_UPDATE"
        ),
    }
    checks = {
        "preregistration_exact": preregistration.get("status")
        == "PREREGISTERED_WINNER_V12_FULL_CALIBRATOR_TRAINING"
        and preregistration.get("decision")
        == "AUTHORIZE_FULL_CALIBRATOR_RUNNER_AND_CPU_CONTRACT_ONLY",
        "zero_update_authority": preregistration["authority"]["optimizer_updates_now"]
        == 0
        and preregistration["authority"]["formal_support_cells_now"] == 0,
        "schedule_exact": schedule
        == {
            "root_seed": 120120,
            "parameter_seed": 60720,
            "episode_ticks": 250,
            "stage1_updates": 100,
            "stage2_updates": 100,
            "scheduled_tick_slots_per_update": 20_000,
        },
        "runner_has_exact_population_and_seed_binding": "def training_population("
        in source
        and "def prng_for_update(" in source
        and "zip(episodes, population, strict=True)" in source,
        "runner_has_atomic_hash_verified_recovery": "def save_snapshot(" in source
        and "def ensure_snapshot_receipt(" in source
        and "def quarantine_uncommitted_pending(" in source
        and "def validate_stage2_lineage(" in source
        and "def newest_committed_snapshot(" in source,
        "runner_requires_one_run_launch_claim": "LAUNCH_CONTRACT =" in source
        and "def claim_receipt_payload(" in source
        and "def consume_or_validate_claim(" in source
        and "launch authorization claim identity changed" in source,
        "runner_hashes_all_artifacts": "def build_snapshot_manifest(" in source
        and '"exact_201_immutable_snapshots"' in source
        and '"stage1_final_artifact"' in source
        and '"persistent_artifacts"' in source,
        "runner_asserts_per_update_invariants": "def validate_stage2_masks(" in source
        and "def validate_log_std(" in source
        and "def validate_stage1_normalization(" in source
        and "snapshot archive member schema changed" in source
        and "snapshot metadata schema changed" in source
        and "snapshot metric-row schema changed" in source
        and "Stage-1 fixed-P30 observation slot changed" in source
        and "Stage-2 changed frozen Stage-1 leaves" in source,
        "onnx_contract_uses_nonzero_bank": "persistent ONNX observation bank lost nonzero coverage"
        in source
        and '"onnx_observation_bank"' in source,
        "dispatch_failure_is_preexecution_only": dispatch_attribution.get("status")
        == "INVALID_PREEXECUTION_WORKFLOW_NOT_ON_DEFAULT_BRANCH"
        and dispatch_attribution["attempt"]["github_run_created"] is False
        and dispatch_attribution["authority"]["optimizer_updates"] == 0
        and dispatch_attribution["authority"]["formal_cpu_contract_executed"] is False,
        "serialization_failure_is_zero_update_only": serialization_failure_attribution.get(
            "status"
        )
        == "INVALID_RESULT_SERIALIZATION_AFTER_ZERO_UPDATE_EXECUTION"
        and serialization_failure_attribution.get("decision")
        == "AUTHORIZE_ONE_CORRECTED_ZERO_UPDATE_CPU_CONTRACT_RUN_ONLY"
        and serialization_failure_attribution["attempt"]["github_run_id"] == 29806564376
        and serialization_failure_attribution["authority"]["optimizer_updates"] == 0
        and serialization_failure_attribution["authority"][
            "full_calibrator_training_executed"
        ]
        is False
        and serialization_failure_attribution["authority"]["formal_cpu_contract_passed"]
        is False,
        "training_failure_is_preupdate_only": training_preupdate_failure.get("status")
        == "INVALID_PREUPDATE_STAGE1_NORMALIZATION_VALIDATION"
        and training_preupdate_failure.get("decision")
        == "AUTHORIZE_CORRECTED_RUNNER_AND_NEW_ZERO_UPDATE_CPU_CONTRACT_ONLY"
        and training_preupdate_failure["attempt"]["github_run_id"] == 29807546004
        and training_preupdate_failure["execution"]["optimizer_updates"] == 0
        and training_preupdate_failure["evidence"]["committed_snapshots"] == 0
        and training_preupdate_failure["evidence"]["result_written"] is False,
        "workflow_is_one_shot_branch_path_cpu_contract": "workflow_dispatch:"
        not in workflow_source
        and "push:" in workflow_source
        and "codex/winner-v4-response-contract" in workflow_source
        and "- .github/workflows/winner-v12-full-calibrator-training-cpu-contract.yml"
        in workflow_source
        and "matrix:" not in workflow_source
        and 'python-version: "3.12.13"' in workflow_source
        and "fetch-depth: 0" in workflow_source,
        "every_workflow_python_tool_hash_bound": bool(workflow_python_tools)
        and workflow_python_tools <= manifest_paths,
        "calibrator_only_scope_preserved": preregistration["architectural_scope"][
            "calibrator_only"
        ]
        is True
        and preregistration["architectural_scope"]["locomotion_adapter_training"]
        is False,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise SystemExit(f"full-training CPU contract build failed: {failed}")
    contract = {
        "schema_version": "winner_v12.full_calibrator_training_cpu_contract.v2",
        "status": "PASS_WINNER_V12_FULL_CALIBRATOR_TRAINING_CPU_CONTRACT_FROZEN",
        "decision": "AUTHORIZE_ONE_ZERO_UPDATE_FULL_TRAINING_CPU_CONTRACT_RUN_ONLY",
        "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
        "software_versions": {
            key: value
            for key, value in preregistration[
                "implementation_contract_environment"
            ].items()
            if key != "platform"
        },
        "platform": "CPU only",
        "schedule": schedule,
        "formal_contract_execution": {
            "full_stage1_rollout_environments": 80,
            "stage1_scheduled_tick_slots_per_environment_capacity": 250,
            "full_stage2_rollout_environments": 80,
            "stage2_scheduled_tick_slots_per_environment_capacity": 250,
            "actual_attempted_and_valid_transitions": "recorded separately in the formal result because invalid-support termination may end an episode early",
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "required_checks": [
            "exact source, software, Playground, fit, population, seed and initialization identities",
            "full 80-environment Stage-1 and Stage-2 no-update rollouts",
            "independent full-population float64 Stage-1 normalizer recomputation and frozen lineage",
            "finite objectives and gradients without calling Adam",
            "fixed-P30 observer slot and exact previous-action chain",
            "exact Stage-2 terminal masks and graph-owned action boundary",
            "atomic snapshot readback, self-hash, receipt, lineage and newest-state selection",
            "pending-artifact quarantine and stale-latest-pointer repair",
            "nonzero 250-tick JAX/ONNX recurrent-chain equivalence",
            "one logical-run authorization claim bound to one exact resolved work root",
            "heldout configurations absent from normalization and optimizer populations",
        ],
        "expected_result": {
            "status": "PASS_WINNER_V12_FULL_CALIBRATOR_TRAINING_CPU_CONTRACT",
            "decision": "AUTHORIZE_ONE_WINNER_V12_FULL_CALIBRATOR_TRAINING_RUN_ONLY",
            "execution": {
                "optimizer_updates": 0,
                "formal_support_cells": 0,
                "locomotion_training_steps": 0,
                "robot_or_rdk_access": 0,
            },
        },
        "superseded_preexecution_dispatch": {
            "status": dispatch_attribution["status"],
            "workflow_commit": dispatch_attribution["attempt"]["workflow_commit"],
            "github_run_created": False,
            "optimizer_updates": 0,
            "formal_cpu_contract_executed": False,
        },
        "superseded_zero_update_serialization_failure": {
            "status": serialization_failure_attribution["status"],
            "github_run_id": serialization_failure_attribution["attempt"][
                "github_run_id"
            ],
            "commit": serialization_failure_attribution["attempt"]["commit"],
            "optimizer_updates": 0,
            "formal_cpu_contract_passed": False,
        },
        "superseded_preupdate_training_failure": {
            "status": training_preupdate_failure["status"],
            "github_run_id": training_preupdate_failure["attempt"]["github_run_id"],
            "commit": training_preupdate_failure["attempt"]["commit"],
            "optimizer_updates": 0,
            "committed_snapshots": 0,
            "full_calibrator_training_started": False,
        },
        "checks": checks,
        "failed_checks": [],
        "sources": source_manifest(),
        "pass_authorizes_only": "one frozen, seed-120120, no-retry full calibrator training run with per-update recovery; it does not authorize the 124-cell gate, locomotion training, deployment, Gate 5, or robot access",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(contract, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    markdown = f"""# Winner-v12 full calibrator training CPU contract

- Status: `{contract["status"]}`
- Decision: `{contract["decision"]}`
- Contract SHA-256: `{lf_sha256(OUTPUT)}`
- Source-manifest SHA-256: `{canonical_sha256(contract["sources"])}`

This prospective contract authorizes one CPU-only implementation check with zero optimizer updates. It exercises the complete 80-episode rollout topology, exact terminal masking, snapshot/recovery integrity, and a nonzero recurrent ONNX chain. It does not run formal support cells or train locomotion, and it provides no robot or Gate 5 clearance.

A passing result may authorize only the single frozen full calibrator run described by the preregistration. The trained calibrator would still require its separate 124-cell support/context gate and is not itself a walking policy.
"""
    MARKDOWN.write_text(markdown, encoding="utf-8")
    print(json.dumps({"status": contract["status"], "sha256": lf_sha256(OUTPUT)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
