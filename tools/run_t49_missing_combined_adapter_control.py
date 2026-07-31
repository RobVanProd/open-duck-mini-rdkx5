#!/usr/bin/env python3
"""Run T49's one missing combined adapter control and aggregate T48."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = (
    ANALYSIS
    / "t49_missing_combined_adapter_control_preregistration.json"
)
OUTPUT = ANALYSIS / "t49_missing_combined_adapter_control_result.json"
MARKDOWN = (
    ANALYSIS
    / "T49_MISSING_COMBINED_ADAPTER_CONTROL_RESULT_20260728.md"
)
CACHE_ROOT = (
    Path("D:/CodexArtifacts/open-duck-policy")
    / "t49_missing_combined_adapter_control_run_v1"
)

sys.path.insert(0, str(ROOT / "tools"))
import run_t48_final_adapter_core_head_factorial as t48  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    payload = dict(value)
    payload.pop("result_sha256", None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def verify_receipt(item: dict[str, Any], label: str) -> None:
    path = Path(item["path"])
    if (
        not path.is_file()
        or path.stat().st_size != int(item["bytes"])
        or sha256(path) != item["sha256"]
    ):
        raise ValueError(f"changed T49 receipt: {label}={path}")


def verify(prereg: dict[str, Any]) -> None:
    expected = prereg["preregistered_contract_sha256"]
    actual = hashlib.sha256(
        json.dumps(
            {
                key: value
                for key, value in prereg.items()
                if key != "preregistered_contract_sha256"
            },
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()
    if actual != expected:
        raise ValueError("changed T49 preregistration")
    if prereg["status"] != (
        "PREREGISTERED_T49_MISSING_COMBINED_ADAPTER_CONTROL"
    ):
        raise ValueError("T49 preregistration is not green")
    for label, item in prereg["frozen_inputs"].items():
        verify_receipt(item, label)
    verify_receipt(prereg["variant"]["policy"], "variant_policy")
    for index, cell in enumerate(prereg["completed_cells"]):
        verify_receipt(
            cell["execution"]["evaluation"],
            f"prior_{index}_evaluation",
        )
        verify_receipt(
            cell["execution"]["stdout"], f"prior_{index}_stdout"
        )
        verify_receipt(
            cell["execution"]["trace"], f"prior_{index}_trace"
        )
    for label, item in (
        ("fit", prereg["fit"]),
        ("calibrator", prereg["calibrator"]),
        ("reference", prereg["reference_feature_table"]),
    ):
        verify_receipt(item, label)


def require_clean_worktree() -> str:
    status = subprocess.run(
        ["git", "status", "--short"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if status.strip():
        raise RuntimeError("formal T49 execution requires a clean worktree")
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise SystemExit("refusing T49 execution without --execute")
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T49 result")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    verify(prereg)
    commit = require_clean_worktree()
    CACHE_ROOT.mkdir(parents=True, exist_ok=False)
    t48.CACHE_ROOT = CACHE_ROOT
    environment = os.environ.copy()
    environment.update(
        {
            "CUDA_VISIBLE_DEVICES": "",
            "HIP_VISIBLE_DEVICES": "",
            "ROCR_VISIBLE_DEVICES": "",
            "JAX_PLATFORMS": "cpu",
            "JAX_PLATFORM_NAME": "cpu",
            "JAX_COMPILATION_CACHE_DIR": str(
                CACHE_ROOT.parent / "jax_compilation_cache"
            ),
            "XLA_PYTHON_CLIENT_PREALLOCATE": "false",
        }
    )
    started = time.time()
    new_cell = t48.evaluate_variant(
        prereg,
        prereg["variant"],
        environment,
    )
    cells = [*prereg["completed_cells"], new_cell]
    valid = all(
        item["trace_valid"]
        and item["handoff"]["all_checks_pass"]
        and item["override_readback_exact"]
        for item in cells
    )
    passing = [item for item in cells if item["cell_green"]]
    one_group = [
        item for item in passing if item["half_group_count"] == 1
    ]
    order = {
        variant_id: index
        for index, variant_id in enumerate(prereg["execution_order"])
    }
    selected = (
        min(one_group, key=lambda item: order[item["variant_id"]])
        if one_group
        else None
    )
    combined_pass = bool(new_cell["cell_green"])
    if not valid:
        status = "INVALID_T49_COMPLETED_ADAPTER_FACTORIAL"
        decision = "ZERO_POLICY_DECISION_WEIGHT"
    elif selected is not None:
        status = "PASS_T49_COMPLETED_ADAPTER_ONE_SUBBLOCK_CAUSE"
        decision = (
            f"EARN_T50_{selected['variant_id']}_"
            "UNIFORM_TRANSFORM_PREREGISTRATION"
        )
    elif combined_pass:
        status = "PASS_T49_COMPLETED_ADAPTER_COUPLED_ONLY"
        decision = "CLOSE_T49_ENDPOINT_DUPLICATING_ADAPTER_SUBSTITUTION"
    else:
        status = "PASS_T49_COMPLETED_ADAPTER_NO_REPAIR"
        decision = "CLOSE_T49_ADAPTER_SUBBLOCK_SUBSTITUTION"
    result: dict[str, Any] = {
        "schema_version": (
            "open_duck.t49_missing_combined_adapter_control_result.v1"
        ),
        "status": status,
        "decision": decision,
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "repository_commit": commit,
        "cells": cells,
        "summary": {
            "prior_formal_behavior_cells_reused": 2,
            "new_formal_behavior_cells": 1,
            "aggregate_formal_behavior_cells": 3,
            "valid_cells": sum(
                bool(
                    item["trace_valid"]
                    and item["handoff"]["all_checks_pass"]
                    and item["override_readback_exact"]
                )
                for item in cells
            ),
            "green_cells": len(passing),
            "passing_variants": [
                item["variant_id"] for item in passing
            ],
            "one_group_passing_variants": [
                item["variant_id"] for item in one_group
            ],
            "selected_mechanism_variant_diagnostic": (
                selected["variant_id"] if selected is not None else None
            ),
            "selected_half_groups": (
                selected["half_groups"] if selected is not None else None
            ),
            "combined_variant_pass": combined_pass,
            "wall_seconds": time.time() - started,
        },
        "authority": {
            "uniform_transform_preregistration": (
                valid and selected is not None
            ),
            "policy_promotion": False,
            "checkpoint_selection": False,
            "training": False,
            "colab": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    result["result_sha256"] = canonical_sha256(result)
    OUTPUT.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T49 missing combined adapter control result",
                "",
                f"- Status: `{status}`",
                f"- Decision: `{decision}`",
                "- Prior/new/aggregate cells: `2/1/3`",
                (
                    "- Passing variants: `"
                    + ",".join(result["summary"]["passing_variants"])
                    + "`"
                ),
                (
                    "- Selected: `"
                    + str(
                        result["summary"][
                            "selected_mechanism_variant_diagnostic"
                        ]
                    )
                    + "`"
                ),
                "",
                "No policy is promoted. A one-subblock cause authorizes "
                "only a separate uniform-transform qualification.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(status)
    print(f"decision={decision}")
    print(f"passing_variants={result['summary']['passing_variants']}")
    print(
        "selected="
        f"{result['summary']['selected_mechanism_variant_diagnostic']}"
    )
    print(f"result_sha256={result['result_sha256']}")
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
