from __future__ import annotations

from pathlib import Path

import jax.numpy as jnp
import numpy as np
import pytest

from training import t227_command_atom_bank as bank


ROOT = Path(__file__).resolve().parents[1]


def test_t227_exact_256_cartesian_lattice() -> None:
    configuration = np.asarray(bank.configuration_category_ids(256))
    command = np.asarray(bank.command_category_ids(256))
    assert np.array_equal(configuration[:8], np.arange(8))
    assert np.array_equal(command[:8], np.zeros(8, dtype=np.int32))
    assert np.array_equal(command[8:16], np.ones(8, dtype=np.int32))
    counts = bank.cartesian_counts(256)
    assert len(counts) == 32
    assert set(counts.values()) == {8}


def test_t227_command_selection_preserves_broad_and_exact_atoms() -> None:
    sampled = jnp.asarray([0.0755] * 32, dtype=jnp.float32)
    selected = np.asarray(
        jnp.asarray(
            [
                bank.select_forward_command(sampled[index], index)
                for index in range(32)
            ]
        )
    )
    assert np.array_equal(selected[:8], np.full(8, np.float32(0.0755)))
    assert np.array_equal(selected[8:16], np.full(8, np.float32(0.074)))
    assert np.array_equal(selected[16:24], np.full(8, np.float32(0.077)))
    assert np.array_equal(selected[24:32], np.full(8, np.float32(0.080)))


def test_t227_population_must_cover_the_complete_lattice() -> None:
    for population in (0, 8, 31, 33, 256 + 8):
        with pytest.raises(ValueError):
            bank.validate_population(population)
    bank.validate_population(32)
    bank.validate_population(256)


def test_t227_composer_freezes_training_only_scope() -> None:
    text = (
        ROOT / "tools/compose_t227_command_atom_playground.py"
    ).read_text(encoding="utf-8")
    assert "winner_t227_command_atom_bank=False" in text
    assert "self._winner_t227_command_atom_bank_enabled" in text
    assert "self.env.unwrapped._config.winner_t227_command_atom_bank = True" in text
    assert "self.eval_env.unwrapped._config.winner_t227_command_atom_bank = True" in text
    assert "args.ppo_num_envs % 32 == 0" in text
    assert "select_named_axis_forward" in text
    assert '"configuration_randomizer_change": False' in text
    assert '"reward_change": False' in text
    assert '"cost_change": False' in text
    assert '"policy_abi_change": False' in text
    assert '"deployment_graph_change": False' in text
    assert '"x_zero_training_change": False' in text


def test_t227_cpu_contract_freezes_scope_and_authority() -> None:
    builder = (
        ROOT / "tools/build_t227_command_atom_cpu_preregistration.py"
    ).read_text(encoding="utf-8")
    runner = (
        ROOT / "tools/run_t227_command_atom_cpu_contract.py"
    ).read_text(encoding="utf-8")
    worker = (
        ROOT / "tools/run_t227_command_atom_environment_worker.py"
    ).read_text(encoding="utf-8")
    assert '"source": "T216_FINAL"' in builder
    assert '"cartesian_strata": 32' in builder
    assert '"reward_change": False' in builder
    assert '"cost_change": False' in builder
    assert '"hosted_training": False' in builder
    assert '"--winner_t227_command_atom_bank"' in runner
    assert '"--ppo_num_envs", "32"' in runner
    assert '"--ppo_batch_size", "32"' in runner
    assert "only_t216_negative_adapter_head_changes" in runner
    assert "exact_32_cell_cartesian_reset_green" in runner
    assert "exact_command_atoms_survive_t19_reset_and_resample" in worker
    assert '"optimizer_steps": 0' in worker
    assert '"formal_behavior_cells": 0' in worker


def test_t227a_retry_is_instrumentation_only() -> None:
    builder = (
        ROOT
        / "tools/build_t227a_command_atom_cpu_retry_preregistration.py"
    ).read_text(encoding="utf-8")
    runner = (
        ROOT / "tools/run_t227a_command_atom_cpu_contract.py"
    ).read_text(encoding="utf-8")
    worker = (
        ROOT / "tools/run_t227_command_atom_environment_worker.py"
    ).read_text(encoding="utf-8")
    assert "POST_RESET_AUDIT_READ_OF_ESCAPED_JAX_TRACER" in builder
    assert '"scientific_mechanism_changed": False' in builder
    assert '"optimizer_steps_before_abort": 0' in builder
    assert '"one_corrected_cpu_contract_retry": True' in builder
    assert "t227a_command_atom_cpu_contract_v2" in runner
    assert '"prior_optimizer_steps": 0' in runner
    assert "nominal_torso_body_ipos = np.asarray(" in worker
    assert "- nominal_torso_body_ipos" in worker
