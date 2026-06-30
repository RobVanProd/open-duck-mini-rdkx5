# Phase 2 Z002 Teacher-Prior Manifold Audit

status: `HOLD_TEACHER_PRIOR_NOT_ROBUST`
generated_at: `2026-06-30T06:20:00Z`

## Summary

The z=0.002 teacher-continuity A100 run held on low forward progress. Before
spending another A100 run on stronger teacher-continuity weights, the exact
behavior-prior MLP used by that recipe was evaluated as a standalone ONNX
policy at x=0.08 under the corrected fitted actuator bridge.

Result: the behavior-prior MLP is not a robust walking teacher. It passed only
3/8 seeds over a short 3s fitted-bridge gate, fell on 2/8 seeds, and held on
low forward progress on 3/8 seeds.

## Evaluated Teacher

- ONNX: `outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate/candidate.onnx`
- NPZ: `outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate/candidate_mlp.npz`
- source role: behavior prior for `phase2-z002-teacher-continuity`
- command_x: `0.08`
- duration_s: `3.0`
- bridge: corrected fitted actuator bridge
- seeds: `0-7`

## Result

| seed | status | samples | mean_local_vx | track_ratio | max_tracking_p95 | max_pitch_vel_p95 |
|---:|---|---:|---:|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 150 | 0.0209 | 0.2617 | 0.1946 | 1.6881 |
| 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 33 | 0.0172 | 0.2156 | 0.2753 | 1.2187 |
| 2 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 150 | 0.0076 | 0.0953 | 0.1157 | 0.9884 |
| 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 150 | -0.0092 | -0.1145 | 0.1158 | 0.9090 |
| 4 | `PASS_CANDIDATE_SIM_GATE` | 150 | 0.0238 | 0.2970 | 0.1763 | 1.5844 |
| 5 | `PASS_CANDIDATE_SIM_GATE` | 150 | 0.0294 | 0.3681 | 0.1874 | 1.6658 |
| 6 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 150 | 0.0096 | 0.1202 | 0.1747 | 1.6134 |
| 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 34 | 0.0133 | 0.1660 | 0.3041 | 1.6187 |

Distribution:

- runs: `8`
- falls: `2`
- duration_complete: `6`
- track_ratio_mean: `0.1762`
- vx_mean: `0.0141 m/s`
- max_vel_excess_mean: `0.0000`
- single_support_mean: `29.6845%`
- double_support_mean: `67.8605%`

## Decision

`HOLD_TEACHER_PRIOR_NOT_ROBUST`

The current behavior-prior MLP is a useful weak prior, but not a reliable
teacher-action manifold. The full A100 teacher-continuity hold should not be
answered by simply increasing the same MLP prior scale. The prior itself
contains the low-progress and fall modes we are trying to avoid.

Next aligned work should use the source-VX selector/live-oracle mechanism
directly, or build a stronger teacher dataset from the selector's own
successful corrected-bridge rollouts before another PPO refinement run.

No robot test, SSH, deploy, runtime behavior change, grounded replay, or
candidate promotion was performed.
