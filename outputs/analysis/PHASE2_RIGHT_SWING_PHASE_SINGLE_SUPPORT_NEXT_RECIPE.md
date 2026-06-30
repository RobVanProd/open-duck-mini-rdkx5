# Phase 2 Right-Swing Phase-Single-Support Recipe

status: `PRE_REGISTERED_NOT_STARTED`

## Purpose

Test whether the current Phase 2 plateau is caused by a learned high
double-support contact pattern rather than missing local swing lift. The
structural, phase-lift, and phase-advance branches all stayed upright but
remained near `0.020 m/s`, `0.25` track ratio, and `85%` double support.

This branch adds a phase-primary contact objective: during the commanded swing
window, the swing foot should unload and the stance foot should stay planted.
Phase defines the requested window; contact remains the measured outcome.

## Scope

- Offline sim/training only.
- No robot, SSH, deploy, grounded replay, or runtime behavior change.
- Warm-start from the corrected-bridge candidate lineage.
- Keep `obs[1,101] -> actions[1,14]`.
- Keep the corrected bridge authoritative:
  `outputs/analysis/actuator_response_fit_corrected_knee.json`.
- Keep corrected per-joint velocity-envelope gates unchanged.

## Training Recipe

Workflow:

```text
phase2-right-swing-phase-single-support
```

Additional reward terms over the phase-advance baseline:

```text
forward_phase_single_support_scale: -0.004
forward_phase_single_support_swing_contact_weight: 1.0
forward_phase_single_support_stance_no_contact_weight: 2.0
```

Retained safety and motion terms:

```text
forward_swing_target_rate_limit_scale: -0.0025
forward_swing_target_rate_limit_joint_indices: 11,12,13
forward_swing_target_rate_limit_values: 2.25,2.75,2.00
forward_phase_swing_lift_scale: -0.0006
forward_phase_swing_lift_target_m: 0.012
forward_swing_advance_scale: -0.001
forward_swing_advance_target_m: 0.004
forward_swing_clearance_scale: -0.00025
forward_swing_clearance_target_m: 0.016
```

## Gate

Run the same corrected-bridge terrain gate used by the prior branches:

```text
task: rough_terrain_backlash
command_x: 0.08
terrain_hfield_z_scale: 0.0024
bridge: fitted corrected-knee bridge
seeds: 0-7
duration: 15 s
terrain swing subchecks enabled
```

Promote only if:

```text
PASS_CANDIDATE_SIM_GATE 8/8
falls 0/8
duration_complete 8/8
corrected-envelope max target-velocity excess 0 on every seed
mean track ratio materially above the ~=0.25 plateau
double-support dwell materially below the ~=85% plateau
```

## Falsifier

If the candidate remains near the same `0.25` track-ratio / `85%` double-support
plateau, stop the scalar reward-shaping line and pivot to the live-oracle /
phase-aware student path. That would show that feed-forward reward shaping is
preserving the wrong contact mode.
