#!/usr/bin/env python3
"""Compose the proven negative plateau with T162's positive repair."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import time
from typing import Any

import numpy as np
import onnxruntime as ort

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    receipt,
    verify,
)
from run_t149_negative_context_command_plateau_transform import (
    CAP_M_S,
    equivalence_contract,
    transform,
)


PREREG = ANALYSIS / "t164_prior_repair_composition_preregistration.json"
RESULT = ANALYSIS / "t164_prior_repair_composition_result.json"
MARKDOWN = ANALYSIS / "T164_PRIOR_REPAIR_COMPOSITION_RESULT_20260729.md"
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t164_prior_repair_composition_v1"
)


def cross_graph_contract(
    composed: Path,
    t149_graph: Path,
    t162_graph: Path,
    contexts: list[dict[str, Any]],
    seed: int,
) -> dict[str, Any]:
    composed_session = ort.InferenceSession(
        str(composed), providers=["CPUExecutionProvider"]
    )
    negative_session = ort.InferenceSession(
        str(t149_graph), providers=["CPUExecutionProvider"]
    )
    positive_session = ort.InferenceSession(
        str(t162_graph), providers=["CPUExecutionProvider"]
    )
    output_names = [
        item.name for item in composed_session.get_outputs()
    ]
    rng = np.random.default_rng(seed)
    rows = []
    all_exact = True
    all_finite = True
    for context_row in contexts:
        context = np.asarray(
            context_row["context"], dtype=np.float32
        ).reshape(1, 64)
        population = context_row["population"]
        reference_session = (
            negative_session
            if population == "com_x_negative"
            else positive_session
        )
        for command in (0.0, 0.074, 0.077, 0.080):
            exact = True
            finite = True
            for _ in range(32):
                obs = rng.normal(0.0, 0.25, (1, 115)).astype(np.float32)
                obs[0, 6] = np.float32(command)
                previous = rng.uniform(
                    -0.9, 0.9, (1, 14)
                ).astype(np.float32)
                hidden = rng.uniform(
                    -0.9, 0.9, (1, 64)
                ).astype(np.float32)
                feed = {
                    "obs": obs,
                    "previous_action": previous,
                    "h_in": hidden,
                    "calibration_context": context,
                }
                actual = composed_session.run(output_names, feed)
                expected = reference_session.run(output_names, feed)
                exact &= all(
                    np.array_equal(left, right)
                    for left, right in zip(actual, expected)
                )
                finite &= all(
                    np.all(np.isfinite(output)) for output in actual
                )
            rows.append(
                {
                    "population": population,
                    "fit_id": context_row["fit_id"],
                    "command_x_m_s": command,
                    "reference_graph": (
                        "T149B_NEGATIVE_PLATEAU"
                        if population == "com_x_negative"
                        else "T162_POSITIVE_ENDPOINT"
                    ),
                    "samples": 32,
                    "all_outputs_bit_exact": bool(exact),
                    "all_outputs_finite": bool(finite),
                }
            )
            all_exact &= exact
            all_finite &= finite
    return {
        "provider": composed_session.get_providers()[0],
        "rows": rows,
        "samples": sum(row["samples"] for row in rows),
        "all_outputs_bit_exact": bool(all_exact),
        "all_outputs_finite": bool(all_finite),
        "negative_matches_t149b": all(
            row["all_outputs_bit_exact"]
            for row in rows
            if row["population"] == "com_x_negative"
        ),
        "nominal_and_positive_match_t162": all(
            row["all_outputs_bit_exact"]
            for row in rows
            if row["population"] != "com_x_negative"
        ),
        "x0_exact": all(
            row["all_outputs_bit_exact"]
            for row in rows
            if row["command_x_m_s"] == 0.0
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    if RESULT.exists() or MARKDOWN.exists() or WORK.exists():
        raise FileExistsError("refusing to overwrite T164 output")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T164 execution requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T164_PRIOR_REPAIR_COMPOSITION"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T164 preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, f"frozen_inputs.{name}")
    for index, item in enumerate(prereg["graphs"]):
        verify(item["t149b"], f"graphs[{index}].t149b")
        verify(item["t162"], f"graphs[{index}].t162")

    WORK.mkdir(parents=True)
    outputs = []
    started = time.time()
    for graph in prereg["graphs"]:
        step = str(graph["step"])
        destination = WORK / step / "composed_three_way_router.onnx"
        structure = transform(Path(graph["t162"]["path"]), destination)
        equivalence = equivalence_contract(
            Path(graph["t162"]["path"]),
            destination,
            prereg["contexts"],
            seed=int(prereg["inference"]["seed"]) + int(step),
        )
        cross = cross_graph_contract(
            destination,
            Path(graph["t149b"]["path"]),
            Path(graph["t162"]["path"]),
            prereg["contexts"],
            int(prereg["inference"]["seed"]) + int(step) + 1,
        )
        outputs.append(
            {
                "step": int(step),
                "structure": structure,
                "negative_cap_equivalence": equivalence,
                "cross_graph_equivalence": cross,
            }
        )

    checks = {
        "two_graphs": len(outputs) == 2,
        "all_nine_nodes_inserted": all(
            row["structure"]["nine_nodes_inserted"] for row in outputs
        ),
        "all_two_raw_obs_consumers_rewired_exact": all(
            row["structure"]["two_raw_obs_consumers_rewired_exact"]
            for row in outputs
        ),
        "all_other_nodes_byte_exact": all(
            row["structure"]["all_other_nodes_byte_exact"]
            for row in outputs
        ),
        "all_existing_initializers_byte_exact": all(
            row["structure"]["existing_initializers_byte_exact"]
            for row in outputs
        ),
        "all_abis_exact": all(
            row["structure"]["abi_exact"] for row in outputs
        ),
        "all_cap_equivalence_exact": all(
            row["negative_cap_equivalence"]["all_rows_bit_exact"]
            and row["negative_cap_equivalence"]["all_chains_bit_exact"]
            for row in outputs
        ),
        "all_negative_matches_t149b": all(
            row["cross_graph_equivalence"]["negative_matches_t149b"]
            for row in outputs
        ),
        "all_nominal_positive_matches_t162": all(
            row["cross_graph_equivalence"][
                "nominal_and_positive_match_t162"
            ]
            for row in outputs
        ),
        "all_x0_exact": all(
            row["cross_graph_equivalence"]["x0_exact"]
            for row in outputs
        ),
        "all_outputs_finite": all(
            row["cross_graph_equivalence"]["all_outputs_finite"]
            for row in outputs
        ),
        "cpu_only": all(
            row["cross_graph_equivalence"]["provider"]
            == "CPUExecutionProvider"
            for row in outputs
        ),
        "negative_cap_exact": float(CAP_M_S) == float(np.float32(0.074)),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    status = (
        "PASS_T164_PRIOR_REPAIR_COMPOSITION"
        if not failed
        else "HOLD_T164_PRIOR_REPAIR_COMPOSITION"
    )
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t164_prior_repair_composition_result.v1"
        ),
        "status": status,
        "decision": (
            "EARN_T165_COMPOSED_FULL_R2_PREREGISTRATION_ONLY"
            if not failed
            else "HOLD_FULL_R2_AND_AUDIT_REPAIR_COMPOSITION"
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "graphs": outputs,
        "execution": {
            "inference_samples": sum(
                row["negative_cap_equivalence"]["sample_rows"]
                + row["cross_graph_equivalence"]["samples"]
                for row in outputs
            ),
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
            "wall_seconds": time.time() - started,
        },
        "authority": {
            "composed_full_r2_preregistration": not failed,
            "behavior_matrix": False,
            "training": False,
            "gate5": False,
            "robot_or_rdk": False,
        },
    }
    value["result_sha256"] = canonical_sha256(value)
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T164 prior-repair composition result\n\n"
        f"- Status: `{status}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Exact inference samples: "
        f"`{value['execution']['inference_samples']}`\n"
        "- Negative contexts match T149B; nominal/positive contexts match "
        "T162 bit-for-bit.\n"
        "- Behavior/training/hosted/robot: `0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(status)
    print(f"decision={value['decision']}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
