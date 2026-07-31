#!/usr/bin/env python3
"""Prove T129 was evaluated behind a gate absent during its training."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
from typing import Any

import onnx

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    verify,
)


PREREG = ANALYSIS / "t142_t129_forward_path_mismatch_preregistration.json"
RESULT = ANALYSIS / "t142_t129_forward_path_mismatch_result.json"
MARKDOWN = (
    ANALYSIS / "T142_T129_FORWARD_PATH_MISMATCH_RESULT_20260729.md"
)


def consumer_inventory(path: Path) -> dict[str, Any]:
    model = onnx.load(path)
    consumers = [
        {
            "index": index,
            "op_type": node.op_type,
            "name": node.name,
            "inputs": list(node.input),
            "outputs": list(node.output),
        }
        for index, node in enumerate(model.graph.node)
        if "conditional_adapter_location" in node.output
    ]
    gate_consumers = [
        row
        for row in consumers
        if row["op_type"] == "Where"
        and row["inputs"]
        == [
            "negative_com_gate",
            "negative_adapter_location",
            "zero_adapter_location",
        ]
    ]
    always_on_consumers = [
        row
        for row in consumers
        if row["op_type"] == "Identity"
        and row["inputs"] == ["negative_adapter_location"]
    ]
    return {
        "node_count": len(model.graph.node),
        "consumers": consumers,
        "hard_gate_consumers": len(gate_consumers),
        "always_on_consumers": len(always_on_consumers),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--read-only-authorized", action="store_true")
    args = parser.parse_args()
    if not args.read_only_authorized:
        raise PermissionError("T142 requires --read-only-authorized")
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T142: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T142 execution requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T142_T129_FORWARD_PATH_MISMATCH_AUDIT"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T142 preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, name)
    for group in ("raw_training_graphs", "hard_gate_deployments"):
        for step, item in prereg[group].items():
            verify(item, f"{group}:{step}")
    raw = {
        step: consumer_inventory(Path(item["path"]))
        for step, item in prereg["raw_training_graphs"].items()
    }
    deployed = {
        step: consumer_inventory(Path(item["path"]))
        for step, item in prereg["hard_gate_deployments"].items()
    }
    t128 = json.loads(
        Path(prereg["frozen_inputs"]["t128_result"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    t129 = json.loads(
        Path(prereg["frozen_inputs"]["t129_prereg"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    t131_prereg = json.loads(
        Path(prereg["frozen_inputs"]["t131_prereg"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    t141 = json.loads(
        Path(prereg["frozen_inputs"]["t141b_result"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    moving_failures = [
        cell
        for block in t141["blocks"]
        for cell in block["result"]["cells"]
        if cell["command_x_m_s"] > 0.0 and not cell["cell_green"]
    ]
    checks = {
        "t128_contract_is_always_on": (
            t128["always_on_transform"]["replacement_exact"]
            and t128["always_on_transform"][
                "negative_gate_consumer_count"
            ]
            == 0
            and t128["checks"]["exact_always_on_transform"]
        ),
        "t129_preregistered_forward_path_always_on": (
            t129["training"]["forward_path"]
            == "negative_adapter_location_always_on"
        ),
        "both_raw_training_exports_always_on": all(
            row["always_on_consumers"] == 1
            and row["hard_gate_consumers"] == 0
            for row in raw.values()
        ),
        "t131_explicitly_restored_hard_gate": (
            t131_prereg["frozen_chain"][0]
            == "restore_t98_hard_hidden_gate"
            and all(
                row["hard_gate_consumers"] == 1
                and row["always_on_consumers"] == 0
                for row in deployed.values()
            )
        ),
        "t141_all_twelve_moving_cells_fail_under_hard_gate": (
            t141["status"]
            == "HOLD_T141B_EXPERT_BANK_NEGATIVE_ENDPOINT_MATRIX"
            and t141["condition"]["green_cells"] == 4
            and len(moving_failures) == 12
            and all(
                cell["behavior"]["mean_local_vx_m_s"] < 0.0
                and cell["behavior"]["termination_reason"] == "fall_or_nan"
                for cell in moving_failures
            )
        ),
        "formal_behavior_cells_zero": True,
        "optimizer_colab_robot_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t142_t129_forward_path_mismatch_result.v1"
        ),
        "status": (
            "PASS_T142_T129_FORWARD_PATH_MISMATCH_AUDIT"
            if passed
            else "HOLD_T142_T129_FORWARD_PATH_MISMATCH_AUDIT"
        ),
        "classification": (
            "T129_TRAINED_ALWAYS_ON_BUT_EVALUATED_HARD_GATED"
            if passed
            else "T129_FORWARD_PATH_MISMATCH_NOT_ESTABLISHED"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if passed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "raw_training_graphs": raw,
        "hard_gate_deployments": deployed,
        "moving_failure_count": len(moving_failures),
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "onnx_graphs_read": len(raw) + len(deployed),
            "formal_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "conditional_forward_path_transform_preregistration": passed,
            "behavior_evaluation": False,
            "training": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["result_sha256"] = canonical_sha256(value)
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T142 T129 forward-path mismatch audit\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        "- Training: negative expert always on\n"
        "- Prior deployment tests: negative expert hard gated\n"
        "- Behavior / optimizer / Colab / robot: `0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
