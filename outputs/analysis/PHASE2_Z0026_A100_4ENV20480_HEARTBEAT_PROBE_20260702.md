# Phase 2 Z0026 A100 4env/20480 Heartbeat Probe

generated_at: `2026-07-02T05:15:00Z`

## Executive Summary

- `PASS_A100_HEARTBEAT_ARTIFACT_RECOVERY`: the new periodic artifact heartbeat produced recoverable bundles during the remote run.
- `PASS_SMOKE_RUN`: the 4-env/20480-step teacher-continuity probe completed on A100 and exported an ONNX checkpoint.
- `HOLD_PARTIAL_CANDIDATE_CHECKPOINT`: the compact x=0.08 sweep improved forward progress but still held on pitch-chain tracking.

No robot test, SSH, deployment, grounded replay, or runtime behavior change was performed.

## Remote Run

- session: `open-duck-a100-heartbeat`
- workflow: `phase2-z002-teacher-continuity`
- candidate name: `phase2_z0026_teacher_continuity_a100_4env20480_heartbeat_probe`
- remote mode: `foreground-remote`
- remote artifact interval: `120s`
- training envs: `4`
- training timesteps: `20480`
- episode length: `128`
- post-training gates: compact checkpoint sweep only
- exit status: `0`
- artifact bundle sha256: `bad2b950a4f48d0235b0f55d566f4aebbc23b555646dba2ba6f22d46c9768033`
- ONNX: `/content/open_duck_training_phase2_z002_teacher_continuity_cli/smoke_20260702T045858Z_gpu/2026_07_02_050621_20480.onnx`
- ONNX sha256: `2ca86dd002614716a7d8c7061fa6d371dab0f9a4879433156e4e3736652fb5a5`

## Heartbeat Result

The partial bundle became recoverable before final exit and contained:

- `COLAB_CLI_HEARTBEAT.json`
- `COLAB_CLI_EXIT_STATUS.txt`
- the exported ONNX
- checkpoint directory
- training summary
- partial compact-sweep output while x=0.08 was still running

This validates `--remote-artifact-interval-s` as the right mitigation for Colab jobs that disappear before their final sentinel.

## Compact Sweep

The compact CPU sweep evaluated `[0.0, 0.08]` for `1.0s` with the fitted corrected actuator bridge.

| command_x | status | samples | termination | max_pitch_vel_p95 | max_tracking_p95 | track_ratio | mean_local_vx |
|---:|---|---:|---|---:|---:|---:|---:|
| 0.000 | `PASS_CANDIDATE_SIM_GATE` | 50 | `duration_complete` | 1.0858 | 0.1935 | NA | 0.0062 |
| 0.080 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 1.5470 | 0.2194 | 0.3039 | 0.0243 |

Promotion decision:

- status: `HOLD_PARTIAL_CANDIDATE_CHECKPOINT`
- pass count: `1/2`
- failure reason: `command 0.08: HOLD_CANDIDATE_TRACKING`
- max action saturation: `0.0%`
- positive command tracking ratio mean: `0.3039`

## Interpretation

Compared with the smaller 4-env/8192-step foreground probe, the longer 4-env/20480 run improved x=0.08 forward progress from low-progress hold into an interesting in-envelope moving checkpoint:

- x=0.08 track ratio improved from `0.2315` to `0.3039`
- x=0.08 mean local vx improved from `0.0185` to `0.0243`
- max pitch velocity remained safely below the corrected envelope at `1.5470 rad/s`
- tracking p95 remained above the compact gate threshold at `0.2194 rad`

This is not a deployable policy. It is a useful bounded training result and supports another scaled probe, but the next run should keep heartbeat artifacts enabled.

## Next Step

Use the heartbeat artifact path for the next scale test. The clean bracket is now:

- `4 envs / 8192 steps`: completed, low-progress hold
- `4 envs / 20480 steps`: completed, tracking hold with meaningful x=0.08 progress
- `8 envs / 20480 steps`: previously lost sentinel without heartbeat

The next A100 attempt should retry `8 envs / 20480 steps` with `--remote-artifact-interval-s 120` enabled, or run an intermediate `8 envs / 8192 steps` if preserving Colab stability is more important than immediate scale.
