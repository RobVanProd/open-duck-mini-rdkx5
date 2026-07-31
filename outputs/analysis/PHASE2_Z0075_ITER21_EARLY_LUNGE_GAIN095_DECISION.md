# Phase 2 z0.0075 Iter21 Early-Lunge Recovery Decision

status: `HOLD_ITER21_RECOVERY_LABELS_NEAR_MISS`

Offline-only Phase 2 analysis. No robot tests, SSH, deploy, grounded replay,
runtime behavior change, or PPO training was performed.

## Inputs

- base_manifest: `outputs/analysis/phase2_z0075_iter21_early_lunge_gain095_merged_manifest.json`
- base_student: `policy/candidates/phase2_z0075_iter21_early_lunge_gain095_rate150_20260704/candidate.onnx`
- base_student_sha256: `72aa93c2ab249d2e9b22bb5415ef6c96c7407833fbfd21233892b6daa6afda14`
- reg02_student: `policy/candidates/phase2_z0075_iter21_early_lunge_gain095_rate150_reg02_20260704/candidate.onnx`
- reg02_student_sha256: `1472277913622a7277977b212bf6ab552e8d834f28222c363a3de1c4661cf0b5`
- canonical_bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- task: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.0075`
- push: `enabled`, interval `1.0-1.5s`, magnitude `0.075-0.125`
- reset_mode: `home-support`

## Training Summary

The Iter21 recovery-label manifest adds 31 aligned gain0.95 pass-control
samples to the Iter13 push-window recovery manifest.

| student | target_rate_scale | target_rate_limit | fit status | train p95 abs error | target-rate p95 |
|---|---:|---:|---|---:|---:|
| rate150 | 0.1 | 1.5 | `HOLD_BC_FIT_NO_CLOSED_LOOP` | 0.0362 | 1.3695 |
| rate150_reg02 | 0.2 | 1.5 | `HOLD_BC_FIT_NO_CLOSED_LOOP` | 0.0370 | 1.3536 |

Both students exported successfully and passed ONNX fidelity checks. The
`HOLD_BC_FIT_NO_CLOSED_LOOP` status means the fit/export smoke intentionally
did not run the closed-loop gate.

## Focused Gate

Canonical focused gate: seeds `0,2,6`, 15s, `x=0.08`, fitted corrected bridge,
rough terrain z-scale `0.0075`, intermediate push schedule.

| candidate | seed | status | samples | track_ratio | max p95 tracking | max target vel p95 | max target vel excess | body pitch p95 | base height min |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| rate150 | 0 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | 0.3097 | 0.1816 | 1.6319 | 0.2014 | 0.1733 | 0.1532 |
| rate150 | 2 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | 0.3236 | 0.1844 | 1.6392 | 0.2014 | 0.1637 | 0.1532 |
| rate150 | 6 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | 0.3630 | 0.1784 | 1.6347 | 0.2014 | 0.1477 | 0.1532 |

The rate150 student completed all three focused seeds without falling and
preserved forward progress. The only gate violation was the same repeated
left-hip-pitch max target-velocity spike:

| joint | max_rad_s | corrected_limit_rad_s | excess_rad_s |
|---|---:|---:|---:|
| `left_hip_pitch` | 2.7014 | 2.5000 | 0.2014 |

## Rejected Fixes

| test | seed | duration | status | track_ratio | max target vel excess | reason rejected |
|---|---:|---:|---|---:|---:|---|
| global gain 0.925 | 0 | 5s | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1815 | 0.0000 | clears spike but falls below forward-progress gate |
| global gain 0.90 | 0 | 5s | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0195 | 0.0000 | freezes / no meaningful forward motion |
| reg02 target-rate retrain | 0 | 5s | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 2.1286 | 0.0000 | removes spike but lunges and falls by sample 117 |

## Interpretation

- Iter21 recovery labels are useful: the old seed0 lunge became a full-duration
  rough-push rollout with acceptable tracking, posture, height, and forward
  progress.
- The candidate is not promotable because the corrected per-joint envelope has
  a hard max gate, and the rate150 student repeats a left-hip-pitch max spike
  on all focused seeds.
- A global gain wrapper is not the right fix; it removes the spike by removing
  the gait.
- Blunter rate regularization is not the right fix; the reg02 retrain removes
  the spike but destabilizes into a lunge/fall.

## Next Branch

Use the Iter21 evidence to target the exact residual defect:

1. Locate the left-hip-pitch spike timestep in the rate150 rollouts.
2. Build a local relabel or continuity constraint around that spike only.
3. Preserve the Iter21 gait labels and do not apply global output scaling.
4. Re-gate seeds `0,2,6` before any full 8-seed Phase 2 promotion gate.

The Phase 2 goal remains active.
