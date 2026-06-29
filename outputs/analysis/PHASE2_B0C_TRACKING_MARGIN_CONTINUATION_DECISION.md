# Phase 2 B0C Tracking-Margin Continuation Decision

status: `HOLD_B0C_TRACKING_MARGIN_NOT_PROMOTABLE`

This continuation started from the Stage B0 mild-push checkpoint and trained on rough
terrain with gentle pushes plus actuator-tracking pressure:

- restore checkpoint: `outputs/phase2_domain_randomization/stage_b0_mild_push_from_a2_gpu/smoke_20260628T075006Z_gpu/2026_06_28_035626_491520`
- task: `rough_terrain_backlash`
- terrain: `hfield_z_scale=0.002`
- push: enabled, magnitude `0.02-0.10`
- actuator tracking scale: `-0.025`
- restore-policy KL scale: `0.8`
- platform: local ROCm GPU

Training completed without robot access and wrote checkpoints at `81920`, `163840`, and
`245760` steps. The final checkpoint reward was higher than the initial checkpoint, but
the strict candidate gate did not improve enough.

## Gate Screen

Final checkpoint:

`outputs/phase2_domain_randomization/stage_b0c_rough_z002_push_tracking_margin_from_b0_gpu/smoke_20260629T062042Z_gpu/2026_06_29_022725_245760.onnx`

Screen:

- corrected bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- command: `x=0.08`
- task: `rough_terrain_backlash`
- terrain: `hfield_z_scale=0.002`
- push: enabled, interval `1.0-1.5s`, magnitude `0.05-0.10`
- seeds: `0,2,4,5`

| seed | status | track ratio | max tracking p95 | max pitch vel p95 | push success |
|---:|---|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_TRACKING` | 0.4867 | 0.2081 | 1.7774 | 0.7500 |
| 2 | `HOLD_CANDIDATE_TRACKING` | 0.4052 | 0.2024 | 1.7780 | 0.7500 |
| 4 | `PASS_CANDIDATE_SIM_GATE` | 0.4755 | 0.1997 | 1.7929 | 0.7500 |
| 5 | `PASS_CANDIDATE_SIM_GATE` | 0.5057 | 0.1993 | 1.7827 | 1.0000 |

## Interpretation

B0C preserved useful forward motion and low target velocity, but it did not solve the
strict tracking-margin blocker. It improved some B0 failing seeds while worsening or
leaving seed 0/2 above the `0.20 rad` tracking threshold.

The result reinforces the current Phase 2 picture:

- output filters can fix rate but hurt nominal tracking,
- B0-style push training preserves motion but misses strict tracking,
- stronger B1-style push training freezes,
- naive actuator-tracking continuation does not close the remaining margin.

## Next Recommendation

Do not promote B0C. The next attempt should not simply increase actuator-tracking penalty.
Use seed-targeted data or loss shaping around seeds 0 and 2 specifically, while preserving
B0/B0C's forward track ratio and low target velocity.

No robot test, SSH, deploy, grounded replay, or runtime behavior change was performed.
