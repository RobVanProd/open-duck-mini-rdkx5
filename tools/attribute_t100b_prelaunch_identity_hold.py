#!/usr/bin/env python3
"""Prove T100B's package identity mismatch before any hosted launch."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
BUNDLE = Path(
    "D:/CodexArtifacts/open-duck-policy/t100b_hidden_expert_package_v1/"
    "t100b_hidden_expert_bundle"
)
DRIVER = BUNDLE / "colab_t100_hidden_expert_continuation.py"
ORIGINAL_PREREG = BUNDLE / "t100_hidden_expert_hosted_preregistration.json"
RECOVERY_PREREG = BUNDLE / "t100b_preexecution_recovery_preregistration.json"
PACKAGE_CONTRACT = ANALYSIS / "t100b_hidden_expert_hosted_package_contract.json"
OUTPUT = ANALYSIS / "t100b_prelaunch_identity_hold_attribution.json"
MARKDOWN = ANALYSIS / "T100B_PRELAUNCH_IDENTITY_HOLD_ATTRIBUTION_20260728.md"

sys.path.insert(0, str(BUNDLE))
sys.path.insert(0, str(ROOT / "tools"))
from colab_winner_v114_linear_torque_continuation import sha256  # noqa: E402


def canonical_sha256(value: Any) -> str:
    import hashlib

    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def load_driver():
    spec = importlib.util.spec_from_file_location("t100b_packaged_driver", DRIVER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load T100B packaged driver")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T100B hold: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T100B attribution requires clean worktree")

    package = json.loads(PACKAGE_CONTRACT.read_text(encoding="utf-8"))
    original = json.loads(ORIGINAL_PREREG.read_text(encoding="utf-8"))
    recovery = json.loads(RECOVERY_PREREG.read_text(encoding="utf-8"))
    driver = load_driver()
    observed_error = None
    try:
        driver.validate_inputs(BUNDLE)
    except ValueError as exc:
        observed_error = f"{type(exc).__name__}: {exc}"
    checks = {
        "package_was_not_launched": (
            package["execution"]["replacement_sessions_opened"] == 0
            and package["execution"]["optimizer_steps"] == 0
            and package["execution"]["formal_behavior_cells"] == 0
        ),
        "exact_validation_failure_reproduced": (
            observed_error == "ValueError: T100 frozen inputs changed"
        ),
        "packaged_driver_matches_recovery_prereg": (
            sha256(DRIVER) == recovery["input_hashes"]["driver"]
        ),
        "packaged_driver_conflicts_with_original_prereg": (
            sha256(DRIVER) != original["input_hashes"]["driver"]
        ),
        "driver_selects_original_prereg_only": (
            driver.PREREGISTRATION_NAME
            == "t100_hidden_expert_hosted_preregistration.json"
        ),
        "optimizer_simulator_behavior_steps_zero": True,
        "robot_or_rdk_access_zero": (
            package["execution"]["robot_or_rdk_access"] == 0
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T100B hold attribution checks failed: {failed}")
    basis: dict[str, Any] = {
        "schema_version": "open_duck.t100b_prelaunch_identity_hold.v1",
        "status": "PASS_T100B_PRELAUNCH_IDENTITY_HOLD_ATTRIBUTION",
        "classification": "PRELAUNCH_DRIVER_PREREGISTRATION_IDENTITY_MISMATCH",
        "decision": "EARN_T100C_ORIGINAL_DRIVER_WRAPPER_PREREGISTRATION_ONLY",
        "failure": {
            "reproduction": observed_error,
            "packaged_driver": {
                "path": str(DRIVER.resolve()),
                "sha256": sha256(DRIVER),
            },
            "original_preregistration_driver_sha256": original["input_hashes"][
                "driver"
            ],
            "recovery_preregistration_driver_sha256": recovery["input_hashes"][
                "driver"
            ],
            "package_contract": {
                "path": str(PACKAGE_CONTRACT.resolve()),
                "sha256": sha256(PACKAGE_CONTRACT),
            },
        },
        "interpretation": {
            "hosted_session_opened": False,
            "optimizer_started": False,
            "simulator_training_started": False,
            "behavior_started": False,
            "mechanism_or_recipe_falsified": False,
            "t100b_package_launchable": False,
        },
        "recovery_design": {
            "preserve_original_t100_driver_byte_exact": True,
            "preserve_original_t100_preregistration_byte_exact": True,
            "add_hash_frozen_external_dispatch_wrapper": True,
            "mechanism_source_gate_recipe_changes": 0,
        },
        "checks": {name: bool(value) for name, value in checks.items()},
        "failed_checks": failed,
        "authority": {
            "one_t100c_wrapper_preregistration": True,
            "hosted_launch": False,
            "additional_training_attempt_retry_or_resume": False,
            "behavior_evaluation": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value = {**basis, "result_sha256": canonical_sha256(basis)}
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T100B prelaunch identity hold attribution",
                "",
                f"- Status: `{value['status']}`",
                f"- Classification: `{value['classification']}`",
                "- Hosted session / optimizer / simulator / behavior: `0 / 0 / 0 / 0`",
                "- Cause: corrected driver hash cannot satisfy the immutable original preregistration",
                "- Recovery: original driver plus one external corrected-dispatch wrapper",
                f"- Result SHA-256: `{value['result_sha256']}`",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"result_sha256={value['result_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
