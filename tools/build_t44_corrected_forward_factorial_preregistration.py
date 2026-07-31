#!/usr/bin/env python3
"""Freeze T44's corrected x=.080 forward actor-block factorial."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T43_PREREG = (
    ANALYSIS / "t43_forward_actor_block_factorial_preregistration.json"
)
T43_INVALIDATION = ANALYSIS / "t43_worker_contract_invalidation.json"
RUNNER = ROOT / "tools" / "run_t44_corrected_forward_factorial.py"
WORKER = ROOT / "tools" / "evaluate_t44_t43_x008_causal_cell.py"
OUTPUT = (
    ANALYSIS / "t44_corrected_forward_factorial_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T44_CORRECTED_FORWARD_FACTORIAL_PREREGISTRATION_20260728.md"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


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


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T44 prereg: {path}")
    t43 = json.loads(T43_PREREG.read_text(encoding="utf-8"))
    invalidation = json.loads(
        T43_INVALIDATION.read_text(encoding="utf-8")
    )
    worker_text = WORKER.read_text(encoding="utf-8")
    variants = t43["variants"]
    checks = {
        "t43_invalidation_green_and_earned_t44": (
            invalidation["status"]
            == "PASS_T43_ZERO_CELL_WORKER_CONTRACT_INVALIDATION"
            and invalidation["decision"]
            == "CLOSE_T43_ZERO_WEIGHT_NO_RETRY_"
            "EARN_T44_CORRECTED_X008_FACTORIAL_PREREGISTRATION"
        ),
        "t43_formal_behavior_cells_zero": (
            invalidation["classification"]["formal_behavior_cells"] == 0
        ),
        "corrected_worker_exact_x0p080": (
            "worker.FORMAL_COMMANDS = (0.08,)" in worker_text
            and "0.077" not in worker_text
        ),
        "exact_same_three_assets": (
            len(variants) == 3
            and all(
                sha256(Path(item["policy"]["path"]))
                == item["policy"]["sha256"]
                for item in variants
            )
        ),
        "same_cell_except_corrected_worker": (
            t43["cell"]["condition"]["id"] == "JOINT_FRICTIONLOSS_LO"
            and t43["cell"]["fit_id"] == "p30"
            and t43["cell"]["command_x_m_s"] == 0.08
            and t43["cell"]["seed"] == 167931544
            and t43["cell"]["duration_s"] == 12.0
        ),
        "all_support_assets_exact": all(
            sha256(Path(item["path"])) == item["sha256"]
            for item in (
                t43["fit"],
                t43["calibrator"],
                t43["reference_feature_table"],
            )
        ),
        "runner_and_worker_present": RUNNER.is_file() and WORKER.is_file(),
        "behavior_cells_zero": True,
        "training_or_colab_zero": True,
        "robot_or_rdk_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t44_corrected_forward_factorial_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T44_CORRECTED_FORWARD_ACTOR_FACTORIAL"
            if not failed
            else "HOLD_T44_CORRECTED_FORWARD_FACTORIAL_PREREGISTRATION"
        ),
        "question": t43["question"],
        "correction": {
            "only_change": "formal_worker_command_x0p077_to_x0p080",
            "t43_policy_assets_reused_exact": True,
            "t43_policy_outcomes_reused": False,
        },
        "groups": t43["groups"],
        "variants": variants,
        "execution_order": t43["execution_order"],
        "cell": t43["cell"],
        "fit": t43["fit"],
        "calibrator": t43["calibrator"],
        "reference_feature_table": t43["reference_feature_table"],
        "playground": t43["playground"],
        "support_handoff": t43["support_handoff"],
        "behavior_contract": t43["behavior_contract"],
        "protection_contract": t43["protection_contract"],
        "decision_rule": {
            **t43["decision_rule"],
            "one_group_pass_decision": (
                "EARN_T45_SELECTED_ONE_BLOCK_UNIFORM_TRANSFORM_"
                "PREREGISTRATION"
            ),
            "no_retry": True,
        },
        "checks": checks,
        "failed_checks": failed,
        "frozen_inputs": {
            "t43_preregistration": receipt(T43_PREREG),
            "t43_invalidation": receipt(T43_INVALIDATION),
            "runner": receipt(RUNNER),
            "worker": receipt(WORKER),
        },
        "execution_now": {
            "formal_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_three_cpu_cells": not failed,
            "uniform_transform_preregistration": False,
            "policy_promotion": False,
            "training": False,
            "colab": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T44 corrected forward actor-block factorial",
                "",
                f"- Status: `{value['status']}`",
                "- Only correction: formal worker command `.077 → .080`",
                "- Policy assets: exact T43 hashes",
                "- Cells: three, all required, no early stop",
                "- T43 outcomes reused: `NO`",
                "- Training/Colab/Gate 5/robot: `0/0/0/0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(
        "contract_sha256="
        f"{value['preregistered_contract_sha256']}"
    )
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
