# A100 V18 Phase-1 Low-Command Hold Summary

Date: 2026-06-24

Run:

```text
recipe: movement_bootstrap_v18
session: open-duck-a100
gpu: A100
phase: 1 only
training command range: x=0.035-0.045
phase gate command: x=0.04
phase gate bridge: vanilla
phase gate seeds: 0-3
duration: 5 s
robot tests: none
deploy/SSH: none
```

Training completed and exported checkpoints/ONNX files on the remote A100 run.
The selected phase-1 ONNX was evaluated at the same low command used by the
phase-1 discovery recipe.

Gate result:

```text
HOLD_PHASE_MULTI_SEED_FALLS
```

Per-seed summary:

| seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| 0 | HOLD_CANDIDATE_LOW_FORWARD_PROGRESS | 250 | duration_complete | 0.0007 | 0.0165 | 0.0567 | 0.1536 | 0.1212 | 0.0485 |
| 1 | HOLD_CANDIDATE_FALL_OR_TERMINATION | 33 | fall_or_nan | -0.0977 | -2.4426 | 0.0041 | 0.1000 | 0.7654 | 0.2062 |
| 2 | HOLD_CANDIDATE_LOW_FORWARD_PROGRESS | 250 | duration_complete | 0.0023 | 0.0575 | 0.0472 | 0.1526 | 0.1211 | 0.0502 |
| 3 | HOLD_CANDIDATE_LOW_FORWARD_PROGRESS | 250 | duration_complete | -0.0047 | -0.1171 | 0.0732 | 0.1569 | 0.1212 | 0.0548 |

Distribution:

```text
runs: 4
falls: 1
duration_complete: 3
track_ratio_mean: -0.6214
vx_mean: -0.0249 m/s
```

Interpretation:

V18 did not discover coherent low-command forward locomotion. Three seeds
survived the 5 s gate while barely moving or drifting backward; one seed
reversed/collapsed early. This is not an actuator-envelope failure and not an
`x=0.08` target-speed issue. The lowest-command discovery setup still lands in
low-progress/reverse behavior.

Stop rule:

```text
Do not run V18 phase 2.
Do not test V18 at x=0.08.
Do not move to robot validation.
```

Next work:

The next offline step should inspect why PPO is still preferring low/reverse
motion despite dense signed progress and wrong-direction pressure. Treat this as
a reward/objective or task-construction problem before launching another large
training run.

Artifacts:

```text
outputs/analysis/V18_A100_STAGED_PLAN.md
outputs/analysis/v18_a100_staged_plan.json
outputs/analysis/V18_PHASE1_LOW_COMMAND_SEED_GATE.md
outputs/analysis/v18_phase1_low_command_seed_gate.json
```
