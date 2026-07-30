#!/usr/bin/env python3
"""Freeze a read-only recovery of T221's endpoint/sensitivity verifier."""

from __future__ import annotations

import json
import math
from pathlib import Path
import subprocess
from typing import Any

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    receipt,
)


T221_PREREG = (
    ANALYSIS / "t221_t220_command_route_audit_preregistration.json"
)
T221 = ANALYSIS / "t221_t220_command_route_audit_result.json"
OUTPUT = (
    ANALYSIS
    / "t221b_command_route_verifier_recovery_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T221B_COMMAND_ROUTE_VERIFIER_RECOVERY_PREREGISTRATION_20260730.md"
)
RUNNER = ROOT / "tools/run_t221b_command_route_verifier_recovery.py"
TEST = ROOT / "tests/test_t221b_command_route_verifier_recovery.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T221B preregistration")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T221B preregistration requires clean worktree")
    prereg = json.loads(T221_PREREG.read_text(encoding="utf-8"))
    result = json.loads(T221.read_text(encoding="utf-8"))
    endpoint = float(prereg["audit"]["candidate_global_cap_m_s"])
    targeted = [
        row
        for row in prereg["targeted_cells"]
        if math.isclose(
            float(row["command_x_m_s"]), endpoint, rel_tol=0.0, abs_tol=1e-7
        )
    ]
    contexts = {
        row["fit_id"]: row for row in prereg["contexts"]
    }
    graphs = {row["step"]: row for row in prereg["graphs"]}
    pairs = []
    for row in targeted:
        graph = graphs[int(row["step"])]
        trace = row["protection"]
        pairs.append(
            {
                "checkpoint_id": row["checkpoint_id"],
                "step": row["step"],
                "role": graph["role"],
                "fit_id": row["fit_id"],
                "graph": graph["graph"],
                "context": contexts[row["fit_id"]],
                "trace": {
                    "path": trace["path"],
                    "bytes": Path(trace["path"]).stat().st_size,
                    "sha256": trace["sha256"],
                },
                "cell_green": row["cell_green"],
                "samples": row["behavior"]["samples"],
                "mean_local_vx_m_s": row["behavior"]["mean_local_vx_m_s"],
            }
        )
    frozen = {
        "builder": receipt(Path(__file__)),
        "runner": receipt(RUNNER),
        "test": receipt(TEST),
        "t221_preregistration": receipt(T221_PREREG),
        "t221_partial_result": receipt(T221),
        "t221_original_runner": prereg["frozen_inputs"]["runner"],
    }
    expected_failed = [
        "every_nominal_x0077_cell_passes",
        "every_targeted_x0077_cell_passes",
        "nominal_x0077_retains_external_x008_minimum_ratio",
        "source_policy_responds_to_077_vs_080",
        "targeted_x0077_retains_external_x008_minimum_ratio",
    ]
    checks = {
        "t221_exact_partial_hold": (
            result["status"] == "HOLD_T221_T220_COMMAND_ROUTE_AUDIT"
            and result["failed_checks"] == expected_failed
            and result["result_sha256"]
            == "ec3992c8d7f5d0dcfe6082a72556386eee5d478e66968df9f79f18924a494980"
        ),
        "all_non_endpoint_and_route_checks_green": all(
            passed
            for name, passed in result["checks"].items()
            if name not in expected_failed
        ),
        "four_exact_passing_endpoint_pairs": (
            len(pairs) == 4
            and all(row["cell_green"] for row in pairs)
            and {(row["step"], row["fit_id"]) for row in pairs}
            == {
                (1_003_520, "p30"),
                (1_003_520, "p31_34"),
                (2_007_040, "p30"),
                (2_007_040, "p31_34"),
            }
        ),
        "all_trace_graph_and_context_inputs_present": all(
            Path(row["trace"]["path"]).is_file()
            and Path(row["graph"]["path"]).is_file()
            and row["context"]["context_sha256"]
            == next(
                cell["handoff"]["context_sha256"]
                for cell in prereg["targeted_cells"]
                if cell["checkpoint_id"] == row["checkpoint_id"]
                and cell["fit_id"] == row["fit_id"]
                and math.isclose(
                    float(cell["command_x_m_s"]),
                    endpoint,
                    rel_tol=0.0,
                    abs_tol=1e-7,
                )
            )
            for row in pairs
        ),
        "zero_simulator_optimizer_behavior_hosted_or_robot_now": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T221B preregistration checks failed: {failed}")
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t221b_command_route_verifier_recovery_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T221B_COMMAND_ROUTE_VERIFIER_RECOVERY",
        "question": (
            "Do tolerance-safe endpoint selection and same-state inference "
            "on the frozen passing T220 x=.077 trajectory states recover "
            "T221 without changing its route attribution, cap, or decision?"
        ),
        "frozen_inputs": frozen,
        "source_t221_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "source_t221_result_sha256": result["result_sha256"],
        "pairs": pairs,
        "recovery": {
            "endpoint_m_s": endpoint,
            "endpoint_absolute_tolerance": 1e-7,
            "external_command_m_s": 0.08,
            "minimum_track_ratio": 0.4,
            "trace_rows_per_pair": 64,
            "trace_row_selection": "first_64_contiguous_rows",
            "same_state_commands_m_s": [0.077, 0.080],
            "provider": "CPUExecutionProvider",
            "defects": [
                "strict float64 JSON versus float32 endpoint equality",
                "random states saturated or rate-clipped command sensitivity",
            ],
            "allowed_change": "verifier_selection_and_state_population_only",
            "selection_weight": 0,
        },
        "decision_rule": {
            "recover_if": [
                "exactly four nominal and four targeted x=.077 cells pass",
                "all eight retain >=.4 velocity ratio against external x=.080",
                "all four frozen targeted x=.077 traces are exact and contiguous",
                "same-state x=.077 versus x=.080 changes policy action on every pair",
                "all T221 route and T149-cap checks remain green",
            ],
            "pass": (
                "RECOVER_T221_AND_EARN_T222_GLOBAL_X008_TO_X0077_"
                "PLATEAU_CPU_CONTRACT_PREREGISTRATION_ONLY"
            ),
            "fail": "CLOSE_GLOBAL_COMMAND_PLATEAU_WITHOUT_BEHAVIOR",
            "rerun_t221": False,
            "simulator_replay": False,
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "saved_trace_rows": 0,
            "onnx_inferences": 0,
            "simulator_transitions": 0,
            "optimizer_steps": 0,
            "behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_read_only_recovery": True,
            "transform_contract_preregistration": False,
            "behavior": False,
            "training": False,
            "colab": False,
            "gate5": False,
            "robot_or_rdk": False,
        },
    }
    value = {
        **basis,
        "preregistered_contract_sha256": canonical_sha256(basis),
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T221B command-route verifier recovery preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Recovery: tolerance-safe `.077` selection plus frozen trace states\n"
        "- T221 result and graph/trace hashes remain immutable\n"
        "- Simulator / optimizer / behavior / hosted / robot: `0/0/0/0/0`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(
        "preregistered_contract_sha256="
        f"{value['preregistered_contract_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
