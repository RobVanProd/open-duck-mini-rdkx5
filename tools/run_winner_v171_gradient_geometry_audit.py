#!/usr/bin/env python3
"""Run V171's preregistered reward/cost actor-gradient geometry audit."""

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
PREREG = ANALYSIS / "winner_v171_gradient_geometry_preregistration.json"
RESULT = ANALYSIS / "winner_v171_gradient_geometry_result.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V171_GRADIENT_GEOMETRY_RESULT_20260725.md"
)
V119_PREREG = ANALYSIS / "winner_v119_transition_cpu_preregistration.json"


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


def one_iteration_command(
    playground: Path,
    source: Path,
    output: Path,
) -> list[str]:
    result = v127_command(playground, source, output)
    index = result.index("--num_timesteps")
    result[index + 1] = "32"
    return result


def run_smoke(
    *,
    playground: Path,
    source: Path,
    output: Path,
    log: Path,
) -> tuple[list[str], float]:
    output.mkdir(parents=True)
    command = one_iteration_command(playground, source, output)
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
    log.write_text(completed.stdout, encoding="utf-8")
    if completed.returncode != 0:
        raise RuntimeError(
            f"V171 CPU smoke failed rc={completed.returncode}; "
            f"tail={completed.stdout[-5000:]}"
        )
    return command, elapsed


def indexed_outputs(output: Path) -> dict[str, dict[int, Path]]:
    policy = {
        int(path.name.rsplit("_", 1)[1]): path
        for path in output.iterdir()
        if path.is_dir() and "_v127_cost_value" not in path.name
    }
    cost = {
        int(path.name.split("_v127_cost_value", 1)[0].rsplit("_", 1)[1]): path
        for path in output.glob("*_v127_cost_value")
    }
    raw = {
        int(path.stem.rsplit("_", 1)[1]): path
        for path in output.glob("*.onnx")
    }
    aux = {
        int(json.loads(path.read_text(encoding="utf-8"))["step"]): path
        for path in output.glob("*_v127_aux.json")
    }
    observed = {
        "policy": policy,
        "cost": cost,
        "raw": raw,
        "aux": aux,
    }
    if any(sorted(paths) != [0, 32] for paths in observed.values()):
        raise ValueError(f"incomplete V171 outputs: {observed}")
    return observed


def exact_tree_comparison(left, right) -> dict[str, Any]:
    structure, errors = tree_errors(left, right)
    return {
        "structure_exact": bool(structure),
        "leaf_max_abs_error": errors,
        "max_abs_error": max(errors.values(), default=0.0),
        "bit_exact": bool(
            structure and max(errors.values(), default=0.0) == 0.0
        ),
    }


