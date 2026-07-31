#!/usr/bin/env python3
"""Review immutable T241 output sensitivity without rerunning it."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    canonical_sha256,
)


PREREG = (
    ANALYSIS
    / "t241b_random_sensitivity_recovery_preregistration.json"
)
OUTPUT = ANALYSIS / "t241b_random_sensitivity_recovery_result.json"
MARKDOWN = (
    ANALYSIS / "T241B_RANDOM_SENSITIVITY_RECOVERY_RESULT_20260731.md"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T241B: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    if (
        prereg["status"]
        != "PREREGISTERED_T241B_RANDOM_SENSITIVITY_RECOVERY"
    ):
        raise RuntimeError("T241B preregistration status changed")
    for row in prereg["frozen_inputs"].values():
        path = Path(row["path"])
        if sha256(path) != row["sha256"]:
            raise RuntimeError(f"T241B frozen input changed: {path}")
    t241 = json.loads(
        Path(prereg["frozen_inputs"]["t241_result"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    nonrandom_checks = {
        name: passed
        for name, passed in t241["checks"].items()
        if name != "random_contract_exact"
    }
    checks = {
        "sole_failed_check_is_random_sensitivity": (
            t241["failed_checks"] == ["random_contract_exact"]
        ),
        "all_structure_abi_and_trace_checks_green": all(
            nonrandom_checks.values()
        ),
        "random_preservation_and_finiteness_green": all(
            graph["random_inference"]["all_outputs_finite"]
            and graph["random_inference"]["all_non_home_negative_exact"]
            and graph["random_inference"]["all_home_negative_x0_exact"]
            for graph in t241["graphs"]
        ),
        "all_twelve_failed_traces_changed": (
            sum(
                len(graph["trace_replay"]["traces"])
                for graph in t241["graphs"]
            )
            == 12
            and all(
                graph["trace_replay"]["all_source_replay_exact"]
                and graph["trace_replay"]["all_transformed_finite"]
                and graph["trace_replay"]["every_trace_changed"]
                for graph in t241["graphs"]
            )
        ),
        "all_948_failed_state_rows_replayed": (
            sum(
                graph["trace_replay"]["rows"] for graph in t241["graphs"]
            )
            == 948
        ),
        "immutable_review_no_rerun_behavior_training_hosted_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    status = (
        "PASS_T241B_RANDOM_SENSITIVITY_REPORTING_RECOVERY"
        if passed
        else "HOLD_T241B_RANDOM_SENSITIVITY_RECOVERY"
    )
    decision = (
        prereg["recovery_rule"]["pass_decision"]
        if passed
        else prereg["recovery_rule"]["fail_decision"]
    )
    result_basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t241b_random_sensitivity_recovery.v1"
        ),
        "status": status,
        "decision": decision,
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "classification": (
            "NON_CAUSAL_RANDOM_SENSITIVITY_EXPECTATION"
            if passed
            else "UNRECOVERED_T241_HOLD"
        ),
        "immutable_t241_result_sha256": t241["result_sha256"],
        "execution": {
            "onnx_transforms": 0,
            "inference_rows": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_sessions": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "home_offset_behavior_preregistration": passed,
            "training": False,
            "hosted": False,
            "gate5": False,
            "robot_or_rdk": False,
        },
    }
    result = {
        **result_basis,
        "result_sha256": canonical_sha256(result_basis),
    }
    OUTPUT.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T241B random-sensitivity recovery result\n\n"
        f"- Status: `{status}`\n"
        f"- Decision: `{decision}`\n"
        "- Classification: random equality was non-causal; all `948` "
        "actual failed-state rows changed under the bounded route\n"
        "- Transform/inference/behavior/training/hosted/robot reruns: "
        "`0/0/0/0/0/0`\n"
        f"- Result SHA-256: `{result['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(status)
    print(f"decision={decision}")
    print(f"result_sha256={result['result_sha256']}")
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
