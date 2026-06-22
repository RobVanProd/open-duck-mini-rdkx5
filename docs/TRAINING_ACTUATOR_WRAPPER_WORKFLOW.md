# Training Actuator Wrapper Workflow

Last updated: 2026-06-22

## Purpose

The CUDA L4 closed-loop eval returned `PASS_CLOSED_LOOP_REPRODUCTION`: the
fitted actuator bridge makes `BEST_WALK_ONNX_2` degrade in sim in the same
range as the real suspended `x=0.08` replay.

The next step is to add the same actuator model to the Open Duck Playground
training environment so a new policy learns trackable target dynamics.

This is still offline-only work:

- no robot motion
- no deployment
- no runtime behavior changes
- no policy overwrite
- no grounded replay

## Insertion Point

The target-stage insertion point in
`Open_Duck_Playground/playground/open_duck_mini_v2/joystick.py` is:

```text
action delay
target = home + delayed_action * action_scale
max_motor_velocity rate limit
actuator bridge
mjx_env.step(...)
```

The wrapper must keep `state.info["motor_targets"]` as the commanded/sent
target, not the lagged physical target. This preserves the deployed policy
observation contract for obs `83:97` while the simulated joint state reflects
lagged actuator dynamics.

## Patch Tool

Prepare the default-off patch:

```bash
python3 tools/prepare_training_actuator_wrapper_patch.py \
  --playground-path ../Open_Duck_Playground
```

Apply it only when ready to modify the sibling Playground checkout:

```bash
python3 tools/prepare_training_actuator_wrapper_patch.py \
  --playground-path ../Open_Duck_Playground \
  --apply
```

Default behavior prints a unified diff and does not edit the Playground repo.

## Patch Contents

The prepared patch adds a default-off config block:

```text
actuator_bridge.enable = False
delay_min_ticks = 3
delay_max_ticks = 8
tau_min_s = 0.06
tau_max_s = 0.14
velocity_limit_min_rad_s = 2.5
velocity_limit_max_rad_s = 4.7
per_joint_variation = 0.15
```

It also adds two optional reward/cost terms with zero default scale:

```text
target_rate = 0.0
actuator_tracking = 0.0
```

These are intentionally disabled by default so existing training behavior is
unchanged unless config overrides enable the bridge and assign nonzero costs.

## Validation After Applying

Use a CUDA backend first because the local `7900 XTX` ROCm/MJX path is still
blocked at `HOLD_PLAYGROUND_GPU_STEP`.

Minimum checks:

```bash
python -m py_compile \
  ../Open_Duck_Playground/playground/open_duck_mini_v2/joystick.py

python tools/audit_policy_sim_contract.py \
  --policy policy/BEST_WALK_ONNX_2.onnx \
  --playground-path ../Open_Duck_Playground \
  --env-python "$(command -v python)" \
  --instantiate-timeout-s 600
```

Then run a short closed-loop eval with the bridge enabled in Playground config
before starting any training job. The first training PR should add a small
smoke-training command with:

```text
num_timesteps: small smoke value
command curriculum: x = 0.00 -> 0.04 -> 0.08
target velocity metrics
action-rate metrics
simulated actuator tracking metrics
```

Minimum enabled-bridge smoke check:

```bash
cd ../Open_Duck_Playground
JAX_PLATFORM_NAME=cpu ../envs/open-duck-playground/bin/python - <<'PY'
import jax
import jax.numpy as jp
from playground.open_duck_mini_v2 import joystick

cfg = joystick.default_config()
cfg.actuator_bridge.enable = True
cfg.push_config.enable = False
cfg.noise_config.action_min_delay = 0
cfg.noise_config.action_max_delay = 1

env = joystick.Joystick(config=cfg)
state = env.reset(jax.random.PRNGKey(0))
state = env.step(state, jp.zeros(env.action_size))
print(state.obs["state"].shape, state.info["actuator_bridge_applied_targets"].shape)
PY
```

This catches regressions where the wrapper tries to assign fields on the frozen
MJX `State` dataclass instead of updating the existing `info` dictionary.

## Acceptance Gate

Proceed toward training only when:

- the patched Playground contract remains `state[101] -> action[14]`
- actuator order still matches `BEST_WALK_ONNX_2`
- the bridge is disabled by default
- enabling the bridge reproduces the fitted/stress behavior seen in CUDA eval
- no robot behavior has changed

Do not run robot validation until a candidate ONNX is trained, exported under a
new filename, and passes suspended `x=0.0` and `x=0.08` validation.
