#!/usr/bin/env python3
"""Run T94's frozen 40-cell automatic-calibration manifold screen."""

from __future__ import annotations

import argparse
from concurrent.futures import as_completed, ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs" / "analysis"
sys.path.insert(0, str(TOOLS))
import run_t7_universal_response_support as t7  # noqa: E402


PREREG = ANALYSIS / "t94_r2_calibration_manifold_preregistration_v3.json"
OUTPUT = ANALYSIS / "t94_r2_calibration_manifold_result.json"
MARKDOWN = ANALYSIS / "T94_R2_CALIBRATION_MANIFOLD_RESULT_20260728.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any, ignored: str) -> str:
    payload = dict(value)
    payload.pop(ignored, None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def t7_compatible_prereg(prereg: dict[str, Any]) -> dict[str, Any]:
    inputs = prereg["repository_inputs"]
    original = json.loads(
        Path(inputs["t7_preregistration"]["path"]).read_text(encoding="utf-8")
    )
    return {
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "repository_inputs": {
            "evaluator": inputs["evaluator"],
            "fit_p30": inputs["fit_p30"],
            "fit_p31_34": inputs["fit_p31_34"],
            "reference_features": inputs["reference_features"],
        },
        "playground": prereg["playground"],
        "frozen_policy": prereg["frozen_policy"],
        "matrix": {
            "command_x_m_s": prereg["matrix"]["command_x_m_s"],
            "seed": prereg["matrix"]["seed"],
            "duration_ticks": prereg["matrix"]["duration_ticks"],
            "frequency_hz": prereg["matrix"]["frequency_hz"],
        },
        "behavior_contract": original["behavior_contract"],
    }


def context_prototypes() -> dict[tuple[str, str], np.ndarray]:
    source = json.loads(
        (ANALYSIS / "t7_universal_response_support_result.json").read_text(
            encoding="utf-8"
        )
    )
    return {
        (cell["configuration_id"], cell["fit_id"]): np.asarray(
            cell["response_context"], dtype=np.float64
        )
        for cell in source["cells"]
        if cell["repeat"] == 0
    }


def longest_true(mask: np.ndarray) -> int:
    current = np.zeros(mask.shape[1], dtype=np.int64)
    longest = np.zeros(mask.shape[1], dtype=np.int64)
    for row in mask:
        current = np.where(row, current + 1, 0)
        longest = np.maximum(longest, current)
    return int(np.max(longest))


def analyze(
    prereg: dict[str, Any],
    manifest: dict[str, Any],
    prototypes: dict[tuple[str, str], np.ndarray],
) -> dict[str, Any]:
    contract = manifest["block_contract"]
    records = t7.read_trace(Path(manifest["trace"]["path"]))
    evaluation = json.loads(
        Path(manifest["evaluation"]["path"]).read_text(encoding="utf-8")
    )
    actions = np.asarray([row["action"] for row in records], np.float32)
    h_in = np.asarray(
        [row["policy_state_input"]["h_in"][0] for row in records], np.float32
    )
    h_out = np.asarray(
        [row["policy_state_output"]["h_out"][0] for row in records], np.float32
    )
    p_in = np.asarray(
        [
            row["policy_state_input"]["previous_action"][0]
            for row in records
        ],
        np.float32,
    )
    p_out = np.asarray(
        [
            row["policy_state_output"]["previous_action_out"][0]
            for row in records
        ],
        np.float32,
    )
    context = h_out[prereg["matrix"]["response_context_tick"]].astype(
        np.float64
    )
    target = np.asarray(
        prereg["frozen_policy"]["universal_raw_action"], np.float32
    )
    graph = t7.graph_contract(t7_compatible_prereg(prereg))
    delta = np.asarray(graph["maximum_action_delta"], np.float32)
    expected = []
    previous = np.zeros(14, np.float32)
    for _ in records:
        previous = np.maximum(
            np.minimum(target, np.minimum(previous + delta, 1.0)),
            np.maximum(previous - delta, -1.0),
        )
        expected.append(previous.copy())
    exact_chain = bool(
        np.array_equal(actions, np.asarray(expected))
        and np.array_equal(p_out, actions)
        and np.array_equal(p_in[0], np.zeros(14, np.float32))
        and np.array_equal(p_in[1:], p_out[:-1])
        and np.array_equal(h_in[0], np.zeros(64, np.float32))
        and np.array_equal(h_in[1:], h_out[:-1])
    )
    distances = {
        f"{configuration}:{fit}": float(np.linalg.norm(context - prototype))
        for (configuration, fit), prototype in prototypes.items()
    }
    nearest = min(distances, key=distances.get)
    predicted_fit = nearest.split(":")[1]
    same_fit = {
        key: value
        for key, value in distances.items()
        if key.endswith(f":{predicted_fit}")
    }
    nearest_config = min(same_fit, key=same_fit.get).split(":")[0]
    actual_id = contract["configuration"]["id"]
    negative_expected = actual_id == "TORSO_COM_X_NEG"
    negative_predicted = nearest_config == "TORSO_COM_X_NEG"
    best = sorted(same_fit.values())
    nearest_margin = best[1] - best[0]
    forces = np.abs(
        np.asarray([row["actuator_force_nm"] for row in records], np.float64)
    )
    current = forces / 0.784532
    runs = evaluation.get("runs") or []
    run = runs[0] if len(runs) == 1 else {}
    dynamics = run.get("dynamics_override") or {}
    override = contract["configuration"]["override"]
    key, expected_value = next(iter(override.items()))
    checks = {
        "ticks_exact": len(records) == 250
        and all(row["tick"] == index for index, row in enumerate(records)),
        "duration_complete": (run.get("emergence") or {}).get(
            "termination_reason"
        )
        == "duration_complete",
        "context_finite": bool(np.all(np.isfinite(context))),
        "action_and_recurrent_chains_exact": exact_chain,
        "dynamics_override_value_exact": (
            dynamics.get("enabled") is True
            and dynamics.get("key") == key
            and dynamics.get("value") == expected_value
        ),
        "minimum_height": min(row["base_height_m"] for row in records) >= 0.12,
        "pitch_p95": float(
            np.percentile(
                np.abs([row["body_pitch_rad"] for row in records]), 95
            )
        )
        <= 0.25,
        "zero_saturation": not any(
            bool(np.any(row["action_saturated"])) for row in records
        ),
        "zero_rate_excess": max(
            max(
                float(np.max(row["sent_target_rate_excess_rad_s"])),
                float(np.max(row["conservative_rate_excess_rad_s"])),
            )
            for row in records
        ) <= 0.0,
        "overcurrent_duration": longest_true(current > 2.0) <= 99,
        "overload_duration": longest_true(forces > 1.5298374) <= 99,
    }
    return {
        "condition_index": contract["configuration"]["condition_index"],
        "configuration_id": actual_id,
        "fit_id": contract["fit_id"],
        "pass": all(checks.values()),
        "checks": checks,
        "context": context.astype(float).tolist(),
        "context_sha256": t7.array_sha256(context.astype(np.float32)),
        "nearest_prototype": nearest,
        "predicted_fit": predicted_fit,
        "fit_correct": predicted_fit == contract["fit_id"],
        "nearest_same_fit_configuration": nearest_config,
        "negative_expected": negative_expected,
        "negative_predicted": negative_predicted,
        "negative_correct": negative_expected == negative_predicted,
        "nearest_same_fit_margin": nearest_margin,
        "prototype_distances": distances,
        "trace": manifest["trace"],
        "evaluation": manifest["evaluation"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-root", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise PermissionError("T94 requires --execute")
    for path in (OUTPUT, MARKDOWN, args.cache_root):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T94 output: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    if (
        prereg["status"] != "PREREGISTERED_T94_R2_CALIBRATION_MANIFOLD_V3"
        or canonical_sha256(prereg, "preregistered_contract_sha256")
        != prereg["preregistered_contract_sha256"]
    ):
        raise ValueError("T94 preregistration changed")
    for name, item in prereg["repository_inputs"].items():
        path = Path(item["path"])
        if sha256(path) != item["sha256"]:
            raise ValueError(f"T94 input changed: {name}")
    compatible = t7_compatible_prereg(prereg)
    prototypes = context_prototypes()
    args.cache_root.mkdir(parents=True)
    plans = [
        (configuration, fit)
        for configuration in prereg["conditions"]
        for fit in prereg["fits"]
    ]

    def execute(plan: tuple[dict[str, Any], str]) -> dict[str, Any]:
        configuration, fit = plan
        manifest, _ = t7.run_or_load_block(
            compatible, configuration, fit, 0, args.cache_root
        )
        return analyze(prereg, manifest, prototypes)

    cells: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(execute, plan) for plan in plans]
        for future in as_completed(futures):
            cell = future.result()
            cells.append(cell)
            print(
                f"T94 {len(cells):02}/40 {cell['configuration_id']} "
                f"{cell['fit_id']} cell={cell['pass']} "
                f"fit={cell['fit_correct']} "
                f"negative={cell['negative_correct']}",
                flush=True,
            )
    fit_order = {name: index for index, name in enumerate(prereg["fits"])}
    cells.sort(key=lambda item: (item["condition_index"], fit_order[item["fit_id"]]))
    anchors = {
        "FLOOR_FRICTION_HI": "NOMINAL",
        "ARMATURE_LO": "NOMINAL",
        "TORSO_COM_X_NEG": "TORSO_COM_X_NEG",
        "TORSO_COM_X_POS": "TORSO_COM_X_POS",
    }
    anchor_checks = []
    for cell in cells:
        if cell["configuration_id"] not in anchors:
            continue
        expected = prototypes[(anchors[cell["configuration_id"]], cell["fit_id"])]
        observed = np.asarray(cell["context"], np.float64)
        anchor_checks.append(
            {
                "configuration_id": cell["configuration_id"],
                "fit_id": cell["fit_id"],
                "expected_t7_prototype": anchors[cell["configuration_id"]],
                "bit_exact": np.array_equal(
                    observed.astype(np.float32), expected.astype(np.float32)
                ),
            }
        )
    true_positives = sum(
        cell["negative_expected"] and cell["negative_predicted"]
        for cell in cells
    )
    false_positives = sum(
        not cell["negative_expected"] and cell["negative_predicted"]
        for cell in cells
    )
    checks = {
        "all_40_calibration_cells_pass": len(cells) == 40
        and all(cell["pass"] for cell in cells),
        "all_fit_classifications_exact": all(
            cell["fit_correct"] for cell in cells
        ),
        "negative_com_true_positives_exact": true_positives == 2,
        "negative_com_false_positives_zero": false_positives == 0,
        "all_nearest_prototype_margins_strictly_positive": all(
            cell["nearest_same_fit_margin"] > 0.0 for cell in cells
        ),
        "all_eight_available_t7_anchors_bit_exact": (
            len(anchor_checks) == 8
            and all(item["bit_exact"] for item in anchor_checks)
        ),
        "no_locomotion_policy_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    value: dict[str, Any] = {
        "schema_version": "open_duck.t94_r2_calibration_manifold_result.v1",
        "status": (
            "PASS_T94_R2_CALIBRATION_MANIFOLD"
            if passed
            else "HOLD_T94_R2_CALIBRATION_MANIFOLD"
        ),
        "classification": (
            "R2_CALIBRATION_MANIFOLD_ROUTABLE"
            if passed
            else "R2_CALIBRATION_MANIFOLD_NOT_ROUTABLE"
        ),
        "decision": (
            "EARN_CALIBRATION_ROUTED_FIXED_EXPERT_CPU_PREREGISTRATION_ONLY"
            if passed
            else "CLOSE_CALIBRATION_ROUTED_EXPERT_MECHANISM"
        ),
        "checks": checks,
        "failed_checks": failed,
        "summary": {
            "cells": len(cells),
            "passing_calibration_cells": sum(cell["pass"] for cell in cells),
            "fit_correct_cells": sum(cell["fit_correct"] for cell in cells),
            "negative_com_true_positives": true_positives,
            "negative_com_false_positives": false_positives,
            "minimum_nearest_same_fit_margin": min(
                cell["nearest_same_fit_margin"] for cell in cells
            ),
        },
        "anchor_checks": anchor_checks,
        "cells": cells,
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "execution": {
            "simulator_calibration_ticks": 40 * 250,
            "locomotion_policy_ticks": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "successor_cpu_preregistration": passed,
            "locomotion_behavior": False,
            "hosted_training": False,
            "deployment": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["result_sha256"] = canonical_sha256(value, "result_sha256")
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T94 R2 calibration-manifold result",
                "",
                f"- Status: `{value['status']}`",
                f"- Classification: `{value['classification']}`",
                f"- Decision: `{value['decision']}`",
                f"- Failed checks: `{failed}`",
                f"- Calibration cells: `{value['summary']['passing_calibration_cells']}/40`",
                f"- Fit classifier: `{value['summary']['fit_correct_cells']}/40`",
                (
                    "- Negative-COM detector TP/FP: "
                    f"`{true_positives}/{false_positives}`"
                ),
                "- Training / Colab / RDK / robot: `0 / 0 / 0 / 0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"classification={value['classification']}")
    print(f"decision={value['decision']}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
