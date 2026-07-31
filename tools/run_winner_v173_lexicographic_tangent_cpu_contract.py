#!/usr/bin/env python3
"""Run V173's preregistered lexicographic-tangent CPU contract."""

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
import jax.numpy as jnp
import numpy as np
from orbax import checkpoint as ocp


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from build_winner_v113_postexport_policies import sha256  # noqa: E402
from run_winner_v111_peak_torque_cpu_smoke import (  # noqa: E402
    tree_errors,
)
from run_winner_v119_transition_cpu_smoke import (  # noqa: E402
    deployed_onnx_contract,
)
from run_winner_v127_constrained_cpu_contract import (  # noqa: E402
    command as v127_command,
    deployment_inference_error,
    input_sha256_directory,
)


ANALYSIS = ROOT / "outputs/analysis"
PREREG = (
    ANALYSIS
    / "winner_v173_lexicographic_tangent_cpu_preregistration.json"
)
RESULT = (
    ANALYSIS / "winner_v173_lexicographic_tangent_cpu_result.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V173_LEXICOGRAPHIC_TANGENT_CPU_RESULT_20260725.md"
)
V119_PREREG = ANALYSIS / "winner_v119_transition_cpu_preregistration.json"


def restore_like(path: Path, template):
    checkpointer = ocp.PyTreeCheckpointer()
    restore_args = orbax_utils.restore_args_from_target(template)
    return checkpointer.restore(
        str(path), item=template, restore_args=restore_args
    )


