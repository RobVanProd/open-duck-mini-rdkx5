from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = (
    ROOT / "outputs/analysis/winner_v12_full_calibrator_training_cpu_contract.json"
)
PREREGISTRATION = (
    ROOT / "outputs/analysis/winner_v12_full_calibrator_training_preregistration.json"
)
RUNNER = ROOT / "tools/run_winner_v12_full_calibrator_training.py"
CHECKER = ROOT / "tools/check_winner_v12_full_calibrator_training_cpu_contract.py"
WORKFLOW = (
    ROOT / ".github/workflows/winner-v12-full-calibrator-training-cpu-contract.yml"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load() -> dict:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def literal_assignments(path: Path) -> dict[str, object]:
    module = ast.parse(path.read_text(encoding="utf-8"))
    values = {}
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    try:
                        values[target.id] = ast.literal_eval(node.value)
                    except (ValueError, TypeError):
                        pass
    return values


def test_contract_is_prospective_zero_update_cpu_only() -> None:
    contract = load()
    assert (
        contract["status"]
        == "PASS_WINNER_V12_FULL_CALIBRATOR_TRAINING_CPU_CONTRACT_FROZEN"
    )
    assert (
        contract["decision"]
        == "AUTHORIZE_ONE_ZERO_UPDATE_FULL_TRAINING_CPU_CONTRACT_RUN_ONLY"
    )
    assert contract["formal_contract_execution"] == {
        "full_stage1_rollout_environments": 80,
        "stage1_scheduled_tick_slots_per_environment_capacity": 250,
        "full_stage2_rollout_environments": 80,
        "stage2_scheduled_tick_slots_per_environment_capacity": 250,
        "actual_attempted_and_valid_transitions": "recorded separately in the formal result because invalid-support termination may end an episode early",
        "optimizer_updates": 0,
        "formal_support_cells": 0,
        "locomotion_training_steps": 0,
        "robot_or_rdk_access": 0,
    }


def test_runner_schedule_has_no_cli_tuning_surface() -> None:
    values = literal_assignments(RUNNER)
    assert values["ROOT_SEED"] == 120120
    assert values["PARAMETER_SEED"] == 60720
    assert values["EPISODE_TICKS"] == 250
    assert values["STAGE1_UPDATES"] == 100
    assert values["STAGE2_UPDATES"] == 100
    assert values["SCHEDULED_TICK_SLOTS_PER_UPDATE"] == 20_000
    source = RUNNER.read_text(encoding="utf-8")
    assert 'parser.add_argument("--stage1-updates"' not in source
    assert 'parser.add_argument("--stage2-updates"' not in source
    assert 'parser.add_argument("--seed"' not in source
    assert 'parser.add_argument("--learning-rate"' not in source
    assert "while True" not in source


def test_full_population_and_seed_derivation_are_literal() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "population.extend([dict(configuration), dict(configuration)])" in source
    assert "if len(population) != 80" in source
    assert "entropy = [ROOT_SEED, stage, update_index, environment_index]" in source
    assert "zip(episodes, population, strict=True)" in source
    assert "expected_plant = smoke.PLANTS[environment % 2]" in source


def test_atomic_recovery_and_complete_artifact_manifest_are_required() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    for literal in (
        "def save_snapshot(",
        "def ensure_snapshot_receipt(",
        "def newest_committed_snapshot(",
        "def validate_stage2_lineage(",
        "def quarantine_uncommitted_pending(",
        "def ensure_stage1_final_checkpoint(",
        "def build_snapshot_manifest(",
        '"exact_201_immutable_snapshots"',
        "write_json_exclusive(result_path, result)",
    ):
        assert literal in source
    assert "COMMITTED_SNAPSHOT_RE.fullmatch(path.name)" in source
    assert "replace_latest_snapshot(newest_resume_snapshot" in source
    assert "replace_latest_snapshot(newest_snapshot, latest_snapshot)" in source


def test_one_run_authority_requires_frozen_launch_claim_and_work_root() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "LAUNCH_CONTRACT =" in source
    assert "PASS_WINNER_V12_FULL_CALIBRATOR_TRAINING_LAUNCH_FROZEN" in source
    assert "AUTHORIZE_EXACTLY_ONE_LOGICAL_TRAINING_RUN" in source
    assert "def claim_receipt_payload(" in source
    assert "launch claim does not authorize this resolved work root" in source
    assert "def consume_or_validate_claim(" in source


def test_every_update_checks_masks_lineage_bounds_and_finiteness() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "Stage-1 fixed-P30 observation slot changed" in source
    assert "Stage-1 realized-action chain changed" in source
    assert "Stage-2 changed frozen Stage-1 leaves" in source
    assert "Stage-2 sample-mask active prefix is not exact one" in source
    assert "Stage-2 transition-mask active prefix is not exact one" in source
    assert "Stage-2 done mask is not exact one-hot" in source
    assert "Stage-2 log_std clamp changed" in source
    assert '"gradients": gradients' in source
    assert '"optimizer": optimizer' in source


def test_onnx_chain_uses_a_nonzero_observation_bank() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "np.arange(EPISODE_TICKS * training.OBS_SIZE" in source
    assert "persistent ONNX observation bank lost nonzero coverage" in source
    assert '"onnx_observation_bank"' in source
    assert '"jax_onnx_at_most_1e_7"' in source
    assert '"previous_action_out_equals_action_bit_exact"' in source


def test_checker_cannot_execute_an_optimizer_update() -> None:
    source = CHECKER.read_text(encoding="utf-8")
    assert "def forbidden_adam_step(" in source
    assert "training.adam_step = forbidden_adam_step" in source
    assert "CPU contract may not execute an optimizer update" in source
    assert '"optimizer_updates": optimizer_calls' in source
    assert '"formal_support_cells": 0' in source
    assert '"robot_or_rdk_access": 0' in source


def test_checker_normalizes_only_boolean_check_values_for_json() -> None:
    source = CHECKER.read_text(encoding="utf-8")
    assert "def normalize_check_bools(" in source
    assert "isinstance(value, (bool, np.bool_))" in source
    assert "normalized[name] = bool(value)" in source
    assert "checks = normalize_check_bools(checks)" in source


def test_workflow_is_one_shot_branch_path_exact_cpu_run() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")
    assert "workflow_dispatch:" not in source
    assert "push:" in source
    assert "codex/winner-v4-response-contract" in source
    assert (
        "- .github/workflows/winner-v12-full-calibrator-training-cpu-contract.yml"
        in source
    )
    assert "matrix:" not in source
    assert 'python-version: "3.12.13"' in source
    assert "fetch-depth: 0" in source
    assert "cuda" not in source.lower()
    assert "check_winner_v12_full_calibrator_training_cpu_contract.py" in source


def test_failed_manual_dispatch_is_recorded_as_zero_execution() -> None:
    attribution = json.loads(
        (
            ROOT
            / "outputs/analysis/winner_v12_full_calibrator_training_cpu_contract_dispatch_attribution.json"
        ).read_text(encoding="utf-8")
    )
    assert (
        attribution["status"] == "INVALID_PREEXECUTION_WORKFLOW_NOT_ON_DEFAULT_BRANCH"
    )
    assert attribution["attempt"]["github_run_created"] is False
    assert attribution["authority"]["optimizer_updates"] == 0
    assert attribution["authority"]["formal_cpu_contract_executed"] is False


def test_failed_result_serialization_is_attributed_without_training_authority() -> None:
    attribution = json.loads(
        (
            ROOT
            / "outputs/analysis/winner_v12_full_calibrator_training_cpu_contract_serialization_failure_attribution.json"
        ).read_text(encoding="utf-8")
    )
    assert (
        attribution["status"]
        == "INVALID_RESULT_SERIALIZATION_AFTER_ZERO_UPDATE_EXECUTION"
    )
    assert attribution["attempt"]["github_run_id"] == 29806564376
    assert attribution["authority"]["optimizer_updates"] == 0
    assert attribution["authority"]["full_calibrator_training_executed"] is False
    assert attribution["authority"]["formal_cpu_contract_passed"] is False


def test_every_workflow_python_tool_is_hash_bound() -> None:
    commands = set(
        re.findall(r"python (tools/[A-Za-z0-9_./-]+\.py)", WORKFLOW.read_text())
    )
    manifest_paths = {item["path"] for item in load()["sources"].values()}
    assert commands
    assert commands <= manifest_paths


def test_environment_and_authority_match_preregistration() -> None:
    contract = load()
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    expected = dict(preregistration["implementation_contract_environment"])
    assert expected.pop("platform") == "CPU only"
    assert contract["software_versions"] == expected
    assert contract["preregistration_lf_sha256"] == lf_sha256(PREREGISTRATION)
    assert contract["pass_authorizes_only"].startswith(
        "one frozen, seed-120120, no-retry full calibrator training run"
    )
    assert "does not authorize" in contract["pass_authorizes_only"]


def test_contract_hashes_every_execution_source() -> None:
    contract = load()
    assert contract["checks"] and all(contract["checks"].values())
    assert contract["failed_checks"] == []
    for item in contract["sources"].values():
        path = ROOT / item["path"]
        observed = lf_sha256(path) if item["hash_mode"] == "lf" else sha256(path)
        assert observed == item["sha256"], item["path"]
