#!/usr/bin/env python3
"""Run the preregistered T12 response-prefix negative-COM screen."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

from run_t6_corrected_robustness_screen import (
    behavior_row,
    classify_behavior,
    trace_summary,
)
from run_t8_state_coherent_handoff import (
    read_trace,
    state_handoff_summary,
)


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t12_response_prefix_com_preregistration.json"
RESULT = ANALYSIS / "t12_response_prefix_com_result.json"
MARKDOWN = ANALYSIS / "T12_RESPONSE_PREFIX_COM_RESULT_20260726.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


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


def verify_receipt(item: dict[str, Any], label: str) -> None:
    path = Path(item["path"])
    if (
        not path.is_file()
        or path.stat().st_size != item["bytes"]
        or sha256(path) != item["sha256"]
    ):
        raise RuntimeError(f"T12 frozen receipt changed: {label}={path}")


def load_prereg() -> dict[str, Any]:
    value = json.loads(PREREG.read_text(encoding="utf-8"))
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
        != "open_duck.t12_response_prefix_com_preregistration.v1"
        or value["status"]
        != "PREREGISTERED_T12_RESPONSE_PREFIX_COM_SCREEN"
        or canonical_sha256(basis)
        != value["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T12 preregistration identity changed")
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
            raise RuntimeError(f"T12 playground changed: {relative}")
    return value


def block_directory(
    root: Path,
    checkpoint_id: str,
    fit_id: str,
) -> Path:
    return root / checkpoint_id / fit_id


def run_block(
    prereg: dict[str, Any],
    checkpoint: dict[str, Any],
    fit_id: str,
    root: Path,
) -> dict[str, Any]:
    directory = block_directory(
        root, checkpoint["checkpoint_id"], fit_id
    )
    if directory.exists():
        raise FileExistsError(f"refusing to reuse T12 block: {directory}")
    traces = directory / "traces"
    traces.mkdir(parents=True)
    evaluation = directory / "evaluation.json"
    stdout = directory / "stdout.log"
    command = [
        sys.executable,
        str(ROOT / "tools" / "evaluate_t12_response_prefix_com.py"),
        "--policy",
        checkpoint["policy"]["path"],
        "--playground-root",
        prereg["playground"]["path"],
        "--fit",
        prereg["candidate"]["fits"][fit_id]["path"],
        "--reference-feature-table",
        prereg["candidate"]["reference"]["path"],
        "--calibrator",
        prereg["candidate"]["calibrator"]["path"],
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
        completed.stdout, encoding="utf-8", newline="\n"
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"T12 worker failed rc={completed.returncode}; "
            f"tail={completed.stdout[-8000:]}"
        )
    value = json.loads(evaluation.read_text(encoding="utf-8"))
    trace_paths = sorted(traces.glob("*.jsonl"))
    if len(trace_paths) != 3:
        raise RuntimeError("T12 worker did not produce three traces")
    return {
        "checkpoint_id": checkpoint["checkpoint_id"],
        "fit_id": fit_id,
        "command": command,
        "evaluation": receipt(evaluation),
        "stdout": receipt(stdout),
        "traces": [receipt(path) for path in trace_paths],
        "payload": value,
    }


def exact_com_readback(report: dict[str, Any] | None) -> bool:
    report = report or {}
    readback = report.get("readback") or {}
    return bool(
        report.get("enabled") is True
        and report.get("key") == "torso_com_offset_m"
        and report.get("value") == [-0.05, 0.0, 0.0]
        and readback.get("body_id") == 2
        and readback.get("body_name") == "trunk_assembly"
        and isinstance(readback.get("before"), list)
        and isinstance(readback.get("after"), list)
        and len(readback["before"]) == 3
        and len(readback["after"]) == 3
        and abs(
            float(readback["after"][0])
            - float(readback["before"][0])
            + 0.05
        )
        <= 1.0e-12
        and float(readback["after"][1])
        == float(readback["before"][1])
        and float(readback["after"][2])
        == float(readback["before"][2])
    )


def analyze_block(
    prereg: dict[str, Any],
    block: dict[str, Any],
) -> dict[str, Any]:
    value = block["payload"]
    expected_inputs = {
        "commands_x_m_s": [0.074, 0.077, 0.08],
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
            "torso_com_offset_m": [-0.05, 0.0, 0.0]
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
            behavior_row(run), prereg["behavior_contract"]
        )
        protection = trace_summary(
            path, prereg["protection_contract"]
        )
        handoff = state_handoff_summary(run, records)
        trace_valid = bool(
            protection["ticks_contiguous_from_zero"]
            and protection["rows"] == behavior["samples"]
            and sha256(path) == trace_receipt["sha256"]
        )
        readback_exact = exact_com_readback(
            run.get("dynamics_override")
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
        )
        cells.append(
            {
                "checkpoint_id": block["checkpoint_id"],
                "fit_id": block["fit_id"],
                "command_x_m_s": float(run["command_x"]),
                "behavior": behavior,
                "protection": protection,
                "handoff": handoff,
                "trace": trace_receipt,
                "trace_valid": trace_valid,
                "com_readback_exact": readback_exact,
                "cell_green": green,
            }
        )
    return {
        "checkpoint_id": block["checkpoint_id"],
        "fit_id": block["fit_id"],
        "worker_inputs_exact": inputs_exact,
        "execution_platform": (value.get("execution") or {}).get(
            "platform"
        ),
        "cells": cells,
        "block_green": bool(
            inputs_exact
            and len(cells) == 3
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
        raise SystemExit("T12 requires --execute")
    if RESULT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T12 result")
    root = args.cache_root.resolve()
    if root.exists():
        raise FileExistsError(f"refusing to reuse T12 cache: {root}")
    root.mkdir(parents=True)
    prereg = load_prereg()
    blocks = []
    for checkpoint in prereg["candidate"]["checkpoints"]:
        for fit_id in prereg["candidate"]["fits"]:
            block = run_block(prereg, checkpoint, fit_id, root)
            blocks.append(analyze_block(prereg, block))
    cells = [cell for block in blocks for cell in block["cells"]]
    checks = {
        "matrix_exact": (
            len(blocks) == 4
            and len(cells) == 12
            and all(len(block["cells"]) == 3 for block in blocks)
        ),
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
        "all_cells_green": all(cell["cell_green"] for cell in cells),
        "optimizer_steps_zero": True,
        "hosted_compute_zero": True,
        "robot_access_zero": True,
    }
    failed = [name for name, passed in checks.items() if not passed]
    passed = not failed
    basis = {
        "schema_version": "open_duck.t12_response_prefix_com_result.v1",
        "status": (
            "PASS_T12_RESPONSE_PREFIX_COM_SCREEN"
            if passed
            else "HOLD_T12_RESPONSE_PREFIX_COM_SCREEN"
        ),
        "decision": (
            "EARN_RESPONSE_PREFIX_FULL_R2_PREREGISTRATION"
            if passed
            else "CLOSE_RESPONSE_PREFIX_STATE_PREPARATION"
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "blocks": blocks,
        "summary": {
            "green_cells": sum(
                int(cell["cell_green"]) for cell in cells
            ),
            "total_cells": len(cells),
            "minimum_mean_vx_m_s": min(
                float(cell["behavior"]["mean_local_vx_m_s"])
                for cell in cells
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
        },
        "execution": {
            "optimizer_steps": 0,
            "hosted_or_colab_compute": 0,
            "simulator_behavior_cells": 12,
            "robot_or_rdk_access": 0,
        },
    }
    value = {**basis, "result_sha256": canonical_sha256(basis)}
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T12 response-prefix negative-COM result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Green cells: `{value['summary']['green_cells']}/12`\n"
        f"- Minimum mean vx: "
        f"`{value['summary']['minimum_mean_vx_m_s']:.9g} m/s`\n"
        f"- Worst tracking p95: "
        f"`{value['summary']['worst_tracking_p95_rad']:.9g} rad`\n"
        f"- Failed checks: `{failed}`\n"
        "- Optimizer/hosted/robot execution: `0/0/0`\n"
        f"- Canonical SHA-256: `{value['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"green_cells={value['summary']['green_cells']}/12")
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
