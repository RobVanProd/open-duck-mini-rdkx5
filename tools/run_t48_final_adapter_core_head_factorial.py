#!/usr/bin/env python3
"""Run T48's three-cell final-adapter core/head causal factorial."""

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
    / "t48_final_adapter_core_head_factorial_preregistration.json"
)
OUTPUT = ANALYSIS / "t48_final_adapter_core_head_factorial_result.json"
MARKDOWN = (
    ANALYSIS
    / "T48_FINAL_ADAPTER_CORE_HEAD_FACTORIAL_RESULT_20260728.md"
)
CACHE_ROOT = (
    Path("D:/CodexArtifacts/open-duck-policy")
    / "t48_final_adapter_core_head_factorial_run_v1"
)

sys.path.insert(0, str(ROOT / "tools"))
from run_t6_corrected_robustness_screen import (  # noqa: E402
    behavior_row,
    classify_behavior,
    exact_override_readback,
    trace_summary,
)
from run_t8_state_coherent_handoff import (  # noqa: E402
    read_trace,
    state_handoff_summary,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


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
        raise ValueError("changed T48 preregistration")
    if prereg["status"] != (
        "PREREGISTERED_T48_FINAL_ADAPTER_CORE_HEAD_FACTORIAL"
    ):
        raise ValueError("T48 preregistration is not green")
    for item in prereg["frozen_inputs"].values():
        path = Path(item["path"])
        if sha256(path) != item["sha256"]:
            raise ValueError(f"changed T48 frozen input: {path}")
    for variant in prereg["variants"]:
        item = variant["policy"]
        if sha256(Path(item["path"])) != item["sha256"]:
            raise ValueError("changed T48 variant policy")
    for item in (
        prereg["fit"],
        prereg["calibrator"],
        prereg["reference_feature_table"],
    ):
        if sha256(Path(item["path"])) != item["sha256"]:
            raise ValueError("changed T48 evaluated input")


def require_clean_worktree() -> str:
    status = subprocess.run(
        ["git", "status", "--short"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if status.strip():
        raise RuntimeError("formal T48 execution requires a clean worktree")
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def evaluate_variant(
    prereg: dict[str, Any],
    variant: dict[str, Any],
    environment: dict[str, str],
) -> dict[str, Any]:
    cell = prereg["cell"]
    condition = cell["condition"]
    policy = variant["policy"]
    root = CACHE_ROOT / variant["variant_id"]
    root.mkdir(parents=True)
    trace_dir = root / "traces"
    trace_dir.mkdir()
    evaluation_path = root / "evaluation.json"
    stdout_path = root / "stdout.log"
    command_x = float(cell["command_x_m_s"])
    command = [
        sys.executable,
        prereg["frozen_inputs"]["worker"]["path"],
        "--formal",
        "--policy",
        policy["path"],
        "--policy-sha256",
        policy["sha256"],
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
            condition["override"],
            separators=(",", ":"),
            sort_keys=True,
        ),
        "--commands",
        str(command_x),
        "--seed",
        str(cell["seed"]),
        "--duration-s",
        str(cell["duration_s"]),
        "--trace-dir",
        str(trace_dir),
        "--output-json",
        str(evaluation_path),
    ]
    with stdout_path.open("w", encoding="utf-8") as stream:
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
    trace_path = (
        trace_dir
        / (
            f"x{command_x:.3f}_seed{cell['seed']}_"
            f"{Path(policy['path']).stem}.jsonl"
        )
    )
    if (
        completed.returncode != 0
        or not evaluation_path.is_file()
        or not trace_path.is_file()
    ):
        raise RuntimeError(
            f"T48 worker failed for {variant['variant_id']}: "
            f"{completed.returncode}; {stdout_path}"
        )
    evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
    if evaluation.get("formal") is not True or len(evaluation["runs"]) != 1:
        raise ValueError("T48 worker returned the wrong formal matrix")
    run = evaluation["runs"][0]
    records = read_trace(trace_path)
    behavior = classify_behavior(
        behavior_row(run), prereg["behavior_contract"]
    )
    protection = trace_summary(
        trace_path, prereg["protection_contract"]
    )
    handoff = state_handoff_summary(run, records)
    readback = exact_override_readback(
        run.get("dynamics_override"), condition["override"]
    )
    trace_valid = (
        protection["ticks_contiguous_from_zero"]
        and protection["rows"] == behavior["samples"]
    )
    cell_green = (
        trace_valid
        and behavior["core_pass"]
        and behavior["replacement_quality_pass"]
        and protection["duration_protection_pass"]
        and protection["maximum_full_measured_vector_excess_rad_s"] == 0.0
        and handoff["all_checks_pass"]
        and readback
    )
    return {
        "variant_id": variant["variant_id"],
        "half_groups": variant["half_groups"],
        "half_group_count": variant["half_group_count"],
        "semantically_equals_half_endpoint": variant[
            "semantically_equals_half_endpoint"
        ],
        "policy": policy,
        "behavior": behavior,
        "protection": protection,
        "handoff": handoff,
        "override_readback_exact": readback,
        "trace_valid": trace_valid,
        "cell_green": cell_green,
        "execution": {
            "command": command,
            "evaluation": receipt(evaluation_path),
            "stdout": receipt(stdout_path),
            "trace": receipt(trace_path),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise SystemExit("refusing T48 execution without --execute")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    verify(prereg)
    commit = require_clean_worktree()
    CACHE_ROOT.mkdir(parents=True, exist_ok=False)
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
        item = evaluate_variant(prereg, variant, environment)
        cells.append(item)
        print(
            json.dumps(
                {
                    "variant_id": item["variant_id"],
                    "half_groups": item["half_groups"],
                    "cell_green": item["cell_green"],
                    "samples": item["behavior"]["samples"],
                    "elapsed_s": time.time() - started,
                }
            ),
            flush=True,
        )
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
        item["cell_green"] and item["half_group_count"] == 2
        for item in cells
    )
    if not valid:
        status = "INVALID_T48_FINAL_ADAPTER_CORE_HEAD_FACTORIAL"
        decision = "ZERO_POLICY_DECISION_WEIGHT"
    elif selected is not None:
        status = "PASS_T48_FINAL_ADAPTER_ONE_SUBBLOCK_CAUSE"
        decision = (
            f"EARN_T49_{selected['variant_id']}_"
            "UNIFORM_TRANSFORM_PREREGISTRATION"
        )
    elif combined_pass:
        status = "PASS_T48_FINAL_ADAPTER_COUPLED_ONLY"
        decision = "CLOSE_T48_ENDPOINT_DUPLICATING_ADAPTER_SUBSTITUTION"
    else:
        status = "PASS_T48_FINAL_ADAPTER_NO_REPAIR"
        decision = "CLOSE_T48_ADAPTER_SUBBLOCK_SUBSTITUTION"
    result: dict[str, Any] = {
        "schema_version": (
            "open_duck.t48_final_adapter_core_head_factorial_result.v1"
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
    table = [
        "| variant | half groups | green | samples | tracking p95 |",
        "|---|---|---:|---:|---:|",
    ]
    for item in cells:
        table.append(
            "| `{}` | `{}` | `{}` | `{}` | `{:.9f}` |".format(
                item["variant_id"],
                ",".join(item["half_groups"]),
                item["cell_green"],
                item["behavior"]["samples"],
                item["behavior"]["pitch_tracking_p95_rad"],
            )
        )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T48 final-adapter core/head factorial result",
                "",
                f"- Status: `{status}`",
                f"- Decision: `{decision}`",
                "",
                *table,
                "",
                "A one-subblock pass authorizes only a separate uniform "
                "transform qualification. The combined variant duplicates "
                "the half endpoint and cannot promote.",
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
