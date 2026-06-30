# Phase 2 Z002 Teacher Continuity Full A100 Result

status: `HOLD_LOW_FORWARD_PROGRESS`
generated_at: `2026-06-30T05:55:00Z`

## Summary

The fresh `open-duck-a100-phase2-full` Colab A100 session successfully ran
the Phase 2 Z002 teacher-continuity workflow with the pinned CUDA stack:
JAX/JAXLIB `0.7.2`, Brax `0.14.2`, MuJoCo/MJX `3.9.0`, and CUDA GPU
backend.

Training completed and exported three ONNX checkpoints. The remote CPU
checkpoint sweep stalled, so the artifact bundle was recovered and the same
compact sweep was run locally. The result is a clean hold: checkpoints remain
below the corrected measured velocity envelope, but x=0.08 forward progress
is too low.

## Training Run

- workflow: `phase2-z002-teacher-continuity`
- session: `open-duck-a100-phase2-full`
- candidate_name: `phase2_z002_teacher_continuity_full_a100`
- platform: `gpu`
- returncode: `0`
- elapsed_s: `734.989960597`
- actuator_bridge_enabled: `True`
- target_rate_scale: `-0.01`
- actuator_tracking_scale: `-0.005`
- non_deployable: `True`

## Exported ONNX Checkpoints

| step | sha256 |
|---:|---|
| 40960 | `0e7968e11eb6413cdfcb90c50ed7c0ea7e47589b218f2457936a46422fc6d635` |
| 81920 | `0872b58301e9f89ad6890cd361b4f04e2a91580a5194177e01237ce8a1fa77e2` |
| 122880 | `abfe4267ca7fda9ef7b2ddbbe8e418302b701ce3d73ca1326ce42aa795af88f5` |

## Reward Steps

| step | reward | reward_std |
|---:|---:|---:|
| 0 | 32.523781 | 29.220947 |
| 40960 | 38.774055 | 30.957735 |
| 81920 | 40.663956 | 31.227600 |
| 122880 | 43.156578 | 31.167498 |

## Local Compact Sweep

Local CPU compact sweep:
`outputs/analysis/phase2_z002_teacher_continuity_full_a100_local_compact_sweep/`

| checkpoint | command_x | status | max_pitch_vel_p95 | max_tracking_p95 | track_ratio | mean_local_vx |
|---|---:|---|---:|---:|---:|---:|
| 40960 | 0.000 | `PASS_CANDIDATE_SIM_GATE` | 1.0526 | 0.1937 | NA | 0.0068 |
| 40960 | 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 1.5478 | 0.2178 | 0.2102 | 0.0168 |
| 81920 | 0.000 | `PASS_CANDIDATE_SIM_GATE` | 1.0721 | 0.1946 | NA | 0.0063 |
| 81920 | 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 1.5473 | 0.2174 | 0.2189 | 0.0175 |
| 122880 | 0.000 | `PASS_CANDIDATE_SIM_GATE` | 1.1208 | 0.1950 | NA | 0.0056 |
| 122880 | 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 1.5543 | 0.2158 | 0.2040 | 0.0163 |

Best compact checkpoint by x=0.08 track ratio:
`81920`, with track ratio `0.2189`, mean local vx `0.0175 m/s`,
max pitch sent target velocity p95 `1.5473 rad/s`, and max tracking p95
`0.2174 rad`.

## Decision

`HOLD_LOW_FORWARD_PROGRESS`

This run did not fail by exceeding the measured actuator envelope. It failed
because the teacher-continuity training objective suppressed forward motion
below the compact promotion threshold. The next recipe should preserve the
teacher/source action more directly or introduce a stronger trust-region
continuity term; another scalar reward-only tweak is unlikely to address this
specific hold.

No robot test, SSH, deploy, runtime behavior change, grounded replay, or
candidate promotion was performed.
