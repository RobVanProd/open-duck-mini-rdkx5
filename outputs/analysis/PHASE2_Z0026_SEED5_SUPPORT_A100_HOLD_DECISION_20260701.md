# Phase 2 z=0.0026 Seed-5 Support A100 Decision

status: `HOLD_LOW_FORWARD_PROGRESS`
recorded_at_utc: `2026-07-01T21:22:37Z`

## Summary

The A100 training run completed and produced checkpoints at 40960, 81920, and 122880
timesteps. The compact checkpoint sweep did not find a promotable checkpoint.

All checkpoints stayed below the corrected actuator envelope, but all held at x=0.08 for
low forward progress. The best available checkpoint was 122880, with track ratio 0.1736
and mean local vx 0.0139 m/s in the compact 1-second sweep.

The full 8-seed z=0.0026 gate was started, but the Colab CLI session was pruned while
seed 0 was starting. No full-seed result is claimed from this run.

## Run

- session: `open-duck-a100-phase2-z0026`
- workflow: `phase2-z0025-boundary`
- terrain override: `z=0.0026`
- candidate name: `phase2_z0026_seed5_support_cuda`
- training backend: A100 / CUDA
- JAX/JAXLIB: `0.7.2`
- task: `rough_terrain_backlash`
- corrected bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- bridge velocity range used for training: `2.0-3.25 rad/s`
- restore checkpoint: Phase A2 preserve narrow flat no-push checkpoint
- timesteps: `122880`

## Compact Sweep

| checkpoint | command_x | status | samples | max_pitch_vel_p95 | envelope | max_tracking_p95 | track_ratio | mean_local_vx |
|---|---:|---|---:|---:|---|---:|---:|---:|
| 40960 | 0.000 | `PASS_CANDIDATE_SIM_GATE` | 50 | 1.0842 | `BELOW_MEASURED_ENVELOPE` | 0.1919 | NA | 0.0066 |
| 40960 | 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | 1.4217 | `BELOW_MEASURED_ENVELOPE` | 0.2165 | 0.1663 | 0.0133 |
| 81920 | 0.000 | `PASS_CANDIDATE_SIM_GATE` | 50 | 1.0965 | `BELOW_MEASURED_ENVELOPE` | 0.1923 | NA | 0.0058 |
| 81920 | 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | 1.4156 | `BELOW_MEASURED_ENVELOPE` | 0.2123 | 0.1644 | 0.0132 |
| 122880 | 0.000 | `PASS_CANDIDATE_SIM_GATE` | 50 | 1.0371 | `BELOW_MEASURED_ENVELOPE` | 0.1926 | NA | 0.0065 |
| 122880 | 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | 1.4290 | `BELOW_MEASURED_ENVELOPE` | 0.2144 | 0.1736 | 0.0139 |

Selected checkpoint:

`/content/open_duck_training_phase2_z0025_boundary_cli/smoke_20260701T201848Z_gpu/2026_07_01_203039_122880.onnx`

Selection status: `best_available_but_not_promoted` / `HOLD_PARTIAL_CANDIDATE_CHECKPOINT`.

## Full Gate Status

The full seed sweep command was launched:

```text
tools/run_candidate_seed_sweep.py
  --policies phase2_z0026_seed5_support_cuda=<122880.onnx>
  --seeds 0-7
  --command-x 0.08
  --task rough_terrain_backlash
  --duration 15
  --bridge-mode fitted
  --terrain-hfield-z-scale 0.0026
```

The Colab session was pruned while seed 0 was starting:

```text
SEED_SWEEP_START policy=phase2_z0026_seed5_support_cuda seed=0 ...
session_terminated reason=pruned
```

No full-gate pass, hold, or per-seed distribution is claimed.

## Decision

This run does not improve the z=0.0026 boundary. The training recipe made the policy safer
but too slow at x=0.08. The compact sweep is enough to reject promotion.

Next work should not be another tiny scalar reward change. The evidence points to a
continuity/teacher-action mechanism or a targeted support strategy that preserves the
existing z=0.0025 motion while addressing the seed-5 z=0.0026 transition.
