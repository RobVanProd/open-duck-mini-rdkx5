# Phase 2 PPO Step-0 Seed 5 Trace Analysis

status: `HOLD_POST_PUSH_SEED5_MARGIN`

This is an offline trace comparison between the passing phase-modulated parent
and the PPO-loc step-0 export. It did not train, SSH, deploy, run robot tests,
touch the robot, or change robot runtime behavior.

## Inputs

- phase parent: `outputs/analysis/phase2_health_routed_pass_parent_phase_mod_rate150_student/candidate.onnx`
- PPO step-0 ONNX: `outputs/analysis/phase2_health_routed_parent_ppo_loc_rate150_step0.onnx`
- PPO step-0 checkpoint: `outputs/analysis/phase2_health_routed_parent_ppo_loc_rate150_step0_checkpoint`
- comparison gate: `outputs/analysis/PHASE2_HEALTH_ROUTED_PARENT_PPO_STEP0_SEED5_TRACE_COMPARE.md`
- comparison JSON: `outputs/analysis/phase2_health_routed_parent_ppo_step0_seed5_trace_compare.json`
- setting: `x=0.08`, `rough_terrain_backlash`, corrected fitted bridge, terrain z scale `0.0075`, pushes enabled `0.075`-`0.125`, reset `home-support` with `10` settle ticks.

## Gate Split

| policy | seed | status | samples | termination | mean vx | track ratio | base height min | max vel p95 | max tracking p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|
| phase parent | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0296 | 0.3700 | 0.1588 | 1.5335 | 0.1874 |
| PPO step-0 | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 625 | `fall_or_nan` | 0.0010 | 0.0122 | 0.0819 | 1.5172 | 0.1755 |

Both policies stayed within the corrected velocity envelope. The failure is not
caused by target-rate excess.

## Same-Observation Policy Delta

The two policies were evaluated on the same full observation traces to separate
action mismatch from closed-loop state divergence.

On the passing phase-parent observations:

- action abs delta p50: `0.00249`
- action abs delta p95: `0.00796`
- action abs delta p99: `0.01086`
- action abs delta max: `0.01712`

On the PPO step-0 observations:

- action abs delta p50: `0.00262`
- action abs delta p95: `0.00978`
- action abs delta p99: `0.03207`
- action abs delta max: `0.27831`
- window `0-100` p95/max: `0.00677` / `0.01255`
- window `100-300` p95/max: `0.00872` / `0.02226`
- window `300-500` p95/max: `0.00712` / `0.01623`
- window `500-625` p95/max: `0.03208` / `0.27831`
- window `600-625` p95/max: `0.10403` / `0.27831`

First same-observation max action delta thresholds on the PPO step-0 trace:

- `>0.02`: tick `248`
- `>0.05`: tick `618`
- `>0.10`: tick `619`
- `>0.20`: tick `622`

Interpretation: on the nominal parent manifold the PPO step-0 export is very
close to the phase parent. The large action delta appears only after the PPO
rollout is already off-manifold near the fall.

## Rollout Divergence

Same-tick PPO step-0 minus phase-parent rollout deltas over ticks `0-624`:

- base-height diff p50: `0.00025` m
- base-height abs diff p95: `0.01199` m
- base-height max abs diff: `0.08107` m
- final base-height diff: `-0.08107` m
- body-pitch diff p50: `-0.01199` rad
- body-pitch abs diff p95: `0.32517` rad
- body-pitch max abs diff: `1.57832` rad
- vx diff mean: `-0.02920` m/s
- vx diff p95 abs: `0.13617` m/s

First base-height divergence thresholds:

- abs diff `>0.01` m: tick `541`
- abs diff `>0.02` m: tick `606`
- abs diff `>0.04` m: tick `622`
- abs diff `>0.06` m: tick `624`

The PPO step-0 trace had push events at the same cadence as the parent and
failed after the late push sequence. The collapse is a post-push stability
margin loss on seed 5, not a global export/fidelity failure.

## Decision

Do not launch Stage A DR from this PPO step-0 checkpoint yet. It is close enough
to be a useful trainable artifact, but it does not preserve the phase parent's
seed-5 post-push margin.

Next work should target the seed-5 post-push region directly:

1. Add seed-5 post-push parent trace samples around ticks `500-625` to the
   PPO-compatible manifest with higher weight.
2. Rebuild the PPO-loc prior and step-0 checkpoint.
3. Re-run the x=0.08 seed-5 screen first, then the full8 x=0.08 and x=0.0 gates.
4. Only after the PPO step-0 checkpoint clears both gates should Stage A DR
   training resume.
