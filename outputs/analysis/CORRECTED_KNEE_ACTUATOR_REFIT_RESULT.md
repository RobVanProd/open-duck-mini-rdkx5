# Corrected-Knee Actuator Refit Result

status: `PASS_SINE_ONLY_TRACKING_DYNAMIC_REFIT_PENDING`

This result records the first corrected-knee robot-side actuator tracking
evidence after the left knee soft offset was changed from `-1.488 rad` to
`0.0371 rad`.

No grounded replay, walking policy replay, gain tuning, offset edit, remap,
action-scale change, phase change, deployment, or training was performed.

## Inputs

- evidence directory: `outputs/first_evidence/20260627T213827Z_corrected_knee_refit`
- config snapshot: `outputs/first_evidence/20260627T213827Z_corrected_knee_refit/20260627T213849Z_rdkx5_config_snapshot.json`
- duck_config sha256: `131a7b8fce1107b14f4727562f44f9e17324caf7fc22512ad7115911f050991b`
- corrected left_knee offset: `0.0371 rad`
- right_knee offset: `0.0798 rad`
- robot condition: supported/on stand
- policy: disabled
- sweep amplitude: `0.03 rad`
- joints: left/right hip pitch, left/right knee, left/right ankle

## Sweep Results

| frequency | max pitch-chain sent velocity p95 | max pitch-chain tracking p95 | max terminal p95 | write errors | decision |
|---:|---:|---:|---:|---:|---|
| `0.25 Hz` | `0.0470 rad/s` | `0.0103 rad` | `0.0103 rad` | `0` | `PASS` |
| `0.5 Hz` | `0.0852 rad/s` | `0.0076 rad` | `0.0111 rad` | `0` | `PASS` |
| `1.0 Hz` | `0.1683 rad/s` | `0.0103 rad` | `0.0154 rad` | `0` | `PASS` |

Read checksum errors were still observed, but write errors were zero and
tracking remained clean. Continue treating read errors as a watch item unless
they correlate with tracking spikes or control damage.

## Corrected-Knee Interpretation

The corrected left knee no longer appears as a low-speed tracking outlier:

```text
left_knee raw_tracking_p95:  0.0078 rad
right_knee raw_tracking_p95: 0.0078 rad
left-right knee raw p95 delta: approximately 0.0000 rad
```

This supports the mechanical/software offset correction at low speed.

## Sine-Only Fit

Generated:

```text
outputs/analysis/ACTUATOR_RESPONSE_FIT_CORRECTED_KNEE_SINE_ONLY.md
outputs/analysis/actuator_response_fit_corrected_knee_sine_only.json
outputs/analysis/CORRECTED_KNEE_ACTUATOR_FIT_COMPARE_SINE_ONLY.md
outputs/analysis/corrected_knee_actuator_fit_compare_sine_only.json
```

The sine-only fit selected delay `1 tick`, tau `0.040 s`, and velocity limit
`1.00 rad/s` for all pitch-chain joints, with the warning:

```text
velocity limit hit lower grid bound
```

That warning is expected for this low-velocity evidence: even the `1.0 Hz`,
`0.03 rad` sweep only reaches about `0.17 rad/s` p95 target velocity, far below
the original policy waveform range. Therefore this fit verifies corrected
low-speed tracking, but it must not replace the dynamic `x=0.08` policy-waveform
bridge for walking approval.

## Gate Decision

```text
PASS_SINE_ONLY_TRACKING_DYNAMIC_REFIT_PENDING
```

Robot walking validation remains blocked. The next robot-side evidence needed
for a corrected full bridge is a separately approved suspended dynamic policy
waveform replay, not grounded replay.
