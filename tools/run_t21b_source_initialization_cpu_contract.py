#!/usr/bin/env python3
"""Run T21b's corrected source-coordinate initialization CPU contract."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

import numpy as np

import run_t21_two_rate_separation_cpu_contract as t21


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREGISTRATION = (
    ANALYSIS / "t21b_source_initialization_cpu_preregistration.json"
)
RESULT = ANALYSIS / "t21b_source_initialization_cpu_result.json"
MARKDOWN = (
    ANALYSIS / "T21B_SOURCE_INITIALIZATION_CPU_RESULT_20260726.md"
)


def prefix_diagnostic_worker(
    playground: Path,
    reference: Path,
    *,
    seed: int,
) -> dict[str, Any]:
    sys.path.insert(0, str(playground))
    import jax
    import jax.numpy as jnp
    from playground.common import t19_support_trainthrough as t19
    from playground.open_duck_mini_v2 import joystick

    config = t21.configure_environment(
        joystick,
        reference,
        enabled=True,
        deviation_scale=0.0,
    )
    env = joystick.Joystick(
        task="flat_terrain_backlash",
        config=config,
    )
    wrapper = t19.SupportPrefixWrapper(env)
    diagnostic = jax.jit(wrapper.prefix_diagnostic)(
        jax.random.PRNGKey(seed)
    )
    actions = np.asarray(jax.device_get(diagnostic["actions"]))
    motor_targets = np.asarray(
        jax.device_get(diagnostic["motor_targets"])
    )
    source_targets = np.asarray(
        jax.device_get(diagnostic["source_motor_targets"])
    )
    valid = bool(np.asarray(jax.device_get(diagnostic["valid"])))
    home = np.asarray(env._default_actuator, dtype=np.float32)
    expected_motor_targets = (
        home[None, :] + actions * np.float32(0.25)
    )
    coherent_initial_source = (
        home
        + np.asarray(
            t19.inverse_action(jnp.zeros(14, dtype=jnp.float32))
        )
        * np.float32(0.25)
    )
    previous_motor_targets = np.concatenate(
        (home[None, :], motor_targets[:-1]),
        axis=0,
    )
    previous_source_targets = np.concatenate(
        (coherent_initial_source[None, :], source_targets[:-1]),
        axis=0,
    )
    motor_differences = np.abs(
        motor_targets - previous_motor_targets
    )
    source_differences = np.abs(
        source_targets - previous_source_targets
    )
    external_limits = (
        t21.EXTERNAL_RATE_LIMITS_RAD_S * np.float32(0.02)
    )
    source_limits = t21.SOURCE_RATE_LIMITS_RAD_S * np.float32(0.02)
    tolerance = float(64 * np.finfo(np.float32).eps)
    configured_source = np.asarray(
        config.ground_up_action_velocity_limits_rad_s,
        dtype=np.float32,
    )
    external_target_error = float(
        np.max(
            np.abs(
                motor_targets.astype(np.float64)
                - expected_motor_targets.astype(np.float64)
            )
        )
    )
    external_excess = t21._maximum_excess(
        motor_differences,
        external_limits,
    )
    source_excess = t21._maximum_excess(
        source_differences,
        source_limits,
    )
    source_home_error = float(
        np.max(
            np.abs(
                source_targets[-1].astype(np.float64)
                - home.astype(np.float64)
            )
        )
    )
    checks = {
        "cpu_only": sorted({device.platform for device in jax.devices()})
        == ["cpu"],
        "prefix_valid": valid,
        "history_shapes_exact": (
            actions.shape
            == motor_targets.shape
            == source_targets.shape
            == (250, 14)
        ),
        "coherent_initial_source_is_nonzero": (
            np.count_nonzero(coherent_initial_source - home) > 0
        ),
        "external_target_matches_action_all_ticks": (
            external_target_error <= tolerance
        ),
        "external_physical_rate_all_ticks": (
            external_excess <= tolerance
        ),
        "source_trained_rate_all_ticks": source_excess <= tolerance,
        "final_external_support_exact": np.array_equal(
            actions[-1],
            np.asarray(t19.SUPPORT_ACTION, dtype=np.float32),
        ),
        "final_external_target_exact": (
            float(
                np.max(
                    np.abs(
                        motor_targets[-1].astype(np.float64)
                        - (
                            home
                            + np.asarray(
                                t19.SUPPORT_ACTION,
                                dtype=np.float32,
                            )
                            * np.float32(0.25)
                        ).astype(np.float64)
                    )
                )
            )
            <= tolerance
        ),
        "final_source_target_returns_home": (
            source_home_error <= tolerance
        ),
        "configured_source_vector_exact": np.array_equal(
            configured_source,
            t21.SOURCE_RATE_LIMITS_RAD_S,
        ),
        "module_source_vector_exact": np.array_equal(
            np.asarray(t19.SOURCE_RATE_LIMITS_RAD_S),
            t21.SOURCE_RATE_LIMITS_RAD_S,
        ),
        "module_external_vector_exact": np.array_equal(
            np.asarray(t19.RATE_LIMITS_RAD_S),
            t21.EXTERNAL_RATE_LIMITS_RAD_S,
        ),
    }
    checks = {name: bool(passed) for name, passed in checks.items()}
    return {
        "mode": "prefix_diagnostic",
        "playground": str(playground),
        "seed": seed,
        "ticks": int(actions.shape[0]),
        "checks": checks,
        "failed_checks": sorted(
            name for name, passed in checks.items() if not passed
        ),
        "coherent_initial_source_target_rad": (
            coherent_initial_source.astype(float).tolist()
        ),
        "maximum_errors": {
            "external_target_rad": external_target_error,
            "external_rate_excess_rad_per_tick": external_excess,
            "source_rate_excess_rad_per_tick": source_excess,
            "final_source_home_rad": source_home_error,
        },
        "source_rate_limits_rad_s": configured_source.astype(float).tolist(),
        "external_rate_limits_rad_s": (
            t21.EXTERNAL_RATE_LIMITS_RAD_S.astype(float).tolist()
        ),
        "platforms": sorted({device.platform for device in jax.devices()}),
    }


def worker_main(args: argparse.Namespace) -> int:
    playground = args.playground.resolve()
    reference = args.reference.resolve()
    if args.worker == "default_off":
        value = t21.default_off_worker(playground, reference)
    elif args.worker == "enabled":
        value = t21.enabled_worker(
            playground,
            reference,
            env_count=args.env_count,
            seed=args.seed,
        )
    elif args.worker == "prefix_diagnostic":
        value = prefix_diagnostic_worker(
            playground,
            reference,
            seed=args.seed,
        )
    else:
        raise ValueError(args.worker)
    args.worker_output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(value, allow_nan=False, sort_keys=True))
    return 0


def run_worker(
    mode: str,
    playground: Path,
    reference: Path,
    output: Path,
    *,
    env_count: int,
    seed: int,
) -> dict[str, Any]:
    command = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--worker",
        mode,
        "--playground",
        str(playground),
        "--reference",
        str(reference),
        "--env-count",
        str(env_count),
        "--seed",
        str(seed),
        "--worker-output",
        str(output),
    ]
    environment = dict(os.environ)
    environment.update(
        {
            "CUDA_VISIBLE_DEVICES": "",
            "HIP_VISIBLE_DEVICES": "",
            "JAX_PLATFORMS": "cpu",
            "XLA_PYTHON_CLIENT_PREALLOCATE": "false",
            "JAX_COMPILATION_CACHE_DIR": str(
                Path(
                    "D:/CodexArtifacts/open-duck-policy/"
                    "jax_compilation_cache"
                )
            ),
        }
    )
    completed = subprocess.run(
        command,
        cwd=playground,
        env=environment,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=1800,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"T21b worker failed mode={mode} rc={completed.returncode}\n"
            f"{completed.stdout[-12000:]}"
        )
    return json.loads(output.read_text(encoding="utf-8"))


def formal_main(args: argparse.Namespace) -> int:
    if not args.execute:
        raise SystemExit("T21b formal contract requires --execute")
    for path in (RESULT, MARKDOWN, args.work_root):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T21b path: {path}")
    prereg = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    basis = {
        key: prereg[key]
        for key in (
            "schema_version",
            "status",
            "question",
            "causal_basis",
            "sources",
            "playgrounds",
            "contract",
            "decision_rule",
            "authority",
            "execution_now",
        )
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T21B_SOURCE_INITIALIZATION_CPU_CONTRACT"
        or t21.canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T21b preregistration identity changed")
    for name, value in prereg["sources"].items():
        t21.verify_receipt(value, name)
    args.work_root.mkdir(parents=True)
    reference = Path(prereg["contract"]["reference_path"])
    base = Path(prereg["playgrounds"]["base"]["path"])
    composed = Path(prereg["playgrounds"]["composed"]["path"])
    seed = prereg["contract"]["seed"]
    base_value = run_worker(
        "default_off",
        base,
        reference,
        args.work_root / "base_default_off.json",
        env_count=1,
        seed=seed,
    )
    composed_value = run_worker(
        "default_off",
        composed,
        reference,
        args.work_root / "composed_default_off.json",
        env_count=1,
        seed=seed,
    )
    enabled_value = run_worker(
        "enabled",
        composed,
        reference,
        args.work_root / "enabled.json",
        env_count=prereg["contract"]["variable_configuration_envs"],
        seed=seed,
    )
    diagnostic_value = run_worker(
        "prefix_diagnostic",
        composed,
        reference,
        args.work_root / "prefix_diagnostic.json",
        env_count=1,
        seed=seed,
    )
    checks = {
        "default_off_canonical_trajectory_9_of_9": (
            len(base_value["trajectory_digests"]) == 9
            and base_value["trajectory_digests"]
            == composed_value["trajectory_digests"]
        ),
        "default_off_shapes_exact": (
            base_value["observation_shape"]
            == composed_value["observation_shape"]
            == [115]
        ),
        "default_off_finite": (
            base_value["finite"] and composed_value["finite"]
        ),
        "all_64_variable_configuration_checks_pass": (
            enabled_value["env_count"] == 64
            and enabled_value["prefix_valid_count"] == 64
            and enabled_value["episode_reset_count"] == 64
            and enabled_value["failed_checks"] == []
        ),
        "all_250_prefix_diagnostic_checks_pass": (
            diagnostic_value["ticks"] == 250
            and diagnostic_value["failed_checks"] == []
        ),
        "cpu_only": (
            base_value["platforms"]
            == composed_value["platforms"]
            == enabled_value["platforms"]
            == diagnostic_value["platforms"]
            == ["cpu"]
        ),
        "optimizer_steps_zero": True,
        "hosted_compute_zero": True,
        "robot_access_zero": True,
    }
    checks = {name: bool(passed) for name, passed in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    result_basis = {
        "schema_version": "open_duck.t21b_source_initialization_result.v1",
        "status": (
            "PASS_T21B_SOURCE_INITIALIZATION_CPU_CONTRACT"
            if not failed
            else "HOLD_T21B_SOURCE_INITIALIZATION_CPU_CONTRACT"
        ),
        "decision": (
            "EARN_T22_CORRECTED_ONE_UPDATE_CPU_SMOKE"
            if not failed
            else "CLOSE_T21B_SOURCE_INITIALIZATION_IMPLEMENTATION"
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "default_off": {
            "base": base_value,
            "composed": composed_value,
        },
        "enabled": enabled_value,
        "prefix_diagnostic": diagnostic_value,
        "execution": {
            "optimizer_steps": 0,
            "hosted_or_colab_compute": 0,
            "robot_or_rdk_access": 0,
        },
    }
    value = {
        **result_basis,
        "result_sha256": t21.canonical_sha256(result_basis),
    }
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T21b source-coordinate initialization CPU result",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                f"- Failed checks: `{failed}`",
                (
                    "- Variable-configuration prefixes/resets: "
                    f"`{enabled_value['prefix_valid_count']}/"
                    f"{enabled_value['episode_reset_count']}/64`"
                ),
                (
                    "- Prefix diagnostic: "
                    f"`{diagnostic_value['ticks']}/250 ticks`"
                ),
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
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if not failed else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--worker",
        choices=("default_off", "enabled", "prefix_diagnostic"),
    )
    parser.add_argument("--playground", type=Path)
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--env-count", type=int, default=64)
    parser.add_argument("--seed", type=int, default=100)
    parser.add_argument("--worker-output", type=Path)
    parser.add_argument("--work-root", type=Path)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.worker:
        required = (
            args.playground,
            args.reference,
            args.worker_output,
        )
        if any(value is None for value in required):
            raise SystemExit("T21b worker arguments are incomplete")
        return worker_main(args)
    if args.work_root is None:
        raise SystemExit("T21b formal contract requires --work-root")
    return formal_main(args)


if __name__ == "__main__":
    raise SystemExit(main())
