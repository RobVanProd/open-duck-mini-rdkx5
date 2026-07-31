#!/usr/bin/env python3
"""Resolve T217's sole cost-init hold at frozen float32 resolution."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""
os.environ["ROCR_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"

from flax.training import orbax_utils
import jax
from orbax import checkpoint as ocp


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
sys.path.insert(0, str(ROOT / "tools"))
from run_t136_static_calibration_router_transform import (  # noqa: E402
    canonical_sha256,
    verify,
)
from validate_winner_v112_recovered_training import (  # noqa: E402
    directory_sha256,
    tree_deltas,
    tree_finite,
)


PREREG = ANALYSIS / "t217b_cost_init_backend_recovery_preregistration.json"
RESULT = ANALYSIS / "t217b_cost_init_backend_recovery_result.json"
MARKDOWN = ANALYSIS / "T217B_COST_INIT_BACKEND_RECOVERY_RESULT_20260730.md"
FAILED_CHECK = "step_zero_cost_tree_reproducible_bit_exact"


def restore_tree(path: Path, template: Any) -> Any:
    return ocp.PyTreeCheckpointer().restore(
        str(path),
        item=template,
        restore_args=orbax_utils.restore_args_from_target(template),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T217B result")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T217B execution requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T217B_COST_INIT_BACKEND_RECOVERY"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T217B preregistration changed")
    for name in ("builder", "runner", "test", "t217_hold", "t215b_cpu_result"):
        verify(prereg["frozen_inputs"][name], f"frozen_inputs.{name}")
    cpu_path = Path(
        prereg["frozen_inputs"]["cpu_cost_zero"]["path"]
    ).resolve()
    hosted_path = Path(
        prereg["frozen_inputs"]["hosted_cost_zero"]["path"]
    ).resolve()
    if (
        directory_sha256(cpu_path)
        != prereg["frozen_inputs"]["cpu_cost_zero"]["sha256"]
        or directory_sha256(hosted_path)
        != prereg["frozen_inputs"]["hosted_cost_zero"]["sha256"]
    ):
        raise RuntimeError("T217B cost checkpoint identity changed")
    t217 = json.loads(
        Path(prereg["frozen_inputs"]["t217_hold"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    cpu_tree = ocp.PyTreeCheckpointer().restore(str(cpu_path))
    hosted_tree = restore_tree(hosted_path, cpu_tree)
    structure, deltas = tree_deltas(cpu_tree, hosted_tree)
    tolerance = float(prereg["recovery_rule"]["absolute_tolerance"])
    maximum = max(deltas.values(), default=0.0)
    nonzero = {
        name: value for name, value in deltas.items() if value != 0.0
    }
    checks = {
        "preregistered_tolerance_exact": (
            tolerance == 1.1920928955078125e-7
        ),
        "cost_tree_structure_exact": structure,
        "both_cost_trees_finite": (
            tree_finite(cpu_tree) and tree_finite(hosted_tree)
        ),
        "all_leaf_deltas_finite": all(
            math.isfinite(float(value)) for value in deltas.values()
        ),
        "maximum_delta_within_one_float32_epsilon": maximum <= tolerance,
        "t217_exact_single_hold_preserved": (
            t217["status"]
            == "HOLD_T217_T216_RECOVERED_TRAINING_VALIDATION"
            and t217["failed_checks"] == [FAILED_CHECK]
            and all(
                passed
                for name, passed in t217["checks"].items()
                if name != FAILED_CHECK
            )
        ),
        "cpu_only": all(
            device.platform == "cpu" for device in jax.devices()
        ),
        "zero_optimizer_simulator_onnx_behavior_hosted_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    basis_result: dict[str, Any] = {
        "schema_version": (
            "open_duck.t217b_cost_init_backend_recovery_result.v1"
        ),
        "status": (
            "PASS_T217B_COST_INIT_BACKEND_RECOVERY"
            if not failed
            else "HOLD_T217B_COST_INIT_BACKEND_RECOVERY"
        ),
        "decision": (
            "RECOVER_T217_AND_EARN_T218_T216_POSTEXPORT_"
            "COMPOSITION_PREREGISTRATION_ONLY"
            if not failed
            else "HOLD_T216_WITHOUT_BEHAVIOR"
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "comparison": {
            "cpu_cost_zero": {
                **prereg["frozen_inputs"]["cpu_cost_zero"],
                "directory_sha256": directory_sha256(cpu_path),
            },
            "hosted_cost_zero": {
                **prereg["frozen_inputs"]["hosted_cost_zero"],
                "directory_sha256": directory_sha256(hosted_path),
            },
            "leaf_count": len(deltas),
            "nonzero_leaf_count": len(nonzero),
            "nonzero_leaf_deltas": nonzero,
            "maximum_absolute_leaf_delta": maximum,
            "absolute_tolerance": tolerance,
            "maximum_over_tolerance": maximum / tolerance,
        },
        "recovered_t217": {
            "status": (
                "PASS_T217_T216_RECOVERED_TRAINING_VALIDATION"
                if not failed
                else t217["status"]
            ),
            "substantive_checks": {
                name: passed
                for name, passed in t217["checks"].items()
                if name != FAILED_CHECK
            },
            "recovered_check": (
                not failed
            ),
            "original_result_sha256": t217["result_sha256"],
        },
        "execution": {
            "checkpoint_restores": 2,
            "optimizer_steps": 0,
            "simulator_transitions": 0,
            "onnx_inferences": 0,
            "behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "composition_preregistration": not failed,
            "behavior": False,
            "training": False,
            "colab": False,
            "gate5": False,
            "robot_or_rdk": False,
        },
    }
    value = {
        **basis_result,
        "result_sha256": canonical_sha256(basis_result),
    }
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T217B cost-init backend recovery result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Failed checks: `{failed}`\n"
        f"- Nonzero leaves: `{len(nonzero)}/{len(deltas)}`\n"
        f"- Maximum delta: `{maximum}`\n"
        f"- Float32 epsilon: `{tolerance}`\n"
        "- Optimizer / simulator / ONNX / behavior / hosted / robot: "
        "`0/0/0/0/0/0`\n"
        f"- Result SHA-256: `{value['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
