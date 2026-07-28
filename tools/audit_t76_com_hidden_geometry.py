#!/usr/bin/env python3
"""Run T76's frozen paired COM-hidden response-geometry audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import onnx
from onnx import numpy_helper


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t76_com_hidden_geometry_preregistration.json"
OUTPUT = ANALYSIS / "t76_com_hidden_geometry_result.json"
MARKDOWN = ANALYSIS / "T76_COM_HIDDEN_GEOMETRY_RESULT_20260728.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any, hash_key: str) -> str:
    payload = dict(value)
    payload.pop(hash_key, None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def verify_receipt(item: dict[str, Any]) -> bool:
    path = Path(item["path"])
    return (
        path.is_file()
        and path.stat().st_size == item["bytes"]
        and sha256(path) == item["sha256"]
    )


def read_h_out(path: Path, ticks: set[int]) -> dict[int, np.ndarray]:
    rows: dict[int, np.ndarray] = {}
    with path.open("r", encoding="utf-8") as stream:
        for line in stream:
            if not line.strip():
                continue
            row = json.loads(line)
            tick = int(row["tick"])
            if tick in ticks:
                value = np.asarray(
                    row["policy_state_output"]["h_out"], dtype=np.float64
                )
                if value.shape != (1, 64) or not np.all(np.isfinite(value)):
                    raise RuntimeError(f"invalid h_out in {path} at tick {tick}")
                rows[tick] = value[0]
    missing = sorted(ticks - set(rows))
    if missing:
        raise RuntimeError(f"{path} missing frozen ticks {missing}")
    return rows


def initializer(path: Path, name: str) -> np.ndarray:
    model = onnx.load(str(path), load_external_data=False)
    values = {
        item.name: numpy_helper.to_array(item)
        for item in model.graph.initializer
    }
    if name not in values:
        raise RuntimeError(f"{path} missing initializer {name}")
    return np.asarray(values[name], dtype=np.float64)


def cosine_rows(rows: np.ndarray, direction: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(rows, axis=1)
    if np.any(norms <= 0.0):
        raise RuntimeError("zero paired COM hidden delta")
    return (rows @ direction) / norms


def main() -> int:
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T76 result")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    issues: list[str] = []
    if (
        canonical_sha256(prereg, "preregistered_contract_sha256")
        != prereg["preregistered_contract_sha256"]
    ):
        issues.append("preregistration_sha")
    for name, item in prereg["frozen_inputs"].items():
        if not verify_receipt(item):
            issues.append(f"frozen_input.{name}")
    for population_name in ("nominal_traces", "shifted_traces"):
        for key, item in prereg[population_name].items():
            if not verify_receipt(item):
                issues.append(f"{population_name}.{key}")
    for policy in prereg["policies"]:
        if not verify_receipt(policy):
            issues.append(f"policy.{policy['checkpoint_id']}")
    if issues:
        raise RuntimeError(f"T76 frozen-input failure: {issues}")

    ticks = set(prereg["population"]["sample_ticks"])
    policy_by_checkpoint = {
        item["checkpoint_id"]: item for item in prereg["policies"]
    }
    thresholds = prereg["thresholds"]
    checkpoint_results: list[dict[str, Any]] = []

    for checkpoint in prereg["population"]["checkpoints"]:
        basis: list[np.ndarray] = []
        heldout: list[np.ndarray] = []
        records: list[dict[str, Any]] = []
        for fit in prereg["population"]["fits"]:
            for command in prereg["population"]["commands_x_m_s"]:
                key = f"{checkpoint}|{fit}|{command:.3f}"
                nominal = read_h_out(
                    Path(prereg["nominal_traces"][key]["path"]), ticks
                )
                shifted = read_h_out(
                    Path(prereg["shifted_traces"][key]["path"]), ticks
                )
                group = (
                    "basis"
                    if fit == "p30" and command in (0.074, 0.080)
                    else "heldout"
                )
                for tick in sorted(ticks):
                    delta = shifted[tick] - nominal[tick]
                    (basis if group == "basis" else heldout).append(delta)
                    records.append(
                        {
                            "fit_id": fit,
                            "command_x_m_s": command,
                            "tick": tick,
                            "group": group,
                            "delta_l2": float(np.linalg.norm(delta)),
                        }
                    )

        basis_matrix = np.asarray(basis, dtype=np.float64)
        heldout_matrix = np.asarray(heldout, dtype=np.float64)
        if basis_matrix.shape != (10, 64) or heldout_matrix.shape != (20, 64):
            raise RuntimeError(
                f"{checkpoint} geometry population "
                f"{basis_matrix.shape}/{heldout_matrix.shape}"
            )
        _, singular, right = np.linalg.svd(
            basis_matrix, full_matrices=False
        )
        direction = right[0].copy()
        mean_delta = np.mean(basis_matrix, axis=0)
        mean_l2 = float(np.linalg.norm(mean_delta))
        if float(mean_delta @ direction) < 0.0:
            direction *= -1.0
        basis_energy = float(
            singular[0] ** 2 / np.sum(np.square(singular))
        )
        heldout_cosine = cosine_rows(heldout_matrix, direction)
        heldout_projection = heldout_matrix @ direction
        heldout_total_energy = float(np.sum(np.square(heldout_matrix)))
        heldout_projected_energy = float(
            np.sum(np.square(heldout_projection)) / heldout_total_energy
        )
        positive_fraction = float(np.mean(heldout_projection > 0.0))
        median_abs_cosine = float(np.median(np.abs(heldout_cosine)))

        adapter_weight = initializer(
            Path(policy_by_checkpoint[checkpoint]["path"]), "adapter_weight"
        )
        if adapter_weight.shape != (64, 14):
            raise RuntimeError(
                f"{checkpoint} adapter_weight shape {adapter_weight.shape}"
            )
        head_axis_response = direction @ adapter_weight
        head_axis_response_l2 = float(np.linalg.norm(head_axis_response))
        checks = {
            "basis_population_exact": basis_matrix.shape == (10, 64),
            "heldout_population_exact": heldout_matrix.shape == (20, 64),
            "basis_mean_nonzero": (
                mean_l2 >= thresholds["minimum_basis_mean_delta_l2"]
            ),
            "basis_rank_one_energy": (
                basis_energy
                >= thresholds[
                    "minimum_basis_first_singular_energy_fraction"
                ]
            ),
            "heldout_direction_sign_consistent": (
                positive_fraction
                >= thresholds[
                    "minimum_heldout_positive_projection_fraction"
                ]
            ),
            "heldout_direction_cosine": (
                median_abs_cosine
                >= thresholds["minimum_heldout_median_absolute_cosine"]
            ),
            "heldout_projected_energy": (
                heldout_projected_energy
                >= thresholds[
                    "minimum_heldout_projected_energy_fraction"
                ]
            ),
            "output_head_axis_actionable": (
                head_axis_response_l2
                >= thresholds["minimum_head_axis_response_l2"]
            ),
        }
        checkpoint_results.append(
            {
                "checkpoint_id": checkpoint,
                "basis_pairs": len(basis),
                "heldout_pairs": len(heldout),
                "basis_mean_delta_l2": mean_l2,
                "basis_first_singular_energy_fraction": basis_energy,
                "heldout_positive_projection_fraction": positive_fraction,
                "heldout_median_absolute_cosine": median_abs_cosine,
                "heldout_projected_energy_fraction": heldout_projected_energy,
                "head_axis_response_l2": head_axis_response_l2,
                "direction": direction.astype(float).tolist(),
                "head_axis_response": (
                    head_axis_response.astype(float).tolist()
                ),
                "checks": checks,
                "all_checks_pass": all(checks.values()),
                "records": records,
            }
        )

    passed = (
        len(checkpoint_results) == 2
        and all(item["all_checks_pass"] for item in checkpoint_results)
    )
    decision = (
        prereg["decision_rule"]["pass_decision"]
        if passed
        else prereg["decision_rule"]["fail_decision"]
    )
    failed = [
        f"{item['checkpoint_id']}.{name}"
        for item in checkpoint_results
        for name, ok in item["checks"].items()
        if not ok
    ]
    value: dict[str, Any] = {
        "schema_version": "open_duck.t76_com_hidden_geometry_result.v1",
        "status": (
            "PASS_T76_COM_HIDDEN_GEOMETRY"
            if passed
            else "HOLD_T76_COM_HIDDEN_GEOMETRY"
        ),
        "classification": (
            "COHERENT_LOW_RANK_COM_HIDDEN_AXIS"
            if passed
            else "COM_HIDDEN_DISPLACEMENT_NOT_STABLE_RANK_ONE"
        ),
        "decision": decision,
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checkpoint_results": checkpoint_results,
        "failed_checks": failed,
        "execution": {
            "new_simulator_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "t77_transform_preregistration": passed,
            "behavior": False,
            "training": False,
            "colab": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["result_sha256"] = canonical_sha256(value, "result_sha256")
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# T76 COM-hidden response-geometry result",
        "",
        f"- Status: `{value['status']}`",
        f"- Classification: `{value['classification']}`",
        f"- Decision: `{decision}`",
        "- New simulator cells / optimizer / Colab / robot: `0/0/0/0`",
        "",
    ]
    for item in checkpoint_results:
        lines.extend(
            [
                f"## {item['checkpoint_id']}",
                "",
                (
                    "- Basis first-axis energy: "
                    f"`{item['basis_first_singular_energy_fraction']:.9f}`"
                ),
                (
                    "- Held-out positive projection: "
                    f"`{item['heldout_positive_projection_fraction']:.9f}`"
                ),
                (
                    "- Held-out median |cosine|: "
                    f"`{item['heldout_median_absolute_cosine']:.9f}`"
                ),
                (
                    "- Held-out projected energy: "
                    f"`{item['heldout_projected_energy_fraction']:.9f}`"
                ),
                (
                    "- Output-head axis response L2: "
                    f"`{item['head_axis_response_l2']:.9f}`"
                ),
                "",
            ]
        )
    MARKDOWN.write_text("\n".join(lines), encoding="utf-8")
    print(value["status"])
    print(f"classification={value['classification']}")
    print(f"decision={decision}")
    for item in checkpoint_results:
        print(
            item["checkpoint_id"],
            json.dumps(
                {
                    key: item[key]
                    for key in (
                        "basis_first_singular_energy_fraction",
                        "heldout_positive_projection_fraction",
                        "heldout_median_absolute_cosine",
                        "heldout_projected_energy_fraction",
                        "head_axis_response_l2",
                        "all_checks_pass",
                    )
                },
                sort_keys=True,
            ),
        )
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
