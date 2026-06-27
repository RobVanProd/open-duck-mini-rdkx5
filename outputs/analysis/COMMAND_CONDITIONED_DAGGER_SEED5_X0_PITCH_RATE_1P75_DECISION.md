# Command-Conditioned DAgger Seed-5 Pitch-Rate 1.75 Decision

status: `HOLD_PITCH_RATE_LABEL_SMOOTHING_KILLS_PROGRESS`

Purpose: test whether smoothing only the `x=0.08` pitch-chain labels improves
fitted-bridge tracking while preserving the DAgger seed-5 `x=0.0` fix.

This is offline analysis only. It did not train PPO, deploy, SSH, run robot
tests, or change robot runtime behavior.

## Label Curation

The `source_vx_pitch_chain_rate_limited_2p25` moving labels were rate-limited
again on the pitch chain:

```text
artifact: outputs/analysis/SOURCE_VX_PITCH_CHAIN_RATE_LIMITED_1P75_TRACES.md
status: PASS_BC_TRACE_ACTION_RATE_LIMIT_READY
traces: 8
samples_out: 4000
changed_ticks: 6059
max_target_velocity_rad_s: 1.75
```

Only the moving labels were smoothed. The x=0.0 standstill labels and DAgger
seed-5 corrective labels were left intact.

## Dataset And Fit

Manifest:

```text
outputs/analysis/COMMAND_CONDITIONED_DAGGER_SEED5_X0_PITCH_RATE_1P75_MANIFEST.md
status: PASS_BC_TRACE_MANIFEST_READY
entries: 17
samples: 8072
```

BC student:

```text
outputs/analysis/COMMAND_CONDITIONED_DAGGER_SEED5_X0_PITCH_RATE_1P75_BC_STUDENT.md
status: PASS_PPO_LOC_BC_FIT_SMOKE
MAE: 0.006966
p95 action error: 0.024948
target-rate p95: 1.643471 rad/s
```

## x=0 Gate

Canonical backlash, fitted bridge, 10 seconds, seeds 0-7:

```text
artifact: outputs/analysis/COMMAND_CONDITIONED_DAGGER_SEED5_X0_PITCH_RATE_1P75_X0_FITTED_10S.md
status: all seeds PASS_CANDIDATE_SIM_GATE
falls: 0 / 8
duration complete: 8 / 8
seed 5: PASS, vx_mean 0.0053, tracking_p95 0.0725
```

This preserves the DAgger seed-5 zero-command fix.

## x=0.08 Gate

Canonical backlash, fitted bridge, 10 seconds, seeds 0-7:

```text
artifact: outputs/analysis/COMMAND_CONDITIONED_DAGGER_SEED5_X0_PITCH_RATE_1P75_X008_FITTED_10S.md
status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
falls: 0 / 8
duration complete: 8 / 8
mean vx: 0.0094 m/s
mean track ratio: 0.1171
body pitch p95 mean: 0.0990 rad
pitch-chain target velocity p95 range: 1.4886-1.6901 rad/s
tracking p95 range: 0.1472-0.1834 rad
```

The smoothing improves the tracking/target-rate direction but removes too much
forward motion. This confirms that tracking cannot be fixed by simply making
the moving labels slower; the policy needs a different action shape or
closed-loop fine-tuning that preserves propulsion.

## Decision

Do not promote this ONNX.

This is a bounded negative result:

```text
x=0.0 stability: preserved
x=0.08 tracking: somewhat improved
x=0.08 progress: failed
```

Next branch should not lower the moving pitch-chain label rate further. It
should preserve the current DAgger seed-5 checkpoint and add tracking feedback
or PPO fine-tuning that can trade tracking and propulsion in closed loop rather
than only smoothing labels offline.

Robot validation remains blocked.
