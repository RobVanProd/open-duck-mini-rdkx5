# PPO-Loc Iter24 Step-0 Trace Failure Decision

status: `HOLD_PPO_LOC_STEP0_CLOSED_LOOP_INSTABILITY`

Offline diagnostic only. No training, robot test, SSH, deploy, grounded replay,
or runtime behavior change was performed.

## Inputs

- PPO step-0 ONNX: `outputs/analysis/ppo_loc_iter24_live_oracle_seed2_active_rate150_step0.onnx`
- BC fit NPZ: `outputs/analysis/ppo_loc_iter24_live_oracle_seed2_active_rate150_candidate/candidate_mlp.npz`
- aggregate manifest: `outputs/analysis/live_oracle_dagger_phase_student/iter_024_history_context_resetsettle10_seed2_active/live_oracle_dagger_aggregate_manifest.json`
- corrected bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- traced sweep: `outputs/analysis/ppo_loc_iter24_live_oracle_seed2_active_rate150_step0_trace_seed0_1_6_7.json`

Trace replay used the same compact rough+push gate shape as the earlier step-0
screen:

```text
task: rough_terrain_backlash
terrain_hfield_z_scale: 0.0075
reset_mode: home-support
reset_settle_ticks: 10
bridge: fitted corrected bridge
command_x: 0.08
pushes: 0.075-0.125, interval 1.0-1.5s
seeds: 0,1,6,7
trace_full_obs: true
```

## Replay Result

| seed | status | samples | track_ratio | mean vx | base min | p95 excess | max excess | single support | double support |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 638 | 0.0190 | 0.0015 | 0.0788 | 0.0000 | 0.0000 | 24.4514 | 75.3918 |
| 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.3428 | 0.0274 | 0.1583 | 0.0000 | 0.0000 | 25.4667 | 74.5333 |
| 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 212 | -0.7918 | -0.0633 | 0.0724 | 0.0000 | 0.0000 | 13.6792 | 86.3208 |
| 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 577 | 0.6774 | 0.0542 | 0.0033 | 0.0000 | 0.0000 | 23.0503 | 76.2565 |

The regression reproduces without corrected-envelope velocity excess. Seed 1 is
included as a passing control.

## Manifest-Coverage Analysis

Each trace was analyzed with `tools/analyze_warmstart_seed_failure.py` against
the Iter24 live-oracle aggregate. Thresholds were the tool defaults:

```text
OOD p95 nearest distance > 2.0
action L1 p95 > 0.12
```

| seed | analyzer status | nearest dist mean | nearest dist p95 | nearest dist max | action L1 mean | action L1 p95 | action L1 max |
|---:|---|---:|---:|---:|---:|---:|---:|
| 0 | `HOLD_SEED_FAILURE_CLOSED_LOOP_INSTABILITY` | 0.1468 | 0.2306 | 0.5975 | 0.0114 | 0.0218 | 0.1104 |
| 1 | `HOLD_SEED_FAILURE_CLOSED_LOOP_INSTABILITY` | 0.1515 | 0.2267 | 0.5015 | 0.0109 | 0.0209 | 0.1104 |
| 6 | `HOLD_SEED_FAILURE_CLOSED_LOOP_INSTABILITY` | 0.1953 | 0.3357 | 0.5947 | 0.0137 | 0.0271 | 0.1104 |
| 7 | `HOLD_SEED_FAILURE_CLOSED_LOOP_INSTABILITY` | 0.1535 | 0.2228 | 0.6520 | 0.0113 | 0.0247 | 0.1104 |

All traced seeds are close to the aggregate and have modest nearest-action
mismatch. The failed seeds are not out-of-distribution under the current BC
normalization, and the action fit is not locally bad by this diagnostic.

## Decision

The PPO-compatible step-0 path is technically valid, but the current PPO-loc
compression is not a trainable promotion point. Its failures are closed-loop
stability/representation failures on well-covered states, not missing-label or
local action-fit failures.

Do not launch long PPO/domain-randomization training from this step-0 checkpoint
as-is. Action fidelity and manifest coverage are insufficient gates for the
warm-start. The next aligned Phase 2 step must select or train warm-starts by
task-matched closed-loop corrected-bridge gates, or add an explicit behavior
preservation mechanism that survives closed-loop seed perturbations before any
large PPO/DR run.

## Artifacts

- seed 0 analysis: `outputs/analysis/PPO_LOC_ITER24_STEP0_SEED_000_WARMSTART_FAILURE_ANALYSIS.md`
- seed 1 analysis: `outputs/analysis/PPO_LOC_ITER24_STEP0_SEED_001_WARMSTART_FAILURE_ANALYSIS.md`
- seed 6 analysis: `outputs/analysis/PPO_LOC_ITER24_STEP0_SEED_006_WARMSTART_FAILURE_ANALYSIS.md`
- seed 7 analysis: `outputs/analysis/PPO_LOC_ITER24_STEP0_SEED_007_WARMSTART_FAILURE_ANALYSIS.md`
