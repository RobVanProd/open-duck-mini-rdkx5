#!/usr/bin/env python3
"""Run corrected T180 attribution after exact condition binding."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREGISTRATION = (
    ANALYSIS / "t180b_transform_route_attribution_preregistration.json"
)
RESULT = ANALYSIS / "t180b_transform_route_attribution_result.json"
MARKDOWN = (
    ANALYSIS / "T180B_TRANSFORM_ROUTE_ATTRIBUTION_RESULT_20260730.md"
)

sys.path.insert(0, str(ROOT / "tools"))
import run_t180_transform_route_attribution as base  # noqa: E402
from run_t27_t23_robustness_matrix import (  # noqa: E402
    canonical_sha256,
    verify_receipt,
)


def run(
    preregistration_path: Path = PREREGISTRATION,
    result_path: Path = RESULT,
    markdown_path: Path = MARKDOWN,
) -> dict[str, Any]:
    base._require(not result_path.exists(), f"refusing to overwrite: {result_path}")
    base._require(
        not markdown_path.exists(), f"refusing to overwrite: {markdown_path}"
    )
    base._require(
        not subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=ROOT, text=True
        ).strip(),
        "T180B execution requires committed clean preregistration",
    )
    prereg = base._load_json(preregistration_path)
    base._require(
        prereg.get("status")
        == "PREREGISTERED_T180B_TRANSFORM_ROUTE_ATTRIBUTION_RECOVERY",
        "unexpected T180B preregistration status",
    )
    base._require(
        base._canonical_without(prereg, "preregistered_contract_sha256")
        == prereg.get("preregistered_contract_sha256"),
        "T180B preregistration hash differs",
    )
    for label, item in prereg["frozen_inputs"].items():
        verify_receipt(item, label)

    import onnxruntime as ort

    sessions: dict[str, Any] = {}
    case_results = []
    all_banks: dict[str, list[dict[str, Any]]] = {
        "negative_y_rescue": [],
        "positive_z_regression": [],
        "positive_z_shared_failure": [],
    }
    prefix_ticks = int(prereg["analysis_contract"]["prefix_ticks"])
    gait_period = int(prereg["analysis_contract"]["gait_period_ticks"])
    for case in prereg["cases"]:
        for role in ("source_graph", "transformed_graph"):
            graph = case[role]
            verify_receipt(graph, f"{case['case_id']}:{role}")
            if graph["sha256"] not in sessions:
                sessions[graph["sha256"]] = ort.InferenceSession(
                    graph["path"], providers=["CPUExecutionProvider"]
                )
        context = np.asarray(case["context"], dtype=np.float32)
        base._require(
            context.shape == (64,), f"context shape differs: {case['case_id']}"
        )
        base._require(
            base.array_sha256(context) == case["context_sha256"],
            f"context hash differs: {case['case_id']}",
        )
        banks = []
        for bank_role in ("source_trace", "transformed_trace"):
            rows = base._read_prefix(
                case[bank_role],
                prefix_ticks=prefix_ticks,
                expected_command=float(case["command_x_m_s"]),
                expected_context_sha256=case["context_sha256"],
            )
            bank = base.replay_bank(
                rows,
                context=context,
                source_session=sessions[case["source_graph"]["sha256"]],
                transformed_session=sessions[
                    case["transformed_graph"]["sha256"]
                ],
                own_graph=(
                    "source" if bank_role == "source_trace" else "transformed"
                ),
                gait_period_ticks=gait_period,
            )
            bank["bank_role"] = bank_role
            banks.append(bank)
            all_banks[case["family"]].append(bank)
        case_results.append(
            {
                key: case[key]
                for key in (
                    "case_id",
                    "family",
                    "condition_id",
                    "checkpoint_pair",
                    "fit_id",
                    "command_x_m_s",
                    "source_cell_green",
                    "transformed_cell_green",
                )
            }
            | {"banks": banks}
        )
    aggregates = {
        name: base.aggregate_banks(banks) for name, banks in all_banks.items()
    }
    replay_max = max(
        bank["own_replay_max_abs_error"]
        for banks in all_banks.values()
        for bank in banks
    )
    family_cosine = base.cosine(
        aggregates["negative_y_rescue"]["signed_mean_delta"],
        aggregates["positive_z_regression"]["signed_mean_delta"],
    )
    classification, decision = base.classify_route(
        replay_max_error=replay_max,
        helpful=aggregates["negative_y_rescue"],
        harmful=aggregates["positive_z_regression"],
        signed_cosine=family_cosine,
        cosine_threshold=float(
            prereg["analysis_contract"]["shared_direction_cosine_threshold"]
        ),
    )
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t180b_transform_route_attribution_result.v1"
        ),
        "status": "COMPLETE_T180B_TRANSFORM_ROUTE_ATTRIBUTION_RECOVERY",
        "classification": classification,
        "decision": decision,
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "recovery_sha256": prereg["recovery_sha256"],
        "summary": {
            "cases": len(case_results),
            "banks": sum(len(item["banks"]) for item in case_results),
            "ticks_per_bank": prefix_ticks,
            "maximum_own_replay_error": replay_max,
            "helpful_harmful_signed_cosine": family_cosine,
        },
        "family_aggregates": aggregates,
        "cases": case_results,
        "execution": {
            "saved_trace_banks": 12,
            "saved_trace_rows": 12 * prefix_ticks,
            "onnx_graphs": len(sessions),
            "new_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": prereg["authority_after_result"],
    }
    basis["result_sha256"] = canonical_sha256(basis)
    result_path.write_text(
        json.dumps(basis, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    markdown_path.write_text(
        "# T180B corrected transform-route attribution\n\n"
        f"- Status: `{basis['status']}`\n"
        f"- Classification: `{classification}`\n"
        f"- Decision: `{decision}`\n"
        f"- Maximum own-graph replay error: `{replay_max:.9g}`\n"
        f"- Helpful dominant joint: "
        f"`{aggregates['negative_y_rescue']['dominant_joint']}`\n"
        f"- Harmful dominant joint: "
        f"`{aggregates['positive_z_regression']['dominant_joint']}`\n"
        f"- Signed family cosine: `{family_cosine:.6f}`\n"
        "- New behavior / optimizer / hosted compute / robot: `0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    return basis


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preregistration", type=Path, default=PREREGISTRATION)
    parser.add_argument("--result", type=Path, default=RESULT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    result = run(args.preregistration, args.result, args.markdown)
    print(result["status"])
    print(f"classification={result['classification']}")
    print(f"decision={result['decision']}")
    print(f"result_sha256={result['result_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
