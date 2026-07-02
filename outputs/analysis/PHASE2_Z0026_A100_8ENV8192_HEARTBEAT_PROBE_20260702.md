# Phase 2 Z0026 A100 8env/8192 Heartbeat Probe

generated_at: `2026-07-02T05:40:00Z`

## Executive Summary

- `PASS_A100_HEARTBEAT_ARTIFACT_RECOVERY`: the periodic heartbeat artifact path worked for another A100 run.
- `PASS_SMOKE_RUN`: the 8-env/8192-step teacher-continuity probe completed and exported an ONNX checkpoint.
- `HOLD_PARTIAL_CANDIDATE_CHECKPOINT`: the checkpoint regressed to low x=0.08 progress and is not promotable.

No robot test, SSH, deployment, grounded replay, or runtime behavior change was performed.

## Remote Run

- session: `open-duck-a100-heartbeat`
- workflow: `phase2-z002-teacher-continuity`
- candidate name: `phase2_z0026_teacher_continuity_a100_8env8192_heartbeat_probe`
- remote mode: `foreground-remote`
- remote artifact interval: `120s`
- training envs: `8`
- training timesteps requested: `8192`
- exported step: `8960`
- episode length: `128`
- post-training gates: compact checkpoint sweep only
- exit status: `0`
- artifact bundle sha256: `72ec2135b101ad94c9e76c747b78177bd4f4b177c5e1530ae3f8934fde27964e`
- ONNX: `/content/open_duck_training_phase2_z002_teacher_continuity_cli/smoke_20260702T052444Z_gpu/2026_07_02_053037_8960.onnx`
- ONNX sha256: `343342e5135ae12534ee8fde33e6d22e6b90bbe49dce2e3ef202f8ca71412b4a`

## Compact Sweep

The compact CPU sweep evaluated `[0.0, 0.08]` for `1.0s` with the fitted corrected actuator bridge.

| command_x | status | samples | termination | max_pitch_vel_p95 | max_tracking_p95 | track_ratio | mean_local_vx |
|---:|---|---:|---|---:|---:|---:|---:|
| 0.000 | `PASS_CANDIDATE_SIM_GATE` | 50 | `duration_complete` | 1.0658 | 0.1941 | NA | 0.0058 |
| 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | 1.5208 | 0.2197 | 0.2088 | 0.0167 |

Promotion decision:

- status: `HOLD_PARTIAL_CANDIDATE_CHECKPOINT`
- pass count: `1/2`
- failure reasons:
  - `command 0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`
  - `command 0.08: track ratio 0.2088 < 0.2500`
  - `command 0.08: mean vx 0.0167 < 0.0200`
- max action saturation: `0.0%`

## Interpretation

This run isolates env-count scaling against the successful heartbeat transport path. Increasing from 4 envs to 8 envs at the shorter timestep budget did not improve the candidate. It regressed below the 4-env/8192 and 4-env/20480 compact x=0.08 progress metrics.

Current compact probe ordering:

| probe | x=0.08 status | track_ratio | mean_vx | tracking_p95 |
|---|---|---:|---:|---:|
| 4env/8192 foreground | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.2315 | 0.0185 | 0.2174 |
| 4env/20480 heartbeat | `HOLD_CANDIDATE_TRACKING` | 0.3039 | 0.0243 | 0.2194 |
| 8env/8192 heartbeat | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.2088 | 0.0167 | 0.2197 |

The 4env/20480 checkpoint is the most interesting of these bounded probes, but still not promotable. The common tracking plateau around `0.217-0.220 rad` remains.

## Next Step

Do not promote this checkpoint. Before retrying a larger 8env/20480 run, decide whether the objective should keep pushing this teacher-continuity recipe or pivot back to the registered live-oracle DAgger/phase-memory branch, because all three bounded PPO probes still sit at the same corrected-bridge tracking plateau.
