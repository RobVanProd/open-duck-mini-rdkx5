# Phase 2 z=0.0075 Iter17 Motion-Only Recurrent Decision

status: `HOLD_RECURRENT_MOTION_STABILITY_SPLIT`

This is offline sim/analysis only. It did not SSH, deploy, run robot tests,
grounded replay, or change runtime behavior.

## Question

Iter15 and Iter16 recurrent students survived the intermediate-push condition
only by collapsing into double-support standstill. Iter17 tested whether that
was caused by data balance: the recurrent manifest was filtered to keep only
entries with `mean_vx >= 0.015 m/s`, then the same stateful H96/S32 recurrent
student was trained with the softer rate penalty.

The recurrent export remains diagnostic-only:

```text
inputs:  obs[1,101], h_in[1,96]
outputs: continuous_actions[1,14], h_out[1,96]
```

It is not robot-deployable without a runtime hidden-state adapter.

## Artifacts

- motion-only manifest: `outputs/analysis/phase2_z0075_iter17_motion_only_recurrent_manifest.json`
- kept entries: `51`
- exported ONNX: `outputs/analysis/phase2_z0075_iter17_motion_only_recurrent_h96_s32_candidate/candidate.onnx`
- ONNX sha256: `ae0be632977d00cf0e594a2b2f941d0ebc9a4aa1fef995656fc37614599a0f67`
- NPZ sha256: `2fd24cb73a497db81a510346f6fb219c5b457de1e14ede648ed5efc2e0851b9c`

## Fail-Seed Gate

Condition:

- task: `rough_terrain_backlash`
- command_x: `0.08`
- bridge: corrected fitted bridge
- terrain z scale: `0.0075`
- reset mode: `home-support`
- push interval: `1.0-1.5s`
- push magnitude: `0.075-0.125`
- seeds: `0,2,6`

| seed | status | samples | mean vx | track ratio | pitch p95 | base min | p95 excess | max excess | tracking p95 | push success |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 311 | -0.0345 | -0.4313 | 0.1984 | 0.0763 | 0.0000 | 2.8166 | 0.1858 | 0.6000 |
| 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 692 | 0.0531 | 0.6636 | 0.2805 | -0.0049 | 0.0000 | 0.1971 | 0.1919 | 0.8333 |
| 6 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | 0.0307 | 0.3838 | 0.1744 | 0.1532 | 0.0000 | 0.1971 | 0.1876 | 0.9231 |

## Decision

`HOLD_RECURRENT_MOTION_STABILITY_SPLIT`

Filtering out low-motion data restores movement, but it also reintroduces
instability and target-velocity holds. Iter15/16 showed the recurrent class can
stabilize by standing; Iter17 shows motion-only recurrent BC can move but cannot
clear the rough z=0.0075 intermediate-push fail-seed gate.

This is stronger than a simple architecture failure: the current recurrent BC
objective has a motion/stability split. Hidden state is not enough without an
objective or aggregation rule that simultaneously preserves forward motion,
push recovery, and corrected-envelope compliance.

## Next Recommendation

Do not promote Iter17. Do not add a runtime recurrent adapter for these
artifacts.

The next branch should stop treating the tradeoff as a pure supervised fit.
Use one of:

1. gate-aware live-oracle DAgger that explicitly labels both sides of the
   tradeoff: full-gain seed0 lunge, gain-0.95 seed0 pass, gain-0.95 seed6 late
   collapse, and Iter17 moving failures
2. a deployable feed-forward push-lunge classifier/wrapper that applies
   attenuation only when the observation indicates the first-push lunge state
3. PPO fine-tuning from the best deployable feed-forward candidate with hard
   progress and push-recovery gates, using the corrected actuator bridge

The corrected actuator envelope remains fixed. Robot validation remains blocked.
