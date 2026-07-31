#!/usr/bin/env python3
"""Compose a V131 two-fit oracle evaluator from the frozen V126 source."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools/closed_loop_sim_eval_v126_all_tick.py"
HELPER = ROOT / "tools/exact_torque_oracle_two_fit.py"
EXPECTED = {
    "source": (
        "9ac610245ea835f023c1e933ad1224bf0e4f1cd94ba84a224f29c9cde32fe21b"
    ),
    "helper": (
        "c9894fa982d0837fbd6281dc778248365c9079e60680c928fd34a50c2e55eb27"
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def replace_once(text: str, old: str, new: str, name: str) -> str:
    if text.count(old) != 1:
        raise ValueError(
            f"V131 expected one {name} marker, found {text.count(old)}"
        )
    return text.replace(old, new, 1)


def compose(text: str) -> str:
    text = replace_once(
        text,
        "from oracle_phase_com_controller import (\n",
        "from exact_torque_oracle_two_fit import project_two_fit_action\n"
        "from oracle_phase_com_controller import (\n",
        "two-fit import",
    )
    text = replace_once(
        text,
        "    exact_torque_oracle_schedule_ticks: tuple[int, ...] | None = None\n",
        "    exact_torque_oracle_schedule_ticks: tuple[int, ...] | None = None\n"
        "    exact_torque_oracle_shadow_fit: Mapping[str, Any] | None = None\n"
        "    exact_torque_oracle_maximum_fit_passes: int = 14\n",
        "config fields",
    )
    text = replace_once(
        text,
        "        termination_reason = None\n",
        "        exact_oracle_shadow_bridge = (\n"
        "            None\n"
        "            if config.exact_torque_oracle_shadow_fit is None\n"
        "            else ActuatorBridgeModel(\n"
        "                mode_params(\n"
        '                    "fitted",\n'
        "                    config.exact_torque_oracle_shadow_fit,\n"
        "                    include_gain_ratio=bool(\n"
        "                        config.winner_v3_home_relative_actuator_gain\n"
        "                    ),\n"
        "                ),\n"
        "                initial_target=initial_target,\n"
        "                home_target=(\n"
        "                    np.asarray(env._default_actuator, dtype=float)\n"
        "                    if config.winner_v3_home_relative_actuator_gain\n"
        "                    else None\n"
        "                ),\n"
        "            )\n"
        "        )\n"
        "        if (\n"
        "            exact_oracle_shadow_bridge is not None\n"
        "            and policy_observer_bridge is not None\n"
        "        ):\n"
        "            raise ValueError(\n"
        '                "V131 two-fit oracle excludes a separate policy observer fit"\n'
        "            )\n"
        "        termination_reason = None\n",
        "shadow bridge initialization",
    )

    block_start = text.index(
        "                    def exact_oracle_rollout(\n"
    )
    block_end = text.index("\n                    try:\n", block_start)
    rollout_block = '''                    def exact_oracle_rollout_with_bridge(
                        candidate_action: np.ndarray,
                        bridge_seed: ActuatorBridgeModel,
                    ) -> np.ndarray:
                        branch_state = state.replace(
                            info=dict(state.info),
                            metrics=dict(state.metrics),
                        )
                        branch_bridge = copy.deepcopy(bridge_seed)
                        branch_hidden = {
                            name: np.asarray(value, dtype=np.float32).copy()
                            for name, value in hidden_state.items()
                        }
                        if "previous_action" in branch_hidden:
                            branch_hidden["previous_action"] = np.asarray(
                                candidate_action, dtype=np.float32
                            )[None, :]
                        branch_imu_history = winner_v3_imu_history.copy()
                        force_rows: list[np.ndarray] = []
                        branch_action = np.asarray(
                            candidate_action, dtype=np.float32
                        )
                        for offset in range(maximum_horizon + 1):
                            if offset > 0:
                                if config.policy_phase_advance_before_observation:
                                    branch_state = advance_reference_jit(
                                        branch_state
                                    )
                                    branch_state = refresh_obs_jit(branch_state)
                                branch_obs = np.asarray(
                                    jax.device_get(
                                        branch_state.obs["state"]
                                    ),
                                    dtype=np.float32,
                                ).copy()
                                branch_imu_history = np.roll(
                                    branch_imu_history, 1, axis=0
                                )
                                branch_imu_history[0] = branch_obs[0:6]
                                branch_obs[0:6] = branch_imu_history[0]
                                branch_feed = {
                                    input_name: branch_obs[None, :]
                                }
                                for state_name in state_input_names:
                                    branch_feed[state_name] = branch_hidden[
                                        state_name
                                    ]
                                branch_outputs = session.run(
                                    [output_name, *state_output_names],
                                    branch_feed,
                                )
                                branch_action = graph_authoritative_action(
                                    branch_outputs[0],
                                    expected_action_dim=(
                                        config.expected_action_dim
                                    ),
                                    previous_action_output=(
                                        branch_outputs[
                                            1
                                            + state_output_names.index(
                                                "previous_action_out"
                                            )
                                        ]
                                        if "previous_action_out"
                                        in state_output_names
                                        else None
                                    ),
                                )
                                for (
                                    state_name,
                                    _output_state_name,
                                    value,
                                ) in zip(
                                    state_input_names,
                                    state_output_names,
                                    branch_outputs[1:],
                                    strict=True,
                                ):
                                    branch_hidden[state_name] = np.asarray(
                                        value, dtype=np.float32
                                    )
                            (
                                branch_state,
                                _branch_action_w_delay,
                                _branch_pre_rate,
                                branch_sent_target,
                                branch_push,
                                branch_push_impulse,
                            ) = prepare_step_jit(
                                branch_state, jp.asarray(branch_action)
                            )
                            branch_sent_np = np.asarray(
                                jax.device_get(branch_sent_target),
                                dtype=float,
                            )
                            branch_applied_np = branch_bridge.step(
                                branch_sent_np, float(env.dt)
                            )
                            branch_state = apply_motor_target_runner(
                                branch_state,
                                jp.asarray(branch_action),
                                branch_sent_target,
                                jp.asarray(branch_applied_np),
                                jp.asarray(branch_applied_np),
                                branch_push,
                                branch_push_impulse,
                            )
                            force_rows.append(
                                np.asarray(
                                    jax.device_get(
                                        branch_state.data.actuator_force
                                    ),
                                    dtype=np.float64,
                                )
                            )
                        return np.asarray(force_rows, dtype=np.float64)

                    def exact_oracle_rollout(
                        candidate_action: np.ndarray,
                    ) -> np.ndarray:
                        return exact_oracle_rollout_with_bridge(
                            candidate_action, bridge
                        )

                    def exact_oracle_shadow_rollout(
                        candidate_action: np.ndarray,
                    ) -> np.ndarray:
                        if exact_oracle_shadow_bridge is None:
                            raise ValueError(
                                "V131 shadow rollout requested without fit"
                            )
                        return exact_oracle_rollout_with_bridge(
                            candidate_action, exact_oracle_shadow_bridge
                        )
'''
    text = text[:block_start] + rollout_block + text[block_end:]

    call_start = text.index(
        "                    try:\n", block_start
    )
    call_end = text.index(
        "                    except ValueError as exc:\n", call_start
    )
    call_block = '''                    try:
                        if exact_oracle_shadow_bridge is None:
                            action, exact_oracle_tick = (
                                project_exact_torque_action(
                                    base_action=action,
                                    low_action=low_action,
                                    high_action=high_action,
                                    force_horizon_ticks=horizons,
                                    rollout=exact_oracle_rollout,
                                    constants=exact_oracle_constants,
                                )
                            )
                        else:
                            action, exact_oracle_tick = (
                                project_two_fit_action(
                                    base_action=action,
                                    low_action=low_action,
                                    high_action=high_action,
                                    force_horizon_ticks=horizons,
                                    primary_rollout=exact_oracle_rollout,
                                    shadow_rollout=exact_oracle_shadow_rollout,
                                    constants=exact_oracle_constants,
                                    maximum_fit_passes=int(
                                        config.exact_torque_oracle_maximum_fit_passes
                                    ),
                                )
                            )
'''
    text = text[:call_start] + call_block + text[call_end:]

    main_step_marker = '''            applied_np = (
                sent_np.copy()
                if mode == "vanilla"
                else bridge.step(sent_np, float(env.dt))
            )
            policy_observer_applied_np = (
'''
    main_step_replacement = '''            applied_np = (
                sent_np.copy()
                if mode == "vanilla"
                else bridge.step(sent_np, float(env.dt))
            )
            if exact_oracle_shadow_bridge is not None:
                exact_oracle_shadow_bridge.step(sent_np, float(env.dt))
            policy_observer_applied_np = (
'''
    if text.count(main_step_marker) != 1:
        raise ValueError(
            "V131 could not isolate the real main-loop bridge step"
        )
    text = text.replace(main_step_marker, main_step_replacement, 1)
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    output_root = args.output_root.resolve()
    if output_root.exists():
        raise FileExistsError(
            f"refusing to overwrite V131 evaluator: {output_root}"
        )
    input_hashes = {"source": sha256(SOURCE), "helper": sha256(HELPER)}
    if input_hashes != EXPECTED:
        raise ValueError("V131 evaluator inputs changed")
    output_root.mkdir(parents=True)
    output = output_root / "closed_loop_sim_eval_v131_two_fit.py"
    output.write_text(
        compose(SOURCE.read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    compile(output.read_text(encoding="utf-8"), str(output), "exec")
    manifest = {
        "schema_version": "winner_v131.two_fit_evaluator_composition.v1",
        "status": "PASS_WINNER_V131_TWO_FIT_EVALUATOR_COMPOSITION",
        "input_hashes": input_hashes,
        "output": {
            "path": str(output),
            "sha256": sha256(output),
            "bytes": output.stat().st_size,
        },
        "default_off": (
            "exact_torque_oracle_shadow_fit=None preserves the V126 path"
        ),
        "authority": {
            "cpu_contract": False,
            "formal_behavior": False,
            "training": False,
            "hosted_training": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    manifest_path = output_root / "composition_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    print(manifest["status"])
    print(f"output_sha256={manifest['output']['sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
