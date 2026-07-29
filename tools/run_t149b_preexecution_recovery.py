#!/usr/bin/env python3
"""Run T149B after correcting T149's pre-execution verifier call."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
from typing import Any

import run_t149_negative_context_command_plateau_transform as t149


PREREG = (
    t149.ANALYSIS
    / "t149b_preexecution_recovery_preregistration.json"
)
RESULT = (
    t149.ANALYSIS
    / "t149b_negative_context_command_plateau_result.json"
)
MARKDOWN = (
    t149.ANALYSIS
    / "T149B_NEGATIVE_CONTEXT_COMMAND_PLATEAU_RESULT_20260729.md"
)
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t149b_negative_context_command_plateau_v1"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    if RESULT.exists() or MARKDOWN.exists() or WORK.exists():
        raise FileExistsError("refusing to overwrite T149B")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=t149.ROOT, text=True
    ).strip():
        raise RuntimeError("T149B execution requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T149B_PREEXECUTION_RECOVERY"
        or prereg["failed_checks"]
        or t149.canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T149B preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        t149.verify(item, name)

    t145 = json.loads(
        Path(prereg["frozen_inputs"]["t145c_result"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    t143 = json.loads(
        Path(prereg["frozen_inputs"]["t143c_result"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    t135 = json.loads(
        Path(prereg["frozen_inputs"]["t135b_contexts"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    reference = Path(
        prereg["frozen_inputs"]["reference_feature_table"]["path"]
    )
    attribution = t149.trace_attribution(t145)
    alias = t149.table_alias(reference)
    contexts = t135["runs"]
    WORK.mkdir(parents=True)
    transforms = {}
    contracts = {}
    for index, (step, item) in enumerate(
        sorted(t143["graphs"].items()), start=1
    ):
        source = Path(item["transformed"]["path"])
        destination = WORK / step / "negative_command_plateau.onnx"
        transforms[step] = t149.transform(source, destination)
        contracts[step] = t149.equivalence_contract(
            source,
            destination,
            contexts,
            seed=20260729 + index,
        )

    checks = {
        "source_failure_attribution_exact": (
            attribution["all_four_anchor_cells_green"]
            and attribution["all_eight_upper_cells_fail"]
            and attribution["maximum_reference_feature_delta"] == 0.0
            and attribution["minimum_compared_rows"] >= 95
        ),
        "reference_table_alias_exact": alias["same_reference_row"],
        "graph_transforms_structurally_exact": all(
            item["nine_nodes_inserted"]
            and item["inserted_node_names_exact"]
            and item["two_raw_obs_consumers_rewired_exact"]
            and item["all_other_nodes_byte_exact"]
            and item["existing_initializers_byte_exact"]
            and item["nine_initializers_added"]
            and item["abi_exact"]
            for item in transforms.values()
        ),
        "all_context_command_rows_bit_exact": all(
            item["all_rows_bit_exact"] for item in contracts.values()
        ),
        "all_stateful_chains_bit_exact": all(
            item["all_chains_bit_exact"] for item in contracts.values()
        ),
        "expected_equivalence_population": all(
            item["sample_rows"] == 512 for item in contracts.values()
        ),
        "environment_training_colab_robot_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t149b_negative_context_command_plateau_result.v1"
        ),
        "status": (
            "PASS_T149B_NEGATIVE_CONTEXT_COMMAND_PLATEAU"
            if passed
            else "HOLD_T149B_NEGATIVE_CONTEXT_COMMAND_PLATEAU"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if passed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "recovery_kind": "T149_MISSING_VERIFY_LABEL_PREEXECUTION",
        "source_t149_contract_sha256": prereg[
            "source_t149_contract_sha256"
        ],
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "attribution": attribution,
        "reference_table_alias": alias,
        "transforms": transforms,
        "contracts": contracts,
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "random_equivalence_rows": sum(
                item["sample_rows"] for item in contracts.values()
            ),
            "stateful_chain_steps": sum(
                row["steps"]
                for item in contracts.values()
                for row in item["chain_rows"]
            ),
            "environment_steps": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "negative_endpoint_preregistration": passed,
            "training": False,
            "colab": False,
            "policy_promotion": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["result_sha256"] = t149.canonical_sha256(value)
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T149B negative-context command plateau result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Failed checks: `{failed}`\n"
        "- Recovery: missing receipt-verifier label only\n"
        "- Environment / behavior / optimizer / Colab / robot: `0/0/0/0/0`\n"
        f"- Result SHA-256: `{value['result_sha256']}`\n",
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