def indexed_outputs(output: Path) -> dict[str, dict[int, Path]]:
    observed = {
        "policy": {
            int(path.name.rsplit("_", 1)[1]): path
            for path in output.iterdir()
            if path.is_dir() and "_v127_cost_value" not in path.name
        },
        "cost": {
            int(
                path.name.split("_v127_cost_value", 1)[0].rsplit("_", 1)[1]
            ): path
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
        raise ValueError(f"incomplete V173 outputs: {observed}")
    return observed


def input_paths(
    prereg: dict[str, Any],
    playground: Path,
) -> dict[str, Path]:
    return {
        "builder": ROOT
        / "tools/build_winner_v173_lexicographic_tangent_cpu_preregistration.py",
        "runner": Path(__file__).resolve(),
        "composer": ROOT
        / "tools/compose_winner_v173_lexicographic_tangent.py",
        "update_patch": ROOT
        / "patches/winner_v173_lexicographic_tangent_update.patch",
        "direction_helper": ROOT
        / "training/winner_v173_lexicographic_tangent.py",
        "v127_cpu_preregistration": ANALYSIS
        / "winner_v127_constrained_cpu_preregistration.json",
        "v127_cpu_result": ANALYSIS
        / "winner_v127_constrained_cpu_result.json",
        "v171a_correction": ANALYSIS
        / "winner_v171a_zero_cost_sufficiency_correction.json",
        "v172_preregistration": ANALYSIS
        / "winner_v172_positive_cost_geometry_preregistration.json",
        "v172_result": ANALYSIS
        / "winner_v172_positive_cost_geometry_result.json",
        "v173_manifest": playground
        / "WINNER_V173_COMPOSED_SOURCE_MANIFEST.json",
        "source_checkpoint": Path(prereg["external_paths"]["source_checkpoint"]),
        "v121_half_deployed": Path(
            prereg["external_paths"]["v121_half_deployed"]
        ),
    }


def synthetic_direction_tests(module) -> dict[str, Any]:
    reward = {"x": jnp.asarray([3.0, 0.0], dtype=jnp.float32)}
    cost = {"x": jnp.asarray([-2.0, 2.0], dtype=jnp.float32)}
    cases = {}
    for name, batch_cost, cost_seen in (
        ("reward_only", 0.0, False),
        ("cost_first", 1.0, False),
        ("tangent", 0.0, True),
    ):
        direction, metrics = module.select_actor_direction(
            reward,
            cost,
            batch_cost=jnp.asarray(batch_cost, dtype=jnp.float32),
            cost_seen_before=jnp.asarray(cost_seen),
            max_grad_norm=1.0,
        )
        cases[name] = {
            "direction": np.asarray(direction["x"]).tolist(),
            "metrics": {
                key: float(value) for key, value in metrics.items()
            },
        }
    checks = {
        "reward_only_branch_exact": (
            cases["reward_only"]["metrics"]["reward_only_branch"] == 1.0
            and cases["reward_only"]["metrics"]["cost_first_branch"] == 0.0
            and cases["reward_only"]["metrics"]["tangent_branch"] == 0.0
            and np.allclose(
                cases["reward_only"]["direction"],
                [-1.0, 0.0],
                rtol=0.0,
                atol=1.0e-7,
            )
        ),
        "cost_first_branch_exact": (
            cases["cost_first"]["metrics"]["cost_first_branch"] == 1.0
            and cases["cost_first"]["metrics"][
                "selected_cost_derivative"
            ]
            < 0.0
        ),
        "tangent_branch_exact": (
            cases["tangent"]["metrics"]["tangent_branch"] == 1.0
            and cases["tangent"]["metrics"]["tangent_cost_derivative"]
            <= 1.0e-6
            and cases["tangent"]["metrics"]["tangent_reward_retention"]
            > 0.0
        ),
        "all_synthetic_directions_norm_capped": all(
            case["metrics"]["clipped_direction_norm"] <= 1.000001
            for case in cases.values()
        ),
    }
    return {"cases": cases, "checks": checks}


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
            raise FileExistsError(f"refusing to overwrite V173: {path}")

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
        != "PREREGISTERED_WINNER_V173_LEXICOGRAPHIC_TANGENT_CPU_CONTRACT"
        or prereg.get("failed_checks") != []
        or prereg.get("input_hashes") != observed_hashes
    ):
        raise ValueError("V173 preregistration or inputs changed")
    cpu_only = (
        jax.default_backend() == "cpu"
        and all(device.platform == "cpu" for device in jax.devices())
    )
    if not cpu_only:
        raise RuntimeError("V173 must execute CPU-only")

    sys.path.insert(0, str(playground))
    from playground.common import (  # noqa: E402
        winner_v173_lexicographic_tangent as v173_tangent,
    )

    synthetic = synthetic_direction_tests(v173_tangent)
    work.mkdir(parents=True)
    output = work / "smoke"
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
    (work / "training.log").write_text(completed.stdout, encoding="utf-8")
    if completed.returncode != 0:
        raise RuntimeError(
            f"V173 CPU runner failed rc={completed.returncode}; "
            f"tail={completed.stdout[-5000:]}"
        )

    outputs = indexed_outputs(output)
    checkpointer = ocp.PyTreeCheckpointer()
    initial_tree = checkpointer.restore(str(outputs["policy"][0]))
    source_tree = restore_like(paths["source_checkpoint"], initial_tree)
    final_tree = restore_like(outputs["policy"][1024], initial_tree)
    source_structure, source_deltas = tree_errors(source_tree, initial_tree)
    final_structure, final_deltas = tree_errors(initial_tree, final_tree)
    policy_deltas = {
        name: value
        for name, value in final_deltas.items()
        if name.startswith("1/params/")
    }
    reward_value_deltas = {
        name: value
        for name, value in final_deltas.items()
        if name.startswith("2/params/")
    }
    initial_cost = checkpointer.restore(str(outputs["cost"][0]))
    final_cost = restore_like(outputs["cost"][1024], initial_cost)
    cost_structure, cost_deltas = tree_errors(initial_cost, final_cost)
    aux = {
        step: json.loads(path.read_text(encoding="utf-8"))
        for step, path in outputs["aux"].items()
    }
    initial_aux = aux[0]
    final_aux = aux[1024]
    expected_updates = int(final_aux["total_training_iterations"]) * 2
    observed_updates = (
        float(final_aux["v173_reward_only_updates"])
        + float(final_aux["v173_cost_first_updates"])
        + float(final_aux["v173_tangent_updates"])
    )

    v119_prereg = json.loads(V119_PREREG.read_text(encoding="utf-8"))
    deployed = {}
    for step, raw_path in outputs["raw"].items():
        deployed_path = work / f"v173_deployed_{step}.onnx"
        deployed[str(step)] = deployed_onnx_contract(
            raw_path, deployed_path, prereg=v119_prereg
        )
        deployed[str(step)]["path"] = str(deployed_path)
        deployed[str(step)]["sha256"] = sha256(deployed_path)
    step0_error = deployment_inference_error(
        Path(deployed["0"]["path"]), paths["v121_half_deployed"]
    )
    all_policy_finite = all(
        np.isfinite(np.asarray(leaf)).all()
        for leaf in jax.tree_util.tree_leaves(final_tree)
    )
    all_cost_finite = all(
        np.isfinite(np.asarray(leaf)).all()
        for leaf in jax.tree_util.tree_leaves(final_cost)
    )
    retention_floor = float(prereg["decision_rule"]["retention_floor"])
    checks = {
        "cpu_only": cpu_only,
        **synthetic["checks"],
        "source_restore_structure_exact": source_structure,
        "source_restore_bit_exact": max(
            source_deltas.values(), default=0.0
        )
        == 0.0,
        "trained_policy_structure_exact": final_structure,
        "every_actor_leaf_updated": bool(policy_deltas)
        and all(value > 0.0 for value in policy_deltas.values()),
        "every_reward_critic_leaf_updated": bool(reward_value_deltas)
        and all(value > 0.0 for value in reward_value_deltas.values()),
        "every_cost_critic_leaf_updated": bool(cost_deltas)
        and all(value > 0.0 for value in cost_deltas.values()),
        "all_trained_trees_finite": (
            all_policy_finite and all_cost_finite and cost_structure
        ),
        "dual_path_pinned_exactly_zero_and_uninitialized": (
            float(final_aux["lambda"]) == 0.0
            and float(final_aux["eta"]) == 0.0
            and float(final_aux["initial_cost"]) == 0.0
            and final_aux["initialized"] is False
        ),
        "real_positive_cost_was_seen": final_aux["v173_cost_seen"] is True,
        "reward_only_branch_exercised": (
            float(final_aux["v173_reward_only_updates"]) > 0.0
        ),
        "cost_first_branch_exercised": (
            float(final_aux["v173_cost_first_updates"]) > 0.0
        ),
        "all_real_updates_accounted_once": math.isclose(
            observed_updates,
            float(expected_updates),
            rel_tol=0.0,
            abs_tol=0.0,
        ),
        "zero_actor_directions_absent": (
            float(final_aux["v173_zero_direction_updates"]) == 0.0
        ),
        "real_tangent_retention_above_derived_floor": (
            float(final_aux["v173_tangent_updates"]) == 0.0
            or float(final_aux["v173_min_tangent_retention"])
            >= retention_floor
        ),
        "real_constrained_directions_nonincreasing_within_tolerance": (
            float(final_aux["v173_max_constrained_derivative_excess"])
            <= float(prereg["decision_rule"]["derivative_excess_tolerance"])
        ),
        "step0_deployed_inference_matches_v121_half": step0_error <= 1.0e-7,
        "both_deployed_graph_contracts_pass": all(
            row["inference"]["pass"] for row in deployed.values()
        ),
        "wall_seconds_at_most_1800": elapsed <= 1800,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "winner_v173.lexicographic_tangent_cpu_result.v1"
        ),
        "status": (
            "PASS_WINNER_V173_LEXICOGRAPHIC_TANGENT_CPU_CONTRACT"
            if not failed
            else "HOLD_WINNER_V173_LEXICOGRAPHIC_TANGENT_CPU_CONTRACT"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {
            **observed_hashes,
            "preregistration": sha256(PREREG),
        },
        "synthetic": synthetic,
        "training": {
            "command": command,
            "elapsed_seconds": elapsed,
            "policy_leaf_max_abs_delta": policy_deltas,
            "reward_value_leaf_max_abs_delta": reward_value_deltas,
            "cost_value_leaf_max_abs_delta": cost_deltas,
            "initial_aux": initial_aux,
            "final_aux": final_aux,
            "expected_actor_updates": expected_updates,
            "observed_actor_updates": observed_updates,
        },
        "deployment": {
            "step0_v121_half_max_abs_error": step0_error,
            "graphs": deployed,
        },
        "decision": (
            "EARN_V174_NOMINAL_BEHAVIOR_SCREEN_ONLY"
            if not failed
            else "CLOSE_LEXICOGRAPHIC_TANGENT_OPTIMIZER_IMPLEMENTATION"
        ),
        "authority": {
            "v174_nominal_behavior_screen": not failed,
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
        "# Winner V173 lexicographic-tangent CPU contract result\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Reward-only / cost-first / tangent updates: "
        f"`{final_aux['v173_reward_only_updates']}` / "
        f"`{final_aux['v173_cost_first_updates']}` / "
        f"`{final_aux['v173_tangent_updates']}`.\n"
        f"- Minimum real tangent retention: "
        f"`{final_aux['v173_min_tangent_retention']}`.\n"
        f"- Maximum constrained derivative excess: "
        f"`{final_aux['v173_max_constrained_derivative_excess']}`.\n"
        f"- Step-0 V121 inference error: `{step0_error}`.\n"
        f"- Decision: `{payload['decision']}`\n"
        "- CPU-only smoke; no hosted run, candidate, robustness matrix, "
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
