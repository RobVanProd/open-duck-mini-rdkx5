# Phase 2 Z002 Teacher Continuity Clean A100 FG64 Result

status: `HOLD_DIAGNOSTIC_ONLY`
generated_at: `2026-06-30T05:00:00Z`

## Summary

The fresh `open-duck-a100-clean` Colab A100 session successfully ran the
Phase 2 Z002 teacher-continuity workflow with the reduced diagnostic
`--phase2-num-timesteps 64` override. This confirms the maintained Colab
workflow can train/export on a clean A100 session; the earlier no-sentinel
failures were consistent with the stale/flaky `open-duck-l4` session rather
than the recipe itself.

This is not a promoted candidate. The run was intentionally tiny and the
local compact sweep still held at x=0.08 on the candidate tracking gate.

## Training Run

- workflow: `phase2-z002-teacher-continuity`
- session: `open-duck-a100-clean`
- candidate_name: `phase2_z002_teacher_continuity_clean_fg64`
- platform: `gpu`
- returncode: `0`
- elapsed_s: `798.0699514370001`
- actuator_bridge_enabled: `True`
- target_rate_scale: `-0.01`
- actuator_tracking_scale: `-0.005`
- non_deployable: `True`
- artifact bundle downloaded: `True`

## Exported ONNX Checkpoints

| step | sha256 |
|---:|---|
| 40960 | `6148963790d356515a738a472adb33d1781e5b50862449bcbc5eb4af9c826321` |
| 81920 | `aa14be31769cfc72a942bdc4c92d36bb6b7aca99274acc47e1fd4a949ced7221` |
| 122880 | `9fd3019c18ec8ddfccaeff0187595dc4e2266df5b6ff3946faf639b1c560d010` |

## Local Compact Sweep

Local CPU compact sweep:
`outputs/analysis/phase2_z002_teacher_continuity_clean_fg64_local_compact_sweep/`

| checkpoint | command_x | status | max_pitch_vel_p95 | max_tracking_p95 | track_ratio | mean_local_vx |
|---|---:|---|---:|---:|---:|---:|
| 40960 | 0.000 | `PASS_CANDIDATE_SIM_GATE` | 1.0601 | 0.1942 | NA | 0.0057 |
| 40960 | 0.080 | `HOLD_CANDIDATE_TRACKING` | 1.5646 | 0.2200 | 0.2598 | 0.0208 |
| 81920 | 0.000 | `PASS_CANDIDATE_SIM_GATE` | 1.1026 | 0.1947 | NA | 0.0066 |
| 81920 | 0.080 | `HOLD_CANDIDATE_TRACKING` | 1.5218 | 0.2174 | 0.3029 | 0.0242 |
| 122880 | 0.000 | `PASS_CANDIDATE_SIM_GATE` | 1.1428 | 0.1951 | NA | 0.0063 |
| 122880 | 0.080 | `HOLD_CANDIDATE_TRACKING` | 1.5089 | 0.2175 | 0.3174 | 0.0254 |

Best diagnostic checkpoint by x=0.08 track ratio:
`122880`, with track ratio `0.3174`, mean local vx `0.0254 m/s`,
max pitch sent target velocity p95 `1.5089 rad/s`, and max tracking p95
`0.2175 rad`.

## Decision

`HOLD_DIAGNOSTIC_ONLY`

The clean A100 path is usable, and the recipe starts correctly, but the
64-step diagnostic checkpoints are not promotable. The next full run should
use a fresh A100 session and keep the corrected teacher-continuity settings;
this diagnostic only validates the execution path.

No robot test, SSH, deploy, runtime behavior change, grounded replay, or
candidate promotion was performed.
