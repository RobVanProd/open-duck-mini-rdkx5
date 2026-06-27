# Next Deployable Policy Branch Decision

status: `PLAN_GATE_AWARE_ROLLOUT_CORRECTION_OR_RECURRENT_STUDENT`

This is an offline decision artifact. It does not train, run simulation, SSH, deploy, run robot tests, or change runtime behavior.

## Executive Summary

Do not run another clip/filter/weight-blend/feed-forward-BC branch. Build a gate-aware deployable-policy training path that preserves the working selector behavior while directly penalizing fitted-bridge tracking through the right-knee contact transition.

The cheap post-hoc branches are now closed negative. The remaining blocker is the deployable policy's representation/training of the right-knee contact transition, not one missing scalar cap.

## Candidate Gate Comparison

| candidate | status | runs | complete | falls/terms | vx mean | track ratio | vel p95 range | tracking p95 range |
|---|---|---:|---:|---:|---:|---:|---|---|
| exact selector blend ONNX | `HOLD_CANDIDATE_TRACKING` | 8 | 8 | 0 | 0.0461 | 0.5768 | 4.7355-5.1118 | 0.2679-0.2800 |
| right-knee 4.3 curation | `HOLD_CANDIDATE_TRACKING` | 8 | 8 | 0 | 0.0479 | 0.5992 | 4.1979-4.2994 | 0.2682-0.2773 |
| pitch-chain 4.3 curation | `HOLD_CANDIDATE_TRACKING` | 8 | 8 | 0 | 0.0477 | 0.5965 | 4.1935-4.2879 | 0.2685-0.2794 |
| right-knee transition filter | `HOLD_CANDIDATE_TRACKING` | 8 | 8 | 0 | 0.0449 | 0.5617 | 4.6244-4.7790 | 0.2675-0.2782 |
| pitch-chain 4.3 PPO-shape rate student | `HOLD_CANDIDATE_TRACKING` | 8 | 8 | 0 | 0.0393 | 0.4913 | 3.6035-3.7059 | 0.2516-0.2561 |

## PPO / Blend Sweep Evidence

| sweep | best policy | status | track ratio | max tracking p95 | max velocity p95 | failure reasons |
|---|---|---|---:|---:|---:|---|
| behavior-prior PPO weight blend sweep | `blends_actuator_tracking_behavior_prior_weight_blends_blend_alpha_0p0500` | `HOLD_REJECT_CANDIDATE_CHECKPOINT` | 0.3158 | 0.2217 | 1.8523 | `['command 0: HOLD_CANDIDATE_TRACKING', 'command 0.08: HOLD_CANDIDATE_TRACKING']` |
| behavior-prior PPO checkpoint sweep | `smoke_20260627T102504Z_gpu_2026_06_27_102952_0` | `HOLD_REJECT_CANDIDATE_CHECKPOINT` | 0.2692 | 0.2233 | 1.9323 | `['command 0: HOLD_CANDIDATE_TRACKING', 'command 0.08: HOLD_CANDIDATE_TRACKING']` |

## Right-Knee Transition Evidence

```text
right-knee action-derived velocity > 3.75 rad/s: 506 / 3992
within 2 ticks of contact transition: 404 / 506
```

## Closed Branches

- `uniform pitch-chain clipping`: 4.3 rad/s cap across the pitch chain was numerically indistinguishable from right-knee-only 4.3 and still held tracking.
- `transition-adjacent sample deletion`: filtering preserved stability but reduced forward progress and raised target-velocity p95.
- `post-hoc ONNX weight interpolation`: small blends did not reduce tracking; larger blends regressed toward low progress.
- `scalar behavior-prior PPO smoke`: prior PPO smoke and A100 probe improved reward or calmness while losing useful forward motion.
- `feed-forward PPO-shape BC smoothing`: pitch-chain 4.3 PPO-shape rate student lowered target velocity and tracking slightly but lost progress and still held the strict fitted-bridge tracking gate.
- `static gate-aware source-VX relabeling`: targeted relabeling of strict-gate seed 1/4 states produced only tiny tracking changes and did not clear the same fitted-bridge tracking hold.

## Recommended Next Branch

`PLAN_GATE_AWARE_ROLLOUT_CORRECTION_OR_RECURRENT_STUDENT`

Minimum requirements:

- uses the standard strict fitted-backlash x=0.08 multi-seed gate as the primary score
- compares against the exact selector blend and PPO-shape warm-start baselines
- preserves duration_complete 8/8 and mean vx near 0.045-0.050 m/s before claiming progress
- reduces max pitch velocity p95 below the 3.75 rad/s envelope or explicitly documents why the gate remains held
- reduces max tracking p95 materially below the current ~0.27 rad plateau
- does not pass by freezing, reversing, or shortening the horizon

Candidate mechanisms:

- DAgger/rollout correction with the strict gate failure states added back to the teacher dataset
- recurrent or phase-aware student for the stance-transition discontinuity
- PPO fine-tune from a PPO-compatible BC warm start with stronger teacher-action continuity and gate metrics checked after every short run

## Stop Rules

- Do not run robot validation from any candidate in this table.
- Do not launch another clipping, deletion, or scalar weight-blend branch unless a new diagnostic identifies a different failure mechanism.
- Do not count a run as improvement if it lowers falls by freezing or reducing forward progress.
- Do not relax the fitted actuator envelope to make the candidate pass.
