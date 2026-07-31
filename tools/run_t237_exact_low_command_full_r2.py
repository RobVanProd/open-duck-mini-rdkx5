#!/usr/bin/env python3
"""Run T234B's sequential full R2 matrix one condition per invocation."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t237_exact_low_command_full_r2_preregistration.json"
RESULT = ANALYSIS / "t237_exact_low_command_full_r2_result.json"
MARKDOWN = ANALYSIS / "T237_EXACT_LOW_COMMAND_FULL_R2_RESULT_20260730.md"
CACHE = Path(
    "D:/CodexArtifacts/open-duck-policy/t237_exact_low_command_full_r2_v1"
)
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t237_exact_low_command_full_r2_engine_v1"
)
sys.path.insert(0, str(ROOT / "tools"))
from run_t136_static_calibration_router_transform import (  # noqa: E402
    canonical_sha256,
    receipt,
)


def load_engine():
    path = ROOT / "tools" / "run_t225_global_plateau_full_r2.py"
    spec = importlib.util.spec_from_file_location("t237_engine", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen sequential R2 engine")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_preregistration(engine) -> dict[str, Any]:
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        value.get("status")
        != "PREREGISTERED_T237_EXACT_LOW_COMMAND_FULL_R2"
        or value.get("failed_checks")
        or engine.canonical_sha256(basis)
        != value.get("preregistered_contract_sha256")
    ):
        raise RuntimeError("T237 preregistration changed")
    for label, item in value["repository_inputs"].items():
        engine.verify_receipt(item, label)
    for label, item in value["frozen_inputs"].items():
        engine.verify_receipt(item, label)
    for policy in value["policies"]:
        engine.verify_receipt(policy, f"policy:{policy['checkpoint_id']}")
    for fit in value["fits"]:
        engine.verify_receipt(fit, f"fit:{fit['fit_id']}")
    engine.verify_receipt(value["calibrator"], "calibrator")
    engine.verify_receipt(value["reference_feature_table"], "reference")
    engine.verify_receipt(
        value["playground"]["manifest"], "playground_manifest"
    )
    plan = engine.matrix_plan(
        value["conditions"],
        value["policies"],
        value["fits"],
        value["commands_x_m_s"],
        int(value["seed"]),
    )
    if (
        len(plan) != value["matrix"]["maximum_cells"]
        or engine.canonical_sha256(plan) != value["matrix"]["plan_sha256"]
    ):
        raise RuntimeError("T237 matrix plan changed")
    return value


def write_progress(
    prereg: dict[str, Any],
    conditions: list[dict[str, Any]],
    *,
    cache_hits: int,
    new_blocks: int,
    wall_seconds: float,
) -> Path:
    value = {
        "schema_version": (
            "open_duck.t237_exact_low_command_full_r2_progress.v1"
        ),
        "status": "IN_PROGRESS_T237_EXACT_LOW_COMMAND_FULL_R2",
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "completed_conditions": len(conditions),
        "expected_conditions": len(prereg["conditions"]),
        "conditions": conditions,
        "cache_hits": cache_hits,
        "new_blocks": new_blocks,
        "wall_seconds_this_invocation": wall_seconds,
        "selection_or_decision_made": False,
        "hosted_compute_units": 0,
        "robot_or_rdk_access": 0,
    }
    value["progress_sha256"] = canonical_sha256(value)
    path = CACHE / "progress.json"
    path.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return path


def write_markdown(value: dict[str, Any]) -> None:
    lines = [
        "# T237 exact low-command full R2 result",
        "",
        f"- Status: `{value['status']}`",
        f"- Decision: `{value['decision']}`",
        f"- Completed conditions: "
        f"`{value['summary']['completed_conditions']}/20`",
        f"- Green cells: "
        f"`{value['summary']['green_cells']}/"
        f"{value['summary']['completed_cells']}`",
        f"- First failure: "
        f"`{value['summary']['first_failed_condition']}`",
        "- Training/hosted/robot: `0/0/0`",
        "",
        "| index | condition | green | tracking p95 | min vx | overcurrent run | overload run |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    for item in value["conditions"]:
        lines.append(
            f"| {item['condition_index']} | `{item['condition_id']}` | "
            f"{item['green_cells']}/{item['cells']} | "
            f"{item['worst_tracking_p95_rad']:.9f} | "
            f"{item['minimum_moving_vx_m_s']:.9f} | "
            f"{item['worst_strict_overcurrent_run_ticks']} | "
            f"{item['worst_strict_overload_run_ticks']} |"
        )
    MARKDOWN.write_text(
        "\n".join(lines) + "\n", encoding="utf-8", newline="\n"
    )


def finalize(inner_path: Path) -> int:
    inner = json.loads(inner_path.read_text(encoding="utf-8"))
    complete = bool(inner["summary"]["matrix_complete"])
    all_green = bool(inner["summary"]["all_twenty_conditions_green"])
    basis = {
        **{
            key: value
            for key, value in inner.items()
            if key != "result_sha256"
        },
        "schema_version": (
            "open_duck.t237_exact_low_command_full_r2_result.v1"
        ),
        "status": (
            "PASS_T237_EXACT_LOW_COMMAND_FULL_R2"
            if all_green
            else "HOLD_T237_EXACT_LOW_COMMAND_FULL_R2"
        ),
    }
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis["decision"] = (
        prereg["decision_rule"]["pass_decision"]
        if all_green
        else prereg["decision_rule"]["fail_decision"]
    )
    basis["cache_root"] = str(CACHE)
    value = {**basis, "result_sha256": canonical_sha256(basis)}
    if not complete and all_green:
        raise RuntimeError("T237 impossible incomplete green result")
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    write_markdown(value)
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if all_green else 1


def main() -> int:
    if RESULT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T237 result")
    engine = load_engine()
    WORK.mkdir(parents=True, exist_ok=True)
    engine.PREREG = PREREG
    engine.RESULT = WORK / "inner_result.json"
    engine.MARKDOWN = WORK / "inner_result.md"
    engine.CACHE = CACHE
    engine.load_preregistration = lambda: load_preregistration(engine)
    engine.write_progress = write_progress
    engine.write_markdown = lambda value: None
    return_code = int(engine.main())
    if engine.RESULT.is_file():
        return finalize(engine.RESULT)
    progress = CACHE / "progress.json"
    if not progress.is_file():
        raise RuntimeError(
            f"T237 engine returned {return_code} without progress/result"
        )
    value = json.loads(progress.read_text(encoding="utf-8"))
    print("IN_PROGRESS_T237_EXACT_LOW_COMMAND_FULL_R2")
    print(
        f"completed_conditions={value['completed_conditions']}/"
        f"{value['expected_conditions']}"
    )
    print(f"progress={progress}")
    print(f"progress_sha256={receipt(progress)['sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
