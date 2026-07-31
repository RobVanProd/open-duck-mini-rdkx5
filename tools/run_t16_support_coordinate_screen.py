#!/usr/bin/env python3
"""Run T16's preregistered support-coordinate behavior screen."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

import numpy as np

from run_t6_corrected_robustness_screen import (
    behavior_row,
    classify_behavior,
    trace_summary,
)
from run_t8_state_coherent_handoff import (
    read_trace,
    state_handoff_summary,
)
from t16_support_coordinate_onnx import (
    SUPPORT_ACTION,
    sha256,
    verify_wrapper,
    wrap_support_coordinate,
)


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREGISTRATION = (
    ANALYSIS / "t16_support_coordinate_preregistration.json"
)
RESULT = ANALYSIS / "t16_support_coordinate_result.json"
MARKDOWN = ANALYSIS / "T16_SUPPORT_COORDINATE_RESULT_20260726.md"


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def verify_receipt(value: dict[str, Any], label: str) -> None:
    path = Path(value["path"])
    if (
        not path.is_file()
        or path.stat().st_size != value["bytes"]
        or sha256(path) != value["sha256"]
    ):
        raise RuntimeError(f"T16 frozen receipt changed: {label}={path}")


def load_preregistration() -> dict[str, Any]:
    value = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    basis = {
        key: value[key]
        for key in (
            "schema_version",
            "status",
            "question",
            "causal_basis",
            "sources",
            "playground",
            "candidate",
            "transform",
            "matrix",
            "handoff_contract",
            "behavior_contract",
            "protection_contract",
            "decision_rule",
            "authority",
            "execution_now",
        )
    }
    if (
        value["schema_version"]
        != "open_duck.t16_support_coordinate_preregistration.v1"
        or value["status"]
        != "PREREGISTERED_T16_SUPPORT_COORDINATE_SCREEN"
        or canonical_sha256(basis)
        != value["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T16 preregistration identity changed")
    for name, item in value["sources"].items():
        verify_receipt(item, name)
    for checkpoint in value["candidate"]["checkpoints"]:
        verify_receipt(checkpoint["policy"], checkpoint["checkpoint_id"])
    for fit_id, item in value["candidate"]["fits"].items():
        verify_receipt(item, fit_id)
    verify_receipt(value["candidate"]["calibrator"], "calibrator")
    verify_receipt(value["candidate"]["reference"], "reference")
    playground = Path(value["playground"]["path"])
    for relative, expected in value["playground"][
        "required_file_sha256"
    ].items():
        if sha256(playground / relative) != expected:
            raise RuntimeError(f"T16 playground changed: {relative}")
    return value


def run_block(
    prereg: dict[str, Any],
    checkpoint: dict[str, Any],
    wrapped: Path,
    fit_id: str,
    condition: dict[str, Any],
    root: Path,
) -> dict[str, Any]:
    directory = (
        root
        / "blocks"
        / checkpoint["checkpoint_id"]
        / fit_id
        / condition["id"]
    )
    if directory.exists():
        raise FileExistsError(f"refusing to reuse T16 block: {directory}")
    directory.mkdir(parents=True)
    traces = directory / "traces"
    evaluation = directory / "evaluation.json"
    stdout = directory / "stdout.log"
    command = [
        sys.executable,
        str(ROOT / "tools" / "evaluate_t16_support_coordinate.py"),
        "--policy",
        str(wrapped),
        "--playground-root",
        prereg["playground"]["path"],
        "--fit",
        prereg["candidate"]["fits"][fit_id]["path"],
        "--reference-feature-table",
        prereg["candidate"]["reference"]["path"],
        "--calibrator",
        prereg["candidate"]["calibrator"]["path"],
        "--com-x",
        str(condition["torso_com_x_m"]),
        "--trace-dir",
        str(traces),
        "--output-json",
        str(evaluation),
    ]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=3600,
    )
    stdout.write_text(
        completed.stdout,
        encoding="utf-8",
        newline="\n",
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"T16 worker failed rc={completed.returncode}; "
            f"tail={completed.stdout[-8000:]}"
        )
    payload = json.loads(evaluation.read_text(encoding="utf-8"))
    trace_paths = sorted(traces.glob("*.jsonl"))
    if len(trace_paths) != 4:
        raise RuntimeError("T16 worker did not produce four traces")
    return {
        "checkpoint_id": checkpoint["checkpoint_id"],
        "fit_id": fit_id,
        "condition_id": condition["id"],
        "torso_com_x_m": condition["torso_com_x_m"],
        "command": command,
        "evaluation": receipt(evaluation),
        "stdout": receipt(stdout),
        "traces": [receipt(path) for path in trace_paths],
        "payload": payload,
    }


def exact_com_readback(
    report: dict[str, Any] | None,
    expected_x_m: float,
) -> bool:
    report = report or {}
    readback = report.get("readback") or {}
    before = readback.get("before")
    after = readback.get("after")
    return bool(
        report.get("enabled") is True
        and report.get("key") == "torso_com_offset_m"
        and report.get("value") == [expected_x_m, 0.0, 0.0]
        and readback.get("body_id") == 2
        and readback.get("body_name") == "trunk_assembly"
        and isinstance(before, list)
        and isinstance(after, list)
        and len(before) == len(after) == 3
        and abs(float(after[0]) - float(before[0]) - expected_x_m)
        <= 1.0e-12
        and float(after[1]) == float(before[1])
        and float(after[2]) == float(before[2])
    )


def support_actions_exact(records: list[dict[str, Any]]) -> bool:
    actions = np.asarray([row["action"] for row in records], dtype=np.float32)
    return bool(
        actions.shape == (len(records), 14)
        and np.array_equal(
            actions,
            np.broadcast_to(SUPPORT_ACTION, actions.shape),
        )
    )


def analyze_block(
    prereg: dict[str, Any],
    block: dict[str, Any],
) -> dict[str, Any]:
    value = block["payload"]
    expected_inputs = {
        "commands_x_m_s": [0.0, 0.074, 0.077, 0.08],
        "seed": 167931544,
        "duration_s": 12.0,
        "calibration_ticks": 250,
        "home_return_ticks": 0,
        "preserve_handoff_state": True,
        "expected_observation_dim": 115,
        "expected_action_dim": 14,
        "policy_state_input_names": ["h_in", "previous_action"],
        "policy_state_output_names": ["h_out", "previous_action_out"],
        "policy_context_input_name": "calibration_context",
        "policy_graph_authoritative_output": True,
        "policy_applied_target_observation": True,
        "reference_start_phase": 0,
        "eval_dynamics_override": {
            "torso_com_offset_m": [
                block["torso_com_x_m"],
                0.0,
                0.0,
            ]
        },
    }
    inputs_exact = value.get("inputs") == expected_inputs
    traces = {
        Path(item["path"]).name: item for item in block["traces"]
    }
    cells = []
    for run in value["runs"]:
        trace_name = Path(run["trace_jsonl"]).name
        trace_receipt = traces[trace_name]
        path = Path(trace_receipt["path"])
        records = read_trace(path)
        behavior = classify_behavior(
            behavior_row(run),
            prereg["behavior_contract"],
        )
        protection = trace_summary(
            path,
            prereg["protection_contract"],
        )
        handoff = state_handoff_summary(run, records)
        trace_valid = bool(
            protection["ticks_contiguous_from_zero"]
            and protection["rows"] == behavior["samples"]
            and sha256(path) == trace_receipt["sha256"]
        )
        readback_exact = exact_com_readback(
            run.get("dynamics_override"),
            block["torso_com_x_m"],
        )
        x0 = float(run["command_x"]) == 0.0
        x0_support_exact = (
            support_actions_exact(records) if x0 else None
        )
        green = bool(
            trace_valid
            and behavior["core_pass"]
            and behavior["replacement_quality_pass"]
            and protection["duration_protection_pass"]
            and protection[
                "maximum_full_measured_vector_excess_rad_s"
            ]
            == 0.0
            and handoff["all_checks_pass"]
            and readback_exact
            and (not x0 or x0_support_exact)
        )
        cells.append(
            {
                "checkpoint_id": block["checkpoint_id"],
                "fit_id": block["fit_id"],
                "condition_id": block["condition_id"],
                "torso_com_x_m": block["torso_com_x_m"],
                "command_x_m_s": float(run["command_x"]),
                "behavior": behavior,
                "protection": protection,
                "handoff": handoff,
                "trace": trace_receipt,
                "trace_valid": trace_valid,
                "com_readback_exact": readback_exact,
                "x0_support_action_exact": x0_support_exact,
                "cell_green": green,
            }
        )
    return {
        "checkpoint_id": block["checkpoint_id"],
        "fit_id": block["fit_id"],
        "condition_id": block["condition_id"],
        "torso_com_x_m": block["torso_com_x_m"],
        "worker_inputs_exact": inputs_exact,
        "execution_platform": (value.get("execution") or {}).get(
            "platform"
        ),
        "cells": cells,
        "block_green": bool(
            inputs_exact
            and len(cells) == 4
            and all(item["cell_green"] for item in cells)
        ),
        "raw": {
            key: block[key]
            for key in ("evaluation", "stdout", "traces", "command")
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-root", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise SystemExit("T16 requires --execute")
    if RESULT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T16 result")
    root = args.cache_root.resolve()
    if root.exists():
        raise FileExistsError(f"refusing to reuse T16 cache: {root}")
    root.mkdir(parents=True)
    prereg = load_preregistration()

    wrappers = []
    wrapped_paths: dict[str, Path] = {}
    for checkpoint in prereg["candidate"]["checkpoints"]:
        wrapped = (
            root
            / "wrapped"
            / checkpoint["checkpoint_id"]
            / "support_coordinate.onnx"
        )
        wrapper = wrap_support_coordinate(
            Path(checkpoint["policy"]["path"]),
            wrapped,
        )
        verification = verify_wrapper(
            Path(checkpoint["policy"]["path"]),
            wrapped,
            cases=prereg["transform"]["contract_cases"],
            seed=prereg["transform"]["contract_seed"],
        )
        wrappers.append(
            {
                "checkpoint_id": checkpoint["checkpoint_id"],
                "wrapper": wrapper,
                "verification": verification,
            }
        )
        wrapped_paths[checkpoint["checkpoint_id"]] = wrapped

    blocks = []
    for checkpoint in prereg["candidate"]["checkpoints"]:
        wrapped = wrapped_paths[checkpoint["checkpoint_id"]]
        for fit_id in prereg["candidate"]["fits"]:
            for condition in prereg["matrix"]["conditions"]:
                block = run_block(
                    prereg,
                    checkpoint,
                    wrapped,
                    fit_id,
                    condition,
                    root,
                )
                blocks.append(analyze_block(prereg, block))

    cells = [cell for block in blocks for cell in block["cells"]]
    wrapper_contract_green = all(
        row["verification"]["maximum_action_error"] == 0.0
        and row["verification"]["maximum_previous_action_error"] == 0.0
        and row["verification"]["maximum_hidden_error"] == 0.0
        and row["verification"][
            "previous_action_out_equals_action_bit_exact"
        ]
        and row["verification"][
            "x0_output_equals_support_action_bit_exact"
        ]
        and row["verification"]["inputs_exact"]
        and row["verification"]["outputs_exact"]
        and row["verification"]["provider"] == "CPUExecutionProvider"
        for row in wrappers
    )
    checks = {
        "matrix_exact": (
            len(blocks) == 8
            and len(cells) == 32
            and all(len(block["cells"]) == 4 for block in blocks)
        ),
        "wrapper_contract_green": wrapper_contract_green,
        "cpu_only": all(
            block["execution_platform"] == "cpu" for block in blocks
        ),
        "worker_inputs_exact": all(
            block["worker_inputs_exact"] for block in blocks
        ),
        "all_com_readbacks_exact": all(
            cell["com_readback_exact"] for cell in cells
        ),
        "all_handoff_chains_exact": all(
            cell["handoff"]["all_checks_pass"] for cell in cells
        ),
        "all_eight_x0_cells_retain_support_exactly": (
            sum(cell["command_x_m_s"] == 0.0 for cell in cells) == 8
            and all(
                cell["x0_support_action_exact"]
                for cell in cells
                if cell["command_x_m_s"] == 0.0
            )
        ),
        "all_cells_green": all(cell["cell_green"] for cell in cells),
        "optimizer_steps_zero": True,
        "hosted_compute_zero": True,
        "robot_access_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    basis = {
        "schema_version": "open_duck.t16_support_coordinate_result.v1",
        "status": (
            "PASS_T16_SUPPORT_COORDINATE_SCREEN"
            if passed
            else "HOLD_T16_SUPPORT_COORDINATE_SCREEN"
        ),
        "decision": (
            "EARN_SUPPORT_COORDINATE_FULL_R2_PREREGISTRATION"
            if passed
            else "CLOSE_EXACT_SUPPORT_COORDINATE_CONJUGATION"
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "wrappers": wrappers,
        "blocks": blocks,
        "summary": {
            "green_cells": sum(
                int(cell["cell_green"]) for cell in cells
            ),
            "total_cells": len(cells),
            "green_by_condition": {
                condition["id"]: sum(
                    int(cell["cell_green"])
                    for cell in cells
                    if cell["condition_id"] == condition["id"]
                )
                for condition in prereg["matrix"]["conditions"]
            },
            "minimum_moving_mean_vx_m_s": min(
                float(cell["behavior"]["mean_local_vx_m_s"])
                for cell in cells
                if cell["command_x_m_s"] > 0.0
            ),
            "worst_tracking_p95_rad": max(
                float(cell["behavior"]["pitch_tracking_p95_rad"])
                for cell in cells
            ),
            "worst_rate_excess_rad_s": max(
                float(
                    cell["protection"][
                        "maximum_full_measured_vector_excess_rad_s"
                    ]
                )
                for cell in cells
            ),
            "worst_action_saturation_pct": max(
                float(cell["behavior"]["action_saturation_pct"])
                for cell in cells
            ),
        },
        "execution": {
            "optimizer_steps": 0,
            "hosted_or_colab_compute": 0,
            "simulator_behavior_cells": 32,
            "robot_or_rdk_access": 0,
        },
    }
    value = {**basis, "result_sha256": canonical_sha256(basis)}
    RESULT.write_text(
        json.dumps(
            value,
            allow_nan=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T16 support-coordinate behavior result",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                (
                    "- Green cells: "
                    f"`{value['summary']['green_cells']}/"
                    f"{value['summary']['total_cells']}`"
                ),
                (
                    "- Green by condition: "
                    f"`{value['summary']['green_by_condition']}`"
                ),
                (
                    "- Minimum moving vx: "
                    f"`{value['summary']['minimum_moving_mean_vx_m_s']:.9g} m/s`"
                ),
                (
                    "- Worst tracking p95: "
                    f"`{value['summary']['worst_tracking_p95_rad']:.9g} rad`"
                ),
                f"- Failed checks: `{failed}`",
                "- Optimizer/hosted/robot execution: `0/0/0`",
                f"- Result SHA-256: `{value['result_sha256']}`",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(
        "green_cells="
        f"{value['summary']['green_cells']}/{value['summary']['total_cells']}"
    )
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
