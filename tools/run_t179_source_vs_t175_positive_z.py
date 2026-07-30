#!/usr/bin/env python3
"""Run the frozen positive-Z source-versus-T175 CPU behavior A/B."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREGISTRATION = (
    ANALYSIS / "t179_source_vs_t175_positive_z_preregistration.json"
)
RESULT = ANALYSIS / "t179_source_vs_t175_positive_z_result.json"
MARKDOWN = ANALYSIS / "T179_SOURCE_VS_T175_POSITIVE_Z_RESULT_20260730.md"
CACHE = Path(
    r"D:\CodexArtifacts\open-duck-policy"
    r"\t179_source_vs_t175_positive_z_v1"
)

sys.path.insert(0, str(ROOT / "tools"))
from run_t27_t23_robustness_matrix import (  # noqa: E402
    canonical_sha256,
    condition_summary,
    extract_block,
    receipt,
    run_or_load_block,
    verify_receipt,
)


class T179Error(RuntimeError):
    """The frozen T179 causal A/B contract was violated."""


def _require(condition: object, message: str) -> None:
    if not condition:
        raise T179Error(message)


def _load_json(path: Path) -> dict[str, Any]:
    _require(path.is_file(), f"missing JSON artifact: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def _canonical_without(value: Mapping[str, Any], field: str) -> str:
    basis = dict(value)
    basis.pop(field, None)
    return canonical_sha256(basis)


def failure_keys(blocks: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    failures = []
    for block in blocks:
        for cell in block["result"]["cells"]:
            if not cell["cell_green"]:
                failures.append(
                    {
                        "checkpoint_id": block["checkpoint_id"],
                        "fit_id": block["fit_id"],
                        "command_x_m_s": float(cell["command_x_m_s"]),
                        "samples": int(cell["behavior"]["samples"]),
                        "termination_reason": cell["behavior"][
                            "termination_reason"
                        ],
                    }
                )
    return sorted(
        failures,
        key=lambda row: (
            row["checkpoint_id"],
            row["fit_id"],
            row["command_x_m_s"],
        ),
    )


def classify_ab(
    *,
    source_green: int,
    transformed_green: int,
    source_failures: Sequence[Mapping[str, Any]],
    transformed_failures: Sequence[Mapping[str, Any]],
    identical_trace_count: int,
) -> tuple[str, str]:
    same_failure_cells = {
        (
            row["checkpoint_id"].replace("T170_SOURCE", ""),
            row["fit_id"],
            float(row["command_x_m_s"]),
        )
        for row in source_failures
    } == {
        (
            row["checkpoint_id"].replace("T175_HEAD_MEAN", ""),
            row["fit_id"],
            float(row["command_x_m_s"]),
        )
        for row in transformed_failures
    }
    if source_green == 16:
        return (
            "T175_HEAD_PREFIX_MEAN_INTRODUCED_POSITIVE_Z_REGRESSION",
            "EARN_T180_TRANSFORM_ROUTE_ATTRIBUTION_CPU_PREREGISTRATION_ONLY",
        )
    if source_green > transformed_green:
        return (
            "T175_HEAD_PREFIX_MEAN_NET_POSITIVE_Z_REGRESSION",
            "EARN_T180_TRANSFORM_ROUTE_ATTRIBUTION_CPU_PREREGISTRATION_ONLY",
        )
    if (
        source_green == transformed_green
        and same_failure_cells
        and identical_trace_count == 16
    ):
        return (
            "T175_NO_EFFECT_POSITIVE_Z_FAILURE_PREDATES_TRANSFORM",
            "EARN_T180_POSITIVE_Z_BALANCE_MECHANISM_REVIEW_ONLY",
        )
    if source_green == transformed_green and same_failure_cells:
        return (
            "T175_NONCAUSAL_SHARED_POSITIVE_Z_FAILURE_MATRIX",
            "EARN_T180_POSITIVE_Z_BALANCE_MECHANISM_REVIEW_ONLY",
        )
    if source_green < transformed_green:
        return (
            "T175_PARTIAL_POSITIVE_Z_IMPROVEMENT_INSUFFICIENT",
            "EARN_T180_POSITIVE_Z_BALANCE_MECHANISM_REVIEW_ONLY",
        )
    return (
        "MIXED_SOURCE_AND_T175_POSITIVE_Z_OUTCOME",
        "EARN_T180_POSITIVE_Z_BALANCE_MECHANISM_REVIEW_ONLY",
    )


def _load_preregistration(path: Path) -> dict[str, Any]:
    value = _load_json(path)
    _require(
        value.get("status")
        == "PREREGISTERED_T179_SOURCE_VS_T175_POSITIVE_Z_CPU_AB",
        "unexpected T179 preregistration status",
    )
    _require(
        _canonical_without(value, "preregistered_contract_sha256")
        == value.get("preregistered_contract_sha256"),
        "T179 preregistration hash differs",
    )
    for label, item in value["frozen_inputs"].items():
        verify_receipt(item, label)
    for policy in value["source_policies"]:
        verify_receipt(policy, f"source_policy:{policy['checkpoint_id']}")
    for fit in value["fits"]:
        verify_receipt(fit, f"fit:{fit['fit_id']}")
    verify_receipt(value["calibrator"], "calibrator")
    verify_receipt(value["reference_feature_table"], "reference")
    verify_receipt(value["playground"]["manifest"], "playground_manifest")
    for block in value["transformed_blocks"]:
        verify_receipt(
            block["manifest"],
            f"transformed:{block['checkpoint_id']}:{block['fit_id']}",
        )
        for trace in block["traces"]:
            verify_receipt(
                trace,
                f"transformed_trace:{block['checkpoint_id']}:"
                f"{block['fit_id']}:{trace['command_x_m_s']:.3f}",
            )
    return value


def _source_trace_receipts(
    manifest: Mapping[str, Any],
    commands: Sequence[float],
) -> list[dict[str, Any]]:
    _require(
        len(manifest["traces"]) == len(commands),
        "source manifest trace count differs",
    )
    result = []
    for command, trace in zip(commands, manifest["traces"], strict=True):
        verify_receipt(trace, f"source_trace:{command:.3f}")
        result.append({"command_x_m_s": float(command), **trace})
    return result


def _markdown(value: Mapping[str, Any]) -> str:
    return (
        "# T179 source versus T175 positive-Z CPU A/B\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Classification: `{value['classification']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Source green: `{value['summary']['source_green_cells']}/16`\n"
        f"- T175 green: `{value['summary']['transformed_green_cells']}/16`\n"
        f"- Byte-identical traces: "
        f"`{value['summary']['identical_trace_files']}/16`\n"
        "- Fresh source behavior / transformed reruns: `16/0`\n"
        "- Optimizer / hosted compute / robot: `0/0/0`\n\n"
        "This A/B attributes the positive-Z failure only. It does not authorize "
        "training, deployment audit, Gate 5, or hardware.\n"
    )


def run(
    preregistration_path: Path = PREREGISTRATION,
    result_path: Path = RESULT,
    markdown_path: Path = MARKDOWN,
    cache_root: Path = CACHE,
) -> dict[str, Any]:
    _require(not result_path.exists(), f"refusing to overwrite: {result_path}")
    _require(not markdown_path.exists(), f"refusing to overwrite: {markdown_path}")
    _require(
        not subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=ROOT, text=True
        ).strip(),
        "T179 execution requires committed clean preregistration",
    )
    prereg = _load_preregistration(preregistration_path)
    cache_root.mkdir(parents=True, exist_ok=True)
    condition = prereg["condition"]
    commands = [float(item) for item in prereg["commands_x_m_s"]]
    started = time.time()
    source_blocks = []
    source_trace_map: dict[tuple[str, str, float], dict[str, Any]] = {}
    for policy in prereg["source_policies"]:
        for fit in prereg["fits"]:
            manifest, cached = run_or_load_block(
                prereg, condition, policy, fit, cache_root
            )
            _require(not cached, "T179 requires a fresh source cache")
            block_result = extract_block(prereg, condition, manifest)
            manifest_path = (
                cache_root
                / f"{condition['condition_index']:02d}_{condition['id']}"
                / policy["checkpoint_id"]
                / fit["fit_id"]
                / "manifest.json"
            )
            source_traces = _source_trace_receipts(manifest, commands)
            for trace in source_traces:
                source_trace_map[
                    (
                        policy["checkpoint_id"],
                        fit["fit_id"],
                        trace["command_x_m_s"],
                    )
                ] = trace
            source_blocks.append(
                {
                    "condition_index": condition["condition_index"],
                    "condition_id": condition["id"],
                    "checkpoint_id": policy["checkpoint_id"],
                    "step": policy["step"],
                    "fit_id": fit["fit_id"],
                    "cached": False,
                    "manifest": receipt(manifest_path),
                    "traces": source_traces,
                    "result": block_result,
                }
            )
            print(
                json.dumps(
                    {
                        "checkpoint": policy["checkpoint_id"],
                        "fit": fit["fit_id"],
                        "green": block_result["block_green"],
                        "elapsed_s": time.time() - started,
                    }
                ),
                flush=True,
            )

    transformed_blocks = prereg["transformed_blocks"]
    source_summary = condition_summary(condition, source_blocks)
    transformed_summary = condition_summary(condition, transformed_blocks)
    transformed_trace_map = {
        (
            block["checkpoint_id"],
            block["fit_id"],
            float(trace["command_x_m_s"]),
        ): trace
        for block in transformed_blocks
        for trace in block["traces"]
    }
    checkpoint_pairs = prereg["checkpoint_pairs"]
    identical = []
    for pair in checkpoint_pairs:
        for fit in prereg["fits"]:
            for command in commands:
                source = source_trace_map[
                    (pair["source_checkpoint_id"], fit["fit_id"], command)
                ]
                transformed = transformed_trace_map[
                    (pair["transformed_checkpoint_id"], fit["fit_id"], command)
                ]
                identical.append(
                    {
                        "source_checkpoint_id": pair["source_checkpoint_id"],
                        "transformed_checkpoint_id": pair[
                            "transformed_checkpoint_id"
                        ],
                        "fit_id": fit["fit_id"],
                        "command_x_m_s": command,
                        "byte_identical": (
                            source["bytes"] == transformed["bytes"]
                            and source["sha256"] == transformed["sha256"]
                        ),
                    }
                )
    source_failures = failure_keys(source_blocks)
    transformed_failures = failure_keys(transformed_blocks)
    identical_count = sum(int(row["byte_identical"]) for row in identical)
    classification, decision = classify_ab(
        source_green=int(source_summary["green_cells"]),
        transformed_green=int(transformed_summary["green_cells"]),
        source_failures=source_failures,
        transformed_failures=transformed_failures,
        identical_trace_count=identical_count,
    )
    basis: dict[str, Any] = {
        "schema_version": "open_duck.t179_source_vs_t175_positive_z_result.v1",
        "status": "COMPLETE_T179_SOURCE_VS_T175_POSITIVE_Z_CPU_AB",
        "classification": classification,
        "decision": decision,
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "summary": {
            "source_green_cells": int(source_summary["green_cells"]),
            "transformed_green_cells": int(
                transformed_summary["green_cells"]
            ),
            "identical_trace_files": identical_count,
            "source_failure_count": len(source_failures),
            "transformed_failure_count": len(transformed_failures),
            "wall_seconds": time.time() - started,
        },
        "source_condition_summary": source_summary,
        "transformed_condition_summary": transformed_summary,
        "source_failures": source_failures,
        "transformed_failures": transformed_failures,
        "trace_identity": identical,
        "source_blocks": source_blocks,
        "transformed_blocks": transformed_blocks,
        "execution": {
            "new_source_behavior_cells": 16,
            "transformed_behavior_cells_reused": 16,
            "transformed_behavior_cells_rerun": 0,
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
        _markdown(basis), encoding="utf-8", newline="\n"
    )
    return basis


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument("--preregistration", type=Path, default=PREREGISTRATION)
    parser.add_argument("--result", type=Path, default=RESULT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    parser.add_argument("--cache-root", type=Path, default=CACHE)
    args = parser.parse_args()
    result = run(
        args.preregistration, args.result, args.markdown, args.cache_root
    )
    print(result["status"])
    print(f"classification={result['classification']}")
    print(f"decision={result['decision']}")
    print(f"result_sha256={result['result_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
