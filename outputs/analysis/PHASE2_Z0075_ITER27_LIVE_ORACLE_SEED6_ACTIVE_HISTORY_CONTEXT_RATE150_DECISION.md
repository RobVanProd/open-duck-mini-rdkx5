# Phase 2 z0.0075 Iter27 Live-Oracle Seed6-Active History-Context Rate150 Decision

status: `HOLD_ITER27_LIVE_ORACLE_MULTI_SEED_REGRESSION`

## Context

Iter24 recovered the prior seed2 failure but regressed seed6. Iter25 and
Iter26 showed that simple dual-anchor sample weighting was not a viable
anti-regression method. Iter27 returned to the live-oracle DAgger mechanism
without scalar anchor weighting:

- student policy: iter24 deployable history-context student
- teacher/base manifest: iter24 live-oracle aggregate
- task: `rough_terrain_backlash`
- command: `x=0.08`
- terrain hfield z scale: `0.0075`
- reset mode: `home-support`
- reset settle ticks: `10`
- corrected bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- push perturbations: enabled, `0.075-0.125`, interval `1.0-1.5 s`

No robot tests, SSH, deploy, runtime behavior changes, grounded replay, or PPO
training were performed.

## Candidate

- path: `policy/candidates/phase2_z0075_iter27_live_oracle_seed6_active_history_context_rate150_20260705/candidate.onnx`
- ONNX sha256: `e072b44e6e1f0e8be2487c1c79849f8decf325824ebec55c27859c5e54207d6a`
- NPZ sha256: `0c370948f3b058341049dca47d1cfd46aae5a3e941367416a16bfe6345a927d9`
- aggregate manifest: `outputs/analysis/live_oracle_dagger_phase_student/iter_027_history_context_resetsettle10_seed6_active/live_oracle_dagger_aggregate_manifest.json`
- aggregate manifest sha256: `ccf4639771c78d6d24638bc9a5db9d51098f767b356791afeeab06c8151eff46`
- x=0.08 screen JSON sha256: `80d4e8ec2d2cd2e77f34bcf0e17588d8a43bf5e39f0db5b6e19541731626ef14`
- training status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`
- training samples: `71969`

## Live-Oracle Rollout Before Relabel

The iter27 data-collection rollout reproduced the known iter24 distribution:
seeds 0, 1, 2, and 7 passed; seed6 failed at 250 samples with reverse motion.
The relabel therefore captured the active seed6 failed-state distribution.

## Compact x=0.08 Screen

| seed | status | samples | termination | track_ratio | mean_local_vx | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 | max_vel_excess |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3395 | 0.0272 | 0.1793 | 0.1587 | 1.5389 | 0.1848 | 0.0000 |
| 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3830 | 0.0306 | 0.1897 | 0.1576 | 1.5272 | 0.1843 | 0.0000 |
| 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 307 | `fall_or_nan` | -0.4823 | -0.0386 | 0.1841 | 0.0701 | 1.5546 | 0.1753 | 0.0000 |
| 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 390 | `fall_or_nan` | 0.9697 | 0.0776 | 0.4099 | 0.0005 | 1.5506 | 0.1868 | 0.0000 |
| 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 611 | `fall_or_nan` | 0.0141 | 0.0011 | 0.2035 | 0.0817 | 1.5395 | 0.1827 | 0.0000 |

Distribution:

- pass count: `2 / 5`
- fall count: `3 / 5`
- track_ratio_mean: `0.2448`
- mean_local_vx_mean: `0.0196 m/s`
- max velocity-envelope excess: `0.0000 rad/s`

## Interpretation

Iter27 is worse than iter24 on the compact rough+push x=0.08 screen. The live
relabel did not fix seed6, and it regressed seed2 and seed7. All failures still
have zero corrected velocity-envelope excess, so this is not an actuator-rate
or bridge-tracking issue.

This falsifies a clean continuation of the current history-context
live-oracle BC loop as a sufficient fix for the seed-conditioned stability
trade. Together with Iter25/Iter26, it also reinforces that adding more global
sample pressure to the same BC representation is misaligned.

## Decision

Do not promote this candidate. Do not run x=0.0 gates or robot validation.

Recommended next step:

- stop continuing this BC-only live-oracle rung as-is;
- use iter24 as the latest useful deployable baseline for analysis;
- change the policy class or optimization objective before another expensive
  gate, for example a validation-aware mixture/ensemble diagnostic, recurrent
  policy with explicit hidden-state export, or PPO fine-tuning from a walking
  BC baseline with strict multi-seed validation.
