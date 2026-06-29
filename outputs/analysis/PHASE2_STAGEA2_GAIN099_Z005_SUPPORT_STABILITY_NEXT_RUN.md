# Phase 2 z=0.005 Support-Stability Next Run

status: `PASS_Z005_SUPPORT_STABILITY_RECIPE_CPU_PLUMBING`

## Scope

This is an offline CPU training-plumbing check and next-run specification. It
did not produce a promotable policy. No robot tests, SSH, deploy, grounded
replay, runtime behavior changes, or policy overwrite were performed.

## Why This Run

The packaged gain-0.99 candidate is the current best reviewed offline Phase 2
sim candidate at rough `z=0.002`, including gentle pushes:

```text
candidate:
  policy/candidates/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/candidate.onnx

candidate_sha256:
  209b85a75cf9cbbcf10df573c1b530921943a72e81082111889c15f63a9a2c7b

z=0.002:
  x=0.08 no-push:      PASS 8/8
  x=0.0 no-push:       PASS 8/8
  x=0.08 gentle-push:  PASS 8/8
  x=0.0 gentle-push:   PASS 8/8
```

At rough `z=0.005`, it holds on seed 5:

```text
artifact:
  outputs/analysis/PHASE2_STAGEA2_GAIN099_Z005_SEED5_TRACE_ANALYSIS.md

failure:
  seed 5 fall at 56 samples
  double support: 91.1%
  single support: 7.1%
  body pitch min: -1.4489 rad
  last local vx: -1.4738 m/s
  max pitch-chain tracking p95: 0.1533 rad
  corrected envelope excess: 0.0000 rad/s
```

The next training target is therefore support timing and backward-pitch
stability on rougher terrain, not actuator-envelope relaxation.

## Trainable Starting Point

The packaged gain-0.99 candidate is a deployable ONNX graph composition, not an
Orbax checkpoint that PPO can restore directly. Use it as the gate baseline, but
use the closest trainable Stage A2 checkpoint as the PPO restore source:

```text
restore_checkpoint_path:
  outputs/phase2_domain_randomization/stage_a2_preserve_narrow_flat_no_push_gpu/smoke_20260628T031553Z_gpu/2026_06_27_232221_491520
```

## CPU Plumbing Check

The exact recipe wiring was validated with a tiny CPU run:

```text
status: PASS_SMOKE_RUN
output_dir: /tmp/open_duck_phase2_z005_support_smoke/smoke_20260629T161022Z_cpu
elapsed_s: 85.08
PPO step: 20
reward: 1.8584
export_min_step: 1
saved_checkpoint:
  /tmp/open_duck_phase2_z005_support_smoke/smoke_20260629T161022Z_cpu/2026_06_29_121116_20
```

The terrain XML was restored after the temporary `z=0.005` patch:

```text
scene_rough_terrain_backlash.xml sha256 before:
  879768817f5ae5d2c01b5494f855686bb10d1ec444a404efeced8f5766574ffc

patched:
  cc97b6de11d8362ecb54b18126f3b7ea2cbf0c850e42b967f7b977a74d8ab28e

restored:
  879768817f5ae5d2c01b5494f855686bb10d1ec444a404efeced8f5766574ffc
```

## Recommended Policy-Producing Run

Run this only on a stable GPU path, preferably the pinned CUDA/A100 workflow or
another verified GPU session. Local ROCm full-shape evaluator reset remains
unreliable and should not be used for policy-producing runs until fixed.

Core settings:

```text
task: rough_terrain_backlash
terrain_hfield_z_scale: 0.005
restore_policy_kl_scale: 3.0
ppo_learning_rate: 0.000003
ppo_clipping_epsilon: 0.02
ppo_max_grad_norm: 0.1
num_timesteps: 81920
ppo_num_envs: 64
ppo_num_evals: 4
ppo_episode_length: 750
```

Corrected actuator bridge training range:

```text
delay_ticks: 3
tau_s: 0.06-0.14
velocity_limit_rad_s: 2.0-3.25
per_joint_variation: 0.10
```

Reward/regularization focus:

```text
preserve forward motion:
  tracking_lin_vel_scale: 3
  tracking_sigma: 0.01
  forward_progress_scale: 2.5
  command_progress_scale: 1.5
  command_progress_shortfall_scale: -4
  command_progress_required_ratio: 0.45

prevent seed-5 reversal/collapse:
  forward_wrong_direction_scale: -3.0
  forward_wrong_direction_allowed_reverse_ratio: 0.05
  base_height_scale: -0.45
  forward_pitch_scale: -0.10
  forward_pitch_rate_scale: -0.010

support timing:
  forward_single_support_scale: 0.20
  forward_double_support_scale: -0.35
  forward_double_support_dwell_scale: -1.0
  forward_double_support_dwell_grace_steps: 8

step margin:
  forward_swing_advance_scale: -0.002
  forward_swing_advance_target_m: 0.004
  forward_swing_clearance_scale: -0.0005
  forward_swing_clearance_target_m: 0.018
```

Keep randomization narrow for this rung:

```text
friction: 0.98-1.02
mass scale: 0.995-1.005
COM jitter: 0.002 m
qpos jitter: 0.002 rad
actuator gain scale: 0.995-1.005
leg geometry jitter: 0.001
pushes: disabled
```

## Promotion Gate

A trained checkpoint from this recipe is promotable only if it passes:

```text
x=0.08, rough z=0.005, no push:
  8/8 seeds
  15 s
  no falls
  corrected velocity excess: 0.0000 rad/s
  max pitch-chain tracking p95 <= 0.20 rad

x=0.0, rough z=0.005, no push:
  8/8 seeds
  15 s
  no falls
  mean |vx| <= 0.005 m/s
```

It must also retain the already-reviewed `z=0.002` gates:

```text
x=0.08 no-push
x=0.0 no-push
x=0.08 gentle-push
x=0.0 gentle-push
```

The CPU plumbing pass is not a policy result and is not robot approval.
