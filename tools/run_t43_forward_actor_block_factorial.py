#!/usr/bin/env python3
"""Run T43's three-cell forward actor-block causal factorial."""

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
    ANALYSIS / "t43_forward_actor_block_factorial_preregistration.json"
)
OUTPUT = ANALYSIS / "t43_forward_actor_block_factorial_result.json"
MARKDOWN = (
    ANALYSIS / "T43_FORWARD_ACTOR_BLOCK_FACTORIAL_RESULT_20260728.md"
)
CACHE_ROOT = (
    Path("D:/CodexArtifacts/open-duck-policy")
    / "t43_forward_actor_block_factorial_run_v1"
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


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


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
        raise ValueError("changed T43 preregistration")
    if (
        prereg["status"]
        != "PREREGISTERED_T43_FORWARD_ACTOR_BLOCK_FACTORIAL"
    ):
        raise ValueError("T43 preregistration is not green")
    for item in prereg["frozen_inputs"].values():
        path = Path(item["path"])
        if sha256(path) != item["sha256"]:
            raise ValueError(f"changed T43 frozen input: {path}")
    for variant in prereg["variants"]:
        item = variant["policy"]
        path = Path(item["path"])
        if sha256(path) != item["sha256"]:
            raise ValueError(f"changed T43 variant asset: {path}")
    for item in (
        prereg["fit"],
        prereg["calibrator"],
        prereg["reference_feature_table"],
    ):
        path = Path(item["path"])
        if sha256(path) != item["sha256"]:
            raise ValueError(f"changed T43 evaluated input: {path}")


def require_clean_worktree() -> str:
    status = subprocess.run(
        ["git", "status", "--short"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if status.strip():
        raise RuntimeError("formal T43 execution requires a clean worktree")
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
        str(cell["command_x_m_s"]),
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
            f"x0.080_seed{cell['seed']}_"
            f"{Path(policy['path']).stem}.jsonl"
        )
    )
    if (
        completed.returncode != 0
        or not evaluation_path.is_file()
        or not trace_path.is_file()
    ):
        raise RuntimeError(
            f"T43 worker failed for {variant['variant_id']}: "
            f"{completed.returncode}; {stdout_path}"
        )
    evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
    if evaluation.get("formal") is not True or len(evaluation["runs"]) != 1:
        raise ValueError("T43 worker returned the wrong formal matrix")
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
        "final_groups": variant["final_groups"],
        "final_group_count": variant["final_group_count"],
        "semantically_equals_final_endpoint": variant[
            "semantically_equals_final_endpoint"
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
        raise SystemExit("refusing T43 outcome execution without --execute")
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
        cell = evaluate_variant(prereg, variant, environment)
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
            one_group,
            key=lambda item: order[item["variant_id"]],
        )
    combined_pass = any(
        cell["cell_green"] and cell["final_group_count"] == 2
        for cell in cells
    )
    if not valid:
        status = "INVALID_T43_FORWARD_ACTOR_BLOCK_FACTORIAL"
        decision = "ZERO_POLICY_DECISION_WEIGHT"
    elif selected is not None:
        status = "PASS_T43_FORWARD_ACTOR_BLOCK_ONE_BLOCK_CAUSE"
        decision = (
            f"EARN_T44_{selected['variant_id']}_"
            "UNIFORM_TRANSFORM_PREREGISTRATION"
        )
    elif combined_pass:
        status = "PASS_T43_FORWARD_ACTOR_BLOCK_COUPLED_ONLY"
        decision = (
            "CLOSE_POSTHOC_FORWARD_BLOCK_ENDPOINT_DUPLICATION"
        )
    else:
        status = "PASS_T43_FORWARD_ACTOR_BLOCK_NO_REPAIR"
        decision = "CLOSE_FORWARD_ACTOR_BLOCK_SUBSTITUTION"
    payload: dict[str, Any] = {
        "schema_version": (
            "open_duck.t43_forward_actor_block_factorial_result.v1"
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
                "# T43 forward actor-block factorial result",
                "",
                f"- Status: `{status}`",
                f"- Decision: `{decision}`",
                "",
                *table,
                "",
                "This is causal attribution only. No hybrid policy is "
                "promoted and no training, Gate 5, RDK-X5, or robot work "
                "is authorized.",
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
