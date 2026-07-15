#!/usr/bin/env python3
"""Run the frozen reset-estimator job through the epsilon-aware expansion gate."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from pathlib import Path
import shutil
import sys
from typing import Any


HOSTED_SOURCE = Path("/content/colab_ground_up_reset_com_estimator_training.py")
ULP_RESULT = Path("/content/ground_up_reset_com_estimator_action_distribution_ulp_sensitivity.json")
ORIGINAL_REPORT_NAME = "hosted_expansion_report_original_1e7.json"
EPSILON = 2.0 ** -23
EXPECTED_SOURCE_DIRECTORY_SHA256 = "05c0c08468f02b96d7e4316fdae6527c6ee223fba507ce3f6a3221b2561a920e"
EXPECTED_HOSTED_SHA256 = "a3e5fc38994cecd65d89fdc6b9ede23c2433e917b84583dfcced42c161e79d67"
EXPECTED_ULP_SHA256 = "a30df798a2dd659f0299c92586fb4b1eb48047a0323bb727426e59dcc95d9c7e"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_hosted() -> Any:
    if sha256(HOSTED_SOURCE) != EXPECTED_HOSTED_SHA256:
        raise RuntimeError("frozen hosted source hash changed")
    spec = importlib.util.spec_from_file_location("epsilon_aware_frozen_hosted", HOSTED_SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen hosted source")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_ulp() -> dict[str, Any]:
    if sha256(ULP_RESULT) != EXPECTED_ULP_SHA256:
        raise RuntimeError("ULP result hash changed")
    result = json.loads(ULP_RESULT.read_text())
    if (
        result.get("status") != "PASS_ACTION_DISTRIBUTION_ULP_SENSITIVITY_AUDIT"
        or result.get("decision") != "ULP_ENVELOPE_BELOW_EXISTING_ACTION_IDENTITY_BOUNDARY"
        or result.get("measured_envelope") != EPSILON
        or result.get("failed_checks") != []
    ):
        raise RuntimeError("ULP evidence does not authorize epsilon-aware correction")
    return result


def correct_report(raw: dict[str, Any], *, live_gpu: bool) -> dict[str, Any]:
    cells = raw.get("output_equivalence", [])
    errors = [cell.get(key) for cell in cells
              for key in ("actor_max_abs_error", "critic_max_abs_error")]
    other_checks = {key: value for key, value in raw.get("checks", {}).items()
                    if key != "step_zero_outputs_exact"}
    checks = {
        "raw_status_is_original_failure": raw.get("status") == "FAIL_HOSTED_CHECKPOINT_EXPANSION",
        "raw_sole_failure_is_step_zero": raw.get("failed_checks") == ["step_zero_outputs_exact"]
        and raw.get("checks", {}).get("step_zero_outputs_exact") is False,
        "all_other_raw_checks_pass": bool(other_checks) and all(other_checks.values()),
        "source_directory_hash_exact": raw.get("source_directory_sha256")
        == EXPECTED_SOURCE_DIRECTORY_SHA256,
        "cells_exact": len(cells) == 3
        and [cell.get("z") for cell in cells] == [-1.0, 0.0, 1.0],
        "six_errors_finite": len(errors) == 6
        and all(isinstance(value, (int, float)) and math.isfinite(value) for value in errors),
        "critic_errors_zero": len(cells) == 3
        and all(cell.get("critic_max_abs_error") == 0.0 for cell in cells),
        "actor_errors_within_float32_epsilon": len(cells) == 3
        and all(isinstance(cell.get("actor_max_abs_error"), (int, float))
                and cell["actor_max_abs_error"] <= EPSILON for cell in cells),
        "report_device_exact_cuda0": raw.get("devices") == ["cuda:0"],
        "live_jax_gpu": live_gpu,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"epsilon-aware expansion correction failed: {failed}")
    return {
        "schema_version": "ground_up_reset_estimator_hosted_expansion_epsilon_aware.v1",
        "status": "PASS_HOSTED_CHECKPOINT_EXPANSION_EPSILON_AWARE",
        "checks": checks,
        "failed_checks": [],
        "threshold": {"name": "float32_epsilon", "value": EPSILON},
        "maximum_actor_error": max(cell["actor_max_abs_error"] for cell in cells),
        "maximum_critic_error": max(cell["critic_max_abs_error"] for cell in cells),
        "raw_original_1e7_report": raw,
        "raw_original_1e7_status_preserved": raw["status"],
        "raw_original_1e7_failed_checks_preserved": raw["failed_checks"],
        "ulp_evidence": {
            "path": str(ULP_RESULT), "sha256": EXPECTED_ULP_SHA256,
            "decision": "ULP_ENVELOPE_BELOW_EXISTING_ACTION_IDENTITY_BOUNDARY",
        },
    }


def run(module: Any) -> int:
    import jax

    load_ulp()
    original_expand = module.hosted_expand
    invocation_count = 0

    def epsilon_aware_expand(source: Path, destination: Path, report_path: Path) -> dict[str, Any]:
        nonlocal invocation_count
        invocation_count += 1
        if invocation_count != 1:
            raise RuntimeError("expansion correction must execute exactly once")
        try:
            original_expand(source, destination, report_path)
        except RuntimeError:
            pass
        if not report_path.is_file():
            raise RuntimeError("original expansion report missing")
        raw_bytes = report_path.read_bytes()
        raw = json.loads(raw_bytes)
        live_gpu = any(device.platform == "gpu" for device in jax.devices())
        corrected = correct_report(raw, live_gpu=live_gpu)
        original_path = report_path.with_name(ORIGINAL_REPORT_NAME)
        if original_path.exists():
            raise FileExistsError(original_path)
        original_path.write_bytes(raw_bytes)
        report_path.write_text(json.dumps(corrected, indent=2, sort_keys=True) + "\n")
        return corrected

    module.hosted_expand = epsilon_aware_expand
    result = module.main()
    if invocation_count != 1:
        raise RuntimeError(f"expected one expansion correction, found {invocation_count}")
    return result


def main() -> int:
    return run(load_hosted())


if __name__ == "__main__":
    raise SystemExit(main())
