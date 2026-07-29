from __future__ import annotations

import json
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np

from tools.t147_command_group_risk import (
    command_group_ids,
    grouped_policy_loss,
)


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_group_ids_and_unique_worst_gradient() -> None:
    commands = jnp.asarray([0.074, 0.074, 0.077, 0.077, 0.08, 0.08])
    surrogate = jnp.asarray([1.0, 1.0, -2.0, -2.0, 0.0, 0.0])
    assert np.array_equal(
        np.asarray(command_group_ids(commands)),
        np.asarray([0, 0, 1, 1, 2, 2]),
    )
    loss, metrics = grouped_policy_loss(surrogate, commands)
    gradient = jax.grad(lambda x: grouped_policy_loss(x, commands)[0])(
        surrogate
    )
    assert float(loss) == 2.0
    assert int(metrics["selected_group"]) == 1
    assert np.array_equal(
        np.asarray(gradient),
        np.asarray([0.0, 0.0, -0.5, -0.5, 0.0, 0.0]),
    )


def test_t147_preregistration_when_present() -> None:
    path = ANALYSIS / "t147_command_group_risk_cpu_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T147_COMMAND_GROUP_RISK_CPU_CONTRACT"
    )
    assert value["mechanism"]["new_scalar_hyperparameters"] == 0


def test_t147_result_when_present() -> None:
    path = ANALYSIS / "t147_command_group_risk_cpu_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T147_COMMAND_GROUP_RISK_CPU_CONTRACT"
    assert value["failed_checks"] == []
    assert value["execution"]["optimizer_steps"] == 0
