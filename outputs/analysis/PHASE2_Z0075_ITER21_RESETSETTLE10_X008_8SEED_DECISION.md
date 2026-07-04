# Phase 2 z0.0075 Iter21 Reset-Settle10 x0.08 8-Seed Decision

status: `HOLD_INTERMEDIATE_PUSH_ROBUSTNESS`

Offline-only gate and failure-surface analysis. No robot tests, SSH, deploy,
grounded replay, runtime behavior change, policy edit, or training was
performed.

## Candidate

- candidate: `policy/candidates/phase2_z0075_iter21_early_lunge_gain095_rate150_20260704/candidate.onnx`
- candidate_sha256: `72aa93c2ab249d2e9b22bb5415ef6c96c7407833fbfd21233892b6daa6afda14`
- corrected_bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- corrected_bridge_sha256: `3661543d0745073b561eb4fa2ae8f9616368ee8b72cb397f8b953dada532c8c0`
- reset_mode: `home-support`
- reset_settle_ticks: `10`

## Gate

- task: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.0075`
- command_x: `0.08`
- bridge_mode: `fitted`
- policy_action_gain: `1.0`
- duration_s: `15.0`
- seeds: `0-7`
- push: enabled
- push_interval_s: `1.0-1.5`
- push_magnitude: `0.075-0.125`
- jax_platform: `cpu`

## Result

The full x=0.08 rough/intermediate-push gate does not pass.

| seed | status | samples | termination | track_ratio | max_vel_excess | base_height_min | push_success |
|---:|---|---:|---|---:|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3391 | 0.0000 | 0.1593 | 11/12 |
| 1 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.3964 | 0.0583 | 0.1576 | 12/13 |
| 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3225 | 0.0000 | 0.1589 | 12/13 |
| 3 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.3514 | 0.0097 | 0.1587 | 12/13 |
| 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3014 | 0.0000 | 0.1593 | 11/12 |
| 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 599 | `fall_or_nan` | -0.0672 | 0.0000 | 0.0630 | 9/10 |
| 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3567 | 0.0000 | 0.1588 | 12/13 |
| 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3886 | 0.0000 | 0.1593 | 9/10 |

Distribution:

- pass: `5/8`
- target-velocity hold: `2/8`
- fall/termination hold: `1/8`
- mean track_ratio: `0.2986`
- mean max_vel_excess: `0.0085 rad/s`
- mean push_success: `0.9157`

## Failure Trace Findings

Seeds `1`, `3`, and `5` were rerun with tick-level trace enabled under the same
gate settings.

### Seed 1

- status: `HOLD_CANDIDATE_TARGET_VELOCITY`
- violation: one tick
- tick: `281`
- time_s: `5.62`
- joint: `right_ankle`
- velocity: `-2.0583 rad/s`
- corrected_limit: `2.0000 rad/s`
- excess: `0.0583 rad/s`
- push active on tick: `False`
- p95 velocity excess: `0.0000`

### Seed 3

- status: `HOLD_CANDIDATE_TARGET_VELOCITY`
- violation: one tick
- tick: `150`
- time_s: `3.00`
- joint: `right_ankle`
- velocity: `-2.0097 rad/s`
- corrected_limit: `2.0000 rad/s`
- excess: `0.0097 rad/s`
- push active on tick: `False`
- p95 velocity excess: `0.0000`

### Seed 5

- status: `HOLD_CANDIDATE_FALL_OR_TERMINATION`
- no corrected-envelope target velocity excess
- fall sample: `599`
- last push start before collapse: tick `549`, time `10.98s`
- collapse: tick `598`, time `11.96s`
- final base_height_m: `0.0630`
- final body_pitch_rad: `-1.4099`
- final local_vx_m_s: `-1.5263`

## No-Push Control

Seed `5` was rerun with identical rough terrain, corrected bridge, command, and
reset-settle settings, but with push perturbations disabled.

- status: `PASS_CANDIDATE_SIM_GATE`
- samples: `750`
- termination: `duration_complete`
- track_ratio: `0.3617`
- max target velocity excess: `0.0000`
- max pitch tracking p95: `0.1810`
- base_height_min: `0.1593`

The no-push control confirms that the seed-5 failure is push-induced, not a
base rough-terrain gait failure.

## Interpretation

- `reset_settle_ticks=10` remains useful and removes the focused startup
  left-hip-pitch spike without destabilizing most seeds.
- The candidate is not Phase-2 promotable yet because the full x=0.08
  rough/intermediate-push gate is `5/8` pass.
- The remaining target-rate holds are single-tick right-ankle max violations,
  with clean p95 velocity. They are small but still violate the strict corrected
  per-joint envelope gate.
- The material robustness blocker is seed-5 push recovery: the same seed passes
  rough terrain without pushes and falls only under the intermediate push
  schedule.

## Next Decision

Do not run robot validation. Do not promote the candidate.

Next offline work should target push recovery while preserving the current
rough-terrain/no-push gait:

1. Use the seed-5 push-failure trace around ticks `549-598` to curate or train a
   push-recovery intervention.
2. Preserve the right-ankle envelope by keeping the corrected per-joint limit
   hard in the gate.
3. Re-run the same x=0.08 rough/intermediate-push 8-seed gate with
   `reset_settle_ticks=10`.
4. Only after x=0.08 passes, run the x=0.0 command-semantics gate with the same
   reset convention.
