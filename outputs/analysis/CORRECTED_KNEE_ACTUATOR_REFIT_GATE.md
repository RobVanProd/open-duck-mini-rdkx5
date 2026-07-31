# Corrected-Knee Actuator Refit Gate

status: `PREPARED_NOT_RUN`

The left-knee soft-offset correction makes the old hardware-derived actuator
bridge stale for final robot validation.

## Current Known Hardware Change

```text
left_knee: -1.488 -> 0.0371
right_knee: 0.0798 unchanged
```

## Required Next Evidence

Supported/on-stand corrected-hardware actuator tracking logs:

```text
policy disabled
operator present
hip pitch / knee / ankle pitch
0.03 rad sine
0.25 Hz -> 0.5 Hz if clean -> 1.0 Hz only if clean
JSONL telemetry + terminal log + duck_config hash/snapshot
```

## Offline Refit Outputs

Expected corrected-hardware fit artifacts:

```text
outputs/analysis/ACTUATOR_RESPONSE_FIT_CORRECTED_KNEE.md
outputs/analysis/actuator_response_fit_corrected_knee.json
outputs/analysis/CORRECTED_KNEE_ACTUATOR_FIT_COMPARE.md
outputs/analysis/corrected_knee_actuator_fit_compare.json
```

## Decision

```text
PREPARED_NOT_RUN
```

No robot walking validation is approved by this artifact.
