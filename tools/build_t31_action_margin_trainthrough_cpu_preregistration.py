#!/usr/bin/env python3
"""Preregister T31's 1,024-step action-margin train-through CPU smoke."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import run_t20_support_trainthrough_one_update as t20


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T22_PREREG = ANALYSIS / "t22_corrected_one_update_cpu_preregistration.json"
T24_RESULT = ANALYSIS / "t24_t23_postexport_result.json"
T28_CONDITION = ANALYSIS / "t28_t23_action_margin_condition_result.json"
T28_TRANSFORM = ANALYSIS / "t28_t23_action_margin_transform_contract.json"
T29_RESULT = ANALYSIS / "t29_t28_remaining_r2_result.json"
T30_RECONCILIATION = (
    ANALYSIS / "t30_t28_margin_causality_reconciliation.json"
)
RUNNER = ROOT / "tools" / "run_t31_action_margin_trainthrough_cpu_smoke.py"
COMPOSED = Path(r"D:\CodexProjects\Open_Duck_Playground-composed-t31-v1")
SOURCE_CHECKPOINT = Path(
    r"D:\CodexArtifacts\open-duck-policy\t23b_extracted_20260726"
    r"\t23_support_trainthrough_continuation\training"
    r"\2026_07_26_231352_1003520"
)
OUTPUT = (
    ANALYSIS
    / "t31_action_margin_trainthrough_cpu_preregistration.json"
)
OUTPUT_MD = (
    ANALYSIS
    / "T31_ACTION_MARGIN_TRAINTHROUGH_CPU_PREREGISTRATION_20260727.md"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    payload = dict(value)
    payload.pop("preregistered_contract_sha256", None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def file_receipt(path: Path) -> dict[str, Any]:
    return {
        "kind": "file",
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def python_inventory(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): sha256(path)
        for path in sorted(root.rglob("*.py"))
    }


def main() -> int:
    t22 = json.loads(T22_PREREG.read_text(encoding="utf-8"))
    t24 = json.loads(T24_RESULT.read_text(encoding="utf-8"))
    t28_condition = json.loads(
        T28_CONDITION.read_text(encoding="utf-8")
    )
    t28_transform = json.loads(
        T28_TRANSFORM.read_text(encoding="utf-8")
    )
    t29 = json.loads(T29_RESULT.read_text(encoding="utf-8"))
    t30 = json.loads(
        T30_RECONCILIATION.read_text(encoding="utf-8")
    )
    half_green_cells = (
        sum(
            block["result"]["green_cells"]
            if "green_cells" in block["result"]
            else sum(
                int(cell["cell_green"])
                for cell in block["result"]["cells"]
            )
            for block in t28_condition["blocks"]
            if block["checkpoint_id"] == "T23_SUPPORT_HALF"
        )
        + sum(
            sum(int(cell["cell_green"]) for cell in block["result"]["cells"])
            for block in t29["blocks"]
            if block["checkpoint_id"] == "T23_SUPPORT_HALF"
        )
    )
    t24_half = t24["deployments"]["1003520"]
    margin_half = next(
        item
        for item in t28_transform["policies"]
        if item["checkpoint_id"] == "T23_SUPPORT_HALF"
    )
    assets = {
        "source_checkpoint": {
            "kind": "directory",
            **t20.directory_receipt(SOURCE_CHECKPOINT),
        },
        "cpu_topology_template": t22["assets"]["cpu_topology_template"],
        "source_v121_half_onnx": file_receipt(
            Path(t24_half["raw"]["path"])
        ),
        "frozen_t18_context_abi_onnx": file_receipt(
            Path(t24_half["context_abi"]["path"])
        ),
        "frozen_t18_pre_margin_wrapped_onnx": file_receipt(
            Path(t24_half["wrapped"]["path"])
        ),
        "frozen_t18_wrapped_onnx": file_receipt(
            Path(margin_half["wrapped"]["path"])
        ),
    }
    sources = {
        "reference": t22["sources"]["reference"],
        "runner": file_receipt(RUNNER),
        "t28_condition": file_receipt(T28_CONDITION),
        "t29_result": file_receipt(T29_RESULT),
        "t30_reconciliation": file_receipt(T30_RECONCILIATION),
    }
    inventory = python_inventory(COMPOSED)
    checks = {
        "posthoc_t28_closed": (
            t30["status"] == "PASS_T30_MIXED_OUTCOME_RECONCILIATION"
            and t30["decision"] == "CLOSE_T28_POSTHOC_MARGIN_TRANSFORM"
        ),
        "half_checkpoint_is_margin_feasible": half_green_cells == 24,
        "t28_exact_transform_contract_green": (
            t28_transform["status"]
            == "PASS_T28_T23_ACTION_MARGIN_TRANSFORM_CONTRACT"
        ),
        "t22_cpu_restore_pipeline_green": (
            t22["status"]
            == "PREREGISTERED_T22_CORRECTED_ONE_UPDATE_CPU_SMOKE"
        ),
        "source_checkpoint_and_graphs_present": all(
            Path(item["path"]).exists() for item in assets.values()
        ),
        "composed_source_inventory_complete": (
            len(inventory) >= 30
            and "playground/open_duck_mini_v2/joystick.py" in inventory
            and "playground/open_duck_mini_v2/runner.py" in inventory
        ),
        "t31_default_off_source_present": (
            "winner_t31_action_margin_trainthrough=False"
            in (
                COMPOSED
                / "playground/open_duck_mini_v2/joystick.py"
            ).read_text(encoding="utf-8")
        ),
        "runner_present": RUNNER.is_file(),
    }
    failed_checks = [name for name, passed in checks.items() if not passed]
    payload: dict[str, Any] = {
        "schema_version": (
            "open_duck.t31_action_margin_trainthrough_cpu_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T31_ACTION_MARGIN_TRAINTHROUGH_CPU_SMOKE"
            if not failed_checks
            else "HOLD_T31_ACTION_MARGIN_TRAINTHROUGH_CPU_PREREGISTRATION"
        ),
        "question": (
            "Can the exact T23 half checkpoint restore and take one finite "
            "PPO update while the final physical action is clipped to the "
            "frozen 0.98 margin inside the environment and export graph?"
        ),
        "selection_evidence": {
            "half_margin_green_cells": half_green_cells,
            "posthoc_wrapper_closed": True,
            "mechanism": (
                "Train through the exact final physical margin so state, "
                "reward, applied-target observation, and recurrent feedback "
                "all carry the realized bounded action."
            ),
            "reward_changes": 0,
            "new_scalar_search": False,
        },
        "transition": {
            "flag": "--winner_t31_action_margin_trainthrough",
            "default_off": True,
            "requires": "--winner_t19_support_trainthrough",
            "limit_equation": (
                "nextafter(float32(0.98), float32(0.0))"
            ),
            "insertion": (
                "After T19 support homeomorphism and external physical rate "
                "projection; before motor physics, applied-target observer, "
                "reward, last-action history, and inverse source-state update."
            ),
            "deployment": (
                "Append the same two-output float32 Clip transform after the "
                "complete frozen T24 graph."
            ),
        },
        "cpu_smoke": {
            "simulator_steps": 1024,
            "ppo_envs": 4,
            "exports": [0, 1024],
            "restore": "T23_SUPPORT_HALF step 1003520",
            "checks": [
                "CPU topology remap and source restore exact",
                "step-zero raw/context/pre-margin/final hashes exact",
                "environment command includes the default-off T31 flag",
                "both final graphs enforce the margin and exact feedback",
                "all policy and critic leaves update and remain finite",
                "reward metric finite",
                "no formal behavior, hosted compute, or robot access",
            ],
        },
        "playground": {
            "path": str(COMPOSED.resolve()),
            "python_inventory": inventory,
            "python_inventory_sha256": hashlib.sha256(
                json.dumps(
                    inventory,
                    separators=(",", ":"),
                    sort_keys=True,
                ).encode()
            ).hexdigest(),
        },
        "sources": sources,
        "assets": assets,
        "checks": checks,
        "failed_checks": failed_checks,
        "decision_rule": {
            "pass": (
                "Authorize only a separate hosted-continuation "
                "preregistration. Do not launch hosted compute."
            ),
            "fail": (
                "Close T31 without hosted training or behavior evaluation."
            ),
        },
        "authority": {
            "execute_1024_cpu_steps": not failed_checks,
            "hosted_preregistration": False,
            "hosted_training": False,
            "behavior_evaluation": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    payload["preregistered_contract_sha256"] = canonical_sha256(payload)
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# T31 action-margin train-through CPU preregistration",
                "",
                f"status: `{payload['status']}`",
                "",
                f"- Frozen feasible half cells: `{half_green_cells}/24`",
                "- CPU simulator steps: `1,024`",
                "- Exports: `0 / 1,024`",
                "- Reward changes / hosted / robot: `0 / 0 / 0`",
                "",
                "Passing authorizes only a separate hosted-continuation "
                "preregistration. It does not authorize Colab, behavior "
                "selection, Gate 5, RDK-X5, robot, torque, or motion.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"failed_checks={failed_checks}")
    print(f"half_green_cells={half_green_cells}")
    print(
        "contract_sha256="
        f"{payload['preregistered_contract_sha256']}"
    )
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed_checks else 1


if __name__ == "__main__":
    raise SystemExit(main())
