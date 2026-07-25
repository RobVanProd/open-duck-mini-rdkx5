#!/usr/bin/env python3
"""Run V172's first-positive-cost actor-gradient geometry audit."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""
os.environ["ROCR_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"

from flax.training import orbax_utils
import jax
import numpy as np
from orbax import checkpoint as ocp


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from build_winner_v113_postexport_policies import sha256  # noqa: E402
from run_winner_v111_peak_torque_cpu_smoke import tree_errors  # noqa: E402
from run_winner_v127_constrained_cpu_contract import (  # noqa: E402
    command as v127_command,
    input_sha256_directory,
)


ANALYSIS = ROOT / "outputs/analysis"
PREREG = (
    ANALYSIS / "winner_v172_positive_cost_geometry_preregistration.json"
)
RESULT = ANALYSIS / "winner_v172_positive_cost_geometry_result.json"
MARKDOWN = (
    ANALYSIS
    / "WINNER_V172_POSITIVE_COST_GEOMETRY_RESULT_20260725.md"
)
GEOMETRY_KEYS = (
    "reward_gradient_norm",
    "cost_gradient_norm",
    "reward_cost_gradient_cosine",
    "reward_descent_cost_derivative_before",
    "projected_cost_derivative_after",
    "projected_reward_direction_retention",
    "projection_active",
    "cost_descent_derivative",
)


def restore_like(path: Path, template):
    checkpointer = ocp.PyTreeCheckpointer()
    restore_args = orbax_utils.restore_args_from_target(template)
    return checkpointer.restore(
        str(path), item=template, restore_args=restore_args
    )


def exact_tree_comparison(left, right) -> dict[str, Any]:
    structure, errors = tree_errors(left, right)
    maximum = max(errors.values(), default=0.0)
    return {
        "structure_exact": bool(structure),
        "leaf_max_abs_error": errors,
        "max_abs_error": maximum,
        "bit_exact": bool(structure and maximum == 0.0),
    }


def indexed_outputs(output: Path) -> dict[str, dict[int, Path]]:
    observed = {
        "policy": {
            int(path.name.rsplit("_", 1)[1]): path
            for path in output.iterdir()
            if path.is_dir() and "_v127_cost_value" not in path.name
        },
        "cost": {
            int(path.name.split("_v127_cost_value", 1)[0].rsplit("_", 1)[1]): path
            for path in output.glob("*_v127_cost_value")
        },
        "raw": {
            int(path.stem.rsplit("_", 1)[1]): path
            for path in output.glob("*.onnx")
        },
        "aux": {
            int(json.loads(path.read_text(encoding="utf-8"))["step"]): path
            for path in output.glob("*_v127_aux.json")
        },
    }
    if any(sorted(paths) != [0, 1024] for paths in observed.values()):
        raise ValueError(f"incomplete V172 outputs: {observed}")
    return observed


def frozen_outputs(smoke: Path) -> dict[str, dict[int, Path]]:
    return indexed_outputs(smoke)


def input_paths(
    prereg: dict[str, Any],
    playground: Path,
) -> dict[str, Path]:
    return {
        "builder": ROOT
        / "tools/build_winner_v172_positive_cost_geometry_preregistration.py",
        "runner": Path(__file__).resolve(),
        "composer": ROOT
        / "tools/compose_winner_v172_positive_cost_geometry.py",
        "capture_patch": ROOT
        / "patches/winner_v172_positive_cost_capture.patch",
        "v171_helper": ROOT / "training/winner_v171_gradient_geometry.py",
        "v127_cpu_preregistration": ANALYSIS
        / "winner_v127_constrained_cpu_preregistration.json",
        "v127_cpu_result": ANALYSIS
        / "winner_v127_constrained_cpu_result.json",
        "v171_result": ANALYSIS
        / "winner_v171_gradient_geometry_result.json",
        "v171a_correction": ANALYSIS
        / "winner_v171a_zero_cost_sufficiency_correction.json",
        "v172_manifest": playground
        / "WINNER_V172_COMPOSED_SOURCE_MANIFEST.json",
        "source_checkpoint": Path(prereg["external_paths"]["source_checkpoint"]),
        "frozen_smoke": Path(prereg["external_paths"]["frozen_v127_smoke"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument("--playground", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    args = parser.parse_args()
    playground = args.playground.resolve()
    work = args.work_root.resolve()
    for path in (RESULT, MARKDOWN, work):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V172: {path}")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    paths = input_paths(prereg, playground)
    observed_hashes = {
        name: (
            input_sha256_directory(path) if path.is_dir() else sha256(path)
        )
        for name, path in paths.items()
    }
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V172_POSITIVE_COST_GEOMETRY"
        or prereg.get("failed_checks") != []
        or prereg.get("input_hashes") != observed_hashes
    ):
        raise ValueError("V172 preregistration or inputs changed")
    if not (
        jax.default_backend() == "cpu"
        and all(device.platform == "cpu" for device in jax.devices())
    ):
        raise RuntimeError("V172 must execute CPU-only")

    work.mkdir(parents=True)
    output = work / "audit"
    output.mkdir()
    command = v127_command(playground, paths["source_checkpoint"], output)
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(playground)
    started = time.monotonic()
    completed = subprocess.run(
        command,
        cwd=playground,
        env=environment,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=1800,
        check=False,
    )
    elapsed = time.monotonic() - started
    (work / "audit.log").write_text(completed.stdout, encoding="utf-8")
    if completed.returncode != 0:
        raise RuntimeError(
            f"V172 CPU runner failed rc={completed.returncode}; "
            f"tail={completed.stdout[-5000:]}"
        )

    audit = indexed_outputs(output)
    frozen = frozen_outputs(paths["frozen_smoke"])
    checkpointer = ocp.PyTreeCheckpointer()
    frozen_initial = checkpointer.restore(str(frozen["policy"][0]))
    frozen_final = restore_like(frozen["policy"][1024], frozen_initial)
    audit_initial = restore_like(audit["policy"][0], frozen_initial)
    audit_final = restore_like(audit["policy"][1024], frozen_initial)
    frozen_cost_initial = checkpointer.restore(str(frozen["cost"][0]))
    frozen_cost_final = restore_like(
        frozen["cost"][1024], frozen_cost_initial
    )
    audit_cost_initial = restore_like(
        audit["cost"][0], frozen_cost_initial
    )
    audit_cost_final = restore_like(
        audit["cost"][1024], frozen_cost_initial
    )
    comparisons = {
        "initial_policy": exact_tree_comparison(
            frozen_initial, audit_initial
        ),
        "final_policy": exact_tree_comparison(frozen_final, audit_final),
        "initial_cost_critic": exact_tree_comparison(
            frozen_cost_initial, audit_cost_initial
        ),
        "final_cost_critic": exact_tree_comparison(
            frozen_cost_final, audit_cost_final
        ),
    }
    frozen_aux = {
        step: json.loads(path.read_text(encoding="utf-8"))
        for step, path in frozen["aux"].items()
    }
    audit_aux = {
        step: json.loads(path.read_text(encoding="utf-8"))
        for step, path in audit["aux"].items()
    }
    frozen_aux_keys = (
        "lambda",
        "eta",
        "initial_cost",
        "initialized",
        "total_training_iterations",
        "quarter_iterations",
    )
    aux_exact = all(
        all(
            frozen_aux[step][key] == audit_aux[step][key]
            for key in frozen_aux_keys
        )
        for step in (0, 1024)
    )
    geometry = {
        key: float(audit_aux[1024][f"v171_{key}"])
        for key in GEOMETRY_KEYS
    }
    batch_cost = float(audit_aux[1024]["v172_geometry_batch_cost"])
    norm_product = (
        geometry["reward_gradient_norm"] * geometry["cost_gradient_norm"]
    )
    tolerance = (
        64.0
        * float(np.finfo(np.float32).eps)
        * max(
            1.0,
            abs(geometry["reward_descent_cost_derivative_before"]),
            norm_product,
        )
    )
    expected_cost_descent = -(geometry["cost_gradient_norm"] ** 2)
    retention_floor = float(prereg["decision_rule"]["retention_floor"])
    expected_projection_active = (
        geometry["reward_descent_cost_derivative_before"] > 0.0
        and geometry["cost_gradient_norm"] > 0.0
    )
    raw_hashes_exact = all(
        sha256(audit["raw"][step]) == sha256(frozen["raw"][step])
        for step in (0, 1024)
    )
    checks = {
        "cpu_only": True,
        "exact_1024_step_schedule": (
            audit_aux[1024]["total_training_iterations"] == 32
        ),
        "first_positive_cost_geometry_captured": (
            audit_aux[1024]["v171_geometry_initialized"] is True
            and batch_cost > 0.0
        ),
        "captured_batch_cost_matches_dual_first_positive_cost": math.isclose(
            batch_cost,
            float(audit_aux[1024]["initial_cost"]),
            rel_tol=0.0,
            abs_tol=0.0,
        ),
        "all_geometry_values_finite": all(
            math.isfinite(value) for value in geometry.values()
        ),
        "reward_gradient_nonzero": geometry["reward_gradient_norm"] > 0.0,
        "cost_gradient_nonzero": geometry["cost_gradient_norm"] > 0.0,
        "cosine_in_closed_unit_interval": (
            -1.000001
            <= geometry["reward_cost_gradient_cosine"]
            <= 1.000001
        ),
        "projection_activation_matches_exact_rule": (
            bool(round(geometry["projection_active"]))
            == expected_projection_active
        ),
        "projected_direction_first_order_cost_nonincreasing": (
            geometry["projected_cost_derivative_after"] <= tolerance
        ),
        "projected_direction_retains_derived_nontrivial_fraction": (
            geometry["projected_reward_direction_retention"]
            >= retention_floor
        ),
        "cost_descent_direction_exact": math.isclose(
            geometry["cost_descent_derivative"],
            expected_cost_descent,
            rel_tol=64.0 * float(np.finfo(np.float32).eps),
            abs_tol=tolerance,
        )
        and geometry["cost_descent_derivative"] < 0.0,
        "instrumented_policy_and_critic_trees_bit_exact_to_frozen_v127": (
            all(row["bit_exact"] for row in comparisons.values())
        ),
        "instrumented_dual_state_bit_exact_to_frozen_v127": aux_exact,
        "instrumented_raw_graphs_bit_exact_to_frozen_v127": raw_hashes_exact,
        "wall_seconds_at_most_1800": elapsed <= 1800,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v172.positive_cost_geometry_result.v1",
        "status": (
            "PASS_WINNER_V172_POSITIVE_COST_GEOMETRY"
            if not failed
            else "HOLD_WINNER_V172_POSITIVE_COST_GEOMETRY"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {
            **observed_hashes,
            "preregistration": sha256(PREREG),
        },
        "geometry": {
            **geometry,
            "captured_raw_batch_cost": batch_cost,
            "float32_directional_tolerance": tolerance,
            "retention_floor": retention_floor,
            "expected_cost_descent_derivative": expected_cost_descent,
        },
        "audit_only_equivalence": {
            **comparisons,
            "dual_state_exact": aux_exact,
            "raw_graph_hashes_exact": raw_hashes_exact,
        },
        "execution": {
            "command": command,
            "elapsed_seconds": elapsed,
            "work_root": str(work),
        },
        "decision": (
            "EARN_V173_LEXICOGRAPHIC_TANGENT_UPDATE_CPU_CONTRACT_ONLY"
            if not failed
            else "CLOSE_LEXICOGRAPHIC_TANGENT_OPTIMIZER_GEOMETRY"
        ),
        "authority": {
            "v173_cpu_contract_design": not failed,
            "optimizer_implementation": False,
            "hosted_training": False,
            "candidate_selection": False,
            "robustness_matrix": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    RESULT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V172 first-positive-cost gradient geometry result\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Captured raw batch cost: `{batch_cost}`.\n"
        f"- Reward/cost gradient cosine: "
        f"`{geometry['reward_cost_gradient_cosine']}`.\n"
        f"- Projection active: `{bool(round(geometry['projection_active']))}`.\n"
        f"- Direction retention: "
        f"`{geometry['projected_reward_direction_retention']}`.\n"
        f"- Cost derivative before/after: "
        f"`{geometry['reward_descent_cost_derivative_before']}` / "
        f"`{geometry['projected_cost_derivative_after']}`.\n"
        f"- Instrumented output bit-exact to V127: "
        f"`{all(row['bit_exact'] for row in comparisons.values())}`.\n"
        f"- Decision: `{payload['decision']}`\n"
        "- CPU-only audit; no hosted training, candidate, robustness matrix, "
        "Gate 5, RDK-X5, or robot.\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "failed_checks": failed,
                "output": str(RESULT),
                "sha256": sha256(RESULT),
            }
        )
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