def input_paths(
    prereg: dict[str, Any],
    audit_playground: Path,
    control_playground: Path,
) -> dict[str, Path]:
    return {
        "builder": ROOT
        / "tools/build_winner_v171_gradient_geometry_preregistration.py",
        "runner": Path(__file__).resolve(),
        "composer": ROOT / "tools/compose_winner_v171_gradient_geometry.py",
        "patch": ROOT / "patches/winner_v171_gradient_geometry_audit.patch",
        "geometry_helper": ROOT
        / "training/winner_v171_gradient_geometry.py",
        "v127_cpu_preregistration": ANALYSIS
        / "winner_v127_constrained_cpu_preregistration.json",
        "v127_cpu_result": ANALYSIS
        / "winner_v127_constrained_cpu_result.json",
        "v127_hosted_result": ANALYSIS
        / "winner_v128_nominal_behavior_result.json",
        "v163_v165_addendum": ANALYSIS
        / "FABLE_V163_V165_ADDENDUM_20260725.md",
        "v170_result": ANALYSIS
        / "winner_v170_exact_oracle_r2_feasibility_result.json",
        "audit_manifest": audit_playground
        / "WINNER_V171_COMPOSED_SOURCE_MANIFEST.json",
        "control_manifest": control_playground
        / "WINNER_V127_COMPOSED_SOURCE_MANIFEST.json",
        "source_checkpoint": Path(prereg["external_paths"]["source_checkpoint"]),
        "v121_half_deployed": Path(
            prereg["external_paths"]["v121_half_deployed"]
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument("--audit-playground", type=Path, required=True)
    parser.add_argument("--control-playground", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    args = parser.parse_args()
    audit_playground = args.audit_playground.resolve()
    control_playground = args.control_playground.resolve()
    work = args.work_root.resolve()
    for path in (RESULT, MARKDOWN, work):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V171: {path}")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    paths = input_paths(prereg, audit_playground, control_playground)
    observed_hashes = {
        name: (
            input_sha256_directory(path) if path.is_dir() else sha256(path)
        )
        for name, path in paths.items()
    }
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V171_GRADIENT_GEOMETRY_AUDIT"
        or prereg.get("failed_checks") != []
        or prereg.get("input_hashes") != observed_hashes
    ):
        raise ValueError("V171 preregistration or inputs changed")
    if not (
        jax.default_backend() == "cpu"
        and all(device.platform == "cpu" for device in jax.devices())
    ):
        raise RuntimeError("V171 must execute CPU-only")

    work.mkdir(parents=True)
    control_output = work / "control"
    audit_output = work / "audit"
    control_command, control_elapsed = run_smoke(
        playground=control_playground,
        source=paths["source_checkpoint"],
        output=control_output,
        log=work / "control.log",
    )
    audit_command, audit_elapsed = run_smoke(
        playground=audit_playground,
        source=paths["source_checkpoint"],
        output=audit_output,
        log=work / "audit.log",
    )
    control = indexed_outputs(control_output)
    audit = indexed_outputs(audit_output)

    checkpointer = ocp.PyTreeCheckpointer()
    control_initial = checkpointer.restore(str(control["policy"][0]))
    control_final = restore_like(control["policy"][32], control_initial)
    audit_initial = restore_like(audit["policy"][0], control_initial)
    audit_final = restore_like(audit["policy"][32], control_initial)
    control_cost_initial = checkpointer.restore(str(control["cost"][0]))
    control_cost_final = restore_like(
        control["cost"][32], control_cost_initial
    )
    audit_cost_initial = restore_like(
        audit["cost"][0], control_cost_initial
    )
    audit_cost_final = restore_like(
        audit["cost"][32], control_cost_initial
    )
    initial_policy_comparison = exact_tree_comparison(
        control_initial, audit_initial
    )
    final_policy_comparison = exact_tree_comparison(control_final, audit_final)
    initial_cost_comparison = exact_tree_comparison(
        control_cost_initial, audit_cost_initial
    )
    final_cost_comparison = exact_tree_comparison(
        control_cost_final, audit_cost_final
    )

    control_aux = {
        step: json.loads(path.read_text(encoding="utf-8"))
        for step, path in control["aux"].items()
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
    aux_control_exact = all(
        all(
            control_aux[step][key] == audit_aux[step][key]
            for key in frozen_aux_keys
        )
        for step in (0, 32)
    )
    geometry = {
        key: float(audit_aux[32][f"v171_{key}"])
        for key in GEOMETRY_KEYS
    }
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

    v119_prereg = json.loads(V119_PREREG.read_text(encoding="utf-8"))
    deployed = {}
    for step, raw_path in audit["raw"].items():
        deployed_path = work / f"v171_deployed_{step}.onnx"
        deployed[str(step)] = deployed_onnx_contract(
            raw_path, deployed_path, prereg=v119_prereg
        )
        deployed[str(step)]["path"] = str(deployed_path)
        deployed[str(step)]["sha256"] = sha256(deployed_path)
    step0_error = deployment_inference_error(
        Path(deployed["0"]["path"]), paths["v121_half_deployed"]
    )

    expected_projection_active = (
        geometry["reward_descent_cost_derivative_before"] > 0.0
        and geometry["cost_gradient_norm"] > 0.0
    )
    checks = {
        "cpu_only": True,
        "control_and_audit_each_exactly_one_training_iteration": (
            control_aux[32]["total_training_iterations"] == 1
            and audit_aux[32]["total_training_iterations"] == 1
        ),
        "audit_initial_geometry_uninitialized_and_zero": (
            audit_aux[0]["v171_geometry_initialized"] is False
            and all(
                float(audit_aux[0][f"v171_{key}"]) == 0.0
                for key in GEOMETRY_KEYS
            )
        ),
        "audit_final_geometry_initialized": (
            audit_aux[32]["v171_geometry_initialized"] is True
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
        "audit_instrumentation_policy_update_bit_exact_to_control": (
            initial_policy_comparison["bit_exact"]
            and final_policy_comparison["bit_exact"]
        ),
        "audit_instrumentation_cost_update_bit_exact_to_control": (
            initial_cost_comparison["bit_exact"]
            and final_cost_comparison["bit_exact"]
        ),
        "audit_instrumentation_dual_state_bit_exact_to_control": (
            aux_control_exact
        ),
        "step0_deployed_inference_matches_v121_half": step0_error <= 1.0e-7,
        "both_deployed_graph_contracts_pass": all(
            row["inference"]["pass"] for row in deployed.values()
        ),
        "wall_seconds_at_most_1800_each": (
            control_elapsed <= 1800 and audit_elapsed <= 1800
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v171.gradient_geometry_result.v1",
        "status": (
            "PASS_WINNER_V171_GRADIENT_GEOMETRY_AUDIT"
            if not failed
            else "HOLD_WINNER_V171_GRADIENT_GEOMETRY_AUDIT"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {
            **observed_hashes,
            "preregistration": sha256(PREREG),
        },
        "geometry": {
            **geometry,
            "float32_directional_tolerance": tolerance,
            "retention_floor": retention_floor,
            "expected_cost_descent_derivative": expected_cost_descent,
        },
        "audit_only_equivalence": {
            "initial_policy": initial_policy_comparison,
            "final_policy": final_policy_comparison,
            "initial_cost_critic": initial_cost_comparison,
            "final_cost_critic": final_cost_comparison,
            "dual_state_exact": aux_control_exact,
        },
        "deployment": {
            "step0_v121_half_max_abs_error": step0_error,
            "graphs": deployed,
        },
        "execution": {
            "control_command": control_command,
            "audit_command": audit_command,
            "control_elapsed_seconds": control_elapsed,
            "audit_elapsed_seconds": audit_elapsed,
            "work_root": str(work),
        },
        "decision": (
            "EARN_V172_LEXICOGRAPHIC_TANGENT_UPDATE_CPU_CONTRACT_ONLY"
            if not failed
            else "CLOSE_LEXICOGRAPHIC_TANGENT_OPTIMIZER_GEOMETRY"
        ),
        "authority": {
            "v172_cpu_contract_design": not failed,
            "training": False,
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
        "# Winner V171 actor-gradient geometry result\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Reward-gradient norm: `{geometry['reward_gradient_norm']}`.\n"
        f"- Cost-gradient norm: `{geometry['cost_gradient_norm']}`.\n"
        f"- Reward/cost gradient cosine: "
        f"`{geometry['reward_cost_gradient_cosine']}`.\n"
        f"- Projection active: `{bool(round(geometry['projection_active']))}`.\n"
        f"- Projected direction retention: "
        f"`{geometry['projected_reward_direction_retention']}` "
        f"(floor `{retention_floor}`).\n"
        f"- Cost derivative before/after: "
        f"`{geometry['reward_descent_cost_derivative_before']}` / "
        f"`{geometry['projected_cost_derivative_after']}`.\n"
        f"- Audit update bit-exact to control: "
        f"`{final_policy_comparison['bit_exact']}`.\n"
        f"- Decision: `{payload['decision']}`\n"
        "- CPU-only audit; no hosted training, candidate selection, "
        "robustness authorization, Gate 5, RDK-X5, or robot.\n",
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
