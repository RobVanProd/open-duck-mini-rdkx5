#!/usr/bin/env python3
"""Prepare the Open Duck Playground training actuator bridge patch.

Default mode is read-only: it validates the expected Joystick insertion points
and prints a unified diff. Pass --apply to modify the sibling Playground
checkout.
"""

from __future__ import annotations

import argparse
import difflib
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAYGROUND = ROOT.parent / "Open_Duck_Playground"
JOYSTICK_REL = Path("playground/open_duck_mini_v2/joystick.py")


ACTUATOR_BRIDGE_CONFIG = '''        actuator_bridge=config_dict.create(
            enable=False,
            delay_min_ticks=3,
            delay_max_ticks=8,
            tau_min_s=0.06,
            tau_max_s=0.14,
            velocity_limit_min_rad_s=2.5,
            velocity_limit_max_rad_s=4.7,
            per_joint_variation=0.15,
        ),
'''


BRIDGE_SAMPLE_BLOCK = '''        rng, bridge_rng = jax.random.split(rng)
        bridge_delay_ticks, bridge_tau_s, bridge_velocity_limit_rad_s = (
            self._sample_actuator_bridge_params(bridge_rng)
        )

'''


BRIDGE_INFO_BLOCK = '''            "actuator_bridge_target_history": jp.tile(
                self._default_actuator,
                self._config.actuator_bridge.delay_max_ticks + 1,
            ),
            "actuator_bridge_applied_targets": self._default_actuator,
            "actuator_bridge_delay_ticks": bridge_delay_ticks,
            "actuator_bridge_tau_s": bridge_tau_s,
            "actuator_bridge_velocity_limit_rad_s": bridge_velocity_limit_rad_s,
            "actuator_bridge_tracking_cost": jp.zeros(()),
            "target_velocity_cost": jp.zeros(()),
'''


HELPER_METHODS = '''
    def _sample_actuator_bridge_params(
        self, rng: jax.Array
    ) -> tuple[jax.Array, jax.Array, jax.Array]:
        """Sample per-episode actuator bridge parameters.

        The bridge is disabled by default. When enabled, it models the measured
        real target-to-joint delay with a target delay queue, first-order lag,
        and effective velocity limit. Shapes are fixed by delay_max_ticks so the
        environment remains JAX-compilable.
        """
        cfg = self._config.actuator_bridge
        if not cfg.enable:
            return (
                jp.array(0, dtype=jp.int32),
                jp.full((self._actuators,), self.dt),
                jp.full((self._actuators,), self._config.max_motor_velocity),
            )

        rng, delay_rng, tau_rng, vel_rng, tau_jitter_rng, vel_jitter_rng = (
            jax.random.split(rng, 6)
        )
        delay_ticks = jax.random.randint(
            delay_rng,
            (),
            minval=cfg.delay_min_ticks,
            maxval=cfg.delay_max_ticks + 1,
            dtype=jp.int32,
        )
        tau_base = jax.random.uniform(
            tau_rng, (), minval=cfg.tau_min_s, maxval=cfg.tau_max_s
        )
        vel_base = jax.random.uniform(
            vel_rng,
            (),
            minval=cfg.velocity_limit_min_rad_s,
            maxval=cfg.velocity_limit_max_rad_s,
        )
        tau_jitter = jax.random.uniform(
            tau_jitter_rng,
            (self._actuators,),
            minval=1.0 - cfg.per_joint_variation,
            maxval=1.0 + cfg.per_joint_variation,
        )
        vel_jitter = jax.random.uniform(
            vel_jitter_rng,
            (self._actuators,),
            minval=1.0 - cfg.per_joint_variation,
            maxval=1.0 + cfg.per_joint_variation,
        )
        tau_s = jp.clip(tau_base * tau_jitter, cfg.tau_min_s, cfg.tau_max_s)
        velocity_limit = jp.clip(
            vel_base * vel_jitter,
            cfg.velocity_limit_min_rad_s,
            cfg.velocity_limit_max_rad_s,
        )
        return delay_ticks, tau_s, velocity_limit

    def _apply_actuator_bridge(
        self, info: dict[str, Any], sent_motor_targets: jax.Array
    ) -> tuple[jax.Array, dict[str, Any]]:
        """Return the lagged plant target while preserving sent-target history."""
        history = (
            jp.roll(info["actuator_bridge_target_history"], self._actuators)
            .at[: self._actuators]
            .set(sent_motor_targets)
        )
        delayed_target = history.reshape((-1, self._actuators))[
            info["actuator_bridge_delay_ticks"]
        ]
        previous_applied = info["actuator_bridge_applied_targets"]
        tau_s = jp.maximum(info["actuator_bridge_tau_s"], 1.0e-4)
        alpha = 1.0 - jp.exp(-self.dt / tau_s)
        lagged_target = previous_applied + alpha * (delayed_target - previous_applied)
        max_step = info["actuator_bridge_velocity_limit_rad_s"] * self.dt
        applied_target = jp.clip(
            lagged_target,
            previous_applied - max_step,
            previous_applied + max_step,
        )
        info["actuator_bridge_target_history"] = history
        info["actuator_bridge_applied_targets"] = applied_target
        return applied_target, info

'''


