# Phase 2 z0.0075 Iter22 Live-Oracle History-Context Rate150 Decision

status: `HOLD_LIVE_ORACLE_RECOVERS_SEED7_REGRESSES_0_6`

## Context

This experiment used the first live-oracle DAgger aggregate from the
history-context student:

- rollout policy: `policy/candidates/phase2_z0075_iter21_history_context_rate150_20260704/candidate.onnx`
- teacher manifest: `outputs/analysis/phase2_z0075_iter21_seed67_w2_seed1_plus_seed2_merged_manifest.json`
- aggregate manifest: `outputs/analysis/live_oracle_dagger_phase_student/iter_022_history_context/live_oracle_dagger_aggregate_manifest.json`

The live-oracle iteration collected student-visited traces, relabeled them with
the source-VX selector oracle, added zero-action x=0 relabels, and merged those
with the previous corrected manifest.

Important limitation: the live-oracle wrapper did not yet forward
`reset_settle_ticks`, so the iter22 relabel rollouts were collected with settle
`0`, while the canonical compact gate uses settle `10`. The wrapper has now been
updated to expose and record `--reset-settle-ticks` before the next live-oracle
iteration.

No robot tests, SSH, deploy, runtime behavior changes, grounded replay, or PPO
training were performed.

## Candidate

- path: `policy/candidates/phase2_z0075_iter22_live_oracle_history_context_rate150_20260704/candidate.onnx`
- ONNX sha256: `f76a9db11a99dba8de5c01e2c3fe5c46b461209df449401046839cc3adc3f1e5`
- NPZ sha256: `cd28c90f8a09460fad17c6eda2a933eca7fbf7ab5fb15fa19955ca670c4d4dca`
- aggregate manifest sha256: `f948bbe63d927e55f7db4b13484df160f37bec3e98c2f1dd3bbfe9a6fff1703c`
- screen JSON sha256: `59f7723ee7eabfa4bdc8e34ee585ccc525de67cd5f1298f6c18f21d3e2a0182c`
- training status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`
- ONNX max abs fidelity error: `0.00000024`

## Fit Metrics

- samples: `57928`
- MAE: `0.009129`
- p95 abs error: `0.030975`
- target-rate p95: `1.378188 rad/s`
- target-rate max: `10.117901 rad/s`

## Compact Screen

Corrected-bridge screen:

- command: `x=0.08`
- task: `rough_terrain_backlash`
- terrain hfield z scale: `0.0075`
- bridge: `fitted`
- reset: `home-support`, settle `10` ticks
- pushes: enabled, `0.075-0.125`, interval `1.0-1.5 s`
- seeds: `0,1,2,6,7`

| seed | status | samples | termination | track_ratio | mean_local_vx | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 | max_vel_excess |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 639 | `fall_or_nan` | 0.0197 | 0.0016 | 0.1838 | 0.0706 | 1.5874 | 0.1854 | 0.0000 |
| 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3979 | 0.0318 | 0.2211 | 0.1580 | 1.5819 | 0.1919 | 0.0000 |
| 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.4087 | 0.0327 | 0.1792 | 0.1585 | 1.5826 | 0.1833 | 0.0000 |
| 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 120 | `fall_or_nan` | 2.0231 | 0.1618 | 0.9614 | 0.0116 | 1.5453 | 0.1982 | 0.0000 |
| 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3726 | 0.0298 | 0.1652 | 0.1589 | 1.5927 | 0.1821 | 0.0000 |

## Interpretation

Live-oracle aggregation changed the distribution but did not solve it. It
recovered the previously failing seed7, but regressed seed0 into low-progress
fall and seed6 into early lunge/fall. All rows still have zero corrected
velocity-envelope excess, so this remains a stability/data-distribution problem,
not an actuator-rate violation.

The iter22 data collection also exposed a tooling mismatch: relabel rollouts
used reset settle `0`, while the canonical compact gate used reset settle `10`.
That mismatch is now fixed in `tools/run_live_oracle_dagger_iteration.py`.

## Decision

Do not promote this candidate and do not run x=0.0 or robot validation.

Recommended next step:

- rerun live-oracle DAgger collection with `--reset-settle-ticks 10`;
- train the same deployable history-context student on that corrected aggregate;
- gate again on sensitive seeds `0,1,2,6,7`.
