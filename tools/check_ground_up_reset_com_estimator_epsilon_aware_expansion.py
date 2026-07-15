#!/usr/bin/env python3
"""Contract the epsilon-aware hosted checkpoint-expansion wrapper on CPU."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any


REPO = Path(__file__).resolve().parents[1]
WRAPPER = REPO / "tools/colab_ground_up_reset_com_estimator_epsilon_aware_training.py"
HOSTED = REPO / "tools/colab_ground_up_reset_com_estimator_training.py"
PREREG = REPO / "outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_EPSILON_AWARE_HOSTED_EXPANSION_CORRECTION_PREREGISTRATION_20260715.md"
ULP_JSON = REPO / "outputs/analysis/ground_up_reset_com_estimator_action_distribution_ulp_sensitivity.json"
ULP_MD = REPO / "outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_ACTION_DISTRIBUTION_ULP_SENSITIVITY_RESULT_20260715.md"
EXPECTED = {
    "wrapper": "c1d88f6c48a6d2fb3191e4c25088f83e1163ff217058a94d79b2a17394aabda4",
    "hosted": "a3e5fc38994cecd65d89fdc6b9ede23c2433e917b84583dfcced42c161e79d67",
    "prereg": "22daea5aaddf8d480d5748d3c1d1053ff6dd7bff2d4ab04af2b69750d73a5947",
    "ulp_json": "a30df798a2dd659f0299c92586fb4b1eb48047a0323bb727426e59dcc95d9c7e",
    "ulp_md": "b08f138aa29af0798e2d626c0fb9a03e0f21289f1f1fa50326a2da61aaa0b3ff",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def fixture(error: float = 2.0 ** -23, critic: float = 0.0) -> dict[str, Any]:
    checks = {
        "source_shapes_exact": True, "source_count_exact": True,
        "expanded_shapes_exact": True, "inserted_normalizer_exact": True,
        "inserted_rows_zero": True, "all_other_values_bit_exact": True,
        "save_restore_bit_exact": True, "step_zero_outputs_exact": False,
        "reference_tail_exact": True, "all_values_finite": True,
    }
    return {
        "status": "FAIL_HOSTED_CHECKPOINT_EXPANSION",
        "checks": checks, "failed_checks": ["step_zero_outputs_exact"],
        "source_directory_sha256": "05c0c08468f02b96d7e4316fdae6527c6ee223fba507ce3f6a3221b2561a920e",
        "devices": ["cuda:0"],
        "output_equivalence": [
            {"z": z, "actor_max_abs_error": error,
             "critic_max_abs_error": critic, "reference_tail_exact": True}
            for z in (-1.0, 0.0, 1.0)
        ],
    }


def rejected(wrapper: Any, value: dict[str, Any], live_gpu: bool = True) -> bool:
    try:
        wrapper.correct_report(value, live_gpu=live_gpu)
    except RuntimeError:
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    paths = {"wrapper": WRAPPER, "hosted": HOSTED, "prereg": PREREG,
             "ulp_json": ULP_JSON, "ulp_md": ULP_MD}
    hashes = {name: sha256(path) for name, path in paths.items()}
    wrapper = load(WRAPPER, "epsilon_wrapper_contract")
    hosted = load(HOSTED, "epsilon_hosted_contract")
    ulp = json.loads(ULP_JSON.read_text())
    valid_raw = fixture()
    valid = wrapper.correct_report(valid_raw, live_gpu=True)
    raw_copy = json.loads(json.dumps(valid_raw))

    too_large = fixture(float(2.0 ** -23 + 1.0e-12))
    critic_nonzero = fixture(critic=1.0e-12)
    wrong_source = fixture(); wrong_source["source_directory_sha256"] = "wrong"
    extra_failure = fixture(); extra_failure["failed_checks"].append("save_restore_bit_exact"); extra_failure["checks"]["save_restore_bit_exact"] = False
    original_pass = fixture(0.0); original_pass["status"] = "PASS_HOSTED_CHECKPOINT_EXPANSION"; original_pass["failed_checks"] = []; original_pass["checks"]["step_zero_outputs_exact"] = True

    command = hosted.training_command(Path("/root"), Path("/assets"), Path("/arm"), Path("/restore"))
    checks = {
        "frozen_hashes_exact": hashes == EXPECTED,
        "ulp_evidence_exact": ulp.get("status") == "PASS_ACTION_DISTRIBUTION_ULP_SENSITIVITY_AUDIT"
        and ulp.get("decision") == "ULP_ENVELOPE_BELOW_EXISTING_ACTION_IDENTITY_BOUNDARY"
        and ulp.get("measured_envelope") == 2.0 ** -23 and ulp.get("failed_checks") == [],
        "valid_epsilon_fixture_passes": valid.get("status")
        == "PASS_HOSTED_CHECKPOINT_EXPANSION_EPSILON_AWARE" and valid.get("failed_checks") == [],
        "raw_failure_preserved_unchanged": valid_raw == raw_copy
        and valid.get("raw_original_1e7_report") == raw_copy
        and valid.get("raw_original_1e7_status_preserved") == "FAIL_HOSTED_CHECKPOINT_EXPANSION"
        and valid.get("raw_original_1e7_failed_checks_preserved") == ["step_zero_outputs_exact"],
        "threshold_exact_float32_epsilon": valid.get("threshold")
        == {"name": "float32_epsilon", "value": 2.0 ** -23},
        "over_epsilon_rejected": rejected(wrapper, too_large),
        "nonzero_critic_rejected": rejected(wrapper, critic_nonzero),
        "wrong_source_rejected": rejected(wrapper, wrong_source),
        "extra_failure_rejected": rejected(wrapper, extra_failure),
        "original_pass_not_reinterpreted": rejected(wrapper, original_pass),
        "no_gpu_proof_rejected": rejected(wrapper, fixture(), live_gpu=False),
        "original_recipe_constants_exact": hosted.ARM_NAME == "RESET_EST_LATCH_U05"
        and hosted.EXPECTED_STEPS == [0, 1_003_520, 2_007_040]
        and hosted.MAX_HOSTED_SECONDS == 2_400 and hosted.MAX_COMPUTE_UNITS == 2.0,
        "original_training_command_exact": " ".join(command).count("--num_timesteps 2000000") == 1
        and "--ppo_seed 100" in " ".join(command)
        and "--ground_up_reset_com_estimator_input" in command
        and "--ground_up_torso_com_distribution uniform" in " ".join(command)
        and command[-2:] == ["--restore_checkpoint_path", "/restore"],
        "wrapper_changes_only_expansion_boundary": "module.hosted_expand = epsilon_aware_expand" in WRAPPER.read_text()
        and "result = module.main()" in WRAPPER.read_text()
        and "raw_original_1e7_report" in WRAPPER.read_text(),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    result = {
        "schema_version": "ground_up_reset_estimator_epsilon_aware_expansion_contract.v1",
        "status": "PASS_EPSILON_AWARE_HOSTED_EXPANSION_CONTRACT" if not failed else "FAIL_EPSILON_AWARE_HOSTED_EXPANSION_CONTRACT",
        "checks": checks, "failed_checks": failed, "source_hashes": hashes,
        "pass_fixture": valid,
        "original_training_command": command,
        "execution": {"cpu_only": True, "colab_sessions_created": 0,
                      "remote_bytes": 0, "training_steps": 0,
                      "behavior_cells": 0, "robot_or_rdk": False},
        "authority": {"wall_only_launcher_contract_next_if_pass": True,
                      "training_now": False, "colab_now": False,
                      "local_gpu_or_igpu": False, "robot_or_rdk": False},
    }
    args.output.resolve().write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "failed_checks": failed}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
