# Phase 2 z0.0075 Iter23 Live-Oracle Reset-Settle10 History-Context Rate150 Decision

status: `HOLD_ITER23_LIVE_ORACLE_SEED2_REVERSE`

## Context

Iter22 live-oracle data recovered seed7 but regressed seeds 0 and 6. That
iteration also exposed a tooling mismatch: the live-oracle wrapper collected
student rollouts with reset settle `0`, while the canonical compact gate uses
reset settle `10`.

The wrapper was updated to forward `--reset-settle-ticks`, then iter23 reran the
live-oracle data collection with:

- reset mode: `home-support`
- reset settle ticks: `10`
- task: `rough_terrain_backlash`
- terrain hfield z scale: `0.0075`
- push perturbations: enabled

No robot tests, SSH, deploy, runtime behavior changes, grounded replay, or PPO
training were performed.

## Candidate

- path: `policy/candidates/phase2_z0075_iter23_live_oracle_resetsettle10_history_context_rate150_20260704/candidate.onnx`
- ONNX sha256: `38536ea5c3efcbd207e48743cbde5a0e899978c4726b3cfca001d2e54e449a33`
- NPZ sha256: `fcdfdf832c9b2b834c399949a4fb79f63dfb0af71d69fdf1e2236f7f226ffb31`
- aggregate manifest: `outputs/analysis/live_oracle_dagger_phase_student/iter_023_history_context_resetsettle10/live_oracle_dagger_aggregate_manifest.json`
- aggregate manifest sha256: `b4602b20a53d246a5b95f75a37b68c7020d28c5602a104370504599225c4d467`
- live-oracle run sha256: `549af56cae4ce8d479602b690665609e5a10b356eb44919ac4afff3b6f703644`
- screen JSON sha256: `61b37b17bc38bf7d0bbdea917f86afbe850443d6b3933ecdbc4c3220c13de8bb`
- training status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`
- ONNX max abs fidelity error: `0.00000024`

## Fit Metrics

- samples: `62437`
- MAE: `0.009804`
- p95 abs error: `0.032053`
- target-rate p95: `1.366249 rad/s`
- target-rate max: `9.211689 rad/s`

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
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.4012 | 0.0321 | 0.1719 | 0.1587 | 1.5480 | 0.1827 | 0.0000 |
| 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3544 | 0.0284 | 0.1913 | 0.1561 | 1.5485 | 0.1840 | 0.0000 |
| 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 282 | `fall_or_nan` | -0.5509 | -0.0441 | 0.1832 | 0.0646 | 1.5665 | 0.1771 | 0.0000 |
| 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3311 | 0.0265 | 0.1714 | 0.1577 | 1.5444 | 0.1787 | 0.0000 |
| 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3479 | 0.0278 | 0.1777 | 0.1589 | 1.5429 | 0.1816 | 0.0000 |

## Interpretation

Corrected-settle live-oracle DAgger improved the distribution but did not clear
the compact gate.

Compared with iter22:

- seed0 recovered from fall to pass;
- seed6 recovered from early lunge/fall to pass;
- seed7 remained pass;
- seed2 regressed into reverse/fall.

The remaining seed2 failure again has zero corrected velocity-envelope excess
and tracking p95 below `0.20 rad`, so this is not a corrected actuator-rate
violation. The failure is still a seed-conditioned stability/recovery issue in
the learned deployable map.

## Decision

Do not promote this candidate and do not run x=0.0 or robot validation.

Recommended next step:

- continue live-oracle DAgger with corrected reset settle `10`;
- treat seed2 as the active anti-regression seed;
- avoid returning to static one-off snippet patches unless they are part of the
  live-oracle aggregate loop.
