#!/usr/bin/env python3
"""Run T44's corrected three-cell forward actor-block factorial."""

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
    ANALYSIS / "t44_corrected_forward_factorial_preregistration.json"
)
OUTPUT = ANALYSIS / "t44_corrected_forward_factorial_result.json"
MARKDOWN = ANALYSIS / "T44_CORRECTED_FORWARD_FACTORIAL_RESULT_20260728.md"
CACHE_ROOT = (
    Path("D:/CodexArtifacts/open-duck-policy")
    / "t44_corrected_forward_factorial_run_v1"
)

sys.path.insert(0, str(ROOT / "tools"))
import run_t43_forward_actor_block_factorial as t43  # noqa: E402


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
        raise ValueError("changed T44 preregistration")
    if (
        prereg["status"]
        != "PREREGISTERED_T44_CORRECTED_FORWARD_ACTOR_FACTORIAL"
    ):
        raise ValueError("T44 preregistration is not green")
    for item in prereg["frozen_inputs"].values():
        path = Path(item["path"])
        if sha256(path) != item["sha256"]:
            raise ValueError(f"changed T44 frozen input: {path}")
    for variant in prereg["variants"]:
        item = variant["policy"]
        if sha256(Path(item["path"])) != item["sha256"]:
            raise ValueError("changed T44 variant policy")
    for item in (
        prereg["fit"],
        prereg["calibrator"],
        prereg["reference_feature_table"],
    ):
        if sha256(Path(item["path"])) != item["sha256"]:
            raise ValueError("changed T44 evaluated input")


def require_clean_worktree() -> str:
    status = subprocess.run(
        ["git", "status", "--short"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if status.strip():
        raise RuntimeError("formal T44 execution requires a clean worktree")
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
        raise SystemExit("refusing T44 outcome execution without --execute")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    verify(prereg)
    commit = require_clean_worktree()
    CACHE_ROOT.mkdir(parents=True, exist_ok=False)
    t43.CACHE_ROOT = CACHE_ROOT
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
    cells: list[dict[str, Any]] = []
    started = time.time()
    for variant in prereg["variants"]:
        cell = t43.evaluate_variant(prereg, variant, environment)
        cells.append(cell)
        print(
            json.dumps(
                {
                    "variant_id": cell["variant_id"],
                    "final_groups": cell["final_groups"],
                    "cell_green": cell["cell_green"],
                    "samples": cell["behavior"]["samples"],
                    "elapsed_s": time.time() - started,
                }
            ),
            flush=True,
        )
    valid = all(
        cell["trace_valid"]
        and cell["handoff"]["all_checks_pass"]
        and cell["override_readback_exact"]
        for cell in cells
    )
    passing = [cell for cell in cells if cell["cell_green"]]
    one_group = [
        cell for cell in passing if cell["final_group_count"] == 1
    ]
    selected = None
    if one_group:
        order = {
            variant_id: index
            for index, variant_id in enumerate(prereg["execution_order"])
        }
        selected = min(
            one_group, key=lambda item: order[item["variant_id"]]
        )
    combined_pass = any(
        cell["cell_green"] and cell["final_group_count"] == 2
        for cell in cells
    )
    if not valid:
        status = "INVALID_T44_CORRECTED_FORWARD_FACTORIAL"
        decision = "ZERO_POLICY_DECISION_WEIGHT"
    elif selected is not None:
        status = "PASS_T44_CORRECTED_FORWARD_ONE_BLOCK_CAUSE"
        decision = (
            f"EARN_T45_{selected['variant_id']}_"
            "UNIFORM_TRANSFORM_PREREGISTRATION"
        )
    elif combined_pass:
        status = "PASS_T44_CORRECTED_FORWARD_COUPLED_ONLY"
        decision = "CLOSE_POSTHOC_FORWARD_BLOCK_ENDPOINT_DUPLICATION"
    else:
        status = "PASS_T44_CORRECTED_FORWARD_NO_REPAIR"
        decision = "CLOSE_FORWARD_ACTOR_BLOCK_SUBSTITUTION"
    payload: dict[str, Any] = {
        "schema_version": (
            "open_duck.t44_corrected_forward_factorial_result.v1"
        ),
        "status": status,
        "decision": decision,
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "repository_commit": commit,
        "cells": cells,
        "summary": {
            "formal_behavior_cells": len(cells),
            "valid_cells": sum(
                bool(
                    cell["trace_valid"]
                    and cell["handoff"]["all_checks_pass"]
                    and cell["override_readback_exact"]
                )
                for cell in cells
            ),
            "green_cells": len(passing),
            "passing_variants": [
                cell["variant_id"] for cell in passing
            ],
            "one_group_passing_variants": [
                cell["variant_id"] for cell in one_group
            ],
            "selected_mechanism_variant_diagnostic": (
                selected["variant_id"] if selected is not None else None
            ),
            "selected_final_groups": (
                selected["final_groups"] if selected is not None else None
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
    payload["result_sha256"] = canonical_sha256(payload)
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    table = [
        "| variant | final groups | green | samples | tracking p95 |",
        "|---|---|---:|---:|---:|",
    ]
    for cell in cells:
        table.append(
            "| `{}` | `{}` | `{}` | `{}` | `{:.9f}` |".format(
                cell["variant_id"],
                ",".join(cell["final_groups"]),
                cell["cell_green"],
                cell["behavior"]["samples"],
                cell["behavior"]["pitch_tracking_p95_rad"],
            )
        )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T44 corrected forward actor-block factorial result",
                "",
                f"- Status: `{status}`",
                f"- Decision: `{decision}`",
                "",
                *table,
                "",
                "No hybrid policy is promoted. A one-block pass authorizes "
                "only a separately preregistered uniform-transform screen.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(status)
    print(f"decision={decision}")
    print(f"passing_variants={payload['summary']['passing_variants']}")
    print(
        "selected="
        f"{payload['summary']['selected_mechanism_variant_diagnostic']}"
    )
    print(f"result_sha256={payload['result_sha256']}")
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
