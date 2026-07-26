#!/usr/bin/env python3
"""Run T18's preregistered rate-coherent support screen."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import run_t16_support_coordinate_screen as t16
from t18_rate_coherent_support_onnx import (
    CONTRACT_TOLERANCE,
    sha256,
    verify_wrapper,
    wrap_rate_coherent_support,
)


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREGISTRATION = (
    ANALYSIS / "t18_rate_coherent_support_preregistration.json"
)
RESULT = ANALYSIS / "t18_rate_coherent_support_result.json"
MARKDOWN = ANALYSIS / "T18_RATE_COHERENT_SUPPORT_RESULT_20260726.md"


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def verify_receipt(value: dict[str, Any], label: str) -> None:
    path = Path(value["path"])
    if (
        not path.is_file()
        or path.stat().st_size != value["bytes"]
        or sha256(path) != value["sha256"]
    ):
        raise RuntimeError(f"T18 frozen receipt changed: {label}={path}")


def load_preregistration() -> dict[str, Any]:
    value = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    basis = {
        key: value[key]
        for key in (
            "schema_version",
            "status",
            "question",
            "causal_basis",
            "sources",
            "playground",
            "candidate",
            "transition",
            "matrix",
            "handoff_contract",
            "behavior_contract",
            "protection_contract",
            "decision_rule",
            "authority",
            "execution_now",
        )
    }
    if (
        value["schema_version"]
        != "open_duck.t18_rate_coherent_support_preregistration.v1"
        or value["status"]
        != "PREREGISTERED_T18_RATE_COHERENT_SUPPORT_SCREEN"
        or canonical_sha256(basis)
        != value["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T18 preregistration identity changed")
    for name, item in value["sources"].items():
        verify_receipt(item, name)
    for checkpoint in value["candidate"]["checkpoints"]:
        verify_receipt(checkpoint["policy"], checkpoint["checkpoint_id"])
    for fit_id, item in value["candidate"]["fits"].items():
        verify_receipt(item, fit_id)
    verify_receipt(value["candidate"]["calibrator"], "calibrator")
    verify_receipt(value["candidate"]["reference"], "reference")
    playground = Path(value["playground"]["path"])
    for relative, expected in value["playground"][
        "required_file_sha256"
    ].items():
        if sha256(playground / relative) != expected:
            raise RuntimeError(f"T18 playground changed: {relative}")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-root", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise SystemExit("T18 requires --execute")
    if RESULT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T18 result")
    root = args.cache_root.resolve()
    if root.exists():
        raise FileExistsError(f"refusing to reuse T18 cache: {root}")
    root.mkdir(parents=True)
    prereg = load_preregistration()
    if (
        prereg["transition"]["contract_tolerance"]
        != CONTRACT_TOLERANCE
    ):
        raise RuntimeError("T18 float32 contract tolerance changed")

    wrappers = []
    wrapped_paths: dict[str, Path] = {}
    for checkpoint in prereg["candidate"]["checkpoints"]:
        wrapped = (
            root
            / "wrapped"
            / checkpoint["checkpoint_id"]
            / "rate_coherent_support.onnx"
        )
        wrapper = wrap_rate_coherent_support(
            Path(checkpoint["policy"]["path"]),
            wrapped,
        )
        verification = verify_wrapper(
            Path(checkpoint["policy"]["path"]),
            wrapped,
            cases=prereg["transition"]["contract_cases"],
            seed=prereg["transition"]["contract_seed"],
        )
        wrappers.append(
            {
                "checkpoint_id": checkpoint["checkpoint_id"],
                "wrapper": wrapper,
                "verification": verification,
            }
        )
        wrapped_paths[checkpoint["checkpoint_id"]] = wrapped

    blocks = []
    for checkpoint in prereg["candidate"]["checkpoints"]:
        wrapped = wrapped_paths[checkpoint["checkpoint_id"]]
        for fit_id in prereg["candidate"]["fits"]:
            for condition in prereg["matrix"]["conditions"]:
                block = t16.run_block(
                    prereg,
                    checkpoint,
                    wrapped,
                    fit_id,
                    condition,
                    root,
                )
                blocks.append(t16.analyze_block(prereg, block))

    cells = [cell for block in blocks for cell in block["cells"]]
    wrapper_contract_green = all(
        row["verification"]["maximum_action_error"]
        <= CONTRACT_TOLERANCE
        and row["verification"]["maximum_previous_action_error"]
        <= CONTRACT_TOLERANCE
        and row["verification"]["maximum_hidden_error"]
        <= CONTRACT_TOLERANCE
        and row["verification"]["maximum_normalized_rate_excess"]
        <= CONTRACT_TOLERANCE
        and row["verification"][
            "previous_action_out_equals_action_bit_exact"
        ]
        and row["verification"][
            "x0_output_equals_support_action_bit_exact"
        ]
        and row["verification"]["output_bounds_exact"]
        and row["verification"]["inputs_exact"]
        and row["verification"]["outputs_exact"]
        and row["verification"]["provider"] == "CPUExecutionProvider"
        for row in wrappers
    )
    checks = {
        "matrix_exact": (
            len(blocks) == 8
            and len(cells) == 32
            and all(len(block["cells"]) == 4 for block in blocks)
        ),
        "wrapper_contract_green": wrapper_contract_green,
        "cpu_only": all(
            block["execution_platform"] == "cpu" for block in blocks
        ),
        "worker_inputs_exact": all(
            block["worker_inputs_exact"] for block in blocks
        ),
        "all_com_readbacks_exact": all(
            cell["com_readback_exact"] for cell in cells
        ),
        "all_handoff_chains_exact": all(
            cell["handoff"]["all_checks_pass"] for cell in cells
        ),
        "all_eight_x0_cells_retain_support_exactly": (
            sum(cell["command_x_m_s"] == 0.0 for cell in cells) == 8
            and all(
                cell["x0_support_action_exact"]
                for cell in cells
                if cell["command_x_m_s"] == 0.0
            )
        ),
        "all_cells_green": all(cell["cell_green"] for cell in cells),
        "optimizer_steps_zero": True,
        "hosted_compute_zero": True,
        "robot_access_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    basis = {
        "schema_version": (
            "open_duck.t18_rate_coherent_support_result.v1"
        ),
        "status": (
            "PASS_T18_RATE_COHERENT_SUPPORT_SCREEN"
            if passed
            else "HOLD_T18_RATE_COHERENT_SUPPORT_SCREEN"
        ),
        "decision": (
            "EARN_T18_FULL_R2_PREREGISTRATION"
            if passed
            else "CLOSE_ZERO_TRAINING_RATE_COHERENT_SUPPORT_COMPOSITION"
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "wrappers": wrappers,
        "blocks": blocks,
        "summary": {
            "green_cells": sum(
                int(cell["cell_green"]) for cell in cells
            ),
            "total_cells": len(cells),
            "green_by_condition": {
                condition["id"]: sum(
                    int(cell["cell_green"])
                    for cell in cells
                    if cell["condition_id"] == condition["id"]
                )
                for condition in prereg["matrix"]["conditions"]
            },
            "minimum_moving_mean_vx_m_s": min(
                float(cell["behavior"]["mean_local_vx_m_s"])
                for cell in cells
                if cell["command_x_m_s"] > 0.0
            ),
            "worst_tracking_p95_rad": max(
                float(cell["behavior"]["pitch_tracking_p95_rad"])
                for cell in cells
            ),
            "worst_rate_excess_rad_s": max(
                float(
                    cell["protection"][
                        "maximum_full_measured_vector_excess_rad_s"
                    ]
                )
                for cell in cells
            ),
            "worst_action_saturation_pct": max(
                float(cell["behavior"]["action_saturation_pct"])
                for cell in cells
            ),
            "worst_strict_overcurrent_run_ticks": max(
                int(
                    cell["protection"][
                        "worst_strict_overcurrent_run_ticks"
                    ]
                )
                for cell in cells
            ),
            "worst_strict_overload_run_ticks": max(
                int(
                    cell["protection"][
                        "worst_strict_overload_run_ticks"
                    ]
                )
                for cell in cells
            ),
        },
        "execution": {
            "optimizer_steps": 0,
            "hosted_or_colab_compute": 0,
            "simulator_behavior_cells": 32,
            "robot_or_rdk_access": 0,
        },
    }
    value = {**basis, "result_sha256": canonical_sha256(basis)}
    RESULT.write_text(
        json.dumps(
            value,
            allow_nan=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T18 rate-coherent support result",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                (
                    "- Green cells: "
                    f"`{value['summary']['green_cells']}/"
                    f"{value['summary']['total_cells']}`"
                ),
                (
                    "- Green by condition: "
                    f"`{value['summary']['green_by_condition']}`"
                ),
                (
                    "- Minimum moving vx: "
                    f"`{value['summary']['minimum_moving_mean_vx_m_s']:.9g} m/s`"
                ),
                (
                    "- Worst tracking p95: "
                    f"`{value['summary']['worst_tracking_p95_rad']:.9g} rad`"
                ),
                (
                    "- Worst rate excess: "
                    f"`{value['summary']['worst_rate_excess_rad_s']:.9g} rad/s`"
                ),
                (
                    "- Worst saturation: "
                    f"`{value['summary']['worst_action_saturation_pct']:.9g}%`"
                ),
                f"- Failed checks: `{failed}`",
                "- Optimizer/hosted/robot execution: `0/0/0`",
                f"- Result SHA-256: `{value['result_sha256']}`",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(
        "green_cells="
        f"{value['summary']['green_cells']}/{value['summary']['total_cells']}"
    )
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