BRIDGE_STEP_BLOCK = '''        # motor_targets.at[5:9].set(state.info["command"][3:])  # head joints
        sent_motor_targets = motor_targets
        if not USE_MOTOR_SPEED_LIMITS:
            prev_motor_targets = state.info["motor_targets"]
        target_velocity = (sent_motor_targets - prev_motor_targets) / self.dt
        applied_motor_targets = sent_motor_targets
        if self._config.actuator_bridge.enable:
            applied_motor_targets, _ = self._apply_actuator_bridge(
                state.info, sent_motor_targets
            )
        state.info["target_velocity_cost"] = jp.mean(jp.square(target_velocity))
        state.info["actuator_bridge_tracking_cost"] = jp.mean(
            jp.square(sent_motor_targets - applied_motor_targets)
        )
        data = mjx_env.step(
            self.mjx_model, state.data, applied_motor_targets, self.n_substeps
        )

        state.info["motor_targets"] = sent_motor_targets
'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise ValueError(f"expected one {label} insertion point, found {count}")
    return text.replace(old, new, 1)


def patch_text(text: str) -> str:
    if "actuator_bridge=config_dict.create(" in text:
        return text

    text = replace_once(
        text,
        "        reward_config=config_dict.create(\n",
        ACTUATOR_BRIDGE_CONFIG + "        reward_config=config_dict.create(\n",
        "actuator_bridge config",
    )
    text = replace_once(
        text,
        "                stand_still=-0.2,  # was -1.0\u00a0TODO try to relax this a bit ?\n",
        (
            "                stand_still=-0.2,  # was -1.0\u00a0TODO try to relax this a bit ?\n"
            "                target_rate=0.0,\n"
            "                actuator_tracking=0.0,\n"
        ),
        "reward scales",
    )
    text = replace_once(
        text,
        "        info = {\n",
        BRIDGE_SAMPLE_BLOCK + "        info = {\n",
        "bridge parameter sampling",
    )
    text = replace_once(
        text,
        '            "motor_targets": self._default_actuator,\n',
        '            "motor_targets": self._default_actuator,\n' + BRIDGE_INFO_BLOCK,
        "bridge info state",
    )
    text = replace_once(
        text,
        "    def step(self, state: mjx_env.State, action: jax.Array) -> mjx_env.State:\n",
        HELPER_METHODS
        + "    def step(self, state: mjx_env.State, action: jax.Array) -> mjx_env.State:\n",
        "helper methods",
    )
    text = replace_once(
        text,
        '''        # motor_targets.at[5:9].set(state.info["command"][3:])  # head joints
        data = mjx_env.step(self.mjx_model, state.data, motor_targets, self.n_substeps)

        state.info["motor_targets"] = motor_targets
''',
        BRIDGE_STEP_BLOCK,
        "target-stage bridge",
    )
    text = replace_once(
        text,
        '''            "action_rate": cost_action_rate(action, info["last_act"]),
            "alive": reward_alive(),
''',
        '''            "action_rate": cost_action_rate(action, info["last_act"]),
            "target_rate": info["target_velocity_cost"],
            "actuator_tracking": info["actuator_bridge_tracking_cost"],
            "alive": reward_alive(),
''',
        "bridge reward terms",
    )
    return text


def unified_diff(path: Path, before: str, after: str) -> str:
    return "".join(
        difflib.unified_diff(
            before.splitlines(keepends=True),
            after.splitlines(keepends=True),
            fromfile=f"a/{JOYSTICK_REL}",
            tofile=f"b/{JOYSTICK_REL}",
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare the default-off Open Duck Playground actuator bridge patch."
    )
    parser.add_argument("--playground-path", default=str(DEFAULT_PLAYGROUND))
    parser.add_argument("--apply", action="store_true", help="modify joystick.py")
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate patch generation without applying; default behavior",
    )
    args = parser.parse_args()

    playground = Path(args.playground_path).expanduser().resolve()
    joystick = playground / JOYSTICK_REL
    if not joystick.exists():
        print(f"Missing joystick.py: {joystick}", file=sys.stderr)
        return 2

    before = joystick.read_text()
    try:
        after = patch_text(before)
    except ValueError as exc:
        print(f"HOLD_PATCH_CONTEXT_MISMATCH: {exc}", file=sys.stderr)
        return 3

    if after == before:
        print("PASS_ALREADY_PATCHED")
        return 0

    diff = unified_diff(joystick, before, after)
    if not diff:
        print("No diff generated", file=sys.stderr)
        return 4

    if args.apply:
        joystick.write_text(after)
        print(f"APPLIED {joystick}")
    else:
        print(diff)
        print("PASS_PATCH_PREPARED", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
