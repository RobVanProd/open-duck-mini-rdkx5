# Phase 2 z=0.005 Live-Oracle Iter0 Student Fit Decision

status: `HOLD_ITER0_SOURCE_NEEDS_STRENGTHENING`

This is an offline decision artifact. It did not run robot tests, SSH, deploy,
grounded replay, PPO training, or runtime behavior changes.

## Inputs

- corrected bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- aggregate manifest: `outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0_aggregate_manifest.json`
- aggregate dataset id: `3f68992af82062f7`
- aggregate samples: `12806`
- task: `rough_terrain_backlash`
- terrain hfield z scale: `0.005`
- command: `x=0.08`

## Student Results

| student | deployable contract | fit status | gate status | main failure |
|---|---|---|---|---|
| phase/command-modulated feed-forward | `obs[1,101] -> continuous_actions[1,14]` | clean, p95 action error `0.018830`, target-rate p95 `1.783 rad/s` | `1/8` pass, `1/8` fall | seed 5 support collapse; surviving seeds under-progress |
| recurrent H96 diagnostic | stateful ONNX with `h_in/h_out` | p95 action error `0.044005`, target-rate p95 `1.717 rad/s`, target-rate max `3.890 rad/s` | `0/8` pass, `8/8` falls | closed-loop overdrive, max pitch velocity p95 `5.240 rad/s` on every seed |

## Seed 5 Relabel Check

The iter0 live-oracle relabel did not provide a strong recovery for the seed-5
z=0.005 failure state:

- original student seed-5 rollout length: `56` samples
- mean local vx: `-0.2654 m/s`
- final/min base height: `0.0677 m`
- max body pitch: `1.4489 rad`
- double support: `91.1%`
- single support: `7.1%`
- relabel summary action_delta_p95: `0.1610`
- relabel summary action_delta_max: `0.2628`
- local max-action-delta p95 check: `0.2455`

The relabeled trace is therefore still a failed, double-support-dominated,
backward-moving support state. Treating it as another positive supervised batch
does not change the mechanism enough to justify more fits on the same aggregate.

## Decision

Do not promote either iter0 ONNX. Do not run robot validation. Do not continue
supervised-rate-only architecture tweaks on this aggregate.

The next useful offline branch must strengthen the corrected z=0.005 source or
oracle before another live-oracle iteration. A valid next iteration needs labels
that change the seed-5 support state, not merely a larger student model.

Recommended next action:

1. Build or mine a corrected z=0.005 support/recovery source that keeps the
   corrected per-joint velocity envelope and survives seed 5.
2. Verify that the new source has forward progress, non-collapse base height,
   and useful single-support timing on z=0.005 before using it as an oracle.
3. Only then run live-oracle DAgger iteration 1 against the strengthened source.
