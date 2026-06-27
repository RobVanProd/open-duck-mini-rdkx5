# A100 V19 Reference-Seed Partial Hold Summary

status: `HOLD_REFERENCE_SEED_DEGRADED_PARTIAL`
date: `2026-06-25`
recipe: `movement_bootstrap_v19`
phase: `phase1_reference_imitation_seed_x004`
session: `open-duck-a100`

## Summary

V19 trained phase 1 on the A100 and reached the x=0.04 multi-seed gate with:

```text
dynamics: vanilla
actuator bridge: disabled
command_x: 0.04
gate bridge mode: vanilla
seeds requested: 0-7
reward overrides: phase1_reference_imitation_seed_x004
```

The Colab session was lost before the final artifact bundle could be
downloaded, so this is a partial result. The observed gate results are still
decisive enough to reject V19 as a pass: all six completed seeds failed by
fall/termination, low progress, reverse motion, or collapse.

## Training Evidence

Training reached the final phase-1 export:

```text
final observed ONNX:
  /content/open_duck_staged_curriculum_cli/01_phase1_reference_imitation_seed_x004/smoke_20260625T014233Z_gpu/2026_06_25_015139_337920.onnx
final observed checkpoint:
  2026_06_25_015139_337920
```

Observed PPO reward checkpoints:

| step | reward | reward_std |
|---:|---:|---:|
| 0 | -414.6607 | 286.9659 |
| 112640 | -461.5324 | 296.7176 |
| 225280 | -416.4703 | 298.2595 |
| 337920 | -369.5875 | 285.4691 |

The final ONNX/checkpoint were not recovered because the Colab session dropped
before artifact bundling/download completed.

## Partial Seed Gate

All observed seeds used the V19 reward overrides and vanilla bridge mode.

| seed | status | samples | vx_mean_m_s | track_ratio | base_height_min_m | max_tracking_p95_rad | note |
|---:|---|---:|---:|---:|---:|---:|---|
| 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 70 | -0.0010 | -0.0239 | 0.1535 | 0.0708 | near-zero/reverse, fell |
| 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 34 | -0.0898 | -2.2442 | 0.0924 | 0.2051 | reverse/collapse |
| 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 70 | 0.0077 | 0.1931 | 0.1526 | 0.0801 | low progress, fell |
| 3 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 70 | -0.0161 | -0.4032 | 0.1579 | 0.1106 | reverse, fell |
| 4 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 149 | 0.0080 | 0.1999 | 0.1513 | 0.0485 | low progress, fell |
| 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 46 | -0.3257 | -8.1420 | 0.0585 | 0.1698 | hard reverse/collapse |

Seed 6 was running when the final monitor started; the session was later lost
before a complete result for seeds 6-7 or the final phase summary could be
retrieved.

## Interpretation

V19 does not support `PASS_SEEDED_GAIT_REFINES`.

The reference-imitation reward did not refine into coherent low-command forward
motion. In the observed seed distribution, the policy still fell, reversed, or
collapsed even with:

```text
imitation_scale: 4.0
alive_scale: 0.0
zero_command_probability: 0.0
actuator bridge: disabled
```

This shifts the next offline question from reward-weight tuning to reference
path debugging:

```text
Does the environment/reward actually preserve and reward the upstream reference
trajectory when it is followed, or does the task landscape destroy it?
```

## Limitations

```text
session lost before artifact download
seeds 6-7 not recovered
final ONNX not recovered
final phase_seed_gate.json not recovered
```

Do not send V19 to the robot. Do not run x=0.08. Do not reintroduce the fitted
actuator bridge until low-command forward motion is solved.
