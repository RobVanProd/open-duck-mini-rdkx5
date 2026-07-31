#!/usr/bin/env python3
"""Run T192's one exact half-to-final head-switch behavior cell."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t192_one_period_head_switch_preregistration.json"
RESULT = ANALYSIS / "t192_one_period_head_switch_result.json"
MARKDOWN = ANALYSIS / "T192_ONE_PERIOD_HEAD_SWITCH_RESULT_20260730.md"
CACHE = Path(
    "D:/CodexArtifacts/open-duck-policy/t192_one_period_head_switch_v1"
)
sys.path.insert(0, str(ROOT / "tools"))
from run_t27_t23_robustness_matrix import (  # noqa: E402
    block_contract,
    canonical_sha256,
    extract_block,
    receipt,
    verify_receipt,
)


def verify(value: Mapping[str, Any], label: str) -> None:
    verify_receipt(value, label)


def read_rows(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    if RESULT.exists() or MARKDOWN.exists() or CACHE.exists():
        raise FileExistsError("refusing to overwrite T192 output")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T192 execution requires clean worktree")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"] != "PREREGISTERED_T192_ONE_PERIOD_HEAD_SWITCH"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T192 preregistration changed")
    for label, item in prereg["frozen_inputs"].items():
        verify(item, f"frozen:{label}")
    for label, item in prereg["repository_inputs"].items():
        verify(item, f"repository:{label}")
    for label, item in (
        ("policy", prereg["policy"]),
        ("switch_policy", prereg["switch_policy"]),
        ("fit", prereg["fit"]),
        ("calibrator", prereg["calibrator"]),
        ("reference", prereg["reference_feature_table"]),
        ("playground", prereg["playground"]["manifest"]),
        ("original_failure", prereg["original_failure_trace"]),
    ):
        verify(item, label)

    directory = (
        CACHE
        / "09_TORSO_COM_Y_NEG"
        / "T186_HALF_TO_FINAL_SWITCH"
        / "p31_34"
    )
    trace_dir = directory / "traces"
    trace_dir.mkdir(parents=True)
    trace = trace_dir / "x0.080_seed167931544_t186_half_to_final.jsonl"
    evaluation = directory / "evaluation.json"
    stdout = directory / "stdout.log"
    manifest_path = directory / "manifest.json"
    command = [
        sys.executable,
        prereg["repository_inputs"]["worker"]["path"],
        "--formal",
        "--policy",
        prereg["policy"]["path"],
        "--policy-sha256",
        prereg["policy"]["sha256"],
        "--switch-policy",
        prereg["switch_policy"]["path"],
        "--switch-policy-sha256",
        prereg["switch_policy"]["sha256"],
        "--switch-tick",
        str(prereg["switch_tick"]),
        "--playground-root",
        prereg["playground"]["path"],
        "--fit",
        prereg["fit"]["path"],
        "--reference-feature-table",
        prereg["reference_feature_table"]["path"],
        "--calibrator",
        prereg["calibrator"]["path"],
        "--calibrator-sha256",
        prereg["calibrator"]["sha256"],
        "--override-json",
        json.dumps(
            prereg["condition"]["override"],
            separators=(",", ":"),
            sort_keys=True,
        ),
        "--command",
        "0.08",
        "--seed",
        str(prereg["seed"]),
        "--duration-s",
        "12.0",
        "--trace-jsonl",
        str(trace),
        "--output-json",
        str(evaluation),
    ]
    environment = os.environ.copy()
    environment.update(
        {
            "CUDA_VISIBLE_DEVICES": "",
            "HIP_VISIBLE_DEVICES": "",
            "ROCR_VISIBLE_DEVICES": "",
            "JAX_PLATFORMS": "cpu",
            "JAX_PLATFORM_NAME": "cpu",
            "JAX_COMPILATION_CACHE_DIR": str(
                CACHE.parent / "jax_compilation_cache"
            ),
            "XLA_PYTHON_CLIENT_PREALLOCATE": "false",
        }
    )
    started = time.time()
    with stdout.open("w", encoding="utf-8") as stream:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            env=environment,
            stdout=stream,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=2400,
            check=False,
        )
    if (
        completed.returncode != 0
        or not evaluation.is_file()
        or not trace.is_file()
    ):
        raise RuntimeError(
            f"T192 worker failed: returncode={completed.returncode}; "
            f"log={stdout}"
        )

    contract = {
        **block_contract(
            prereg,
            prereg["condition"],
            prereg["policy"],
            prereg["fit"],
        ),
        "switch_policy": {
            "checkpoint_id": prereg["switch_policy"]["checkpoint_id"],
            "step": prereg["switch_policy"]["step"],
            "sha256": prereg["switch_policy"]["sha256"],
        },
        "switch_tick": prereg["switch_tick"],
    }
    manifest = {
        "schema_version": "open_duck.t192_head_switch_block.v1",
        "block_contract": contract,
        "block_contract_sha256": canonical_sha256(contract),
        "command": command,
        "evaluation": receipt(evaluation),
        "stdout": receipt(stdout),
        "traces": [receipt(trace)],
    }
    manifest_path.write_text(
        json.dumps(manifest, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    block = extract_block(prereg, prereg["condition"], manifest)
    if len(block["cells"]) != 1:
        raise RuntimeError("T192 worker did not produce exactly one cell")
    cell = block["cells"][0]

    original_rows = read_rows(Path(prereg["original_failure_trace"]["path"]))
    hybrid_rows = read_rows(trace)
    prefix_rows = min(prereg["switch_tick"], len(hybrid_rows))
    prefix_exact = (
        prefix_rows == prereg["switch_tick"]
        and len(original_rows) >= prefix_rows
        and all(
            all(
                hybrid_rows[index].get(key) == value
                for key, value in original_rows[index].items()
            )
            for index in range(prefix_rows)
        )
    )
    switch_schedule_exact = all(
        bool(row.get("policy_switch_active"))
        is (int(row["tick"]) >= prereg["switch_tick"])
        and row.get("policy_session_role")
        == (
            "switch"
            if int(row["tick"]) >= prereg["switch_tick"]
            else "primary"
        )
        for row in hybrid_rows
    )
    switch_executed = (
        len(hybrid_rows) > prereg["switch_tick"]
        and bool(hybrid_rows[prereg["switch_tick"]]["policy_switch_active"])
    )
    state_continuity = False
    if switch_executed:
        before = hybrid_rows[prereg["switch_tick"] - 1][
            "policy_state_output"
        ]
        after = hybrid_rows[prereg["switch_tick"]]["policy_state_input"]
        state_continuity = (
            before["h_out"] == after["h_in"]
            and before["previous_action_out"] == after["previous_action"]
        )
    integrity_checks = {
        "worker_inputs_exact": block["worker_inputs_exact"],
        "pre_switch_520_rows_exact_to_frozen_failure": prefix_exact,
        "switch_schedule_exact": switch_schedule_exact,
        "switch_executed": switch_executed,
        "recurrent_state_continuity_at_switch": state_continuity,
        "trace_receipt_exact": receipt(trace) == manifest["traces"][0],
    }
    integrity_green = all(integrity_checks.values())
    behavior_green = bool(cell["cell_green"])
    status = (
        "PASS_T192_ONE_PERIOD_HEAD_SWITCH_FEASIBILITY"
        if integrity_green and behavior_green
        else "HOLD_T192_ONE_PERIOD_HEAD_SWITCH_FEASIBILITY"
    )
    if not integrity_green:
        decision = prereg["decision_rule"]["integrity_fail"]
    elif behavior_green:
        decision = prereg["decision_rule"]["pass"]
    else:
        decision = prereg["decision_rule"]["behavior_fail"]
    basis_result: dict[str, Any] = {
        "schema_version": (
            "open_duck.t192_one_period_head_switch_result.v1"
        ),
        "status": status,
        "decision": decision,
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "integrity_checks": integrity_checks,
        "cell": cell,
        "switch": {
            "tick": prereg["switch_tick"],
            "trace_rows": len(hybrid_rows),
            "primary_rows": sum(
                not bool(row["policy_switch_active"]) for row in hybrid_rows
            ),
            "switch_rows": sum(
                bool(row["policy_switch_active"]) for row in hybrid_rows
            ),
            "pre_switch_prefix_rows_compared": prefix_rows,
        },
        "manifest": receipt(manifest_path),
        "execution": {
            "new_behavior_cells": 1,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
            "wall_seconds": time.time() - started,
        },
        "authority": {
            **prereg["authority_after_result"],
            "checkpoint_consistency_teacher_preregistration": (
                integrity_green and behavior_green
            ),
        },
    }
    value = {
        **basis_result,
        "result_sha256": canonical_sha256(basis_result),
    }
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T192 one-period head-switch result\n\n"
        f"- Status: `{status}`\n"
        f"- Decision: `{decision}`\n"
        f"- Cell green: `{cell['cell_green']}`\n"
        f"- Samples: `{cell['behavior']['samples']}`\n"
        f"- Termination: `{cell['behavior']['termination_reason']}`\n"
        f"- Prefix exact / state continuity: "
        f"`{prefix_exact}/{state_continuity}`\n"
        f"- Primary / switch rows: "
        f"`{basis_result['switch']['primary_rows']}/"
        f"{basis_result['switch']['switch_rows']}`\n"
        "- Optimizer / hosted compute / robot: `0/0/0`\n"
        f"- Result SHA-256: `{value['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(status)
    print(f"decision={decision}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if integrity_green and behavior_green else 1


if __name__ == "__main__":
    raise SystemExit(main())
