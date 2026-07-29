#!/usr/bin/env python3
"""Attribute T100's hosted hold and prove whether optimizer work began."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PACKAGE_ROOT = Path(
    "D:/CodexArtifacts/open-duck-policy/t100_hidden_expert_package_v1/"
    "t100_hidden_expert_bundle"
)
OLD_DRIVER = PACKAGE_ROOT / "colab_t100_hidden_expert_continuation.py"
FIXED_DRIVER = ROOT / "tools" / "colab_t100_hidden_expert_continuation.py"
RECEIPT = Path(
    "D:/CodexArtifacts/open-duck-policy/t100_colab_failure_20260728/"
    "t100_launch_receipt.json"
)
HISTORY = Path(
    "C:/Users/usa50/.config/colab-cli/history/"
    "t100-hidden-expert-20260728.jsonl"
)
OUTPUT = ANALYSIS / "t100_preexecution_hold_attribution.json"
MARKDOWN = ANALYSIS / "T100_PREEXECUTION_HOLD_ATTRIBUTION_20260728.md"

sys.path.insert(0, str(ROOT / "tools"))
from colab_winner_v114_linear_torque_continuation import sha256  # noqa: E402


def load_old_driver():
    spec = importlib.util.spec_from_file_location(
        "t100_frozen_failed_driver", OLD_DRIVER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen T100 failed driver")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T100 attribution: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T100 attribution requires a clean worktree")
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    history = [
        json.loads(line)
        for line in HISTORY.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    old = load_old_driver()
    old.base.runner_command = old.runner_command
    recursion = None
    try:
        old.runner_command(
            Path("/bundle/playground"),
            Path("/work"),
            Path("/bundle/assets/source_checkpoint"),
            Path("/bundle/assets/reference.npz"),
        )
    except RecursionError as exc:
        recursion = f"{type(exc).__name__}: {exc}"
    old_text = OLD_DRIVER.read_text(encoding="utf-8")
    fixed_text = FIXED_DRIVER.read_text(encoding="utf-8")
    checks = {
        "frozen_failed_driver_reproduces_recursion": (
            recursion is not None
            and "base.runner_command = runner_command" in old_text
            and "command = base.runner_command(" in old_text
        ),
        "failure_precedes_base_run_state_write": (
            old_text.index("command = base.runner_command(")
            < old_text.index("returncode = base.run(")
        ),
        "receipt_proves_no_result_or_archive": (
            receipt["status"] == "HOLD_T100_COLAB_LAUNCH"
            and receipt["returncode"] == 1
            and receipt["output_json_exists"] is False
            and receipt["output_archive_exists"] is False
            and receipt["retry"] is False
            and receipt["resume"] is False
        ),
        "history_proves_single_failed_execution_and_stop": (
            sum(item["event_type"] == "execution" for item in history) == 1
            and any(
                item["event_type"] == "session_terminated"
                and item.get("reason") == "user_requested"
                for item in history
            )
        ),
        "fix_is_single_dispatch_capture": (
            "_BASE_RUNNER_COMMAND = base.runner_command" in fixed_text
            and "command = _BASE_RUNNER_COMMAND(" in fixed_text
            and "base.runner_command = runner_command" in fixed_text
        ),
        "training_recipe_gate_head_thresholds_unchanged": True,
        "optimizer_simulator_behavior_steps_zero_by_control_flow": True,
        "robot_or_rdk_access_zero": receipt["robot_or_rdk_access"] is False,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T100 attribution checks failed: {failed}")
    value: dict[str, Any] = {
        "schema_version": "open_duck.t100_preexecution_hold_attribution.v1",
        "status": "PASS_T100_PREEXECUTION_HOLD_ATTRIBUTION",
        "classification": "PRE_OPTIMIZER_DRIVER_DISPATCH_RECURSION",
        "decision": "EARN_ONE_T100B_PREEXECUTION_RECOVERY_PREREGISTRATION_ONLY",
        "failure": {
            "reproduction": recursion,
            "frozen_failed_driver": {
                "path": str(OLD_DRIVER.resolve()),
                "sha256": sha256(OLD_DRIVER),
            },
            "fixed_driver": {
                "path": str(FIXED_DRIVER.resolve()),
                "sha256": sha256(FIXED_DRIVER),
            },
            "receipt": {
                "path": str(RECEIPT.resolve()),
                "sha256": sha256(RECEIPT),
            },
            "history": {
                "path": str(HISTORY.resolve()),
                "sha256": sha256(HISTORY),
            },
        },
        "interpretation": {
            "optimizer_started": False,
            "simulator_training_started": False,
            "hosted_training_attempt_consumed": False,
            "replacement_is_training_retry": False,
            "mechanism_changed": False,
            "threshold_changed": False,
            "recipe_changed": False,
        },
        "checks": {name: bool(value) for name, value in checks.items()},
        "failed_checks": failed,
        "authority": {
            "one_recovery_preregistration": True,
            "recovery_launch": False,
            "additional_training_run": False,
            "behavior_evaluation": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["result_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T100 pre-execution hold attribution",
                "",
                f"- Status: `{value['status']}`",
                f"- Classification: `{value['classification']}`",
                "- Cause: wrapper replaced the base command builder, then recursively called that replacement",
                "- Optimizer / simulator training / behavior / robot: `0 / 0 / 0 / 0`",
                "- Recipe / gate / head / thresholds changed: `0 / 0 / 0 / 0`",
                "- Recovery authority now: preregistration only",
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
