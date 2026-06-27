# Pitch-Chain Rate-Limit Curation Result

Status: `HOLD_PITCH_CHAIN_4P3_DOES_NOT_FIX_TRACKING`

This was an offline-only analysis. No robot tests, SSH, deploy, runtime behavior
change, or PPO training was performed.

## Question

The exact source-vx selector ONNX can move forward through the fitted actuator
bridge, but strict x=0.08 fitted-backlash gates hold because pitch-chain target
velocity and simulated tracking remain too high. Earlier diagnostics showed the
right knee was both the fastest and worst-tracking joint.

This probe tested whether capping the full pitch chain at `4.3 rad/s` would
improve the strict fitted-backlash gate more than the earlier right-knee-only
`4.3 rad/s` curation.

## Artifacts

- curation: `outputs/analysis/SOURCE_VX_SELECTOR_TRACE_PITCH_CHAIN_RATE_LIMITED_4P3.md`
- manifest: `outputs/analysis/SOURCE_VX_SELECTOR_TRACE_PITCH_CHAIN_RATE_LIMITED_4P3_MANIFEST.md`
- smoke gate: `outputs/analysis/SOURCE_VX_SELECTOR_TRACE_PITCH_CHAIN_LIMITED_4P3_BLEND080_EXACT_ONNX_FITTED_BRIDGE_BC_GATE_X008_10S.md`
- strict gate: `outputs/analysis/SOURCE_VX_SELECTOR_TRACE_PITCH_CHAIN_LIMITED_4P3_BLEND080_EXACT_ONNX_MULTI_SEED_FITTED_BACKLASH_SUMMARY.md`

## Curation

The source traces were rate-limited at `4.3 rad/s` on:

```text
left_hip_pitch
left_knee
left_ankle
right_hip_pitch
right_knee
right_ankle
```

The curation changed `543` ticks:

| joint | changed ticks |
|---|---:|
| left_hip_pitch | 0 |
| left_knee | 7 |
| left_ankle | 23 |
| right_hip_pitch | 0 |
| right_knee | 493 |
| right_ankle | 20 |

So even when the full pitch chain is eligible, the correction is still mostly a
right-knee correction.

## Result

The exact-blend ONNX exported cleanly and passed the smoke replay:

```text
status: PASS_BC_FIT_SMOKE_FORWARD_REPLAY
dataset_id: 3aedbacc4a592fc8
samples: 4000
best_alpha: 0.01
```

The strict fitted-backlash x=0.08 8-seed gate completed all rollouts and kept
forward motion, but every seed still held on tracking:

```text
status: HOLD_CANDIDATE_TRACKING
duration_complete: 8/8
falls: 0/8
mean vx: 0.0477 m/s
mean track ratio: 0.5965
max pitch velocity p95 range: 4.1935-4.2879 rad/s
max tracking p95 range: 0.2685-0.2794 rad
```

## Comparison With Right-Knee-Only 4.3

| curation | vx mean | track ratio mean | max pitch velocity p95 mean | max tracking p95 mean |
|---|---:|---:|---:|---:|
| right-knee-only 4.3 | 0.0479 | 0.5992 | 4.2391 | 0.2720 |
| pitch-chain 4.3 | 0.0477 | 0.5965 | 4.2399 | 0.2735 |

The pitch-chain curation did not materially improve target velocity or tracking.

## Interpretation

The simple action-delta curation family has likely reached its useful limit.
Applying the same `4.3 rad/s` cap to the whole pitch chain preserves stable
forward replay, but it does not make the exact ONNX candidate robot-ready under
the fitted actuator bridge.

The remaining problem is not "one more pitch joint needs the same cap." It is
the learned/replayed right-knee phase/contact transition itself. The next
deployable-policy path should focus on dynamics-aware relabeling or training:

- reject source windows with right-knee phase/contact discontinuities,
- relabel around stance/swing transitions instead of rate-limiting afterward,
- or use gate-aware fine-tuning that penalizes simulated tracking while
  preserving the working closed-loop behavior.

Do not proceed to robot validation from this candidate.
