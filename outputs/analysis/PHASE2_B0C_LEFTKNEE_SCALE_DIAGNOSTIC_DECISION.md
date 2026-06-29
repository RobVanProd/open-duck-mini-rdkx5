# Phase 2 B0C Left-Knee Scale Diagnostic Decision

status: `HOLD_NOT_PROMOTABLE`

## Purpose

Test whether the remaining B0C rough-terrain gentle-push tracking holds were caused by a
small, localized left-knee action amplitude excess rather than a broader robustness gap.

The wrapper is offline-only and default-off. It does not change robot runtime behavior.

## Input Policy

- source checkpoint:
  `outputs/phase2_domain_randomization/stage_b0c_rough_z002_push_tracking_margin_from_b0_gpu/smoke_20260629T062042Z_gpu/2026_06_29_022725_245760.onnx`
- wrapper tool: `tools/wrap_policy_command_scale.py`
- wrapper change: optional 14-joint `--joint-action-scale` applied after command scaling.
- tested joint: `left_knee` action index `3`

## Screens

All screens used:

- corrected-knee actuator bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- task: `rough_terrain_backlash`
- command: `x=0.08`
- terrain heightfield scale: `0.002`
- fitted bridge
- gentle pushes: 0.05-0.10, interval 1.0-1.5 s
- CPU evaluator
- duration: 5 s

| wrapper | seeds | result | note |
|---|---|---|---|
| left_knee scale `0.98` | 0,2 | `HOLD` | seed 0/2 still near or above 0.20 rad tracking threshold |
| left_knee scale `0.96` | 0,2 | `PASS` | fixed targeted seeds |
| left_knee scale `0.96` | 4,5 | `HOLD` | seed 5 regressed to tracking p95 0.2039 rad |
| left_knee scale `0.97` | 0,2,5 | `PASS` | cleared targeted failing set |
| left_knee scale `0.97` | 0-7 | `HOLD` | 7/8 pass; seed 4 tracking p95 0.2013 rad |

## Full 8-Seed Result For 0.97

Artifact:

- `outputs/analysis/PHASE2_B0C_245_LEFTKNEE_SCALE097_X008_ROUGH_Z002_GENTLE_PUSH_8SEED_GATE_CPU.md`
- `outputs/analysis/phase2_b0c_245_leftknee_scale097_x008_rough_z002_gentle_push_8seed_gate_cpu.json`

Summary:

- duration complete: 8/8
- falls: 0/8
- strict candidate gate: 7/8 pass
- hold reason: seed 4 `HOLD_CANDIDATE_TRACKING`
- seed 4 max tracking p95: `0.2013 rad`
- velocity envelope excess: `0.0000 rad/s`
- mean track ratio: `0.4353`
- mean local vx: `0.0348 m/s`
- mean push success: `0.9062`
- mean single support: `23.75%`
- mean double support: `76.10%`

## Interpretation

The left-knee scale wrapper is a useful diagnostic but not a promotable candidate.

The result confirms that the remaining B0C failure is a very narrow tracking-margin issue,
not a fall, velocity-envelope, saturation, swing-clearance, or push-recovery failure. A
3% left-knee action attenuation improves several previously failing seeds, but it still
misses the strict 8/8 gate and shifts the borderline seed rather than eliminating the
margin problem.

Do not spend more candidate-search time on post-hoc scalar joint attenuation as the main
path. The next robust fix should come from training or relabeling with explicit tracking
margin, not from another local wrapper sweep.

## Decision

`HOLD_NOT_PROMOTABLE`

No robot test, SSH, deploy, grounded replay, training, or runtime behavior change was
performed.
