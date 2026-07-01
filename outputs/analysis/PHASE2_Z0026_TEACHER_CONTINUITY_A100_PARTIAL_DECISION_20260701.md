# Phase 2 z=0.0026 Teacher-Continuity A100 Decision

status: `HOLD_PARTIAL_CANDIDATE_TRACKING`
recorded_at_utc: `2026-07-01T22:21:00Z`

## Summary

The teacher-continuity A100 run completed and produced checkpoints at 40960, 81920, and
122880 timesteps. Training artifacts and the compact checkpoint sweep were downloaded
successfully.

Compared with the previous z=0.0026 seed-5 support run, this recipe recovered meaningful
forward motion in the compact x=0.08 sweep. The best checkpoint was 81920:

- track ratio: `0.3049`
- mean local vx: `0.0244 m/s`
- max pitch sent-target velocity p95: `1.4966 rad/s`
- action saturation: `0.0%`
- max pitch tracking p95: `0.2187 rad`

That is not promotable because the corrected-bridge tracking threshold is `0.20 rad`.
It is, however, a useful directional result: behavior-prior / restore-policy continuity
improved motion without exceeding the actuator envelope.

## Run

- session: `open-duck-a100-phase2-z0026-tc`
- workflow: `phase2-z002-teacher-continuity`
- terrain override: `z=0.0026`
- candidate name: `phase2_z0026_teacher_continuity_cuda`
- training backend: A100 / CUDA
- JAX/JAXLIB: `0.7.2`
- task: `rough_terrain_backlash`
- corrected bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- restore checkpoint: `stage_c0_terrain_z002_preserve_from_a2_gpu/.../2026_06_28_064431_245760`
- behavior prior: `outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate/candidate_mlp.npz`
- post-training full gates: skipped intentionally to avoid long Colab CPU-gate transport loss
- downloaded bundle: `outputs/analysis/colab_cli_downloads/open_duck_colab_cli_phase2-z002-teacher-continuity_20260701T212721Z_artifacts.final.tar.gz`
- bundle sha256: `1f9976b4b51de22cf2b651beba78a3f0e9d79f6e773094add779876ab64c5b6a`

## Compact Sweep

| checkpoint | command_x | status | samples | max_pitch_vel_p95 | envelope | max_tracking_p95 | track_ratio | mean_local_vx |
|---|---:|---|---:|---:|---|---:|---:|---:|
| 40960 | 0.000 | `PASS_CANDIDATE_SIM_GATE` | 50 | 1.0851 | `BELOW_MEASURED_ENVELOPE` | 0.1946 | NA | 0.0064 |
| 40960 | 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | 1.5225 | `BELOW_MEASURED_ENVELOPE` | 0.2188 | 0.2200 | 0.0176 |
| 81920 | 0.000 | `PASS_CANDIDATE_SIM_GATE` | 50 | 1.1000 | `BELOW_MEASURED_ENVELOPE` | 0.1948 | NA | 0.0065 |
| 81920 | 0.080 | `HOLD_CANDIDATE_TRACKING` | 50 | 1.4966 | `BELOW_MEASURED_ENVELOPE` | 0.2187 | 0.3049 | 0.0244 |
| 122880 | 0.000 | `PASS_CANDIDATE_SIM_GATE` | 50 | 1.0799 | `BELOW_MEASURED_ENVELOPE` | 0.1950 | NA | 0.0063 |
| 122880 | 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | 1.5840 | `BELOW_MEASURED_ENVELOPE` | 0.2171 | 0.2303 | 0.0184 |

Selected checkpoint:

`/content/open_duck_training_phase2_z002_teacher_continuity_cli/smoke_20260701T213042Z_gpu/2026_07_01_214216_81920.onnx`

Selection status: `best_available_but_not_promoted` / `HOLD_PARTIAL_CANDIDATE_CHECKPOINT`.

## Decision

Do not promote this candidate. It is below the actuator velocity envelope and has meaningful
forward motion, but it misses the corrected-bridge pitch-chain tracking threshold.

The next run should preserve the teacher-continuity structure and target the remaining
tracking error directly. This result supports a narrow tracking-margin follow-up from the
81920 checkpoint, not a return to the previous low-progress support recipe.
