# Support-Transition Recovery Fine-Tune Plan

Purpose: define the next offline PPO fine-tune only after the deployable
warm-start work showed a stable but still poorly tracked fitted-bridge gait.
This is a planning artifact, not a robot approval.

## Current Evidence

The best current deployable warm start remains the command-conditioned,
pitch-rate-limited swish PPO checkpoint:

```text
checkpoint: outputs/analysis/ppo_bc_swish_cmd_pitch_rl_2p25_step0_checkpoint
onnx: outputs/analysis/ppo_bc_swish_cmd_pitch_rl_2p25_step0.onnx
```

Its step-0 gates:

```text
x=0.0 fitted bridge:
  duration complete: 8 / 8
  mean max tracking p95: 0.0740 rad

x=0.08 fitted bridge:
  duration complete: 8 / 8
  mean vx: 0.0347 m/s
  mean track ratio: 0.4343
  mean max pitch target velocity p95: 2.1196 rad/s
  mean max pitch tracking p95: 0.1958 rad
```

That checkpoint is useful because it already separates the two core behaviors:

```text
x=0.0: stable stand
x=0.08: low but coherent in-envelope forward motion
```

It is not robot-ready because fitted actuator tracking is still too poor.

The later DAgger-7 PPO-loc checkpoint is useful restore/export evidence, but it
is a worse fine-tune anchor right now:

```text
checkpoint: outputs/analysis/ppo_loc_dagger7_targeted_recovery_step0_checkpoint
x=0.08 fitted bridge: falls on seeds 1 and 7
```

Use it only for targeted hard-seed research, not as the default PPO fine-tune
anchor.

## Why Not Another Scalar PPO Sweep

Three A100 fine-tunes from the command-conditioned warm start already showed the
failure mode:

```text
standard fine-tune: stable standstill at x=0.08
conservative fine-tune: stable standstill at x=0.08
weak behavior-prior fine-tune: stable standstill at x=0.08
```

Those runs improved stability/tracking by erasing forward motion. The next run
must therefore include explicit support-transition and forward-preservation
pressure. Do not launch another run that only tweaks learning rate, PPO clip,
or target-rate scale.

## Proposed First Smoke

Artifact:

```text
outputs/analysis/support_transition_recovery_finetune/dry_run_manifest.json
```

Status:

```text
DRY_RUN_REVIEWED_AND_TINY_SMOKE_RUN
robot_touched: false
deploy_performed: false
```

The dry-run command restores the command-conditioned pitch-rate-limited PPO
checkpoint, keeps the fitted actuator bridge active, samples only straight
commands in `x=[0.0, 0.08]`, and adds support-transition pressure:

```text
forward_progress_scale: 6
forward_shortfall_scale: -3
forward_wrong_direction_scale: -2
forward_overshoot_scale: -0.5
base_height_scale: -0.5
forward_pitch_scale: -0.3
forward_pitch_rate_scale: -0.1
forward_contact_support_scale: -0.1
forward_single_support_scale: 0.1
forward_double_support_scale: -0.05
forward_contact_transition_scale: 0.1
forward_double_support_dwell_scale: -0.02
target_rate_scale: -0.0005
actuator_tracking_scale: -0.005
```

Sign convention:

```text
cost terms use negative scale
reward terms use positive scale
```

This smoke is intentionally small (`1024` timesteps, CPU dry-run target). It is
meant to verify that restore, reward wiring, and export are coherent before any
long CUDA/A100 job.

## Tiny Smoke Result

The reviewed tiny CPU smoke was run after this plan was created:

```text
decision: outputs/analysis/SUPPORT_TRANSITION_RECOVERY_FINETUNE_SMOKE_RESULT.md
final manifest: outputs/analysis/support_transition_recovery_finetune/final_manifest.json
x=0.0 gate: outputs/analysis/SUPPORT_TRANSITION_RECOVERY_FINETUNE_X0_FITTED_15S.md
baseline control: outputs/analysis/CMD_PITCH_RL_2P25_STEP0_FLAT_X0_FITTED_15S.md
canonical x=0 hard seeds: outputs/analysis/SUPPORT_TRANSITION_RECOVERY_FINETUNE_BACKLASH_X0_FITTED_15S_HARD_SEEDS.md
canonical x=0.08 full seeds: outputs/analysis/SUPPORT_TRANSITION_RECOVERY_FINETUNE_BACKLASH_X008_FITTED_15S.md
status: HOLD_X008_LOW_PROGRESS_AND_ONE_FALL
```

The restore/export path worked. Under the non-canonical `flat_terrain` stress
model, the first x=0 gate failed:

```text
x=0.0 fitted bridge, 15 s, seeds 0-7
falls: seeds 1 and 7
duration complete: 6 / 8
```

The original step-0 warm start was rerun under the same `flat_terrain`,
15-second x=0 gate and failed on the same seeds. This means the smoke did not
create a new zero-command failure.

After the canonical model decision, the same smoke was checked on
`flat_terrain_backlash`:

```text
x=0.0 fitted bridge, 15 s, hard seeds 1 and 7:
  duration complete: 2 / 2
  max_tracking_p95: 0.0552-0.0555 rad

x=0.08 fitted bridge, 15 s, seeds 0-7:
  duration complete: 7 / 8
  fall/termination: seed 3 at 78 samples
  mean vx: -0.0284 m/s
  mean track ratio: -0.3549
```

Interpretation: the tiny smoke preserves canonical x=0 hard-seed standing, but
it does not produce usable forward motion. It mostly under-drives x=0.08 and
still has one unstable/reverse seed. Do not scale this exact reward mix to
A100.

## Required Gates After Any Run

Do not inspect reward alone. A run is useful only if it is followed by the
standard fitted-bridge gates:

```bash
../envs/open-duck-playground/bin/python tools/run_candidate_seed_sweep.py \
  --run \
  --policies candidate=<exported_onnx> \
  --seeds 0-7 \
  --fit-json outputs/analysis/actuator_response_fit.json \
  --playground-path ../Open_Duck_Playground \
  --env-python ../envs/open-duck-playground/bin/python \
  --command-x 0.0 \
  --task flat_terrain_backlash \
  --duration 15 \
  --bridge-mode fitted \
  --jax-platform cpu \
  --output-dir outputs/analysis/<run>_x0_fitted_15s \
  --output-md outputs/analysis/<RUN>_X0_FITTED_15S.md \
  --output-json outputs/analysis/<run>_x0_fitted_15s.json
```

Then repeat with:

```text
--command-x 0.08
```

## Stop Rules

Hold and do not continue the same recipe if any are true:

```text
x=0.0 falls on any seed
x=0.08 falls on any seed
x=0.08 mean track ratio falls below the step-0 baseline of 0.4343
x=0.08 mean vx falls below the step-0 baseline of 0.0347 m/s
x=0.08 max pitch tracking p95 does not improve meaningfully from 0.1958 rad
target velocity p95 rises above the fitted envelope while tracking does not improve
```

If the smoke erases forward motion again, the conclusion is:

```text
HOLD_SCALAR_PPO_RECOVERY_STILL_ERASES_MOTION
```

Then pivot to a stronger behavior objective or a larger on-distribution
selector-generated dataset before more PPO.

## Robot Boundary

This plan does not authorize:

```text
robot test
SSH/deploy
runtime behavior change
duck_config.json edit
policy overwrite
grounded replay
```

Robot work remains blocked until a candidate passes offline x=0.0 and x=0.08
fitted-bridge gates and the physical start-pose gate remains clean.
