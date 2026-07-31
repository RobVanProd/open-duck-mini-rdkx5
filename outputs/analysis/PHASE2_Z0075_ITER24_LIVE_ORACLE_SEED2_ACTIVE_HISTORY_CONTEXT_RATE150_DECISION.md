# Phase 2 z0.0075 Iter24 Live-Oracle Seed2-Active History-Context Rate150 Decision

status: `HOLD_ITER24_LIVE_ORACLE_SEED6_REGRESSION`

## Context

Iter23 corrected-settle live-oracle DAgger recovered seeds 0, 1, 6, and 7
under the compact rough+push corrected-bridge screen, but seed2 reversed and
fell at 282 samples. Iter24 continued the live-oracle loop from the iter23
deployable student and relabeled the current student-visited state distribution
with the source-VX selector oracle.

The live-oracle data collection used the canonical compact setup:

- reset mode: `home-support`
- reset settle ticks: `10`
- task: `rough_terrain_backlash`
- terrain hfield z scale: `0.0075`
- corrected bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- push perturbations: enabled, `0.075-0.125`, interval `1.0-1.5 s`

No robot tests, SSH, deploy, runtime behavior changes, grounded replay, or PPO
training were performed.

## Candidate

- path: `policy/candidates/phase2_z0075_iter24_live_oracle_seed2_active_history_context_rate150_20260704/candidate.onnx`
- ONNX sha256: `31a5c2d20d0ae33733c82d0280ca8a297035d74b2a62cc35055b11ebeb152670`
- NPZ sha256: `ed24bdae116c628f72b4a96eb8dfb88ae060c9987ee348447fc8e25650083c5e`
- aggregate manifest: `outputs/analysis/live_oracle_dagger_phase_student/iter_024_history_context_resetsettle10_seed2_active/live_oracle_dagger_aggregate_manifest.json`
- aggregate manifest sha256: `3532495e898a2166846f082254384b3a7de88c49637ff713136a7b4dd7c8be6a`
- live-oracle run sha256: `2fc9cff08b631dfca0697084fe6dac0d0b423dcbaacb0b5022dda32cfdea66dd`
- x=0.08 screen JSON sha256: `14b6ea7cee12ce4f890550933289b6aa297c140a70b1f19319f9281ab94d8ce9`
- x=0.0 screen JSON sha256: `8f91f0dc873d77f466086f5f88093fadaab5a8bb796fb8df45f738275c21171d`
- training status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

## Fit Metrics

- samples: `67219`
- target-rate p95: `1.369480 rad/s`
- target-rate max: `9.827526 rad/s`

## Compact x=0.08 Screen

| seed | status | samples | termination | track_ratio | mean_local_vx | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 | max_vel_excess |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3256 | 0.0261 | 0.1922 | 0.1591 | 1.5713 | 0.1836 | 0.0000 |
| 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3584 | 0.0287 | 0.1786 | 0.1585 | 1.5572 | 0.1854 | 0.0000 |
| 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3278 | 0.0262 | 0.1822 | 0.1590 | 1.5779 | 0.1886 | 0.0000 |
| 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 250 | `fall_or_nan` | -0.5659 | -0.0453 | 0.2187 | 0.0690 | 1.5557 | 0.1794 | 0.0000 |
| 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3437 | 0.0275 | 0.1863 | 0.1565 | 1.5715 | 0.1876 | 0.0000 |

## Compact x=0.0 Screen

| seed | status | samples | termination | mean_local_vx | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 | max_vel_excess |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0007 | 0.0621 | 0.1615 | 0.0085 | 0.0412 | 0.0000 |
| 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0009 | 0.0652 | 0.1610 | 0.0087 | 0.0423 | 0.0000 |

## Interpretation

Iter24 recovered the active iter23 seed2 reverse/fall failure, but regressed
seed6 into a reverse/fall at 250 samples. It preserved the compact x=0.0 command
semantics on seeds 0 and 1 and stayed inside the corrected velocity envelope,
but it did not improve the compact distribution enough to promote.

This confirms the current live-oracle history-context loop is still trading
seed-specific stability failures rather than producing a seed-robust deployable
policy.

## Decision

Do not promote this candidate and do not run robot validation.

Recommended next step:

- treat seed6 as the active regression if continuing live-oracle DAgger;
- compare iter23 and iter24 seed2/seed6 traces before another iteration;
- avoid one-off static patches outside the aggregate live-oracle loop unless
  they are used only to diagnose the seed trade.
