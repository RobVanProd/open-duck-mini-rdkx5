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

## Playground Patch

The actual training-environment patch is preserved in the RobVanProd fork:

```text
repo: https://github.com/RobVanProd/Open_Duck_Playground
PR: https://github.com/RobVanProd/Open_Duck_Playground/pull/1
branch: codex/training-actuator-bridge
```

That PR adds:

- default-off actuator bridge in `playground/open_duck_mini_v2/joystick.py`
- runner flags to enable/tune the bridge
- PPO override flags for small smoke-training runs

The original upstream remains:

```text
https://github.com/apirrone/Open_Duck_Playground
```

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

The Playground runner PR adds these relevant flags:

```text
--enable_actuator_bridge
--actuator_bridge_delay_min_ticks
--actuator_bridge_delay_max_ticks
--actuator_bridge_tau_min_s
--actuator_bridge_tau_max_s
--actuator_bridge_velocity_limit_min_rad_s
--actuator_bridge_velocity_limit_max_rad_s
--actuator_bridge_per_joint_variation
--target_rate_scale
--actuator_tracking_scale
--ppo_num_envs
--ppo_num_evals
--ppo_episode_length
--ppo_unroll_length
--ppo_batch_size
--ppo_num_minibatches
--ppo_num_updates_per_batch
```

It also adds always-on scalar diagnostics:

```text
diagnostic/target_velocity_cost
diagnostic/actuator_bridge_tracking_cost
diagnostic/actuator_bridge_delay_ticks
diagnostic/actuator_bridge_tau_mean_s
diagnostic/actuator_bridge_velocity_limit_mean_rad_s
```

These are diagnostics, not reward terms. Reward scales remain default `0.0`
unless explicitly changed.

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
cd /home/lsd/robots/open-duck-mini-rdkx5
JAX_PLATFORM_NAME=cpu ../envs/open-duck-playground/bin/python \
  tools/smoke_actuator_bridge_wrapper.py \
  --playground-path ../Open_Duck_Playground \
  --platform cpu \
  --steps 10
```

This catches regressions where the wrapper tries to assign fields on the frozen
MJX `State` dataclass instead of updating the existing `info` dictionary.

Current local result:

```text
status: PASS_ACTUATOR_BRIDGE_SMOKE
steps: 10
platform: cpu
obs_state_shape: [101]
obs_privileged_shape: [212]
action_size: 14
applied_targets_shape: [14]
max_target_velocity_cost: 1.4459760189056396
max_actuator_bridge_tracking_cost: 0.002514034043997526
```

## Tiny PPO Smoke

A tiny CPU PPO smoke run was executed against the patched Playground branch.
This is not a candidate policy; it only proves the patched training loop can
start, export, and reach a finite eval callback with the bridge enabled.

Use the RDK helper to print the exact command first:

```bash
cd /home/lsd/robots/open-duck-mini-rdkx5
python3 tools/run_actuator_bridge_training_smoke.py
```

Run the tiny smoke only after the printed command is reviewed:

```bash
python3 tools/run_actuator_bridge_training_smoke.py --run
```

The helper defaults to:

```text
platform: cpu
output root: /tmp/open_duck_actuator_bridge_smoke
actuator bridge: enabled
target_rate_scale: 0.0
actuator_tracking_scale: 0.0
```

It writes `smoke_manifest.start.json`, `stdout.txt`, `stderr.txt`, and
`smoke_manifest.final.json` under `/tmp`. These are smoke artifacts, not
deployable policy outputs.

Summarize a smoke or training output directory with:

```bash
python3 tools/summarize_training_run.py \
  /tmp/open_duck_actuator_bridge_smoke/smoke_20260622T054611Z_cpu \
  --output-md /tmp/open_duck_training_run_smoke_summary.md \
  --output-json /tmp/open_duck_training_run_smoke_summary.json
```

For the tiny CPU smoke run, this produced:

```text
status: INFO_NON_DEPLOYABLE_TRAINING_RUN
latest_onnx_step: 80
latest_onnx_sha256: 22dd18a33ea5fadd98a2f94bc43205b5b71b6bbc37968cd49ae632eea23498ee
reward: 11.377256
reward_std: 4.541440
```

The launcher was validated with a smaller CPU run:

```bash
python3 tools/run_actuator_bridge_training_smoke.py \
  --run \
  --num-timesteps 64 \
  --ppo-num-envs 8 \
  --ppo-batch-size 8 \
  --ppo-episode-length 50 \
  --ppo-unroll-length 5 \
  --timeout-s 900
```

Result:

```text
status: PASS_SMOKE_RUN
step: 80
reward: 11.377256393432617
reward_std: 4.541440010070801
checkpoints:
  /tmp/open_duck_actuator_bridge_smoke/smoke_20260622T054611Z_cpu/..._0
  /tmp/open_duck_actuator_bridge_smoke/smoke_20260622T054611Z_cpu/..._80
```

The exported smoke ONNX was also run through the candidate package helper with
an explicit non-deployable label:

```bash
python3 tools/package_candidate_policy.py \
  /tmp/open_duck_actuator_bridge_smoke/smoke_20260622T054611Z_cpu/2026_06_22_014652_80.onnx \
  --candidate-name smoke_not_deployable \
  --training-manifest /tmp/open_duck_actuator_bridge_smoke/smoke_20260622T054611Z_cpu/smoke_manifest.final.json \
  --output-md /tmp/open_duck_candidate_package_smoke.md \
  --output-json /tmp/open_duck_candidate_package_smoke.json \
  --allow-missing-evidence \
  --non-deployable-reason "Tiny CPU smoke artifact only; not a deployable robot policy."
```

Result:

```text
status: INFO_NON_DEPLOYABLE_ARTIFACT
contract: PASS_POLICY_CONTRACT
input_dim: 101
output_dim: 14
```

Command shape:

```bash
cd /home/lsd/robots/Open_Duck_Playground
JAX_PLATFORM_NAME=cpu timeout 900s ../envs/open-duck-playground/bin/python \
  playground/open_duck_mini_v2/runner.py \
  --task flat_terrain \
  --env joystick \
  --output_dir /tmp/open_duck_ppo_bridge_smoke \
  --num_timesteps 256 \
  --enable_actuator_bridge \
  --ppo_num_envs 16 \
  --ppo_num_evals 1 \
  --ppo_episode_length 100 \
  --ppo_unroll_length 5 \
  --ppo_batch_size 16 \
  --ppo_num_minibatches 1 \
  --ppo_num_updates_per_batch 1 \
  --target_rate_scale 0.0 \
  --actuator_tracking_scale 0.0
```

Result:

```text
PPO params reflect the small overrides.
Checkpoint/export at step 0 completed.
Checkpoint/export at step 320 completed.
STEP: 320 reward: 15.308966636657715 reward_std: 9.823185920715332
```

Artifacts were written only to:

```text
/tmp/open_duck_ppo_bridge_smoke
```

Do not treat those exported ONNX files as deployable policies.

## Acceptance Gate

Proceed toward training only when:

- the patched Playground contract remains `state[101] -> action[14]`
- actuator order still matches `BEST_WALK_ONNX_2`
- the bridge is disabled by default
- enabling the bridge reproduces the fitted/stress behavior seen in CUDA eval
- no robot behavior has changed

Do not run robot validation until a candidate ONNX is trained, exported under a
new filename, and passes suspended `x=0.0` and `x=0.08` validation.
