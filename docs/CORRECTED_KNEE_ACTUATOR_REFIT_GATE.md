# Corrected-Knee Actuator Refit Gate

Status: `PREPARED_NOT_RUN`

Purpose: refresh the actuator response model after the left-knee soft-offset
correction before interpreting new sim-to-real policy results.

This gate is operator-run hardware evidence collection plus offline fitting.
It does not authorize grounded replay, walking policy replay, gain tuning, IMU
remaps, offset edits, phase changes, action-scale changes, or policy changes.

## Why This Gate Exists

The previous bridge fit was built before the left-knee correction:

```text
old left_knee offset: -1.488 rad
new left_knee offset:  0.0371 rad
```

That correction removed a large software compensation from one pitch-chain
joint. Any old fitted delay/lag/velocity-limit result involving the left knee
or symmetric pitch-chain behavior is now stale for final robot-side validation.

The old fit may remain useful for offline continuity and comparison, but it
must not be treated as the final corrected-hardware bridge.

## Required Robot Condition

```text
robot supported/on stand
operator physically present
policy disabled
no grounded replay
no walking replay
no tuning
motors off at the end
```

Run only conservative actuator tracking diagnostics. Prefer the same actuator
sine-sweep procedure used for the first fit so the before/after comparison is
clean.

Minimum corrected-hardware evidence:

```text
left/right hip pitch
left/right knee
left/right ankle
0.03 rad amplitude
0.25 Hz and 0.5 Hz if clean
1.0 Hz only if 0.5 Hz is clean
JSONL telemetry
terminal log
duck_config hash/snapshot
```

Stop on unexpected motion, twitching, large tracking error, bus bursts, or
operator concern.

## Offline Fit Command

After copying the corrected-hardware JSONL logs back, run:

```bash
python3 tools/fit_actuator_response_model.py \
  outputs/first_evidence/<corrected_knee_timestamp>/suspended_policy_replay_x008_thresholds.jsonl \
  --selection-metric trimmed_rmse_95 \
  --output-md outputs/analysis/ACTUATOR_RESPONSE_FIT_CORRECTED_KNEE.md \
  --output-json outputs/analysis/actuator_response_fit_corrected_knee.json
```

If corrected x=0.08 suspended replay is not approved, fit the conservative
sine-sweep logs first and clearly label the result as low-velocity-only:

```bash
python3 tools/fit_actuator_response_model.py \
  outputs/first_evidence/<corrected_knee_timestamp>/actuator_sine_sweep_05*.jsonl \
  --selection-metric trimmed_rmse_95 \
  --output-md outputs/analysis/ACTUATOR_RESPONSE_FIT_CORRECTED_KNEE_SINE_ONLY.md \
  --output-json outputs/analysis/actuator_response_fit_corrected_knee_sine_only.json
```

Do not use a low-frequency sine-only fit to approve walking. It can verify
that the knee correction did not break basic tracking, but the policy bridge
still needs dynamic policy-waveform evidence before robot deployment.

## Comparison Command

Compare old versus corrected fit:

```bash
python3 tools/compare_actuator_response_fits.py \
  --old outputs/analysis/actuator_response_fit.json \
  --new outputs/analysis/actuator_response_fit_corrected_knee.json \
  --output-md outputs/analysis/CORRECTED_KNEE_ACTUATOR_FIT_COMPARE.md \
  --output-json outputs/analysis/corrected_knee_actuator_fit_compare.json
```

If this compare tool does not exist yet, create it before interpreting the new
fit. The comparison must report at least:

```text
per-joint delay_ticks
tau_s
velocity_limit_rad_s
p95 model error
raw tracking p95
target velocity p95
left/right knee asymmetry
left/right pitch-chain asymmetry
```

## Pass Criteria

Pass this gate only if:

```text
new duck_config hash/snapshot captured
left_knee offset is 0.0371 rad or the new current value is explicitly recorded
right_knee remains near 0.0798 rad or any change is explained
corrected telemetry has no unexpected motion
corrected fit is generated with robust selection metric
left_knee no longer appears as a special outlier from the old offset state
new bridge ranges are documented before any candidate robot validation
```

## Hold Criteria

Hold robot walking validation if:

```text
corrected telemetry is missing
duck_config hash/snapshot is missing
left_knee tracking remains materially asymmetric
bus errors correlate with tracking spikes
fit quality is poor or hits grid boundaries without explanation
new fit is sine-only but someone wants to approve walking
```

## Decision

Current status:

```text
PREPARED_NOT_RUN
```

The next robot-side action is corrected-hardware actuator tracking evidence,
not policy replay. Until that evidence exists, software candidates can continue
offline but cannot be promoted to robot walking validation.
