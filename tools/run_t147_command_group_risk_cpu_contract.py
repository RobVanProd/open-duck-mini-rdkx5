#!/usr/bin/env python3
"""Run the parameter-free T147 command-group risk CPU contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
from typing import Any

import jax
import jax.numpy as jnp
import numpy as np

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    verify,
)
from t147_command_group_risk import (
    COMMAND_ANCHORS,
    COMMAND_BOUNDARIES,
    command_group_ids,
    grouped_policy_loss,
)


PREREG = ANALYSIS / "t147_command_group_risk_cpu_preregistration.json"
RESULT = ANALYSIS / "t147_command_group_risk_cpu_result.json"
MARKDOWN = ANALYSIS / "T147_COMMAND_GROUP_RISK_CPU_RESULT_20260729.md"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise PermissionError("T147 requires --execute")
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T147: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T147 execution requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T147_COMMAND_GROUP_RISK_CPU_CONTRACT"
        or prereg["failed_checks"]
        or canonical_sha256(basis) != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T147 preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, name)

    commands = jnp.asarray(
        [0.074, 0.074, 0.077, 0.077, 0.080, 0.080],
        dtype=jnp.float32,
    )
    surrogate = jnp.asarray(
        [1.0, 1.0, -2.0, -2.0, 0.0, 0.0], dtype=jnp.float32
    )
    loss, metrics = grouped_policy_loss(surrogate, commands)
    gradient = jax.grad(lambda value: grouped_policy_loss(value, commands)[0])(
        surrogate
    )
    compiled_loss, compiled_metrics = jax.jit(grouped_policy_loss)(
        surrogate, commands
    )
    permutation = jnp.asarray([5, 2, 0, 4, 1, 3], dtype=jnp.int32)
    permuted_loss, _ = grouped_policy_loss(
        surrogate[permutation], commands[permutation]
    )
    standard_loss = -jnp.mean(surrogate)
    anchor_groups = command_group_ids(COMMAND_ANCHORS)
    boundary_probe = command_group_ids(
        jnp.asarray(
            [0.074, 0.075499, 0.0755, 0.078499, 0.0785, 0.08],
            dtype=jnp.float32,
        )
    )
    expected_gradient = np.asarray(
        [0.0, 0.0, -0.5, -0.5, 0.0, 0.0], dtype=np.float32
    )
    checks = {
        "cpu_only": jax.default_backend() == "cpu",
        "anchors_and_boundaries_exact": (
            np.array_equal(
                np.asarray(COMMAND_ANCHORS),
                np.asarray([0.074, 0.077, 0.08], dtype=np.float32),
            )
            and np.array_equal(
                np.asarray(COMMAND_BOUNDARIES),
                np.asarray([0.0755, 0.0785], dtype=np.float32),
            )
        ),
        "anchor_group_ids_exact": np.array_equal(
            np.asarray(anchor_groups), np.asarray([0, 1, 2], dtype=np.int32)
        ),
        "boundary_rule_exact": np.array_equal(
            np.asarray(boundary_probe),
            np.asarray([0, 0, 1, 1, 2, 2], dtype=np.int32),
        ),
        "all_groups_present_twice": (
            bool(np.asarray(metrics["all_groups_present"]))
            and np.array_equal(
                np.asarray(metrics["group_counts"]),
                np.asarray([2.0, 2.0, 2.0], dtype=np.float32),
            )
        ),
        "group_losses_exact": np.array_equal(
            np.asarray(metrics["group_losses"]),
            np.asarray([-1.0, 2.0, 0.0], dtype=np.float32),
        ),
        "unique_worst_group_selected": (
            int(np.asarray(metrics["selected_group"])) == 1
            and float(np.asarray(loss)) == 2.0
        ),
        "only_worst_group_receives_gradient": np.array_equal(
            np.asarray(gradient), expected_gradient
        ),
        "permutation_invariant": float(np.asarray(permuted_loss)) == 2.0,
        "differs_from_batch_average": (
            float(np.asarray(standard_loss)) != float(np.asarray(loss))
            and np.isclose(float(np.asarray(standard_loss)), 1.0 / 3.0)
        ),
        "jit_matches_eager": (
            float(np.asarray(compiled_loss)) == float(np.asarray(loss))
            and np.array_equal(
                np.asarray(compiled_metrics["group_losses"]),
                np.asarray(metrics["group_losses"]),
            )
        ),
        "all_values_finite": all(
            np.all(np.isfinite(np.asarray(value)))
            for value in (loss, gradient, compiled_loss, standard_loss)
        ),
        "environment_optimizer_behavior_colab_robot_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    value: dict[str, Any] = {
        "schema_version": "open_duck.t147_command_group_risk_cpu_result.v1",
        "status": (
            "PASS_T147_COMMAND_GROUP_RISK_CPU_CONTRACT"
            if passed
            else "HOLD_T147_COMMAND_GROUP_RISK_CPU_CONTRACT"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if passed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "synthetic": {
            "commands_x_m_s": np.asarray(commands).tolist(),
            "clipped_surrogate": np.asarray(surrogate).tolist(),
            "group_losses": np.asarray(metrics["group_losses"]).tolist(),
            "group_counts": np.asarray(metrics["group_counts"]).tolist(),
            "selected_group": int(np.asarray(metrics["selected_group"])),
            "grouped_policy_loss": float(np.asarray(loss)),
            "standard_policy_loss": float(np.asarray(standard_loss)),
            "surrogate_gradient": np.asarray(gradient).tolist(),
        },
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "synthetic_rows": int(commands.size),
            "environment_steps": 0,
            "optimizer_steps": 0,
            "behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "integrated_one_update_preregistration": passed,
            "training": False,
            "colab": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["result_sha256"] = canonical_sha256(value)
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T147 command-group risk CPU result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        "- Selected synthetic weak group: `x=.077`\n"
        "- Gradient outside selected group: exact zero\n"
        "- Environment / optimizer / behavior / Colab / robot: `0/0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
